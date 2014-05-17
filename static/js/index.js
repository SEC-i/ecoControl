// READY
$(function() {
    $('#login_form').submit(function(event) {
        login_user();
        event.preventDefault();
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
           console.log('fail');
        }
    });
}

function redirect_to_tech(show) {
    window.location.href = 'tech/index.html';
}

function redirect_to_mgmt(show) {
    window.location.href = 'mgmt/index.html';
}