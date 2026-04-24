def score(jd, c):

    score = 0

    jd_skills = set(jd.get("skills", []))
    c_skills = set(c.get("skills", []))

    score += len(jd_skills & c_skills) * 30

    if c.get("years", 0) >= jd.get("min_years", 1):
        score += 25

    if jd.get("domain") == c.get("domain"):
        score += 10

    score += len(c_skills)

    return min(score, 100)


def rank(jd, candidates):

    results = []

    for c in candidates:

        results.append({
            "name": c["name"],
            "score": score(jd, c),
            "skills": c.get("skills", []),
            "years": c.get("years", 0),
            "domain": c.get("domain", "")
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
