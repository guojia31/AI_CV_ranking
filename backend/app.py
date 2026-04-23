# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import fitz  # PyMuPDF
import os

from ranking_engine import rank_resumes

# ========================
# 🚀 初始化
# ========================
app = Flask(__name__)
CORS(app)  # 允许跨域（前端访问必须）


# ========================
# 📄 PDF解析
# ========================
def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""

        for page in doc:
            text += page.get_text()

        return text.strip()

    except Exception as e:
        print(f"❌ PDF解析失败: {file.filename}", e)
        return ""


# ========================
# 🧠 API：简历筛选
# ========================
@app.route("/rank", methods=["POST"])
def rank():
    try:
        # 1️⃣ 获取JD
        jd = request.form.get("jd")

        if not jd:
            return jsonify({"error": "JD is required"}), 400

        # 2️⃣ 获取PDF文件（多文件）
        files = request.files.getlist("files")

        if not files or len(files) == 0:
            return jsonify({"error": "No PDF files uploaded"}), 400

        resumes = []

        # 3️⃣ 解析PDF
        for f in files:
            print(f"📄 正在解析: {f.filename}")

            text = extract_text_from_pdf(f)

            # ⚠️ 跳过空简历（很重要）
            if not text:
                print(f"⚠️ 空内容: {f.filename}")
                continue

            resumes.append({
                "姓名": f.filename,
                "内容": text
            })

        # 4️⃣ 全部失败
        if len(resumes) == 0:
            return jsonify({"error": "All PDFs failed to parse"}), 400

        # 5️⃣ 转 DataFrame
        df = pd.DataFrame(resumes)

        print("🧠 开始AI筛选...")

        # 6️⃣ AI排序
        results = rank_resumes(df, jd, top_k=min(10, len(df)))

        return jsonify(results)

    except Exception as e:
        print("❌ 后端错误:", e)
        return jsonify({"error": "Server error"}), 500


# ========================
# 🏠 健康检查（用于测试）
# ========================
@app.route("/")
def home():
    return "✅ AI Resume Screening Backend Running"


# ========================
# ▶️ 启动（适配 Railway）
# ========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Backend running on port {port}")
    app.run(host="0.0.0.0", port=port)
