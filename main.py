"""AI Document Analyzer
Parses unstructured invoice text with Google Gemini and returns
Pydantic-validated JSON.

Usage:
    python main.py                       # processes every .txt file in samples/
    python main.py samples/invoice.txt   # processes one file
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from schemas import Invoice, LineItem

# ---------------------------------------------------------------- configuration
load_dotenv()  # reads GEMINI_API_KEY from the .env file

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
MAX_RETRIES = 3

SAMPLES_DIR = Path("samples")
OUTPUTS_DIR = Path("outputs")

# ---------------------------------------------------------------- few-shot example
EXAMPLE_TEXT = """
INVOICE #INV-1001
From: Bright Stationers
Bill To: Ravi Sharma
Date: March 5, 2026   Due: March 20, 2026
2 x Notebook @ 3.50 = 7.00
1 x Desk Lamp @ 20.00 = 20.00
Subtotal: 27.00   Tax: 2.70   TOTAL: 29.70 USD
"""

EXAMPLE_OUTPUT = Invoice(
    invoice_number="INV-1001",
    vendor_name="Bright Stationers",
    customer_name="Ravi Sharma",
    invoice_date="2026-03-05",
    due_date="2026-03-20",
    currency="USD",
    line_items=[
        LineItem(description="Notebook", quantity=2, unit_price=3.50, total=7.00),
        LineItem(description="Desk Lamp", quantity=1, unit_price=20.00, total=20.00),
    ],
    subtotal=27.00,
    tax=2.70,
    total_amount=29.70,
)


# ---------------------------------------------------------------- prompt template
def build_prompt(document_text: str) -> str:
    """Parameterized prompt template: the document text is the variable."""
    example_json = EXAMPLE_OUTPUT.model_dump_json(indent=2)
    return (
        "You are an expert at extracting structured data from invoices.\n"
        "Read the invoice text and return ONLY a JSON object matching the schema.\n"
        "Rules:\n"
        "- Dates must be in YYYY-MM-DD format.\n"
        "- Use null for any field that is not present in the text.\n"
        "- Numbers must be plain numbers (no currency symbols or commas).\n"
        "- Do not invent information.\n\n"
        "### Example input\n"
        f"{EXAMPLE_TEXT.strip()}\n\n"
        "### Example output\n"
        f"{example_json}\n\n"
        "### Now extract from this invoice\n"
        f"{document_text.strip()}\n"
    )


# ---------------------------------------------------------------- LLM call
def extract_invoice(client: genai.Client, document_text: str) -> Invoice:
    """Call Gemini and return a validated Invoice. Retries on bad JSON."""
    prompt = build_prompt(document_text)
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",  # force JSON output
                    response_schema=Invoice,                # schema guidance
                    temperature=0,                          # consistent results
                ),
            )
            # Strict validation with Pydantic
            return Invoice.model_validate_json(response.text)

        except ValidationError as err:
            last_error = err
            print(f"  Attempt {attempt}: output failed validation, retrying...")
        except json.JSONDecodeError as err:
            last_error = err
            print(f"  Attempt {attempt}: invalid JSON, retrying...")
        except Exception as err:  # network, quota, auth errors, etc.
            last_error = err
            print(f"  Attempt {attempt}: API error: {err}")

    raise RuntimeError(f"Extraction failed after {MAX_RETRIES} attempts: {last_error}")


# ---------------------------------------------------------------- file handling
def process_file(client: genai.Client, path: Path) -> None:
    print(f"Processing {path} ...")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        print("  Skipped: file is empty.")
        return

    invoice = extract_invoice(client, text)

    OUTPUTS_DIR.mkdir(exist_ok=True)
    out_path = OUTPUTS_DIR / f"{path.stem}.json"
    out_path.write_text(invoice.model_dump_json(indent=2), encoding="utf-8")

    print(f"  Saved validated JSON to {out_path}")
    print(invoice.model_dump_json(indent=2))


def main() -> None:
    if not API_KEY:
        sys.exit("Error: GEMINI_API_KEY not found. Add it to your .env file.")

    client = genai.Client(api_key=API_KEY)

    if len(sys.argv) > 1:
        files = [Path(sys.argv[1])]
    else:
        files = sorted(SAMPLES_DIR.glob("*.txt"))

    if not files:
        sys.exit("No input files found. Put a .txt invoice in the samples/ folder.")

    for file in files:
        if not file.exists():
            print(f"File not found: {file}")
            continue
        try:
            process_file(client, file)
        except RuntimeError as err:
            print(f"  Error: {err}")


if __name__ == "__main__":
    main()
