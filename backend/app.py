from flask import Flask, request, jsonify

from services.parser import read_file
from services.extractor import extract_jd, extract_resume
from services.ranker import rank

app = Flask(__name__)


@app.route("/rank", methods=["POST"])
def run_rank():

    jd_text = request.form["jd"]

    jd = extract_jd(jd_text)

    candidates = []

    for f in request.files.getlist("files"):

        text = read_file(f, f.filename)

        parsed = extract_resume(text)

        candidates.append({
            "name": f.filename,
            "skills": parsed.get("skills", []),
            "years": parsed.get("years", 0),
            "domain": parsed.get("domain", "general")
        })

    results = rank(jd, candidates)

    return jsonify({
        "jd": jd,
        "results": results
    })


if __name__ == "__main__":
    app.run(debug=True)
