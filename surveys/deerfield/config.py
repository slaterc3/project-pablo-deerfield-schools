# surveys/deerfield/config.py

SURVEY_SOURCE = "S"
PAGE_STRUCTURE = "deerfield"  # outside/inside with cross-page Q13-Q17

NO_RESPONSE_DEFAULTS = {
    "Q1": 4, "Q2": 6, "Q3": 6, "Q4": 5,
    "Q5": 2, "Q6": None, "Q7": 2, "Q8": 5,
    "Q9a": 1, "Q9b": 1, "Q9c": 1, "Q9d": 1, "Q9e": 1, "Q9f": 1,
    "Q10a": 1, "Q10b": 1, "Q10c": 1, "Q10d": 1, "Q10e": 1, "Q10f": 1, "Q10g": 1,
    "Q11a": 1, "Q11b": 1, "Q11c": 1, "Q11d": 1,
    "Q12": 5, "Q13": 5, "Q14": 5, "Q15": 5,
    "Q16": 4, "Q17": 6,
}

# (children_question, school_question) for skip logic
SKIP_LOGIC = ("Q5", "Q6")
