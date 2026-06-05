#!/usr/bin/env python3
# tally.py — count Q9 (bond referendum vote) across East Maine results

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

# Q9 = column AD = index 29 (0-based)
# source = column AL = index 37
counts = Counter()
total = 0

for f in files:
    try:
        wb = openpyxl.load_workbook(f, read_only=True)
        ws = wb.active
        for row in ws.iter_rows(min_row=4, values_only=True):
            if row[1] is None:
                break
            source = row[37] if len(row) > 37 else None
            if source != 'S':
                continue
            q9 = row[29] if len(row) > 29 else None
            counts[q9] += 1
            total += 1
        wb.close()
        print(f"OK: {f}")
    except Exception as e:
        print(f"ERROR: {f}: {e}")

labels = {
    1: 'Definitely Yes',
    2: 'Probably Yes',
    3: 'Probably No',
    4: 'Definitely No',
    5: "Don't Know",
    None: 'No Answer'
}

print(f'\nTotal surveys: {total}')
print()
for k in [1, 2, 3, 4, 5, None]:
    print(f'{labels[k]}: {counts[k]}')
