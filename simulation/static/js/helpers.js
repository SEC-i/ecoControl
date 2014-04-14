function get_timestamp(string) {
    return new Date(parseFloat(string) * 1000).getTime();
}

function hide_forecasts() {
    var chart = $('#simulation_diagram').highcharts();
    for (var i = 0; i < 7; i++) {
        chart.series[14+i].setVisible(false, false);
    };
    chart.redraw();
}