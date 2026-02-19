"""
Calibrate Perplexity pricing based on actual invoice data
"""
import pandas as pd
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load invoice data
with open(r'C:\work\project\API_USEAGE\perplexity\invoices_data.json', 'r', encoding='utf-8') as f:
    invoices = json.load(f)

# Load calculated daily data
daily_df = pd.read_csv(r'C:\work\project\bcave_25\API_USEAGE\perplexity\2505_daily_costs.csv')

# Find May 2025 invoice
inv7 = [x for x in invoices if x['filename'] == 'Invoice-LISGSS-00007.pdf'][0]

print("="*80)
print("CALIBRATING PRICING MODEL - May 2025")
print("="*80)

# Calculate totals from CSV
csv_totals = {
    'api_requests': daily_df['api_requests'].sum(),
    'citation_tokens': daily_df['citation_tokens'].sum(),
    'input_tokens': daily_df['input_tokens'].sum(),
    'output_tokens': daily_df['output_tokens'].sum(),
    'reasoning_tokens': daily_df['reasoning_tokens'].sum(),
    'search_queries': daily_df['search_queries'].sum()
}

# Invoice costs
invoice_costs = {
    'api_requests': inv7['api_requests'],
    'citation_tokens': inv7['citation_tokens'],
    'input_tokens': inv7['input_tokens'],
    'output_tokens': inv7['output_tokens'],
    'reasoning_tokens': inv7['reasoning_tokens'],
    'search_queries': inv7['search_queries']
}

print("\n📊 USAGE TOTALS FROM CSV:")
for cat, total in csv_totals.items():
    print(f"  {cat:20s}: {total:>15,.0f}")

print("\n💰 INVOICE COSTS:")
for cat, cost in invoice_costs.items():
    print(f"  {cat:20s}: ${cost:>10.2f}")

print("\n🔍 CALCULATED UNIT PRICES:")
calibrated_pricing = {}
for cat in csv_totals.keys():
    if csv_totals[cat] > 0:
        unit_price = invoice_costs[cat] / csv_totals[cat]
        calibrated_pricing[cat] = unit_price
        print(f"  {cat:20s}: ${unit_price:.10f} per unit")
    else:
        calibrated_pricing[cat] = 0.0
        print(f"  {cat:20s}: $0.00 (no usage)")

# Verify
print("\n✅ VERIFICATION:")
total_calculated = sum(csv_totals[cat] * calibrated_pricing[cat] for cat in csv_totals.keys())
total_invoice = sum(invoice_costs.values())

print(f"  Invoice total: ${total_invoice:.2f}")
print(f"  Calculated total: ${total_calculated:.2f}")
print(f"  Difference: ${abs(total_calculated - total_invoice):.2f}")

# Save calibrated pricing
pricing_config = {
    'source': 'Invoice-LISGSS-00007 (May 2025)',
    'date': '2025-06-01',
    'pricing': calibrated_pricing
}

output_file = r'C:\work\project\bcave_25\API_USEAGE\perplexity\calibrated_pricing.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(pricing_config, f, indent=2, ensure_ascii=False)

print(f"\n💾 Calibrated pricing saved to: {output_file}")
print("="*80)
