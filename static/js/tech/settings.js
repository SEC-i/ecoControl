var settings_data = null;

// READY
$(function() {
    $.getJSON('/api/status/', function(status_data) {
        $.getJSON('/api/settings/', function(data) {
            var system_status = status_data['system_status'];
            settings_data = data;
            $.each(settings_data, function(device_id, device_configurations) {
                $.each(device_configurations, function(key, config_data) {
                    var namespace = namespaces[device_id];
                    var item = $('#' + namespace + '_panel .panel-body');
                    if (item.length) {
                        if (system_status == 'init') {
                            item.append(get_input_field_code(namespace, key, config_data));
                        } else {
                            item.append(get_plain_text(namespace, key, config_data));
                        }
                    }
                });
            });

            $('.setting_input').editable({
                url: '/api/configure/',
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

            if (system_status == 'init') {
                $('#container').prepend(
                    '<div class="alert alert-warning fade in">\
                      <h4>Please Configure The System</h4>\
                      <p>Duis mollis, est non commodo luctus, nisi erat porttitor ligula, eget lacinia odio sem nec elit. Cras mattis consectetur purus sit amet fermentum.</p>\
                    </div>'
                );
                $('#panels').append(
                    '<div class="row">\
                        <div class="col-sm-3 col-sm-offset-2">\
                            <button type="button" class="configure_button btn btn-success btn-block btn-lg" data-demo="1">Start Demo</button>\
                        </div>\
                        <div class="col-sm-3 col-sm-offset-2">\
                            <button type="button" class="configure_button btn btn-success btn-block btn-lg" data-demo="0">Start Normal</button>\
                        </div>\
                    </div>'
                );
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
                        url: '/api/configure/',
                        data: JSON.stringify(post_data),
                        dataType: 'json'
                    }).done(function(response) {
                        $.post("/api/start/", {
                            demo: demo
                        }).done(function() {
                            window.location.href = 'index.html';
                        });
                    });
                });
            }
        });
    });
});

function get_input_field_code(namespace, key, data) {
    var device_id = namespaces.indexOf(namespace);
    var output =
            '<div class="col-sm-4"><div class="form-group">' +
                '<label for="' + namespace + '_' + key + '">' + get_text(key) + '</label>';
    if (data.unit == '') {
        output +=
                '<input type="text" class="configuration form-control" id="' + namespace + '_' + key + '" data-device="' + device_id + '" data-key="' + key + '" data-type="' + data.type + '" data-unit="' + data.unit + '"  value="' + data.value + '">';
    } else {
        output +=
                '<div class="input-group">' +
                    '<input type="text" class="configuration form-control" id="' + namespace + '_' + key + '" data-device="' + device_id + '" data-key="' + key + '" data-type="' + data.type + '" data-unit="' + data.unit + '"  value="' + data.value + '">' +
                    '<span class="input-group-addon">' + data.unit + '</span>' +
                '</div>';
    }
    output += '</div></div>';
    return output;
}

function get_plain_text(namespace, key, data) {
    var device_id = namespaces.indexOf(namespace);
    return '<div class="col-lg-4 col-sm-6">\
                <div class="row">\
                    <div class="col-xs-9">\
                        <b>' + get_text(key) + '</b>:\
                    </div>\
                    <div class="col-xs-3 text-right">\
                        <a href="#" class="setting_input" data-type="' + get_mapped_type(data.type) + '" data-title="' + get_text(key) + (data.unit == '' ? '' : ' in ' + data.unit) +  '" data-pk="' + key + '" data-device="' + device_id + '" data-unit="' + data.unit + '" data-type2="' + data.type + '">' + data.value + '</a> ' + data.unit + '\
                    </div>\
                </div>\
            </div>';
}

function get_mapped_type(type) {
    switch(type) {
        case 3:
            return 'date'
        default:
            return 'text'
    }
}