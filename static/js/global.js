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