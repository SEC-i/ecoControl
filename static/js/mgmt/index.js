// READY
$(function() {
    $.getJSON("/api2/balance/total/", function(data) {
        $('#date_headline').text($.format.date(new Date(data.year, data.month, 1), "MMMM yyyy"));
        $('#date_rewards').text(data.rewards + '€');
        $('#date_costs').text('-' + data.costs + '€');
        $('#date_balance').text(data.balance + '€');
    });
});