var diagram_initialized = false;
var plotline_timestamp = null;
var sensor_count = 0;

// READY
$(function() {
    $.getJSON("/api/status/", function(data) {
        if (data['system_status'] == 'init') {
            redirect_to_settings();
        } else {
            initialize_diagram();
            initialize_tuning_form();
            initialize_editor();
            if (data['system_mode'] == 'demo') {
                initialize_forward_buttons();
            }
        }
    });
});


// Diagram
function initialize_diagram() {
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    var series = [];
    $.getJSON('/api/data/', function(data) {
        $.each(data, function(index, sensor) {
            series.push({
                name: sensor.name + ' (' + sensor.device + ')',
                data: sensor.data,
                color: colors_past[index],
                tooltip: {
                    valueSuffix: ' ' + sensor.unit
                }
            });
        });
        sensor_count = series.length;
    }).done(function () {
        $.getJSON('/api/forecast/', function(forecast_data) {
            $.each(forecast_data, function(index, sensor) {
                $.merge(series[index].data, sensor.data);
            });
            plotline_timestamp = forecast_data[0].data[0][0];
        }).done(function () {
            // Create the chart
            $('#simulation_diagram').highcharts('StockChart', {
                chart: {
                    height: 500,
                    zoomType: 'xy',
                    events: {
                        load: update_now_line,
                        setExtremes: update_now_line
                    }
                },
                legend: {
                    enabled: true
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
                        type: 'all',
                        text: 'All'
                    }],
                    selected: 4,
                    inputEnabled: false
                },
                xAxis: {
                    plotLines: [{
                        id: 'now',
                    }],
                    PlotBands: [{
                        id: 'now_band',
                    }]
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
                    },
                    line: {
                        animation: false
                    }
                },
                series: series,
                credits: {
                    enabled: false
                }
            });

            setTimeout(refresh, 10000);
        });
    });
}

function refresh() {
    var chart = $('#simulation_diagram').highcharts();
    var series_data = []
    $.getJSON('/api/data/', function(data) {
        $.each(data, function(index, sensor) {
            series_data.push(sensor.data);
        });
    }).done(function () {
        $.getJSON('/api/forecast/', function(forecast_data) {
            $.each(forecast_data, function(index, sensor) {
                chart.series[index].setData($.merge(series_data[index], sensor.data), false);
            });

            plotline_timestamp = forecast_data[0].data[0][0];
        }).done(function () {
            chart.redraw();

            setTimeout(refresh, 10000);
        });
    });
}

function update_now_line() {
    var chart = $(this)[0];

    chart.xAxis[0].removePlotBand('now_band');
    chart.xAxis[0].addPlotBand({
        id: 'now_band',
        from: plotline_timestamp,
        to: plotline_timestamp + 14 * 24 * 60 * 60 * 1000,
        color: '#F0F0F0',
        label: {
            text: 'Forecast',
            rotation: 0,
            align: 'center',
            y: 32,
            x: 6
        }
    });
    chart.xAxis[0].removePlotLine('now');
    chart.xAxis[0].addPlotLine({
        id: 'now',
        value: plotline_timestamp,
        width: 2,
        color: 'red',
        label: {
            text: 'Now',
            align: 'right',
            y: 32,
            x: 6
        }
    });

    if (!diagram_initialized) {
        chart.xAxis[0].setExtremes(new Date(plotline_timestamp - 7 * 24 * 60 * 60 * 1000), new Date(plotline_timestamp + 7 * 24 * 60 * 60 * 1000));
        diagram_initialized = true;
    }
}

function initialize_forward_buttons() {
    $('#live_diagram_header').append(
        '<div class="btn-group btn-group-xs pull-right" data-toggle="buttons"></div>'
    );

    var forward_options = [[1, '1 Day'], [7, '1 Week'], [14, '2 Weeks'], [4 * 7, '1 Month']];
    $.each(forward_options, function(index, option){
        $('#live_diagram_header .btn-group').append(
            '<button type="button" class="btn btn-default" value="' + option[0] + '" data-toggle="button">\
              <span class="glyphicon glyphicon-fast-forward"></span> ' + option[1] + '\
            </button>'
        );
    });

    $('#live_diagram_header button').click(function() {
        // send value to forward hook
        console.log($(this).val());
    });
}

