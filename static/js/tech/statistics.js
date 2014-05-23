// READY
$(function() {
    $.getJSON("/api/status/", function(data) {
        if (data['system_status'] == 'init') {
            redirect_to_settings();
        }
    }).done(function() {
        $.getJSON('/api/statistics/monthly/', function(data) {
            var cu_series_data_1 = [{
                type: 'column',
                name: 'Gas Consumption',
                yAxis: 0,
                data: [],
            }, {
                type: 'column',
                name: 'Hours of Operation',
                yAxis: 1,
                data: [],
            }];

            var cu_series_data_2 = [{
                type: 'column',
                name: 'Power-Ons',
                yAxis: 0,
                data: [],
            }, {
                type: 'column',
                name: 'Average Workload',
                yAxis: 1,
                data: [],
            }];

            var plb_series_data_1 = [{
                type: 'column',
                name: 'Gas Consumption',
                yAxis: 0,
                data: [],
            }, {
                type: 'column',
                name: 'Hours of Operation',
                yAxis: 1,
                data: [],
            }];

            var plb_series_data_2 = [{
                type: 'column',
                name: 'Power-Ons',
                data: [],
            }];

            $.each(data, function(month, values) {
                $.each(values, function(system, system_data) {
                    var timestamp = parseInt(month);
                    if (system_data.type == '2') {
                        cu_series_data_1[0].data.push([timestamp, system_data['total_gas_consumption']]);
                        cu_series_data_1[1].data.push([timestamp, system_data['hours_of_operation']]);
                        cu_series_data_2[0].data.push([timestamp, system_data['power_ons']]);
                        cu_series_data_2[1].data.push([timestamp, system_data['average_workload']]);
                    } else if (system_data.type == '3') {
                        plb_series_data_1[0].data.push([timestamp, system_data['total_gas_consumption']]);
                        plb_series_data_1[1].data.push([timestamp, system_data['hours_of_operation']]);
                        plb_series_data_2[0].data.push([timestamp, system_data['power_ons']]);
                    }
                });
            });

            $('#cu_statistics_1').highcharts({
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
                        format: '{value}kWh',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                    title: {
                        text: 'Gas Consumption in kWh',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                }, {
                    labels: {
                        format: '{value} hours',
                        style: { color: Highcharts.getOptions().colors[0] }
                    },
                    title: {
                        text: 'Hours of Operations in %',
                        style: { color: Highcharts.getOptions().colors[0] }
                    },
                    opposite: true
                }],
                tooltip: {
                    shared: true
                },
                series: cu_series_data_1,
                credits: {
                    enabled: false
                }
            });

            $('#cu_statistics_2').highcharts({
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
                        format: '{value}',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                    title: {
                        text: 'Power Ons',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                }, {
                    labels: {
                        format: '{value}%',
                        style: { color: Highcharts.getOptions().colors[0] }
                    },
                    title: {
                        text: 'Average Workload in %',
                        style: { color: Highcharts.getOptions().colors[0] }
                    },
                    opposite: true
                }],
                tooltip: {
                    shared: true
                },
                series: cu_series_data_2,
                credits: {
                    enabled: false
                }
            });

            $('#plb_statistics_1').highcharts({
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
                        format: '{value}kWh',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                    title: {
                        text: 'Gas Consumption in kWh',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                }, {
                    labels: {
                        format: '{value} hours',
                        style: { color: Highcharts.getOptions().colors[0] }
                    },
                    title: {
                        text: 'Hours of Operations in %',
                        style: { color: Highcharts.getOptions().colors[0] }
                    },
                    opposite: true
                }],
                tooltip: {
                    shared: true
                },
                series: plb_series_data_1,
                credits: {
                    enabled: false
                }
            });

            $('#plb_statistics_2').highcharts({
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
                        format: '{value}',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                    title: {
                        text: 'Power Ons',
                        style: { color: Highcharts.getOptions().colors[1] }
                    },
                }],
                tooltip: {
                    shared: true
                },
                series: plb_series_data_2,
                credits: {
                    enabled: false
                }
            });
        });
    });
});

function redirect_to_settings(show) {
    window.location.href = 'settings.html';    
}
