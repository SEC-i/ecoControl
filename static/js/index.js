// READY
$(function() {
    $.getJSON('/api/status/', function(status_data) {
        if (status_data['login'] == 'active') {
            if (status_data['technician']) {
                if (status_data['system_status'] == 'init') {
                    redirect_to_tech_settings();
                } else {
                    redirect_to_tech();
                }
            } else if (status_data['manager']) {
                redirect_to_mgmt();
            }
        } else {
            $('#login_form').submit(function(event) {
                login_user();
                event.preventDefault();
            }); 
        }
    });   
});

function login_user() {
    $.ajax({
        type: 'POST',
        url: '/api/login/',
        data: {
            username: $('#login_username').val(),
            password: $('#login_password').val(),
        }
    }).done(function(data) {
        if (data['login'] == 'successful') {
            $.getJSON('/api/status/', function(status_data) {
                if (status_data['technician']) {
                    redirect_to_tech();
                }else if (status_data['manager']) {
                    redirect_to_mgmt();
                }
            });
        } else {
            var login_button = $('#login_button');
            login_button.text('Login incorrect. Please try again!').removeClass('btn-primary').addClass('btn-danger');
            setTimeout(function() {
                login_button.text('Login').removeClass('btn-danger').addClass('btn-primary');
            }, 2000);
        }
    });
}

function redirect_to_tech() {
    window.location.href = 'tech/index.html';
}

function redirect_to_tech_settings() {
    window.location.href = 'tech/settings.html';
}

function redirect_to_mgmt() {
    window.location.href = 'mgmt/index.html';
}