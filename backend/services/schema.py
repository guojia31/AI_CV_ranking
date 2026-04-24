class Candidate:
    def __init__(self, name, skills, years, domain, text=""):
        self.name = name
        self.skills = skills
        self.years = years
        self.domain = domain
        self.text = text


class JD:
    def __init__(self, skills, min_years, domain):
        self.skills = skills
        self.min_years = min_years
        self.domain = domain
