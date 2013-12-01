var series_data = [];

function draw_diagram(){
    $.get( api_url + "device/" + device_id + "/entrieshc/start/" + range_start + "/end/" + range_end + "/")
        .done(function(data){

        series_data = [];

        $.each(data, function(index, value){
            $.each(value['data'], function(data_index, data_value){
                data_value[0] = new Date(data_value[0]);
                data_value[1] = parseFloat(data_value[1]);
            });

            series_data.push(
                {
                    name: value['name'],
                    data: value['data'],
                    tooltip: {
                        valueSuffix: ' ' + value['unit']
                    },
                }
                );
        });

        $("#diagram_container").highcharts('StockChart', {
            chart: {
                type: 'spline',
            },
            rangeSelector: {
                buttons: [{
                    type: 'hour',
                    count: 1,
                    text: '1h'
                }, {
                    type: 'hour',
                    count: 6,
                    text: '6h'
                }, {
                    type: 'hour',
                    count: 12,
                    text: '12h'
                }, {
                    type: 'day',
                    count: 1,
                    text: '1D'
                }, {
                    type: 'all',
                    count: 1,
                    text: 'All'
                }],
                selected: 2,
            },
            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: { // don't display the dummy year
                    month: '%e. %b',
                    year: '%b'
                }
            },
            yAxis: {
                min: 0,
                plotLines : (device_id==2?[{
                    value : 500,
                    color : 'red',
                    dashStyle : 'shortdash',
                    width : 1,
                    label : {
                        text : 'Water too low'
                    }
                }]:[]),
            },
            tooltip : {
                valueDecimals : 2
            },
            plotOptions: {
                series: {
                    marker: {
                        enabled: false
                    },
                    lineWidth: 1,
                }
            },
            series: series_data,
            credits: {
                enabled: false
            },
        });
    });
}