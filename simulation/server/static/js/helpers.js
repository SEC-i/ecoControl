function get_timestamp(string) {
    return new Date(parseFloat(string) * 1000).getTime();
}

function hide_forecasts() {
    var chart = $('#simulation_diagram').highcharts();
    for (var i = 0; i < 7; i++) {
        chart.series[14 + i].setData([], false);
    };
    chart.redraw();
}

function filter_series() {
    var chart = $('#simulation_diagram').highcharts();
    var all_unchecked = true;

    $(".diagram_filter").each(function() {
        i = parseInt($(this).val());
        visible = $(this).is(":checked");
        chart.series[i].setVisible(visible, false);
        chart.series[i + 7].setVisible(visible, false);
        chart.series[i + 14].setVisible(visible, false);
        if ($(this).is(":checked")) {
            all_unchecked = false;
        }
    });
    if (all_unchecked) {
        $.each(chart.series, function(index, series) {
            series.setVisible(true, false);
        });
    }
    chart.redraw();
}