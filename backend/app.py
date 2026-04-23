# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import fitz
import os

from ranking_engine import rank_resumes

app = Flask(__name__)
CORS(app)


# ========================
# PDF解析
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
# API
# ========================
@app.route("/rank", methods=["POST"])
def rank():
    try:
        jd = request.form.get("jd")
        files = request.files.getlist("files")

        if not jd:
            return jsonify({"error": "JD is required"}), 400

        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        resumes = []

        for f in files:
            text = extract_text_from_pdf(f)

            if not text:
                continue

            resumes.append({
                "姓名": f.filename,
                "内容": text
            })

        if not resumes:
            return jsonify({"error": "All PDFs failed"}), 400

        df = pd.DataFrame(resumes)

        results = rank_resumes(df, jd)

        return jsonify(results)

    except Exception as e:
        print("❌ backend error:", e)
        return jsonify({"error": "Server error"}), 500


# ========================
# 健康检查
# ========================
@app.route("/")
def home():
    return "✅ Backend running"


# ========================
# 启动
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
