({
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

        ace: "../libs/ace",
        ace_snippets: "../libs/ace/snippets/",
    },
    shim: {
        'jquery_address': ['jquery'],
        'jquery_dateFormat': ['jquery'],
        'jquery_table2csv': ['jquery'],
        'core': ['jquery'],
        'lang': ['jquery'],
        'login': ['jquery'],
        'notifications': ['jquery'],
        'tech/overview.snippets': ['jquery'],
        'tech/overview': ['jquery'],
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

    baseUrl : "static/js",
    name: "main",
    out: "static/js/main.min.js",
    removeCombined: true
})