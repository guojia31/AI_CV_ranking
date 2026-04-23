# -*- coding: utf-8 -*-
import json
import requests
import os
import time

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_NAME = "doubao-lite-4k"


# =========================
# LLM调用（稳定）
# =========================
def call_llm(prompt, max_retries=3):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_API_KEY}"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    for _ in range(max_retries):
        try:
            res = requests.post(DOUBAO_URL, headers=headers, json=data, timeout=30)

            if res.status_code != 200:
                print("LLM error:", res.text)
                time.sleep(1)
                continue

            return res.json().get("choices", [{}])[0].get("message", {}).get("content", "")

        except Exception as e:
            print("LLM exception:", e)
            time.sleep(1)

    return ""


# =========================
# JSON解析（强增强版🔥）
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
            print("⚠️ JSON parse failed, raw output:")
            print(text)
            return {}


# =========================
# JD解析（🔥强约束版本）
# =========================
def extract_jd(jd_text):

    prompt = f"""
你是严格JSON生成器。

⚠️ 你必须只输出JSON，不允许任何解释、文字、markdown。

输出格式必须严格如下：

{{
  "must_have_skills": ["SQL", "Python"],
  "preferred_skills": ["Teamwork"],
  "min_years": 3,
  "domain": "Data Science"
}}

规则：
- 只能输出JSON
- 不要解释
- 不要多余文字

JD:
{jd_text[:1000]}
"""

    res = call_llm(prompt)
    print("=== JD RAW OUTPUT ===")
    print(res)

    data = safe_json_parse(res)

    # 🔥 强制 fallback（避免空系统）
    return {
        "must_have_skills": data.get("must_have_skills", []) or [],
        "preferred_skills": data.get("preferred_skills", []) or [],
        "min_years": data.get("min_years", 0) or 0,
        "domain": data.get("domain", "") or ""
    }


# =========================
# Resume解析（稳定）
# =========================
def extract_resume(resume_text):

    prompt = f"""
提取简历信息，只输出JSON：

{{
  "skills": ["Python"],
  "years_experience": 3,
  "domain": "Data Science",
  "keywords": []
}}

简历：
{resume_text[:1200]}
"""

    res = call_llm(prompt)
    data = safe_json_parse(res)

    return {
        "skills": data.get("skills", []) or [],
        "years_experience": data.get("years_experience", 0) or 0,
        "domain": data.get("domain", "") or "",
        "keywords": data.get("keywords", []) or []
    }


# =========================
# scoring（稳定核心🔥）
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
# explanation（可选）
# =========================
def explain(jd, resume, score):

    prompt = f"""
一句话解释为什么得分 {score}。

JD: {jd}
Resume: {resume}
"""

    res = call_llm(prompt)
    return res.strip() if res else "Matched based on skills and experience"


# =========================
# 主函数（🔥最终稳定版）
# =========================
def rank_resumes(df, jd_text, top_k=10):

    jd = extract_jd(jd_text)

    results = []

    for _, row in df.iterrows():

        resume_text = row.get("内容", "")

        if not resume_text or len(resume_text) < 20:
            continue

        resume = extract_resume(resume_text)

        score = compute_score(jd, resume)

        reason = explain(jd, resume, score)

        results.append({
            "name": row.get("姓名", ""),
            "score": score,
            "reason": reason,
            "resume_structured": resume
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {
        "jd": jd,
        "results": results[:top_k]
    }
