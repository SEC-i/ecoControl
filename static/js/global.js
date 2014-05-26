var colors_past = ['#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce', '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'];
var colors_future = ['#3895ff', '#153a61', '#a8e329', '#b80000', '#20cef5', '#623896', '#ffa561', '#9ac1ff', '#eb2d2d', '#c6f07f'];
var colors_modified = ['#225999', '#000000', '#5c7d16', '#520000', '#13788f', '#201230', '#b36a32', '#5675a6', '#851919', '#728a49'];

var namespaces = ['general', 'hs', 'pm', 'cu', 'plb'];
var categories = ['default', 'primary', 'success', 'info', 'warning', 'danger'];

function get_label(category_id) {
    return '<span class="label label-' + categories[category_id] + '">' + categories[category_id] + '</span>'
}

function draw_table(target, headlines, rows) {
    if (rows.length > 0 && headlines.length == rows[0].length) {
        target.html(
            '<table class="table table-striped table-condensed">\
              <thead>\
              </thead>\
              <tbody>\
              </tbody>\
            </table>'
        );

        // add thead elements
        var td_head = '';
        $.each(headlines, function(index, col_text) {
            td_head += '<td><b>' + col_text + '</b></td>';
        })
        $('thead', target).append(
            '<tr>' + td_head + '</tr>'
        );

        // add tbody elements
        $.each(rows, function(index, row) {
            var cols = '';
            $.each(row, function(index2, col_text) {
                cols += '<td>' + col_text + '</td>';
            })
            $('tbody', target).append(
                '<tr>' + cols + '</tr>'
            );
        });
    } else {
        target.html('More or less headlines than rows or empty rows!');
    }
}