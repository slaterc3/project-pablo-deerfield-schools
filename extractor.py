# surveybot/extractor.py
# Core extraction engine: PDF → images → Claude vision → JSON

import fitz  # pymupdf
import anthropic
import base64
import json
import os
from pathlib import Path
from prompt import SYSTEM_PROMPT, USER_PROMPT


def pdf_to_page_images(pdf_path: str, dpi: int = 150, max_width: int = 2000) -> list[bytes]:
    """
    Convert all pages of a PDF to PNG image bytes.
    Resizes to max_width to keep under Claude API 5MB image limit.
    """
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        # Resize if too wide
        if pix.width > max_width:
            scale = max_width / pix.width
            mat2 = fitz.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72 * scale, dpi / 72 * scale))
        images.append(pix.tobytes("png"))
    doc.close()
    return images


def extract_survey(outside_img: bytes, inside_img: bytes, client: anthropic.Anthropic) -> dict:
    """
    Send two page images to Claude vision and return extracted JSON.
    outside_img: bytes of the outside page (Q1-Q4, Q13-Q17)
    inside_img:  bytes of the inside page (Q5-Q12)
    """
    outside_b64 = base64.standard_b64encode(outside_img).decode("utf-8")
    inside_b64  = base64.standard_b64encode(inside_img).decode("utf-8")

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Image 1 - OUTSIDE page (Q1-Q4, Q13-Q17):"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": outside_b64}},
                    {"type": "text", "text": "Image 2 - INSIDE page (Q5-Q12):"},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": inside_b64}},
                    {"type": "text", "text": USER_PROMPT}
                ]
            }
        ]
    )

    raw = message.content[0].text.strip()
    # Strip markdown fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def process_pdf(pdf_path: str, api_key: str = None) -> list[dict]:
    """
    Process a batch PDF of surveys.
    Returns a list of extracted survey dicts (one per survey).
    Assumes pages are ordered: [outside_1, inside_1, outside_2, inside_2, ...]
    """
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    
    print(f"Loading PDF: {pdf_path}")
    images = pdf_to_page_images(pdf_path)
    total_pages = len(images)
    
    if total_pages % 2 != 0:
        print(f"WARNING: Odd number of pages ({total_pages}). Last page will be skipped.")
    
    num_surveys = total_pages // 2
    print(f"Found {total_pages} pages → {num_surveys} surveys to process")
    
    results = []
    for i in range(num_surveys):
        outside_img = images[i * 2]
        inside_img  = images[i * 2 + 1]
        survey_num  = i + 1

        print(f"  Extracting survey {survey_num}/{num_surveys}...", end=" ", flush=True)
        try:
            result = extract_survey(outside_img, inside_img, client)
            result["_page_index"] = i
            result["_status"] = "ok"

            # Flag any low-confidence responses
            low_conf = [k for k, v in result.items()
                       if isinstance(v, dict) and v.get("confidence") == "low"]
            if low_conf:
                result["_flags"] = low_conf
                print(f"⚠️  flagged: {low_conf}")
            else:
                print("✓")

            results.append(result)

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "survey_id": f"ERROR-{survey_num}",
                "_page_index": i,
                "_status": "error",
                "_error": str(e)
            })

    return results


def flatten_result(result: dict) -> dict:
    """
    Flatten extracted JSON into a simple key→value dict for Excel writing.
    Strips confidence wrappers, converts multi-select arrays to comma strings.
    """
    flat = {
        "survey_id": result.get("survey_id", ""),
        "likely_voter": result.get("likely_voter", ""),
        "_status": result.get("_status", ""),
        "_flags": ",".join(result.get("_flags", [])),
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
    # Quick test against the sample PDF
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/uploads/Sample_returned_surveys_scanned_in_and_numbered.pdf"
    
    results = process_pdf(pdf)
    
    print("\n--- EXTRACTED RESULTS ---")
    for r in results:
        flat = flatten_result(r)
        print(json.dumps(flat, indent=2))
