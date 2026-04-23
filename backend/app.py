# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import pandas as pd
import fitz  # PyMuPDF
from ranking_engine import rank_resumes
from flask_cors import CORS
CORS(app)
app = Flask(__name__)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
# ========================
# 📄 PDF解析函数
# ========================
def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""

        for page in doc:
            text += page.get_text()

        return text.strip()
    except Exception as e:
        print("❌ PDF解析失败:", e)
        return ""


# ========================
# 🚀 API接口
# ========================
@app.route("/rank", methods=["POST"])
def rank():
    try:
        jd = request.form.get("jd")

        if not jd:
            return jsonify({"error": "JD is required"}), 400

        files = request.files.getlist("files")

        if not files:
            return jsonify({"error": "No PDF files uploaded"}), 400

        resumes = []

        for f in files:
            print(f"📄 正在解析: {f.filename}")

            text = extract_text_from_pdf(f)

            if not text:
                print(f"⚠️ 空文本: {f.filename}")
                continue

            resumes.append({
                "姓名": f.filename,
                "内容": text
            })

        if len(resumes) == 0:
            return jsonify({"error": "All PDFs failed to parse"}), 400

        df = pd.DataFrame(resumes)

        print("🧠 开始AI筛选...")

        results = rank_resumes(df, jd, top_k=min(10, len(df)))

        return jsonify(results)

    except Exception as e:
        print("❌ 后端错误:", e)
        return jsonify({"error": "Server error"}), 500


# ========================
# 启动
# ========================
if __name__ == "__main__":
    print("🚀 Backend running at http://localhost:5000")
    app.run(debug=True, port=5000)
