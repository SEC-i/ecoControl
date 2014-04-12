function refresh() {
    if (refresh_gui) {
        $.getJSON("./api/data/", function (data) {
            update_setup(data);
            update_diagram(data);
        });
    }
}

function update_setup(data) {
    data = data['past'];
    $.each(data, function (key, value) {
        value = value[value.length - 1];
        var item = $('.' + key);
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
    });
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
        [],
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
        new_data[0].push([timestamp, past['cu_workload'][i]]);
        new_data[1].push([timestamp, past['plb_workload'][i]]);
        new_data[2].push([timestamp, past['hs_temperature'][i]]);
        new_data[3].push([timestamp, past['thermal_consumption'][i]]);
        new_data[4].push([timestamp, past['warmwater_consumption'][i]]);
        new_data[5].push([timestamp, past['outside_temperature'][i]]);
        new_data[6].push([timestamp, past['electrical_consumption'][i]]);
    };
    chart.xAxis[0].plotLinesAndBands[0].options['value'] = timestamp; // moves vertical line to end of past data set
    for (var i = 0; i < future['time'].length; i++) {
        var timestamp = get_timestamp(future['time'][i]);
        new_data[7].push([timestamp, future['cu_workload'][i]]);
        new_data[8].push([timestamp, future['plb_workload'][i]]);
        new_data[9].push([timestamp, future['hs_temperature'][i]]);
        new_data[10].push([timestamp, future['thermal_consumption'][i]]);
        new_data[11].push([timestamp, future['warmwater_consumption'][i]]);
        new_data[12].push([timestamp, future['outside_temperature'][i]]);
        new_data[13].push([timestamp, future['electrical_consumption'][i]]);
    };

    for (var i = new_data.length - 1; i >= 0; i--) {
        chart.series[i].setData(new_data[i], false);
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