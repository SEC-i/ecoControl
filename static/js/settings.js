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
                        location.reload(true);
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
                                '<input type="text" class="form-control" id="' + namespace + '_' + device_config[0] + '" data-key="' + device_config[0] + '" data-unit="' + device_config[3] + '"  value="' + device_config[1] + '">';
                    } else {
                        code +=
                                '<div class="input-group">' +
                                    '<input type="text" class="form-control" id="' + namespace + '_' + device_config[0] + '" data-key="' + device_config[0] + '" data-unit="' + device_config[3] + '"  value="' + device_config[1] + '">' +
                                    '<span class="input-group-addon">' + device_config[3] + '</span>' +
                                '</div>';
                    }
                    code += '</div></div>';

                    item.append(code);
                }
            }
        });
    });
});