# -*- coding: utf-8 -*-
import json
import requests
import os
import time

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_NAME = "doubao-lite-4k"


# ========================
# 工具函数（新增）
# ========================
def clean_text(text):
    if not text:
        return ""
    return text.replace("\x00", "").strip()


# ========================
# LLM调用（稳定版）
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
                print("❌ API错误:", response.text)
                time.sleep(2)
                continue

            result = response.json()
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            if content:
                return content

        except Exception as e:
            print("❌ LLM异常:", e)

        time.sleep(2)

    return ""


# ========================
# JSON解析（增强版）
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
# JD解析
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

    if not data:
        return {
            "must_have_skills": [],
            "preferred_skills": [],
            "experience_years": "",
            "education": ""
        }

    return data


# ========================
# 简历评分（强化版🔥）
# ========================
def score_resume(resume_text, jd_structured):

    resume_text = clean_text(resume_text)

    # 🚨 核心防护：空简历直接跳过
    if len(resume_text) < 20:
        return {
            "score": 0,
            "reason": "Empty or invalid resume text"
        }

    prompt = f"""
岗位需求：
{json.dumps(jd_structured, ensure_ascii=False)}

简历：
{resume_text[:1200]}

请严格返回JSON：
{{"score": 0-100整数, "reason": "简要分析"}}
"""

    response = call_llm(prompt)

    data = safe_json_parse(response)

    # 🚨 fallback强化
    if not data:
        return {
            "score": 0,
            "reason": "LLM解析失败"
        }

    if "score" not in data:
        return {
            "score": 0,
            "reason": "Missing score field"
        }

    # 防止奇怪类型
    try:
        data["score"] = int(data["score"])
    except:
        data["score"] = 0

    return data


# ========================
# 主流程（稳定版🔥）
# ========================
def rank_resumes(df, jd_text, top_k=10):
    try:
        jd_structured = parse_jd(jd_text)

        results = []

        for _, row in df.iterrows():

            resume_text = clean_text(row.get("内容", ""))

            print("🔍 resume preview:", resume_text[:50])  # debug关键

            if len(resume_text) < 20:
                print("⚠️ skip empty resume")
                continue

            res = score_resume(resume_text, jd_structured)

            results.append({
                "name": row.get("姓名", ""),
                "score": res.get("score", 0),
                "similarity": 0,
                "reason": res.get("reason", "")
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    except Exception as e:
        print("❌ rank_resumes error:", e)
        return []
