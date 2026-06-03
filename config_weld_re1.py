# surveybot/config_weld_re1.py
# Configuration for Weld County School District RE-1 survey
# Colorado printer — page order is REVERSED (inside first, outside second)
# Survey label (L #X) is handwritten at top of inside page

SURVEY_SOURCE = "S"  # S = Snail Mail

# Page structure override for this survey
# inside page comes FIRST, outside page comes SECOND
PAGE_ORDER = "inside_first"

CODING_SCHEME = {
    "Q1": {
        "question": "Prior to receiving this survey, how much had you read/seen/heard about Weld RE-1's proposed MLO and bond measure?",
        "type": "single",
        "options": {
            1: "A lot",
            2: "Some",
            3: "Hardly anything",
            4: "Nothing at all"
        }
    },
    "Q2": {
        "question": "Overall opinion of Weld RE-1 - letter grade",
        "type": "single",
        "options": {
            1: "A", 2: "B", 3: "C", 4: "D", 5: "F",
            6: "Don't know"
        }
    },
    "Q3": {
        "question": "Opinion of Weld RE-1 facilities - letter grade",
        "type": "single",
        "options": {
            1: "A", 2: "B", 3: "C", 4: "D", 5: "F",
            6: "Don't know"
        }
    },
    "Q4": {
        "question": "How confident are you that Weld RE-1 would use funds from voter-approved ballot measures responsibly?",
        "type": "single",
        "options": {
            1: "Very confident",
            2: "Somewhat confident",
            3: "Not very confident",
            4: "Not at all confident",
            5: "Don't know"
        }
    },
    "Q5": {
        "question": "Priority for funding operating need (1=Low, 5=High)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Improving teacher and staff pay to close the gap with other school districts"
        }
    },
    "Q6": {
        "question": "Priority for funding proposed facility improvements (1=Low, 5=High)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Constructing a new grade 6-12 school (Valley Middle-High School) in Gilcrest",
            "b": "Updating Pete Mirich Elementary School in LaSalle",
            "c": "Converting Educational and Community Center in Platteville to PK-5 school",
            "d": "Replacing outdated buses to improve transportation safety",
            "e": "Upgrading technology infrastructure",
            "f": "Improving the athletic field complex"
        }
    },
    "Q7": {
        "question": "Do you have school-age (PK-12) children?",
        "type": "single",
        "options": {
            1: "Yes",
            2: "No"
        }
    },
    "Q8": {
        "question": "If yes, which school(s) do they attend? (multi-select)",
        "type": "multi",
        "options": {
            1: "Gilcrest Elementary",
            2: "Platteville Elementary",
            3: "Pete Mirich Elementary",
            4: "Valley Middle School",
            5: "Valley High School",
            6: "Other"
        }
    },
    "Q9": {
        "question": "How convincing are these SUPPORTING statements? (1=Not at all, 5=Very convincing)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Oil/gas industry pays 66% of taxes; homeowners pay 7%",
            "b": "Declining enrollment — consolidating schools is financially responsible",
            "c": "New 6-12 school offers academic and CTE programs",
            "d": "Weld RE-1 has lowest starting teacher pay among peer districts",
            "e": "Expensive to recruit/train teachers who then leave for better pay",
            "f": "Protecting school quality prevents enrollment losses and lower property values"
        }
    },
    "Q10": {
        "question": "How convincing are these OPPOSING statements? (1=Not at all, 5=Very convincing)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Proposed improvements including new 6-12 school seem like a lot",
            "b": "Cost of groceries/fuel/necessities rising — families can't afford higher taxes",
            "c": "Property taxes are already too high",
            "d": "Residents skeptical bond funds would be spent as intended",
            "e": "District should address one challenge at a time, starting with teacher turnover",
            "f": "If oil/gas property values go up, homeowner share goes down — future tax uncertainty"
        }
    },
    "Q11": {
        "question": "Concern about $21/$400k MLO tax increase impact on household budget?",
        "type": "single",
        "options": {
            1: "Very concerned",
            2: "Somewhat concerned",
            3: "Not very concerned",
            4: "Not at all concerned",
            5: "Don't know"
        }
    },
    "Q12": {
        "question": "Vote on $1.3M mill levy override question?",
        "type": "single",
        "options": {
            1: "Definitely yes",
            2: "Probably yes",
            3: "Probably no",
            4: "Definitely no",
            5: "Don't know"
        }
    },
    "Q13": {
        "question": "Concern about $227/$400k bond measure tax increase impact on household budget?",
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
        "question": "Vote on $219M bond measure question?",
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
        "question": "Gender (multi-select, multiple people may respond)",
        "type": "multi",
        "options": {
            1: "Male",
            2: "Female",
            3: "Prefer to self-describe",
            4: "Prefer not to say"
        }
    },
    "Q16": {
        "question": "Age (multi-select, multiple people may respond)",
        "type": "multi",
        "options": {
            1: "18-34",
            2: "35-44",
            3: "45-54",
            4: "55-64",
            5: "65-74",
            6: "75 or older",
            7: "Prefer not to say"
        }
    },
    "Q17": {
        "question": "Do you own or rent your home?",
        "type": "single",
        "options": {
            1: "Own",
            2: "Rent",
            3: "Other",
            4: "Prefer not to say"
        }
    }
}

# No-response defaults (last valid option per question)
# Scale questions default to 1 per Pablo's instruction
NO_RESPONSE_DEFAULTS = {
    "Q1": 4,    # Nothing at all
    "Q2": 6,    # Don't know
    "Q3": 6,    # Don't know
    "Q4": 5,    # Don't know
    "Q5a": 1,
    "Q6a": 1, "Q6b": 1, "Q6c": 1,
    "Q6d": 1, "Q6e": 1, "Q6f": 1,
    "Q7": 2,    # No
    "Q8": None, # Depends on Q7
    "Q9a": 1, "Q9b": 1, "Q9c": 1,
    "Q9d": 1, "Q9e": 1, "Q9f": 1,
    "Q10a": 1, "Q10b": 1, "Q10c": 1,
    "Q10d": 1, "Q10e": 1, "Q10f": 1,
    "Q11": 5,   # Don't know
    "Q12": 5,   # Don't know
    "Q13": 5,   # Don't know
    "Q14": 5,   # Don't know
    "Q15": 4,   # Prefer not to say
    "Q16": 7,   # Prefer not to say
    "Q17": 4,   # Prefer not to say
}
