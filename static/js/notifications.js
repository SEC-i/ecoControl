var notifications_per_page = 15;

// READY
function notifications_ready() {
    update_notifications(0);
    if(is_technician()){
        technician_thresholds_ready();
    }
}

function update_notifications(start) {
    var url = api_base_url + 'notifications/start/' + start + '/end/' + (start + notifications_per_page) + '/';
    $.getJSON(url, function(data) {
        var notification_list = data['notifications'];
        $.each(notification_list, function(index, notification) {
            notification.time = $.format.date(new Date(notification['sensor_value']['timestamp']), "HH:MM dd.MM.yyyy");
            notification.message = get_label(notification['threshold']['category']) + ' Sensor #' + notification['sensor_value']['sensor'] + ' was ' + Math.round(notification['sensor_value']['value'] * 100) / 100 + ' and should\'ve been ' + Math.round(notification['target'] * 100) / 100 + '.';
        });

        var rendered = render_template($('#snippet_notification_list').html(), {
            notifications: notification_list
        });
        $('#notification_list').html(rendered);

        if (data['total'] > notifications_per_page) {
            update_pagination(start/notifications_per_page, data['total']);
        }

    });
}

function update_pagination(current, total) {
    $('#notification_pagination').html(
        '<ul class="pagination">\
            <li' + (current == 0 ? ' class="disabled"': '') + '><a href="#" data-start="' + (current - 1) * notifications_per_page  + '">&laquo;</a></li>\
        </ul>'
    );

    for (var i = 0; i < total/notifications_per_page; i++) {
        $('#notification_pagination .pagination').append('<li' + (i == current ? ' class="active"' : '') + '><a href="#" data-start="' + i * notifications_per_page  + '">' + (i + 1) + (i == current ? ' <span class="sr-only">(current)</span>' : '') + '</a></li>');
    };

    $('#notification_pagination .pagination').append(
        '<li' + (current + 1 == total/notifications_per_page ? ' class="disabled"': '') + '><a href="#" data-start="' + (current + 1) * notifications_per_page  + '">&raquo;</a></li>'
    );

    $('#notification_pagination .pagination li a').click(function(event) {
        event.preventDefault();
        if (!$(this).parent().hasClass('disabled') && !$(this).parent().hasClass('active')) {
            update_notifications(parseInt($(this).attr('data-start')));
        }
    });

}


// TECHNICIAN ONLY
var x_editable_sensor_list = [];

// READY
function technician_thresholds_ready() {
    refresh_thresholds();
    initialize_sensor_list();

    $('#add_threshold_form').submit(function(event) {
        event.preventDefault();
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
            url: api_base_url + 'manage/thresholds/',
            data: JSON.stringify(post_data),
            dataType: 'json'
        }).done( function () {
            refresh_thresholds();
            $('#add_threshold_form').each( function(){
              this.reset();
            });
        });
    });
}

function initialize_sensor_list() {
    $.getJSON(api_base_url + 'sensors/', function(data) {
        $('#sensor_list').html('<option value="">Select Sensor</option>');
        $.each(data, function(index, sensor) {
            $('#sensor_list').append('<option value="' + sensor.id + '">' + sensor.name + ' #' + sensor.id + ' (' + sensor.system + ')</option>');
            x_editable_sensor_list.push({value: sensor.id, text: sensor.name + ' #' + sensor.id + ' (' + sensor.system + ')'});
        });
    });
}

function refresh_thresholds() {
    $.getJSON(api_base_url + 'thresholds/', function(threshold_list) {
        $.each(threshold_list, function(index, threshold) {
            threshold.index = index + 1;
            threshold.category_html = get_label(threshold.category);
            threshold.show_manager_value = (threshold.show_manager == true ? '1' : '0');
            threshold.show_manager_text = (threshold.show_manager == true ? 'Yes' : 'No');
        });
        var rendered = render_template($('#snippet_notification_threshold_list').html(), {
            thresholds: threshold_list
        });
        $('#threshold_list').html(rendered);

        $('.x_editable_name').editable({
            url: api_base_url + 'manage/thresholds/',
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
            url: api_base_url + 'manage/thresholds/',
            params: function(params) {
                var post_data = {'id': params.pk};
                post_data[params.name] = params.value;
                return JSON.stringify(post_data);
            },
            source: x_editable_sensor_list
        });
        $('.x_editable_values').editable({
            url: api_base_url + 'manage/thresholds/',
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
            url: api_base_url + 'manage/thresholds/',
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
            url: api_base_url + 'manage/thresholds/',
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
        $('.delete_button').click(function(event) {
            event.preventDefault();
            delete_threshold($(this).attr('data-threshold'));
        });
    });
}

function delete_threshold(threshold_id) {
    $.ajax({
        type: 'POST',
        contentType: 'application/json',
        url: api_base_url + 'manage/thresholds/',
        data: JSON.stringify({
            'id': threshold_id,
            'delete': true
        }),
        dataType: 'json'
    }).done( function () {
        refresh_thresholds();
    });
}