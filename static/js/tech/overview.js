var diagram_initialized = false;
var plotline_timestamp = null;
var sensor_count = 0;
var editor = null;
var live_diagram_detailed = true;

// READY
function technician_overview_ready() {
    initialize_technician_diagram();
    initialize_technician_tuning_form();
    initialize_technician_editor();
    if (status_data['system_mode'] == 'demo') {
        initialize_forward_buttons();
    }
}

// Diagram
function initialize_technician_diagram() {
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    var series = [];
    $.getJSON(api_base_url + 'data/' + (live_diagram_detailed ? 'monthly/' : 'yearly/'), function(data) {
        var table_headlines = ['Sensor', 'Device', 'Value'];
        var table_rows = [];
        var latest_date = 0;
        $.each(data, function(index, sensor) {
            $.each(sensor.data, function(index, value){
                value[0] = new Date(value[0]).getTime();
            });
            series.push({
                id: index,
                name: sensor.name + ' (' + sensor.device + ')',
                data: sensor.data,
                color: colors_past[index],
                tooltip: {
                    valueSuffix: ' ' + sensor.unit
                }
            });
            latest_value = Math.round(sensor.data[sensor.data.length - 1][1] * 100) / 100;
            latest_date = sensor.data[sensor.data.length - 1][0];
            table_rows.push([sensor.name, sensor.device, latest_value + ' ' + sensor.unit]);
        });
        update_now_table(table_rows, latest_date);
        sensor_count = series.length;
    }).done(function () {
        $.getJSON(api_base_url + 'forecast/', function(forecast_data) {
            $.each(forecast_data, function(index, sensor) {
                $.each(sensor.data, function(index, value){
                    value[0] = new Date(value[0]).getTime();
                });
                if (index < series.length) {
                    $.merge(series[index].data, sensor.data);
                }
            });
            plotline_timestamp = forecast_data[0].data[0][0];
        }).done(function () {
            // Create the chart
            $('#tech_live_diagram').highcharts('StockChart', {
                chart: {
                    height: 500,
                    zoomType: 'xy',
                    events: {
                        load: update_now_line,
                        setExtremes: update_now_line
                    }
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
                        text: '1'+get_text('day_abbr'),
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
                        text: get_text('all')
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
                    noData: get_text('chart_loading')
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
            }, function(chart) {
                initialize_tech_live_diagram_filters(series);
            });

            setTimeout(function() {
                refresh_technician_diagram(true);
            }, 10000);
        });
    });

    $('#live_data_month').click(function() {
        live_diagram_detailed = true;
        refresh_technician_diagram(false);
    });

    $('#live_data_year').click(function() {
        live_diagram_detailed = false;
        refresh_technician_diagram(false);
    });

    $('#tech_live_data_export_button').click(function(event) {
        event.preventDefault();
        export_table($('#tech_live_data_table_container'));
    });
}

function refresh_technician_diagram(repeat) {
    var chart = $('#tech_live_diagram').highcharts();
    var series_data = []
    $.getJSON(api_base_url + 'data/' + (live_diagram_detailed ? 'monthly/' : 'yearly/'), function(data) {
        var table_rows = [];
        var latest_date = 0;
        $.each(data, function(index, sensor) {
            $.each(sensor.data, function(index, value){
                value[0] = new Date(value[0]).getTime();
            });
            series_data.push(sensor.data);
            latest_value = Math.round(sensor.data[sensor.data.length - 1][1] * 100) / 100;
            latest_date = sensor.data[sensor.data.length - 1][0];
            table_rows.push([sensor.name, sensor.device, latest_value + ' ' + sensor.unit]);
        });
        update_now_table(table_rows, latest_date);
    }).done(function () {
        $.getJSON(api_base_url + 'forecast/', function(forecast_data) {
            $.each(forecast_data, function(index, sensor) {
                $.each(sensor.data, function(index, value){
                    value[0] = new Date(value[0]).getTime();
                });
                if (index < series_data.length) {
                    chart.series[index].setData($.merge(series_data[index], sensor.data), false);
                }
            });
            plotline_timestamp = forecast_data[0].data[0][0];
        }).done(function () {
            chart.redraw();

            if (repeat && get_current_page() == 'overview') {
                setTimeout(function() {
                    refresh_technician_diagram(true);
                }, 10000);
            }
        });
    });
}

function initialize_tech_live_diagram_filters(series) {
    var rows = [{filters: []}];
    $.each(series, function(index, series_data) {
        var row = Math.floor(series_data.id / 4);
        if (rows[row] == undefined) {
            rows.push({filters: []});
        }
        rows[row].filters.push({
            id: series_data.id,
            name: series_data.name,
            color: series_data.color});
    });
    var output = render_template($('#snippet_tech_live_diagram_filters').html(), { rows: rows });
    $('#tech_live_diagram_filters').html(output);
    $('.tech_live_data_filter_button').change(function() {
        var chart = $('#tech_live_diagram').highcharts();

        var check_selected = false;
        $('#tech_live_diagram_filters .tech_live_data_filter_button').each(function(index, item) {
            var series_index = $(item).val();
            var visible = $(this).is(":checked");
            check_selected = check_selected || visible;
            chart.series[series_index].setVisible(visible, false);
            var simulated_index = series.length + parseInt(series_index) + 1;
            if (simulated_index < chart.series.length) {
                chart.series[simulated_index].setVisible(visible, false);
            }
        });

        if (!check_selected) {
            $.each(chart.series, function(index, series) {
                series.setVisible(true, false);
            });
        }

        chart.redraw();
    });
}

function update_now_table(rows, date) {
    var headlines = ['Sensor', 'Device', 'Value'];
    draw_table($('#tech_live_data_table_container'), headlines, rows);
    $('#tech_live_data_table_container').prepend('<h3>' + $.format.date(new Date(date), "dd.MM.yyyy HH:MM") + '</h3>');
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
            text: get_text('overview_chart_forecast'),
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
            text: get_text('overview_chart_now'),
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
    var forward_options = {
        buttons: [
        {
            value: 1,
            text: '1' + get_text('overview_chart_day')
        }, {
            value: 7,
            text: '1' + get_text('overview_chart_week')
        }, {
            value: 14,
            text: '2' + get_text('overview_chart_weeks')
        }, {
            value: 4 * 7,
            text: '1' + get_text('overview_chart_month')
        }]
    };

    var output = render_template($('#snippet_forward_buttons').html(), forward_options);
    $('#live_diagram_header').append(output);

    $('#live_diagram_header button').click(function() {
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: api_base_url + 'forward/',
            data: JSON.stringify({
                forward_time: $(this).val()
            }),
            dataType: 'json',
            success: function(data) {
                refresh_technician_diagram(false);
                console.log(data);
            }
        });
    });
}

