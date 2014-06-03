var settings_data = null;

// READY
function technician_settings_ready() {
    $.getJSON(api_base_url + 'settings/', function(data) {
        settings_data = data;
        $.each(settings_data, function(device_id, device_configurations) {
            $.each(device_configurations, function(key, config_data) {
                var namespace = namespaces[device_id];
                var item = $('#' + namespace + '_panel .panel-body');
                if (item.length) {
                    var view = {
                        datatype: get_mapped_type(config_data.type),
                        device: device_id,
                        id: namespace + '_' + key,
                        key: key,
                        name: get_text(key),
                        type: config_data.type,
                        unit: config_data.unit,
                        value: config_data.value,
                    };
                    if (status_data['system_status'] == 'init') {
                        var output = Mustache.render($('#snippet_settings_input').html(), view);
                        item.append(output);
                    } else {
                        var output = Mustache.render($('#snippet_settings_plain').html(), view);
                        item.append(output);
                    }
                }
            });
        });

        $('#panels .setting_input').editable({
            url: api_base_url + 'configure/',
            params: function(params) {
                var item = $('a[data-pk="' + params.pk + '"]');
                var post_data = [{
                    device: item.attr('data-device'),
                    key: params.pk,
                    type: item.attr('data-type2'),
                    value: params.value,
                    unit: item.attr('data-unit')
                }];
                return JSON.stringify(post_data);
            },
            validate: function(value) {
               if($.trim(value) == '') return 'This field is required';
            }
        });

        if (status_data['system_status'] == 'init') {
            $('#container').prepend($('#snippet_settings_notice').html());
            $('#panels').append($('#snippet_settings_buttons').html());
            $(".configure_button").click(function(event) {
                var demo = $(this).attr('data-demo');

                var post_data = [];
                $( ' .configuration' ).each(function( index ) {
                    post_data.push({
                        device: $(this).attr('data-device'),
                        key: $(this).attr('data-key'),
                        type: $(this).attr('data-type'),
                        value: $(this).val(),
                        unit: $(this).attr('data-unit')
                    });
                });

                $.ajax({
                    type: 'POST',
                    contentType: 'application/json',
                    url: api_base_url + 'configure/',
                    data: JSON.stringify(post_data),
                    dataType: 'json'
                }).done(function(response) {
                    $.postJSON(api_base_url + "start/", {
                        demo: demo
                    }, function() {
                        $.address.value('overview');
                    });
                });
            });
        }
    });
}

function get_mapped_type(type) {
    switch(type) {
        case 3:
            return 'date'
        default:
            return 'text'
    }
}