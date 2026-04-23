# -*- coding: utf-8 -*-
import json
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ========================
# 🔧 配置
# ========================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:latest"

IGNORE_COLUMNS = ["姓名", "电话", "邮箱", "筛选结果"]

# embedding模型（本地）
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


# ========================
# 🧠 基础函数：调用LLM
# ========================
def call_ollama(prompt, temperature=0.2):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        return response.json().get("response", "")
    except Exception as e:
        print("❌ Ollama error:", e)
        return ""


# ========================
# 🧠 Step 1：解析JD
# ========================
def parse_jd(jd_text):
    prompt = f"""
你是招聘分析系统。

请从以下JD提取结构化信息，并返回JSON：

必须包含：
- must_have_skills
- preferred_skills
- experience_years
- education

JD:
{jd_text}
"""

    response = call_ollama(prompt)

    try:
        return json.loads(response)
    except:
        print("⚠️ JD解析失败，使用默认结构")
        return {
            "must_have_skills": [],
            "preferred_skills": [],
            "experience_years": 0,
            "education": ""
        }


# ========================
# 🧠 Step 2：Embedding
# ========================
def get_embedding(text):
    return embedding_model.encode(text)


def build_resume_text(row, feature_columns):
    parts = []
    for col in feature_columns:
        val = row[col]
        if pd.notna(val) and str(val).strip():
            parts.append(f"{col}: {val}")
    return "\n".join(parts)


# ========================
# 🧠 Step 3：Top-K召回
# ========================
def retrieve_top_k(df, jd_text, k=10):
    feature_columns = [c for c in df.columns if c not in IGNORE_COLUMNS]

    print("⚡ Computing embeddings...")

    jd_emb = get_embedding(jd_text)

    resume_texts = [
        build_resume_text(row, feature_columns)
        for _, row in df.iterrows()
    ]

    resume_embs = embedding_model.encode(resume_texts)

    sims = cosine_similarity([jd_emb], resume_embs)[0]

    top_k_idx = sims.argsort()[-k:][::-1]

    return top_k_idx, sims


# ========================
# 🧠 Step 4：LLM评分
# ========================
def build_scoring_prompt(resume_text, jd_structured):
    return f"""
你是招聘评分模型。

岗位需求：
{json.dumps(jd_structured, ensure_ascii=False)}

候选人简历：
{resume_text}

请评分（0-100）：

评分标准：
- 技能匹配（40）
- 经验（30）
- 学历（20）
- 加分项（10）

输出JSON：
{{
"score": 85,
"reason": "简要说明"
}}
"""


def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        # 尝试修复
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except:
            return {"score": 0, "reason": "parse_error"}


def score_resume(resume_text, jd_structured):
    prompt = build_scoring_prompt(resume_text, jd_structured)
    response = call_ollama(prompt)

    result = safe_json_parse(response)

    score = result.get("score", 0)
    reason = result.get("reason", "")

    return score, reason


# ========================
# 🧠 Step 5：Hybrid评分
# ========================
def hybrid_score(llm_score, similarity, alpha=0.7):
    """
    alpha: LLM权重
    """
    return alpha * llm_score + (1 - alpha) * similarity * 100


# ========================
# 🧠 主函数（给API用）
# ========================
def rank_resumes(df, jd_text, top_k=10):
    print("\n🔍 Parsing JD...")
    jd_structured = parse_jd(jd_text)

    print("\n⚡ Retrieving Top-K...")
    top_k_idx, sims = retrieve_top_k(df, jd_text, k=top_k)

    feature_columns = [c for c in df.columns if c not in IGNORE_COLUMNS]

    results = []

    print("\n🧠 Reranking with LLM...")

    for idx in top_k_idx:
        row = df.iloc[idx]

        resume_text = build_resume_text(row, feature_columns)

        llm_score, reason = score_resume(resume_text, jd_structured)

        final_score = hybrid_score(llm_score, sims[idx])

        results.append({
            "index": int(idx),
            "name": row.get("姓名", ""),
            "llm_score": llm_score,
            "similarity": float(sims[idx]),
            "final_score": round(final_score, 2),
            "reason": reason
        })

        print(f"✅ {idx} → {final_score:.2f}")

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    return results
