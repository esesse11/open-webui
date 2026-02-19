"""
AI API Usage Analytics Dashboard
Interactive dashboard using Streamlit and Plotly
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_processor import APIDataProcessor

# Page configuration
st.set_page_config(
    page_title="AI API Usage Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Pretendard font and styling
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css');

    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }

    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }

    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    """Load and cache data"""
    processor = APIDataProcessor()
    return processor


def format_currency(value):
    """Format value as USD currency"""
    return f"${value:,.2f}"


def format_percentage(value):
    """Format value as percentage"""
    if pd.isna(value):
        return "N/A"
    return f"{value:+.1f}%"


def apply_pretendard_font(fig):
    """Apply Pretendard font to Plotly figure"""
    fig.update_layout(
        font=dict(
            family="Pretendard, -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif",
            size=12
        )
    )
    return fig


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


def plot_daily_cost_bar(daily_df):
    """Create daily cost bar chart (similar to reference image)"""

    # Aggregate by date
    daily_total = daily_df.groupby('date')['cost'].sum().reset_index()
    daily_total = daily_total.sort_values('date')

    # Create color coding
    colors = create_cost_range_colors(daily_total['cost'])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=daily_total['date'],
        y=daily_total['cost'],
        marker_color=colors,
        text=daily_total['cost'].apply(lambda x: f"${x:.2f}" if x >= 20 else ""),
        textposition='outside',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>비용: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': '일별 크레딧 사용량 (USD)',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        xaxis_title='날짜',
        yaxis_title='사용량 (USD)',
        height=400,
        hovermode='x unified',
        showlegend=True,
        template='plotly_white'
    )

    # Add legend for color ranges
    fig.add_trace(go.Bar(
        x=[None], y=[None],
        marker_color='#d3d3d3',
        name='< $5',
        showlegend=True
    ))
    fig.add_trace(go.Bar(
        x=[None], y=[None],
        marker_color='#808080',
        name='$5 - 20',
        showlegend=True
    ))
    fig.add_trace(go.Bar(
        x=[None], y=[None],
        marker_color='#2c3e50',
        name='≥ $20',
        showlegend=True
    ))

    return apply_pretendard_font(fig)


def plot_daily_cost_with_ma(daily_df):
    """Create daily cost with moving averages (similar to reference image 2)"""

    # Aggregate by date
    daily_total = daily_df.groupby('date')['cost'].sum().reset_index()
    daily_total = daily_total.sort_values('date')

    # Calculate moving averages
    daily_total['ma_7'] = daily_total['cost'].rolling(window=7, min_periods=1).mean()
    daily_total['ma_30'] = daily_total['cost'].rolling(window=30, min_periods=1).mean()

    fig = go.Figure()

    # Bar chart
    colors = create_cost_range_colors(daily_total['cost'])

    fig.add_trace(go.Bar(
        x=daily_total['date'],
        y=daily_total['cost'],
        name='일별 1인당 사용량',
        marker_color=colors,
        opacity=0.6,
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>비용: $%{y:.2f}<extra></extra>'
    ))

    # 7-day MA
    fig.add_trace(go.Scatter(
        x=daily_total['date'],
        y=daily_total['ma_7'],
        name='7일 이동평균',
        line=dict(color='#808080', width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>7일 평균: $%{y:.2f}<extra></extra>'
    ))

    # 30-day MA
    fig.add_trace(go.Scatter(
        x=daily_total['date'],
        y=daily_total['ma_30'],
        name='30일 이동평균',
        line=dict(color='#2c3e50', width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>30일 평균: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': '1인당 일별 크레딧 사용량 추이 분석',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        xaxis_title='날짜',
        yaxis_title='1인당 사용량 (USD)',
        height=450,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        )
    )

    return apply_pretendard_font(fig)


def plot_provider_pie(daily_df):
    """Create provider cost distribution pie chart"""

    provider_total = daily_df.groupby('provider')['cost'].sum().reset_index()
    provider_total = provider_total.sort_values('cost', ascending=False)

    fig = go.Figure(data=[go.Pie(
        labels=provider_total['provider'],
        values=provider_total['cost'],
        hole=0.4,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c']),
        textinfo='label+percent+value',
        texttemplate='%{label}<br>%{percent}<br>$%{value:.2f}',
        hovertemplate='<b>%{label}</b><br>비용: $%{value:.2f}<br>비중: %{percent}<extra></extra>'
    )])

    fig.update_layout(
        title={
            'text': '제공자별 비용 비중',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        height=400,
        template='plotly_white'
    )

    return apply_pretendard_font(fig)


def plot_monthly_trend(monthly_df):
    """Create monthly cost trend chart"""

    fig = go.Figure()

    # Get provider columns (exclude year_month, total, mom_change)
    provider_cols = [col for col in monthly_df.columns if col not in ['year_month', 'total', 'mom_change']]

    # Stacked area chart
    for provider in provider_cols:
        if provider in monthly_df.columns:
            fig.add_trace(go.Scatter(
                x=monthly_df['year_month'],
                y=monthly_df[provider],
                name=provider,
                mode='lines',
                stackgroup='one',
                hovertemplate='<b>%{x}</b><br>%{fullData.name}: $%{y:.2f}<extra></extra>'
            ))

    fig.update_layout(
        title={
            'text': '월별 비용 추이 (누적)',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        xaxis_title='년월',
        yaxis_title='비용 (USD)',
        height=450,
        hovermode='x unified',
        template='plotly_white'
    )

    return apply_pretendard_font(fig)


def plot_weekday_heatmap(daily_df):
    """Create weekday heatmap showing usage patterns"""

    if daily_df.empty:
        return go.Figure()

    # Prepare data
    df = daily_df.copy()
    df['weekday'] = df['date'].dt.day_name()
    df['week'] = df['date'].dt.isocalendar().week

    # Aggregate by weekday and week
    heatmap_data = df.groupby(['week', 'weekday'])['cost'].sum().reset_index()

    # Pivot for heatmap
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = heatmap_data.pivot(index='weekday', columns='week', values='cost')
    pivot = pivot.reindex(weekday_order)

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'],
        colorscale='Blues',
        hovertemplate='주차: %{x}<br>요일: %{y}<br>비용: $%{z:.2f}<extra></extra>',
        colorbar=dict(title='비용 (USD)')
    ))

    fig.update_layout(
        title={
            'text': '요일별 사용 패턴 히트맵',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        xaxis_title='주차',
        yaxis_title='요일',
        height=400,
        template='plotly_white'
    )

    return apply_pretendard_font(fig)


def plot_sunburst_hierarchy(daily_df, cost_df):
    """Create sunburst chart showing provider > model hierarchy"""

    if cost_df.empty:
        return go.Figure()

    # Prepare hierarchical data
    sunburst_data = cost_df.groupby(['provider', 'model'])['cost_usd'].sum().reset_index()
    sunburst_data.columns = ['provider', 'model', 'cost']

    # Create labels and parents for sunburst
    labels = ['Total']
    parents = ['']
    values = [sunburst_data['cost'].sum()]

    # Add providers
    for provider in sunburst_data['provider'].unique():
        labels.append(provider)
        parents.append('Total')
        values.append(sunburst_data[sunburst_data['provider'] == provider]['cost'].sum())

    # Add models
    for _, row in sunburst_data.iterrows():
        labels.append(row['model'])
        parents.append(row['provider'])
        values.append(row['cost'])

    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues='total',
        hovertemplate='<b>%{label}</b><br>비용: $%{value:.2f}<br>비중: %{percentParent}<extra></extra>',
        marker=dict(
            colorscale='Blues',
            cmid=np.mean(values)
        )
    ))

    fig.update_layout(
        title={
            'text': '제공자-모델 계층 구조 (선버스트)',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        height=500,
        template='plotly_white'
    )

    return apply_pretendard_font(fig)


def plot_cost_boxplot(daily_df):
    """Create box plot showing cost distribution by provider"""

    if daily_df.empty:
        return go.Figure()

    fig = go.Figure()

    providers = daily_df['provider'].unique()
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    for idx, provider in enumerate(providers):
        provider_data = daily_df[daily_df['provider'] == provider]['cost']

        fig.add_trace(go.Box(
            y=provider_data,
            name=provider,
            marker_color=colors[idx % len(colors)],
            boxmean='sd',  # Show mean and standard deviation
            hovertemplate='<b>%{fullData.name}</b><br>비용: $%{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        title={
            'text': '제공자별 비용 분포 분석 (박스플롯)',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        yaxis_title='비용 (USD)',
        height=450,
        template='plotly_white',
        showlegend=True
    )

    return apply_pretendard_font(fig)


def plot_budget_gauge(current_cost, budget=1000):
    """Create gauge chart showing budget usage"""

    usage_pct = (current_cost / budget) * 100 if budget > 0 else 0

    # Determine color based on usage
    if usage_pct < 70:
        color = '#2ca02c'  # Green
    elif usage_pct < 90:
        color = '#ff7f0e'  # Orange
    else:
        color = '#d62728'  # Red

    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=current_cost,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': '월 예산 사용률', 'font': {'size': 24, 'family': 'Pretendard'}},
        delta={'reference': budget * 0.8, 'increasing': {'color': color}},
        number={'prefix': '$', 'font': {'size': 40}},
        gauge={
            'axis': {'range': [None, budget], 'tickprefix': '$'},
            'bar': {'color': color},
            'steps': [
                {'range': [0, budget * 0.7], 'color': '#d4edda'},
                {'range': [budget * 0.7, budget * 0.9], 'color': '#fff3cd'},
                {'range': [budget * 0.9, budget], 'color': '#f8d7da'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': budget
            }
        }
    ))

    fig.update_layout(
        height=350,
        template='plotly_white',
        font={'family': 'Pretendard'}
    )

    return apply_pretendard_font(fig)


def plot_waterfall_monthly(monthly_df):
    """Create waterfall chart showing monthly cost changes"""

    if monthly_df.empty or len(monthly_df) < 2:
        return go.Figure()

    # Calculate changes
    months = monthly_df['year_month'].tolist()
    totals = monthly_df['total'].tolist()

    # Prepare waterfall data
    measure = ['relative'] * (len(months) - 1) + ['total']
    x = months[1:]  # Skip first month
    y = [totals[i] - totals[i-1] for i in range(1, len(totals))]
    y.append(totals[-1])  # Add final total

    # Add labels
    text = [f'${val:+.2f}' if val >= 0 else f'-${abs(val):.2f}' for val in y[:-1]]
    text.append(f'${y[-1]:.2f}')

    fig = go.Figure(go.Waterfall(
        name='월간 비용 변화',
        orientation='v',
        measure=measure,
        x=x,
        y=y,
        text=text,
        textposition='outside',
        connector={'line': {'color': 'rgb(63, 63, 63)'}},
        increasing={'marker': {'color': '#2ca02c'}},
        decreasing={'marker': {'color': '#d62728'}},
        totals={'marker': {'color': '#1f77b4'}},
        hovertemplate='<b>%{x}</b><br>변화: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': '월별 비용 증감 분석 (워터폴)',
            'font': {'size': 20, 'family': 'Pretendard'}
        },
        xaxis_title='년월',
        yaxis_title='비용 변화 (USD)',
        height=450,
        template='plotly_white',
        showlegend=False
    )

    return apply_pretendard_font(fig)


def main():
    """Main dashboard function"""

    # Header
    st.markdown('<div class="main-header">📊 AI API 사용량 분석 대시보드</div>', unsafe_allow_html=True)
    st.markdown('---')

    # Load data
    with st.spinner('데이터 로딩 중...'):
        processor = load_data()
        daily_df = processor.get_daily_costs_all_providers()
        monthly_df = processor.get_monthly_summary()
        claude_cost_df, claude_token_df = processor.load_claude_data()
        model_breakdown = processor.get_model_breakdown_claude()
        token_analysis = processor.get_token_analysis_claude()
        anomalies = processor.detect_anomalies()

    # Sidebar filters
    st.sidebar.header('필터 옵션')

    if not daily_df.empty:
        min_date = daily_df['date'].min().date()
        max_date = daily_df['date'].max().date()

        date_range = st.sidebar.date_input(
            '날짜 범위 선택',
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
            daily_df = daily_df[(daily_df['date'].dt.date >= start_date) & (daily_df['date'].dt.date <= end_date)]

        # Provider filter
        providers = st.sidebar.multiselect(
            '제공자 선택',
            options=daily_df['provider'].unique().tolist(),
            default=daily_df['provider'].unique().tolist()
        )

        if providers:
            daily_df = daily_df[daily_df['provider'].isin(providers)]

    # Section 1: Executive Summary
    st.markdown('<div class="section-header">📊 1. 대시보드 개요 (Executive Summary)</div>', unsafe_allow_html=True)

    if not daily_df.empty:
        col1, col2, col3, col4 = st.columns(4)

        total_cost = daily_df['cost'].sum()
        avg_daily_cost = daily_df.groupby('date')['cost'].sum().mean()
        num_days = daily_df['date'].nunique()

        # Calculate MoM change
        if not monthly_df.empty and len(monthly_df) >= 2:
            last_month_total = monthly_df.iloc[-1]['total']
            prev_month_total = monthly_df.iloc[-2]['total']
            mom_change = ((last_month_total - prev_month_total) / prev_month_total) * 100 if prev_month_total > 0 else 0
        else:
            mom_change = 0

        with col1:
            st.metric(
                label="총 누적 비용",
                value=format_currency(total_cost),
                delta=format_percentage(mom_change)
            )

        with col2:
            st.metric(
                label="일평균 비용",
                value=format_currency(avg_daily_cost)
            )

        with col3:
            st.metric(
                label="분석 기간",
                value=f"{num_days}일"
            )

        with col4:
            if not monthly_df.empty:
                current_month_cost = monthly_df.iloc[-1]['total']
                st.metric(
                    label="이번 달 현황",
                    value=format_currency(current_month_cost)
                )

        # Provider breakdown
        st.markdown('#### 제공자별 비용 비중')
        col1, col2 = st.columns([1, 1])

        with col1:
            st.plotly_chart(plot_provider_pie(daily_df), use_container_width=True)

        with col2:
            provider_summary = daily_df.groupby('provider')['cost'].sum().reset_index()
            provider_summary['비중 (%)'] = (provider_summary['cost'] / provider_summary['cost'].sum() * 100).round(2)
            provider_summary['비용 (USD)'] = provider_summary['cost'].apply(lambda x: f"${x:,.2f}")
            provider_summary = provider_summary[['provider', '비용 (USD)', '비중 (%)']].sort_values('비중 (%)', ascending=False)
            provider_summary.columns = ['제공자', '비용 (USD)', '비중 (%)']
            st.write(provider_summary.to_html(index=False, escape=False), unsafe_allow_html=True)

    # Section 2: Time Series Analysis
    st.markdown('---')
    st.markdown('<div class="section-header">📈 2. 시계열 분석 (Time Series Analysis)</div>', unsafe_allow_html=True)

    if not daily_df.empty:
        # Daily cost bar chart
        st.plotly_chart(plot_daily_cost_bar(daily_df), use_container_width=True)

        # Daily cost with moving averages
        st.plotly_chart(plot_daily_cost_with_ma(daily_df), use_container_width=True)

        # Monthly trend
        if not monthly_df.empty:
            st.plotly_chart(plot_monthly_trend(monthly_df), use_container_width=True)

            # Waterfall chart for monthly changes
            st.plotly_chart(plot_waterfall_monthly(monthly_df), use_container_width=True)

    # Section 3: Pattern Analysis
    st.markdown('---')
    st.markdown('<div class="section-header">🔍 3. 패턴 분석 (Pattern Analysis)</div>', unsafe_allow_html=True)

    if not daily_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            # Weekday heatmap
            st.plotly_chart(plot_weekday_heatmap(daily_df), use_container_width=True)

        with col2:
            # Box plot
            st.plotly_chart(plot_cost_boxplot(daily_df), use_container_width=True)

    # Section 4: Hierarchical Analysis
    st.markdown('---')
    st.markdown('<div class="section-header">🌳 4. 계층 분석 (Hierarchical Analysis)</div>', unsafe_allow_html=True)

    if not claude_cost_df.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Sunburst chart
            st.plotly_chart(plot_sunburst_hierarchy(daily_df, claude_cost_df), use_container_width=True)

        with col2:
            st.markdown("#### 💡 선버스트 차트 사용법")
            st.info("""
            - **중앙 클릭**: 상위 레벨로 이동
            - **세그먼트 클릭**: 해당 레벨로 드릴다운
            - **호버**: 상세 정보 확인

            계층 구조:
            1. Total (전체)
            2. Provider (제공자)
            3. Model (모델)
            """)

    # Section 5: Cost Prediction
    st.markdown('---')
    st.markdown('<div class="section-header">💰 5. 비용 예측 및 예산 관리</div>', unsafe_allow_html=True)

    # Budget gauge
    if not monthly_df.empty:
        col1, col2 = st.columns([1, 2])

        with col1:
            # Budget input
            st.markdown("#### 예산 설정")
            monthly_budget = st.number_input(
                "월 예산 (USD)",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100,
                help="월별 예산을 설정하세요"
            )

            current_month_cost = monthly_df.iloc[-1]['total']
            st.plotly_chart(plot_budget_gauge(current_month_cost, monthly_budget), use_container_width=True)

        with col2:
            st.markdown("#### 비용 예측")
            if len(monthly_df) >= 3:
                # Simple linear forecast for next 3 months
                recent_months = monthly_df.tail(3)['total'].values
                avg_growth = np.mean(np.diff(recent_months))

                last_month_cost = monthly_df.iloc[-1]['total']
                forecast = [
                    last_month_cost + avg_growth,
                    last_month_cost + 2 * avg_growth,
                    last_month_cost + 3 * avg_growth
                ]

                col_a, col_b, col_c = st.columns(3)

                with col_a:
                    st.metric(
                        label="다음 달 예상",
                        value=format_currency(max(0, forecast[0])),
                        delta=format_percentage((forecast[0] - last_month_cost) / last_month_cost * 100) if last_month_cost > 0 else "N/A"
                    )

                with col_b:
                    st.metric(
                        label="2개월 후",
                        value=format_currency(max(0, forecast[1]))
                    )

                with col_c:
                    st.metric(
                        label="3개월 후",
                        value=format_currency(max(0, forecast[2]))
                    )

                # Budget warning
                if forecast[0] > monthly_budget:
                    st.warning(f"⚠️ 다음 달 예상 비용(${forecast[0]:.2f})이 예산(${monthly_budget:.2f})을 초과할 것으로 예상됩니다!")
                else:
                    st.success(f"✅ 다음 달 예상 비용이 예산 내에 있습니다.")

    # Section 6: Anomaly Detection
    st.markdown('---')
    st.markdown('<div class="section-header">⚠️ 6. 이상 탐지 및 알림 (Anomaly Detection)</div>', unsafe_allow_html=True)

    if not anomalies.empty:
        st.warning(f"⚠️ {len(anomalies)}개의 이상 사용 패턴이 감지되었습니다!")

        anomalies_display = anomalies.copy()
        anomalies_display['date'] = anomalies_display['date'].dt.strftime('%Y-%m-%d')
        anomalies_display['cost'] = anomalies_display['cost'].apply(lambda x: f"${x:.2f}")
        anomalies_display['z_score'] = anomalies_display['z_score'].round(2)
        anomalies_display.columns = ['날짜', '비용', '이상치', 'Z-점수']

        st.write(anomalies_display.to_html(index=False, escape=False), unsafe_allow_html=True)
    else:
        st.success("✅ 이상 사용 패턴이 감지되지 않았습니다.")

    # Section 7: Detailed Statistics
    st.markdown('---')
    st.markdown('<div class="section-header">📊 7. 상세 통계 테이블 (Detailed Statistics)</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["월별 요약", "모델별 상세 (Claude)"])

    with tab1:
        if not monthly_df.empty:
            monthly_display = monthly_df.copy()
            monthly_display['mom_change'] = monthly_display['mom_change'].apply(format_percentage)

            # Format currency columns
            for col in monthly_display.columns:
                if col not in ['year_month', 'mom_change'] and monthly_display[col].dtype in [np.float64, np.int64]:
                    monthly_display[col] = monthly_display[col].apply(lambda x: f"${x:.2f}")

            monthly_display.columns = ['년월'] + [col if col == 'mom_change' else col for col in monthly_display.columns[1:]]
            if 'mom_change' in monthly_display.columns:
                monthly_display.rename(columns={'mom_change': '전월 대비'}, inplace=True)

            st.write(monthly_display.to_html(index=False, escape=False), unsafe_allow_html=True)

    with tab2:
        if not model_breakdown.empty:
            model_display = model_breakdown.copy()
            model_display['cost_usd'] = model_display['cost_usd'].apply(lambda x: f"${x:.2f}")
            model_display['percentage'] = model_display['percentage'].round(2).astype(str) + '%'
            model_display.columns = ['모델', '비용 (USD)', '비중 (%)']

            st.write(model_display.to_html(index=False, escape=False), unsafe_allow_html=True)

    # Section 8: Insights
    st.markdown('---')
    st.markdown('<div class="section-header">🎯 8. 인사이트 및 권장사항 (Insights & Recommendations)</div>', unsafe_allow_html=True)

    if not daily_df.empty:
        # Generate insights
        insights = []

        # Top cost day
        daily_total = daily_df.groupby('date')['cost'].sum().reset_index()
        if not daily_total.empty:
            max_cost_day = daily_total.loc[daily_total['cost'].idxmax()]
            insights.append(f"📌 가장 높은 비용 발생일: {max_cost_day['date'].strftime('%Y-%m-%d')} (${max_cost_day['cost']:.2f})")

        # Cache usage insight (if cache data available)
        if not token_analysis.empty and 'cache_utilization' in token_analysis.columns:
            recent_cache = token_analysis['cache_utilization'].tail(10).mean()
            if not pd.isna(recent_cache) and recent_cache > 0:
                insights.append(f"💾 최근 캐시 활용률: {recent_cache:.1f}%")

        # Provider dominance
        provider_total = daily_df.groupby('provider')['cost'].sum()
        if not provider_total.empty:
            dominant_provider = provider_total.idxmax()
            dominant_pct = (provider_total.max() / provider_total.sum() * 100)
            insights.append(f"🏆 주요 제공자: {dominant_provider} ({dominant_pct:.1f}%)")

        # Display insights
        for insight in insights:
            st.info(insight)

    # Footer
    st.markdown('---')
    st.markdown(
        '<div style="text-align: center; color: gray; padding: 1rem;">'
        f'마지막 업데이트: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
