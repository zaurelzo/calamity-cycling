
function buildMonthlyDistanceChart(monthlyDistance) {
          var margin = {top: 20, right: 30, bottom: 90, left: 60};
         var width =  document.getElementById('monthly-distance').offsetWidth  - margin.left - margin.right;
        var height = document.getElementById('monthly-distance').offsetWidth/3 - margin.top - margin.bottom;

    const x = d3.scaleBand()
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .range([height, 0]);

    const svg = d3.select("#monthly-distance").append("svg")
        .attr("id", "svg2")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

//    const div = d3.select("body").append("div")
//        .attr("class", "tooltip")
//        .style("opacity", 0);


        // Conversion des caractères en nombres
//        monthlyDistance.forEach(d => d.population = d.population);

        // Mise en relation du scale avec les données de notre fichier
        // Pour l'axe X, c'est la liste des pays
        // Pour l'axe Y, c'est le max des populations
        x.domain(monthlyDistance.map(d => d.month));
        y.domain([0, d3.max(monthlyDistance, d => d.distance)]);

        // Ajout de l'axe X au SVG
        // Déplacement de l'axe horizontal et du futur texte (via la fonction translate) au bas du SVG
        // Selection des noeuds text, positionnement puis rotation
        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x).tickSize(0))
            .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", "rotate(-65)");

        // Ajout de l'axe Y au SVG avec 6 éléments de légende en utilisant la fonction ticks (sinon D3JS en place autant qu'il peut).
        svg.append("g")
            .call(d3.axisLeft(y))
            .append("text")
                .attr("fill", "#000")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", "0.71em")
                .style("text-anchor", "end")
                .text("km");

        // Ajout des bars en utilisant les données de notre fichier data.tsv
        // La largeur de la barre est déterminée par la fonction x
        // La hauteur par la fonction y en tenant compte de la population
        // La gestion des events de la souris pour le popup
        svg.selectAll(".bar")
            .data(monthlyDistance)
        .enter().append("rect")
            .attr("class", "bar")
            .attr("fill", "blue")
            .attr("stroke", "blue")
            .attr("x", d => x(d.month))
            .attr("width", x.bandwidth())
            .attr("y", d => y(d.distance))
            .attr("height", d => height - y(d.distance));
}


buildMonthlyDistanceChart(monthly_distance);


//build the dropdown menu to show the available year
var select_year_button  = document.querySelector("#select-year-monthly-dist");
//function from average_speed.js
createOptionElement(select_year_button,Object.keys(years_and_months));


// update the average speed graph when clicking on th retrieve button
(function() {
  var httpRequest;
  document.getElementById("retrieve-monthly-dist").addEventListener('click', makeRequest);

  function makeRequest() {
    httpRequest = new XMLHttpRequest();

    if (!httpRequest) {
      alert('Abandon :( Impossible de créer une instance de XMLHTTP');
      return false;
    }
    httpRequest.onreadystatechange = showNewDistances;
    var e = document.querySelector("#select-year-monthly-dist");
    var year = e.options[e.selectedIndex].text;
    if (year !=="Open to select a year" ){
        httpRequest.open('GET'," distance_by_month/"+year );
        httpRequest.send();
    }else {
        return false;
    }

  }

  function showNewDistances() {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      if (httpRequest.status === 200) {
        var asJson = JSON.parse(httpRequest.responseText);
        d3.select("#monthly-distance").select("svg").remove();
        buildMonthlyDistanceChart(asJson["monthly_dist"]);
      } else {
        alert('Il y a eu un problème avec la requête.');
      }
    }
  }
})();


