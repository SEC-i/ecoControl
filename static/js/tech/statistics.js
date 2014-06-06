// READY
function technician_statistics_ready() {
    $.getJSON(api_base_url + 'statistics/monthly/', function(data) {
        var cu_series_data_1 = [{
            type: 'column',
            name: get_text('gas_consumption'),
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

        var cu_statistics_table_headlines = ['Month', 'Gas Consumption', 'Hours of Operation', 'Power-Ons', 'Average Workload'];
        var plb_statistics_table_headlines = ['Month', 'Gas Consumption', 'Hours of Operation', 'Power-Ons'];
        
        var cu_statistics_table_data = [];
        var plb_statistics_table_data = [];

        $.each(data, function(index, values) {
            $.each(values, function(system, system_data) {
                if (system_data.type == '2') {
                    cu_series_data_1[0].data.push(system_data['total_gas_consumption']);
                    cu_series_data_1[1].data.push(system_data['hours_of_operation']);

                    cu_series_data_2[0].data.push(system_data['power_ons']);
                    cu_series_data_2[1].data.push(system_data['average_workload']);

                    cu_statistics_table_data.push([
                        get_text('months')[index], system_data['total_gas_consumption'] + 'kWh',
                        system_data['hours_of_operation'] + 'h', system_data['power_ons'],
                        system_data['average_workload'] + '%'
                    ]);
                } else if (system_data.type == '3') {
                    plb_series_data_1[0].data.push(system_data['total_gas_consumption']);
                    plb_series_data_1[1].data.push(system_data['hours_of_operation']);
                    plb_series_data_2[0].data.push(system_data['power_ons']);

                    plb_statistics_table_data.push([
                        get_text('months')[index], system_data['total_gas_consumption'] + 'kWh',
                        system_data['hours_of_operation'] + 'h', system_data['power_ons']
                    ]);
                }
            });
        });

        $('#cu_statistics_1').highcharts({
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: 'CU Gas Consumption and Hours of Operation'
            },
            xAxis: {
                categories: get_text('months')
            },
            yAxis: [{
                labels: {
                    format: '{value}kWh',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
                title: {
                    text: 'Gas Consumption in kWh',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
            }, {
                labels: {
                    format: '{value}h',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: 'Hours of Operations in hours',
                    style: { color: Highcharts.getOptions().colors[1] }
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
                text: 'CU Power Ons and Average Workload'
            },
            xAxis: {
                categories: get_text('months')
            },
            yAxis: [{
                labels: {
                    format: '{value}',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
                title: {
                    text: 'Power Ons',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
            }, {
                labels: {
                    format: '{value}%',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: 'Average Workload in %',
                    style: { color: Highcharts.getOptions().colors[1] }
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
                text: 'PLB Gas Consumption and Hours of Operation'
            },
            xAxis: {
                categories: get_text('months')
            },
            yAxis: [{
                labels: {
                    format: '{value}kWh',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
                title: {
                    text: 'Gas Consumption in kWh',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
            }, {
                labels: {
                    format: '{value}h',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: 'Hours of Operations in hours',
                    style: { color: Highcharts.getOptions().colors[1] }
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
                text: 'PLB Power Ons'
            },
            xAxis: {
                categories: get_text('months')
            },
            yAxis: [{
                labels: {
                    format: '{value}',
                    style: { color: Highcharts.getOptions().colors[0] }
                },
                title: {
                    text: 'Power Ons',
                    style: { color: Highcharts.getOptions().colors[0] }
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

        draw_table($('#cu_statistics_table .panel-body'), cu_statistics_table_headlines, cu_statistics_table_data);
        draw_table($('#plb_statistics_table .panel-body'), plb_statistics_table_headlines, plb_statistics_table_data);

        $('#cu_export_button').click(function(event) {
            event.preventDefault();
            export_table($('#cu_statistics_table .panel-body'));
        });

        $('#plb_export_button').click(function(event) {
            event.preventDefault();
            export_table($('#plb_statistics_table .panel-body'));
        });
    });
}
