"""
Verify Perplexity data: Compare invoice totals with CSV calculated totals
"""
import pandas as pd
from pathlib import Path
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")

# Load invoices data
invoices_file = Path(r"C:\work\project\API_USEAGE\perplexity\invoices_data.json")
with open(invoices_file, 'r', encoding='utf-8') as f:
    invoices = json.load(f)

# Extract usage invoices by month
invoice_totals = {}
for inv in invoices:
    if inv.get('type') == 'usage' and inv.get('total_usage', 0) > 0:
        period = inv.get('period')
        total = inv['total_usage']

        if period:
            # Parse period to month
            if 'Mar' in period:
                invoice_totals['2503'] = {'invoice': total, 'period': period, 'file': inv['filename']}
            elif 'Apr' in period:
                invoice_totals['2504'] = {'invoice': total, 'period': period, 'file': inv['filename']}
            elif 'May' in period:
                invoice_totals['2505'] = {'invoice': total, 'period': period, 'file': inv['filename']}
            elif 'Jun' in period:
                invoice_totals['2506'] = {'invoice': total, 'period': period, 'file': inv['filename']}
            elif 'Jul' in period:
                invoice_totals['2507'] = {'invoice': total, 'period': period, 'file': inv['filename']}
            elif 'Aug' in period:
                invoice_totals['2508'] = {'invoice': total, 'period': period, 'file': inv['filename']}

# Check for September, October, November invoices in PDF files
# We'll need to check the PDF files or look for additional invoice data
print("="*80)
print("PERPLEXITY DATA VERIFICATION")
print("="*80)

# Load CSV calculated totals
csv_files = {
    '2503': '2503_daily_costs_calibrated.csv',
    '2504': '2504_daily_costs_calibrated.csv',
    '2505': '2505_daily_costs_calibrated.csv',
    '2506': '2506_daily_costs_calibrated.csv',
    '2507': '2507_daily_costs_calibrated.csv',
    '2508': '2508_daily_costs_calibrated.csv',
    '2509': '2509_daily_costs_calibrated.csv',
    '2510': '2510_daily_costs_calibrated.csv',
    '2511': '2511_daily_costs_calibrated.csv',
}

month_names = {
    '2503': 'Mar 2025',
    '2504': 'Apr 2025',
    '2505': 'May 2025',
    '2506': 'Jun 2025',
    '2507': 'Jul 2025',
    '2508': 'Aug 2025',
    '2509': 'Sep 2025',
    '2510': 'Oct 2025',
    '2511': 'Nov 2025'
}

print("\nCOMPARISON: Invoice vs CSV Calculated")
print("-" * 80)
print(f"{'Month':<12} {'Invoice':<12} {'CSV Calc':<12} {'Difference':<12} {'% Diff':<10} {'Status'}")
print("-" * 80)

for month_key, csv_filename in csv_files.items():
    csv_path = base_path / csv_filename

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        csv_total = df['daily_cost_calibrated'].sum()

        invoice_total = invoice_totals.get(month_key, {}).get('invoice', None)

        if invoice_total is not None:
            diff = csv_total - invoice_total
            pct_diff = (diff / invoice_total) * 100 if invoice_total > 0 else 0

            # Status check: within 1% is OK, within 5% is warning, >5% is error
            if abs(pct_diff) < 1:
                status = "✓ OK"
            elif abs(pct_diff) < 5:
                status = "⚠ WARNING"
            else:
                status = "✗ ERROR"

            print(f"{month_names[month_key]:<12} ${invoice_total:>10.2f} ${csv_total:>10.2f} ${diff:>10.2f} {pct_diff:>8.1f}% {status}")
        else:
            print(f"{month_names[month_key]:<12} {'N/A':>12} ${csv_total:>10.2f} {'N/A':>12} {'N/A':>10} ⚠ NO INVOICE")
    else:
        print(f"{month_names[month_key]:<12} {'N/A':>12} {'NOT FOUND':>12} {'N/A':>12} {'N/A':>10} ✗ NO CSV")

print("-" * 80)

# Additional analysis: Check for invoice files
print("\n" + "="*80)
print("INVOICE FILES CHECK")
print("="*80)
print("\nLooking for invoice PDF files...")

invoice_pdfs = sorted(base_path.glob("*Invoice*.pdf"))
print(f"\nFound {len(invoice_pdfs)} invoice PDF files:")
for pdf in invoice_pdfs:
    print(f"  - {pdf.name}")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

print("""
For months marked as ERROR or NO INVOICE:
1. Check if invoice PDF exists and extract total_usage manually
2. Verify CSV data completeness (check for missing days)
3. Verify pricing calibration is correct for all categories
4. Check if CSV files include all usage categories

For months within 1% difference: Data is accurate
For months 1-5% difference: Minor discrepancy, acceptable
For months >5% difference: Significant issue, needs investigation
""")
