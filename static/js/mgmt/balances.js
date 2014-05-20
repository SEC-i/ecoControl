var diagram_types = ['balances', 'rewards', 'costs'];

// READY
$(function() {
    initialize_diagram();
    initialize_diagram_filters();
});

function initialize_diagram() {
    $.each(diagram_types, function(index, type) {
        $('#' + type + '_container').highcharts({
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: 'Monthly ' + type.charAt(0).toUpperCase() + type.slice(1)
            },
            xAxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            },
            yAxis: [{
                labels: {
                    format: '{value} €',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: 'Balances in €',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
            }],
            tooltip: {
                valueDecimals: 2
            },
            series: [],
            credits: {
                enabled: false
            }
        });
    });
}

function initialize_diagram_filters() {
    $.getJSON('/api2/history/', function(history_data) {
        $.each(history_data, function(index, year) {
            $('#diagram_filters').append(
                '<label class="btn btn-default">\
                <input class="btn diagram_filter" type="checkbox" value="' + year + '">\
                ' + year + '</label>');
        });
        $('.diagram_filter').change(function () {

            charts = [];
            $.each(diagram_types, function(index, type) {
                charts.push($('#' +type + '_container').highcharts());
            });
            var year = parseInt($(this).val());
            if ($(this).is(":checked")) {
                var found = false;
                $.each(charts, function(index, chart) {
                    $.each(chart.series, function(index2, series) {
                        if (series['name'].substr(series['name'].length - 4) == year) {
                            series.show(false);
                            found = true;
                        }
                    });
                });
                if (!found) {
                    $.getJSON("/api2/balance/total/" + year + "/", function(data) {
                        var balances = {
                            name: 'Total Balances in ' + year,
                            type: 'column',
                            data: []
                        };
                        var rewards = {
                            name: 'Total Rewards in ' + year,
                            type: 'column',
                            data: []
                        };
                        var costs = {
                            name: 'Total Costs in ' + year,
                            type: 'column',
                            data: []
                        };
                        $.each(data, function(date, monthly_data) {
                            balances['data'].push(monthly_data.balance);
                            rewards['data'].push(monthly_data.rewards);
                            costs['data'].push(monthly_data.costs);
                        });
                        charts[0].addSeries(balances);
                        charts[1].addSeries(rewards);
                        charts[2].addSeries(costs);
                    });
                }
            } else {
                $.each(charts, function(index, chart) {
                    $.each(chart.series, function(index, series) {
                        if (series['name'].substr(series['name'].length - 4) == year) {
                            series.hide(false);
                        }
                    });
                });
            }

            // if all series are unchecked, show all
            var all_unchecked = true;
            $(".diagram_filter").each(function() {
                if ($(this).is(":checked")) {
                    all_unchecked = false;
                }
            });
            if (all_unchecked) {
                $.each(charts, function(index, chart) {
                    $.each(chart.series, function(index, series) {
                        series.setVisible(true, false);
                    });
                });
            }

            // finally redraw all charts
            $.each(charts, function(index, chart) {
                chart.redraw();
            });
        });

        // preselect first filter
        $('.diagram_filter').first().parent().button('toggle');
    });
}


