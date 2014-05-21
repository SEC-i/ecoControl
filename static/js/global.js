$(function() {
    $('#logout_button').click(function(event) {
        $.ajax({
            type: "POST",
            url: "/api/logout/",
            crossDomain: true,
            xhrFields: {
                withCredentials: true
            }
        }).done(redirect_to_landing_page());
        event.preventDefault();
    });
});

function redirect_to_landing_page() {
    window.location.href = '/static/index.html';
}

function redirect_to_settings(show) {
    window.location.href = 'settings.html';    
}

var colors_past = ['#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce', '#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a'];
var colors_future = ['#3895ff', '#153a61', '#a8e329', '#b80000', '#20cef5', '#623896', '#ffa561', '#9ac1ff', '#eb2d2d', '#c6f07f'];
var colors_modified = ['#225999', '#000000', '#5c7d16', '#520000', '#13788f', '#201230', '#b36a32', '#5675a6', '#851919', '#728a49'];

var namespaces = ['general', 'hs', 'pm', 'cu', 'plb'];