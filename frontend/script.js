let datasetId = null;

async function uploadCSV() {
  const file = document.getElementById("csvFile").files[0];
  if (!file) {
    document.getElementById("results").innerText = "Please choose a CSV file first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/api/upload", { method: "POST", body: formData });
  const data = await res.json();

  if (data.error) {
    document.getElementById("results").innerText = data.error;
    return;
  }

  datasetId = data.dataset_id;

  // Populate column selector
  const selector = document.getElementById("columnSelector");
  selector.innerHTML = "";
  data.schema.forEach(col => {
    const opt = document.createElement("option");
    opt.value = col.name;
    opt.textContent = `${col.name} (${col.type})`;
    selector.appendChild(opt);
  });

  // Auto-select first column
  if (data.schema.length > 0) {
    selector.value = data.schema[0].name;
  }

  loadTable();
}

async function loadTable() {
  if (!datasetId) {
    document.getElementById("dataTable").innerHTML = "<tr><td>No dataset loaded</td></tr>";
    return;
  }

  const res = await fetch(`/api/dataset/${datasetId}/table`);
  const rows = await res.json();
  console.log("Rows received:", rows);

  const table = document.getElementById("dataTable");
  table.innerHTML = "";

  if (rows.length > 0) {
    const header = Object.keys(rows[0]);
    let headerRow = "<tr>" + header.map(h => `<th>${h}</th>`).join("") + "</tr>";
    table.innerHTML += headerRow;

    rows.forEach(r => {
      let row = "<tr>" + header.map(h => `<td>${r[h]}</td>`).join("") + "</tr>";
      table.innerHTML += row;
    });
  } else {
    table.innerHTML = "<tr><td>No data found</td></tr>";
  }
}

async function getStats() {
  if (!datasetId) {
    document.getElementById("results").innerText = "No dataset uploaded yet.";
    return;
  }
  const col = document.getElementById("columnSelector").value;
  if (!col) {
    document.getElementById("results").innerText = "No column selected.";
    return;
  }

  const res = await fetch(`/api/dataset/${datasetId}/column/${col}/stats`);
  const stats = await res.json();
  document.getElementById("results").innerText = JSON.stringify(stats, null, 2);
}

async function getHistogram() {
  if (!datasetId) {
    document.getElementById("results").innerText = "No dataset uploaded yet.";
    return;
  }
  const col = document.getElementById("columnSelector").value;
  if (!col) {
    document.getElementById("results").innerText = "No column selected.";
    return;
  }

  const res = await fetch(`/api/dataset/${datasetId}/column/${col}/hist`);
  const hist = await res.json();

  if (hist.error) {
    document.getElementById("results").innerText = hist.error;
    return;
  }

  const ctx = document.getElementById("histCanvas").getContext("2d");
  ctx.clearRect(0, 0, 400, 200);
  ctx.fillStyle = "blue";
  const maxCount = Math.max(...hist.counts);
  hist.counts.forEach((c, i) => {
    ctx.fillRect(i * 10, 200 - (c / maxCount * 200), 8, (c / maxCount * 200));
  });
}
