#!/usr/bin/env python3
# tally.py — summary statistics across East Maine results

import openpyxl
from collections import Counter

files = [
    'files/281457 East Maine Likely 1 - 1-59_results_20260603_171517.xlsx',
    'files/281457 East Maine Likely 2 - 60-154_results_20260603_173136.xlsx',
    'files/281457 East Maine Likely 3 - 155-203_results_20260603_174916.xlsx',
    'files/281457 East Maine Likely 4 - 204-214_results_20260603_181110.xlsx',
    'files/281457 East Maine Likely 5 - 215-228_results_20260603_184047.xlsx',
    'files/281457 East Maine Unlikely 1 - 1-21_results_20260603_145736.xlsx',
]

# Column indices (0-based) from East Maine DATA_COLUMNS
# A=0(None), B=1(#), C=2(L_U), D=3(Q1), E=4(Q2), F=5(Q3), G=6(Q4)
# H=7(None/Q5 header), I=8(Q5a)...N=13(Q5f)
# O=14(None/Q6 header), P=15(Q6a)...U=20(Q6f)
# V=21(None/Q7 header), W=22(Q7a)...AB=27(Q7f)
# AC=28(Q8), AD=29(Q9), AE=30(Q10), AF=31(Q11)
# AG=32(Q12), AH=33(Q13), AI=34(Q14), AJ=35(Q15), AK=36(Q16)
# AL=37(source)

COL = {
    "L_U":  2,
    "Q1":   3,
    "Q2":   4,
    "Q3":   5,
    "Q4":   6,
    "Q8":   28,
    "Q9":   29,
    "Q10":  30,
    "Q11":  31,
    "Q12":  32,
    "Q13":  33,
    "Q14":  34,
    "Q15":  35,
    "Q16":  36,
    "source": 37,
}

# Collect all rows
rows = []
for f in files:
    try:
        wb = openpyxl.load_workbook(f, read_only=True)
        ws = wb.active
        for row in ws.iter_rows(min_row=4, values_only=True):
            if row[1] is None:
                break
            if row[COL["source"]] != 'S':
                continue
            rows.append(row)
        wb.close()
    except Exception as e:
        print(f"ERROR: {f}: {e}")

total = len(rows)

def tally(col_idx, labels, title):
    counts = Counter(row[col_idx] for row in rows)
    print(f"\n{title} (n={total})")
    print("-" * 40)
    for k, label in labels.items():
        print(f"  {label}: {counts.get(k, 0)}")

def tally_multiselect(col_idx, labels, title):
    """For multi-select columns stored as comma strings."""
    counts = Counter()
    for row in rows:
        val = row[col_idx]
        if val is None:
            counts[None] += 1
            continue
        for v in str(val).split(","):
            try:
                counts[int(v.strip())] += 1
            except ValueError:
                pass
    print(f"\n{title} (n={total}, multi-select)")
    print("-" * 40)
    for k, label in labels.items():
        print(f"  {label}: {counts.get(k, 0)}")

print(f"{'='*50}")
print(f"EAST MAINE SD 63 — MAIL SURVEY SUMMARY")
print(f"Total surveys: {total}")
print(f"{'='*50}")

# Likely vs Unlikely
lu = Counter(row[COL["L_U"]] for row in rows)
print(f"\nLikely/Unlikely")
print("-" * 40)
print(f"  Likely:   {lu.get('L', 0)}")
print(f"  Unlikely: {lu.get('U', 0)}")

tally(COL["Q1"], {
    1: "A lot",
    2: "Some",
    3: "Hardly anything",
    4: "Nothing at all",
    5: "Don't know",
}, "Q1 — Prior awareness of bond referendum")

tally(COL["Q2"], {
    1:"A", 2:"B", 3:"C", 4:"D", 5:"F", 6:"Don't know"
}, "Q2 — Overall opinion of District 63 (grade)")

tally(COL["Q3"], {
    1:"A", 2:"B", 3:"C", 4:"D", 5:"F", 6:"Don't know"
}, "Q3 — Opinion of facilities (grade)")

tally(COL["Q4"], {
    1:"Very confident", 2:"Somewhat confident",
    3:"Not very confident", 4:"Not at all confident", 5:"Don't know"
}, "Q4 — Confidence district would use funds responsibly")

tally(COL["Q8"], {
    1:"Very concerned", 2:"Somewhat concerned",
    3:"Not very concerned", 4:"Not at all concerned", 5:"Don't know"
}, "Q8 — Concern about tax impact")

tally(COL["Q9"], {
    1:"Definitely Yes", 2:"Probably Yes",
    3:"Probably No", 4:"Definitely No", 5:"Don't know"
}, "Q9 — Vote on bond referendum")

tally(COL["Q10"], {
    1:"Yes", 2:"No"
}, "Q10 — School-age children")

tally(COL["Q12"], {
    1:"Yes", 2:"No"
}, "Q12 — Grandchildren attending District 63")


tally_multiselect(COL["Q14"], {
    1:"Male", 2:"Female", 3:"Prefer to self-describe", 4:"Prefer not to say"
}, "Q14 — Gender")

tally_multiselect(COL["Q15"], {
    1:"18-34", 2:"35-44", 3:"45-54",
    4:"55-64", 5:"65-74", 6:"75 or older", 7:"Prefer not to say"
}, "Q15 — Age")

tally(COL["Q16"], {
    1:"Own", 2:"Rent", 3:"Other"
}, "Q16 — Own or rent")


print(f"\n{'='*50}")
