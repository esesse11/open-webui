"""
Check anomaly dates in detail
"""
import pandas as pd
from data_processor import APIDataProcessor
from datetime import datetime
import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Anomaly dates
anomaly_dates = [
    '2025-07-01',
    '2025-08-01',
    '2025-04-30',
    '2025-06-01'
]

processor = APIDataProcessor()

print("=" * 80)
print("ANOMALY DATES DETAILED ANALYSIS")
print("=" * 80)

for date_str in anomaly_dates:
    date_obj = pd.to_datetime(date_str)
    print(f"\n{'='*80}")
    print(f"📅 DATE: {date_str}")
    print(f"{'='*80}")

    # Check Claude data
    print("\n🔵 CLAUDE API:")
    claude_cost_df, claude_token_df = processor.load_claude_data()

    if not claude_cost_df.empty:
        claude_day = claude_cost_df[claude_cost_df['date'].dt.date == date_obj.date()]
        if not claude_day.empty:
            print(f"  Records found: {len(claude_day)}")
            print(f"  Total cost: ${claude_day['cost_usd'].sum():.2f}")

            # Group by model
            model_summary = claude_day.groupby('model')['cost_usd'].sum().reset_index()
            model_summary = model_summary.sort_values('cost_usd', ascending=False)

            print("\n  Model breakdown:")
            for _, row in model_summary.iterrows():
                print(f"    • {row['model']}: ${row['cost_usd']:.2f}")

            # Check token data for this date
            if not claude_token_df.empty:
                token_day = claude_token_df[claude_token_df['date'].dt.date == date_obj.date()]
                if not token_day.empty:
                    total_input = token_day['usage_input_tokens_no_cache'].sum()
                    total_output = token_day['usage_output_tokens'].sum()
                    print(f"\n  Token usage:")
                    print(f"    Input tokens: {total_input:,.0f}")
                    print(f"    Output tokens: {total_output:,.0f}")
        else:
            print("  No records found")

    # Check OpenAI data
    print("\n🟠 OPENAI API:")
    openai_cost_df = processor.load_openai_cost_data()

    if not openai_cost_df.empty:
        openai_day = openai_cost_df[openai_cost_df['date'].dt.date == date_obj.date()]
        if not openai_day.empty:
            print(f"  Records found: {len(openai_day)}")
            print(f"  Total cost: ${openai_day['cost'].sum():.2f}")

            # Try to load detailed data
            openai_data = processor.load_openai_data()

            for service, df in openai_data.items():
                service_day = df[df['date'].dt.date == date_obj.date()]
                if not service_day.empty:
                    print(f"\n  {service.upper()}:")
                    print(f"    Records: {len(service_day)}")

                    # Check if there's a snapshot_id or model column
                    if 'snapshot_id' in service_day.columns:
                        models = service_day['snapshot_id'].value_counts()
                        print(f"    Models used:")
                        for model, count in models.head(5).items():
                            print(f"      • {model}: {count} requests")

                    # Check for cost information
                    if 'amount_value' in service_day.columns:
                        total = service_day['amount_value'].sum()
                        print(f"    Total cost: ${total:.2f}")
        else:
            print("  No records found")

    # Check Perplexity data
    print("\n🟣 PERPLEXITY API:")
    perplexity_df = processor.load_perplexity_data()

    if not perplexity_df.empty:
        perplexity_day = perplexity_df[perplexity_df['date'].dt.date == date_obj.date()]
        if not perplexity_day.empty:
            print(f"  Records found: {len(perplexity_day)}")
            print(f"  Total cost: ${perplexity_day['amount'].sum():.2f}")

            for _, row in perplexity_day.iterrows():
                print(f"\n  Invoice: {row['invoice_file']}")
                print(f"    Amount: ${row['amount']:.2f}")
        else:
            print("  No records found")

    # Daily total
    print(f"\n{'─'*80}")
    daily_df = processor.get_daily_costs_all_providers()
    day_total = daily_df[daily_df['date'].dt.date == date_obj.date()]

    if not day_total.empty:
        total = day_total['cost'].sum()
        print(f"💰 TOTAL COST FOR {date_str}: ${total:.2f}")

        # Breakdown by provider
        provider_breakdown = day_total.groupby('provider')['cost'].sum()
        print(f"\n  Provider breakdown:")
        for provider, cost in provider_breakdown.items():
            pct = (cost / total * 100) if total > 0 else 0
            print(f"    • {provider}: ${cost:.2f} ({pct:.1f}%)")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
