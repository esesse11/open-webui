"""
Generate HTML Dashboard Report
Creates a standalone HTML report with Plotly charts
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_processor import APIDataProcessor
from datetime import datetime


def create_cost_range_colors(costs):
    """Create color coding based on cost ranges"""
    colors = []
    for cost in costs:
        if cost < 5:
            colors.append('#d3d3d3')  # Light gray
        elif cost < 20:
            colors.append('#808080')  # Gray
        else:
            colors.append('#2c3e50')  # Dark gray/blue
    return colors


def generate_html_dashboard():
    """Generate comprehensive HTML dashboard"""

    # Load data
    processor = APIDataProcessor()
    daily_df = processor.get_daily_costs_all_providers()
    monthly_df = processor.get_monthly_summary()
    model_breakdown = processor.get_model_breakdown_claude()
    anomalies = processor.detect_anomalies()

    # Create HTML
    html_parts = []

    # Header and CSS
    html_parts.append("""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI API 사용량 분석 대시보드</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Noto Sans KR', sans-serif;
            background-color: #f5f7fa;
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1f77b4;
            font-size: 2.5rem;
            margin-bottom: 10px;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 10px;
        }
        h2 {
            color: #333;
            font-size: 1.8rem;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 10px;
            border-left: 4px solid #1f77b4;
        }
        h3 {
            color: #555;
            font-size: 1.3rem;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-card.blue {
            background: linear-gradient(135deg, #1f77b4 0%, #4a9eff 100%);
        }
        .metric-card.green {
            background: linear-gradient(135deg, #2ca02c 0%, #5dd55d 100%);
        }
        .metric-card.orange {
            background: linear-gradient(135deg, #ff7f0e 0%, #ffb347 100%);
        }
        .metric-card.purple {
            background: linear-gradient(135deg, #9467bd 0%, #c5b0d5 100%);
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
        }
        .metric-change {
            font-size: 0.9rem;
            margin-top: 8px;
            opacity: 0.9;
        }
        .chart {
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        th {
            background: linear-gradient(135deg, #1f77b4 0%, #4a9eff 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        tr:hover {
            background-color: #f5f7fa;
        }
        .insight-box {
            background: #e3f2fd;
            border-left: 4px solid #1f77b4;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .warning-box {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .success-box {
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 AI API 사용량 분석 대시보드</h1>
        <p style="color: #666; margin-top: 10px;">Claude, OpenAI, Perplexity API 종합 분석 리포트</p>
""")

    # Section 1: Executive Summary
    if not daily_df.empty:
        total_cost = daily_df['cost'].sum()
        avg_daily_cost = daily_df.groupby('date')['cost'].sum().mean()
        num_days = daily_df['date'].nunique()

        if not monthly_df.empty and len(monthly_df) >= 2:
            last_month_total = monthly_df.iloc[-1]['total']
            prev_month_total = monthly_df.iloc[-2]['total']
            mom_change = ((last_month_total - prev_month_total) / prev_month_total) * 100 if prev_month_total > 0 else 0
        else:
            mom_change = 0

        current_month_cost = monthly_df.iloc[-1]['total'] if not monthly_df.empty else 0

        html_parts.append(f"""
        <h2>📊 1. 대시보드 개요</h2>
        <div class="metrics">
            <div class="metric-card blue">
                <div class="metric-label">총 누적 비용</div>
                <div class="metric-value">${total_cost:,.2f}</div>
                <div class="metric-change">전월 대비: {mom_change:+.1f}%</div>
            </div>
            <div class="metric-card green">
                <div class="metric-label">일평균 비용</div>
                <div class="metric-value">${avg_daily_cost:,.2f}</div>
            </div>
            <div class="metric-card orange">
                <div class="metric-label">분석 기간</div>
                <div class="metric-value">{num_days}일</div>
            </div>
            <div class="metric-card purple">
                <div class="metric-label">이번 달 현황</div>
                <div class="metric-value">${current_month_cost:,.2f}</div>
            </div>
        </div>
""")

    # Chart 1: Daily cost bar chart
    if not daily_df.empty:
        daily_total = daily_df.groupby('date')['cost'].sum().reset_index()
        daily_total = daily_total.sort_values('date')

        colors = create_cost_range_colors(daily_total['cost'])

        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=daily_total['date'],
            y=daily_total['cost'],
            marker_color=colors,
            text=daily_total['cost'].apply(lambda x: f"${x:.2f}" if x >= 20 else ""),
            textposition='outside',
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>비용: $%{y:.2f}<extra></extra>'
        ))

        fig1.update_layout(
            title='일별 크레딧 사용량 (USD)',
            xaxis_title='날짜',
            yaxis_title='사용량 (USD)',
            height=450,
            template='plotly_white',
            font=dict(family='Noto Sans KR')
        )

        html_parts.append(f"""
        <h2>📈 2. 시계열 분석</h2>
        <div class="chart">
            <div id="chart1"></div>
        </div>
        <script>
            var data1 = {fig1.to_json()};
            Plotly.newPlot('chart1', data1.data, data1.layout);
        </script>
""")

        # Chart 2: Daily cost with moving averages
        daily_total['ma_7'] = daily_total['cost'].rolling(window=7, min_periods=1).mean()
        daily_total['ma_30'] = daily_total['cost'].rolling(window=30, min_periods=1).mean()

        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=daily_total['date'],
            y=daily_total['cost'],
            name='일별 사용량',
            marker_color=colors,
            opacity=0.6
        ))
        fig2.add_trace(go.Scatter(
            x=daily_total['date'],
            y=daily_total['ma_7'],
            name='7일 이동평균',
            line=dict(color='#808080', width=2)
        ))
        fig2.add_trace(go.Scatter(
            x=daily_total['date'],
            y=daily_total['ma_30'],
            name='30일 이동평균',
            line=dict(color='#2c3e50', width=2)
        ))

        fig2.update_layout(
            title='1인당 일별 크레딧 사용량 추이 분석',
            xaxis_title='날짜',
            yaxis_title='사용량 (USD)',
            height=450,
            template='plotly_white',
            font=dict(family='Noto Sans KR')
        )

        html_parts.append(f"""
        <div class="chart">
            <div id="chart2"></div>
        </div>
        <script>
            var data2 = {fig2.to_json()};
            Plotly.newPlot('chart2', data2.data, data2.layout);
        </script>
""")

    # Chart 3: Provider pie chart
    if not daily_df.empty:
        provider_total = daily_df.groupby('provider')['cost'].sum().reset_index()

        fig3 = go.Figure(data=[go.Pie(
            labels=provider_total['provider'],
            values=provider_total['cost'],
            hole=0.4,
            marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
        )])

        fig3.update_layout(
            title='제공자별 비용 비중',
            height=450,
            template='plotly_white',
            font=dict(family='Noto Sans KR')
        )

        html_parts.append(f"""
        <div class="chart">
            <div id="chart3"></div>
        </div>
        <script>
            var data3 = {fig3.to_json()};
            Plotly.newPlot('chart3', data3.data, data3.layout);
        </script>
""")

    # Section 6: Anomaly Detection
    html_parts.append('<h2>📉 6. 이상 탐지 및 알림</h2>')

    if not anomalies.empty:
        html_parts.append(f"""
        <div class="warning-box">
            <strong>⚠️ {len(anomalies)}개의 이상 사용 패턴이 감지되었습니다!</strong>
        </div>
        <table>
            <thead>
                <tr>
                    <th>날짜</th>
                    <th>비용 (USD)</th>
                    <th>Z-점수</th>
                </tr>
            </thead>
            <tbody>
""")
        for _, row in anomalies.iterrows():
            html_parts.append(f"""
                <tr>
                    <td>{row['date'].strftime('%Y-%m-%d')}</td>
                    <td>${row['cost']:.2f}</td>
                    <td>{row['z_score']:.2f}</td>
                </tr>
""")
        html_parts.append('</tbody></table>')
    else:
        html_parts.append('<div class="success-box">✅ 이상 사용 패턴이 감지되지 않았습니다.</div>')

    # Section 7: Detailed Statistics
    html_parts.append('<h2>📊 7. 상세 통계 테이블</h2>')

    if not monthly_df.empty:
        html_parts.append("""
        <h3>월별 요약</h3>
        <table>
            <thead>
                <tr>
                    <th>년월</th>
                    <th>Claude (USD)</th>
                    <th>Perplexity (USD)</th>
                    <th>합계 (USD)</th>
                    <th>전월 대비 (%)</th>
                </tr>
            </thead>
            <tbody>
""")
        for _, row in monthly_df.iterrows():
            mom_str = f"{row['mom_change']:+.1f}%" if not pd.isna(row['mom_change']) else "N/A"
            claude_val = row.get('Claude', 0)
            perplexity_val = row.get('Perplexity', 0)

            html_parts.append(f"""
                <tr>
                    <td>{row['year_month']}</td>
                    <td>${claude_val:,.2f}</td>
                    <td>${perplexity_val:,.2f}</td>
                    <td>${row['total']:,.2f}</td>
                    <td>{mom_str}</td>
                </tr>
""")
        html_parts.append('</tbody></table>')

    if not model_breakdown.empty:
        html_parts.append("""
        <h3>모델별 상세 (Claude)</h3>
        <table>
            <thead>
                <tr>
                    <th>모델</th>
                    <th>비용 (USD)</th>
                    <th>비중 (%)</th>
                </tr>
            </thead>
            <tbody>
""")
        for _, row in model_breakdown.iterrows():
            html_parts.append(f"""
                <tr>
                    <td>{row['model']}</td>
                    <td>${row['cost_usd']:,.2f}</td>
                    <td>{row['percentage']:.2f}%</td>
                </tr>
""")
        html_parts.append('</tbody></table>')

    # Section 8: Insights
    html_parts.append('<h2>🎯 8. 인사이트 및 권장사항</h2>')

    if not daily_df.empty:
        daily_total = daily_df.groupby('date')['cost'].sum().reset_index()
        max_cost_day = daily_total.loc[daily_total['cost'].idxmax()]

        html_parts.append(f"""
        <div class="insight-box">
            📌 가장 높은 비용 발생일: {max_cost_day['date'].strftime('%Y-%m-%d')} (${max_cost_day['cost']:.2f})
        </div>
""")

        provider_total = daily_df.groupby('provider')['cost'].sum()
        dominant_provider = provider_total.idxmax()
        dominant_pct = (provider_total.max() / provider_total.sum() * 100)

        html_parts.append(f"""
        <div class="insight-box">
            🏆 주요 제공자: {dominant_provider} ({dominant_pct:.1f}%)
        </div>
""")

    # Footer
    html_parts.append(f"""
        <div class="footer">
            <p>마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>AI API 사용량 분석 대시보드 v1.0</p>
        </div>
    </div>
</body>
</html>
""")

    return ''.join(html_parts)


if __name__ == "__main__":
    print("Generating HTML dashboard...")
    html_content = generate_html_dashboard()

    output_file = r"C:\work\project\api_usage_dashboard.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Dashboard generated successfully: {output_file}")
    print("Open the file in your web browser to view the dashboard.")
