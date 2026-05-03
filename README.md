# SurveyBot — Deerfield 109 Mail Survey Extractor

Extracts handwritten responses from scanned mail surveys into Excel using Claude vision.

## Setup

1. **Install Python 3.11+** (https://python.org)

2. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Set your Anthropic API key:**
   - Mac/Linux: `export ANTHROPIC_API_KEY=sk-ant-...`
   - Windows: `set ANTHROPIC_API_KEY=sk-ant-...`
   - Or create a `.env` file in this folder: `ANTHROPIC_API_KEY=sk-ant-...`

## Usage

```bash
python run.py \
  --pdf path/to/batch_surveys.pdf \
  --template path/to/template.xlsx \
  --output path/to/output.xlsx
```

**Example (sample data):**
```bash
python run.py \
  --pdf Sample_returned_surveys_scanned_in_and_numbered.pdf \
  --template Deerfield_109_template.xlsx
```

## How it works

1. Reads the batch PDF (2 pages per survey: outside + inside)
2. Converts each page pair to images
3. Sends both pages to Claude vision API for extraction
4. Maps responses to the Excel coding scheme
5. Appends rows to the Excel template
6. Flags low-confidence responses in yellow for human review

## Output

- Extracted responses written to Excel (one row per survey)
- **Yellow cells** = low-confidence marks — verify manually
- **Red cells** = extraction failed — enter manually

## PDF format assumption

Surveys must be ordered: `[outside_1, inside_1, outside_2, inside_2, ...]`
i.e., the outside and inside pages of each survey are consecutive.

## Cost estimate

~$0.01-0.03 per survey depending on image size and response complexity.
275 surveys ≈ $3-8 in API costs.
