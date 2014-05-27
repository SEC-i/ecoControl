var status_data = null;

require( [ "jquery", "jquery_address", "jquery_dateFormat", "jquery_table2csv",
    "bootstrap", "bootstratp_editable",
    "mustache",
    "ace", "ace_lang", "ace_python", "ace_github", "ace_text", "ace_snippets", "ace_snippets_python",
    "highstock", "highstock_no_data_to_display", "highstock_exporting", "highstock_csv_export",
    "core", "lang", "login", "notifications",
    "tech_overview_snippets", "tech_overview", "tech_live_setup", "tech_settings", "tech_statistics", "tech_thresholds",
    "mgmt_overview", "mgmt_balances", "mgmt_load_curves", "mgmt_settings", "mgmt_statistics" ], function () {

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