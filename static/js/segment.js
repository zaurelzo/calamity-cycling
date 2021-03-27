function buildAverageSpeedForAGivenSegment(averageSpeedData) {
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


    const svg = d3.select("#segment-info").append("svg")
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
                .text("km/h");


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

function selectElementsFromSegments(segs,tupleIndex){
    var cities = {};
    for (property in segs){
        city = segs[property][tupleIndex];
        if (city!=null && !cities.hasOwnProperty(city)){
            cities[city]=true;
        }
    }
    return cities;
}


//build the dropdown menu to show the available segment name
//function from average_speed.js
createOptionElement(document.querySelector("#select-segments-name"),Object.keys(segments));
// empty average speed graph
buildAverageSpeedForAGivenSegment([]);

//build the dropdown menu to show the available city Name
createOptionElement(document.querySelector("#select-segments-city"),
                    Object.keys( selectElementsFromSegments(segments,3)).sort());

//build the dropdown menu to show the available region
createOptionElement(document.querySelector("#select-segments-region"),
                    Object.keys( selectElementsFromSegments(segments,4)).sort());


// update the average speed of a segment when clicking on th retrieve button
(function() {
  var httpRequest;
  document.getElementById("retrieve-segment-info").addEventListener('click', makeRequest);

  function makeRequest() {
    httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
      alert('Abandon :( Impossible de créer une instance de XMLHTTP');
      return false;
    }
    httpRequest.onreadystatechange = showSegmentsInfo;
    var e = document.querySelector("#select-segments-name");
    var seg = e.options[e.selectedIndex].text;
    if (seg !=="Open to select a segment" ){
        var seg_id_dist_grade = segments[seg]
        console.log("get_recorded_time_for_a_segment/"+seg_id_dist_grade[0]);
        httpRequest.open('GET',"get_recorded_time_for_a_segment/"+seg_id_dist_grade[0] );
        httpRequest.send();
    }else {
        return false;
    }

  }

  function showSegmentsInfo() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        var asJson = JSON.parse(httpRequest.responseText);
        d3.select("#segment-info").select("svg").remove();
        buildAverageSpeedForAGivenSegment(asJson["segments"]);
      } else {
        alert('Il y a eu un problème avec la requête.');
      }
    }
  }
})();


function filterSegmentByRegions() {
    var selectorRegions =document.querySelector("#select-segments-region");
    var region = selectorRegions.options[selectorRegions.selectedIndex].text;
    //filter by region
    var segmentsByRegions = {};
     if (region==="All regions"){
        segmentsByRegions=segments;
    }else {
        for (var seg in segments) {
            if (segments[seg][4]===region){
                segmentsByRegions[seg] = segments[seg];
            }
        }
    }
    //show available city by regions.
    document.querySelector("#select-segments-city").options.length = 1;
    createOptionElement(document.querySelector("#select-segments-city"),
                    Object.keys( selectElementsFromSegments(segmentsByRegions,3)).sort());
}

//sort segments
function sortSegments() {
    var selectorCity =document.querySelector("#select-segments-city");
    var city = selectorCity.options[selectorCity.selectedIndex].text;
     //filter by city
     var segmentsByCity = {};
    if (city==="All cities"){
        segmentsByCity=segments;
    }else {
        for (var seg in segments) {
            if (segments[seg][3]===city){
                segmentsByCity[seg] = segments[seg];
            }
        }
    }

    var sortable = [];
    var keysSorted = {};
    for (var seg in segmentsByCity) {
        //segment name, id, distance, average grade
        sortable.push([seg,segments[seg][0], segments[seg][1],segments[seg][2]]);
    }
    //sort segments according to the selected criteria
    var e = document.querySelector("#segements-order");
    var criteria = e.options[e.selectedIndex].text;
    switch(criteria) {
        case 'Ascending average grade' :
            sortable.sort(function(a, b) { return a[3] - b[3];});
             for (var id in sortable) {
                keysSorted[sortable[id][0]]=sortable[id][3];
             }
            break;
        case 'Descending average grade' :
            sortable.sort(function(a, b) { return b[3] - a[3];});
            for (var id in sortable) {
                keysSorted[sortable[id][0]]=sortable[id][3];
             }
            break;
        case 'Ascending distance' :
            sortable.sort(function(a, b) { return a[2] - b[2];});
            for (var id in sortable) {
                keysSorted[sortable[id][0]]=sortable[id][2];
             }
            break;
        case 'Descending distance' :
            sortable.sort(function(a, b) { return b[2] - a[2];});
            for (var id in sortable) {
                keysSorted[sortable[id][0]]=sortable[id][2];
             }
            break;
        case 'Ascending segment name':
            sortable.sort(function(a, b) {
            if (b > a) {
                 return -1;
            }
             if (a > b) {
                 return 1;
              }
              return 0;}
            );
            for (var id in sortable) {
                keysSorted[sortable[id][0]]=sortable[id][0];
             }
            break;
        case 'Descending segment name':
            sortable.sort(function(a, b) {
            if (a > b) {
                 return -1;
            }
             if (b > a) {
                 return 1;
              }
              return 0;}
            );
            for (var id in sortable) {
                keysSorted[sortable[id][0]]=sortable[id][0];
             }
            break;
        default:
            keysSorted = segments;
            break;
    }
    document.querySelector("#select-segments-name").options.length = 1;
    //build the dropdown menu to show the available segment name
    var select_segments_button  = document.querySelector("#select-segments-name");
    //function from average_speed.js
    createOptionElement(select_segments_button,Object.keys(keysSorted));
}

