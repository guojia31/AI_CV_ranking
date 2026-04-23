from flask import Flask, request, jsonify
import pandas as pd
from ranking_engine import parse_jd, process_resume

app = Flask(__name__)

@app.route("/rank", methods=["POST"])
def rank():
    jd = request.form["jd"]
    file = request.files["file"]

    df = pd.read_csv(file)

    jd_structured = parse_jd(jd)

    results = []

    for _, row in df.iterrows():
        score, _ = process_resume(row, df.columns, jd_structured)

        results.append({
            "score": score,
            "name": row.get("姓名", "")
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
