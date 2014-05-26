var status_data = null;

$(function() {
    $.getJSON('/api/status/', function(data) {
        status_data = data;
    }).done(function() {
        $.address.change(function(event) {  
            // do something depending on the event.value property, e.g.  
            // $('#content').load(event.value + '.xml'); 
            page = event.value.replace('/', '');
            if (page == '') {
                page = 'overview';
            }

            if (is_logged_in()) {
                initialize_navigation();
                if (status_data['technician']) {
                    if (status_data['system_status'] == 'init') {
                        load_page('settings');
                    } else {
                        load_page(page);
                    }
                } else if (status_data['manager']) {
                    load_page(page);
                }
            } else {
                load_page('login'); 
            }
        });
    });

    $('.navbar-brand').click(function(e) {
        if (is_logged_in()) {
            $('.navbar_item').removeClass('active');
            $('.navbar_item').first().addClass('active');
            load_page('overview')
        } else {
            load_page('login'); 
        }
        e.preventDefault();
    })  
    
});

function get_current_page() {
    return $.address.value().replace('/', '');
}

function is_logged_in() {
    return status_data['login'] == 'active';
}

function load_page(target) {
    url = 'templates/' + target + '.html .' + role_name();
    $('#main').load(url, function() {
        if (role_name() + '_' + target + '_ready' in window) {
            window[role_name() + '_' + target + '_ready']();
        } else if (target + '_ready' in window) {
            window[target + '_ready']();
        }
    });
}

function role_name() {
    if (status_data['technician']) {
        return 'technician';
    }
    return 'manager';
}

function initialize_navigation() {
    var url = 'templates/navigation.html .' + role_name();
    $('#navbar_container').load(url, function() {
        // $('.navbar_item').click(function(e) {
        //     $('.navbar_item').removeClass('active');
        //     $(this).addClass('active');
        //     load_page($(this).attr('data-target'));
            
        //     e.preventDefault();
        // });

        $('a').click(function() {
            $('.navbar_item').removeClass('active');
            $(this).parent().addClass('active');
            $.address.value($(this).attr('href'));
        });  
        $('a').address(function() {  
            return $(this).attr('href').replace(/^#/, '');  
        }); 

        $('#logout_button').click(function(event) {
            $('#navbar_container').empty();
            $.ajax({
                type: "POST",
                url: "/api/logout/",
                crossDomain: true,
                xhrFields: {
                    withCredentials: true
                }
            }).done(load_page('login'));
            event.preventDefault();
        });
    });
}

function login_ready() {
    $('#login_form').submit(function(event) {
        login_user();
        event.preventDefault();
    }); 
}

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
            $.getJSON('/api/status/', function(data) {
                status_data = data;
                initialize_navigation();
                load_page('overview');
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