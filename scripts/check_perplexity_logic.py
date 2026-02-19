"""Check Perplexity data loading logic"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from data_processor import APIDataProcessor

p = APIDataProcessor()
df = p.load_perplexity_data()

print("="*80)
print("PERPLEXITY DATA LOADING CHECK")
print("="*80)

print(f"\nTotal records: {len(df)}")

# Show all records with details
print("\n" + "="*80)
print("ALL RECORDS:")
print("="*80)
for idx, row in df.sort_values('date').iterrows():
    source_label = "📅 CSV" if row.get('source') == 'daily_csv' else "📄 INV"
    print(f"{source_label} {row['date'].strftime('%Y-%m-%d')}: ${row['amount']:>8.2f}")

# Group by month
print("\n" + "="*80)
print("MONTHLY TOTALS:")
print("="*80)
monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum()
for month, total in monthly.items():
    print(f"{month}: ${total:.2f}")

# Check for duplicates in August
print("\n" + "="*80)
print("AUGUST 2025 DETAILS:")
print("="*80)
aug_df = df[df['date'].dt.month == 8]
if not aug_df.empty:
    print(aug_df[['date', 'amount', 'source']].to_string())
    print(f"\nTotal August cost: ${aug_df['amount'].sum():.2f}")
else:
    print("No August records found")
