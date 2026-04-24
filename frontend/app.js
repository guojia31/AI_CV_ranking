let files = [];

const fileInput = document.getElementById("fileInput");
const fileList = document.getElementById("fileList");

const API = "http://localhost:5000/rank";

fileInput.addEventListener("change", e => {
  files.push(...e.target.files);
  renderFiles();
});

function renderFiles() {
  fileList.innerHTML = "";

  files.forEach((f, i) => {
    const div = document.createElement("div");
    div.className = "file-item";
    div.innerHTML = `
      <span>📄 ${f.name}</span>
      <button onclick="removeFile(${i})">❌</button>
    `;
    fileList.appendChild(div);
  });
}

function removeFile(i) {
  files.splice(i, 1);
  renderFiles();
}

async function submitData() {

  const jd = document.getElementById("jd").value;
  const loading = document.getElementById("loading");

  loading.classList.remove("hidden");

  const form = new FormData();
  form.append("jd", jd);

  files.forEach(f => form.append("files", f));

  const res = await fetch(API, {
    method: "POST",
    body: form
  });

  const data = await res.json();

  loading.classList.add("hidden");

  renderResults(data.results);
}


// =========================
// DASHBOARD RENDER
// =========================
function renderResults(results) {

  const container = document.getElementById("results");
  container.innerHTML = "";

  results.forEach((r, i) => {

    const scoreWidth = r.score || 0;

    const card = document.createElement("div");
    card.className = "result-card";

    card.innerHTML = `
      <div class="result-header">
        <h3>#${i + 1} ${r.name}</h3>
        <div class="score">${r.score}</div>
      </div>

      <div class="bar">
        <div class="bar-fill" style="width:${scoreWidth}%"></div>
      </div>

      <p>${r.reason || ""}</p>

      <div>
        ${(r.skills || []).map(s => `<span class="tag">${s}</span>`).join("")}
      </div>
    `;

    container.appendChild(card);
  });
}
