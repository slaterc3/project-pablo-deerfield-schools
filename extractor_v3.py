# surveybot/extractor.py
# Core extraction engine: PDF → images → Claude vision → JSON
#
# DEERFIELD PAGE STRUCTURE (each outside scan = 2 panels side by side):
#
#   Page 0 (outside): [orphan Q13-Q17] | [Survey 1: Q1-Q4 + label]
#   Page 1 (inside):  [Survey 1: Q5-Q12 — full page]
#   Page 2 (outside): [Survey 1: Q13-Q17] | [Survey 2: Q1-Q4 + label]
#   ...
#   Crops: front = RIGHT half of outside, inside = FULL inside, back = LEFT half of next outside
#
# WELD RE-1 PAGE STRUCTURE (inside comes first, inside split left/right):
#
#   Page 0 (inside):  [Survey 1: Q5-Q6 LEFT] | [Survey 1: Q7-Q10 RIGHT + label top]
#   Page 1 (outside): [Survey 1: Q11-Q17 LEFT] | [Survey 1: Q1-Q4 RIGHT]
#   Page 2 (inside):  [Survey 2: Q5-Q6 LEFT] | [Survey 2: Q7-Q10 RIGHT + label top]
#   ...
#   Crops: inside_left = LEFT half of inside, inside_right = RIGHT half of inside,
#          outside = FULL outside page

import fitz
import anthropic
import base64
import json
import os
from models import parse_and_validate
from config import NO_RESPONSE_DEFAULTS as DEERFIELD_DEFAULTS

SUPPORTED_SURVEY_TYPES = ["deerfield", "weld_re1"]


def load_prompts(survey_type: str):
    """Load the correct system and user prompts for the given survey type."""
    if survey_type == "deerfield":
        from prompt import SYSTEM_PROMPT, USER_PROMPT
    elif survey_type == "weld_re1":
        from prompt_weld_re1 import SYSTEM_PROMPT, USER_PROMPT
    else:
        raise ValueError(f"Unknown survey type: {survey_type}. Must be one of {SUPPORTED_SURVEY_TYPES}")
    return SYSTEM_PROMPT, USER_PROMPT


def load_defaults(survey_type: str) -> dict:
    """Load the correct NO_RESPONSE_DEFAULTS for the given survey type."""
    if survey_type == "deerfield":
        from config import NO_RESPONSE_DEFAULTS
    elif survey_type == "weld_re1":
        from config_weld_re1 import NO_RESPONSE_DEFAULTS
    else:
        raise ValueError(f"Unknown survey type: {survey_type}")
    return NO_RESPONSE_DEFAULTS


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


def extract_survey(img1: bytes, img2: bytes, img3: bytes | None,
                   client: anthropic.Anthropic,
                   system_prompt: str, user_prompt: str) -> dict:
    """
    Send three images to Claude vision and return raw JSON dict.
    Image descriptions depend on survey type — handled by the prompt.
    """
    b64_1 = base64.standard_b64encode(img1).decode("utf-8")
    b64_2 = base64.standard_b64encode(img2).decode("utf-8")

    content = [
        {"type": "text", "text": "Image 1:"},
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64_1}},
        {"type": "text", "text": "Image 2:"},
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64_2}},
    ]

    if img3 is not None:
        b64_3 = base64.standard_b64encode(img3).decode("utf-8")
        content.append({"type": "text", "text": "Image 3:"})
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64_3}})
    else:
        content.append({"type": "text", "text": "Image 3 is not available — set those questions to null."})

    content.append({"type": "text", "text": user_prompt})

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": content}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def get_survey_images_deerfield(doc: fitz.Document, i: int) -> tuple:
    """
    Get the three image crops for survey i in Deerfield format.
    Returns (img1, img2, img3) where:
      img1 = right half of outside page (Q1-Q4 + label)
      img2 = full inside page (Q5-Q12)
      img3 = left half of next outside page (Q13-Q17), or None if last survey
    """
    total_pages = len(doc)
    outside_page      = i * 2
    inside_page       = i * 2 + 1
    next_outside_page = (i + 1) * 2

    img1 = get_page_crop(doc, outside_page, half="right")
    img2 = get_page_crop(doc, inside_page,  half="full")
    img3 = get_page_crop(doc, next_outside_page, half="left") \
           if next_outside_page < total_pages else None

    return img1, img2, img3


