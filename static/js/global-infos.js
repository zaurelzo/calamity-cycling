function generateTableHead(table, data) {
  let thead = table.createTHead();
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



//build table info regarding top activity speed
let tableTopSpeed = document.querySelector("#top_activity_speed");
generateTable(tableTopSpeed,  global_information["top_activity_speed"]); // generate the table first
generateTableHead(tableTopSpeed, Object.keys(global_information["top_activity_speed"])); // then the head

//build table info regarding longest activity
let tableTopDistance = document.querySelector("#top_distance");
generateTable(tableTopDistance,  global_information["top_distance"]); // generate the table first
generateTableHead(tableTopDistance, Object.keys(global_information["top_distance"])); // then the head

//build table info regarding total distance
let tableTotalDistance = document.querySelector("#total_distance");
generateTable(tableTotalDistance,  global_information["total_distance"]); // generate the table first
generateTableHead(tableTotalDistance, Object.keys(global_information["total_distance"])); // then the head
