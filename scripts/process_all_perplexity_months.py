"""
Process all Perplexity monthly CSV data (2503-2509)
Calculate daily costs using calibrated pricing from May 2025
"""
import pandas as pd
from pathlib import Path
import json
import sys
import io

# Set UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load calibrated pricing
pricing_file = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity\calibrated_pricing.json")
with open(pricing_file, 'r', encoding='utf-8') as f:
    pricing_config = json.load(f)
    pricing = pricing_config['pricing']

print("="*80)
print("PROCESSING ALL PERPLEXITY MONTHLY DATA (Mar-Sep 2025)")
print("="*80)
print("\nUsing calibrated pricing from May 2025:")
for cat, price in pricing.items():
    print(f"  {cat:20s}: ${price:.10f}")

def load_perplexity_csv(file_path):
    """Load Perplexity CSV and extract daily data"""
    df = pd.read_csv(file_path)

    # Get value columns
    value_cols = [col for col in df.columns if col.startswith('data_series__values__')]

    # Create result
    result = pd.DataFrame()
    result['date'] = pd.to_datetime(df['data_series__date'], errors='coerce')
    result['total'] = df[value_cols].sum(axis=1)

    # Remove NaN dates
    result = result.dropna(subset=['date'])

    return result

def process_month(base_path, year_month):
    """Process one month of Perplexity data"""

    categories = {
        'api_requests': f'{year_month}-PERP-APIRequests.csv',
        'citation_tokens': f'{year_month}-PERP-CitationTokens.csv',
        'input_tokens': f'{year_month}-PERP-InputTokens.csv',
        'output_tokens': f'{year_month}-PERP-OutputTokens.csv',
        'reasoning_tokens': f'{year_month}-PERP-ReasoningTokens.csv',
        'search_queries': f'{year_month}-PERP-NumberofSearchQueries.csv'
    }

    data = {}

    for category, filename in categories.items():
        file_path = base_path / filename
        if file_path.exists():
            df = load_perplexity_csv(file_path)
            data[category] = df

    if not data:
        return None

    # Merge all categories
    first_category = list(data.keys())[0]
    merged = data[first_category][['date']].copy()

    for category, df in data.items():
        merged = merged.merge(
            df[['date', 'total']].rename(columns={'total': category}),
            on='date',
            how='outer'
        )

    merged = merged.fillna(0)
    merged = merged.sort_values('date').reset_index(drop=True)

    # Calculate costs using calibrated pricing
    for category, price_per_unit in pricing.items():
        if category in merged.columns:
            merged[f'{category}_cost'] = merged[category] * price_per_unit

    # Total daily cost
    cost_cols = [col for col in merged.columns if col.endswith('_cost')]
    merged['daily_cost_calibrated'] = merged[cost_cols].sum(axis=1)

    return merged

# Process all months
base_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")
months = ['2503', '2504', '2505', '2506', '2507', '2508', '2509']
month_names = {
    '2503': 'Mar 2025',
    '2504': 'Apr 2025',
    '2505': 'May 2025',
    '2506': 'Jun 2025',
    '2507': 'Jul 2025',
    '2508': 'Aug 2025',
    '2509': 'Sep 2025'
}

results = {}

print("\n" + "="*80)
print("PROCESSING EACH MONTH:")
print("="*80)

for month_key in months:
    print(f"\nProcessing {month_names[month_key]} ({month_key})...")

    df = process_month(base_path, month_key)

    if df is not None:
        total_cost = df['daily_cost_calibrated'].sum()
        num_days = len(df)
        max_day = df.loc[df['daily_cost_calibrated'].idxmax()]

        print(f"  ✓ {num_days} days processed")
        print(f"  Total cost: ${total_cost:.2f}")
        print(f"  Max day: {max_day['date'].strftime('%Y-%m-%d')} (${max_day['daily_cost_calibrated']:.2f})")

        # Save to CSV
        output_file = base_path / f"{month_key}_daily_costs_calibrated.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file.name}")

        results[month_key] = {
            'month_name': month_names[month_key],
            'total_cost': float(total_cost),
            'num_days': num_days,
            'output_file': output_file.name
        }
    else:
        print(f"  ✗ No data found")

# Summary
print("\n" + "="*80)
print("SUMMARY:")
print("="*80)

total_all_months = sum(r['total_cost'] for r in results.values())

print(f"\nProcessed {len(results)} months")
print(f"Total cost (Mar-Sep 2025): ${total_all_months:.2f}")

print("\nMonthly breakdown:")
for month_key, result in results.items():
    print(f"  {result['month_name']:12s}: ${result['total_cost']:>8.2f} ({result['num_days']:2d} days)")

# Save summary
summary_file = base_path / "all_months_summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nSummary saved to: {summary_file}")
print("="*80)
