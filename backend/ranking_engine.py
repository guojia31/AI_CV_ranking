{\rtf1\ansi\ansicpg936\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # -*- coding: utf-8 -*-\
import json\
import requests\
import pandas as pd\
from sentence_transformers import SentenceTransformer\
from sklearn.metrics.pairwise import cosine_similarity\
\
# ========================\
# \uc0\u55357 \u56615  \u37197 \u32622 \
# ========================\
OLLAMA_URL = "http://localhost:11434/api/generate"\
MODEL_NAME = "gemma4:latest"\
\
IGNORE_COLUMNS = ["\uc0\u22995 \u21517 ", "\u30005 \u35805 ", "\u37038 \u31665 ", "\u31579 \u36873 \u32467 \u26524 "]\
\
# embedding\uc0\u27169 \u22411 \u65288 \u26412 \u22320 \u65289 \
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')\
\
\
# ========================\
# \uc0\u55358 \u56800  \u22522 \u30784 \u20989 \u25968 \u65306 \u35843 \u29992 LLM\
# ========================\
def call_ollama(prompt, temperature=0.2):\
    payload = \{\
        "model": MODEL_NAME,\
        "prompt": prompt,\
        "temperature": temperature,\
        "stream": False\
    \}\
\
    try:\
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)\
        return response.json().get("response", "")\
    except Exception as e:\
        print("\uc0\u10060  Ollama error:", e)\
        return ""\
\
\
# ========================\
# \uc0\u55358 \u56800  Step 1\u65306 \u35299 \u26512 JD\
# ========================\
def parse_jd(jd_text):\
    prompt = f"""\
\uc0\u20320 \u26159 \u25307 \u32856 \u20998 \u26512 \u31995 \u32479 \u12290 \
\
\uc0\u35831 \u20174 \u20197 \u19979 JD\u25552 \u21462 \u32467 \u26500 \u21270 \u20449 \u24687 \u65292 \u24182 \u36820 \u22238 JSON\u65306 \
\
\uc0\u24517 \u39035 \u21253 \u21547 \u65306 \
- must_have_skills\
- preferred_skills\
- experience_years\
- education\
\
JD:\
\{jd_text\}\
"""\
\
    response = call_ollama(prompt)\
\
    try:\
        return json.loads(response)\
    except:\
        print("\uc0\u9888 \u65039  JD\u35299 \u26512 \u22833 \u36133 \u65292 \u20351 \u29992 \u40664 \u35748 \u32467 \u26500 ")\
        return \{\
            "must_have_skills": [],\
            "preferred_skills": [],\
            "experience_years": 0,\
            "education": ""\
        \}\
\
\
# ========================\
# \uc0\u55358 \u56800  Step 2\u65306 Embedding\
# ========================\
def get_embedding(text):\
    return embedding_model.encode(text)\
\
\
def build_resume_text(row, feature_columns):\
    parts = []\
    for col in feature_columns:\
        val = row[col]\
        if pd.notna(val) and str(val).strip():\
            parts.append(f"\{col\}: \{val\}")\
    return "\\n".join(parts)\
\
\
# ========================\
# \uc0\u55358 \u56800  Step 3\u65306 Top-K\u21484 \u22238 \
# ========================\
def retrieve_top_k(df, jd_text, k=10):\
    feature_columns = [c for c in df.columns if c not in IGNORE_COLUMNS]\
\
    print("\uc0\u9889  Computing embeddings...")\
\
    jd_emb = get_embedding(jd_text)\
\
    resume_texts = [\
        build_resume_text(row, feature_columns)\
        for _, row in df.iterrows()\
    ]\
\
    resume_embs = embedding_model.encode(resume_texts)\
\
    sims = cosine_similarity([jd_emb], resume_embs)[0]\
\
    top_k_idx = sims.argsort()[-k:][::-1]\
\
    return top_k_idx, sims\
\
\
# ========================\
# \uc0\u55358 \u56800  Step 4\u65306 LLM\u35780 \u20998 \
# ========================\
def build_scoring_prompt(resume_text, jd_structured):\
    return f"""\
\uc0\u20320 \u26159 \u25307 \u32856 \u35780 \u20998 \u27169 \u22411 \u12290 \
\
\uc0\u23703 \u20301 \u38656 \u27714 \u65306 \
\{json.dumps(jd_structured, ensure_ascii=False)\}\
\
\uc0\u20505 \u36873 \u20154 \u31616 \u21382 \u65306 \
\{resume_text\}\
\
\uc0\u35831 \u35780 \u20998 \u65288 0-100\u65289 \u65306 \
\
\uc0\u35780 \u20998 \u26631 \u20934 \u65306 \
- \uc0\u25216 \u33021 \u21305 \u37197 \u65288 40\u65289 \
- \uc0\u32463 \u39564 \u65288 30\u65289 \
- \uc0\u23398 \u21382 \u65288 20\u65289 \
- \uc0\u21152 \u20998 \u39033 \u65288 10\u65289 \
\
\uc0\u36755 \u20986 JSON\u65306 \
\{\{\
"score": 85,\
"reason": "\uc0\u31616 \u35201 \u35828 \u26126 "\
\}\}\
"""\
\
\
def safe_json_parse(text):\
    try:\
        return json.loads(text)\
    except:\
        # \uc0\u23581 \u35797 \u20462 \u22797 \
        try:\
            start = text.find("\{")\
            end = text.rfind("\}") + 1\
            return json.loads(text[start:end])\
        except:\
            return \{"score": 0, "reason": "parse_error"\}\
\
\
def score_resume(resume_text, jd_structured):\
    prompt = build_scoring_prompt(resume_text, jd_structured)\
    response = call_ollama(prompt)\
\
    result = safe_json_parse(response)\
\
    score = result.get("score", 0)\
    reason = result.get("reason", "")\
\
    return score, reason\
\
\
# ========================\
# \uc0\u55358 \u56800  Step 5\u65306 Hybrid\u35780 \u20998 \
# ========================\
def hybrid_score(llm_score, similarity, alpha=0.7):\
    """\
    alpha: LLM\uc0\u26435 \u37325 \
    """\
    return alpha * llm_score + (1 - alpha) * similarity * 100\
\
\
# ========================\
# \uc0\u55358 \u56800  \u20027 \u20989 \u25968 \u65288 \u32473 API\u29992 \u65289 \
# ========================\
def rank_resumes(df, jd_text, top_k=10):\
    print("\\n\uc0\u55357 \u56589  Parsing JD...")\
    jd_structured = parse_jd(jd_text)\
\
    print("\\n\uc0\u9889  Retrieving Top-K...")\
    top_k_idx, sims = retrieve_top_k(df, jd_text, k=top_k)\
\
    feature_columns = [c for c in df.columns if c not in IGNORE_COLUMNS]\
\
    results = []\
\
    print("\\n\uc0\u55358 \u56800  Reranking with LLM...")\
\
    for idx in top_k_idx:\
        row = df.iloc[idx]\
\
        resume_text = build_resume_text(row, feature_columns)\
\
        llm_score, reason = score_resume(resume_text, jd_structured)\
\
        final_score = hybrid_score(llm_score, sims[idx])\
\
        results.append(\{\
            "index": int(idx),\
            "name": row.get("\uc0\u22995 \u21517 ", ""),\
            "llm_score": llm_score,\
            "similarity": float(sims[idx]),\
            "final_score": round(final_score, 2),\
            "reason": reason\
        \})\
\
        print(f"\uc0\u9989  \{idx\} \u8594  \{final_score:.2f\}")\
\
    results = sorted(results, key=lambda x: x["final_score"], reverse=True)\
\
    return results}