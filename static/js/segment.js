// -------------------------------------------------------
// STATE
// -------------------------------------------------------
var filteredSegments = Object.assign({}, segments);
var selectedSegmentName = null;

// -------------------------------------------------------
// CHART
// -------------------------------------------------------
function buildSegmentChart(data, segmentName, segmentMeta) {
    d3.select("#segment-chart").select("svg").remove();
    d3.select("#segment-chart").select(".segment-empty").remove();

    if (!data || data.length === 0) {
        d3.select("#segment-chart")
            .append("div")
            .attr("class", "segment-empty")
            .style("display", "flex")
            .style("align-items", "center")
            .style("justify-content", "center")
            .style("height", "200px")
            .style("color", "#555")
            .style("font-size", "0.85rem")
            .style("letter-spacing", "0.1em")
            .text("No data found for this segment");
        return;
    }

    var container = document.getElementById("segment-chart");
    var margin = {top: 30, right: 30, bottom: 50, left: 60};
    var width  = container.offsetWidth - margin.left - margin.right;
    var height = Math.max(200, container.offsetWidth / 3.5) - margin.top - margin.bottom;

    const parseTime = d3.timeParse("%Y-%m-%d");

    data.forEach(d => { d.date = parseTime(d.date); });

    const x = d3.scaleTime().range([0, width])
        .domain(d3.extent(data, d => d.date));
    const y = d3.scaleLinear().range([height, 0])
        .domain([d3.min(data, d => d.speed) * 0.95, d3.max(data, d => d.speed) * 1.05]);

    var line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.speed))
        .curve(d3.curveMonotoneX);

    const svg = d3.select("#segment-chart").append("svg")
        .attr("width",  width  + margin.left + margin.right)
        .attr("height", height + margin.top  + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Grid lines
    svg.append("g")
        .attr("class", "grid")
        .call(d3.axisLeft(y).tickSize(-width).tickFormat(""))
        .selectAll("line")
        .style("stroke", "#2a2a2a")
        .style("stroke-dasharray", "3,3");

    svg.select(".grid .domain").remove();

    // Axes
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(6))
        .selectAll("text, line, path")
        .style("stroke", "#555")
        .style("fill", "#555");

    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text, line, path")
        .style("stroke", "#555")
        .style("fill", "#555");

    svg.append("text")
        .attr("fill", "#555")
        .attr("transform", "rotate(-90)")
        .attr("y", -45)
        .attr("x", -height / 2)
        .style("text-anchor", "middle")
        .style("font-size", "0.7rem")
        .style("letter-spacing", "0.1em")
        .text("km/h");

    // Area fill
    var area = d3.area()
        .x(d => x(d.date))
        .y0(height)
        .y1(d => y(d.speed))
        .curve(d3.curveMonotoneX);

    svg.append("path")
        .datum(data)
        .attr("fill", "rgba(255, 92, 26, 0.08)")
        .attr("d", area);

    // Line
    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#ff5c1a")
        .attr("stroke-width", 2)
        .attr("d", line);

    // Dots
    svg.selectAll(".dot")
        .data(data)
        .enter().append("circle")
        .attr("class", "dot")
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.speed))
        .attr("r", 4)
        .attr("fill", "#ff5c1a")
        .attr("stroke", "#0a0a0a")
        .attr("stroke-width", 2)
        .on("mouseover", function(d) {
            d3.select(this).attr("r", 6);
            tooltip.style("opacity", 1)
                .html(`<strong>${d3.timeFormat("%d %b %Y")(d.date)}</strong><br/>${d.speed} km/h`);
        })
        .on("mousemove", function() {
            tooltip
                .style("left",  (d3.event.pageX + 12) + "px")
                .style("top",   (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).attr("r", 4);
            tooltip.style("opacity", 0);
        });
}

// Tooltip
var tooltip = d3.select("body").append("div")
    .style("position", "absolute")
    .style("background", "#1a1a1a")
    .style("border", "1px solid #2a2a2a")
    .style("color", "#f5f0e8")
    .style("padding", "8px 12px")
    .style("font-size", "0.75rem")
    .style("pointer-events", "none")
    .style("opacity", 0)
    .style("border-radius", "2px");


