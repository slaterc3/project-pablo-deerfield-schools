# surveys/weld_re1/config.py

SURVEY_SOURCE = "S"
PAGE_STRUCTURE = "weld_re1"  # inside first, inside split left/right

NO_RESPONSE_DEFAULTS = {
    "Q1": 4, "Q2": 6, "Q3": 6, "Q4": 5,
    "Q5a": 1,
    "Q6a": 1, "Q6b": 1, "Q6c": 1, "Q6d": 1, "Q6e": 1, "Q6f": 1,
    "Q7": 2, "Q8": None,
    "Q9a": 1, "Q9b": 1, "Q9c": 1, "Q9d": 1, "Q9e": 1, "Q9f": 1,
    "Q10a": 1, "Q10b": 1, "Q10c": 1, "Q10d": 1, "Q10e": 1, "Q10f": 1,
    "Q11": 5, "Q12": 5, "Q13": 5, "Q14": 5,
    "Q15": 4, "Q16": 7, "Q17": 4,
}

SKIP_LOGIC = ("Q7", "Q8")
