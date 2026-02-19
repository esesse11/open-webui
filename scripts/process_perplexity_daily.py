"""
Process Perplexity daily CSV data and calculate daily costs
"""
import pandas as pd
from pathlib import Path
import json
import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_perplexity_csv(file_path):
    """Load Perplexity CSV and extract daily data"""
    df = pd.read_csv(file_path)

    # Get the date column
    date_col = 'data_series__date'

    # Get value columns (exclude metadata columns)
    value_cols = [col for col in df.columns if col.startswith('data_series__values__')]

    # Create a clean dataframe
    result = pd.DataFrame()
    result['date'] = pd.to_datetime(df[date_col], errors='coerce')

    # Sum all value columns for total usage
    result['total'] = df[value_cols].sum(axis=1)

    # Remove rows with NaN dates
    result = result.dropna(subset=['date'])

    return result

def process_all_perplexity_csvs(base_path, year_month='2505'):
    """Process all Perplexity CSV files for a given month"""

    base_path = Path(base_path)

    # Load each category
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
            print(f"✓ Loaded {category}: {len(df)} days")
        else:
            print(f"✗ Missing {category}: {filename}")

    # Merge all categories by date
    if not data:
        print("No data loaded!")
        return None

    # Start with the first category
    first_category = list(data.keys())[0]
    merged = data[first_category][['date']].copy()

    # Add each category's total as a column
    for category, df in data.items():
        merged = merged.merge(
            df[['date', 'total']].rename(columns={'total': category}),
            on='date',
            how='outer'
        )

    # Fill NaN with 0
    merged = merged.fillna(0)

    # Sort by date
    merged = merged.sort_values('date').reset_index(drop=True)

    return merged

def calculate_perplexity_costs(df, pricing=None):
    """Calculate daily costs based on Perplexity pricing

    Based on Perplexity pricing (approximate):
    - API Requests: ~$0.000005 per request
    - Input Tokens: ~$0.0000015 per token
    - Output Tokens: ~$0.000006 per token
    - Citation Tokens: ~$0.00001 per token
    - Reasoning Tokens: ~$0.000003 per token
    - Search Queries: ~$0.00002 per query
    """

    if pricing is None:
        # Default pricing (approximate, adjust based on actual Perplexity pricing)
        pricing = {
            'api_requests': 0.000005,
            'input_tokens': 0.0000015,
            'output_tokens': 0.000006,
            'citation_tokens': 0.00001,
            'reasoning_tokens': 0.000003,
            'search_queries': 0.00002
        }

    result = df.copy()

    # Calculate cost for each category
    for category, price_per_unit in pricing.items():
        if category in result.columns:
            result[f'{category}_cost'] = result[category] * price_per_unit

    # Calculate total daily cost
    cost_cols = [col for col in result.columns if col.endswith('_cost')]
    result['daily_cost'] = result[cost_cols].sum(axis=1)

    return result

if __name__ == "__main__":
    base_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")

    print("="*80)
    print("PROCESSING PERPLEXITY DAILY DATA - May 2025")
    print("="*80)

    # Process 2505 (May 2025) data
    df = process_all_perplexity_csvs(base_path, '2505')

    if df is not None:
        print(f"\n{'='*80}")
        print(f"DATA SUMMARY")
        print(f"{'='*80}")
        print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"Total days: {len(df)}")

        # Calculate costs
        df_with_costs = calculate_perplexity_costs(df)

        print(f"\n{'='*80}")
        print(f"COST SUMMARY")
        print(f"{'='*80}")

        total_cost = df_with_costs['daily_cost'].sum()
        print(f"Total cost for May 2025: ${total_cost:.2f}")

        # Show top 5 days by cost
        print(f"\n{'='*80}")
        print(f"TOP 5 DAYS BY COST")
        print(f"{'='*80}")
        top_days = df_with_costs.nlargest(5, 'daily_cost')[['date', 'daily_cost']]
        for _, row in top_days.iterrows():
            print(f"{row['date'].strftime('%Y-%m-%d')}: ${row['daily_cost']:.2f}")

        # Show daily breakdown
        print(f"\n{'='*80}")
        print(f"DAILY BREAKDOWN (first 10 days)")
        print(f"{'='*80}")

        display_cols = ['date', 'api_requests', 'input_tokens', 'output_tokens',
                       'citation_tokens', 'reasoning_tokens', 'search_queries', 'daily_cost']

        print(df_with_costs[display_cols].head(10).to_string(index=False))

        # Save to CSV
        output_file = base_path / "2505_daily_costs.csv"
        df_with_costs.to_csv(output_file, index=False)
        print(f"\n{'='*80}")
        print(f"Saved to: {output_file}")

        # Also save summary to JSON
        summary = {
            'month': '2025-05',
            'total_cost': float(total_cost),
            'total_days': len(df),
            'date_range': {
                'start': df['date'].min().strftime('%Y-%m-%d'),
                'end': df['date'].max().strftime('%Y-%m-%d')
            },
            'category_totals': {
                'api_requests': float(df['api_requests'].sum()),
                'input_tokens': float(df['input_tokens'].sum()),
                'output_tokens': float(df['output_tokens'].sum()),
                'citation_tokens': float(df['citation_tokens'].sum()),
                'reasoning_tokens': float(df['reasoning_tokens'].sum()),
                'search_queries': float(df['search_queries'].sum())
            },
            'top_days': [
                {
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'cost': float(row['daily_cost'])
                }
                for _, row in df_with_costs.nlargest(5, 'daily_cost').iterrows()
            ]
        }

        summary_file = base_path / "2505_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"Summary saved to: {summary_file}")
        print(f"{'='*80}")
