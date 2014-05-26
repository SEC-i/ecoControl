var status_data = null;

$(function() {
    $.getJSON('/api/status/', function(data) {
        status_data = data;
        if (is_logged_in()) {
            initialize_page(function() {
                if (status_data['technician'] && status_data['system_status'] == 'init') {
                    load_page('settings');
                } else {
                    load_page(get_current_page());
                }
            });
        } else {
            load_page('login'); 
        }
    }).done(function() {
        $.address.change(function(event) {
            selected_page = event.value.replace('/', '');
            if (selected_page == '') {
                selected_page = 'overview';
            }
            load_page(selected_page);
        });
    });

    $('.navbar-brand').click(function(e) {
        if (is_logged_in()) {
            $('.nav li').removeClass('active');
            $('.nav li').first().addClass('active');
            load_page('overview')
        } else {
            load_page('login'); 
        }
        e.preventDefault();
    });
});

function get_current_page() {
    return $.address.value().replace('/', '');
}

function is_logged_in() {
    return status_data['login'] == 'active';
}

function load_page(target) {
    if (target == '') {
        target = 'overview';
    } else if (target == 'logout') {
        $.address.value('login');
        target = 'login';
    }
    url = 'templates/' + target + '.html .' + role_name();
    $('#main').load(url, function() {
        if (role_name() + '_' + target + '_ready' in window) {
            window[role_name() + '_' + target + '_ready']();
        } else if (target + '_ready' in window) {
            window[target + '_ready']();
        }
        $('.nav li').removeClass('active');
        $('a[href=' + target + ']').parent().addClass('active');
    });
}

function role_name() {
    if (status_data['technician']) {
        return 'technician';
    }
    return 'manager';
}

function initialize_page(callback) {
    var url = 'templates/navigation.html .' + role_name();
    $('#navbar_container').load(url, function() {
        $('#navbar_container a').click(function() {
            $.address.value($(this).attr('href'));
        });

        $('#navbar_container a').address(function() {  
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
        callback();
    });
}