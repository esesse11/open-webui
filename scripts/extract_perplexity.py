"""
Extract Perplexity invoice data from PDFs
Only extracts usage invoices (not credit purchases)
"""
import pdfplumber
import re
from pathlib import Path
import json
import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_invoice_data(pdf_path):
    """Extract invoice data from Perplexity PDF"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()

    data = {
        'filename': pdf_path.name,
        'date': None,
        'period': None,
        'api_requests': 0.0,
        'citation_tokens': 0.0,
        'input_tokens': 0.0,
        'output_tokens': 0.0,
        'reasoning_tokens': 0.0,
        'search_queries': 0.0,
        'total_usage': 0.0,
        'amount_due': 0.0
    }

    # Check if this is a credits purchase invoice (skip these)
    if 'Manual credits purchase' in text:
        data['type'] = 'credits_purchase'
        return data

    # Check if this has usage details (API Requests, Tokens, etc.)
    has_usage_details = any(keyword in text for keyword in [
        'API Requests',
        'Citation Tokens',
        'Input Tokens',
        'Output Tokens',
        'Reasoning Tokens',
        'Number of Search Queries'
    ])

    if not has_usage_details:
        data['type'] = 'unknown'
        return data

    # This is a usage invoice
    data['type'] = 'usage'

    # Extract invoice date (format: "Invoice Date Jun 1, 2025")
    date_match = re.search(r'Invoice\s+Date\s+([A-Za-z]{3}\s+\d{1,2},\s+\d{4})', text)
    if date_match:
        from datetime import datetime
        date_str = date_match.group(1)
        try:
            date_obj = datetime.strptime(date_str, '%b %d, %Y')
            data['date'] = date_obj.strftime('%Y-%m-%d')
        except:
            pass

    # Extract usage period (e.g., "Mar 25 – 31, 2025" or "May 1 – 31, 2025")
    period_match = re.search(r'([A-Za-z]{3}\s+\d{1,2})\s*[–-]\s*(\d{1,2},\s+\d{4})', text)
    if period_match:
        data['period'] = f"{period_match.group(1)} to {period_match.group(2)}"

    # Extract each cost category (before "Pre-purchase applied")
    # API Requests
    api_match = re.search(r'API Requests[^$]*?\$([\d.]+)', text)
    if api_match:
        data['api_requests'] = float(api_match.group(1))

    # Citation Tokens
    citation_match = re.search(r'Citation Tokens[^$]*?\$([\d.]+)', text)
    if citation_match:
        data['citation_tokens'] = float(citation_match.group(1))

    # Input Tokens
    input_match = re.search(r'Input Tokens[^$]*?\$([\d.]+)', text)
    if input_match:
        data['input_tokens'] = float(input_match.group(1))

    # Output Tokens
    output_match = re.search(r'Output Tokens[^$]*?\$([\d.]+)', text)
    if output_match:
        data['output_tokens'] = float(output_match.group(1))

    # Reasoning Tokens
    reasoning_match = re.search(r'Reasoning Tokens[^$]*?\$([\d.]+)', text)
    if reasoning_match:
        data['reasoning_tokens'] = float(reasoning_match.group(1))

    # Number of Search Queries
    search_match = re.search(r'Number of Search Queries[^$]*?\$([\d.]+)', text)
    if search_match:
        data['search_queries'] = float(search_match.group(1))

    # Calculate total usage (sum of all categories)
    data['total_usage'] = (
        data['api_requests'] +
        data['citation_tokens'] +
        data['input_tokens'] +
        data['output_tokens'] +
        data['reasoning_tokens'] +
        data['search_queries']
    )

    # Extract amount due (what wasn't covered by credits)
    due_match = re.search(r'Amount\s+due\s+\$\s*([\d.]+)', text)
    if due_match:
        data['amount_due'] = float(due_match.group(1))

    return data

if __name__ == "__main__":
    perplexity_path = Path(r"C:\work\project\API_USEAGE\perplexity")
    pdf_files = sorted(perplexity_path.glob("Invoice-*.pdf"))

    all_data = []
    usage_invoices = []
    credits_invoices = []

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        try:
            data = extract_invoice_data(pdf_file)
            all_data.append(data)

            if data.get('type') == 'usage':
                usage_invoices.append(data)
                print(f"  ✓ Usage Invoice")
                print(f"    Date: {data.get('date')}")
                print(f"    Period: {data.get('period')}")
                print(f"    Total Usage: ${data.get('total_usage', 0):.2f}")
                print(f"    Amount Due: ${data.get('amount_due', 0):.2f}")
            elif data.get('type') == 'credits_purchase':
                credits_invoices.append(data)
                print(f"  ⊗ Credits Purchase (skipped)")
            else:
                print(f"  ? Unknown type")

        except Exception as e:
            print(f"  Error: {e}")

    # Save to JSON
    output_file = perplexity_path / "invoices_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Saved to: {output_file}")
    print(f"Total invoices: {len(all_data)}")
    print(f"  - Usage invoices: {len(usage_invoices)}")
    print(f"  - Credits purchases: {len(credits_invoices)}")
    print(f"  - Unknown: {len(all_data) - len(usage_invoices) - len(credits_invoices)}")

    # Calculate totals for usage invoices only
    total_usage = sum(d['total_usage'] for d in usage_invoices)
    total_due = sum(d['amount_due'] for d in usage_invoices)

    print(f"\n{'='*60}")
    print(f"USAGE SUMMARY (excluding credits purchases):")
    print(f"  Total API Usage: ${total_usage:.2f}")
    print(f"  Amount Due (not covered by credits): ${total_due:.2f}")
