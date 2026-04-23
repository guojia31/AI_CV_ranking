# -*- coding: utf-8 -*-
import json
import requests
import os
import time

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_NAME = "doubao-lite-4k"


# =========================
# LLM 调用（稳定）
# =========================
def call_llm(prompt, max_retries=3):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_API_KEY}"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    for _ in range(max_retries):
        try:
            res = requests.post(DOUBAO_URL, headers=headers, json=data, timeout=30)

            if res.status_code != 200:
                print("LLM error:", res.text)
                time.sleep(1)
                continue

            content = res.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            return content or ""

        except Exception as e:
            print("LLM exception:", e)
            time.sleep(1)

    return ""


# =========================
# JSON 安全解析
# =========================
def safe_json_parse(text):
    if not text:
        return {}

    try:
        return json.loads(text)
    except:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except:
            return {}


# =========================
# 文本清洗
# =========================
def clean_text(text):
    if not text:
        return ""
    return text.replace("\x00", "").strip()


# =========================
# JD 解析（LLM一次）
# =========================
def extract_jd(jd_text):
    prompt = f"""
提取JD信息，返回JSON（严格JSON）：

{{
  "must_have_skills": [],
  "preferred_skills": [],
  "min_years": 0,
  "domain": ""
}}

JD:
{jd_text[:1000]}
"""

    res = call_llm(prompt)
    data = safe_json_parse(res)

    return data or {
        "must_have_skills": [],
        "preferred_skills": [],
        "min_years": 0,
        "domain": ""
    }


# =========================
# Resume 解析（LLM轻任务）
# =========================
def extract_resume(resume_text):
    prompt = f"""
从简历提取信息，返回JSON：

{{
  "skills": [],
  "years_experience": 0,
  "domain": "",
  "keywords": []
}}

简历：
{resume_text[:1200]}
"""

    res = call_llm(prompt)
    data = safe_json_parse(res)

    return data or {
        "skills": [],
        "years_experience": 0,
        "domain": "",
        "keywords": []
    }


# =========================
# scoring（稳定核心）
# =========================
def compute_score(jd, resume):

    score = 0

    must = set(jd.get("must_have_skills", []))
    pref = set(jd.get("preferred_skills", []))
    skills = set(resume.get("skills", []))

    score += len(must & skills) * 25
    score += len(pref & skills) * 10

    if resume.get("years_experience", 0) >= jd.get("min_years", 0):
        score += 20

    if jd.get("domain") and jd.get("domain") == resume.get("domain"):
        score += 10

    return min(score, 100)


# =========================
# explanation（可选AI）
# =========================
def explain(jd, resume, score):

    prompt = f"""
一句话解释为什么得分 {score}

JD: {jd}
Resume: {resume}
"""

    res = call_llm(prompt)
    return res.strip() if res else "Score based on skill matching"


# =========================
# 主函数（🔥最终版）
# =========================
def rank_resumes(df, jd_text, top_k=10):

    jd = extract_jd(jd_text)

    results = []

    for _, row in df.iterrows():

        resume_text = clean_text(row.get("内容", ""))

        if len(resume_text) < 20:
            continue

        resume = extract_resume(resume_text)

        score = compute_score(jd, resume)

        reason = explain(jd, resume, score)

        results.append({
            "name": row.get("姓名", ""),
            "score": score,
            "similarity": 0,
            "reason": reason,
            "resume_structured": resume   # ⭐ 可选：给前端调试用
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {
        "jd": jd,              # ⭐ 前端展示用
        "results": results[:top_k]
    }
