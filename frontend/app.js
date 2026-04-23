async function uploadAndRank() {
  const jd = document.getElementById("jdInput").value;
  const fileInput = document.getElementById("fileInput");
  const loading = document.getElementById("loading");
  const resultsDiv = document.getElementById("results");

  if (!jd) {
    alert("Please input JD");
    return;
  }

  if (!fileInput.files.length) {
    alert("Please upload a CSV file");
    return;
  }

  const file = fileInput.files[0];

  loading.classList.remove("hidden");
  resultsDiv.innerHTML = "";

  const formData = new FormData();
  formData.append("jd", jd);
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:5000/rank", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    loading.classList.add("hidden");

    displayResults(data);

  } catch (error) {
    loading.classList.add("hidden");
    alert("Error connecting to backend");
  }
}

function displayResults(data) {
  const resultsDiv = document.getElementById("results");

  data.forEach((item, index) => {
    const div = document.createElement("div");
    div.className = "result-item";

    div.innerHTML = `
      <strong>#${index + 1}</strong><br>
      Score: ${item.score}<br>
      ${item.name ? "Name: " + item.name : ""}
    `;

    resultsDiv.appendChild(div);
  });
}