var api_base_url = '../api/';

var colors_past = ['#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce', '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'];
var colors_future = ['#3895ff', '#153a61', '#a8e329', '#b80000', '#20cef5', '#623896', '#ffa561', '#9ac1ff', '#eb2d2d', '#c6f07f'];
var colors_modified = ['#225999', '#000000', '#5c7d16', '#520000', '#13788f', '#201230', '#b36a32', '#5675a6', '#851919', '#728a49'];

var namespaces = ['general', 'hs', 'pm', 'cu', 'plb'];
var categories = ['default', 'primary', 'success', 'info', 'warning', 'danger'];

var sensor_list = null;

function get_text(key) {
    if (key in get_language()) {
        return get_language()[key];
    }
    return key;
}

function get_language() {
    if ($.cookie('selected_language') !== undefined) {
        if ($.cookie('selected_language') === "de") {
           return lang_de;
        }
    }
    return lang_en;
}

function get_label(category_id) {
    return '<span class="label label-' + categories[category_id] + '">' + categories[category_id] + '</span>';
}

function get_sensor(sensor_id, sensor_list) {
    if (sensor_list === null) {
        return null;
    }

    var output = null;
    $.each(sensor_list, function (index, sensor) {
        if (sensor.id === sensor_id) {
            output = sensor;
            return false;
        }
    });
    return output;
}

jQuery.extend({
    postJSON: function(url, data, callback) {
        $.ajax({
            type: 'POST',
            contentType: 'application/json',
            url: url,
            data: JSON.stringify(data),
            dataType: 'json',
            success: callback
        });
    }
});

function draw_table(target, headlines, rows) {
    if (rows.length > 0 && headlines.length === rows[0].length) {
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

function export_table(target) {
    Highcharts.post('api/export/', {
        csv: target.table2CSV({delivery:'value'})
    });
}

function get_current_page() {
    return $.address.value().replace('/', '');
}

function is_logged_in() {
    return status_data['login'] === true;
}

function is_technician() {
    return status_data['admin'] === true;
}

function load_page(target) {
    if (status_data === null) {
        setTimeout(function() {
            // wait for status_data to be ready
            load_page(target);
        }, 100);
    } else {
        if (!is_logged_in()) {
            target = 'login';
        } else if (target === "") {
            target = 'overview';
        }
        url = 'templates/' + target + '.html';
        $.ajax({
            url: url,
            dataType: "html",
            success: function(data) {
                var template_data = $("<div>").append( $.parseHTML( data ) ).find( '.' + role_name() );
                var template = "";
                $.each(template_data, function(index, container){
                    template += container.innerHTML;
                });
                var rendered = render_template(template);
                $('#main').html(rendered);

                if (role_name() + '_' + target + '_ready' in window) {
                    window[role_name() + '_' + target + '_ready']();
                } else if (target + '_ready' in window) {
                    window[target + '_ready']();
                }
                $('.nav li').removeClass('active');
                $('a[href=\'/' + target + '\']').parent().addClass('active');
            }
        });
    }
}

function role_name() {
    if (is_technician()) {
        return 'technician';
    }
    return 'manager';
}

function render_template(template, view_extension) {
    var view = $.extend({}, get_language());
    if (arguments.length > 1) {
        $.extend(view, view_extension);
    }
    return Mustache.render(template, view);
}

function initialize_page(callback) {
    if (is_logged_in()) {
        $.get('templates/navigation.html', function(data) {
            var navigation_template = $("<div>").append( $.parseHTML( data ) ).find( '.' + role_name() );
            var rendered = render_template(navigation_template.html());
            $('#navbar_container').html(rendered);

            $('#navbar_container a').address(function() {  
                return $(this).attr('href').replace(/^#/, '');  
            }); 

            $('#logout_button').click(function(event) {
                event.preventDefault();
                $('#navbar_container').empty();
                $.ajax({
                    type: "POST",
                    url: api_base_url + "logout/",
                    crossDomain: true,
                    xhrFields: {
                        withCredentials: true
                    }
                }).done(load_page('login'));
            });

            $('#snippets').load('templates/snippets.html', function() {
                callback();
            });
        });
    }
}