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
        url = './api/data/';
        if (current_time != undefined) {
            url += current_time + '/';
        }
        $.getJSON(url, function(data) {
            update_setup(data);
            update_diagram(data);
            current_time = data['past']['time'][data['past']['time'].length - 1];
        });
    }
    setTimeout(refresh, 2000);
}

function update_setup(data) {
    $.each(data['past'], function(key, value) {
        update_item(key, value[value.length - 1], '');
    });
    $.each(data['future'], function(key, value) {
        update_item(key, value[value.length - 1], '_predicted');
    });
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

function update_diagram(data) {
    var chart = $('#simulation_diagram').highcharts();
    var past = data['past'];

    for (var i = 0; i < past['time'].length; i++) {
        var timestamp = get_timestamp(past['time'][i]);
        $.each(fields, function(index, value) {
            chart.series[index].addPoint([timestamp, past[value][i]], false);
        });
    };
    chart.xAxis[0].plotLinesAndBands[0].options['value'] = timestamp; // moves vertical line to end of past data set

    update_forecast(data['future'], false);
}

function update_forecast(data, unsaved) {
    var chart = $('#simulation_diagram').highcharts();

    new_data = [
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ];

    for (var i = 0; i < data['time'].length; i++) {
        var timestamp = get_timestamp(data['time'][i]);
        $.each(fields, function(index, value) {
            new_data[index].push([timestamp, data[value][i]]);
        });
    };

    for (var i = 0; i < 7; i++) {
        if (!unsaved) {
            chart.series[7 + i].setData(new_data[i], false);
        } else {
            chart.series[14 + i].setData(new_data[i], false);
        }
    };

    chart.redraw();
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