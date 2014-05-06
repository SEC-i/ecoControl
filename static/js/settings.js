// READY
$(function() {
    $.getJSON('/api/settings/', function(data) {
        $.each(data, function(index, device_config) {
            if (device_config[0] == 'system_status') {
                if (device_config[1] == 'init') {
                    $('#container').prepend(
                      '<div class="row">\
                        <div class="col-sm-12">\
                          <div class="panel panel-warning">\
                            <div class="panel-heading"><b>Please Configure The System</b></div>\
                            <div class="panel-body">\
                              <div class="row">\
                                <div class="col-sm-3 col-sm-offset-3"><button type="button" class="btn btn-success btn-block" id="configure_demo_button">Start Demo</button></div>\
                                <div class="col-sm-3"><button type="button" class="btn btn-success btn-block" id="configure_normal_button">Start Normal</button></div>\
                              </div>\
                            </div>\
                          </div>\
                        </div>\
                      </div>'
                    );
                    $("#configure_demo_button").click(function(event) {
                        $.post("/api/start/", {
                            demo: 1
                        });
                        window.location.href = 'index.html';
                    });
                    $("#configure_normal_button").click(function(event) {
                        $.post("/api/start/");
                        location.reload(true);
                    });
                }
            } else {
                var namespace = undefined;
                switch(device_config[4]) {
                    case 0:
                        namespace = 'general';
                        break;
                    case 1:
                        namespace = 'hs';
                        break;
                    case 3:
                        namespace = 'cu';
                        break;
                    case 4:
                        namespace = 'plb';
                        break;
                }
                var item = $('#' + namespace + '_settings');
                if (item.length) {
                    var code =
                            '<div class="col-sm-6"><div class="form-group">' +
                                '<label for="' + namespace + '_' + device_config[0] + '">' + device_config[0] + '</label>';
                    if (device_config[3] == '') {
                        code +=
                                '<input type="text" class="configuration form-control" id="' + namespace + '_' + device_config[0] + '" data-device="' + device_config[4] + '" data-key="' + device_config[0] + '" data-type="' + device_config[2] + '" data-unit="' + device_config[3] + '"  value="' + device_config[1] + '">';
                    } else {
                        code +=
                                '<div class="input-group">' +
                                    '<input type="text" class="configuration form-control" id="' + namespace + '_' + device_config[0] + '" data-device="' + device_config[4] + '" data-key="' + device_config[0] + '" data-type="' + device_config[2] + '" data-unit="' + device_config[3] + '"  value="' + device_config[1] + '">' +
                                    '<span class="input-group-addon">' + device_config[3] + '</span>' +
                                '</div>';
                    }
                    code += '</div></div>';

                    item.append(code);
                }
            }
        });

        $('.configure_button').click(function() {
            var post_data = [];
            $( ".configuration" ).each(function( index ) {
                post_data.push({
                    device: $(this).attr('data-device'),
                    key: $(this).attr('data-key'),
                    type: $(this).attr('data-type'),
                    value: $(this).val(),
                    unit: $(this).attr('data-unit')
                })
            });

            console.log(post_data);


            $.ajax({
                type: 'POST',
                contentType: 'application/json',
                url: '/api/configure/',
                data: JSON.stringify(post_data),
                dataType: 'json'
            }).done(function(response) {
                $('#panels').prepend(
                    '<div class="alert alert-success alert-dismissable">\
                      <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>\
                      <strong>Configurations updated successfully!</strong>\
                    </div>'
                );
            }).fail(function(response) {
                $('#panels').prepend(
                    '<div class="alert alert-danger alert-dismissable">\
                      <button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>\
                      <strong>Warning!</strong> An error occured. Is the server up and running?\
                    </div>'
                );
            });
            setTimeout(function(){$(".alert").alert('close')}, 3000); // close alert after 3s
        });
    });
});