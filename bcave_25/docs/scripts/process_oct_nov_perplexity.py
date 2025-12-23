"""
Process October and November 2025 Perplexity data (split files)
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
print("PROCESSING PERPLEXITY DATA FOR OCTOBER & NOVEMBER 2025")
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

def process_split_month(base_path, file_prefixes, month_name):
    """Process a month that's split into multiple files"""

    categories = {
        'api_requests': 'APIRequests.csv',
        'citation_tokens': 'CitationTokens.csv',
        'input_tokens': 'InputTokens.csv',
        'output_tokens': 'OutputTokens.csv',
        'reasoning_tokens': 'ReasoningTokens.csv',
        'search_queries': 'NumberofSearchQueries.csv'
    }

    all_data = {}

    # Process each file prefix (e.g., 251020, 251031)
    for prefix in file_prefixes:
        for category, filename in categories.items():
            file_path = base_path / f"{prefix}-PERP-{filename}"
            if file_path.exists():
                df = load_perplexity_csv(file_path)

                # Accumulate data for this category
                if category not in all_data:
                    all_data[category] = df
                else:
                    # Append new data
                    all_data[category] = pd.concat([all_data[category], df], ignore_index=True)

    # Aggregate by date to remove duplicates and sum values
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

    # Calculate costs using calibrated pricing
    for category, price_per_unit in pricing.items():
        if category in merged.columns:
            merged[f'{category}_cost'] = merged[category] * price_per_unit

    # Total daily cost
    cost_cols = [col for col in merged.columns if col.endswith('_cost')]
    merged['daily_cost_calibrated'] = merged[cost_cols].sum(axis=1)

    return merged

# Process months
base_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")

months = [
    {
        'prefixes': ['251020', '251031'],
        'key': '2510',
        'name': 'Oct 2025'
    },
    {
        'prefixes': ['251120', '251130'],
        'key': '2511',
        'name': 'Nov 2025'
    }
]

results = {}

print("\n" + "="*80)
print("PROCESSING EACH MONTH:")
print("="*80)

for month_info in months:
    print(f"\nProcessing {month_info['name']} ({month_info['key']})...")
    print(f"  File prefixes: {', '.join(month_info['prefixes'])}")

    df = process_split_month(base_path, month_info['prefixes'], month_info['name'])

    if df is not None:
        total_cost = df['daily_cost_calibrated'].sum()
        num_days = len(df)
        max_day = df.loc[df['daily_cost_calibrated'].idxmax()]

        print(f"  ✓ {num_days} days processed")
        print(f"  Total cost: ${total_cost:.2f}")
        print(f"  Max day: {max_day['date'].strftime('%Y-%m-%d')} (${max_day['daily_cost_calibrated']:.2f})")

        # Save to CSV
        output_file = base_path / f"{month_info['key']}_daily_costs_calibrated.csv"
        df.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file.name}")

        results[month_info['key']] = {
            'month_name': month_info['name'],
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

total_both_months = sum(r['total_cost'] for r in results.values())

print(f"\nProcessed {len(results)} months")
print(f"Total cost (Oct-Nov 2025): ${total_both_months:.2f}")

print("\nMonthly breakdown:")
for month_key, result in results.items():
    print(f"  {result['month_name']:12s}: ${result['total_cost']:>8.2f} ({result['num_days']:2d} days)")

# Save summary
summary_file = base_path / "oct_nov_summary.json"
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nSummary saved to: {summary_file}")
print("="*80)
