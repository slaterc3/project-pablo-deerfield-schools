# surveybot/config_east_maine.py
# Configuration for East Maine School District 63 survey
# Illinois printer — clean 2-page format, no cropping needed
# Label format: UL-X (Unlikely) or L-X (Likely) at top center of outside page

SURVEY_SOURCE = "S"  # S = Snail Mail

PAGE_ORDER = "outside_first"
PAGE_STRUCTURE = "full_pages"  # no cropping, both pages sent full

CODING_SCHEME = {
    "Q1": {
        "question": "Prior to receiving this survey, how much had you read/seen/heard about East Maine SD 63's proposed bond referendum?",
        "type": "single",
        "options": {
            1: "A lot",
            2: "Some",
            3: "Hardly anything",
            4: "Nothing at all"
        }
    },
    "Q2": {
        "question": "Overall opinion of District 63 - letter grade",
        "type": "single",
        "options": {
            1: "A", 2: "B", 3: "C", 4: "D", 5: "F",
            6: "Don't know"
        }
    },
    "Q3": {
        "question": "Opinion of District 63 facilities - letter grade",
        "type": "single",
        "options": {
            1: "A", 2: "B", 3: "C", 4: "D", 5: "F",
            6: "Don't know"
        }
    },
    "Q4": {
        "question": "How confident are you that District 63 would use funds from a voter-approved bond referendum responsibly?",
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
        "question": "Priority for proposed school building improvements (1=Low, 5=High)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Safety and security improvements, including updated fire-safety systems, more secure entryways, and reconfigured drop-off/pick-up areas",
            "b": "ADA upgrades, including elevators to replace aging chair lifts, ADA-compliant restrooms/hallways, and mobile classroom removal",
            "c": "Replacement of outdated, inefficient plumbing, electrical, and mechanical/HVAC systems",
            "d": "Addition and reconfiguration of classrooms and student support spaces to address overcrowding",
            "e": "Construction of gymnasiums at schools that currently rely on multipurpose spaces",
            "f": "Classroom and library updates, including lighting, flooring, acoustics, and furniture"
        }
    },
    "Q6": {
        "question": "How convincing are these SUPPORTING statements? (1=Not at all, 5=Very convincing)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Protecting the safety and security of our students and staff is critical",
            "b": "Replacing aging building systems will extend life of school buildings, reduce emergency repairs, and improve energy efficiency",
            "c": "Without additional space, students will continue learning in undersized classrooms, hallways, mobile units, and shared spaces",
            "d": "Our schools have many ADA challenges which disrupts learning",
            "e": "Total cost of proposed improvements could increase by estimated $35 million if we wait another five years",
            "f": "Investing in schools helps strengthen neighborhoods, provides shared community resources, and protects property values"
        }
    },
    "Q7": {
        "question": "How convincing are these OPPOSING statements? (1=Not at all, 5=Very convincing)",
        "type": "scale_group",
        "sub_questions": {
            "a": "Funding proposal should be limited to replacing outdated systems, not new construction to add classrooms and spaces",
            "b": "Given rising household expenses, now is not a good time to ask taxpayers for additional funding",
            "c": "Property taxes are already high, residents should not be asked to pay more",
            "d": "The District should make do with its existing facilities and resources",
            "e": "Taxpayers should not be required to fund projects that do not directly benefit them, including those without school-age children",
            "f": "Any new voter-approved funds should go to classroom instruction and teachers, not building improvements"
        }
    },
    "Q8": {
        "question": "Concern about $423/$350k tax increase impact on household budget?",
        "type": "single",
        "options": {
            1: "Very concerned",
            2: "Somewhat concerned",
            3: "Not very concerned",
            4: "Not at all concerned",
            5: "Don't know"
        }
    },
    "Q9": {
        "question": "Vote on $163M bond referendum?",
        "type": "single",
        "options": {
            1: "Definitely yes",
            2: "Probably yes",
            3: "Probably no",
            4: "Definitely no",
            5: "Don't know"
        }
    },
    "Q10": {
        "question": "Do you have school-age (PK-12) children?",
        "type": "single",
        "options": {
            1: "Yes",
            2: "No"
        }
    },
    "Q11": {
        "question": "If yes, which school(s) do they attend? (multi-select)",
        "type": "multi",
        "options": {
            1: "First Steps Preschool",
            2: "Apollo Elementary School",
            3: "Mark Twain Elementary School",
            4: "Melzer Elementary School",
            5: "Nelson Elementary School",
            6: "Washington Elementary School",
            7: "Gemini Middle School",
            8: "Maine East High School",
            9: "Other"
        }
    },
    "Q12": {
        "question": "Do you have grandchildren attending a District 63 school?",
        "type": "single",
        "options": {
            1: "Yes",
            2: "No"
        }
    },
    "Q13": {
        "question": "Which elementary school do you consider to be your neighborhood school?",
        "type": "single",
        "options": {
            1: "Apollo Elementary School",
            2: "Mark Twain Elementary School",
            3: "Melzer Elementary School",
            4: "Nelson Elementary School",
            5: "Washington Elementary School",
            6: "Don't know"
        }
    },
    "Q14": {
        "question": "Gender (multi-select, multiple people may respond)",
        "type": "multi",
        "options": {
            1: "Male",
            2: "Female",
            3: "Prefer to self-describe",
            4: "Prefer not to say"
        }
    },
    "Q15": {
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
    "Q16": {
        "question": "Do you own or rent your home?",
        "type": "single",
        "options": {
            1: "Own",
            2: "Rent",
            3: "Other"
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
    "Q5a": 1, "Q5b": 1, "Q5c": 1,
    "Q5d": 1, "Q5e": 1, "Q5f": 1,
    "Q6a": 1, "Q6b": 1, "Q6c": 1,
    "Q6d": 1, "Q6e": 1, "Q6f": 1,
    "Q7a": 1, "Q7b": 1, "Q7c": 1,
    "Q7d": 1, "Q7e": 1, "Q7f": 1,
    "Q8": 5,    # Don't know
    "Q9": 5,    # Don't know
    "Q10": 2,   # No
    "Q11": None, # Depends on Q10
    "Q12": 2,   # No
    "Q13": 6,   # Don't know
    "Q14": 4,   # Prefer not to say
    "Q15": 7,   # Prefer not to say
    "Q16": 3,   # Other
}
