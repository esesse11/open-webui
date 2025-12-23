"""
Reprocess all Perplexity months with month-specific pricing calibration
"""
import pandas as pd
from pathlib import Path
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")

# Load extracted invoice data
extracted_file = base_path / "extracted_invoices.json"
with open(extracted_file, 'r', encoding='utf-8') as f:
    extracted_invoices = json.load(f)

# Combine with known invoice data (for Mar, Apr which had $0 in PDF extraction)
invoices = {
    '2503': {
        'api_requests': 0.12,
        'citation_tokens': 1.30,
        'input_tokens': 0.27,
        'output_tokens': 0.48,
        'reasoning_tokens': 0.59,
        'search_queries': 0.62,
        'total': 3.38
    },
    '2504': {
        'api_requests': 1.24,
        'citation_tokens': 5.48,
        'input_tokens': 5.46,
        'output_tokens': 5.52,
        'reasoning_tokens': 21.53,
        'search_queries': 5.88,
        'total': 45.11
    },
}

# Add extracted invoice data (May onwards)
for month_key, inv_data in extracted_invoices.items():
    if month_key not in invoices and inv_data['total'] > 0:
        invoices[month_key] = inv_data

def get_csv_totals(month_key, file_prefixes=None):
    """Get raw CSV totals for a month (handles split files)"""
    categories = {
        'api_requests': 'APIRequests.csv',
        'citation_tokens': 'CitationTokens.csv',
        'input_tokens': 'InputTokens.csv',
        'output_tokens': 'OutputTokens.csv',
        'reasoning_tokens': 'ReasoningTokens.csv',
        'search_queries': 'NumberofSearchQueries.csv'
    }

    totals = {}

    # Handle split files (Oct, Nov)
    if file_prefixes:
        prefixes = file_prefixes
    else:
        prefixes = [month_key]

    for category, filename in categories.items():
        category_total = 0

        for prefix in prefixes:
            file_path = base_path / f"{prefix}-PERP-{filename}"
            if file_path.exists():
                df = pd.read_csv(file_path)
                value_cols = [col for col in df.columns if col.startswith('data_series__values__')]
                category_total += df[value_cols].sum().sum()

        totals[category] = category_total

    return totals

def load_perplexity_csv(file_path):
    """Load Perplexity CSV and extract daily data"""
    df = pd.read_csv(file_path)
    value_cols = [col for col in df.columns if col.startswith('data_series__values__')]
    result = pd.DataFrame()
    result['date'] = pd.to_datetime(df['data_series__date'], errors='coerce')
    result['total'] = df[value_cols].sum(axis=1)
    result = result.dropna(subset=['date'])
    return result

def process_month_with_calibration(month_key, file_prefixes, invoice_data):
    """Process a month with its specific pricing calibration"""

    # Get CSV totals
    csv_totals = get_csv_totals(month_key, file_prefixes)

    # Calculate unit prices
    prices = {}
    for category in ['api_requests', 'citation_tokens', 'input_tokens', 'output_tokens', 'reasoning_tokens', 'search_queries']:
        invoice_amount = invoice_data.get(category, 0)
        csv_total = csv_totals.get(category, 0)

        if csv_total > 0 and invoice_amount > 0:
            prices[category] = invoice_amount / csv_total
        else:
            prices[category] = 0

    # Load daily data from CSV
    categories = {
        'api_requests': 'APIRequests.csv',
        'citation_tokens': 'CitationTokens.csv',
        'input_tokens': 'InputTokens.csv',
        'output_tokens': 'OutputTokens.csv',
        'reasoning_tokens': 'ReasoningTokens.csv',
        'search_queries': 'NumberofSearchQueries.csv'
    }

    all_data = {}

    for prefix in file_prefixes:
        for category, filename in categories.items():
            file_path = base_path / f"{prefix}-PERP-{filename}"
            if file_path.exists():
                df = load_perplexity_csv(file_path)

                if category not in all_data:
                    all_data[category] = df
                else:
                    all_data[category] = pd.concat([all_data[category], df], ignore_index=True)

    # Aggregate by date
    for category in all_data:
        all_data[category] = all_data[category].groupby('date').agg({'total': 'sum'}).reset_index()

    if not all_data:
        return None

    # Merge all categories
    first_category = list(all_data.keys())[0]
    merged = all_data[first_category][['date']].copy()

    for category, df in all_data.items():
        merged = merged.merge(
            df[['date', 'total']].rename(columns={'total': category}),
            on='date',
            how='outer'
        )

    merged = merged.fillna(0)
    merged = merged.sort_values('date').reset_index(drop=True)

    # Calculate costs using month-specific pricing
    for category, price_per_unit in prices.items():
        if category in merged.columns:
            merged[f'{category}_cost'] = merged[category] * price_per_unit

    # Total daily cost
    cost_cols = [col for col in merged.columns if col.endswith('_cost')]
    merged['daily_cost_calibrated'] = merged[cost_cols].sum(axis=1)

    return merged

