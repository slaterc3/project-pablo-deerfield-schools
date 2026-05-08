# surveybot/extractor.py
# Core extraction engine: PDF → images → Claude vision → JSON
#
# REAL PAGE STRUCTURE (each scanned sheet = 2 panels side by side):
#
#   Page 0 (outside): [orphan Q13-Q17] | [Survey 1: Q1-Q4 + label]
#   Page 1 (inside):  [Survey 1: Q5-Q12]
#   Page 2 (outside): [Survey 1: Q13-Q17] | [Survey 2: Q1-Q4 + label]
#   Page 3 (inside):  [Survey 2: Q5-Q12]
#   ...
#
# For survey i (0-indexed):
#   front  (Q1-Q4)   = RIGHT half of page (i * 2)
#   inside (Q5-Q12)  = FULL page (i * 2 + 1)
#   back   (Q13-Q17) = LEFT half of page ((i + 1) * 2)

import fitz
import anthropic
import base64
import json
import os
from prompt import SYSTEM_PROMPT, USER_PROMPT
from models import SurveyResult, parse_and_validate


def get_page_crop(doc: fitz.Document, page_num: int, half: str = "full", dpi: int = 150) -> bytes:
    """Render a page or half-page to PNG bytes."""
    page = doc[page_num]
    rect = page.rect
    mid_x = rect.width / 2

    if half == "left":
        clip = fitz.Rect(0, 0, mid_x, rect.height)
    elif half == "right":
        clip = fitz.Rect(mid_x, 0, rect.width, rect.height)
    else:
        clip = rect

    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip)
    return pix.tobytes("png")


def extract_survey(front_img, inside_img, back_img, client) -> dict:
    """Send three cropped images to Claude vision and return raw JSON dict."""
    front_b64  = base64.standard_b64encode(front_img).decode("utf-8")
    inside_b64 = base64.standard_b64encode(inside_img).decode("utf-8")

    content = [
        {"type": "text", "text": "Image 1 - FRONT of survey (right panel of outside page): contains survey ID label (e.g. L-1) and Q1, Q2, Q3, Q4."},
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": front_b64}},
        {"type": "text", "text": "Image 2 - INSIDE of survey (full inside page): contains Q5 through Q12."},
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": inside_b64}},
    ]

    if back_img is not None:
        back_b64 = base64.standard_b64encode(back_img).decode("utf-8")
        content.append({"type": "text", "text": "Image 3 - BACK of survey (left panel of next outside page): contains Q13, Q14, Q15, Q16, Q17."})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": back_b64}})
    else:
        content.append({"type": "text", "text": "Image 3 (BACK/Q13-Q17) is not available — set Q13, Q14, Q15, Q16, Q17 to null."})

    content.append({"type": "text", "text": USER_PROMPT})

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def process_pdf(pdf_path: str, api_key: str = None) -> list[dict]:
    """Process a batch PDF of surveys, cropping pages correctly."""
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    print(f"Loading PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    if total_pages % 2 != 0:
        print(f"WARNING: Odd number of pages ({total_pages}). Last page will be skipped.")

    num_surveys = total_pages // 2
    print(f"Found {total_pages} pages → {num_surveys} surveys to process")

    results = []
    for i in range(num_surveys):
        survey_num            = i + 1
        outside_page_num      = i * 2
        inside_page_num       = i * 2 + 1
        next_outside_page_num = (i + 1) * 2

        front_img  = get_page_crop(doc, outside_page_num, half="right")
        inside_img = get_page_crop(doc, inside_page_num,  half="full")
        back_img   = get_page_crop(doc, next_outside_page_num, half="left") \
                     if next_outside_page_num < total_pages else None

        suffix = " (last survey — Q13-Q17 null)" if back_img is None else ""
        print(f"  Extracting survey {survey_num}/{num_surveys}{suffix}...", end=" ", flush=True)

        try:
            # 1. Get raw JSON from Claude
            raw_dict = extract_survey(front_img, inside_img, back_img, client)

            # 2. Validate with Pydantic
            survey, errors = parse_and_validate(raw_dict)

            if errors:
                print(f"VALIDATION ERROR: {errors}")
                results.append({
                    "survey_id": raw_dict.get("survey_id", f"ERROR-{survey_num}"),
                    "likely_voter": raw_dict.get("likely_voter", ""),
                    "_status": "validation_error",
                    "_flags": str(errors),
                })
                continue

            # 3. Get confidence flags from validated model
            flags = survey.get_flags()

            # 4. Auto-flag suspicious multi-select responses
            flat = survey.to_flat_dict()
            multi_thresholds = {"Q6": 2, "Q16": 3, "Q17": 3}
            for q, threshold in multi_thresholds.items():
                val = flat.get(q)
                if val and len(str(val).split(",")) >= threshold:
                    if q not in flags and f"{q}?" not in flags:
                        flags.append(f"{q}?")

            # 5. Build output dict
            flat["_status"] = "ok"
            flat["_flags"]  = ",".join(flags) if flags else ""

            if flags:
                print(f"⚠️  flagged: {flags}")
            else:
                print("✓")

            print(f"    {json.dumps(flat)}")
            results.append(flat)

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "survey_id": f"ERROR-{survey_num}",
                "likely_voter": "",
                "_status": "error",
                "_flags": str(e),
            })

    doc.close()
    return results


def flatten_result(result: dict) -> dict:
    """
    Pass-through for compatibility with writer.py.
    Results from process_pdf are already flat dicts since Pydantic refactor.
    """
    return result


if __name__ == "__main__":
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "files/Sample_survey01.pdf"
    results = process_pdf(pdf)
    print("\n--- EXTRACTED RESULTS ---")
    for r in results:
        print(json.dumps(r, indent=2))