# surveybot/config.py
# Full coding scheme for Deerfield 109 mail survey
# Source: Excel template headers + Pablo's instructions

CODING_SCHEME = {
    "Q1": {
        "question": "Prior to receiving this survey, how much had you read/seen/heard about the bond referendum?",
        "type": "single",
        "options": {
            1: "A lot",
            2: "Some",
            3: "Hardly anything",
            4: "Nothing at all",
            5: "No response"
        }
    },
    "Q2": {
        "question": "Overall opinion of District 109 - letter grade",
        "type": "single",
        "options": {
            1: "A", 2: "B", 3: "C", 4: "D", 5: "F",
            6: "Don't know",
            7: "No response"
        }
    },
    "Q3": {
        "question": "Opinion of District 109 facilities - letter grade",
        "type": "single",
        "options": {
            1: "A", 2: "B", 3: "C", 4: "D", 5: "F",
            6: "Don't know",
            7: "No response"
        }
    },
    "Q4": {
        "question": "How likely are you to vote in March 17, 2026 Midterm Primary Election?",
        "type": "single",
        "options": {
            1: "Very likely",
            2: "Somewhat likely",
            3: "Not very likely",
            4: "Not at all likely",
            5: "Don't know"
        }
    },
    "Q5": {
        "question": "Do you have school-age children?",
        "type": "single",
        "options": {
            1: "Yes",
            2: "No (skip to Q7)"
        }
    },
    "Q6": {
        "question": "Which school(s) do they attend? (multi-select)",
        "type": "multi",
        "options": {
            1: "Kipling Elementary School",
            2: "South Park Elementary School",
            3: "Walden Elementary School",
            4: "Wilmot Elementary School",
            5: "Caruso Middle School",
            6: "Shepard Middle School",
            7: "Deerfield High School",
            8: "Other"
        }
    },
    "Q7": {
        "question": "Do you have any grandchildren attending a District 109 school?",
        "type": "single",
        "options": {
            1: "Yes",
            2: "No"
        }
    },
    "Q8": {
        "question": "Which elementary school is your neighborhood school?",
        "type": "single",
        "options": {
            1: "Kipling Elementary School",
            2: "South Park Elementary School",
            3: "Walden Elementary School",
            4: "Wilmot Elementary School",
            5: "Don't know"
        }
    },
    "Q9": {
        "question": "Priority rating for proposed school building improvements (1=Low, 5=High)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Kipling Elementary School (76 years old)",
            "b": "South Park Elementary School (68 years old)",
            "c": "Walden Elementary School (68 years old)",
            "d": "Wilmot Elementary School (68 years old)",
            "e": "Caruso Middle School (56 years old)",
            "f": "Shepard Middle School (64 years old)"
        }
    },
    "Q10": {
        "question": "How convincing are these SUPPORTING statements? (1=Not at all, 5=Very convincing)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Security improvements - stronger access controls and entry vestibules",
            "b": "Six schools collectively 400 years old - outdated plumbing/electrical/HVAC",
            "c": "Aging water/sewer systems already failing - could shut down a school",
            "d": "Outdated/overcrowded classrooms negatively impact learning",
            "e": "More than half of cost covered by District savings and non-referendum funds",
            "f": "Two new schools + renovations would minimize disruptions, eliminate modulars",
            "g": "Postponing will increase total cost by millions annually due to inflation"
        }
    },
    "Q11": {
        "question": "How convincing are these OPPOSING statements? (1=Not at all, 5=Very convincing)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Economic uncertainty - not the right time to seek additional tax dollars",
            "b": "Property taxes are already too high",
            "c": "All four aging elementary schools should be replaced, not just two",
            "d": "District funding too many projects at once - proposal should be scaled back"
        }
    },
    "Q12": {
        "question": "How confident are you District 109 would manage bond funds responsibly?",
        "type": "single",
        "options": {
            1: "Very confident",
            2: "Somewhat confident",
            3: "Not very confident",
            4: "Not at all confident",
            5: "Don't know"
        }
    },
    "Q13": {
        "question": "Concern about $536/$10k tax increase impact on household budget?",
        "type": "single",
        "options": {
            1: "Very concerned",
            2: "Somewhat concerned",
            3: "Not very concerned",
            4: "Not at all concerned",
            5: "Don't know"
        }
    },
    "Q14": {
        "question": "Vote on $121.4M bond referendum?",
        "type": "single",
        "options": {
            1: "Definitely yes",
            2: "Probably yes",
            3: "Probably no",
            4: "Definitely no",
            5: "Don't know"
        }
    },
    "Q15": {
        "question": "Vote on $153.6M alternative proposal?",
        "type": "single",
        "options": {
            1: "Definitely yes",
            2: "Probably yes",
            3: "Probably no",
            4: "Definitely no",
            5: "Don't know"
        }
    },
    "Q16": {
        "question": "Gender (multi-select, multiple people may respond)",
        "type": "multi",
        "options": {
            1: "Male",
            2: "Female",
            3: "Prefer to self-describe",
            4: "Prefer not to say"
        }
    },
    "Q17": {
        "question": "Age (multi-select, multiple people may respond)",
        "type": "multi",
        "options": {
            1: "18-34",
            2: "35-44",
            3: "45-54",
            4: "55-64",
            5: "65-74",
            6: "75 or older"
        }
    }
}

# Excel column order (matches template exactly)
EXCEL_COLUMNS = [
    "#", "L_U",
    "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8",
    "Q9", "Q9a", "Q9b", "Q9c", "Q9d", "Q9e", "Q9f",
    "Q10", "Q10a", "Q10b", "Q10c", "Q10d", "Q10e", "Q10f", "Q10g",
    "Q11", "Q11a", "Q11b", "Q11c", "Q11d",
    "Q12", "Q13", "Q14", "Q15", "Q16", "Q17", "source"
]

# Note: Q9, Q10, Q11 parent columns are intentionally blank in the template
# (they're header rows only) - sub-question columns carry the data

SURVEY_SOURCE = "S"  # S = Snail Mail (vs Q=QR, T=Text)