# Process all months
print("="*80)
print("REPROCESSING ALL MONTHS WITH MONTH-SPECIFIC CALIBRATION")
print("="*80)

month_configs = [
    {'key': '2503', 'prefixes': ['2503'], 'name': 'Mar 2025'},
    {'key': '2504', 'prefixes': ['2504'], 'name': 'Apr 2025'},
    {'key': '2505', 'prefixes': ['2505'], 'name': 'May 2025'},
    {'key': '2506', 'prefixes': ['2506'], 'name': 'Jun 2025'},
    {'key': '2507', 'prefixes': ['2507'], 'name': 'Jul 2025'},
    {'key': '2508', 'prefixes': ['2508'], 'name': 'Aug 2025'},
    {'key': '2509', 'prefixes': ['2509'], 'name': 'Sep 2025'},
    {'key': '2510', 'prefixes': ['251020', '251031'], 'name': 'Oct 2025'},
    {'key': '2511', 'prefixes': ['251120', '251130'], 'name': 'Nov 2025'},
]

results = {}

for config in month_configs:
    month_key = config['key']
    prefixes = config['prefixes']
    month_name = config['name']

    # For Oct and Nov, combine invoice data from split files
    if month_key == '2510':
        invoice_data = {
            category: extracted_invoices.get('251020', {}).get(category, 0) + extracted_invoices.get('251031', {}).get(category, 0)
            for category in ['api_requests', 'citation_tokens', 'input_tokens', 'output_tokens', 'reasoning_tokens', 'search_queries']
        }
        invoice_data['total'] = sum(invoice_data.values())
    elif month_key == '2511':
        invoice_data = {
            category: extracted_invoices.get('251120', {}).get(category, 0) + extracted_invoices.get('251130', {}).get(category, 0)
            for category in ['api_requests', 'citation_tokens', 'input_tokens', 'output_tokens', 'reasoning_tokens', 'search_queries']
        }
        invoice_data['total'] = sum(invoice_data.values())
    else:
        invoice_data = invoices.get(month_key, {})

    if not invoice_data or invoice_data.get('total', 0) == 0:
        print(f"\n⚠ {month_name} ({month_key}): No invoice data, skipping")
        continue

    print(f"\n{month_name} ({month_key}):")
    print(f"  Invoice total: ${invoice_data['total']:.2f}")

    df = process_month_with_calibration(month_key, prefixes, invoice_data)

    if df is not None:
        total_cost = df['daily_cost_calibrated'].sum()
        num_days = len(df)
        max_day = df.loc[df['daily_cost_calibrated'].idxmax()]

        print(f"  ✓ {num_days} days processed")
        print(f"  Calculated total: ${total_cost:.2f}")
        print(f"  Difference: ${total_cost - invoice_data['total']:.2f}")
        print(f"  Max day: {max_day['date'].strftime('%Y-%m-%d')} (${max_day['daily_cost_calibrated']:.2f})")

        # Save to CSV
        output_file = base_path / f"{month_key}_daily_costs_calibrated.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file.name}")

        results[month_key] = {
            'month_name': month_name,
            'invoice_total': float(invoice_data['total']),
            'calculated_total': float(total_cost),
            'num_days': num_days,
            'output_file': output_file.name
        }
    else:
        print(f"  ✗ No data found")

# Summary
print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)

total_all = sum(r['calculated_total'] for r in results.values())

print(f"\nProcessed {len(results)} months")
print(f"Total cost (Mar-Nov 2025): ${total_all:.2f}")

print("\n" + "-" * 80)
print(f"{'Month':<12} {'Invoice':<12} {'Calculated':<12} {'Difference':<12} {'Days':<6} {'Status'}")
print("-" * 80)

for month_key, result in results.items():
    inv_total = result['invoice_total']
    calc_total = result['calculated_total']
    diff = calc_total - inv_total
    pct_diff = (diff / inv_total * 100) if inv_total > 0 else 0

    if abs(pct_diff) < 0.1:
        status = "✓ PERFECT"
    elif abs(pct_diff) < 1:
        status = "✓ OK"
    else:
        status = "⚠ CHECK"

    print(f"{result['month_name']:<12} ${inv_total:>10.2f} ${calc_total:>10.2f} ${diff:>10.2f} {result['num_days']:>5} {status}")

print("="*80)