// Tuning
function initialize_tuning_form() {
    $.getJSON('/api/settings/tunable/', function(data) {
        var item = $('#tuning_form');
        $.each(data, function(device_id, device_configurations) {
            $.each(device_configurations, function(key, config_data) {
                var namespace = namespaces[device_id];
                item.append(get_input_field_code(namespace, key, config_data));
            });
        });
        $('#tuning_form').change(generate_immediate_feedback);
        $('#tuning_button').click(apply_changes);
        $('#tuning_reset_button').click(function() {
            $('#tuning_form')[0].reset();
        })
    });
}

function generate_immediate_feedback() {
    $('#immediate_notice').show();
    $('#tuning_button').prop('disabled', true);

    var post_data = [];
    $('.configuration').each(function () {
        post_data.push({
            device: $(this).attr('data-device'),
            key: $(this).attr('data-key'),
            type: $(this).attr('data-type'),
            unit: $(this).attr('data-unit'),
            value: $(this).val()
        });
    });
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/api/forecast/',
        data: JSON.stringify(post_data),
        dataType: 'json',
        success: function(data) {
            update_immediate_forecast(data);
            $('#immediate_notice').hide();
            $('#tuning_button').prop('disabled', false);
        }
    });
}

function apply_changes() {
    $('#tuning_button').removeClass('btn-primary').addClass('btn-success');
    var post_data = [];
    $('.configuration').each(function () {
        post_data.push({
            device: $(this).attr('data-device'),
            key: $(this).attr('data-key'),
            type: $(this).attr('data-type'),
            unit: $(this).attr('data-unit'),
            value: $(this).val()
        });
    });
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/api/configure/',
        data: JSON.stringify(post_data),
        dataType: 'json',
        success: function(data) {
            setTimeout(function() {
                $('#tuning_button').removeClass('btn-success').addClass('btn-primary');
            }, 500);
            console.log(data);
        }
    }).done(function() {
        cleanup_diagram();
    });
}

function update_immediate_forecast(data) {
    var chart = $('#simulation_diagram').highcharts();

    cleanup_diagram();

    $.each(data, function(index, sensor) {
        chart.addSeries({
            name: sensor.name + ' (' + sensor.device + ') (predicted)',
            data: sensor.data,
            color: colors_modified[index],
            dashStyle: 'shortdot',
            tooltip: {
                valueSuffix: ' ' + sensor.unit
            }
        }, false);
    });
    chart.redraw();
}

function cleanup_diagram(chart) {
    var chart = $('#simulation_diagram').highcharts();
    var i = 0
    while(chart.series.length > sensor_count + 1) {
        if (chart.series[i].name.indexOf('predicted') != -1) {
            chart.series[i].remove(false);
        } else {
            i++;
        }
    };
    return true;
}

function get_input_field_code(namespace, key, data) {
    var device_id = namespaces.indexOf(namespace);
    var output =
            '<div class="col-sm-4"><div class="form-group">' +
                '<label for="' + namespace + '_' + key + '">' + get_text(key) + ' (Device #' + device_id + ')</label>';
    if (data.unit == '') {
        output +=
                '<input type="text" class="configuration form-control" id="' + namespace + '_' + key + '" data-device="' + device_id + '" data-key="' + key + '" data-type="' + data.type + '" data-unit="' + data.unit + '"  value="' + data.value + '">';
    } else {
        output +=
                '<div class="input-group">' +
                    '<input type="text" class="configuration form-control" id="' + namespace + '_' + key + '" data-device="' + device_id + '" data-key="' + key + '" data-type="' + data.type + '" data-unit="' + data.unit + '"  value="' + data.value + '">' +
                    '<span class="input-group-addon">' + data.unit + '</span>' +
                '</div>';
    }
    output += '</div></div>';
    return output;
}

// Code Editor
function initialize_editor() {
    ace.require("ace/ext/language_tools");
    editor = ace.edit("editor");
    editor.setTheme("ace/theme/github");
    editor.getSession().setMode("ace/mode/python");
    editor.setOptions({
        enableBasicAutocompletion: true,
        enableSnippets: true
    });
    ace.config.loadModule('ace/snippets/snippets', function() {
        var snippetManager = ace.require('ace/snippets').snippetManager;
        ace.config.loadModule('ace/snippets/python', function(m) {
            if (m) {
                m.snippets = m.snippets.concat(custom_snippets);
                snippetManager.register(m.snippets, m.scope);
            }
        });
    });
}