"""
User Analysis Page
Analyze user device preferences and behavior
"""
import streamlit as st
import pandas as pd
from typing import Optional
from src.data_loader import DataLoader
from src.visualizations import DashboardVisualizations
from src.utils import (
    get_available_years, get_available_states,
    validate_dataframe, setup_logging
)
from config.settings import config

# Setup
setup_logging(config.app.log_level)

st.set_page_config(
    page_title="User Analysis",
    page_icon="👥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    padding: 1.5rem;
    border-radius: 10px;
    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
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
    """Analyze user data by year"""
    
    if not validate_dataframe(df):
        st.error("Required columns not found")
        return None
    
    year_data = df[df['Years'] == year]
    
    if year_data.empty:
        st.warning(f"No user data available for year {year}")
        return None
    
    # Aggregate by states
    state_summary = year_data.groupby('States').agg({
        'User_count': 'sum'
    }).reset_index().sort_values('User_count', ascending=False)
    
    # Device brands
    brand_summary = year_data.groupby('Brands').agg({
        'User_count': 'sum'
    }).reset_index().sort_values('User_count', ascending=False)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    total_users = year_data['User_count'].sum()
    avg_users_per_state = total_users / len(state_summary) if not state_summary.empty else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Users</h3>
            <p>{total_users:,}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Brands</h3>
            <p>{len(brand_summary)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Avg per State</h3>
            <p>{avg_users_per_state:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts
    viz = st.session_state.visualizations
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_states = viz.create_bar_chart(
            state_summary.head(15), 'States', 'User_count',
            f"{year} - Top 15 States by Users"
        )
        st.plotly_chart(fig_states, use_container_width=True, key="user_year_state_bar")
    
    with col2:
        fig_brands = viz.create_pie_chart(
            brand_summary.head(10), 'Brands', 'User_count',
            f"{year} - Top Brands Distribution"
        )
        st.plotly_chart(fig_brands, use_container_width=True, key="user_year_brand_pie")
    
    # Geographic visualization
    st.subheader("User Distribution by State")
    
    fig_map = viz.create_choropleth_map(
        state_summary, 'User_count',
        f"{year} - User Distribution Map",
        color_scale="Greens"
    )
    st.plotly_chart(fig_map, use_container_width=True, key="user_year_state_map")
    
    return year_data


def analyze_by_state(df: pd.DataFrame, state: str) -> Optional[pd.DataFrame]:
    """Analyze user data by state"""
    
    state_data = df[df['States'] == state]
    
    if state_data.empty:
        st.warning(f"No user data available for {state}")
        return None
    
    # Aggregate by year
    yearly_data = state_data.groupby('Years').agg({
        'User_count': 'sum'
    }).reset_index().sort_values('Years')
    
    # Brands in this state
    brand_data = state_data.groupby('Brands').agg({
        'User_count': 'sum'
    }).reset_index().sort_values('User_count', ascending=False)
    
    # Charts
    viz = st.session_state.visualizations
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_line = viz.create_line_chart(
            yearly_data, 'Years', 'User_count',
            f"{state} - Yearly User Growth"
        )
        st.plotly_chart(fig_line, use_container_width=True, key="user_state_growth_line")
    
    with col2:
        fig_brands = viz.create_bar_chart(
            brand_data.head(10), 'Brands', 'User_count',
            f"{state} - Top 10 Brands"
        )
        st.plotly_chart(fig_brands, use_container_width=True, key="user_state_brand_bar")
    
    return state_data


def analyze_brands(df: pd.DataFrame) -> None:
    """Analyze brand preferences across India"""
    
    all_brands = df.groupby('Brands').agg({
        'User_count': 'sum'
    }).reset_index().sort_values('User_count', ascending=False)
    
    st.subheader("Device Brand Analysis")
    
    st.info("Top device brands used for PhonePe across India")
    
    viz = st.session_state.visualizations
    
    # Top brands bar chart
    top_brands = all_brands.head(15)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_bar = viz.create_bar_chart(
            top_brands, 'Brands', 'User_count',
            "Top 15 Device Brands"
        )
        st.plotly_chart(fig_bar, use_container_width=True, key="user_brand_bar")
    
    with col2:
        st.dataframe(
            all_brands.head(10),
            use_container_width=True,
            hide_index=True,
            column_config={
                "User_count": st.column_config.NumberColumn(format="%,")
            }
        )


def main():
    """Main page logic"""
    st.title("👥 User Analysis")
    
    st.markdown("Understand user behavior and device preferences across India.")
    
    # Initialize
    init_session_state()
    
    # Load data
    with st.spinner("Loading user data..."):
        loader = st.session_state.data_loader
        df = loader.load_from_json('aggregated', 'user')
    
    if df.empty:
        st.error("No user data available")
        return
    
    # Sidebar filters
    st.sidebar.markdown("### 🔍 Filters")
    
    analysis_type = st.sidebar.radio(
        "Select Analysis Type",
        ["By Year", "By State", "Device Brands"]
    )
    
    if analysis_type == "By Year":
        years = get_available_years(df)
        selected_year = st.sidebar.selectbox("Select Year", years, index=len(years)-1)
        
        analyze_by_year(df, selected_year)
    
    elif analysis_type == "By State":
        states = get_available_states(df)
        selected_state = st.sidebar.selectbox("Select State", states)
        
        analyze_by_state(df, selected_state)
    
    elif analysis_type == "Device Brands":
        analyze_brands(df)


if __name__ == "__main__":
    main()
