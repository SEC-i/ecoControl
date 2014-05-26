var sensor_list = null;

// READY
function manager_load_curves_ready() {
    $.getJSON("/api/sensors/", function(sensor_data) {
        sensor_list = sensor_data;
        $.getJSON("/api2/loads/", function(loads_data) {
            initialize_load_diagrams(loads_data);
        });
    });
}

function initialize_load_diagrams(loads_data) {
    var types = ['thermal', 'warmwater', 'electrical'];
    $.each(types, function (index, type) {
        var diagram_data = get_diagram_data(type, loads_data[type])
        $('#' + type + '_container').highcharts({
            chart: {
                type: 'spline'
            },
            title: {
                text: ''
            },
            xAxis: {
                type: 'datetime'
            },
            plotOptions: {

                spline: {
                    lineWidth: 2,
                    states: {
                        hover: {
                            lineWidth: 4
                        }
                    },
                    marker: {
                        enabled: false
                    },
                }
            },
            yAxis: diagram_data.yaxis,
            tooltip: {
                valueDecimals: 2
            },
            series: diagram_data.series,
            credits: {
                enabled: false
            }
        });
    });
}

function get_diagram_data(type, input_data) {
    output = {
        'series' : [],
        'yaxis' : []
    };
    $.each(input_data, function (sensor_id, sensor_data){
        var sensor = get_sensor(sensor_id);
        
        output['series'].push({
            name: sensor.name + ' #' + sensor.id,
            data: sensor_data,
        });

        output['yaxis'].push({
            min: 0,
            labels: {
                format: '{value}' + sensor.unit
            },
            title: {
                text: sensor.name + ' in ' + sensor.unit
            }
        });
    });
    
    return output;
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