#!/usr/bin/env python3
# surveybot/run.py
# Main entry point — all survey types, one script
#
# Usage:
#   python run.py --pdf surveys.pdf --template template.xlsx --survey-type east_maine

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import time
# from tracemalloc import start

from extractor import process_pdf, flatten_result, SUPPORTED_SURVEY_TYPES
from writer import write_results


def main():
    parser = argparse.ArgumentParser(description="SurveyBot - Extract handwritten survey responses to Excel")
    parser.add_argument("--pdf",         required=True,  help="Path to batch PDF of scanned surveys")
    parser.add_argument("--template",    required=True,  help="Path to Excel template file")
    parser.add_argument("--output",      default=None,   help="Output Excel path (default: auto-named)")
    parser.add_argument("--survey-type", default="deerfield",
                        choices=SUPPORTED_SURVEY_TYPES,
                        help=f"Survey format type. Options: {SUPPORTED_SURVEY_TYPES}")
    parser.add_argument("--start",       type=int, default=None,
                        help="Override starting survey number")
    args = parser.parse_args()

    if not Path(args.pdf).exists():
        print(f"ERROR: PDF not found: {args.pdf}")
        sys.exit(1)
    if not Path(args.template).exists():
        print(f"ERROR: Template not found: {args.template}")
        sys.exit(1)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set. Run: export ANTHROPIC_API_KEY=your_key")
        sys.exit(1)

    if args.output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = Path(args.pdf).stem
        args.output = str(Path(args.template).parent / f"{stem}_results_{timestamp}.xlsx")

    print("=" * 60)
    print("SurveyBot - Mail Survey Extractor")
    print("=" * 60)
    print(f"  PDF:         {args.pdf}")
    print(f"  Template:    {args.template}")
    print(f"  Output:      {args.output}")
    print(f"  Survey type: {args.survey_type}")
    print()

    start = time.time()
    raw_results  = process_pdf(args.pdf, survey_type=args.survey_type)
    
    elapsed = time.time() - start

    print(f"  Extraction time: {elapsed:.1f}s ({elapsed/len(raw_results):.1f}s per survey)")
    flat_results = [flatten_result(r) for r in raw_results]

    print()
    # write_results(flat_results, args.template, args.output, start_number=args.start)
    write_results(flat_results, args.template, args.output, 
              start_number=args.start, survey_type=args.survey_type)

    ok    = sum(1 for r in flat_results if r.get("_status") == "ok")
    errs  = sum(1 for r in flat_results if r.get("_status") == "error")
    flags = sum(1 for r in flat_results if r.get("_flags"))

    print()
    print("=" * 60)
    print("DONE")
    print(f"  ✓  {ok} surveys extracted successfully")
    if flags:
        print(f"  ⚠️  {flags} surveys have flagged responses")
    if errs:
        print(f"  ✗  {errs} surveys failed — check manually")
    print(f"\nOutput saved to: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
