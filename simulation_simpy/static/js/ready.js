var systems_units = {
    cu_workload: '%',
    cu_electrical_production: 'kW',
    cu_total_electrical_production: 'kWh',
    cu_thermal_production: 'kW',
    cu_total_thermal_production: 'kWh',
    cu_total_gas_consumption: 'kWh',
    cu_operating_costs: 'Euro',
    cu_power_ons: 'time(s)',
    cu_total_hours_of_operation: 'h',
    hs_temperature: '°C',
    hs_total_input: 'kWh',
    hs_total_output: 'kWh',
    hs_empty_count: 'time(s)',
    plb_workload: '%',
    plb_thermal_production: 'kW',
    plb_total_gas_consumption: 'kWh',
    plb_operating_costs: 'Euro',
    plb_power_ons: 'time(s)',
    plb_total_hours_of_operation: 'h',
    thermal_consumption: 'kW',
    total_thermal_consumption: 'kWh',
    electrical_consumption: 'kW',
    total_electrical_consumption: 'kWh',
    infeed_reward: 'Euro',
    infeed_costs: 'Euro'
};

var series_data = [{
    name: 'cu_workload',
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
    name: 'hs_temperature',
    data: [],
    tooltip: {
        valueSuffix: ' °C'
    }
},
{
    name: 'thermal_consumption',
    data: [],
    tooltip: {
        valueSuffix: ' kW'
    }
},
{
    name: 'outside_temperature',
    data: [],
    tooltip: {
        valueSuffix: ' °C'
    }
},
{
    name: 'electrical_consumption',
    data: [],
    tooltip: {
        valueSuffix: ' kW'
    }
}];

var editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.getSession().setMode("ace/mode/python");

$(function(){
    $.get( "./static/img/simulation.svg", function( data ) {
        var svg_item = document.importNode(data.documentElement,true);
        $("#simulation_setup").append(svg_item);
    }, "xml");

    initialize_daily_demands();

    $.getJSON( "./api/settings/", function( data ) {
        update_setting(data);
    }).done(function(){
        $.getJSON( "./api/code/", function( data ) {
            editor.setValue(data['code'], 1);
        }).done(function(){
            $.getJSON( "./api/data/", function( data ) {
                for (var i = 0; i < data['time'].length; i++) {
                    var timestamp = get_timestamp(data['time'][i]);
                    series_data[0]['data'].push([timestamp, parseFloat(data['cu_workload'][i])]);
                    series_data[1]['data'].push([timestamp, parseFloat(data['plb_workload'][i])]);
                    series_data[2]['data'].push([timestamp, parseFloat(data['hs_temperature'][i])]);
                    series_data[3]['data'].push([timestamp, parseFloat(data['thermal_consumption'][i])]);
                    series_data[4]['data'].push([timestamp, parseFloat(data['outside_temperature'][i])]);
                    series_data[5]['data'].push([timestamp, parseFloat(data['electrical_consumption'][i])]);
                };
            }).done(function(){
                initialize_diagram();
                // set up refresh loop
                setInterval(function(){
                    refresh();
                }, 2000);
            });
        });
    });
    initialize_event_handlers();
});

function refresh(){
    $.getJSON( "./api/data/", function( data ) {
        update_setup(data);
        update_diagram(data);
    });
}

function update_setting(data){
    $.each(data, function(key, value) {
        if(key == "daily_thermal_demand"){
            $.each(value, function(index, hour_value) {
                $("#daily_thermal_demand_" + index).slider( "value", hour_value * 100);
            });
        }else if(key == "daily_electrical_demand"){
            $.each(value, function(index, hour_value) {
                $("#daily_electrical_demand_" + index).slider( "value", hour_value * 10000);
            });
        }else{
            $("#form_" + key).val(value);
        }
    });
}

function update_setup(data){
    $.each(data, function(key, value) {
        value = value[value.length-1];
        var item = $('.' + key);
        if (item.length) {
            if(key == "time"){
                item.text(format_date(new Date(parseFloat(value) * 1000)));
            }else if(key == "code_execution_status"){
                if(value == 1){
                    item.removeClass('badge-danger');
                    item.addClass('badge-success');
                    item.text('OK');
                }else{
                    item.removeClass('badge-success');
                    item.addClass('badge-danger');
                    item.text('Fail');
                }
            }else{
                item.text(value + " " + systems_units[key]);
            }
        }
    });
}

