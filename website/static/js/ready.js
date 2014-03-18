var api_url = "http://www.hpi.uni-potsdam.de/hirschfeld/bachelorprojects/2013H1/api/";

var device_data = null;
var device_id = null;
var range_start = new Date().getTime() - 24 * 2 * 60 * 60 * 1000;
var range_end = new Date().getTime();

$(document).ready(function() {
    // Login events
    $("#login_submit").click(function(e) {
        login_user()
    });
    $("#login_username").keypress(function(e) {
        if (e.which == 13) {
            login_user();
        }
    });
    $("#login_password").keypress(function(e) {
        if (e.which == 13) {
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

    check_login_status();
});

function check_login_status() {
    $.ajax({
        url: api_url + "status/",
        xhrFields: {
            withCredentials: true
        }
    }).done(function(data) {
        if (data['login'] == "active") {
            $("#nav_username").text(data['user']);
            login_successful();
        } else {
            show_login_box();
        }
    });
}

function show_login_box() {
    // clean input fields
    $("#login_username").val('');
    $("#login_password").val('');
    $("#login_error").html('');
    // show modal box
    $('#login_box').modal({
        backdrop: 'static'
    });
}

function hide_all() {
    $("#home").hide();
    $("#devices").hide();
}

function login_user() {
    $.ajax({
        type: "POST",
        url: api_url + "login/",
        data: {
            username: $("#login_username").val(),
            password: $("#login_password").val(),
        },
        crossDomain: true,
        xhrFields: {
            withCredentials: true
        }
    }).done(function(data) {
        if (data['login'] == "successful") {
            $("#nav_username").text(data['user']);
            login_successful();
        } else {
            login_failed();
        }
    });
}

function login_successful() {
    // get devices
    $.ajax({
        url: api_url + "devices/",
        xhrFields: {
            withCredentials: true
        }
    }).done(function(data) {
        device_data = data;
        $("#device_list").html(''); // clear device list
        $.each(device_data, function(index, value) {
            $("#device_list").append('<li class="device_items" id="device_item_' + value['id'] + '"><a onclick="show_device(' + value['id'] + ', \'' + value['name'] + '\');">' + value['name'] + '</a></li>');
        });
    });

    hide_all();
    $('#login_box').modal('hide');
    $('#footer').fadeIn();
    $("#home").fadeIn();
}

function login_failed() {
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

    prepare_diagram(device_id);
}

function prepare_diagram(device_id) {
    $.ajax({
        url: api_url + "device/" + device_id + "/entries/start/" + range_start + "/end/" + range_end + "/",
        xhrFields: {
            withCredentials: true
        }
    }).done(function(data) {
        draw_diagram(data);
    });
}