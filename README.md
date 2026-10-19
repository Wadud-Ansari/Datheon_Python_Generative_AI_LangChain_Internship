# AI Document Analyzer: Datheon Python + Generative AI & LangChain Internship

## Task 1: Structured JSON Extraction with Gemini

A Python script that reads unstructured invoice text, sends it to the Google Gemini API, and returns **strictly validated JSON** using Pydantic.

## Features

- Connects to the Google Gemini API (`google-genai` SDK)
- Parameterized prompt template (the document text is a variable)
- Few-shot example inside the prompt to guide the output format
- Forces JSON output and checks it against a Pydantic schema
- Retries automatically if the model returns invalid output
- Handles a missing API key, API errors and empty files
- Reads every `.txt` file in `samples/` and saves results to `outputs/`

## Project Structure

```
ai-document-analyzer/
├── main.py            # Main script: prompt, API call, validation
├── schemas.py         # Pydantic models (Invoice, LineItem)
├── requirements.txt   # Dependencies
├── .env.example       # Shows which environment variable is needed
├── samples/
│   └── invoice.txt    # Sample input
└── outputs/
    └── invoice.json   # Sample validated output
```

## Setup

1. Clone the repository and open the folder.

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root (see `.env.example`):
   ```
   GEMINI_API_KEY=your_key_here
   ```
   Get a free key from Google AI Studio (https://aistudio.google.com).
   Optional: set `GEMINI_MODEL` to change the model (default is `gemini-3.8-flash`).

## How to Run

Process all files in `samples/`:

```
python main.py
```

Process a single file:

```
python main.py samples/invoice.txt
```

The validated JSON is printed in the terminal and saved to `outputs/<filename>.json`.

## Example

**Input** (`samples/invoice.txt`):

```
INVOICE #A-2045
From: Himalaya Traders
Bill To: Wadud Ansari
Date: 12 Oct 2026   Due: 26 Oct 2026
3 x USB Cable @ 5.00 = 15.00
1 x Keyboard @ 40.00 = 40.00
Subtotal: 55.00  Tax: 5.50  Total: 60.50 USD
```

**Output** (`outputs/invoice.json`):

```json
{
  "invoice_number": "A-2045",
  "vendor_name": "Himalaya Traders",
  "customer_name": "Wadud Ansari",
  "invoice_date": "2026-10-12",
  "due_date": "2026-10-26",
  "currency": "USD",
  "line_items": [
    { "description": "USB Cable", "quantity": 3.0, "unit_price": 5.0, "total": 15.0 },
    { "description": "Keyboard", "quantity": 1.0, "unit_price": 40.0, "total": 40.0 }
  ],
  "subtotal": 55.0,
  "tax": 5.5,
  "total_amount": 60.5
}
```

## How It Works

1. `main.py` loads the API key from `.env`.
2. `build_prompt()` inserts the document text into a template that contains rules and a few-shot example.
3. Gemini is called with JSON output enabled and the `Invoice` schema.
4. The response is validated with `Invoice.model_validate_json()`. If validation fails, the call is retried (up to 3 times).
5. The validated result is saved as a JSON file.

## Tech Stack

- Python 3
- Google Gemini API (`google-genai`)
- Pydantic (schema validation)
- python-dotenv (environment variables)

## Security

The `.env` file holds the API key and is excluded from the repository through `.gitignore`. Never commit real keys.

## Author

Wadud Ansari
