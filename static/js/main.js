var status_data = null;

require( [ "jquery", "jquery_address", "jquery_dateFormat", "jquery_table2csv",
    "bootstrap", "bootstratp_editable",
    "mustache",
    "ace/ace", "ace/ext-language_tools", "ace/mode-python", "ace/theme-github", "ace_snippets/text", "ace_snippets/snippets", "ace_snippets/python",
    "highstock", "highstock_no_data_to_display", "highstock_exporting", "highstock_csv_export",
    "core", "lang", "login", "notifications",
    "tech/overview.snippets", "tech/overview", "tech/live_setup", "tech/settings", "tech/statistics", "tech/thresholds",
    "mgmt/overview", "mgmt/balances", "mgmt/load_curves", "mgmt/settings", "mgmt/statistics" ], function () {

    $(function() {
        $.getJSON('/api/status/', function(data) {
            status_data = data;
            if (is_logged_in()) {
                initialize_page(function() {
                    if (status_data['technician'] && status_data['system_status'] == 'init') {
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
} );