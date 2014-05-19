var sensor_list = null;
// READY
$(function() {
    $.getJSON('/api/sensors/', function(data) {
        sensor_list = data;
        $.each(sensor_list, function(index, sensor) {
            if (sensor.sum) {
                $('.series_list').append(
                    '<option value="' + sensor.id + '" data-aggregation="sum">SUM ' + sensor.name + ' (' + sensor.device + ')</option>'
                );
            }
            if (sensor.avg) {
                $('.series_list').append(
                    '<option value="' + sensor.id + '" data-aggregation="avg">AVG ' + sensor.name + ' (' + sensor.device + ')</option>'
                );
            }
        });
        initialize_diagram();
        $('.series_list').change(function () {
            var sensor_id = $(this).val();
            var sensor = get_sensor(sensor_id);
            var target = $(this).attr('data-target');
            var url = '/api2/avgs/' + sensor_id + '/';
            if ($(this).find(":selected").attr('data-aggregation') == 'sum') {
                var url = '/api2/sums/' + sensor_id + '/';
            }

            $.getJSON(url, function(data) {
                var chart = $('#diagram_container').highcharts();
                var series_id = 0;
                if (target == 'right') {
                    series_id = 1;
                }

                var series_data = [];
                $.each(data, function(index, value) {
                    series_data.push([parseInt(value.date) * 1000, value.total]);
                });
                chart.series[series_id].update({
                    name: sensor.name
                }, false);
                chart.yAxis[series_id].update({
                    labels: {
                        format: '{value}' + sensor.unit
                    },
                    title: {
                        text: sensor.name + ' in ' + sensor.unit
                    }
                }, false);
                chart.series[series_id].setData(series_data,true);
            });
        });
    }).done(function() {
        if ($('#series_left option').size() >= 2) {
            $("#series_right option:nth-child(2)").prop("selected", true);
        }

        $('.series_list').change();
    });
});

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

function initialize_diagram() {
    $('#diagram_container').highcharts({
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: ''
        },
        xAxis: {
            type: 'datetime',
        },
        yAxis: [{
            labels: {
                style: { color: Highcharts.getOptions().colors[1] }
            },
            title: {
                text: '',
                style: { color: Highcharts.getOptions().colors[1] }
            },
        }, {
            labels: {
                style: { color: Highcharts.getOptions().colors[0] }
            },
            title: {
                text: '',
                style: { color: Highcharts.getOptions().colors[0] }
            },
            opposite: true
        }],
        tooltip: {
            shared: true,
            valueDecimals: 2
        },
        series: [{
            type: 'column',
            yAxis: 0,
            data: [],
        }, {
            type: 'column',
            yAxis: 1,
            data: [],
        }],
        credits: {
            enabled: false
        }
    });
}