// -------------------------------------------------------
// SEGMENT LIST
// -------------------------------------------------------
function buildSegmentList(segs) {
    var list = document.getElementById("segment-list");
    list.innerHTML = "";

    var keys = Object.keys(segs);

    if (keys.length === 0) {
        list.innerHTML = '<div style="padding:1rem;color:#555;font-size:0.8rem;letter-spacing:0.1em;">No segments found</div>';
        return;
    }

    keys.forEach(function(name) {
        var meta    = segs[name];
        var dist    = meta.distance ? (meta.distance / 1000).toFixed(1) + " km" : "—";
        var grade   = meta.avg_grade != null ? meta.avg_grade + "%" : "—";
        var city    = meta.city || "—";

        var item = document.createElement("div");
        item.className = "segment-item" + (name === selectedSegmentName ? " active" : "");
        item.dataset.name = name;
        item.innerHTML = `
            <div class="segment-item-name">${name}</div>
            <div class="segment-item-meta">${city} &nbsp;·&nbsp; ${dist} &nbsp;·&nbsp; ${grade} avg grade</div>
        `;

        item.addEventListener("click", function() {
            document.querySelectorAll(".segment-item").forEach(el => el.classList.remove("active"));
            item.classList.add("active");
            selectedSegmentName = name;
            loadSegmentChart(meta.id, name, meta);
        });

        list.appendChild(item);
    });
}

function loadSegmentChart(segmentId, name, meta) {
    var chart = document.getElementById("segment-chart");
    chart.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:200px;color:#555;font-size:0.8rem;letter-spacing:0.1em;">Loading…</div>';

    document.getElementById("segment-chart-title").textContent = name;
    var dist  = meta.distance ? (meta.distance / 1000).toFixed(1) + " km" : "";
    var grade = meta.avg_grade != null ? meta.avg_grade + "% avg grade" : "";
    document.getElementById("segment-chart-meta").textContent = [dist, grade].filter(Boolean).join("  ·  ");

    fetch("get_recorded_time_for_a_segment/" + segmentId)
        .then(r => r.json())
        .then(json => {
            chart.innerHTML = "";
            buildSegmentChart(json.data, name, meta);
        })
        .catch(() => {
            chart.innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:200px;color:#555;">Error loading data</div>';
        });
}


// -------------------------------------------------------
// FILTERS
// -------------------------------------------------------
function getUniqueValues(segs, key) {
    var vals = {};
    for (var name in segs) {
        var v = segs[name][key];
        if (v) vals[v] = true;
    }
    return Object.keys(vals).sort();
}

function populateSelect(id, values, placeholder) {
    var el = document.getElementById(id);
    el.innerHTML = '<option selected>' + placeholder + '</option>';
    values.forEach(function(v) {
        var opt = document.createElement("option");
        opt.value = v;
        opt.textContent = v;
        el.appendChild(opt);
    });
}

function applyFilters() {
    var region = document.getElementById("seg-filter-region").value;
    var city   = document.getElementById("seg-filter-city").value;
    var order  = document.getElementById("seg-filter-order").value;

    var result = {};
    for (var name in segments) {
        var s = segments[name];
        if (region && region !== "All regions" && s.state !== region) continue;
        if (city   && city   !== "All cities"  && s.city  !== city)   continue;
        result[name] = s;
    }

    // Sort
    var entries = Object.entries(result);
    switch (order) {
        case "Grade ↑":   entries.sort((a,b) => (a[1].avg_grade||0) - (b[1].avg_grade||0)); break;
        case "Grade ↓":   entries.sort((a,b) => (b[1].avg_grade||0) - (a[1].avg_grade||0)); break;
        case "Distance ↑":entries.sort((a,b) => (a[1].distance||0)  - (b[1].distance||0));  break;
        case "Distance ↓":entries.sort((a,b) => (b[1].distance||0)  - (a[1].distance||0));  break;
        case "Name A→Z":  entries.sort((a,b) => a[0].localeCompare(b[0]));                  break;
        case "Name Z→A":  entries.sort((a,b) => b[0].localeCompare(a[0]));                  break;
    }

    filteredSegments = Object.fromEntries(entries);
    buildSegmentList(filteredSegments);
}

// Region change → update city options
document.getElementById("seg-filter-region").addEventListener("change", function() {
    var region = this.value;
    var citiesInRegion = {};
    for (var name in segments) {
        if (region === "All regions" || segments[name].state === region) {
            var c = segments[name].city;
            if (c) citiesInRegion[c] = true;
        }
    }
    populateSelect("seg-filter-city", Object.keys(citiesInRegion).sort(), "All cities");
    applyFilters();
});

document.getElementById("seg-filter-city").addEventListener("change", applyFilters);
document.getElementById("seg-filter-order").addEventListener("change", applyFilters);

// Search
document.getElementById("seg-search").addEventListener("input", function() {
    var q = this.value.toLowerCase();
    var result = {};
    for (var name in filteredSegments) {
        if (name.toLowerCase().includes(q)) result[name] = filteredSegments[name];
    }
    buildSegmentList(result);
});


// -------------------------------------------------------
// INIT
// -------------------------------------------------------
populateSelect("seg-filter-region", getUniqueValues(segments, "state"), "All regions");
populateSelect("seg-filter-city",   getUniqueValues(segments, "city"),  "All cities");
buildSegmentList(segments);