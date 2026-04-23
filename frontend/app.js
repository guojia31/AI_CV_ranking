
// =========================
// 全局文件
// =========================
let selectedFiles = [];

const API_BASE = "https://independent-perception-production.up.railway.app";


// =========================
// 文件上传
// =========================
document.getElementById("fileInput").addEventListener("change", function (e) {
  const files = Array.from(e.target.files);

  files.forEach(file => selectedFiles.push(file));

  renderFileList();
});


// =========================
// 渲染文件列表
// =========================
function renderFileList() {
  const fileList = document.getElementById("fileList");
  fileList.innerHTML = "";

  selectedFiles.forEach((file, index) => {
    const div = document.createElement("div");
    div.className = "file-item";

    div.innerHTML = `
      <span>${file.name}</span>
      <button onclick="removeFile(${index})">❌</button>
    `;

    fileList.appendChild(div);
  });
}


// =========================
// 删除文件
// =========================
function removeFile(index) {
  selectedFiles.splice(index, 1);
  renderFileList();
}


// =========================
// 提交
// =========================
async function submitData() {

  const jd = document.getElementById("jd").value;
  const loading = document.getElementById("loading");
  const resultsDiv = document.getElementById("results");

  if (!jd || selectedFiles.length === 0) {
    alert("Please input JD and upload resumes");
    return;
  }

  loading.classList.remove("hidden");
  resultsDiv.innerHTML = "";

  const formData = new FormData();
  formData.append("jd", jd);

  selectedFiles.forEach(file => {
    formData.append("files", file);
  });

  try {

    const res = await fetch(`${API_BASE}/rank`, {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    loading.classList.add("hidden");

    console.log("API RESPONSE:", data);

    if (!data || !data.jd || !data.results) {
      resultsDiv.innerHTML = "❌ Invalid response";
      return;
    }

    renderJD(data.jd);
    renderResults(data.results);

  } catch (err) {
    loading.classList.add("hidden");
    console.error(err);
    alert("Error connecting to backend");
  }
}


// =========================
// JD展示
// =========================
function renderJD(jd) {

  const resultsDiv = document.getElementById("results");

  const box = document.createElement("div");
  box.className = "card";

  box.innerHTML = `
    <h3>📌 Parsed JD</h3>

    <p><b>Experience:</b> ${jd.min_years || 0} years</p>

    <p><b>Must Skills:</b> ${(jd.must_have_skills || []).join(", ") || "None"}</p>

    <p><b>Preferred Skills:</b> ${(jd.preferred_skills || []).join(", ") || "None"}</p>

    <p><b>Domain:</b> ${jd.domain || "N/A"}</p>
  `;

  resultsDiv.appendChild(box);
}


// =========================
// results展示
// =========================
function renderResults(results) {

  const resultsDiv = document.getElementById("results");

  results.forEach((item, i) => {

    const div = document.createElement("div");
    div.className = "card";

    div.innerHTML = `
      <h3>#${i + 1} ${item.name}</h3>
      <p><b>Score:</b> ${item.score}</p>
      <p><b>Reason:</b> ${item.reason}</p>
    `;

    resultsDiv.appendChild(div);
  });
}
