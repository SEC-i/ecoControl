

var base_url = "http://172.16.64.130/api/";

var base_url_get = "http://172.16.64.130/api/"
$(document).ready(function(){

 
  setInterval("updateData()", 1000);   

  showDiagram();


  $("#switch_button").click(function(event) {
    var jsonData = {"workload": "70" }
    $.post(base_url_get+"device/1/set/", jsonData , function(data) {
      console.log(data);
    });
  });





    $( "#slider" ).slider({
      value:100,
      min: 0,
      max: 100,
      step: 10,
      slide: function( event, ui ) {
        $( "#bhkw_workload" ).val ( ui.value + "%");
      },
      change: function( event, ui ) {
        //alert("This is the workload: " + $( "#slider" ).slider( "value" ));

      
          var jsonWorkload = { "workload" : $( "#slider" ).slider( "value" )};
          $.post(base_url_get+"device/1/set/", jsonWorkload , function(data) {
             console.log(data);
           });
   

      }
    });
    $( "#bhkw_workload" ).val(  $( "#slider" ).slider( "value" ) +  "%" );
  

});
