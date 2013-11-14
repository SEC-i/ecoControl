        var diagram_var = '';
        var diagram_col = '';

        var diagram_var = 'temperature';
        var diagram_col = 'red';


        var diagram_var = 'electrical_power';
        var diagram_col = 'blue';

        var both = true;

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
            .y(function(d) { return y1(d['value']); });


        var line2 = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y0(d['value']); });




;


function showDiagram(){


        var diagram_var = 'temperature';
        var diagram_col = 'red';


        var diagram_var = 'electrical_power';
        var diagram_col = 'blue';

     

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
            .y(function(d) { return y1(d['value']); });


        var line2 = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y0(d['value']); });


        var svg = d3.select("body").append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");



        d3.json(base_url_get+"device/1/entries/limit/200/", function(error, data) {
              var electrical_power = [];
              var thermal_power = [];
              var gas_input = [];
              var workload = [];


              data.forEach(function(d) {
                d['timestamp'] = new Date(d['timestamp']*1000);

        
                switch(d['sensor_id']){
                  case 2: electrical_power.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 3: thermal_power.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 4: gas_input.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 5: workload.push({value: d['value'], timestamp: d['timestamp']}); break;

                }
              });

              console.log(electrical_power);

              x.domain(d3.extent(data, function(d){ 
                return d['timestamp']; 
              }));

              y0.domain([0, d3.max(data, function(d) { 
                return Math.max(d['value']); 
              })]); 
              
                  y1.domain([0, d3.max(data, function(d){ return Math.max(d['value']);})]); //todo
             


              svg.append("g")
              .attr("class", "x axis")
              .attr("transform", "translate(0," + height + ")")
              .call(xAxis);

              svg.append("g")
              .attr("class", "y axis")
              .call(yAxisLeft)
              .style("fill", "green")
              .call(yAxisLeft);

              svg.append("g")
              .attr("class", "y axis")
              .call(yAxisRight)
              .attr("transform", "translate(" + width + " ,0)")
              .style("fill", diagram_col)
              .call(yAxisRight);


              svg.append("text")
                  //.attr("transform", "rotate(-90)")
                  .attr("y", 6)
                  .attr("dy", ".71em")
                  .style("text-anchor", "end")
                  .text("gasAmount");

              svg.append("text")
                  .attr("transform", "rotate(-90)")
                  .attr("transform", "translate(" + width + " ,0)")
                  .attr("y", 6)
                  .attr("dy", ".71em")
                  .style("text-anchor", "end")
                  .text(diagram_var);

               svg.append("path")      // Add the elec_power_line path.
                .attr("id", "gas")
                .attr("class", "line")
                .style("stroke", "green")
                .attr("d", line(gas_input))
                ;

                  svg.append("path")
                    .attr("id", "temp")
                    .attr("class", "line")
                    .style("stroke", "red")
                    .attr("d", line2(thermal_power))
                    ;

                  svg.append("path")
                    .attr("id", "elek")
                    .attr("class", "line")
                    .style("stroke", "blue")
                    .attr("d", line2(electrical_power))
                    ;
            
        
        }); 

  
  } //end ShowDiagram
   



  function updateData() {

      
           var line = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y1(d['value']); });


          var line2 = d3.svg.line()
            .x(function(d) { return x(d['timestamp']); })
            .y(function(d) { return y0(d['value']); });


          d3.json(base_url_get+"device/1/entries/limit/200/", function(error, data) {
              var electrical_power = [];
              var thermal_power = [];
              var gas_input = [];
              var workload = [];


              data.forEach(function(d) {
                d['timestamp'] = new Date(d['timestamp']*1000);

        
                switch(d['sensor_id']){
                  case 2: electrical_power.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 3: thermal_power.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 4: gas_input.push({value: d['value'], timestamp: d['timestamp']}); break;
                  case 5: workload.push({value: d['value'], timestamp: d['timestamp']}); break;

                }
              });
                  // Scale the range of the data again 
             x.domain(d3.extent(data, function(d){ 
                return d['timestamp']; 
              }));

              y0.domain([0, d3.max(data, function(d) { 
                return Math.max(d['value']); 
              })]); 
              
                  y1.domain([0, d3.max(data, function(d){ return Math.max(d['value']);})]); //todo

                  // Select the section we want to apply our changes to
              var svg = d3.select("body").transition();

          // Make the changes
              svg.select("#temp")   // change the line
                  .duration(250)
                  .style("stroke", "red")
                  .attr("d", line(thermal_power));
                
             
              svg.select("#gas")   // change the line
                  .duration(250)
                  .attr("d", line2(gas_input))
                  .style("stroke", "green");

                 svg.select("#elek")   // change the line
                  .duration(250)
                  .attr("d", line(electrical_power))
                  .style("stroke", "blue");
            
                
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