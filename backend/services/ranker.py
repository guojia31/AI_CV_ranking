def score(jd, c):

    score = 0

    must = set(jd.skills)
    cand = set(c.skills)

    score += len(must & cand) * 30

    if c.years >= jd.min_years:
        score += 25

    if jd.domain == c.domain:
        score += 10

    score += len(cand)

    return min(score, 100)


def rank(jd, candidates):

    results = []

    for c in candidates:
        results.append({
            "name": c.name,
            "score": score(jd, c),
            "skills": c.skills,
            "years": c.years,
            "domain": c.domain
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)
