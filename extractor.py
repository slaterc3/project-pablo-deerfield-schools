# surveybot/extractor.py
# Core extraction engine — handles all survey types
#
# Survey types and page structures:
#   deerfield  — outside/inside with cross-page Q13-Q17 (crop left/right/full)
#   weld_re1   — inside first, inside split left/right, outside full
#   east_maine — cleanest: two full pages, no cropping needed

import fitz
import anthropic
import base64
import json
import os
import importlib
from models import parse_and_validate

SUPPORTED_SURVEY_TYPES = ["deerfield", "weld_re1", "east_maine", "troy_30c", "oswego"]
# SUPPORTED_SURVEY_TYPES = ["deerfield", "weld_re1", "east_maine", "troy_30c", "oswego"]

def load_survey(survey_type: str):
    """Dynamically load config and prompt from surveys/<survey_type>/."""
    if survey_type not in SUPPORTED_SURVEY_TYPES:
        raise ValueError(f"Unknown survey type '{survey_type}'. Must be one of {SUPPORTED_SURVEY_TYPES}")
    config = importlib.import_module(f"surveys.{survey_type}.config")
    prompt = importlib.import_module(f"surveys.{survey_type}.prompt")
    return config, prompt


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


def get_survey_images(doc: fitz.Document, i: int, survey_type: str) -> tuple:
    """Return (img1, img2, img3) for survey i based on survey type."""
    total_pages = len(doc)

    if survey_type == "deerfield":
        outside      = i * 2
        inside       = i * 2 + 1
        next_outside = (i + 1) * 2
        img1 = get_page_crop(doc, outside, half="right")
        img2 = get_page_crop(doc, inside,  half="full")
        img3 = get_page_crop(doc, next_outside, half="left") if next_outside < total_pages else None
        return img1, img2, img3

    elif survey_type == "weld_re1":
        inside  = i * 2
        outside = i * 2 + 1
        img1 = get_page_crop(doc, inside,  half="left")
        img2 = get_page_crop(doc, inside,  half="right")
        img3 = get_page_crop(doc, outside, half="full")
        return img1, img2, img3
    # added 'oswego' to the list of supported survey types 6/10/26
    elif survey_type in ("east_maine", "troy_30c", "oswego"):
        outside = i * 2
        inside  = i * 2 + 1
        img1 = get_page_crop(doc, outside, half="full")
        img2 = get_page_crop(doc, inside,  half="full")
        return img1, img2, None


def call_claude(img1: bytes, img2: bytes, img3: bytes | None,
                client: anthropic.Anthropic,
                system_prompt: str, user_prompt: str) -> dict:
    """Send images to Claude vision and return raw JSON dict."""
    b64_1 = base64.standard_b64encode(img1).decode("utf-8")
    b64_2 = base64.standard_b64encode(img2).decode("utf-8")

    content = [
        {"type": "text",  "text": "Image 1:"},
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64_1}},
        {"type": "text",  "text": "Image 2:"},
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": b64_2}},
    ]

    if img3 is not None:
        b64_3 = base64.standard_b64encode(img3).decode("utf-8")
        content.append({"type": "text",  "text": "Image 3:"})
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


def flatten_raw(raw_dict: dict) -> tuple[dict, list]:
    """Flatten raw Claude JSON into flat dict + confidence flags."""
    flags = []
    flat  = {
        "survey_id":    raw_dict.get("survey_id", ""),
        "likely_voter": raw_dict.get("likely_voter", ""),
    }
    for key, val in raw_dict.items():
        if not key.startswith("Q"):
            continue
        if isinstance(val, dict):
            v = val.get("value")
            conf = val.get("confidence", "high")
        elif val is None:
            v = None
            conf = "high"
        else:
            # bare int returned by model
            v = val
            conf = "high"
        
        result = ",".join(str(x) for x in v) if isinstance(v, list) else v
        flat[key] = None if result == "" or result == [] else result
        
        if conf == "low":
            flags.append(key)
        elif conf == "medium":
            flags.append(f"{key}?")
    return flat, flags


def process_pdf(pdf_path: str, survey_type: str = "deerfield", api_key: str = None) -> list[dict]:
    """Process a batch PDF — returns list of flat dicts ready for Excel writing."""
    config, prompt_mod = load_survey(survey_type)
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    print(f"Loading PDF: {pdf_path}")
    print(f"Survey type: {survey_type}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    if total_pages % 2 != 0:
        print(f"WARNING: Odd number of pages ({total_pages}). Last page will be skipped.")

    num_surveys = total_pages // 2
    print(f"Found {total_pages} pages → {num_surveys} surveys to process")

    children_q, school_q = config.SKIP_LOGIC

    results = []
    for i in range(num_surveys):
        survey_num = i + 1
        print(f"  Extracting survey {survey_num}/{num_surveys}...", end=" ", flush=True)

        try:
            img1, img2, img3 = get_survey_images(doc, i, survey_type)
            raw_dict = call_claude(img1, img2, img3, client, prompt_mod.SYSTEM_PROMPT, prompt_mod.USER_PROMPT)

            # Deerfield uses Pydantic validation; others use raw flatten
            if survey_type == "deerfield":
                survey, errors = parse_and_validate(raw_dict)
                if errors:
                    print(f"VALIDATION ERROR: {errors}")
                    results.append({
                        "survey_id":    raw_dict.get("survey_id", f"ERROR-{survey_num}"),
                        "likely_voter": raw_dict.get("likely_voter", ""),
                        "_status": "validation_error",
                        "_flags":  str(errors),
                    })
                    continue
                flags = survey.get_flags()
                flat  = survey.to_flat_dict()
            else:
                flat, flags = flatten_raw(raw_dict)

            # Apply no-response defaults
            # for key, default in config.NO_RESPONSE_DEFAULTS.items():
            #     if flat.get(key) is None and default is not None:
            #         flat[key] = default
            # if survey_type == "troy_30c":
            #     if flat.get("Q3") and flat["Q3"] > 4:
            #         flat["Q3"] = 4
            #         if "Q3" not in flags:
            #             flags.append("Q3?")
            # cs 6/9/26 safer version that above:
            if survey_type == "troy_30c":
                q3 = flat.get("Q3")
                if isinstance(q3, int) and q3 > 4:
                    flat["Q3"] = 4
                    if "Q3" not in flags and "Q3?" not in flags:
                        flags.append("Q3?")

            # Skip logic: no children → null school question
            if flat.get(children_q) == 2:
                flat[school_q] = None

            # Flag remaining nulls
            for key, val in flat.items():
                if val is None and key.startswith("Q"):
                    if key == school_q and flat.get(children_q) == 2:
                        continue
                    if key not in flags and f"{key}?" not in flags:
                        flags.append(f"{key}?")

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
                "survey_id":    f"ERROR-{survey_num}",
                "likely_voter": "",
                "_status": "error",
                "_flags":  str(e),
            })

    doc.close()
    return results


def flatten_result(result: dict) -> dict:
    """Pass-through — results are already flat dicts."""
    return result


if __name__ == "__main__":
    import sys
    pdf         = sys.argv[1] if len(sys.argv) > 1 else "files/Sample_survey01.pdf"
    survey_type = sys.argv[2] if len(sys.argv) > 2 else "deerfield"
    results = process_pdf(pdf, survey_type=survey_type)
    print("\n--- EXTRACTED RESULTS ---")
    for r in results:
        print(json.dumps(r, indent=2))
