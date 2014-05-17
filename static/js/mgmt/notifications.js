// READY
$(function() {
    $.getJSON('/api/notifications/', function(data) {

        $.each(data, function(index, notification) {
            $('#notification_list tbody').append(
                '<tr>\
                    <td>' + $.format.date(new Date(parseFloat(notification['timestamp'])), "HH:MM dd.MM.yyyy") + '</td>\
                    <td>' + get_label(notification['category']) + ' ' + notification['message'] + '</td>\
                </tr>'
            );
        });
    });
});

function get_label(category_id) {
    var categories = ['default', 'primary', 'success', 'info', 'warning', 'danger'];
    return '<span class="label label-' + categories[category_id] + '">' + categories[category_id] + '</span>'
}