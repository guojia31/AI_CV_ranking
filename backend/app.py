from flask import Flask, request, jsonify
from services.parser import read_file
from services.llm import call_llm, safe_json
from services.schema import Candidate, JD
from services.ranker import rank

app = Flask(__name__)


def extract_jd(text):

    prompt = f"""
Extract JSON:

{{
  "skills": [],
  "min_years": 0,
  "domain": ""
}}

Text:
{text}
"""

    res = safe_json(call_llm(prompt))

    return JD(
        skills=res.get("skills", ["communication"]),
        min_years=res.get("min_years", 1),
        domain=res.get("domain", "general")
    )


def extract_candidate(text):

    prompt = f"""
Extract JSON:

{{
  "skills": [],
  "years": 0,
  "domain": ""
}}

Text:
{text[:1500]}
"""

    res = safe_json(call_llm(prompt))

    return res


@app.route("/rank", methods=["POST"])
def run_rank():

    jd_text = request.form["jd"]
    jd = extract_jd(jd_text)

    candidates = []

    for f in request.files.getlist("files"):

        text = read_file(f, f.filename)
        data = extract_candidate(text)

        candidates.append(
            Candidate(
                name=f.filename,
                skills=data.get("skills", []),
                years=data.get("years", 0),
                domain=data.get("domain", "general"),
                text=text
            )
        )

    results = rank(jd, candidates)

    return jsonify({
        "jd": jd.__dict__,
        "results": results
    })


if __name__ == "__main__":
    app.run(debug=True)
