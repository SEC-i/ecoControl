var current_time = 0;

function refresh() {
    if (refresh_gui) {
        $.getJSON("./api/data/" + current_time + "/", function (data) {
            update_setup(data);
            update_diagram(data);
            current_time = data['past']['time'][data['past']['time'].length - 1];
        });
    }
}

function update_setup(data) {
    $.each(data['past'], function (key, value) {
        update_item(key, value[value.length - 1], '');
    });
    $.each(data['future'], function (key, value) {
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
    if (key == "time"){
        $('#live_data_time' + suffix).text($.format.date(new Date(parseFloat(value) * 1000), "dd.MM.yyyy HH:MM"));
    }
}

function update_diagram(data) {
    var chart = $('#simulation_diagram').highcharts();
    var past = data['past'];
    var future = data['future'];

    new_data = [
        [],
        [],
        [],
        [],
        [],
        [],
        []
    ];
    for (var i = 0; i < past['time'].length; i++) {
        var timestamp = get_timestamp(past['time'][i]);
        chart.series[0].addPoint([timestamp, past['cu_workload'][i]], false);
        chart.series[1].addPoint([timestamp, past['plb_workload'][i]], false);
        chart.series[2].addPoint([timestamp, past['hs_temperature'][i]], false);
        chart.series[3].addPoint([timestamp, past['thermal_consumption'][i]], false);
        chart.series[4].addPoint([timestamp, past['warmwater_consumption'][i]], false);
        chart.series[5].addPoint([timestamp, past['outside_temperature'][i]], false);
        chart.series[6].addPoint([timestamp, past['electrical_consumption'][i]], false);
    };
    chart.xAxis[0].plotLinesAndBands[0].options['value'] = timestamp; // moves vertical line to end of past data set
    for (var i = 0; i < future['time'].length; i++) {
        var timestamp = get_timestamp(future['time'][i]);
        new_data[0].push([timestamp, future['cu_workload'][i]]);
        new_data[1].push([timestamp, future['plb_workload'][i]]);
        new_data[2].push([timestamp, future['hs_temperature'][i]]);
        new_data[3].push([timestamp, future['thermal_consumption'][i]]);
        new_data[4].push([timestamp, future['warmwater_consumption'][i]]);
        new_data[5].push([timestamp, future['outside_temperature'][i]]);
        new_data[6].push([timestamp, future['electrical_consumption'][i]]);
    };

    for (var i = new_data.length - 1; i >= 0; i--) {
        chart.series[7 + i].setData(new_data[i], false);
    };

    chart.redraw();
}

function update_forecast(data){
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
        new_data[0].push([timestamp, data['cu_workload'][i]]);
        new_data[1].push([timestamp, data['plb_workload'][i]]);
        new_data[2].push([timestamp, data['hs_temperature'][i]]);
        new_data[3].push([timestamp, data['thermal_consumption'][i]]);
        new_data[4].push([timestamp, data['warmwater_consumption'][i]]);
        new_data[5].push([timestamp, data['outside_temperature'][i]]);
        new_data[6].push([timestamp, data['electrical_consumption'][i]]);
    };

    for (var i = 0; i < 7; i++) {
        chart.series[14+i].setData(new_data[i], false);
        chart.series[14+i].setVisible(true, false);
    };

    chart.redraw();
}

function update_setting(data) {
    $.each(data, function (key, value) {
        switch (key) {
        case "daily_thermal_demand":
            $.each(value, function (index, hour_value) {
                $("#daily_thermal_demand_" + index).slider("value", hour_value * 100);
            });
            break;
        case "daily_electrical_variation":
            $.each(value, function (index, hour_value) {
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
            $.each(value, function (index, snippet_name) {
                $("#snippets").append('<option>' + snippet_name + '</option>');
            });
            break;
        default:
            $("#form_" + key).val(value);
        }
    });
}