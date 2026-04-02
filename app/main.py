"""
PhonePe Pulse Dashboard - Main Application
Home page with overview statistics and navigation
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
from typing import Dict
from src.data_loader import DataLoader
from src.visualizations import DashboardVisualizations
from src.utils import (
    get_summary_stats, format_currency, get_available_years, 
    get_available_states, setup_logging
)
from config.settings import config

# Setup logging
setup_logging(config.app.log_level)


def init_session_state():
    """Initialize Streamlit session state variables"""
    if "data_loader" not in st.session_state:
        st.session_state.data_loader = DataLoader()
    
    if "visualizations" not in st.session_state:
        st.session_state.visualizations = DashboardVisualizations(config.GEOJSON_URL)


def load_all_data() -> Dict:
    """Load all data with caching"""
    loader = st.session_state.data_loader
    
    data = {
        'agg_transaction': loader.load_from_json('aggregated', 'transaction'),
        'agg_insurance': loader.load_from_json('aggregated', 'insurance'),
        'agg_user': loader.load_from_json('aggregated', 'user'),
        'map_transaction': loader.load_from_json('map', 'transaction'),
        'map_insurance': loader.load_from_json('map', 'insurance'),
        'map_user': loader.load_from_json('map', 'user'),
        'top_transaction': loader.load_from_json('top', 'transaction'),
        'top_insurance': loader.load_from_json('top', 'insurance'),
        'top_user': loader.load_from_json('top', 'user'),
    }
    
    return data


def display_metrics(data: Dict):
    """Display overview metrics"""
    st.markdown("---")
    st.subheader("📊 Quick Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Transaction metrics
    trans_df = data['agg_transaction']
    if not trans_df.empty:
        trans_stats = get_summary_stats(trans_df, 'Transaction_amount', 'Transaction_count')
        with col1:
            st.metric(
                "Total Transactions",
                f"{trans_stats['total_count']:,}",
                delta=None,
                help="Total transaction count across all states and years"
            )
        with col2:
            st.metric(
                "Transaction Amount",
                format_currency(trans_stats['total_amount']),
                help="Total transaction amount across all states and years"
            )
    
    # User metrics
    user_df = data['agg_user']
    states = get_available_states(user_df)
    with col3:
        st.metric(
            "States Covered",
            len(states),
            help="Number of Indian states with data"
        )
    
    # Data points
    with col4:
        years = get_available_years(trans_df)
        st.metric(
            "Years Available",
            len(years),
            help="Number of years with data"
        )


def display_home_page():
    """Display home page content"""
    st.set_page_config(
        page_title="PhonePe Pulse Dashboard",
        page_icon="💳",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #5f27cd 0%, #00d4ff 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 10px;
        background: rgba(95, 39, 205, 0.08);
        border-left: 4px solid #5f27cd;
        margin: 0.5rem 0;
        backdrop-filter: blur(10px);
    }
    .feature-card h4 {
        color: #5f27cd;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .feature-card p {
        color: inherit;
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.5;
        opacity: 0.85;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>💳 PhonePe Pulse Dashboard</h1>
        <p>Real-time Data Visualization & Exploration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    init_session_state()
    
    # Load all data
    with st.spinner("Loading data..."):
        data = load_all_data()
    
    # Display metrics
    display_metrics(data)
    
    st.markdown("---")
    
    # Features
    st.subheader("✨ Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4>📈 Transaction Analysis</h4>
        <p>Explore transaction data across states, quarters, and payment methods with interactive visualizations.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
        <h4>🛡️ Insurance Insights</h4>
        <p>Analyze insurance transaction patterns and trends across India with detailed breakdowns.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
        <h4>👥 User Demographics</h4>
        <p>Understand user behavior and device preferences across different regions.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Getting Started
    st.subheader("🚀 Getting Started")
    
    st.info("""
    **How to use this dashboard:**
    
    1. **Navigation**: Use the sidebar menu to explore different analysis sections
    2. **Filters**: Each section provides dropdowns to filter data by year, quarter, and state
    3. **Visualizations**: Hover over charts for detailed information
    4. **Insights**: Look for key metrics and trends in each visualization
    
    **Available Sections:**
    - 📊 **Transaction Analysis**: Explore transaction data and trends
    - 🛡️ **Insurance Analysis**: Deep dive into insurance transactions
    - 👥 **User Analysis**: Analyze user device preferences
    - 🗺️ **Geographic Insights**: State-wise data visualization
    """)
    
    st.markdown("---")
    
    # Data Source
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📚 Data Source")
    
    with col2:
        st.info("Data sourced from PhonePe Pulse GitHub Repository")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 1rem 0;">
        <p>PhonePe Pulse Dashboard | Data Visualization & Exploration Platform</p>
        <p>Built with Streamlit, Plotly, and Python</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    display_home_page()
