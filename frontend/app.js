async function submitData() {
  const jd = document.getElementById("jd").value;
  const files = document.getElementById("files").files;
  const loading = document.getElementById("loading");
  const resultsDiv = document.getElementById("results");

  if (!jd || files.length === 0) {
    alert("Please input JD and upload PDFs");
    return;
  }

  loading.classList.remove("hidden");
  resultsDiv.innerHTML = "";

  const formData = new FormData();
  formData.append("jd", jd);

  for (let i = 0; i < files.length; i++) {
    formData.append("files", files[i]);
  }

  const res = await fetch("http://localhost:5000/rank", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  loading.classList.add("hidden");

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
