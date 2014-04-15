var refresh_gui = true;
var editor = null;

// READY
$(function () {
    initialize_editor();
    initialize_svg();
    initialize_hourly_demands();
    initialize_event_handlers();
    initialize_wizard();

    $.getJSON("./api/settings/", function (data) {
        update_setting(data);
    }).done(function () {
        $.getJSON("./api/code/", function (data) {
            editor.setValue(data['editor_code'], 1);
        }).done(function () {
            initialize_diagram();
            refresh();
            // set up refresh loop
            setInterval(function () {
                refresh();
            }, 2000);
        });
    });
});

// INITIALIZATIONS
function initialize_editor() {
    ace.require("ace/ext/language_tools");
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/github");
    editor.getSession().setMode("ace/mode/python");
    editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true
    });
    ace.config.loadModule('ace/snippets/snippets', function () {
        var snippetManager = ace.require('ace/snippets').snippetManager;
        ace.config.loadModule('ace/snippets/python', function (m) {
            if (m) {
                m.snippets = m.snippets.concat(custom_snippets);
                snippetManager.register(m.snippets, m.scope);
            }
        });
    });
}

function initialize_svg() {
    $.get("./static/img/simulation.svg", function (data) {
        var svg_item = document.importNode(data.documentElement, true);
        $("#simulation_setup").append(svg_item);
    }, "xml");
}

function initialize_hourly_demands() {
    for (var i = 0; i < 24; i++) {
        $("#daily_thermal_demand").append("<span id='daily_thermal_demand_" + i + "' class='slider_thermal'><span>" + i + "</span></span>");
        $("#daily_electrical_variation").append("<span id='daily_electrical_variation_" + i + "' class='slider_electrical'><span>" + i + "</span></span>");
    }

    $(".slider_thermal").slider({
        value: 0,
        min: 0,
        max: 3000,
        range: "min",
        animate: true,
        orientation: "vertical",
        slide: function (event, ui) {
            var text = "(Current value: " + ui.value / 100 + "C)";
            $("#daily_thermal_demand_info").text(text);
        },
        stop: function (event, ui) {
            $("#daily_thermal_demand_info").text('');
        }
    });

    $(".slider_electrical").slider({
        value: 0,
        min: 0,
        max: 20000,
        range: "min",
        animate: true,
        orientation: "vertical",
        slide: function (event, ui) {
            var text = "(Current value: " + ui.value / 100 + "%)";
            $("#daily_electrical_variation_info").text(text);
        },
        stop: function (event, ui) {
            $("#daily_electrical_variation_info").text('');
        }
    });
}

