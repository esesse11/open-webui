"""
Recalibrate pricing for each month individually
Extract actual unit prices from invoice amounts / CSV raw totals
"""
import pandas as pd
from pathlib import Path
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")

# Invoice data by month
invoices = {
    '2503': {  # Mar 25-31
        'api_requests': 0.12,
        'citation_tokens': 1.30,
        'input_tokens': 0.27,
        'output_tokens': 0.48,
        'reasoning_tokens': 0.59,
        'search_queries': 0.62,
        'total': 3.38
    },
    '2504': {  # Apr 1-30
        'api_requests': 1.24,
        'citation_tokens': 5.48,
        'input_tokens': 5.46,
        'output_tokens': 5.52,
        'reasoning_tokens': 21.53,
        'search_queries': 5.88,
        'total': 45.11
    },
    '2505': {  # May 1-31
        'api_requests': 1.16,
        'citation_tokens': 1.92,
        'input_tokens': 3.84,
        'output_tokens': 2.99,
        'reasoning_tokens': 22.08,
        'search_queries': 7.30,
        'total': 39.29
    },
    '2506': {  # Jun 1-30
        'api_requests': 1.75,
        'citation_tokens': 4.20,
        'input_tokens': 11.40,
        'output_tokens': 5.97,
        'reasoning_tokens': 51.21,
        'search_queries': 19.23,
        'total': 93.76
    },
    '2507': {  # Jul 1-31
        'api_requests': 4.98,
        'citation_tokens': 3.05,
        'input_tokens': 35.88,
        'output_tokens': 7.91,
        'reasoning_tokens': 29.31,
        'search_queries': 7.24,
        'total': 88.37
    },
    '2508': {  # Aug 1-31
        'api_requests': 2.97,
        'citation_tokens': 2.32,
        'input_tokens': 22.11,
        'output_tokens': 4.50,
        'reasoning_tokens': 27.11,
        'search_queries': 5.26,
        'total': 64.27
    }
}

def get_csv_totals(month_key):
    """Get raw CSV totals for a month"""
    categories = {
        'api_requests': f'{month_key}-PERP-APIRequests.csv',
        'citation_tokens': f'{month_key}-PERP-CitationTokens.csv',
        'input_tokens': f'{month_key}-PERP-InputTokens.csv',
        'output_tokens': f'{month_key}-PERP-OutputTokens.csv',
        'reasoning_tokens': f'{month_key}-PERP-ReasoningTokens.csv',
        'search_queries': f'{month_key}-PERP-NumberofSearchQueries.csv'
    }

    totals = {}
    for category, filename in categories.items():
        file_path = base_path / filename
        if file_path.exists():
            df = pd.read_csv(file_path)
            value_cols = [col for col in df.columns if col.startswith('data_series__values__')]
            total = df[value_cols].sum().sum()
            totals[category] = total
        else:
            totals[category] = 0

    return totals

print("="*80)
print("RECALIBRATING PRICING FOR EACH MONTH")
print("="*80)

month_names = {
    '2503': 'Mar 2025',
    '2504': 'Apr 2025',
    '2505': 'May 2025',
    '2506': 'Jun 2025',
    '2507': 'Jul 2025',
    '2508': 'Aug 2025'
}

all_prices = {}

for month_key, invoice in invoices.items():
    print(f"\n{month_names[month_key]} ({month_key}):")
    print("-" * 60)

    csv_totals = get_csv_totals(month_key)
    prices = {}

    for category in ['api_requests', 'citation_tokens', 'input_tokens', 'output_tokens', 'reasoning_tokens', 'search_queries']:
        invoice_amount = invoice.get(category, 0)
        csv_total = csv_totals.get(category, 0)

        if csv_total > 0 and invoice_amount > 0:
            unit_price = invoice_amount / csv_total
            prices[category] = unit_price
            print(f"  {category:20s}: ${invoice_amount:>8.2f} / {csv_total:>15,.0f} = ${unit_price:.10f}")
        else:
            prices[category] = 0
            print(f"  {category:20s}: ${invoice_amount:>8.2f} / {csv_total:>15,.0f} = N/A")

    all_prices[month_key] = prices

    # Verify calculation
    calculated_total = sum(csv_totals.get(cat, 0) * prices.get(cat, 0) for cat in prices)
    print(f"\n  Invoice total: ${invoice['total']:.2f}")
    print(f"  Calculated:    ${calculated_total:.2f}")
    print(f"  Difference:    ${calculated_total - invoice['total']:.2f}")

# Summary: Check if prices are consistent
print("\n" + "="*80)
print("PRICE COMPARISON ACROSS MONTHS")
print("="*80)

categories = ['api_requests', 'citation_tokens', 'input_tokens', 'output_tokens', 'reasoning_tokens', 'search_queries']

for category in categories:
    print(f"\n{category.upper().replace('_', ' ')}:")
    prices_for_category = {}
    for month_key in month_names:
        price = all_prices[month_key].get(category, 0)
        if price > 0:
            prices_for_category[month_names[month_key]] = price
            print(f"  {month_names[month_key]}: ${price:.10f}")

    if len(prices_for_category) > 0:
        min_price = min(prices_for_category.values())
        max_price = max(prices_for_category.values())
        ratio = max_price / min_price if min_price > 0 else 0
        print(f"  → Range: ${min_price:.10f} to ${max_price:.10f} (ratio: {ratio:.1f}x)")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("""
If prices vary significantly across months (>10x ratio), then:
- CSV data is in different units/scales per month
- Each month needs its own calibration
- Cannot use a single pricing model

If prices are consistent (<2x ratio), then:
- CSV data units are consistent
- Can use a single pricing model
- Current discrepancies are due to other issues
""")
