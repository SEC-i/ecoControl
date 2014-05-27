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

        ace: "../libs/ace/ace",
        ace_lang: "../libs/ace/ext-language_tools",
        ace_python: "../libs/ace/mode-python",
        ace_github: "../libs/ace/theme-github",
        ace_text: "../libs/ace/snippets/text",
        ace_snippets: "../libs/ace/snippets/snippets",
        ace_snippets_python: "../libs/ace/snippets/python",

        core: "core",
        lang: "lang",

        login: "login",
        notifications: "notifications",

        tech_overview_snippets: "tech/overview.snippets",
        tech_overview: "tech/overview",
        tech_live_setup: "tech/live_setup",
        tech_settings: "tech/settings",
        tech_statistics: "tech/statistics",
        tech_thresholds: "tech/thresholds",

        mgmt_overview: "mgmt/overview",
        mgmt_balances: "mgmt/balances",
        mgmt_load_curves: "mgmt/load_curves",
        mgmt_settings: "mgmt/settings",
        mgmt_statistics: "mgmt/statistics",

    },
    shim: {
        'mustache': {
            exports: 'Mustache'
        },
        'jquery_address': {
            deps: ['jquery']
        },
        'jquery_dateFormat': {
            deps: ['jquery']
        },
        'jquery_table2csv': {
            deps: ['jquery']
        },
        'core': {
            deps: ['jquery']
        },
        'lang': {
            deps: ['jquery']
        },
        'login': {
            deps: ['jquery']
        },
        'notifications': {
            deps: ['jquery']
        },
        'tech_overview_snippets': {
            deps: ['jquery']
        },
        'tech_overview': {
            deps: ['jquery']
        },
        'tech_live_setup': {
            deps: ['jquery']
        },
        'tech_settings': {
            deps: ['jquery']
        },
        'tech_statistics': {
            deps: ['jquery']
        },
        'tech_thresholds': {
            deps: ['jquery']
        },
        'mgmt_overview': {
            deps: ['jquery']
        },
        'mgmt_balances': {
            deps: ['jquery']
        },
        'mgmt_load_curves': {
            deps: ['jquery']
        },
        'mgmt_settings': {
            deps: ['jquery']
        },
        'mgmt_statistics': {
            deps: ['jquery']
        }
    },

    baseUrl : "static/js",
    name: "main",
    out: "static/js/main.min.js",
    removeCombined: true
})