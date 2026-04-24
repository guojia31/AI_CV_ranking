from services.llm_client import call_llm, safe_json


def extract_jd(text):

    prompt = f"""
Extract structured JSON:

{{
  "skills": [],
  "min_years": 1,
  "domain": ""
}}

JD:
{text}
"""

    return safe_json(call_llm(prompt))


def extract_resume(text):

    prompt = f"""
Extract structured JSON:

{{
  "skills": [],
  "years": 0,
  "domain": ""
}}

Resume:
{text[:1500]}
"""

    return safe_json(call_llm(prompt))
