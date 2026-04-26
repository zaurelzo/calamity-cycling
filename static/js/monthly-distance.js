function buildMonthlyDistanceChart(monthlyDistance) {
    var margin = {top: 20, right: 30, bottom: 90, left: 60};
    var width  = document.getElementById('monthly-distance-chart').offsetWidth - margin.left - margin.right;
    var height = document.getElementById('monthly-distance-chart').offsetWidth / 3 - margin.top - margin.bottom;

    const x = d3.scaleBand().range([0, width]).padding(0.1);
    const y = d3.scaleLinear().range([height, 0]);

    const svg = d3.select("#monthly-distance-chart").append("svg")
        .attr("id", "svg2")
        .attr("width",  width  + margin.left + margin.right)
        .attr("height", height + margin.top  + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    if (!monthlyDistance || monthlyDistance.length === 0) return;

    x.domain(monthlyDistance.map(d => d.month));
    y.domain([0, d3.max(monthlyDistance, d => d.distance)]);

    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x).tickSize(0))
        .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)");

    svg.append("g")
        .call(d3.axisLeft(y))
        .append("text")
            .attr("fill", "#000")
            .attr("transform", "rotate(-90)")
            .attr("y", 6)
            .attr("dy", "0.71em")
            .style("text-anchor", "end")
            .text("km");

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


// On load: show first available year from preloaded data
var firstYear = Object.keys(monthly_distance)[0];
if (firstYear) {
    buildMonthlyDistanceChart(monthly_distance[firstYear]);
}

// Build year dropdown
var select_year_button = document.querySelector("#select-year-monthly-dist");
createOptionElement(select_year_button, Object.keys(monthly_distance));


// Retrieve on button click
(function () {
    var httpRequest;
    document.getElementById("retrieve-monthly-dist").addEventListener('click', makeRequest);

    function makeRequest() {
        var e    = document.querySelector("#select-year-monthly-dist");
        var year = e.options[e.selectedIndex].text;

        if (!year || year === "Select a year") return false;

        httpRequest = new XMLHttpRequest();
        if (!httpRequest) {
            alert('Could not create XMLHttpRequest');
            return false;
        }

        httpRequest.onreadystatechange = showNewDistances;
        httpRequest.open('GET', "distance_by_month/" + year);
        httpRequest.send();
    }

    function showNewDistances() {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                var asJson = JSON.parse(httpRequest.responseText);
                d3.select("#monthly-distance-chart").select("svg").remove();
                buildMonthlyDistanceChart(asJson["data"]);
            } else {
                alert('Error fetching monthly distance.');
            }
        }
    }
})();