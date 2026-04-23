// 全局存储文件
let selectedFiles = [];

// 监听文件上传
document.getElementById("fileInput").addEventListener("change", function (e) {
  const files = Array.from(e.target.files);

  files.forEach(file => {
    selectedFiles.push(file);
  });

  renderFileList();
});

// 渲染文件列表
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

// 删除文件
function removeFile(index) {
  selectedFiles.splice(index, 1);
  renderFileList();
}

// 提交
async function submitData() {
  const jd = document.getElementById("jd").value;
  const loading = document.getElementById("loading");
  const resultsDiv = document.getElementById("results");

  if (!jd || selectedFiles.length === 0) {
    alert("Please input JD and upload PDFs");
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
    const res = await fetch("http://localhost:5000/rank", {
      method: "POST",
      body: formData
    });

    const data = await res.json();

    loading.classList.add("hidden");

    displayResults(data);

  } catch (err) {
    loading.classList.add("hidden");
    alert("Error connecting to backend");
  }
}

// 显示结果
function displayResults(data) {
  const resultsDiv = document.getElementById("results");

  data.forEach((item, i) => {
    const div = document.createElement("div");
    div.className = "card";

    div.innerHTML = `
      <h3>#${i + 1} ${item.name}</h3>
      <p>Score: ${item.score}</p>
      <p>Similarity: ${item.similarity}</p>
      <p>${item.reason}</p>
    `;

    resultsDiv.appendChild(div);
  });
}
