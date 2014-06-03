// READY
function manager_settings_ready() {
    $.getJSON(api_base_url + 'settings/', function(data) {
        $.each(data, function(device_id, device_configurations) {
            $.each(device_configurations, function(key, config_data) {
                var namespace = namespaces[device_id];
                var item = $('#' + namespace + '_panel .panel-body');
                if (item.length) {
                    var output = Mustache.render($('#snippet_settings_plain').html(), {
                        key: get_text(key),
                        value: config_data.value,
                        unit: config_data.unit
                    });
                    item.append(output);
                }
            });
        });
    });
}