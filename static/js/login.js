// READY
function login_ready() {
    $('#login_form').submit(function(event) {
        event.preventDefault();
        login_user();
    }); 
}

function login_user() {
    $.ajax({
        type: 'POST',
        url: api_base_url + 'login/',
        data: {
            username: $('#login_username').val(),
            password: $('#login_password').val(),
        }
    }).done(function(data) {
        if (data['login'] === "successful") {
            $.getJSON(api_base_url + 'status/', function(data) {
                status_data = data;
                initialize_page(function() {
                    if (status_data['admin'] && status_data['device_status'] === "init") {
                        $.address.value('settings');
                    } else {
                        $.address.value('overview');
                    }
                });
            });
        } else {
            var login_button = $('#login_button');
            login_button.text(get_text('login_incorrect')).removeClass('btn-primary').addClass('btn-danger');
            setTimeout(function() {
                login_button.text('Login').removeClass('btn-danger').addClass('btn-primary');
            }, 2000);
        }
    });
}