function update_diagram(data){
    var chart = $('#simulation_diagram').highcharts();

    new_data = [[], [], [], [], [], []];
    for (var i = 0; i < data['time'].length; i++) {
        var timestamp = get_timestamp(data['time'][i]);
        new_data[0].push([timestamp, data['cu_workload'][i]]);
        new_data[1].push([timestamp, data['plb_workload'][i]]);
        new_data[2].push([timestamp, data['hs_temperature'][i]]);
        new_data[3].push([timestamp, data['thermal_consumption'][i]]);
        new_data[4].push([timestamp, data['outside_temperature'][i]]);
        new_data[5].push([timestamp, data['electrical_consumption'][i]]);
    };

    for (var i = new_data.length - 1; i >= 0; i--) {
        chart.series[i].setData(new_data[i], false);
    };

    chart.redraw();
}

function format_date(date){
    date = date.toString();
    return date.substring(0, date.length - 15);
}

function get_timestamp(string){
    return new Date(parseFloat(string) * 1000).getTime();
}

function initialize_event_handlers(){
    $("#settings").submit(function( event ){
        var post_data = $( "#settings" ).serialize();
        for(var i = 0; i < 24; i++) {
            post_data += "&daily_thermal_demand_" + i + "=" + ($("#daily_thermal_demand_" + i).slider( "value")/100);
        }
        for(var i = 0; i < 24; i++) {
            post_data += "&daily_electrical_demand_" + i + "=" + ($("#daily_electrical_demand_" + i).slider( "value")/10000);
        }
        $.post( "./api/settings/", post_data, function( data ) {
            $("#settings_button").removeClass("btn-primary");
            $("#settings_button").addClass("btn-success");
            update_setting(data);
            setTimeout(function(){
                $("#settings_button").removeClass("btn-success");
                $("#settings_button").addClass("btn-primary");
            }, 500);
        });
        event.preventDefault();
    });

    $("#editor_button").click(function() {
        $.post( "./api/code/", {code: editor.getValue()}, function( data ) {
            editor.setValue(data['code'], 1);
        });
    });
}

function initialize_daily_demands(){
    for(var i = 0; i < 24; i++) {
        $("#daily_thermal_demand").append("<span id='daily_thermal_demand_" + i + "' class='slider_thermal'><span>" + i + "</span></span>");
        $("#daily_electrical_demand").append("<span id='daily_electrical_demand_" + i + "' class='slider_electrical'><span>" + i + "</span></span>");
    }

    $( ".slider_thermal" ).slider({
        value: 0,
        min: 0,
        max: 3000,
        range: "min",
        animate: true,
        orientation: "vertical",
        slide: function( event, ui ) {
            var text = "(Current value: " + ui.value/100 + "C)";
            $( "#daily_thermal_demand_info" ).text( text );
        },
        stop: function( event, ui ) {
            $( "#daily_thermal_demand_info" ).text('');
        }
    });

    $( ".slider_electrical" ).slider({
        value: 0,
        min: 0,
        max: 10000,
        range: "min",
        animate: true,
        orientation: "vertical",
        slide: function( event, ui ) {
            var text = "(Current value: " + ui.value/100 + "%)";
            $( "#daily_electrical_demand_info" ).text( text );   
        },
        stop: function( event, ui ) {
            $( "#daily_electrical_demand_info" ).text('');
        }
    });
}

function initialize_diagram(){
    Highcharts.setOptions({
        global : {
            useUTC : false
        }
    });
    
    // Create the chart
    $('#simulation_diagram').highcharts('StockChart', {
        chart: {
            height: 400
        },
        rangeSelector: {
            buttons: [{
                count: 6,
                type: 'hour',
                text: '6H'
            }, {
                count: 12,
                type: 'hour',
                text: '12H'
            }, {
                count: 1,
                type: 'day',
                text: '1D'
            }, {
                count: 1,
                type: 'week',
                text: '1W'
            }, {
                count: 2,
                type: 'week',
                text: '2W'
            }, {
                count: 1,
                type: 'month',
                text: '1M'
            }, {
                count: 6,
                type: 'month',
                text: '6M'
            }, {
                type: 'all',
                text: 'All'
            }],
            selected: 2
        },

        yAxis: {
            min: -10
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