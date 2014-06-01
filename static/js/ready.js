var status_data = null;

$(function() {
    $.getJSON(api_base_url + 'status/', function(data) {
        status_data = data;
        if (is_logged_in()) {
            initialize_page(function() {
                if (status_data['admin'] && status_data['system_status'] == 'init') {
                    $.address.value('settings');
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

    $('.navbar-brand').click(function(event) {
        event.preventDefault();
        if (is_logged_in()) {
            $('.nav li').removeClass('active');
            $('.nav li').first().addClass('active');
            load_page('overview')
        } else {
            load_page('login'); 
        }
    });
});
