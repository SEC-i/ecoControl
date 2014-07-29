var balances_diagram_types = ['balances', 'rewards', 'costs'];
var balances_cached_data = {};
var balances_cached_history = [];

// READY
function manager_balances_ready() {
    initialize_balance_diagrams();
    initialize_balance_diagrams_filters();

    resize_diagrams();

    // fix active tab issue
    setTimeout(function() {
        $('#balances_tabs a:first').tab('show');
    }, 100);
}

$(window).resize(function() {
    if (get_current_page() === "balances") {
        resize_diagrams();
    }
});

function resize_diagrams() {
    // resize charts in tabs
    $.each(balances_diagram_types, function(index, type) {
        var container = $('#balances_' + type + '_container');
        var chart = container.highcharts();
        chart.setSize(container.parent().width(), container.parent().height(), false);
    });
}

function initialize_balance_diagrams() {
    $.each(balances_diagram_types, function(index, type) {
        $('#balances_' + type + '_container').highcharts({
            chart: {
                zoomType: 'xy'
            },
            title: {
                text: ''
            },
            xAxis: {
                categories: get_text('months')
            },
            yAxis: [{
                labels: {
                    format: '{value} €',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
                title: {
                    text: get_text('chart_balances_in') + '€',
                    style: { color: Highcharts.getOptions().colors[1] }
                },
            }],
            plotOptions: {
                series: {
                    cursor: 'pointer',
                    point: {
                        events: {
                            click: function (e) {
                                $('#balances_notice_container').empty();
                                var month = get_text('months').indexOf(e.currentTarget.category);
                                var year = get_year_from_string(this.series.name);
                                show_month_details(year, month);
                            }
                        }
                    },
                    marker: {
                        lineWidth: 1
                    }
                }
            },
            tooltip: {
                valueDecimals: 2,
                shared: true
            },
            series: [],
            credits: {
                enabled: false
            }
        });
    });
}

function initialize_balance_diagrams_filters() {
    $.getJSON(api_base_url + 'history/', function(history_data) {
        balances_cached_history = history_data;
        $.each(history_data, function(index, year) {
            $('#balances_diagram_filters').append(
                '<label class="btn btn-default">\
                <input class="btn balances_diagram_filter" type="checkbox" value="' + year + '">\
                ' + year + '</label>');
        });
        $('.balances_diagram_filter').change(function () {
            balances_load_year(parseInt($(this).val()), false);
        });

        // preselect first filter
        $('.balances_diagram_filter').first().parent().button('toggle');
    });
}

function balances_load_year(year, check_button) {
    var corresponding_button = $('.balances_diagram_filter[value=\'' + year + '\']');

    if (check_button) {
        corresponding_button.attr('checked', 'checked');
        corresponding_button.parent().addClass('active');
    }

    charts = [];
    $.each(balances_diagram_types, function(index, type) {
        charts.push($('#balances_' + type + '_container').highcharts());
    });
    if (corresponding_button.is(':checked')) {
        var found = false;
        $.each(charts, function(index, chart) {
            $.each(chart.series, function(index2, series) {
                if (series['name'].substr(series['name'].length - 4) == year) {
                    series.show(false);
                    found = true;
                }
            });
        });
        if (!found) {
            $.getJSON(api_base_url + "balance/total/" + year + "/", function(data) {
                balances_cached_data[year] = data;
                var balances = {
                    name: get_text('chart_total_balances_in') + year,
                    type: 'column',
                    data: []
                };
                var rewards = {
                    name: get_text('chart_total_rewards_in') + year,
                    type: 'column',
                    data: []
                };
                var costs = {
                    name: get_text('chart_total_costs_in') + year,
                    type: 'column',
                    data: [],
                };
                $.each(data, function(index, monthly_data) {
                    balances['data'].push(monthly_data.balance);
                    rewards['data'].push(monthly_data.rewards);
                    costs['data'].push(monthly_data.costs);
                });
                charts[0].addSeries(balances);
                charts[1].addSeries(rewards);
                charts[2].addSeries(costs);

                show_month_details(year, data.length - 1);
            });
        }
    } else {
        $.each(charts, function(index, chart) {
            $.each(chart.series, function(index, series) {
                if (get_year_from_string(series['name']) == year) {
                    series.hide(false);
                }
            });
        });
    }

    // if all series are unchecked, show all
    var all_unchecked = true;
    $(".balances_diagram_filter").each(function() {
        if ($(this).is(':checked')) {
            all_unchecked = false;
        }
    });
    if (all_unchecked) {
        $.each(charts, function(index, chart) {
            $.each(chart.series, function(index, series) {
                series.setVisible(true, false);
            });
        });
    }

    // finally redraw all charts
    $.each(charts, function(index, chart) {
        chart.redraw();
    });
}

function show_month_details(year, month) {
    if (year in balances_cached_data) {
        $.each(balances_cached_data[year], function(index, monthly_data) {
            if (month == index) {
                update_balances_table(monthly_data, year, month);
                $('#balances_selected_year').val(year);
                $('#balances_selected_month').val(month);
            }
        });
    }
}

function update_balances_table(data, year, month) {
    $.get('templates/balances_table.html', function(template) {
        var rendered = render_template(template, {
            title: $.format.date(new Date(year, month, 1), "MMMM yyyy"),
            thermal_revenues: {
                text: get_text('thermal_revenues'),
                price: data['prices']['thermal_revenues'],
                value: data['kwh']['thermal_consumption'],
                total: Math.round(data['kwh']['thermal_consumption'] * data['prices']['thermal_revenues'] * 100)/100
            },
            warmwater_revenues: {
                text: get_text('warmwater_revenues'),
                price: data['prices']['warmwater_revenues'],
                value: data['kwh']['warmwater_consumption'],
                total: Math.round(data['kwh']['warmwater_consumption'] * data['prices']['warmwater_revenues'] * 100)/100
            },
            electrical_revenues: {
                text: get_text('electrical_revenues'),
                price: data['prices']['electrical_revenues'],
                value: data['kwh']['electrical_consumption'],
                total: Math.round(data['kwh']['electrical_consumption'] * data['prices']['electrical_revenues'] * 100)/100
            },
            electrical_infeed: {
                text: get_text('electrical_infeed'),
                price: data['prices']['feed_in_reward'] ,
                value: data['kwh']['electrical_infeed'],
                total: Math.round(data['kwh']['electrical_infeed'] * data['prices']['feed_in_reward'] * 100)/100
            },
            gas_consumption: {
                text: get_text('gas_consumption'),
                price: data['prices']['gas_costs'],
                value: data['kwh']['gas_consumption'],
                total: Math.round(data['kwh']['gas_consumption'] * data['prices']['gas_costs'] * 100)/100
            },
            electrical_purchase: {
                text: get_text('electrical_purchase'),
                price: data['prices']['electrical_costs'],
                value: data['kwh']['electrical_purchase'],
                total: Math.round(data['kwh']['electrical_purchase'] * data['prices']['electrical_costs'] * 100)/100
            },
            rewards: data['rewards'],
            costs: data['costs'],
            balance: data['balance'],
        });
        $('#balances_details_container').html(rendered);
    }).done(function() {
        $('#balances_export_button').click(function(event) {
            event.preventDefault();
            export_table($('#balances_table_container'));
        });

        update_date_selection(year, month);
    });
}

function update_date_selection(selected_year, selected_month) {
    var month_options = "";
    $.each(get_text('months'), function(index, month) {
        month_options += '<option value="' + index + '" ' + (index == selected_month ? ' selected': '') + '>' + month + '</option>';
    });
    $('#balances_selected_month').html(month_options);

    $('#balances_selected_month').change(function() {
        show_month_details($('#balances_selected_year').val(), $(this).val());
    });

    var year_options = "";
    $.each(balances_cached_history, function(index, year) {
        year_options += '<option' + (year == selected_year ? ' selected': '') + '>' + year + '</option>';
    });
    $('#balances_selected_year').html(year_options);

    $('#balances_selected_year').change(function() {
        balances_load_year($(this).val(), true);
        show_month_details($(this).val(), $('#balances_selected_month').val());
    });
}

function get_year_from_string(string) {
    return parseInt(string.substr(string.length - 4));
}
