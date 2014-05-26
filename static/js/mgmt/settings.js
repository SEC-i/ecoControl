var namespaces = ['general', 'hs', 'pm', 'cu', 'plb'];
var settings_data = null;

// READY
function manager_settings_ready() {
    $.getJSON('/api/status/', function(status_data) {
        $.getJSON('/api/settings/', function(data) {
            var system_status = status_data['system_status'];
            settings_data = data;
            $.each(settings_data, function(device_id, device_configurations) {
                $.each(device_configurations, function(key, config_data) {
                    var namespace = namespaces[device_id];
                    var item = $('#' + namespace + '_panel .panel-body');
                    if (item.length) {
                        item.append(get_plain_text(key, config_data));
                    }
                });
            });
        });
    });
}

function get_plain_text(key, data) {
    return '<div class="col-lg-4 col-sm-6">\
                <div class="row">\
                    <div class="col-xs-9">\
                        <b>' + get_text(key) + '</b>:\
                    </div>\
                    <div class="col-xs-3 text-right">\
                        ' + data.value + ' ' + data.unit + '\
                    </div>\
                </div>\
            </div>';
}