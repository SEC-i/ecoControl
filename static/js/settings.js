// READY
$(function() {
    $.getJSON('/api/settings/', function(data) {
        $.each(data, function(index, device_config) {
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
        });
    });
});