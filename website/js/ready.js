var api_url = "http://www.hpi.uni-potsdam.de/hirschfeld/bachelorprojects/2013H1/api/";

var device_data = null;
var device_id = null;
var range_start = new Date().getTime()-24*2*60*60*1000;
var range_end = new Date().getTime();

$(document).ready(function(){
    $("#login_submit").click(function(event) {
        login_user();
    });

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
        $.post(api_url + "logout/")
            .done(function(data) {
                show_login_box();
            });
    });

    $("#home_button").click(function(event) {
        hide_all();
        $("#home").fadeIn();
    });

    $("#settings_button").click(function(event) {
        hide_all();
        $("#settings").fadeIn();
    });

    var max_range = 72;

    $("#range_slider").slider({
      range: true,
      min: -168,
      max: 0,
      values: [ -24, 0 ],
      slide: function( event, ui ) {
        if ( ui.values[0] >= ui.values[1] ) {
            return false;
        }

        if((-ui.values[0]) + ui.values[1] > max_range){
            // check which handle is in use
            if($("#range_slider .ui-slider-handle:first" ).hasClass('ui-state-active')){
                $( "#range_slider" ).slider( "option", "values", [ ui.values[0], ui.values[0]+max_range ] );
            }else{
                $( "#range_slider" ).slider( "option", "values", [ ui.values[1]-max_range, ui.values[1] ] );
            }
        }

        var start_date = new Date();
        start_date.setHours(start_date.getHours() + parseInt(ui.values[0]));
        var end_date = new Date();
        end_date.setHours(end_date.getHours() + parseInt(ui.values[1]));
        set_day_range(start_date, end_date);
      },
      change: function( event, ui ) {
        range_start = new Date().getTime()+60*60*1000*parseInt(ui.values[0]);
        range_end = new Date().getTime()+60*60*1000*parseInt(ui.values[1]);
        draw_diagram();
      }
    });

    set_day_range(new Date(range_start), new Date(range_end));

    $.get( api_url + "status/", function( data ) {
        if(data['login']=="active"){
            login_successful();
        } else {
            show_login_box();
        }
    });
});

function show_login_box(){
    $("#login_username").val('');
    $("#login_password").val('');
    $("#login_error").html('');
    $('#login_box').modal({
        backdrop: 'static'
    });
}

function login_user () {
    $.post(api_url + "login/", { username: $("#login_username").val(), password: $("#login_password").val(), })
        .done(function(data) {
            if(data['login']=="successful"){
                login_successful();
            }else{
                login_failed();
            }
        });
}

function login_successful(){
    // get devices
    $.get( api_url + "devices/", function( data ) {
        if(data['permission'] != undefined){
            show_login_box();
        }else{
            device_data = data;
            $("#device_list").html(''); // clear device list
            $.each(device_data, function(index, value){
                $("#device_list").append('<li class="device_items" id="device_item_' + value['id'] + '" data-toggle="collapse" data-target=".navbar-collapse"><a onclick="show_device(' + value['id'] + ', \'' + value['name'] + '\');">' + value['name'] + '</a></li>');
            });
        }
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

    // $(".device_items").each(function () {
    //     $(this).removeClass('active');
    // });
    // $("#device_item_" + device_id).addClass('active');


    $("#devices").fadeIn();
    $("#device_name").text(device_name);

    $("#diagram_container").html('');
    draw_diagram();
}

function hide_all(){
    $("#home").hide();
    $("#devices").hide();
    $("#settings").hide();
}

function set_day_range(start, end){
    $( "#day_range" ).html( $.formatDateTime('dd.mm.yy g:ii a', start) +
        " to " + $.formatDateTime('dd.mm.yy g:ii a', end) );
}
