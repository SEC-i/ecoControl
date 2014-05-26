var x_editable_sensor_list = [];

// READY
function technician_thresholds_ready() {
    refresh_thresholds();
    initialize_sensor_list();

    $('#add_threshold_form').submit( function ( event ) {
        var post_data = {
            'name': $('#add_threshold_form input[name=threshold_name]').val(),
            'sensor_id': $('#add_threshold_form select[name=sensor_id]').val(),
            'min_value': $('#add_threshold_form input[name=min_value]').val(),
            'max_value': $('#add_threshold_form input[name=max_value]').val(),
            'category': $('#add_threshold_form select[name=category]').val(),
            'show_manager': $('#add_threshold_form select[name=show_manager]').val(),
        };
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: '/api/manage/thresholds/',
            data: JSON.stringify(post_data),
            dataType: 'json'
        }).done( function () {
            refresh_thresholds();
            $('#add_threshold_form').each( function(){
              this.reset();
            });
        });
        event.preventDefault();
    });
}

function initialize_sensor_list() {
    $.getJSON('/api/sensors/', function(data) {
        $('#sensor_list').html('<option value="">Select Sensor</option>');
        $.each(data, function(index, sensor) {
            $('#sensor_list').append('<option value="' + sensor.id + '">' + sensor.name + ' #' + sensor.id + '</option>');
            x_editable_sensor_list.push({value: sensor.id, text: sensor.name + ' #' + sensor.id});
        });
    });
}

function refresh_thresholds() {
    $.getJSON('/api/thresholds/', function(data) {
        $('#threshold_list tbody').empty();
        $.each(data, function(index, threshold) {
            $('#threshold_list tbody').append(
                '<tr>\
                    <td>' + (index + 1) + '</td>\
                    <td><a href="#" class="x_editable_name" data-type="text" data-pk="' + threshold.id + '" data-name="name" data-title="Enter threshold name">' + threshold.name + '</a></td>\
                    <td><a href="#" class="x_editable_sensor_list editable editable-click editable-open" data-type="select" data-pk="' + threshold.id + '" data-name="sensor_id" data-value="' + threshold.sensor_id + '" data-title="Select sensor">' + threshold.sensor_name + '</a></td>\
                    <td><a href="#" class="x_editable_values" data-type="text" data-pk="' + threshold.id + '" data-name="min_value" data-title="Enter minimal value">' + threshold.min_value + '</a></td>\
                    <td><a href="#" class="x_editable_values" data-type="text" data-pk="' + threshold.id + '" data-name="max_value" data-title="Enter maximal value">' + threshold.max_value + '</a></td>\
                    <td><a href="#" class="x_editable_category editable editable-click editable-open" data-type="select" data-pk="' + threshold.id + '" data-name="category" data-value="' + threshold.category + '" data-title="Select type of notification">' + get_label(threshold.category) + '</a></td>\
                    <td><a href="#" class="x_editable_show_manager editable editable-click editable-open" data-type="select" data-pk="' + threshold.id + '" data-name="show_manager" data-value="' + (threshold.show_manager == true ? '1' : '0') + '" data-title="Show Managers?">' + (threshold.show_manager == true ? 'Yes' : 'No') + '</a></td>\
                    <td><a href="#" class="edit_button"><a href="#" class="delete_button" data-threshold="' + threshold.id + '"><span class="glyphicon glyphicon-trash"></span></a></td>\
                </tr>'
            );
        });
        $('.x_editable_name').editable({
            url: '/api/manage/thresholds/',
            params: function(params) {
                var post_data = {'id': params.pk};
                post_data[params.name] = params.value;
                return JSON.stringify(post_data);
            },
            validate: function(value) {
               if($.trim(value) == '') return 'This field is required';
            }
        });
        $('.x_editable_sensor_list').editable({
            url: '/api/manage/thresholds/',
            params: function(params) {
                var post_data = {'id': params.pk};
                post_data[params.name] = params.value;
                return JSON.stringify(post_data);
            },
            source: x_editable_sensor_list
        });
        $('.x_editable_values').editable({
            url: '/api/manage/thresholds/',
            params: function(params) {
                var post_data = {'id': params.pk};
                post_data[params.name] = params.value;
                return JSON.stringify(post_data);
            },
            validate: function(value) {
               if(isNaN($.trim(value))) return 'This fields requires a numeric or empty input';
            }
        });
        $('.x_editable_category').editable({
            url: '/api/manage/thresholds/',
            params: function(params) {
                var post_data = {'id': params.pk};
                post_data[params.name] = params.value;
                return JSON.stringify(post_data);
            },
            source: [
                {value: 0, text: 'Default'},
                {value: 1, text: 'Primary'},
                {value: 2, text: 'Success'},
                {value: 3, text: 'Info'},
                {value: 4, text: 'Warning'},
                {value: 5, text: 'Danger'}
            ]
        });
        $('.x_editable_show_manager').editable({
            url: '/api/manage/thresholds/',
            params: function(params) {
                var post_data = {'id': params.pk};
                post_data[params.name] = params.value;
                return JSON.stringify(post_data);
            },
            source: [
                {value: 0, text: 'No'},
                {value: 1, text: 'Yes'},
            ]
        });
        $('.delete_button').click( function () {
            delete_threshold($(this).attr('data-threshold'));
        });
    });
}

function delete_threshold(threshold_id) {
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: '/api/manage/thresholds/',
        data: JSON.stringify({
            'id': threshold_id,
            'delete': true
        }),
        dataType: 'json'
    }).done( function () {
        refresh_thresholds();
    });
}