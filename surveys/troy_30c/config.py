# surveys/troy_30c/config.py
# Troy Community Consolidated School District 30-C
# Illinois — clean 2-page format, identical structure to East Maine
# Label format: L-X or UL-X at top center of outside page
# IMPORTANT: Only 2 header rows — data starts at row 3

SURVEY_SOURCE = "S"
PAGE_STRUCTURE = "east_maine"  # same: two full pages, no cropping
HEADER_ROWS = 2  # different from East Maine's 3

NO_RESPONSE_DEFAULTS = {
    "Q1": 4,    # Nothing at all
    "Q2": 6,    # Don't know
    "Q3": 4,    # Don't know
    "Q4": 5,    # Don't know
    "Q5a": 1, "Q5b": 1, "Q5c": 1,
    "Q5d": 1, "Q5e": 1, "Q5f": 1,
    "Q6a": 1, "Q6b": 1, "Q6c": 1,
    "Q6d": 1, "Q6e": 1, "Q6f": 1,
    "Q7a": 1, "Q7b": 1, "Q7c": 1,
    "Q7d": 1, "Q7e": 1,
    "Q8": 5,    # Don't know
    "Q9": 5,    # Don't know
    "Q10": 2,   # No
    "Q11": None,
    "Q12": 4,   # Prefer not to say
    "Q13": 7,   # Prefer not to say
    "Q14": 3,   # Other
}

SKIP_LOGIC = ("Q10", "Q11")

DATA_COLUMNS = [
    ("A", "source"),
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
    ("AB", "Q8"),
    ("AC", "Q9"),
    ("AD", "Q10"),
    ("AE", "Q11"),
    ("AF", "Q12"),
    ("AG", "Q13"),
    ("AH", "Q14"),
]
