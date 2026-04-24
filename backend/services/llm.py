import os
import requests
import json

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_NAME = "doubao-lite-4k"


def call_llm(prompt):

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DOUBAO_API_KEY}"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        res = requests.post(DOUBAO_URL, headers=headers, json=data, timeout=30)
        return res.json()["choices"][0]["message"]["content"]
    except:
        return ""


def safe_json(text):
    try:
        return json.loads(text)
    except:
        import re
        try:
            m = re.search(r"\{.*\}", text, re.DOTALL)
            return json.loads(m.group())
        except:
            return {}
