# surveys/east_maine/config.py

SURVEY_SOURCE = "S"
PAGE_STRUCTURE = "east_maine"  # cleanest — two full pages, no cropping

NO_RESPONSE_DEFAULTS = {
    "Q1": 4, "Q2": 6, "Q3": 6, "Q4": 5,
    "Q5a": 1, "Q5b": 1, "Q5c": 1, "Q5d": 1, "Q5e": 1, "Q5f": 1,
    "Q6a": 1, "Q6b": 1, "Q6c": 1, "Q6d": 1, "Q6e": 1, "Q6f": 1,
    "Q7a": 1, "Q7b": 1, "Q7c": 1, "Q7d": 1, "Q7e": 1, "Q7f": 1,
    "Q8": 5, "Q9": 5,
    "Q10": 2, "Q11": None, "Q12": 2, "Q13": 6,
    "Q14": 4, "Q15": 7, "Q16": 3,
}

DATA_COLUMNS = [
    ("A", None),
    ("B", "#"),
    ("C", "L_U"),
    ("D", "Q1"),
    ("E", "Q2"),
    ("F", "Q3"),
    ("G", "Q4"),
    ("H", None),      # Q5 group header
    ("I", "Q5a"),
    ("J", "Q5b"),
    ("K", "Q5c"),
    ("L", "Q5d"),
    ("M", "Q5e"),
    ("N", "Q5f"),
    ("O", None),      # Q6 group header
    ("P", "Q6a"),
    ("Q", "Q6b"),
    ("R", "Q6c"),
    ("S", "Q6d"),
    ("T", "Q6e"),
    ("U", "Q6f"),
    ("V", None),      # Q7 group header
    ("W", "Q7a"),
    ("X", "Q7b"),
    ("Y", "Q7c"),
    ("Z", "Q7d"),
    ("AA", "Q7e"),
    ("AB", "Q7f"),
    ("AC", "Q8"),
    ("AD", "Q9"),
    ("AE", "Q10"),
    ("AF", "Q11"),
    ("AG", "Q12"),
    ("AH", "Q13"),
    ("AI", "Q14"),
    ("AJ", "Q15"),
    ("AK", "Q16"),
    ("AL", "source"),
]

SKIP_LOGIC = ("Q10", "Q11")
