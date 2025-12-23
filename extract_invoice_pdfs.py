"""
Extract invoice data from Perplexity PDF files
"""
import pdfplumber
from pathlib import Path
import re
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")

# Find all invoice PDFs
invoice_pdfs = sorted(base_path.glob("*Invoice*.pdf"))

print("="*80)
print("EXTRACTING INVOICE DATA FROM PDFs")
print("="*80)
print(f"\nFound {len(invoice_pdfs)} invoice PDF files\n")

all_invoice_data = {}

for pdf_file in invoice_pdfs:
    print(f"\nProcessing: {pdf_file.name}")
    print("-" * 60)

    try:
        with pdfplumber.open(pdf_file) as pdf:
            # Extract text from all pages
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"

            # Parse invoice data
            invoice_data = {
                'filename': pdf_file.name,
                'api_requests': 0.0,
                'citation_tokens': 0.0,
                'input_tokens': 0.0,
                'output_tokens': 0.0,
                'reasoning_tokens': 0.0,
                'search_queries': 0.0,
                'total': 0.0
            }

            # Look for line items with dollar amounts
            # Pattern: "Item Name $X.XX" or "Item Name X.XX"

            # Try to find specific line items
            patterns = {
                'api_requests': r'API\s+[Rr]equests?\s+[\$]?([\d,]+\.?\d*)',
                'citation_tokens': r'Citation\s+[Tt]okens?\s+[\$]?([\d,]+\.?\d*)',
                'input_tokens': r'Input\s+[Tt]okens?\s+[\$]?([\d,]+\.?\d*)',
                'output_tokens': r'Output\s+[Tt]okens?\s+[\$]?([\d,]+\.?\d*)',
                'reasoning_tokens': r'Reasoning\s+[Tt]okens?\s+[\$]?([\d,]+\.?\d*)',
                'search_queries': r'(?:Number\s+of\s+)?Search\s+[Qq]uer(?:ies|y)\s+[\$]?([\d,]+\.?\d*)',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    value_str = match.group(1).replace(',', '')
                    invoice_data[key] = float(value_str)
                    print(f"  {key:20s}: ${invoice_data[key]:.2f}")

            # Find total
            # Look for patterns like "Total", "Amount Due", "Usage Total"
            total_patterns = [
                r'Total\s+Usage\s+[\$]?([\d,]+\.?\d*)',
                r'Usage\s+Total\s+[\$]?([\d,]+\.?\d*)',
                r'Total\s+[\$]?([\d,]+\.?\d*)',
                r'Amount\s+Due\s+[\$]?([\d,]+\.?\d*)',
            ]

            for pattern in total_patterns:
                match = re.search(pattern, full_text, re.IGNORECASE)
                if match:
                    value_str = match.group(1).replace(',', '')
                    invoice_data['total'] = float(value_str)
                    print(f"  {'Total':<20s}: ${invoice_data['total']:.2f}")
                    break

            # Calculate total from line items if not found
            if invoice_data['total'] == 0.0:
                calculated_total = sum([
                    invoice_data['api_requests'],
                    invoice_data['citation_tokens'],
                    invoice_data['input_tokens'],
                    invoice_data['output_tokens'],
                    invoice_data['reasoning_tokens'],
                    invoice_data['search_queries']
                ])
                invoice_data['total'] = calculated_total
                print(f"  {'Total (calculated)':<20s}: ${invoice_data['total']:.2f}")

            # Determine month from filename
            # Examples: 2509-PERP-Invoice-LISGSS.pdf, 251020-PERP-Invoice-LISGSS.pdf
            filename = pdf_file.stem
            if filename.startswith('2509'):
                month_key = '2509'
            elif filename.startswith('2510'):
                if '251020' in filename:
                    month_key = '251020'
                else:
                    month_key = '251031'
            elif filename.startswith('2511'):
                if '251120' in filename:
                    month_key = '251120'
                else:
                    month_key = '251130'
            else:
                # Try to extract YYMM format
                match = re.search(r'(\d{4})', filename)
                if match:
                    month_key = match.group(1)
                else:
                    month_key = filename

            all_invoice_data[month_key] = invoice_data

            print(f"  → Assigned to month: {month_key}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

# Save extracted data
output_file = base_path / "extracted_invoices.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_invoice_data, f, indent=2, ensure_ascii=False)

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nExtracted data from {len(all_invoice_data)} invoices")
print(f"Saved to: {output_file}")

# Display summary table
print("\n" + "="*80)
print("INVOICE TOTALS BY MONTH")
print("="*80)
print(f"{'Month Key':<15} {'Total Amount':<15} {'Status'}")
print("-" * 80)

month_names = {
    '2503': 'Mar 2025',
    '2504': 'Apr 2025',
    '2505': 'May 2025',
    '2506': 'Jun 2025',
    '2507': 'Jul 2025',
    '2508': 'Aug 2025',
    '2509': 'Sep 2025',
    '251020': 'Oct 1-20',
    '251031': 'Oct 21-31',
    '251120': 'Nov 1-20',
    '251130': 'Nov 21-30'
}

for month_key in sorted(all_invoice_data.keys()):
    invoice = all_invoice_data[month_key]
    total = invoice['total']
    status = "✓ OK" if total > 0 else "⚠ No data"
    month_name = month_names.get(month_key, month_key)
    print(f"{month_name:<15} ${total:>12.2f} {status}")

print("="*80)
