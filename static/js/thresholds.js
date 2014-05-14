// READY
$(function() {
    $.getJSON("/api/status/", function(data) {
        if (data['system_status'] == 'init') {
            redirect_to_settings();
        }
    }).done(function() {
        refresh_thresholds();
        initialize_sensor_list();

        $('#add_threshold_form').submit( function ( event ) {
            var post_data = {
                'name': $('#add_threshold_form input[name=threshold_name]').val(),
                'sensor_id': $('#add_threshold_form select[name=sensor_id]').val(),
                'min_value': $('#add_threshold_form input[name=min_value]').val(),
                'max_value': $('#add_threshold_form input[name=max_value]').val(),
                'category': $('#add_threshold_form select[name=category]').val(),
            };
            $.ajax({
                type: 'POST',
                contentType: 'application/json',
                url: '/api/manage/thresholds/',
                data: JSON.stringify(post_data),
                dataType: 'json'
            }).done( function () {
                refresh_thresholds();
            });
            event.preventDefault();
        });
    });
});

function redirect_to_settings(show) {
    window.location.href = 'settings.html';    
}

function get_label(category_id) {
    var categories = ['default', 'primary', 'success', 'info', 'warning', 'danger'];
    return '<span class="label label-' + categories[category_id] + '">' + categories[category_id] + '</span>'
}

function initialize_sensor_list() {
    $.getJSON('/api/sensors/', function(data) {
        $('#sensor_list').html('<option value="">Select Sensor</option>');
        $.each(data, function(index, sensor) {
            $('#sensor_list').append('<option value="' + sensor.id + '">' + sensor.name + ' #' + sensor.id + '</option>');
        });
    });
}

function refresh_thresholds() {
    $.getJSON('/api/thresholds/', function(data) {
        $('#threshold_list tbody').empty();
        $.each(data, function(index, threshold) {
            $('#threshold_list tbody').append(
                '<tr>\
                    <td>' + threshold.id + '</td>\
                    <td>' + threshold.name + '</td>\
                    <td>' + threshold.sensor_name + '</td>\
                    <td>' + threshold.min_value + '</td>\
                    <td>' + threshold.max_value + '</td>\
                    <td>' + get_label(threshold.category) + '</td>\
                    <td><span class="glyphicon glyphicon-pencil"></span> <span class="glyphicon glyphicon-remove"></span></td>\
                </tr>'
            );
        });
    });
}