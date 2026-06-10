# surveys/east_maine/config.py
SURVEY_SOURCE = "S"
PAGE_STRUCTURE = "east_maine"
HEADER_ROWS = 3
NO_RESPONSE_DEFAULTS = {}
SKIP_LOGIC = ("Q10", "Q11")
DATA_COLUMNS = [
    ("A", None), ("B", "#"), ("C", "L_U"),
    ("D", "Q1"), ("E", "Q2"), ("F", "Q3"), ("G", "Q4"),
    ("H", None), ("I", "Q5a"), ("J", "Q5b"), ("K", "Q5c"),
    ("L", "Q5d"), ("M", "Q5e"), ("N", "Q5f"),
    ("O", None), ("P", "Q6a"), ("Q", "Q6b"), ("R", "Q6c"),
    ("S", "Q6d"), ("T", "Q6e"), ("U", "Q6f"),
    ("V", None), ("W", "Q7a"), ("X", "Q7b"), ("Y", "Q7c"),
    ("Z", "Q7d"), ("AA", "Q7e"), ("AB", "Q7f"),
    ("AC", "Q8"), ("AD", "Q9"), ("AE", "Q10"), ("AF", "Q11"),
    ("AG", "Q12"), ("AH", "Q13"), ("AI", "Q14"), ("AJ", "Q15"),
    ("AK", "Q16"), ("AL", "source"),
]