// Tuning
function initialize_technician_tuning_form() {
    $.getJSON(api_base_url + 'settings/tunable/', function(data) {
        var item = $('#tuning_form');
        $.each(data, function(device_id, device_configurations) {
            $.each(device_configurations, function(key, config_data) {
                var namespace = namespaces[device_id];
                item.append(get_input_field_tuning(namespace, key, config_data));
            });
        });
        $('#tuning_form').change(generate_immediate_feedback);
        $('#tuning_button').click(apply_changes);
        $('#tuning_reset_button').click(function() {
            $('#tuning_form')[0].reset();
            $('#tuning_form').trigger('change');
        })
    });
}

function generate_immediate_feedback() {
    $('#immediate_notice').show();
    $('#tuning_button').prop('disabled', true);

    var post_data = {
        configurations: [],
        code: editor.getValue()
    };
    $('.configuration').each(function () {
        post_data.configurations.push({
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
        url: api_base_url + 'forecast/',
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
        url: api_base_url + 'configure/',
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
        refresh_technician_diagram(false);
    });
}

function update_immediate_forecast(data) {
    var chart = $('#tech_live_diagram').highcharts();
    cleanup_diagram();
    $.each(data, function(index, sensor) {
        $.each(sensor.data, function(index, value){
            value[0] = new Date(value[0]).getTime();
        });
        chart.addSeries({
            name: sensor.name + ' (' + sensor.device + ') (predicted)',
            data: sensor.data,
            color: colors_modified[index],
            dashStyle: 'shortdot',
            tooltip: {
                valueSuffix: ' ' + sensor.unit
            },
            visible: chart.series[index].visible
        }, false);
    });
    chart.redraw();
}

function cleanup_diagram(chart) {
    var chart = $('#tech_live_diagram').highcharts();
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

function get_input_field_tuning(namespace, key, data) {
    var device_id = namespaces.indexOf(namespace);
    var output =
            '<div class="col-sm-6"><div class="form-group">' +
                '<label for="' + namespace + '_' + key + '">' + get_text(key) + ' (' + data.device + ')</label>';
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
function initialize_technician_editor() {
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

    update_snippet_list();
    update_user_code();

    $("#save_snippet").submit(function(event) {
        event.preventDefault();
        $.postJSON(api_base_url + "snippets/", {
            name: $("#snippet_name").val(),
            code: editor.getValue()
        }, function(data) {
            editor.setValue(data['code'], 1);
            update_snippet_list();
        });
    });

    $("#load_snippet").submit(function(event) {
        event.preventDefault();
        $.postJSON(api_base_url + "snippets/", {
            name: $("#code_snippets").val()
        }, function(data) {
            editor.setValue(data['code'], 1);
        });
        $('#snippet_name').val($("#code_snippets").val());
    });

    $("#editor_apply_button").click(function() {
        $.postJSON(api_base_url + "code/", {
            code: editor.getValue()
        }, function(data) {
            if (data['status'] == '1') {
                editor.setValue(data['code'], 1);
            } else {
                console.log('Failed to apply');
            }
        });
    });

    $("#editor_simulate_button").click(generate_immediate_feedback);
}

function update_snippet_list() {
    $("#code_snippets").empty();
    $.getJSON(api_base_url + 'snippets/', function(data) {
        $.each(data, function(index, snippet) {
             $("#code_snippets").append('<option>' + snippet + '</option>');
        });
    });
}

function update_user_code() {
    $.getJSON(api_base_url + 'code/', function(data) {
        editor.setValue(data['code'], 1);
    });
}
