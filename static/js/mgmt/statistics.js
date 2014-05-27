var sensor_list = null;
var headlines = ['Month', '', ''];
var table_data = [];

// READY
function manager_statistics_ready() {
    $.each(get_text('months'), function(index, month) {
        table_data.push([month, 0, 0]);
    });

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

        $.getJSON('/api/history/', function(history_data) {
            $.each(history_data, function(index, year) {
                $('.years_list').append(
                    '<option value="' + year + '">' + year + '</option>'
                );
            });
        }).done(function() {
            initialize_diagram();
            $('.series_list').change(function () {
                var sensor_id = $(this).val();
                var sensor = get_sensor(sensor_id);
                var target = $(this).attr('data-target');
                var year = $('#years_' + target).val();

                var url = '/api/avgs/sensor/' + sensor_id + '/year/' + year + '/';
                if ($(this).find(":selected").attr('data-aggregation') == 'sum') {
                    var url = '/api/sums/sensor/' + sensor_id + '/year/' + year + '/';
                }

                $.getJSON(url, function(data) {
                    var chart = $('#diagram_container').highcharts();
                    var series_id = 0;
                    if (target == 'right') {
                        series_id = 1;
                    }

                    var series_data = [];
                    $.each(data, function(index, value) {
                        series_data.push([index, value.total]);
                    });
                    chart.series[series_id].update({
                        name: sensor.name + ' (' + year + ')'
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

                    update_table(data, sensor.name + ' in ' + sensor.unit, target == 'right');
                });
            });

            $('.years_list').change(function () {
                $('.series_list').change();
            });

            if ($('#series_left option').size() >= 2) {
                $("#series_right option:nth-child(2)").prop("selected", true);
            }

            $('.series_list').change();
        });
    });

    $('#export_button').click(function(event) {
        event.preventDefault();
        export_table($('#mgmt_statistics_table_container'));
    });
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

function initialize_diagram() {
    $('#diagram_container').highcharts({
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: ''
        },
        xAxis: {
            categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
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

function update_table(data, col_title, right) {
    if (right) {
        var offset = 2;
    } else {
        var offset = 1;
    }

    headlines[offset] = col_title;

    $.each(data, function(index, row) {
        table_data[index][offset] = Math.round(row.total * 100) / 100;
    });

    draw_table($('#mgmt_statistics_table_container'), headlines, table_data);

}