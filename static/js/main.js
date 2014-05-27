var status_data = null;

require.config({
    paths: {
        jquery: "../libs/jquery/jquery.min",
        jquery_address: "../libs/jquery-address/jquery.address",
        jquery_dateFormat: "../libs/jquery-dateFormat/jquery-dateFormat.min",
        jquery_table2csv: "../libs/jquery-table2csv/jquery.table2csv",

        bootstrap: "../libs/bootstrap/js/bootstrap.min",
        bootstratp_editable: "../libs/bootstrap3-editable/js/bootstrap-editable",

        mustache: "../libs/mustache/mustache",

        highstock: "../libs/highstock/highstock",
        highstock_no_data_to_display: "../libs/highstock/modules/no-data-to-display",
        highstock_exporting: "../libs/highstock/modules/exporting",
        highstock_csv_export: "libs/highcharts.csv-export",

        ace: "../libs/ace/",
        ace_snippets: "../libs/ace/snippets/",
    },
    shim: {
        'mustache': {
          exports: 'Mustache'
        },
        'jquery_address': ['jquery'],
        'jquery_dateFormat': ['jquery'],
        'jquery_table2csv': ['jquery'],

        'ace/ext-language_tools': ['ace/ace'],
        'ace/mode-python': ['ace/ace'],
        'ace/theme-github': ['ace/ace'],
        'ace_snippets/text': ['ace/ace'],
        'ace_snippets/snippets': ['ace/ace'],
        'ace_snippets/python': ['ace/ace'],

        'core': ['jquery'],
        'lang': ['jquery'],
        'login': ['jquery'],
        'notifications': ['jquery'],
        'tech/overview.snippets': ['jquery'],
        'tech/overview': ['jquery', 'mustache'],
        'tech/live_setup': ['jquery'],
        'tech/settings': ['jquery'],
        'tech/statistics': ['jquery'],
        'tech/thresholds': ['jquery'],
        'mgmt/overview': ['jquery'],
        'mgmt/balances': ['jquery'],
        'mgmt/load_curves': ['jquery'],
        'mgmt/settings': ['jquery'],
        'mgmt/statistics': ['jquery']
    },
    baseUrl: 'js'
});

require([ "mustache", "jquery", "jquery_address", "jquery_dateFormat", "jquery_table2csv",
    "bootstrap", "bootstratp_editable",
    "ace/ace", "ace/ext-language_tools", "ace/mode-python", "ace/theme-github", "ace_snippets/text", "ace_snippets/snippets", "ace_snippets/python",
    "highstock", "highstock_no_data_to_display", "highstock_exporting", "highstock_csv_export",
    "core", "lang", "login", "notifications",
    "tech/overview.snippets", "tech/overview", "tech/live_setup", "tech/settings", "tech/statistics", "tech/thresholds",
    "mgmt/overview", "mgmt/balances", "mgmt/load_curves", "mgmt/settings", "mgmt/statistics" ], function (Mustache) {

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