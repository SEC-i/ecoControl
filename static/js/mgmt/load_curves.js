var sensor_list = null;

// READY
$(function() {
    $.getJSON("/api/sensors/", function(sensor_data) {
        sensor_list = sensor_data;
        $.getJSON("/api2/loads/", function(loads_data) {
            initialize_diagram(loads_data);
        });
    });
});

function initialize_diagram(loads_data) {
    var types = ['thermal', 'warmwater', 'electrical'];
    $.each(types, function (index, type) {
        $('#' + type + '_container').highcharts({
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: ''
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: [{
                min: 0,
                labels: {
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: '',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
            }],
            tooltip: {
                shared: true,
                valueDecimals: 2
            },
            series: [],
            credits: {
                enabled: false
            }
        });
        update_diagram(type, loads_data);
    });
}

function update_diagram(type, loads_data) {
    var chart = $('#' + type + '_container').highcharts();
    $.each(loads_data[type], function (sensor_id, data){
        var sensor = get_sensor(sensor_id);

        var series_data = [];
        $.each(data, function(index, value) {
            series_data.push([value[0] * 1000, value[1]]);
        });
        
        chart.addSeries({
            name: sensor.name + ' #' + sensor.id,
            data: series_data
        }, false);

        chart.yAxis[0].update({
            labels: {
                format: '{value}' + sensor.unit
            },
            title: {
                text: sensor.name + ' in ' + sensor.unit
            }
        }, false);
    });
    chart.redraw();
}

function get_sensor(sensor_id) {
    if (sensor_list == null) {
        return null;
    }

    var output = null;
    $.each(sensor_list, function (index, sensor) {
        if (sensor.id == sensor_id) {
            output = sensor;
            return false;
        }
    });
    return output;
}