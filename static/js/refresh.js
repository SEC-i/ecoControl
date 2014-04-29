var current_time = 0;
var fields = [
    'cu_workload',
    'plb_workload',
    'hs_temperature',
    'thermal_consumption',
    'warmwater_consumption',
    'outside_temperature',
    'electrical_consumption'
];

function refresh() {
    if (refresh_gui) {
        url = '/api/data/';
        if (current_time != undefined) {
            url += current_time + '/';
        }
        $.getJSON(url, function(data) {
            update_setup(data);
            update_diagram(data);
            if (data[0]['data'].length > 0) {
                current_time = data[0]['data'][data[0]['data'].length - 1][0];
            }
        }).done(function(){
            $.getJSON('/api/forecast/', function(data) {
                update_diagram(data, true);
            });
        });
                
    }
    setTimeout(refresh, 2000);
}

function update_setup(data) {
    // $.each(data, function(index, value) {
    //     update_item(value.key, value[value.length - 1], '');
    // });
}

function update_item(key, value, suffix) {
    var item = $('.' + key + suffix);
    if (item.length) { // check if item exists
        switch (key) {
            case "time":
                item.text($.format.date(new Date(parseFloat(value) * 1000), "dd.MM.yyyy HH:MM"));
                break;
            case "code_execution_status":
                if (value == 1) {
                    item.removeClass('badge-danger');
                    item.addClass('badge-success');
                    item.text('OK');
                } else {
                    item.removeClass('badge-success');
                    item.addClass('badge-danger');
                    item.text('Fail');
                }
                break;
            default:
                item.text(value + " " + systems_units[key]);
        }
    }
    if (key == "time") {
        $('#live_data_time' + suffix).text($.format.date(new Date(parseFloat(value) * 1000), "dd.MM.yyyy HH:MM"));
    }
}

function update_diagram(data, forecast) {
    forecast = typeof forecast !== 'undefined' ? forecast : false;

    var chart = $('#simulation_diagram').highcharts();

    $.each(data, function(index, sensor_value) {
        if (forecast) {
            var data_set = [];
            $.each(sensor_value.data, function(index2, sensor_data) {
                data_set.push([sensor_data[0], parseFloat(sensor_data[1])]);
            });
            chart.series[index * 2 + 1].setData(data_set, false);
        } else {
            $.each(sensor_value.data, function(index2, sensor_data) {
                chart.series[index * 2].addPoint([sensor_data[0], parseFloat(sensor_data[1])], false);
            });
        }
    });

    if (forecast && current_time != undefined) {
        chart.xAxis[0].plotLinesAndBands[0].options['value'] = current_time; // moves vertical line to end of past data set
    }

    chart.redraw();
}

function immediate_feedback() {
    var post_data = $("#settings").serialize();
    for (var i = 0; i < 24; i++) {
        post_data += "&daily_thermal_demand_" + i + "=" + ($("#daily_thermal_demand_" + i).slider("value") / 100);
    }
    for (var i = 0; i < 24; i++) {
        post_data += "&daily_electrical_variation_" + i + "=" + ($("#daily_electrical_variation_" + i).slider("value") / 10000);
    }
    post_data += "&forecast_time=" + 3600.0 * 24 * 30;
    $.post("/api/forecasts/", post_data, function(data) {
        update_forecast(data, true);
    });
}

function update_setting(data) {
    $.each(data, function(key, value) {
        switch (key) {
            case "daily_thermal_demand":
                $.each(value, function(index, hour_value) {
                    $("#daily_thermal_demand_" + index).slider("value", hour_value * 100);
                });
                break;
            case "daily_electrical_variation":
                $.each(value, function(index, hour_value) {
                    $("#daily_electrical_variation_" + index).slider("value", hour_value * 10000);
                });
                break;
            case "cu_mode":
                if (value == 0)
                    $("#cu_mode_thermal_driven").attr('checked', true);
                else
                    $("#cu_mode_electrical_driven").attr('checked', true);
                break;
            case "code_snippets":
                $.each(value, function(index, snippet_name) {
                    $("#snippets").append('<option>' + snippet_name + '</option>');
                });
                break;
            default:
                $("#form_" + key).val(value);
        }
    });
}