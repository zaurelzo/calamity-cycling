function generateTableHead(table, data, tableTitle) {
  let thead = table.createTHead();
  let title = thead.insertRow();
  let th = document.createElement("th");
    th.appendChild(document.createTextNode(tableTitle));
    title.appendChild(th);

  let row = thead.insertRow();
  for (let key of data) {
    let th = document.createElement("th");
    let text = document.createTextNode(key);
    th.appendChild(text);
    row.appendChild(th);
  }
}

function generateTable(table, data) {
    let row = table.insertRow();
    for (key in data) {
      let cell = row.insertCell();
      let text = document.createTextNode(data[key]);
      cell.appendChild(text);
    }
}

//top speed table
let tableTopSpeed = document.querySelector("#top_activity_speed");
generateTable(tableTopSpeed,  global_information["top_activity_speed"]); // generate the table first
generateTableHead(tableTopSpeed, Object.keys(global_information["top_activity_speed"]),"Highest average speed activity information"); // then the head

let tableTopDistance = document.querySelector("#top_distance");
generateTable(tableTopDistance,  global_information["top_distance"]); // generate the table first
generateTableHead(tableTopDistance, Object.keys(global_information["top_distance"]),"Longest activity information"); // then the head