function initialize_event_handlers() {
    $("#settings").submit(function (event) {
        var post_data = $("#settings").serialize();
        for (var i = 0; i < 24; i++) {
            post_data += "&daily_thermal_demand_" + i + "=" + ($("#daily_thermal_demand_" + i).slider("value") / 100);
        }
        for (var i = 0; i < 24; i++) {
            post_data += "&daily_electrical_variation_" + i + "=" + ($("#daily_electrical_variation_" + i).slider("value") / 10000);
        }
        $.post("./api/settings/", post_data, function (data) {
            $("#settings_button").removeClass("btn-primary");
            $("#settings_button").addClass("btn-success");
            update_setting(data);
            setTimeout(function () {
                $("#settings_button").removeClass("btn-success");
                $("#settings_button").addClass("btn-primary");
                hide_forecasts();
            }, 500);
        });
        event.preventDefault();
    });

    $("#settings").change(function () {
        var post_data = $("#settings").serialize();
        for (var i = 0; i < 24; i++) {
            post_data += "&daily_thermal_demand_" + i + "=" + ($("#daily_thermal_demand_" + i).slider("value") / 100);
        }
        for (var i = 0; i < 24; i++) {
            post_data += "&daily_electrical_variation_" + i + "=" + ($("#daily_electrical_variation_" + i).slider("value") / 10000);
        }
        post_data += "&forecast_time=" + 3600.0 * 24 * 30;
        $.post("./api/forecasts/", post_data, function (data) {
            update_forecast(data);
        });
    });

    $(".fast_forward_button").click(function (event) {
        $.post("./api/simulation/", {
            forward: $(this).val()
        });
    });

    $("#editor_button").click(function () {
        $.post("./api/settings/", {
            code: editor.getValue(),
            password: $('#password').val()
        }, function (data) {
            hide_forecasts();
            editor.setValue(data['editor_code'], 1);
        });
    });

    $("#editor_simulate_button").click(function () {
        $.post("./api/forecasts/", {
            code: editor.getValue(),
            password: $('#password').val(),
            forecast_time: 3600.0 * 24 * 30
        }, function (data) {
            update_forecast(data);
        });
    });

    $("#pause_refresh").click(function (event) {
        refresh_gui = !refresh_gui;
        if (refresh_gui) {
            $("#pause_refresh span").removeClass('glyphicon-pause');
            $("#pause_refresh span").addClass('glyphicon-refresh');
        } else {
            $("#pause_refresh span").removeClass('glyphicon-refresh');
            $("#pause_refresh span").addClass('glyphicon-pause');

        }
        event.preventDefault();
    });

    $("#reset_simulation").click(function (event) {
        $.post("./api/simulation/", {
            reset: 1
        });
        // location.reload(true);
    });

    $("#save_snippet").submit(function (event) {
        $.post("./api/code/", {
            save_snippet: $("#snippet_name").val(),
            code: editor.getValue()
        }, function (data) {
            editor.setValue(data['editor_code'], 1);

            // refresh snippet list
            if ('code_snippets' in data) {
                $("#snippets").html('');
                $.each(data['code_snippets'], function (index, snippet_name) {
                    $("#snippets").append('<option>' + snippet_name + '</option>');
                });
            }
        });
        event.preventDefault();
    });

    $("#load_snippet").submit(function (event) {
        $.post("./api/code/", {
            snippet: $("#snippets").val()
        }, function (data) {
            editor.setValue(data['editor_code'], 1);
        });
        event.preventDefault();
    });

    $("#export_data").submit(function (event) {
        $.post("./api/simulation/", {
            export: $("#export_name").val()
        });
        event.preventDefault();
    });
}

function initialize_diagram() {
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    // Create the chart
    $('#simulation_diagram').highcharts('StockChart', {
        chart: {
            height: 400,
            zoomType: 'xy'
        },
        rangeSelector: {
            buttons: [{
                count: 6,
                type: 'hour',
                text: '6H'
            }, {
                count: 12,
                type: 'hour',
                text: '12H'
            }, {
                count: 1,
                type: 'day',
                text: '1D'
            }, {
                count: 1,
                type: 'week',
                text: '1W'
            }, {
                count: 2,
                type: 'week',
                text: '2W'
            }, {
                count: 1,
                type: 'month',
                text: '1M'
            }, {
                count: 2,
                type: 'month',
                text: '2M'
            }, {
                count: 3,
                type: 'month',
                text: '3M'
            }, {
                count: 6,
                type: 'month',
                text: '6M'
            }, {
                count: 9,
                type: 'month',
                text: '9M'
            }, {
                type: 'all',
                text: 'All'
            }],
            selected: 6,
            inputEnabled: false
        },
        xAxis: {
            plotLines: [{
                value: 0,
                width: 2,
                color: 'red',
                label: {
                    text: 'Now',
                    align: 'right',
                    y: 32,
                    x: 6
                }
            }]
        },
        yAxis: {
            min: -10
        },
        tooltip: {
            valueDecimals: 2
        },
        lang: {
            noData: "Loading data..."
        },
        plotOptions: {
            series: {
                marker: {
                    enabled: false
                },
                lineWidth: 1.5,
            }
        },
        series: series_data,
        credits: {
            enabled: false
        }
    });
}

function initialize_wizard() {
    $.fn.wizard.logging = true;
    var options = {};
    var wizard = $("#startup").wizard(options);
    wizard.show();
}