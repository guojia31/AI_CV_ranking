# -*- coding: utf-8 -*-
import json
import requests
import os

# ========================
# Doubao API 配置
# ========================
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_NAME = "doubao-lite-4k"


# ========================
# LLM调用
# ========================
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

        return result.get("choices", [{}])[0].get("message", {}).get("content", "")

    except Exception as e:
        print("❌ Doubao API error:", e)
        return ""


# ========================
# JSON安全解析
# ========================
def safe_json_parse(text):
    try:
        return json.loads(text)
    except:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except:
            return {}


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
    return safe_json_parse(response)


# ========================
# 简历评分
# ========================
def score_resume(resume_text, jd_structured):
    prompt = f"""
岗位需求：
{json.dumps(jd_structured, ensure_ascii=False)}

简历：
{resume_text[:3000]}

请评分0-100，并返回JSON：
{{"score": 80, "reason": "说明"}}
"""

    response = call_llm(prompt)
    return safe_json_parse(response)


# ========================
# 主排序逻辑（无embedding）
# ========================
def rank_resumes(df, jd_text, top_k=10):
    jd_structured = parse_jd(jd_text)

    results = []

    for _, row in df.iterrows():
        resume_text = row.get("内容", "")

        if not resume_text.strip():
            continue

        res = score_resume(resume_text, jd_structured)

        score = res.get("score", 0)

        results.append({
            "name": row.get("姓名", ""),
            "score": score,
            "similarity": 0,
            "reason": res.get("reason", "")
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return results[:top_k]
