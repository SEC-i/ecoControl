var api_url = "http://www.hpi.uni-potsdam.de/hirschfeld/bachelorprojects/2013H1/api/";
var simulation_api_url = "http://www.hpi.uni-potsdam.de/hirschfeld/bachelorprojects/2013H1/simulation/";

var device_data = null;
var device_id = null;
var range_start = new Date().getTime()-24*2*60*60*1000;
var range_end = new Date().getTime();

// simulation-related
var bhkw_info = null;
var hs_info = null;
var rad_info = null;
var electric_consumer_info = null;
var plb_info = null;

$(document).ready(function(){
    // Login events
    $("#login_submit").click(login_user());
    $("#login_username").keypress(function(e) {
        if(e.which == 13) {
            login_user();
        }
    });
    $("#login_password").keypress(function(e) {
        if(e.which == 13) {
            login_user();
        }
    });

    $("#logout").click(function(event) {
        $.ajax({
            type: "POST",
            url: api_url + "logout/",
            crossDomain: true,
            xhrFields: {
              withCredentials: true
            }
        }).done(show_login_box());
    });

    // navigation items
    $("#home_button").click(function(event) {
        hide_all();
        $("#home").fadeIn();
    });

    $("#simulation_button").click(function(event) {
        hide_all();
        $("#simulation").fadeIn();

        $.getJSON( simulation_api_url + "device/0/info", function( data ) {
            bhkw_info = data;
        });
        $.getJSON( simulation_api_url + "device/1/info", function( data ) {
            hs_info = data;
        });
        $.getJSON( simulation_api_url + "device/2/info", function( data ) {
            rad_info = data;
        });
        $.getJSON( simulation_api_url + "device/3/info", function( data ) {
            electric_consumer_info = data;
        });
        $.getJSON( simulation_api_url + "device/4/info", function( data ) {
            plb_info = data;
        });

        setInterval(function(){
            refresh_simulation();
        }, 1000);

    });

    // load simulation svg
    $.get( "./static/img/demo.svg", function( data ) {
        var svg_item = document.importNode(data.documentElement,true);
        $("#simulation_container").append(svg_item);
    }, "xml");

    check_login_status();
});

function check_login_status(){
    $.ajax({
       url: api_url + "status/",
       xhrFields: {
          withCredentials: true
       }
    }).done(function( data ) {
        if(data['login']=="active"){
            $("#nav_username").text(data['user']);
            login_successful();
        } else {
            show_login_box();
        }
    });
}

function show_login_box(){
    // clean input fields
    $("#login_username").val('');
    $("#login_password").val('');
    $("#login_error").html('');
    // show modal box
    $('#login_box').modal({
        backdrop: 'static'
    });
}

function hide_all(){
    $("#home").hide();
    $("#devices").hide();
    $("#simulation").hide();
}

function login_user() {
    $.ajax({
        type: "POST",
        url: api_url + "login/",
        data: { username: $("#login_username").val(), password: $("#login_password").val(), },
        crossDomain: true,
        xhrFields: {
          withCredentials: true
        }
    }).done(function(data) {
        if(data['login']=="successful"){
            $("#nav_username").text(data['user']);
            login_successful();
        }else{
            login_failed();
        }
    });
}

function login_successful(){
    // get devices
    $.ajax({
       url: api_url + "devices/",
       xhrFields: {
          withCredentials: true
       }
    }).done(function( data ) {
        device_data = data;
        device_data.push({"id":9999,"name":"Simulation"});
        $("#device_list").html(''); // clear device list
        $.each(device_data, function(index, value){
            $("#device_list").append('<li class="device_items" id="device_item_' + value['id'] + '"><a onclick="show_device(' + value['id'] + ', \'' + value['name'] + '\');">' + value['name'] + '</a></li>');
        });
    });

    hide_all();
    $('#login_box').modal('hide');
    $('#footer').fadeIn();
    $("#home").fadeIn();
}

function login_failed(){
    $('#login_error').html('<div class="alert alert-warning">Login details invalid.</div>');
}

function show_device(id, device_name) {
    device_id = id;
    
    hide_all();

    $("#refresh_button").click(function(event) {
        range_end = new Date().getTime();
        $("#sensor_selection").html('');
        prepare_diagram();
    });

    $("#devices").fadeIn();
    $("#device_name").text(device_name);

    $("#diagram_container").html('');
    $("#sensor_selection").html('');
    
    if(id == 9999){
        prepare_simulation_diagram();
    }else{
        prepare_diagram(device_id);
    }
}

function prepare_simulation_diagram(){
    $.ajax({
       url: api_url + "device/1/entries/start/" + range_start + "/end/" + range_end + "/",
       xhrFields: {
          withCredentials: true
       }
    }).done(function(data0){
        $.ajax({
           url: api_url + "device/3/entries/start/" + range_start + "/end/" + range_end + "/",
           xhrFields: {
              withCredentials: true
           }
        }).done(function(data1){
            $.ajax({
               url: api_url + "device/4/entries/start/" + range_start + "/end/" + range_end + "/",
               xhrFields: {
                  withCredentials: true
               }
            }).done(function(data2){
                $.ajax({
                   url: api_url + "device/5/entries/start/" + range_start + "/end/" + range_end + "/",
                   xhrFields: {
                      withCredentials: true
                   }
                }).done(function(data3){
                    $.ajax({
                       url: api_url + "device/6/entries/start/" + range_start + "/end/" + range_end + "/",
                       xhrFields: {
                          withCredentials: true
                       }
                    }).done(function(data4){
                        $.merge(data0, $.merge(data1, $.merge(data2, $.merge(data3, data4))));
                        draw_diagram(data0);
                    });
                });
            });
        });
    });
}

function prepare_diagram(device_id){
    $.ajax({
       url: api_url + "device/" + device_id + "/entries/start/" + range_start + "/end/" + range_end + "/",
       xhrFields: {
          withCredentials: true
       }
    }).done(function(data){draw_diagram(data);});
}

function refresh_simulation(){
    $.getJSON( simulation_api_url + "device/0/get", function( data ) {
        update_simulation(data,"bhkw");
    });
    $.getJSON( simulation_api_url + "device/1/get", function( data ) {
        update_simulation(data,"hs");
    });
    $.getJSON( simulation_api_url + "device/2/get", function( data ) {
        update_simulation(data,"rad");
    });
    $.getJSON( simulation_api_url + "device/3/get", function( data ) {
        update_simulation(data,"elec");
    });
    $.getJSON( simulation_api_url + "device/4/get", function( data ) {
        update_simulation(data,"plb");
    });
}

function update_simulation(data,namespace){
    if($("#simulation").is(":visible")){
        $.each(data, function(item_id, value) {
            var item = $('#' + namespace + "_" + item_id);
            if (item.length) {
                item.text(Math.floor(parseFloat(value)*1000)/1000 + " " + get_unit(item_id, namespace));
            }
        });
    }
}

function get_unit(item_id ,namespace){
    switch(namespace){
        case "bhkw":
            return bhkw_info[item_id];
        case "hs":
            return hs_info[item_id];
        case "rad":
            return rad_info[item_id];
        case "elec":
            return electric_consumer_info[item_id];
        case "plb":
            return plb_info[item_id];
    }
}
