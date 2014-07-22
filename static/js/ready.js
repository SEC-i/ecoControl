var status_data = null;

$(function() {
    $.address.change(function(event) {
        load_page(event.value.replace('/', ''));
    });

    $.getJSON(api_base_url + 'status/', function(data) {
        status_data = data;
        initialize_page(function() {
            if ((status_data['admin'] && status_data['system_status'] == 'init')) {
                $.address.value('settings');
            } else {
                $.address.value(get_current_page());
            }
        });
    });

    $('.navbar-brand').click(function(event) {
        event.preventDefault();
        if (is_logged_in()) {
            $('.nav li').removeClass('active');
            $('.nav li').first().addClass('active');
        }
        $.address.value('overview');
    });

    $('.language_selection').click(function(event){
        event.preventDefault();
        $.cookie('selected_language', $(this).attr('data-value'), { expires: 7 });
        location.reload();
    });

    if ($.cookie('selected_language')  != undefined) {
        if ($.cookie('selected_language') == 'de') {
            Highcharts.setOptions({lang: lang_de_highcharts});
        }
    }
});
