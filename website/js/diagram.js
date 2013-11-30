var sensor_data = null;

function prepare_diagram_menu(){
    $.get( api_url + "device/" + device_id + "/sensors/", function( data ) {
        sensor_data = data;

        $("#sensor_list").html('<li class="sensor_items" value="0">' +
            '<a href="#">All sensors</a></li><li class="divider"></li>'+
            '<li class="dropdown-header">Individual sensors</li>');

        $.each(data, function(index, value){
            $("#sensor_list").append('<li class="sensor_items" value="' + value['id'] + '"><a href="#">' + value['name'] + '</a></li>');
        });

        $(".sensor_items").click(function(event) {
            sensor_id = $(this).attr('value');
            $("#sensor_selection").html($('> a', this).text() + ' <span class="caret"></span>');
            draw_diagram();
        });

        $("#refresh_button").click(function(event) {
            range_end = new Date().getTime();
            draw_diagram();
        });
        
    });
}

function draw_diagram(){
    var valuesx = [];
    var valuesy = [];

    if(sensor_id > 0){
        var url = api_url + "sensor/" + sensor_id + "/entries/";
    }else{
        var url = api_url + "device/" + device_id + "/entries/";
    }

    // add all entries to sensor details
    $.get( url + "start/" + range_start + "/end/" + range_end + "/", function( data ) {
        var values_index = 0;
        $.each(sensor_data, function(sensor_index, sensor_value){
            $.each(data, function(index, value){
                if(sensor_value['id'] == value['sensor_id']){
                    if(valuesx[values_index] == undefined){
                        valuesx[values_index] = [];
                    }
                    if(valuesy[values_index] == undefined){
                        valuesy[values_index] = [];
                    }
                    valuesx[values_index].push(value['timestamp']);
                    valuesy[values_index].push(value['value']);
                }
            });
            if(valuesx[values_index] != undefined){
                values_index++;
            }
        });
    }).done(function() { // all data ready for diagram

        $("#diagram_container").html('');

        if (valuesx.length == 0 || valuesy.length == 0){
            $("#diagram_container").html('<p><br /></p><div class="row"><div class="col-lg-6"><div class="alert alert-warning">No data available!</div></div></div>');
            return false;
        }

        var r = Raphael("diagram_container");

        var lines = r.linechart(30, 50, 800, 400, valuesx, valuesy,
                { nostroke: false,
                    axis: "0 0 1 1",
                }
            );


        $.each(sensor_data, function(index, value){
            if (sensor_id > 0){
                if(sensor_id == value['id']){
                    r.text(850, 60, "--- " + value['name'] + " in " + value['unit']).attr({
                        'text-anchor': 'start',
                        'font-size' : 12,
                        'fill' : Raphael.g.colors[0],});
                }
            } else {
                r.text(850, 60 + 20 * index, "--- " + value['name'] + " in " + value['unit']).attr({
                    'text-anchor': 'start',
                    'font-size' : 12,
                    'fill' : Raphael.g.colors[index],});
            }
        });

        // change the x-axis labels 
        var axisItems = lines.axis[0].text.items;
        for( var i = 0, l = axisItems.length; i < l; i++ ) {
           var date = new Date(parseInt(axisItems[i].attr("text")));
           axisItems[i].attr("text", $.formatDateTime('dd.mm.y hh:ii', date));
        }
    });    
}