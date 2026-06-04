#!/usr/bin/env python3
# surveybot/run.py
# Main entry point: process a batch PDF and write results to Excel
#
# Usage:
#   python run.py --pdf surveys.pdf --template template.xlsx --output results.xlsx
#   python run.py --pdf surveys.pdf  (uses default template and auto-names output)

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

from extractor import process_pdf, flatten_result
from writer import write_results


def main():
    parser = argparse.ArgumentParser(description="SurveyBot - Extract handwritten survey responses to Excel")
    parser.add_argument("--pdf",      required=True,  help="Path to batch PDF of scanned surveys")
    parser.add_argument("--template", required=True,  help="Path to Excel template file")
    parser.add_argument("--output",   default=None,   help="Output Excel path (default: auto-named)")
    parser.add_argument("--start",    type=int, default=None,
                        help="Override starting survey number (default: read from survey label)")
    args = parser.parse_args()

    # Validate inputs
    if not Path(args.pdf).exists():
        print(f"ERROR: PDF not found: {args.pdf}")
        sys.exit(1)
    if not Path(args.template).exists():
        print(f"ERROR: Template not found: {args.template}")
        sys.exit(1)

    # Auto-name output if not specified
    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = Path(args.pdf).stem
        args.output = str(Path(args.template).parent / f"{stem}_results_{timestamp}.xlsx")

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("  Set it with: export ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    print("=" * 60)
    print("SurveyBot - Deerfield 109 Mail Survey Extractor")
    print("=" * 60)
    print(f"  PDF:      {args.pdf}")
    print(f"  Template: {args.template}")
    print(f"  Output:   {args.output}")
    print()

    # Step 1: Extract
    raw_results = process_pdf(args.pdf)

    # Step 2: Flatten
    flat_results = [flatten_result(r) for r in raw_results]

    # Step 3: Write to Excel
    print()
    write_results(flat_results, args.template, args.output, start_number=args.start)

    # Step 4: Summary
    ok    = sum(1 for r in flat_results if r.get("_status") == "ok")
    errs  = sum(1 for r in flat_results if r.get("_status") == "error")
    flags = sum(1 for r in flat_results if r.get("_flags"))

    print()
    print("=" * 60)
    print("DONE")
    print(f"  ✓  {ok} surveys extracted successfully")
    if flags:
        print(f"  ⚠️  {flags} surveys have low-confidence responses (highlighted yellow)")
    if errs:
        print(f"  ✗  {errs} surveys failed (highlighted red) — check manually")
    print(f"\nOutput saved to: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
