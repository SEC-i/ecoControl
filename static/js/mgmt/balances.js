// READY
$(function() {
    initialize_diagram();
    initialize_diagram_filters();
});

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
            var chart = $('#diagram_container').highcharts();
            var year = parseInt($(this).val());
            if ($(this).is(":checked")) {
                var found = false;
                $.each(chart.series, function(index, series) {
                    if (series['name'].substr(series['name'].length - 4) == year) {
                        series.show(false);
                        found = true;
                    }
                });
                if (!found) {
                    $.getJSON("/api2/balance/total/" + year + "/", function(data) {
                        var series_data = {
                            name: 'Total Balances in ' + year,
                            type: 'column',
                            data: []
                        };
                        $.each(data, function(date, monthly_data) {
                            series_data['data'].push(monthly_data.balance);
                        });
                        chart.addSeries(series_data);
                    });
                }
            } else {
                $.each(chart.series, function(index, series) {
                    if (series['name'].substr(series['name'].length - 4) == year) {
                        series.hide(false);
                    }
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
                $.each(chart.series, function(index, series) {
                    series.setVisible(true, false);
                });
            }

            // finally redraw the chart
            chart.redraw();
        });

        // preselect first filter
        $('.diagram_filter').first().parent().button('toggle');
    });
}


