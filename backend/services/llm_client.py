import requests
import json
from config import DOUBAO_API_KEY, DOUBAO_URL, MODEL_NAME


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
        res.raise_for_status()

        return res.json()["choices"][0]["message"]["content"]

    except Exception as e:
        print("LLM error:", e)
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
