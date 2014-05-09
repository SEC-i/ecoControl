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
                            item.append(get_plain_text(key, config_data));
                        }
                    }
                });
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
                    send_configuration(function(){
                        $.post("/api/start/", {
                            demo: demo
                        }).done(function() {
                            window.location.href = 'index.html';
                        });
                    });
                });
            }

            if (system_status != 'init') {
                $.each(namespaces, function(index, value) {
                    $('#' + value + '_panel .panel-heading').append('<a href="#" class="edit_button" data-namespace=' + value + '><span class="glyphicon glyphicon-pencil pull-right"></span></a>');
                });

                $('.edit_button').click(function() {
                    edit_settings($(this).attr('data-namespace'));
                });
            }

            // $('.configure_button').click(function() {
            //     var post_data = [];
            //     $( ".configuration" ).each(function( index ) {
            //         post_data.push({
            //             device: $(this).attr('data-device'),
            //             key: $(this).attr('data-key'),
            //             type: $(this).attr('data-type'),
            //             value: $(this).val(),
            //             unit: $(this).attr('data-unit')
            //         })
            //     });

            //     $.ajax({
            //         type: 'POST',
            //         contentType: 'application/json',
            //         url: '/api/configure/',
            //         data: JSON.stringify(post_data),
            //         dataType: 'json'
            //     }).done(function(response) {
            //         $('#panels').prepend(
            //             '<div class="alert alert-success alert-dismissable">\
            //               <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>\
            //               <strong>Configurations updated successfully!</strong>\
            //             </div>'
            //         );
            //     }).fail(function(response) {
            //         $('#panels').prepend(
            //             '<div class="alert alert-danger alert-dismissable">\
            //               <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>\
            //               <strong>Warning!</strong> An error occured. Is the server up and running?\
            //             </div>'
            //         );
            //     });
            //     setTimeout(function(){$(".alert").alert('close')}, 3000); // close alert after 3s
            // });
        });
    });
});

function send_configuration(callback, prefix) {
    prefix = typeof prefix !== 'undefined' ? prefix : '';

    var post_data = [];
    $( prefix + ' .configuration' ).each(function( index ) {
        post_data.push({
            device: $(this).attr('data-device'),
            key: $(this).attr('data-key'),
            type: $(this).attr('data-type'),
            value: $(this).val(),
            unit: $(this).attr('data-unit')
        })
    });

    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/api/configure/',
        data: JSON.stringify(post_data),
        dataType: 'json'
    }).done(function(response) {
        callback();
    });
}

function edit_settings(namespace) {
    var device_id = namespaces.indexOf(namespace);
    var item = $('#' + namespace + '_panel .panel-body');
    if (item.length) {
        item.empty();

        $.each(settings_data[device_id], function(key, config_data) {
            item.append(get_input_field_code(namespace, key, config_data));
        });

        item.append(
            '<div class="row">\
                <div class="col-sm-12">\
                    <div class="row">\
                        <div class="col-sm-6">\
                            <button type="button" class="btn btn-primary btn-block" id="' + namespace + '_apply_button" data-namespace="' + namespace + '">Apply</button>\
                        </div>\
                        <div class="col-sm-6">\
                            <button type="button" class="btn btn-warning btn-block" id="' + namespace + '_reset_button" data-namespace="' + namespace + '">Reset</button>\
                        </div>\
                    </div>\
                </div>\
            </div>'
        );

        $('#' + namespace + '_apply_button').click(function() {
            var namespace = $(this).attr('data-namespace');
            var device_id = namespaces.indexOf(namespace);
            send_configuration(function( index ) {
                var item = $('#' + namespace + '_panel .panel-body');
                if (item.length) {
                    item.empty();
                    $.each(settings_data[device_id], function(key, config_data) {
                        item.append(get_plain_text(key, config_data));
                    });
                }
            }, '#' + namespace + '_panel');
        });


        $('#' + namespace + '_reset_button').click(function() {
            var namespace = $(this).attr('data-namespace');
            var item = $('#' + namespace + '_panel .panel-body');
            if (item.length) {
                item.empty();
                $.each(settings_data[device_id], function(key, config_data) {
                    item.append(get_plain_text(key, config_data));
                });
            }
        });
    }
}

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