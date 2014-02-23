var devices_info = null;
var series_data = [];
var fast_forward_active = false;

var current_time = new Date();

var blacklist = ["name", "energy_external", "energy_infeed", "thermal_power", "gas_input", "electrical_power", "gas_cost", "infeed_reward","consumption_reward", "external_cost"];

$(function(){
    $.get( "./static/img/simulation.svg", function( data ) {
        var svg_item = document.importNode(data.documentElement,true);
        $("#simulation_scheme").append(svg_item);
    }, "xml");

    $.getJSON( "./api/info/", function( info ) {
        devices_info = info;
        $.each(info, function(device_id, device_data) {
            $.each(device_data, function(sensor_name, unit){
                if(blacklist.indexOf(sensor_name) == -1){
                    series_data.push({
                        name: device_data['name'] + " " + sensor_name,
                        data: [],
                        tooltip: {
                            valueSuffix: ' ' + unit
                        }
                    });
                }
            });
        });
    }).done(function(){
        $.getJSON( "./api/data/", function( data ) {
            var i = 0;
            var timestamp = simulation_time();
            $.each(data, function(device_id, device_data) {
                $.each(device_data, function(sensor_name, value){
                    if(blacklist.indexOf(sensor_name) == -1){
                        series_data[i]['data'].push([timestamp, parseFloat(value)]);
                        i++;
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

    initialize_buttons();
});

function refresh(){
    if(!fast_forward_active){
        $.getJSON( "./api/data/", function( data ) {
            update_scheme(data);
            update_diagram(data);
        });
    }
}

function update_scheme(data){
    $.each(data, function(device_id, device_data) {
        var namespace = get_namespace_for_id(device_id);
        $.each(device_data, function(key, value){
            var item = $('#' + namespace + "_" + key);
            if (item.length) {
                item.text(Math.floor(parseFloat(value)*100)/100 + " " + devices_info[device_id][key]);
            }
        });
    });
    var temp_time = current_time.toString();
    $("#current_time").text(temp_time.substring(0, temp_time.length - 15));
}

function get_namespace_for_id(id){
    switch(id){
        case "0":
            return "bhkw";
        case "1":
            return "hs";
        case "2":
            return "rad1";
        case "3":
            return "elec";
        case "4":
            return "plb";
        case "5":
            return "rad2";
        case "6":
            return "rad3";
    }
}

function update_diagram(data, time_delta){
    var chart = $('#simulation_diagram').highcharts();
    var i = 0;
    var timestamp = simulation_time();
    $.each(data, function(device_id, device_data) {
        $.each(device_data, function(sensor_name, value){
            if(blacklist.indexOf(sensor_name) == -1){
                if(typeof time_delta !== 'undefined'){
                    var value_len = value.length;
                    for (var j = 0; j < value.length; j++) {
                        chart.series[i].addPoint([future_time(timestamp, time_delta, j, value_len), parseFloat(value[j])], false);
                    }
                }else{
                    chart.series[i].addPoint([timestamp, parseFloat(value)], false);
                }
                i++;
            }
        });
    });

    if(time_delta != undefined && time_delta > 0){
        simulation_time(time_delta);
    }
    chart.redraw();
}

function future_time(timestamp, time_delta, seconds, total_seconds){
    return new Date(timestamp + time_delta * seconds/total_seconds * 1000).getTime();
}

function simulation_time(additional_seconds){
    additional_seconds = typeof additional_seconds !== 'undefined' ? additional_seconds : 1;

    current_time = new Date(current_time.getTime() + additional_seconds * 1000);
    return current_time.getTime();
}

function fast_forward(){
    fast_forward_active = true;
    $.post( "./api/set/", { fast_forward: $("#fast_forward_selection").val() }, function( data ){
        $("#ff_button").removeClass("btn-primary").addClass("btn-success");

        update_diagram(data, $("#fast_forward_selection").val(), true);

        $("#ff_button").removeClass("btn-success").addClass("btn-primary");
        fast_forward_active = false;
    });
}

function initialize_buttons(){
    $("#form_consumption").submit(function(){
        $.post( "./api/set/", { electric_consumption: $("#electric_consumption").val() }).done(function(){
            $("#consumption_button").removeClass("btn-primary").addClass("btn-success");
            setTimeout(function(){
                $("#consumption_button").removeClass("btn-success").addClass("btn-primary");
            },1000);
        });
        event.preventDefault();
    });

    $("#form_temperature").submit(function(){
        $.post( "./api/set/", { outside_temperature: $("#outside_temperature").val() }).done(function(){
            $("#temperature_button").removeClass("btn-primary").addClass("btn-success");
            setTimeout(function(){
                $("#temperature_button").removeClass("btn-success").addClass("btn-primary");
            },1000);
        });
        event.preventDefault();
    });

    $("#form_ff").submit(function(){
        fast_forward();
        event.preventDefault();
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