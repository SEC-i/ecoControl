function draw_diagram(){
    var sensor_data = null;
    var valuesx = [];
    var valuesy = [];

    $("#diagram_container").html('');

    $.get( api_url + "device/" + device_id + "/sensors/", function( data ) {
        sensor_data = data;
    }).done(function() { // sensor details ready

        // add all entries to sensor details
        $.get( api_url + "device/" + device_id + "/entries/start/" + range_start + "/end/" + range_end + "/", function( data ) {
            $.each(sensor_data, function(sensor_index, sensor_value){
                $.each(data, function(index, value){
                    if(sensor_value['id'] == value['sensor_id']){
                        if(valuesx[sensor_index] == undefined){
                            valuesx[sensor_index] = [];
                        }
                        if(valuesy[sensor_index] == undefined){
                            valuesy[sensor_index] = [];
                        }
                        valuesx[sensor_index].push(value['timestamp']);
                        valuesy[sensor_index].push(value['value']);
                    }
                });
            });
        }).done(function() { // all data ready for diagram

            if (valuesx.length == 0 || valuesy.length == 0){
                $("#diagram_container").html('<p><br /></p><div class="row"><div class="col-lg-6"><div class="alert alert-warning">No data available!</div></div></div>');
                return false;
            }

            var r = Raphael("diagram_container");

            var lines = r.linechart(20, 50, 800, 400, valuesx, valuesy,
                    { nostroke: false,
                        axis: "0 0 1 1",
                    }
                );

            $.each(sensor_data, function(index, value){
                r.text(850, 60 + 20 * index, "--- " + value['name'] + " in " + value['unit']).attr({
                    'text-anchor': 'start',
                    'font-size' : 12,
                    'fill' : Raphael.g.colors[index],});
            });

            // change the x-axis labels 
            var axisItems = lines.axis[0].text.items;
            for( var i = 0, l = axisItems.length; i < l; i++ ) {
               var date = new Date(parseInt(axisItems[i].attr("text")));
               axisItems[i].attr("text", $.formatDateTime('dd.mm.y hh:ii', date));
            }
        });    
    });
}