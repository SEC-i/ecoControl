var plotline_timestamp = null;

// READY
$(function() {
    $.getJSON("/api/status/", function(data) {
        if (data['system_status'] == 'init') {
            redirect_to_settings();
        } else {
            initialize_diagram();
        }
    });
});

function initialize_diagram() {
    Highcharts.setOptions({
        global: {
            useUTC: false
        }
    });

    var navigator_data = [];
    var series = [];
    $.getJSON('/api/data/', function(data) {
        $.each(data, function(index, sensor) {
            series.push({
                name: sensor.name + ' (' + sensor.device + ')',
                data: sensor.data,
                color: colors_past[index],
                id: sensor.id,
                tooltip: {
                    valueSuffix: ' ' + sensor.unit
                }
            });
        });
    }).done(function () {
        $.getJSON('/api/forecast/', function(forecast_data) {
            $.each(forecast_data, function(index, sensor) {
                $.merge(series[index].data, sensor.data);
            });
            plotline_timestamp = forecast_data[0].data[0][0];
        }).done(function () {
            // Create the chart
            $('#simulation_diagram').highcharts('StockChart', {
                chart: {
                    height: 500,
                    zoomType: 'xy',
                    events: {
                        load: update_now_line,
                        redraw: update_now_line
                    }
                },
                navigator: {
                    series: {
                        id: 'navigator',
                        data: navigator_data
                    },
                    adaptToUpdatedData: false
                },
                legend: {
                    enabled: true
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
                        text: '1D'
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
                        text: 'All'
                    }],
                    selected: 5,
                    inputEnabled: false
                },
                xAxis: {
                    plotLines: [{
                        id: 'now_area',
                    }, {
                        id: 'now',
                    }]
                },
                tooltip: {
                    valueDecimals: 2
                },
                lang: {
                    noData: "Loading data..."
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
            });

            setTimeout(refresh, 10000);
        });
    });
}

function refresh() {
    var chart = $('#simulation_diagram').highcharts();
    var series_data = []
    $.getJSON('/api/data/', function(data) {
        $.each(data, function(index, sensor) {
            series_data.push(sensor.data);
        });
    }).done(function () {
        $.getJSON('/api/forecast/', function(forecast_data) {
            $.each(forecast_data, function(index, sensor) {
                chart.series[index].setData($.merge(series_data[index], sensor.data), false);
            });

            plotline_timestamp = forecast_data[0].data[0][0];
            update_now_line();
        }).done(function () {
            chart.redraw();

            setTimeout(refresh, 10000);
        });
    });
}

function update_now_line() {
    var chart = $('#simulation_diagram').highcharts();
    // chart.xAxis[0].removePlotLine('now_area');
    // chart.xAxis[0].addPlotLine({
    //     id: 'now_area',
    //     value: plotline_timestamp + 7 * 24 * 60 * 60 * 1000,
    //     width: chart.chartWidth/2* 0.92,
    //     color: '#F0F0F0',
    //     label: {
    //         text: 'Forecast',
    //         rotation: 0,
    //         align: 'center',
    //         y: 32,
    //         x: 6
    //     }
    // });
    chart.xAxis[0].removePlotLine('now');
    chart.xAxis[0].addPlotLine({
        id: 'now',
        value: plotline_timestamp,
        width: 2,
        color: 'red',
        label: {
            text: 'Now',
            align: 'right',
            y: 32,
            x: 6
        }
    });
}