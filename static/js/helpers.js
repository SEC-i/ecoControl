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


var colors_past = ['#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce', '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'];
var colors_future = ['#3895ff', '#153a61', '#a8e329', '#b80000', '#20cef5', '#623896', '#ffa561', '#9ac1ff', '#eb2d2d', '#c6f07f'];
var colors_modified = ['#225999', '#000000', '#5c7d16', '#520000', '#13788f', '#201230', '#b36a32', '#5675a6', '#851919', '#728a49'];
