// READY
function technician_live_setup_ready() {
    $.get("img/schema.svg", function(data) {
        var svg_item = document.importNode(data.documentElement, true);
        $("#schema_container").append(svg_item);
    }, "xml").done(function() {
        refresh_live_setup();
    });
}

function refresh_live_setup() {
    $.getJSON(api_base_url + 'live/', function(data) {
        $.each(data, function(key, value) {
            var item = $('#' + key);
            if (item.length) { // check if item exists
                if (key == 'time') {
                    item.html($.format.date(new Date(parseFloat(value)), "dd.MM.yyyy HH:MM"));
                } else {
                    item.html(value);
                }
            }
        });
    });

    if (get_current_page() == 'live_setup') {
        setTimeout(refresh_live_setup, 5000);
    }
}