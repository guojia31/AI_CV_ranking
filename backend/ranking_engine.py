# -*- coding: utf-8 -*-
import json
import requests
import os
import time

# ========================
# 配置
# ========================
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_NAME = "doubao-lite-4k"


# ========================
# ✅ 稳定 LLM 调用（带重试）
# ========================
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

    for i in range(max_retries):
        try:
            response = requests.post(
                DOUBAO_URL,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code != 200:
                print("❌ API状态异常:", response.text)
                time.sleep(2)
                continue

            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            if content:
                return content

        except Exception as e:
            print("❌ LLM调用失败:", e)

        time.sleep(2)

    return ""  # 最终失败


# ========================
# ✅ JSON安全解析（超稳）
# ========================
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


# ========================
# JD解析（带fallback）
# ========================
def parse_jd(jd_text):
    prompt = f"""
提取JD关键信息，返回JSON：
- must_have_skills
- preferred_skills
- experience_years
- education

JD:
{jd_text[:1000]}
"""

    response = call_llm(prompt)

    data = safe_json_parse(response)

    # fallback（避免空）
    if not data:
        return {
            "must_have_skills": [],
            "preferred_skills": [],
            "experience_years": "",
            "education": ""
        }

    return data


# ========================
# 简历评分（稳定版）
# ========================
def score_resume(resume_text, jd_structured):
    prompt = f"""
岗位需求：
{json.dumps(jd_structured, ensure_ascii=False)}

简历：
{resume_text[:1200]}

请评分0-100，并返回JSON：
{{"score": 80, "reason": "简要说明"}}
"""

    response = call_llm(prompt)

    data = safe_json_parse(response)

    # fallback（关键！）
    if not data or "score" not in data:
        return {
            "score": 0,
            "reason": "LLM解析失败"
        }

    return data


# ========================
# 主流程（带全局保护）
# ========================
def rank_resumes(df, jd_text, top_k=10):
    try:
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

    except Exception as e:
        print("❌ rank_resumes错误:", e)
        return []