def get_survey_images_weld_re1(doc: fitz.Document, i: int) -> tuple:
    """
    Get the three image crops for survey i in Weld RE-1 format.
    Returns (img1, img2, img3) where:
      img1 = left half of inside page (Q5-Q6)
      img2 = right half of inside page (Q7-Q10 + label)
      img3 = full outside page (Q1-Q4 right, Q11-Q17 left)
    """
    inside_page  = i * 2
    outside_page = i * 2 + 1

    img1 = get_page_crop(doc, inside_page,  half="left")
    img2 = get_page_crop(doc, inside_page,  half="right")
    img3 = get_page_crop(doc, outside_page, half="full")

    return img1, img2, img3

def get_survey_images_east_maine(doc, i):
    outside_page = i * 2
    inside_page  = i * 2 + 1
    img1 = get_page_crop(doc, outside_page, half="full")
    img2 = get_page_crop(doc, inside_page,  half="full")
    return img1, img2, None  # no third image needed

def process_pdf(pdf_path: str, survey_type: str = "deerfield", api_key: str = None) -> list[dict]:
    """
    Process a batch PDF of surveys.
    
    Args:
        pdf_path: Path to the PDF file
        survey_type: "deerfield" or "weld_re1"
        api_key: Anthropic API key (falls back to env var)
    
    Returns:
        List of flat dicts ready for Excel writing.
    """
    if survey_type not in SUPPORTED_SURVEY_TYPES:
        raise ValueError(f"Unknown survey type '{survey_type}'. Must be one of {SUPPORTED_SURVEY_TYPES}")

    client       = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    system_prompt, user_prompt = load_prompts(survey_type)
    defaults     = load_defaults(survey_type)

    print(f"Loading PDF: {pdf_path}")
    print(f"Survey type: {survey_type}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    if total_pages % 2 != 0:
        print(f"WARNING: Odd number of pages ({total_pages}). Last page will be skipped.")

    num_surveys = total_pages // 2
    print(f"Found {total_pages} pages → {num_surveys} surveys to process")

    results = []
    for i in range(num_surveys):
        survey_num = i + 1
        print(f"  Extracting survey {survey_num}/{num_surveys}...", end=" ", flush=True)

        try:
            # Get correct image crops for this survey type
            if survey_type == "deerfield":
                img1, img2, img3 = get_survey_images_deerfield(doc, i)
            elif survey_type == "weld_re1":
                img1, img2, img3 = get_survey_images_weld_re1(doc, i)

            # Get raw JSON from Claude
            raw_dict = extract_survey(img1, img2, img3, client, system_prompt, user_prompt)

            # Validate with Pydantic (Deerfield only for now)
            if survey_type == "deerfield":
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
                flags = survey.get_flags()
                flat  = survey.to_flat_dict()
            else:
                # For other survey types, use raw dict directly
                flags = []
                flat  = {}
                flat["survey_id"]    = raw_dict.get("survey_id", f"UNKNOWN-{survey_num}")
                flat["likely_voter"] = raw_dict.get("likely_voter", "")
                for key, val in raw_dict.items():
                    if key.startswith("Q") and isinstance(val, dict):
                        v = val.get("value")
                        if isinstance(v, list):
                            flat[key] = ",".join(str(x) for x in v) if v else None
                        else:
                            flat[key] = v
                        if val.get("confidence") == "low":
                            flags.append(key)
                        elif val.get("confidence") == "medium":
                            flags.append(f"{key}?")

            # Apply no-response defaults
            for key, default in defaults.items():
                if flat.get(key) is None and default is not None:
                    flat[key] = default

            # Q skip logic
            skip_q = "Q6" if survey_type == "deerfield" else "Q8"
            q5_key = "Q5" if survey_type == "deerfield" else "Q7"
            if flat.get(q5_key) == 2:
                flat[skip_q] = None

            # Flag remaining nulls
            for key, val in flat.items():
                if val is None and key.startswith("Q"):
                    if key == skip_q and flat.get(q5_key) == 2:
                        continue
                    if key not in flags and f"{key}?" not in flags:
                        flags.append(f"{key}?")

            # Build output dict
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
    """Pass-through for compatibility with writer.py."""
    return result


if __name__ == "__main__":
    import sys
    pdf         = sys.argv[1] if len(sys.argv) > 1 else "files/Sample_survey01.pdf"
    survey_type = sys.argv[2] if len(sys.argv) > 2 else "deerfield"
    results = process_pdf(pdf, survey_type=survey_type)
    print("\n--- EXTRACTED RESULTS ---")
    for r in results:
        print(json.dumps(r, indent=2))
