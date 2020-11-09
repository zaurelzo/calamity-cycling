

function buildAverageSpeedGraph(averageSpeedData) {
    var margin = {top: 20, right: 30, bottom: 30, left: 60};
    var width = document.getElementById('average_speed').clientWidth - margin.left - margin.right;
    var  height = document.getElementById('average_speed').clientWidth/3.236 - margin.top - margin.bottom;

    const parseTime = d3.timeParse("%Y-%m-%d");
    const dateFormat = d3.timeFormat("%Y-%m-%d");

    const x = d3.scaleTime()
        .range([0, width]);

    const y = d3.scaleLinear()
        .range([height, 0]);

             // define the line
             var line = d3.line()
                .x(function(d) { return x(d.date); })
                .y(function(d) {  return y(d.speed); });


    const svg = d3.select("#average_speed").append("svg")
        .attr("id", "svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


        // Conversion des données du fichier, parsing des dates et '+' pour expliciter une valeur numérique.
        averageSpeedData.forEach(function(d) {
            d.date = parseTime(d.date);
           // d.speed = d.speed
        });

        // Contrairement au tutoriel Bar Chart, plutôt que de prendre un range entre 0 et le max on demande
        // directement à D3JS de nous donner le min et le max avec la fonction 'd3.extent', pour la date comme
        // pour le cours de fermeture (close).
        x.domain(d3.extent(averageSpeedData, d => d.date));
        y.domain(d3.extent(averageSpeedData, d => d.speed));

        // Ajout de l'axe X
        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

        // Ajout de l'axe Y et du texte associé pour la légende
        svg.append("g")
            .call(d3.axisLeft(y))
            .append("text")
                .attr("fill", "#000")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", "0.71em")
                .style("text-anchor", "end")
                .text(" average speed");


        svg.append('defs')
        .append('marker')
        .attr('id', 'dot')
        .attr('viewBox', [0, 0, 20, 20])
        .attr('refX', 10)
        .attr('refY', 10)
        .attr('markerWidth', 5)
        .attr('markerHeight', 5)
        .append('circle')
        .attr('cx', 10)
        .attr('cy', 10)
        .attr('r', 10)
        .style('fill', 'green');


        // Ajout d'un path calculé par la fonction line à partir des données de notre fichier.
        svg.append("path")
            .datum(averageSpeedData)
            .attr("class", "line")
            .attr("d", line)
            .attr("fill", "none")
            .attr("stroke", "blue")
            .attr("stroke-width", 2)
            .attr('marker-start', 'url(#dot)')
        .attr('marker-mid', 'url(#dot)')
        .attr('marker-end', 'url(#dot)');

}

buildAverageSpeedGraph(average_speed_array);

//build the dropdown menu to show the available year and month for the average speed graph
var select_year_button  = document.querySelector("#select-year");
createOptionElement(select_year_button,Object.keys(years_and_months))
//
function createOptionElement (ul, list_option_element){
    for (li_value of list_option_element) {
        var li=document.createElement('option');
        li.innerHTML=li_value
        ul.appendChild(li);
    }
}


function updateAvailableMonths() {
    var e = document.querySelector("#select-year");
    var value = e.options[e.selectedIndex].text;
    if (years_and_months.hasOwnProperty(value)){
        let select_month_button  = document.querySelector("#select-month");
        createOptionElement(select_month_button,years_and_months[value])
    }else {
        //keep the first option
    	document.querySelector("#select-month").options.length = 1;
    }
}

const month_to_id = {"JANUARY":1,"FEBRUARY":2,"MARCH":3,"APRIL":4,"MAY":5,"JUNE":6,
"JULY":7,"AUGUST":8,"SEPTEMBER":9,"OCTOBER":10,"NOVEMBER":11,"DECEMBER":12};

// update the average speed graph when clicking on th retrieve button
(function() {
  var httpRequest;
  document.getElementById("retrieve-average-speed").addEventListener('click', makeRequest);

  function makeRequest() {
    httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
      alert('Abandon :( Impossible de créer une instance de XMLHTTP');
      return false;
    }
    httpRequest.onreadystatechange = showNewAverageSpeed;
    var e = document.querySelector("#select-year");
    var year = e.options[e.selectedIndex].text;
    var f = document.querySelector("#select-month");
    var month = f.options[f.selectedIndex].text;
    var ulr_average_speed
    if (year !=="All years" && month!=="All months"){
        ulr_average_speed ="average_speed"+ "/" + year + "/"+  month_to_id[month.toUpperCase()]
    }else if (year !=="All years" && month!=="All months" ){
        ulr_average_speed ="average_speed"+ "/" + year
    }else {
        ulr_average_speed ="average_speed"
    }
    httpRequest.open('GET', ulr_average_speed );
    httpRequest.send();
  }

  function showNewAverageSpeed() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        var asJson = JSON.parse(httpRequest.responseText);
        d3.select("#average_speed").select("svg").remove();
        buildAverageSpeedGraph(asJson["average_speed"]);
      } else {
        alert('Il y a eu un problème avec la requête.');
      }
    }
  }
})();




