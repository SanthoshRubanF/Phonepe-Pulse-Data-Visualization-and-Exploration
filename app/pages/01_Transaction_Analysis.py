"""
Transaction Analysis Page
Analyze transaction data across states, quarters, and payment methods
"""
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
    page_title="Transaction Analysis",
    page_icon="💳",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    padding: 1.5rem;
    border-radius: 10px;
    background: linear-gradient(135deg, #5f27cd 0%, #00d4ff 100%);
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
    """Analyze and visualize transaction data by year"""
    
    if not validate_dataframe(df, required_columns=['Years', 'States', 'Transaction_count', 'Transaction_amount']):
        st.error("Required columns not found in data")
        return None
    
    year_data = df[df['Years'] == year]
    
    if year_data.empty:
        st.warning(f"No data available for year {year}")
        return None
    
    # Aggregate by states
    state_summary = year_data.groupby('States').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index().sort_values('Transaction_amount', ascending=False)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    stats = get_summary_stats(year_data)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Transactions</h3>
            <p>{stats['total_count']:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Amount</h3>
            <p>₹{stats['total_amount']/10**9:.2f}B</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg Transaction</h3>
            <p>₹{stats['average_amount']:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    viz = st.session_state.visualizations
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_count = viz.create_bar_chart(
            state_summary, 'States', 'Transaction_count',
            f"{year} - Transaction Count by State"
        )
        st.plotly_chart(fig_count, use_container_width=True, key="tx_year_count_chart")
    
    with col2:
        fig_amount = viz.create_bar_chart(
            state_summary, 'States', 'Transaction_amount',
            f"{year} - Transaction Amount by State"
        )
        st.plotly_chart(fig_amount, use_container_width=True, key="tx_year_amount_chart")
    
    # Choropleth map
    st.subheader("Geographic Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_map_count = viz.create_choropleth_map(
            state_summary, 'Transaction_count',
            f"{year} - Transaction Count Map",
            color_scale="Blues"
        )
        st.plotly_chart(fig_map_count, use_container_width=True, key="tx_year_count_map")
    
    with col2:
        fig_map_amount = viz.create_choropleth_map(
            state_summary, 'Transaction_amount',
            f"{year} - Transaction Amount Map",
            color_scale="Purples"
        )
        st.plotly_chart(fig_map_amount, use_container_width=True, key="tx_year_amount_map")
    
    return year_data


def analyze_by_quarter(df: pd.DataFrame, year: int, quarter: int) -> Optional[pd.DataFrame]:
    """Analyze and visualize transaction data by quarter"""
    
    if not validate_dataframe(df):
        st.error("Invalid data")
        return None
    
    quarter_data = df[(df['Years'] == year) & (df['Quarter'] == quarter)]
    
    if quarter_data.empty:
        st.warning(f"No data available for Q{quarter} {year}")
        return None
    
    # Aggregate by states
    state_summary = quarter_data.groupby('States').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index().sort_values('Transaction_amount', ascending=False)
    
    # Display top states
    st.subheader("Top States by Transaction Amount")
    
    top_states = state_summary.head(10).copy()
    top_states['Percentage'] = (top_states['Transaction_amount'] / top_states['Transaction_amount'].sum() * 100).round(2)
    
    st.dataframe(
        top_states,
        use_container_width=True,
        column_config={
            "Transaction_amount": st.column_config.NumberColumn(format="₹%,.0f"),
            "Transaction_count": st.column_config.NumberColumn(format="%,"),
            "Percentage": st.column_config.ProgressColumn(min_value=0, max_value=100)
        }
    )
    
    # Charts
    viz = st.session_state.visualizations
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = viz.create_pie_chart(
            top_states, 'States', 'Transaction_amount',
            f"Q{quarter} {year} - Amount Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="tx_quarter_amount_pie")
    
    with col2:
        fig_bar = viz.create_bar_chart(
            top_states, 'States', 'Transaction_count',
            f"Q{quarter} {year} - Transaction Count"
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="tx_quarter_count_bar")
    
    return quarter_data


def analyze_by_state(df: pd.DataFrame, state: str) -> Optional[pd.DataFrame]:
    """Analyze transaction data for a specific state"""
    
    state_data = df[df['States'] == state]
    
    if state_data.empty:
        st.warning(f"No data available for {state}")
        return None
    
    # Aggregate by year and quarter
    yearly_data = state_data.groupby('Years').agg({
        'Transaction_count': 'sum',
        'Transaction_amount': 'sum'
    }).reset_index().sort_values('Years')
    
    # Charts
    viz = st.session_state.visualizations
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_line_count = viz.create_line_chart(
            yearly_data, 'Years', 'Transaction_count',
            f"{state} - Yearly Transaction Count"
        )
        st.plotly_chart(fig_line_count, use_container_width=True, key="tx_state_count_line")
    
    with col2:
        fig_line_amount = viz.create_line_chart(
            yearly_data, 'Years', 'Transaction_amount',
            f"{state} - Yearly Transaction Amount"
        )
        st.plotly_chart(fig_line_amount, use_container_width=True, key="tx_state_amount_line")
    
    return state_data


def main():
    """Main page logic"""
    st.title("💳 Transaction Analysis")
    
    st.markdown("Explore transaction data across India with detailed breakdowns by state, quarter, and time period.")
    
    # Initialize
    init_session_state()
    
    # Load data
    with st.spinner("Loading transaction data..."):
        loader = st.session_state.data_loader
        df = loader.load_from_json('aggregated', 'transaction')
    
    if df.empty:
        st.error("No transaction data available")
        return
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["By Year", "By Quarter", "By State", "By Transaction Type"]
    )
    
    if analysis_type == "By Year":
        years = get_available_years(df)
        selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
        
        analyze_by_year(df, selected_year)
    
    elif analysis_type == "By Quarter":
        years = get_available_years(df)
        selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
        
        quarters = get_available_quarters(df[df['Years'] == selected_year])
        selected_quarter = st.sidebar.selectbox("Select Quarter", quarters)
        
        analyze_by_quarter(df, selected_year, selected_quarter)
    
    elif analysis_type == "By State":
        states = get_available_states(df)
        selected_state = st.sidebar.selectbox("Select State", states)
        
        analyze_by_state(df, selected_state)
    
    elif analysis_type == "By Transaction Type":
        trans_types = sorted(df['Transaction_type'].unique())
        selected_type = st.sidebar.selectbox("Select Transaction Type", trans_types)
        
        trans_data = df[df['Transaction_type'] == selected_type]
        
        st.subheader(f"{selected_type} Transactions")
        
        yearly_summary = trans_data.groupby('Years').agg({
            'Transaction_count': 'sum',
            'Transaction_amount': 'sum'
        }).reset_index().sort_values('Years')
        
        viz = st.session_state.visualizations
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = viz.create_line_chart(
                yearly_summary, 'Years', 'Transaction_amount',
                f"{selected_type} - Yearly Amount Trend"
            )
            st.plotly_chart(fig, use_container_width=True, key="tx_type_amount_line")
        
        with col2:
            fig = viz.create_line_chart(
                yearly_summary, 'Years', 'Transaction_count',
                f"{selected_type} - Yearly Count Trend"
            )
            st.plotly_chart(fig, use_container_width=True, key="tx_type_count_line")


if __name__ == "__main__":
    main()
