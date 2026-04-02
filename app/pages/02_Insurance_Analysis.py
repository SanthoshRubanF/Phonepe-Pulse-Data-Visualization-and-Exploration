"""
Insurance Analysis Page
Analyze insurance transaction data across states and time periods
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from typing import Optional
from src.data_loader import DataLoader
from src.visualizations import DashboardVisualizations
from src.utils import (
    get_available_years, get_available_quarters, get_available_states,
    get_summary_stats, validate_dataframe, setup_logging
)
from config.settings import config

# Setup
setup_logging(config.app.log_level)

st.set_page_config(
    page_title="Insurance Analysis",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    padding: 1.5rem;
    border-radius: 10px;
    background: linear-gradient(135deg, #ff6b35 0%, #ffa94d 100%);
    color: white;
    text-align: center;
}
.metric-card h3 {
    margin: 0 0 0.5rem 0;
    font-size: 0.9rem;
    opacity: 0.9;
}
.metric-card p {
    margin: 0;
    font-size: 1.8rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state"""
    if "data_loader" not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    if "visualizations" not in st.session_state:
        st.session_state.visualizations = DashboardVisualizations(config.GEOJSON_URL)


def analyze_by_year(df: pd.DataFrame, year: int) -> Optional[pd.DataFrame]:
    """Analyze insurance data by year"""
    
    if not validate_dataframe(df):
        st.error("Required columns not found")
        return None
    
    year_data = df[df['Years'] == year]
    
    if year_data.empty:
        st.warning(f"No insurance data available for year {year}")
        return None
    
    # Aggregate by states
    state_summary = year_data.groupby('States').agg({
        'Insurance_count': 'sum',
        'Insurance_amount': 'sum'
    }).reset_index().sort_values('Insurance_amount', ascending=False)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    stats = get_summary_stats(year_data, 'Insurance_amount', 'Insurance_count')
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Policies</h3>
            <p>{stats['total_count']:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Premium Amount</h3>
            <p>₹{stats['total_amount']/10**9:.2f}B</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Premium</h3>
            <p>₹{stats['average_amount']:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    viz = st.session_state.visualizations
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_count = viz.create_bar_chart(
            state_summary, 'States', 'Insurance_count',
            f"{year} - Insurance Count by State"
        )
        st.plotly_chart(fig_count, use_container_width=True, key="ins_year_count_chart")
    
    with col2:
        fig_amount = viz.create_bar_chart(
            state_summary, 'States', 'Insurance_amount',
            f"{year} - Insurance Amount by State"
        )
        st.plotly_chart(fig_amount, use_container_width=True, key="ins_year_amount_chart")
    
    # Geographic visualization
    st.subheader("Geographic Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_map = viz.create_choropleth_map(
            state_summary, 'Insurance_count',
            f"{year} - Insurance Count Map",
            color_scale="Oranges"
        )
        st.plotly_chart(fig_map, use_container_width=True, key="ins_year_count_map")
    
    with col2:
        fig_map = viz.create_choropleth_map(
            state_summary, 'Insurance_amount',
            f"{year} - Insurance Amount Map",
            color_scale="YlOrRd"
        )
        st.plotly_chart(fig_map, use_container_width=True, key="ins_year_amount_map")
    
    return year_data


def analyze_by_state(df: pd.DataFrame, state: str) -> Optional[pd.DataFrame]:
    """Analyze insurance data by state"""
    
    state_data = df[df['States'] == state]
    
    if state_data.empty:
        st.warning(f"No insurance data available for {state}")
        return None
    
    # Aggregate by year
    yearly_data = state_data.groupby('Years').agg({
        'Insurance_count': 'sum',
        'Insurance_amount': 'sum'
    }).reset_index().sort_values('Years')
    
    # Insurance types
    insurance_types = state_data.groupby('Insurance_type').agg({
        'Insurance_count': 'sum',
        'Insurance_amount': 'sum'
    }).reset_index().sort_values('Insurance_amount', ascending=False)
    
    # Charts
    viz = st.session_state.visualizations
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_line = viz.create_line_chart(
            yearly_data, 'Years', 'Insurance_amount',
            f"{state} - Yearly Premium Trend"
        )
        st.plotly_chart(fig_line, use_container_width=True, key="ins_state_premium_line")
    
    with col2:
        fig_pie = viz.create_pie_chart(
            insurance_types, 'Insurance_type', 'Insurance_amount',
            f"{state} - Insurance Type Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="ins_state_type_pie")
    
    return state_data


def main():
    """Main page logic"""
    st.title("🛡️ Insurance Analysis")
    
    st.markdown("Deep dive into insurance transaction data across India.")
    
    # Initialize
    init_session_state()
    
    # Load data
    with st.spinner("Loading insurance data..."):
        loader = st.session_state.data_loader
        df = loader.load_from_json('aggregated', 'insurance')
    
    if df.empty:
        st.error("No insurance data available")
        return
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["By Year", "By State", "By Insurance Type"]
    )
    
    if analysis_type == "By Year":
        years = get_available_years(df)
        selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
        
        analyze_by_year(df, selected_year)
    
    elif analysis_type == "By State":
        states = get_available_states(df)
        selected_state = st.sidebar.selectbox("Select State", states)
        
        analyze_by_state(df, selected_state)
    
    elif analysis_type == "By Insurance Type":
        insurance_types = sorted(df['Insurance_type'].unique())
        selected_type = st.sidebar.selectbox("Select Insurance Type", insurance_types)
        
        type_data = df[df['Insurance_type'] == selected_type]
        
        st.subheader(f"{selected_type} Insurance Analysis")
        
        yearly_summary = type_data.groupby('Years').agg({
            'Insurance_count': 'sum',
            'Insurance_amount': 'sum'
        }).reset_index().sort_values('Years')
        
        state_summary = type_data.groupby('States').agg({
            'Insurance_count': 'sum',
            'Insurance_amount': 'sum'
        }).reset_index().sort_values('Insurance_amount', ascending=False).head(10)
        
        viz = st.session_state.visualizations
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = viz.create_line_chart(
                yearly_summary, 'Years', 'Insurance_amount',
                f"{selected_type} - Yearly Trend"
            )
            st.plotly_chart(fig, use_container_width=True, key="ins_type_yearly_line")
        
        with col2:
            fig = viz.create_bar_chart(
                state_summary, 'States', 'Insurance_amount',
                f"{selected_type} - Top 10 States"
            )
            st.plotly_chart(fig, use_container_width=True, key="ins_type_state_bar")


if __name__ == "__main__":
    main()
