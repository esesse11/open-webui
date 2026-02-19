"""Compare calculated costs with invoice data"""
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load invoice data
with open(r'C:\work\project\API_USEAGE\perplexity\invoices_data.json', 'r', encoding='utf-8') as f:
    invoices = json.load(f)

# Find May 2025 invoice (Invoice-LISGSS-00007)
inv7 = [x for x in invoices if x['filename'] == 'Invoice-LISGSS-00007.pdf'][0]

print("="*80)
print("INVOICE VS CALCULATED COMPARISON - May 2025")
print("="*80)

print("\n📄 INVOICE-LISGSS-00007 (May 2025 Usage):")
print(f"  Period: {inv7['period']}")
print(f"  Total Usage: ${inv7['total_usage']:.2f}")
print(f"  Amount Due: ${inv7['amount_due']:.2f}")

print(f"\n  Category Breakdown:")
print(f"    API Requests:     ${inv7['api_requests']:.2f}")
print(f"    Citation Tokens:  ${inv7['citation_tokens']:.2f}")
print(f"    Input Tokens:     ${inv7['input_tokens']:.2f}")
print(f"    Output Tokens:    ${inv7['output_tokens']:.2f}")
print(f"    Reasoning Tokens: ${inv7['reasoning_tokens']:.2f}")
print(f"    Search Queries:   ${inv7['search_queries']:.2f}")

print(f"\n💰 CALCULATED FROM CSV:")
print(f"  Total: $78.00")

print(f"\n📊 DIFFERENCE:")
diff = 78.00 - inv7['total_usage']
diff_pct = (diff / inv7['total_usage'] * 100) if inv7['total_usage'] > 0 else 0
print(f"  ${diff:.2f} ({diff_pct:+.1f}%)")

if abs(diff) > 1:
    print(f"\n⚠️  Large discrepancy detected!")
    print(f"  The pricing model needs adjustment.")
    print(f"  Invoice total: ${inv7['total_usage']:.2f}")
    print(f"  Calculated total: $78.00")
else:
    print(f"\n✅ Pricing model is accurate!")
