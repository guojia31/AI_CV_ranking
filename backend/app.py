{\rtf1\ansi\ansicpg936\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from flask import Flask, request, jsonify\
import pandas as pd\
from ranking_engine import parse_jd, process_resume\
\
app = Flask(__name__)\
\
@app.route("/rank", methods=["POST"])\
def rank():\
    jd = request.form["jd"]\
    file = request.files["file"]\
\
    df = pd.read_csv(file)\
\
    jd_structured = parse_jd(jd)\
\
    results = []\
\
    for _, row in df.iterrows():\
        score, _ = process_resume(row, df.columns, jd_structured)\
\
        results.append(\{\
            "score": score,\
            "name": row.get("\uc0\u22995 \u21517 ", "")\
        \})\
\
    results = sorted(results, key=lambda x: x["score"], reverse=True)\
\
    return jsonify(results)\
\
if __name__ == "__main__":\
    app.run(debug=True)}