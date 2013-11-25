
        var margin = {top: 20, right: 10, bottom: 30, left: 100},
            width = 990 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom;

        var x = d3.time.scale()
            .range([0, width]);

        var y0 = d3.scale.linear().range([height, 0]);

        var y1 = d3.scale.linear().range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxisLeft = d3.svg.axis()
            .scale(y0)
            .orient("left");

        var yAxisRight = d3.svg.axis()
            .scale(y1)
            .orient("right");


        var line = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y0(d['value']); });

        var line_right = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y1(d['value']); });  //switched to y0 for one axis



function showDiagram(){

        var margin = {top: 20, right: 20, bottom: 30, left: 80},
            width = 990 - margin.left - margin.right,
            height = 500 - margin.top - margin.bottom;

        var x = d3.time.scale()
            .range([0, width]);

        var y0 = d3.scale.linear().range([height, 0]);

        var y1 = d3.scale.linear().range([height, 0]);

        var xAxis = d3.svg.axis()
            .scale(x)
            .orient("bottom");

        var yAxisLeft = d3.svg.axis()
            .scale(y0)
            .orient("left");

        var yAxisRight = d3.svg.axis()
            .scale(y1)
            .orient("right");

        var line = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y0(d['value']); });

        var line_right = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y1(d['value']); }); 



        var svg = d3.select("body").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var yesterday = new Date().getTime()-24*60*60*1000;
        d3.json(base_url_get+"device/2/entries/start/" + yesterday + "/", function(error, data) {
              var plant1_value = [];
              var plant2_value = [];
              var plant3_value = [];
              var plant4_value = [];
              var temperature_value = [];
              var light_value = [];


              data.forEach(function(d) {
                d['timestamp'] = new Date(d['timestamp']*1000);

        
                switch(d['sensor_id']){
                  case 5: plant1_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 6: plant2_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 15: plant3_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 16: plant4_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 8: temperature_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 7: light_value.push({value: d['value'], timestamp: d['timestamp']}); break;

                }
              });

              x.domain(d3.extent(data, function(d){ 
                return d['timestamp']; 
              }));

              y0.domain([0, d3.max(data, function(d) { 
                return Math.max(d['value']); 
              })]); 

              y1.domain([20, d3.max(data, function(d) { 
                return 50; 
              })])
        

              svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + height + ")")
              .call(xAxis);

              svg.append("g")
              .attr("class", "y axis")
              .call(yAxisLeft)
              .style("fill", "green")
              .call(yAxisLeft);

            

              svg.append("text")
                  //.attr("transform", "rotate(-90)")
                  .attr("y", 6)
                  .attr("dy", ".71em")
                  .style("text-anchor", "end")
                  .text("einheit");


              svg.append("g")
              .attr("class", "y axis")
              .call(yAxisRight)
              .attr("transform", "translate(" + width + " ,0)")
              .style("fill", "blue")
              .call(yAxisRight);


              svg.append("text")
                  .attr("transform", "rotate(-90)")
                  .attr("transform", "translate(" + width + " ,0)")
                  .attr("y", 6)
                  .attr("dy", ".71em")
                  .style("text-anchor", "end")
                  .text("Grad Celsius");

               svg.append("path")      // Add the elec_power_line path.
                .attr("id", "plant1")
                .attr("class", "line")
                .style("stroke", "green")
                .attr("d", line(plant1_value))
                ;

         
                svg.append("path")
                  .attr("id", "plant2")
                  .attr("class", "line")
                  .style("stroke", "#87A96B")
                  .attr("d", line(plant2_value))
                  ;

         
                svg.append("path")
                  .attr("id", "plant3")
                  .attr("class", "line")
                  .style("stroke", "#29AB87")
                  .attr("d", line(plant3_value))
                  ;

         
                svg.append("path")
                  .attr("id", "plant4")
                  .attr("class", "line")
                  .style("stroke", "#013220")
                  .attr("d", line(plant4_value))
                  ;
            
           
                svg.append("path")
                  .attr("id", "temp")
                  .attr("class", "line")
                  .style("stroke", "blue")
                  .attr("d", line_right(temperature_value))
                  ;

                  svg.append("path")
                  .attr("id", "light")
                  .attr("class", "line")
                  .style("stroke", "red")
                  .attr("d", line(light_value))
                  ;
            
            
            
        
        }); 

  
  } //end ShowDiagram
   



  function updateData() {

      
          if (!$("#update_button").prop("checked"))
             return;

           var line = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y0(d['value']); });


         d3.json(base_url_get+"device/2/entries/limit/10000/", function(error, data) {
              var plant1_value = [];
              var plant2_value = [];
              var plant3_value = [];
              var plant4_value = [];
              var temperature_value = [];
              var light_value = [];


              data.forEach(function(d) {
                d['timestamp'] = new Date(d['timestamp']*1000);

        
                switch(d['sensor_id']){
                  case 5: plant1_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 6: plant2_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 15: plant3_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 16: plant4_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 8: temperature_value.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 7: light_value.push({value: d['value'], timestamp: d['timestamp']}); break;

                }
              });
                  // Scale the range of the data again 
             x.domain(d3.extent(data, function(d){ 
                return d['timestamp']; 
              }));

              y0.domain([0, d3.max(data, function(d) { 
                return Math.max(d['value']); 
              })]); 

              y1.domain([20, d3.max(data, function(d) { 
                return 50; 
              })]);
      
                  // Select the section we want to apply our changes to
              var svg = d3.select("body").transition();

          // Make the changes
            

    
                
             
              svg.select("#plant1")   // change the line
                  .duration(250)
                  .attr("d", line(plant1_value))
                  .style("stroke", "green");
    
              svg.select("#plant2")   // change the line
                  .duration(250)
                  .style("stroke", "#87A96B")
                  .attr("d", line(plant2_value));
             
              svg.select("#plant3")   // change the line
                  .duration(250)
                  .attr("d", line(plant3_value))
                  .style("stroke", "#29AB87");
    
                
             
              svg.select("#plant4")   // change the line
                  .duration(250)
                  .attr("d", line(plant4_value))
                  .style("stroke", "#013220");


          
                 svg.select("#temp")   // change the line
                  .duration(250)
                  .attr("d", line_right(temperature_value))
                  .style("stroke", "blue");

                 svg.select("#light")   // change the line
                  .duration(250)
                  .attr("d", line(light_value))
                  .style("stroke", "red");
              
                
              svg.select(".x.axis") // change the x axis
                  .duration(250)
                  .call(xAxis);

              svg.select(".y.axis") // change the y axis
                  .duration(250)
                  .call(yAxisLeft);

               svg.select(".y.axis") // change the y axis
                  .duration(250)
                  .call(yAxisRight);

          });
  }