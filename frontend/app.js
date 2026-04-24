let files = [];

const input = document.getElementById("fileInput");
const list = document.getElementById("fileList");

const API = "http://localhost:5000/rank";


input.addEventListener("change", e => {
  files.push(...e.target.files);
  render();
});

function render() {
  list.innerHTML = "";

  files.forEach((f, i) => {
    const div = document.createElement("div");
    div.className = "file-item";

    div.innerHTML = `
      <span>${f.name}</span>
      <button onclick="remove(${i})">x</button>
    `;

    list.appendChild(div);
  });
}

function remove(i) {
  files.splice(i, 1);
  render();
}

async function submitData() {

  const jd = document.getElementById("jd").value;

  const form = new FormData();
  form.append("jd", jd);

  files.forEach(f => form.append("files", f));

  const res = await fetch(API, {
    method: "POST",
    body: form
  });

  const data = await res.json();

  document.getElementById("results").innerHTML =
    `<pre>${JSON.stringify(data, null, 2)}</pre>`;
}
