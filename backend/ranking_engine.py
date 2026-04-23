# -*- coding: utf-8 -*-
import json
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ========================
# 配置
# ========================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:latest"

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

import requests
import os

DOUBAO_API_KEY = os.getenv("ark-10293dd2-2975-4230-9123-77c8d293bfd1-207e0")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_NAME = "doubao-lite-4k"  

def call_llm(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_API_KEY}"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(DOUBAO_URL, headers=headers, json=data, timeout=60)
        result = response.json()

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ Doubao API error:", e)
        return ""
# ========================
# JD解析
# ========================
def parse_jd(jd_text):
    prompt = f"""
提取JD信息，返回JSON：
- must_have_skills
- preferred_skills
- experience_years
- education

JD:
{jd_text}
"""

    response = call_llm(prompt)

    try:
        return json.loads(response)
    except:
        return {}


# ========================
# 文本构建（支持PDF）
# ========================
def build_resume_text(row):
    if "内容" in row:
        return row["内容"]
    return ""


# ========================
# Embedding
# ========================
def get_embedding(text):
    return embedding_model.encode(text)


# ========================
# Top-K召回
# ========================
def retrieve_top_k(df, jd_text, k=10):
    jd_emb = get_embedding(jd_text)

    resume_texts = [build_resume_text(row) for _, row in df.iterrows()]
    resume_embs = embedding_model.encode(resume_texts)

    sims = cosine_similarity([jd_emb], resume_embs)[0]

    top_k_idx = sims.argsort()[-k:][::-1]

    return top_k_idx, sims


# ========================
# LLM评分
# ========================
def score_resume(resume_text, jd_structured):
    prompt = f"""
岗位需求：
{json.dumps(jd_structured, ensure_ascii=False)}

简历：
{resume_text}

评分0-100，返回JSON：
{{"score": 80, "reason": "说明"}}
"""

    response = call_llm(prompt)

    try:
        return json.loads(response)
    except:
        return {"score": 0, "reason": "parse_error"}


# ========================
# 主流程
# ========================
def rank_resumes(df, jd_text, top_k=10):
    jd_structured = parse_jd(jd_text)

    top_k_idx, sims = retrieve_top_k(df, jd_text, top_k)

    results = []

    for idx in top_k_idx:
        row = df.iloc[idx]

        resume_text = build_resume_text(row)

        res = score_resume(resume_text, jd_structured)

        llm_score = res.get("score", 0)
        sim_score = sims[idx] * 100

        final_score = 0.7 * llm_score + 0.3 * sim_score

        results.append({
            "name": row.get("姓名", ""),
            "score": round(final_score, 2),
            "similarity": round(sim_score, 2),
            "reason": res.get("reason", "")
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results
