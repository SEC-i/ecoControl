// READY
$(function() {
    $.getJSON("/api/status/", function(data) {
        if (data['system_status'] == 'init') {
            redirect_to_settings();
        }
    }).done(function() {
        $.getJSON('/api/notifications/', function(data) {

            $.each(data, function(index, notification) {
                $('#notification_list tbody').append(
                    '<tr>\
                        <td>' + notification['id'] + '</td>\
                        <td>' + get_label(notification['category']) + '</td>\
                        <td>' + notification['message'] + '</td>\
                        <td>' + $.format.date(new Date(parseFloat(notification['timestamp'])), "HH:MM dd.MM.yyyy") + '</td>\
                        <td>' + (notification['read'] == true ? '' : '<span class="glyphicon glyphicon-ok"></span>' ) + '</td>\
                    </tr>'
                );
            });
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