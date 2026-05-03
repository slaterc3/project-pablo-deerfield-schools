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


def extract_survey(front_img, inside_img, back_img, client):
    """Send three cropped images to Claude vision and return extracted JSON."""
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
            result = extract_survey(front_img, inside_img, back_img, client)
            result["_page_index"] = i
            result["_status"] = "ok"

            # low_conf = [k for k, v in result.items()
            #             if isinstance(v, dict) and v.get("confidence") == "low"]
            # if low_conf:
            #     result["_flags"] = low_conf
            #     print(f"⚠️  flagged: {low_conf}")
            # updated cs 5/3/26
            low_conf = [k for k, v in result.items()
            if isinstance(v, dict) and v.get("confidence") == "low"]
            med_conf = [k for k, v in result.items()
                    if isinstance(v, dict) and v.get("confidence") == "medium"]
            flags = low_conf + [f"{k}?" for k in med_conf]
            if flags:
                result["_flags"] = flags
                print(f"⚠️  flagged: {flags}")
            else:
                print("✓")

            results.append(result)
            print(f"    {json.dumps(flatten_result(result))}")

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "survey_id": f"ERROR-{survey_num}",
                "_page_index": i,
                "_status": "error",
                "_error": str(e)
            })

    doc.close()
    return results


def flatten_result(result: dict) -> dict:
    """Flatten extracted JSON into a simple key→value dict for Excel writing."""
    flat = {
        "survey_id": result.get("survey_id", ""),
        "likely_voter": result.get("likely_voter", ""),
        "_status": result.get("_status", ""),
        "_flags": ",".join(result.get("_flags", [])) if result.get("_flags") else "",
    }

    question_keys = [
        "Q1","Q2","Q3","Q4","Q5","Q6","Q7","Q8",
        "Q9a","Q9b","Q9c","Q9d","Q9e","Q9f",
        "Q10a","Q10b","Q10c","Q10d","Q10e","Q10f","Q10g",
        "Q11a","Q11b","Q11c","Q11d",
        "Q12","Q13","Q14","Q15","Q16","Q17"
    ]

    for key in question_keys:
        entry = result.get(key)
        if entry is None:
            flat[key] = None
        elif isinstance(entry, dict):
            val = entry.get("value")
            if isinstance(val, list):
                flat[key] = ",".join(str(v) for v in val) if val else None
            else:
                flat[key] = val
        else:
            flat[key] = entry

    return flat


if __name__ == "__main__":
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "files/Sample_survey01.pdf"
    results = process_pdf(pdf)
    print("\n--- EXTRACTED RESULTS ---")
    for r in results:
        print(json.dumps(flatten_result(r), indent=2))