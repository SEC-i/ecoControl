// READY
$(function() {
    $.getJSON("/api/status/", function(data) {
        if (data['system'] == 'init') {
            redirect_to_settings();
        }
    }).done(function() {
        $.get("/static/img/simulation.svg", function(data) {
            var svg_item = document.importNode(data.documentElement, true);
            $("#schema_container").append(svg_item);
        }, "xml").done(function() {
            refresh();
        });
    });
});

function refresh() {
    $.getJSON('/api/live/', function(data) {
        update_schema(data);
    });
                
    setTimeout(refresh, 2000);
}

function update_schema(data) {
    $.each(data, function(key, value) {
        var item = $('.' + key);
        if (item.length) { // check if item exists
            if (key == 'time') {
                item.html($.format.date(new Date(parseFloat(value)), "dd.MM.yyyy HH:MM"));
            } else {
                item.html(value);
            }
        }
    });
}

function redirect_to_settings(show) {
    window.location.href = 'settings.html';    
}