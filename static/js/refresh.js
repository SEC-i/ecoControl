var current_time = null;
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
    url = '/api/data/';
    if (current_time != null) {
        url += current_time + '/';
    }
    $.getJSON(url, function(data) {
        if (data[0]['data'].length > 0) {
            current_time = data[0]['data'][data[0]['data'].length - 1][0];
        }
        $.getJSON('/api/forecast/', function(forecast) {
            update_diagram(data);
            if (forecast.length > 0) {
                update_diagram(forecast, true);
            }
        })
    }).done(function () {
            setTimeout(refresh, 2000);
        });;
}

function update_diagram(data, forecast) {
    forecast = typeof forecast !== 'undefined' ? forecast : false;

    var chart = $('#simulation_diagram').highcharts();

    $.each(data, function(index, sensor_value) {
        if (!forecast) {
            $.each(sensor_value.data, function(index2, sensor_data) {
                chart.series[index * 2].addPoint([sensor_data[0] * 1000, parseFloat(sensor_data[1])], false);
            });
        } else {
            var data_set = [];
            $.each(sensor_value.data, function(index2, sensor_data) {
                data_set.push([sensor_data[0] * 1000, parseFloat(sensor_data[1])]);
            });
            chart.series[index * 2 + 1].setData(data_set, false);
        }
    });

    if (forecast && current_time != undefined) {
        chart.xAxis[0].plotLinesAndBands[0].options['value'] = current_time; // moves vertical line to end of past data set
    }

    chart.redraw();
}