// READY
var notifications_per_page = 20;

$(function() {
    $.getJSON("/api/status/", function(data) {
        if (data['system_status'] == 'init') {
            redirect_to_settings();
        }
    }).done(function() {
        update_notifications(0);
    });
});

function redirect_to_settings(show) {
    window.location.href = 'settings.html';    
}

function get_label(category_id) {
    var categories = ['default', 'primary', 'success', 'info', 'warning', 'danger'];
    return '<span class="label label-' + categories[category_id] + '">' + categories[category_id] + '</span>'
}


function update_notifications(start) {
    var url = '/api/notifications/start/' + start + '/end/' + (start + notifications_per_page) + '/';
    $.getJSON(url, function(data) {
        $('#notification_list tbody').empty();
        $.each(data['notifications'], function(index, notification) {
            $('#notification_list tbody').append(
                '<tr>\
                    <td>' + notification['id'] + '</td>\
                    <td>' + $.format.date(new Date(parseFloat(notification['timestamp'] * 1000)), "HH:MM dd.MM.yyyy") + '</td>\
                    <td>' + get_label(notification['category']) + ' ' + notification['message'] + '</td>\
                </tr>'
            );
        });

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
        if (!$(this).parent().hasClass('disabled') && !$(this).parent().hasClass('active')) {
            update_notifications(parseInt($(this).attr('data-start')));
        }
        event.preventDefault();
    });

}

