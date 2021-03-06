// READY
function manager_settings_ready() {
    $.getJSON(api_base_url + 'settings/', function(data) {
        $.each(data, function(device_id, device_configurations) {
            $.each(device_configurations, function(key, config_data) {
                var namespace = namespaces[device_id];
                var item = $('#' + namespace + '_panel .panel-body');
                if (item.length) {
                    var output = render_template($('#snippet_settings_plain').html(), {
                        datatype: get_mapped_type(config_data.type),
                        id: namespace + '_' + key,
                        key: key,
                        name: get_text(key),
                        type: config_data.type,
                        unit: config_data.unit,
                        value: config_data.value,
                    });
                    item.append(output);
                }
            });
        });
    });
}