// READY
$(function() {
    $.getJSON('/api/statistics/monthly/', function(data) {
        var cu_series_data = [{
            type: 'column',
            name: 'Average Workload',
            yAxis: 0,
            data: [],
        }, {
            type: 'column',
            name: 'Gas Consumption',
            yAxis: 1,
            data: [],
        }, {
            type: 'spline',
            name: 'Power-Ons',
            yAxis: 1,
            data: [],
            marker: {
                lineWidth: 2,
                lineColor: Highcharts.getOptions().colors[3],
                fillColor: 'white'
            }
        }, {
            type: 'spline',
            name: 'Hours of Operation',
            yAxis: 2,
            data: [],
            marker: {
                lineWidth: 2,
                lineColor: Highcharts.getOptions().colors[4],
                fillColor: 'white'
            }
        }];

        var plb_series_data = [{
            type: 'column',
            name: 'Gas Consumption',
            yAxis: 1,
            data: [],
        }, {
            type: 'spline',
            name: 'Power-Ons',
            yAxis: 1,
            data: [],
            marker: {
                lineWidth: 2,
                lineColor: Highcharts.getOptions().colors[3],
                fillColor: 'white'
            }
        }, {
            type: 'spline',
            name: 'Hours of Operation',
            yAxis: 2,
            data: [],
            marker: {
                lineWidth: 2,
                lineColor: Highcharts.getOptions().colors[4],
                fillColor: 'white'
            }
        }];

        $.each(data, function(month, values) {
            $.each(values, function(system, system_data) {
                timestamp = parseInt(month) * 1000;
                if (system_data.type == '2') {
                    cu_series_data[0].data.push([timestamp, system_data['average_workload']]);
                    cu_series_data[1].data.push([timestamp, system_data['total_gas_consumption']]);
                    cu_series_data[2].data.push([timestamp, system_data['power_ons']]);
                    cu_series_data[3].data.push([timestamp, system_data['hours_of_operation']]);
                } else if (system_data.type == '3') {
                    plb_series_data[0].data.push([timestamp, system_data['total_gas_consumption']]);
                    plb_series_data[1].data.push([timestamp, system_data['power_ons']]);
                    plb_series_data[2].data.push([timestamp, system_data['hours_of_operation']]);
                }
            });
        });

        $('#cu_statistics').highcharts({
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
                    format: '{value}%',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
                title: {
                    text: 'Average Workload in %',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
            }, {
                labels: {
                    format: '{value}kWh',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: 'Gas Consumption in kWh',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                opposite: true
            }, {
                labels: {
                    enabled: false
                },
                title: {
                    text: null
                },
            }],
            tooltip: {
                shared: true
            },
            series: cu_series_data,
            credits: {
                enabled: false
            }
        });

        $('#plb_statistics').highcharts({
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
                    format: '{value}%',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
                title: {
                    text: 'Average Workload in %',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
                
            }, {
                labels: {
                    format: '{value}kWh',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: 'Gas Consumption in kWh',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                opposite: true
            }, {
                labels: {
                    enabled: false
                },
                title: {
                    text: null
                },
            }],
            tooltip: {
                shared: true
            },
            series: plb_series_data,
            credits: {
                enabled: false
            }
        });
    });
});