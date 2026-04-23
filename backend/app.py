# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import pandas as pd
import fitz  # PyMuPDF

from ranking_engine import rank_resumes

app = Flask(__name__)

# ========================
# 📄 PDF解析
# ========================
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text()

    return text


# ========================
# 🚀 API：上传JD + 多PDF
# ========================
@app.route("/rank", methods=["POST"])
def rank():
    jd = request.form.get("jd")

    if not jd:
        return jsonify({"error": "JD is required"}), 400

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    resumes = []

    for f in files:
        try:
            text = extract_text_from_pdf(f)

            resumes.append({
                "姓名": f.filename,
                "内容": text
            })
        except Exception as e:
            print(f"❌ PDF解析失败: {f.filename}", e)

    df = pd.DataFrame(resumes)

    print("📊 开始AI筛选...")

    results = rank_resumes(df, jd, top_k=min(10, len(df)))

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
