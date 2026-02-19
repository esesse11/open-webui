"""
AI API Usage Data Processing Module
Processes Claude, OpenAI, and Perplexity API usage data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import json
from typing import Dict, List, Tuple


class APIDataProcessor:
    """Process API usage data from multiple providers"""

    def __init__(self, base_path: str = r"C:\work\project\API_USEAGE"):
        self.base_path = Path(base_path)
        self.claude_path = self.base_path / "claude"
        self.openai_path = self.base_path / "openai"
        self.perplexity_path = self.base_path / "perplexity"

    def load_claude_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load Claude cost and token data"""

        # Load cost data
        cost_files = sorted(self.claude_path.glob("claude_api_cost_*.csv"))
        cost_dfs = []

        for file in cost_files:
            df = pd.read_csv(file)
            cost_dfs.append(df)

        cost_df = pd.concat(cost_dfs, ignore_index=True) if cost_dfs else pd.DataFrame()

        # Load token data
        token_files = sorted(self.claude_path.glob("claude_api_tokens_*.csv"))
        token_dfs = []

        for file in token_files:
            df = pd.read_csv(file)
            token_dfs.append(df)

        token_df = pd.concat(token_dfs, ignore_index=True) if token_dfs else pd.DataFrame()

        # Convert date columns
        if not cost_df.empty:
            cost_df['usage_date_utc'] = pd.to_datetime(cost_df['usage_date_utc'])
            cost_df['date'] = cost_df['usage_date_utc']
            cost_df['provider'] = 'Claude'

        if not token_df.empty:
            token_df['usage_date_utc'] = pd.to_datetime(token_df['usage_date_utc'])
            token_df['date'] = token_df['usage_date_utc']

        return cost_df, token_df

    def load_openai_data(self) -> Dict[str, pd.DataFrame]:
        """Load OpenAI data from various service types"""

        service_types = [
            'completions', 'embeddings', 'images',
            'audio_speeches', 'audio_transcriptions',
            'vector_stores', 'code_interpreter_sessions',
            'file_searches', 'web_searches'
        ]

        openai_data = {}

        for service in service_types:
            files = sorted(self.openai_path.glob(f"{service}_usage_*.csv"))
            dfs = []

            for file in files:
                df = pd.read_csv(file)
                # Check if it has actual data beyond timestamps
                if len(df.columns) > 4:  # More than just timestamp columns
                    dfs.append(df)

            if dfs:
                combined_df = pd.concat(dfs, ignore_index=True)
                if not combined_df.empty and 'start_time_iso' in combined_df.columns:
                    combined_df['date'] = pd.to_datetime(combined_df['start_time_iso'], format='ISO8601').dt.date
                    combined_df['date'] = pd.to_datetime(combined_df['date'])
                    openai_data[service] = combined_df

        return openai_data

    def parse_perplexity_invoice(self, pdf_path: Path) -> Dict:
        """Parse Perplexity invoice PDF"""
        # For now, return manual data from the PDFs we saw
        # In production, would use PyPDF2 or pdfplumber to extract

        invoice_data = {
            'Invoice-LISGSS-00001.pdf': {
                'date': '2025-03-25',
                'amount': 50.00,
                'description': 'Credits purchase'
            },
            'Invoice-LISGSS-00002.pdf': {
                'date': '2025-04-01',
                'period': '2025-03-25 to 2025-03-31',
                'api_requests': 0.12,
                'citation_tokens': 1.30,
                'input_tokens': 0.27,
                'search_queries': 0.62,
                'output_tokens': 0.48,
                'reasoning_tokens': 0.59,
                'total_usage': 3.38,
                'prepaid_applied': -3.38,
                'amount_due': 0.00
            }
        }

        filename = pdf_path.name
        return invoice_data.get(filename, {})

    def load_perplexity_data(self) -> pd.DataFrame:
        """Load Perplexity data - prioritize daily CSV over monthly invoices"""

        perplexity_data = []

        # Check for daily CSV data files in bcave_25 folder
        bcave_path = Path(r"C:\work\project\bcave_25\API_USEAGE\perplexity")

        # Load daily data if available (2503-2509: Mar-Sep 2025)
        daily_files = {
            '2503': bcave_path / '2503_daily_costs_calibrated.csv',
            '2504': bcave_path / '2504_daily_costs_calibrated.csv',
            '2505': bcave_path / '2505_daily_costs_calibrated.csv',
            '2506': bcave_path / '2506_daily_costs_calibrated.csv',
            '2507': bcave_path / '2507_daily_costs_calibrated.csv',
            '2508': bcave_path / '2508_daily_costs_calibrated.csv',
            '2509': bcave_path / '2509_daily_costs_calibrated.csv'
        }

        for month_key, csv_file in daily_files.items():
            if csv_file.exists():
                # Load daily CSV data
                daily_df = pd.read_csv(csv_file)
                daily_df['date'] = pd.to_datetime(daily_df['date']).dt.tz_localize(None)

                # Add each day as a separate record
                for _, row in daily_df.iterrows():
                    perplexity_data.append({
                        'date': row['date'],
                        'amount': row['daily_cost_calibrated'],
                        'provider': 'Perplexity',
                        'source': 'daily_csv'
                    })

        # Load monthly invoice data for months without daily CSV
        json_file = self.perplexity_path / "invoices_data.json"

        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                invoices = json.load(f)

            # Get months that already have daily data
            months_with_daily = set()
            for data in perplexity_data:
                month_key = data['date'].strftime('%Y-%m')
                months_with_daily.add(month_key)

            for invoice in invoices:
                # Only include usage invoices (exclude credits purchases)
                if invoice.get('type') == 'usage':
                    date = invoice.get('date')
                    period = invoice.get('period')
                    total_usage = invoice.get('total_usage', 0)

                    if total_usage > 0:
                        # Try to parse period to get actual usage month
                        usage_month = None
                        if period:
                            # Period format: "May 1 to 31, 2025" or "Mar 25 to 31, 2025"
                            import re
                            period_match = re.search(r'([A-Za-z]{3})\s+\d+\s+to\s+\d+,\s+(\d{4})', period)
                            if period_match:
                                month_name = period_match.group(1)
                                year = period_match.group(2)
                                # Convert month name to number
                                month_num = pd.to_datetime(f"{month_name} {year}", format='%b %Y').strftime('%Y-%m')
                                usage_month = month_num

                        # If no period or couldn't parse, use invoice date
                        if not usage_month and date:
                            invoice_date = pd.to_datetime(date)
                            usage_month = invoice_date.strftime('%Y-%m')

                        # Skip if we already have daily data for this month
                        if usage_month and usage_month not in months_with_daily:
                            # Use period end date (last day of usage month) for the record
                            if period:
                                # Parse end date from period (e.g., "Jul 1 to 31, 2025" -> Jul 31, 2025)
                                period_end = re.search(r'[A-Za-z]{3}\s+\d+\s+to\s+(\d+),\s+(\d{4})', period)
                                period_month = re.search(r'([A-Za-z]{3})\s+\d+\s+to', period)
                                if period_end and period_month:
                                    end_day = period_end.group(1)
                                    year = period_end.group(2)
                                    month_name = period_month.group(1)
                                    record_date = pd.to_datetime(f"{month_name} {end_day}, {year}")
                                elif date:
                                    record_date = pd.to_datetime(date)
                                else:
                                    continue
                            elif date:
                                record_date = pd.to_datetime(date)
                            else:
                                continue  # Skip if no date information

                            perplexity_data.append({
                                'invoice_file': invoice['filename'],
                                'date': record_date,
                                'amount': total_usage,
                                'provider': 'Perplexity',
                                'source': 'invoice'
                            })

        df = pd.DataFrame(perplexity_data) if perplexity_data else pd.DataFrame(columns=['date', 'amount', 'provider'])
        return df

    def load_openai_cost_data(self) -> pd.DataFrame:
        """Load OpenAI cost data from cost_*.csv files"""

        cost_files = sorted(self.openai_path.glob("cost_*.csv"))
        cost_dfs = []

        for file in cost_files:
            try:
                df = pd.read_csv(file)
                # Check if it has cost data
                if not df.empty and 'amount_value' in df.columns:
                    # Filter rows with actual cost data
                    df = df[df['amount_value'].notna()]
                    if not df.empty:
                        cost_dfs.append(df)
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                # Skip empty or malformed files
                continue

        if cost_dfs:
            combined_df = pd.concat(cost_dfs, ignore_index=True)
            if not combined_df.empty and 'start_time_iso' in combined_df.columns:
                combined_df['date'] = pd.to_datetime(combined_df['start_time_iso'], format='ISO8601').dt.date
                combined_df['date'] = pd.to_datetime(combined_df['date'])
                combined_df['cost'] = combined_df['amount_value'].astype(float)
                combined_df['provider'] = 'OpenAI'
                return combined_df[['date', 'cost', 'provider']]

        return pd.DataFrame(columns=['date', 'cost', 'provider'])

    def get_daily_costs_all_providers(self) -> pd.DataFrame:
        """Get daily costs across all providers"""

        # Claude data
        claude_cost_df, _ = self.load_claude_data()

        if not claude_cost_df.empty:
            claude_daily = claude_cost_df.groupby('date').agg({
                'cost_usd': 'sum'
            }).reset_index()
            claude_daily['provider'] = 'Claude'
            claude_daily.rename(columns={'cost_usd': 'cost'}, inplace=True)
        else:
            claude_daily = pd.DataFrame(columns=['date', 'cost', 'provider'])

        # OpenAI data (from cost_*.csv files)
        openai_cost_df = self.load_openai_cost_data()
        if not openai_cost_df.empty:
            openai_daily = openai_cost_df.groupby('date').agg({
                'cost': 'sum'
            }).reset_index()
            openai_daily['provider'] = 'OpenAI'
        else:
            openai_daily = pd.DataFrame(columns=['date', 'cost', 'provider'])

        # Perplexity data
        perplexity_df = self.load_perplexity_data()
        if not perplexity_df.empty:
            perplexity_daily = perplexity_df.rename(columns={'amount': 'cost'})
        else:
            perplexity_daily = pd.DataFrame(columns=['date', 'cost', 'provider'])

        # Combine all
        all_daily = pd.concat([claude_daily, openai_daily, perplexity_daily], ignore_index=True)

        if not all_daily.empty:
            all_daily = all_daily.sort_values('date').reset_index(drop=True)

        return all_daily

    def get_monthly_summary(self) -> pd.DataFrame:
        """Get monthly summary across all providers"""

        daily_costs = self.get_daily_costs_all_providers()

        if daily_costs.empty:
            return pd.DataFrame()

        daily_costs['year_month'] = daily_costs['date'].dt.to_period('M')

        monthly = daily_costs.pivot_table(
            index='year_month',
            columns='provider',
            values='cost',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        monthly['total'] = monthly.select_dtypes(include=[np.number]).sum(axis=1)
        monthly['year_month'] = monthly['year_month'].astype(str)

        # Calculate month-over-month change
        monthly['mom_change'] = monthly['total'].pct_change() * 100

        return monthly

    def get_model_breakdown_claude(self) -> pd.DataFrame:
        """Get Claude model usage breakdown"""

        cost_df, _ = self.load_claude_data()

        if cost_df.empty:
            return pd.DataFrame()

        model_breakdown = cost_df.groupby('model').agg({
            'cost_usd': 'sum'
        }).reset_index()

        model_breakdown = model_breakdown.sort_values('cost_usd', ascending=False)
        model_breakdown['percentage'] = (model_breakdown['cost_usd'] / model_breakdown['cost_usd'].sum()) * 100

        return model_breakdown

    def get_token_analysis_claude(self) -> pd.DataFrame:
        """Get Claude token usage analysis"""

        _, token_df = self.load_claude_data()

        if token_df.empty:
            return pd.DataFrame()

        # Aggregate token usage
        token_summary = token_df.groupby('date').agg({
            'usage_input_tokens_no_cache': 'sum',
            'usage_input_tokens_cache_write_5m': 'sum',
            'usage_input_tokens_cache_read': 'sum',
            'usage_output_tokens': 'sum'
        }).reset_index()

        # Calculate ratios
        token_summary['total_input'] = (
            token_summary['usage_input_tokens_no_cache'] +
            token_summary['usage_input_tokens_cache_write_5m']
        )
        token_summary['input_output_ratio'] = (
            token_summary['total_input'] / token_summary['usage_output_tokens']
        ).replace([np.inf, -np.inf], np.nan)

        # Cache utilization
        token_summary['cache_utilization'] = (
            token_summary['usage_input_tokens_cache_read'] /
            (token_summary['total_input'] + token_summary['usage_input_tokens_cache_read'])
        ).replace([np.inf, -np.inf], np.nan) * 100

        return token_summary

    def detect_anomalies(self, threshold_std: float = 2.0) -> pd.DataFrame:
        """Detect anomalous usage days"""

        daily_costs = self.get_daily_costs_all_providers()

        if daily_costs.empty:
            return pd.DataFrame()

        # Calculate daily total
        daily_total = daily_costs.groupby('date').agg({
            'cost': 'sum'
        }).reset_index()

        # Calculate statistics
        mean_cost = daily_total['cost'].mean()
        std_cost = daily_total['cost'].std()

        # Flag anomalies
        daily_total['is_anomaly'] = np.abs(daily_total['cost'] - mean_cost) > (threshold_std * std_cost)
        daily_total['z_score'] = (daily_total['cost'] - mean_cost) / std_cost

        # Return only anomalies
        anomalies = daily_total[daily_total['is_anomaly']].sort_values('date')

        return anomalies


if __name__ == "__main__":
    # Test the processor
    processor = APIDataProcessor()

    print("Loading Claude data...")
    cost_df, token_df = processor.load_claude_data()
    print(f"Claude cost records: {len(cost_df)}")
    print(f"Claude token records: {len(token_df)}")

    print("\nLoading OpenAI data...")
    openai_data = processor.load_openai_data()
    for service, df in openai_data.items():
        print(f"{service}: {len(df)} records")

    print("\nLoading Perplexity data...")
    perplexity_df = processor.load_perplexity_data()
    print(f"Perplexity records: {len(perplexity_df)}")

    print("\nMonthly summary:")
    monthly = processor.get_monthly_summary()
    print(monthly)

    print("\nAnomalies detected:")
    anomalies = processor.detect_anomalies()
    print(anomalies)
