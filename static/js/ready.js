var status_data = null;

$(function() {
    $.address.change(function(event) {
        load_page(event.value.replace('/', ''));
    });

    $.getJSON(api_base_url + 'status/', function(data) {
        status_data = data;
        if (is_logged_in()) {
            initialize_page(function() {
                if ((status_data['admin'] && status_data['system_status'] == 'init')) {
                    $.address.value('settings');
                } else {
                    $.address.value(get_current_page());
                }
            });
        } else {
            $.address.value('login');
        }
    });

    $('.navbar-brand').click(function(event) {
        event.preventDefault();
        if (is_logged_in()) {
            $('.nav li').removeClass('active');
            $('.nav li').first().addClass('active');
            $.address.value('overview');
        } else {
            $.address.value('login');
        }
    });
});
