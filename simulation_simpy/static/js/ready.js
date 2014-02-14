var systems_units = {
    bhkw_workload: '%',
    bhkw_electrical_power: 'kW',
    bhkw_thermal_power: 'kW',
    bhkw_total_gas_consumption: 'kWh',
    hs_level: '%',
    plb_workload: '%',
    plb_thermal_power: 'kW',
    plb_total_gas_consumption: 'kWh',
    thermal_consumption: 'kW'
};

var series_data = [{
    name: 'bhkw_workload',
    data: [],
    tooltip: {
        valueSuffix: ' %'
    }
},
{
    name: 'plb_workload',
    data: [],
    tooltip: {
        valueSuffix: ' %'
    }
},
{
    name: 'hs_level',
    data: [],
    tooltip: {
        valueSuffix: ' %'
    }
},
{
    name: 'thermal_consumption',
    data: [],
    tooltip: {
        valueSuffix: ' kW'
    }
}];

$(function(){
    $.get( "./static/img/simulation.svg", function( data ) {
        var svg_item = document.importNode(data.documentElement,true);
        $("#simulation_scheme").append(svg_item);
    }, "xml");

    $.getJSON( "./api/settings/", function( data ) {
        $.each(data, function(key, value) {
            $("#form_" + key).val(value);
        });
    }).done(function(){
        $.getJSON( "./api/data/", function( data ) {
            var timestamp = get_timestamp(data['time']);
            $.each(data, function(key, value) {
                $.each(series_data, function(series_index, series_data) {
                    if(series_data['name'] == key){
                        series_data['data'].push([timestamp, parseFloat(value)]);
                    }
                });
            });
        }).done(function(){
            initialize_diagram();
            setInterval(function(){
                refresh()
            }, 2000);
        });
    });

    $("#settings").submit(function( event ){
        $.post( "./api/set/", $( "#settings" ).serialize(), function( data ) {
            $("#settings_button").removeClass("btn-primary");
            $("#settings_button").addClass("btn-success");
            $.each(data, function(key, value) {
                $("#form_" + key).val(value);
            });
            setTimeout(function(){
                $("#settings_button").removeClass("btn-success");
                $("#settings_button").addClass("btn-primary");
            }, 500);
        });
        event.preventDefault();
    });
});

function refresh(){
    $.getJSON( "./api/data/", function( data ) {
        update_scheme(data);
        update_diagram(data);
    });
}

function update_scheme(data){
    $.each(data, function(key, value) {
        var item = $('#' + key);
        if (item.length) {
            if(key == "time"){
                item.text(format_date(new Date(parseFloat(value) * 1000)));
            }else{
                item.text(value + " " + systems_units[key]);
            }
        }
    });
}

function update_diagram(data){
    var chart = $('#simulation_diagram').highcharts();
    var timestamp = get_timestamp(data['time']);

    $.each(data, function(key, value) {
        $.each(chart.series, function(series_index, series_data) {
            if(series_data['name'] == key){
                series_data.addPoint([timestamp, value], false);
            }
        });
    });

    chart.redraw();
}

function format_date(date){
    date = date.toString();
    return date.substring(0, date.length - 15);
}

function get_timestamp(string){
    return new Date(parseFloat(string) * 1000).getTime();
}

function initialize_diagram(){
    Highcharts.setOptions({
        global : {
            useUTC : false
        }
    });
    
    // Create the chart
    $('#simulation_diagram').highcharts('StockChart', {
        rangeSelector: {
            buttons: [{
                count: 1,
                type: 'minute',
                text: '1M'
            }, {
                count: 5,
                type: 'minute',
                text: '5M'
            }, {
                count: 10,
                type: 'minute',
                text: '10M'
            }, {
                count: 60,
                type: 'minute',
                text: '1H'
            }, {
                count: 60*12,
                type: 'minute',
                text: '12H'
            }, {
                count: 1,
                type: 'day',
                text: '1D'
            }, {
                count: 7,
                type: 'day',
                text: '7D'
            }, {
                type: 'all',
                text: 'All'
            }],
            selected: 0
        },
        
        title : {
            text : 'Live simulation data'
        },

        yAxis: {
            min: 0
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
        
        series : series_data,

        credits: {
            enabled: false
        }
    });
}