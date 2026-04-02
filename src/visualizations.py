"""
Visualization Module for PhonePe Pulse Dashboard
Handles all chart and visualization creation
"""
import logging
from typing import Optional, Dict, Tuple, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.utils import fetch_geojson, validate_dataframe, get_summary_stats, format_currency

logger = logging.getLogger(__name__)


class DashboardVisualizations:
    """Handle all visualizations for the dashboard"""
    
    # Color schemes matching PhonePe Pulse design
    COLOR_SCHEME_PRIMARY = "#5f27cd"  # PhonePe Purple
    COLOR_SCHEME_SECONDARY = "#00d4ff"  # Light Blue
    COLOR_SCALES = {
        'transaction_amount': px.colors.sequential.Purples,
        'transaction_count': px.colors.sequential.Blues,
        'user_count': px.colors.sequential.Greens,
        'insurance': px.colors.sequential.Oranges,
    }
    
    def __init__(self, geojson_url: str):
        """Initialize visualizations with GeoJSON URL"""
        self.geojson_url = geojson_url
        self.geojson_data = None
    
    def _get_geojson(self) -> Optional[Dict]:
        """Fetch and cache GeoJSON data"""
        if self.geojson_data is None:
            self.geojson_data = fetch_geojson(self.geojson_url)
        return self.geojson_data
    
    def create_metric_card(self, label: str, value: float, delta: Optional[float] = None, 
                          delta_color: str = "normal") -> go.Figure:
        """
        Create a metric card visualization.
        
        Args:
            label: Label for the metric
            value: Numeric value
            delta: Change from previous period
            delta_color: Color for delta indicator
            
        Returns:
            Plotly figure
        """
        fig = go.Figure(go.Indicator(
            mode="number+delta",
            value=value,
            title={"text": label},
            delta={"reference": value * 0.9, "relative": False, "valueformat": ".0f"},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        
        fig.update_layout(
            height=150,
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(size=14),
            paper_bgcolor="rgba(240, 240, 250, 1)",
            plot_bgcolor="rgba(240, 240, 250, 1)"
        )
        
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame, x_col: str, y_col: str, 
                        title: str, color_scheme: str = None) -> go.Figure:
        """
        Create a bar chart.
        
        Args:
            df: Input dataframe
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
            color_scheme: Color scheme to use
            
        Returns:
            Plotly figure
        """
        if not validate_dataframe(df, required_columns=[x_col, y_col]):
            return go.Figure().add_annotation(text="No data available")
        
        color = color_scheme or self.COLOR_SCALES.get('transaction_amount', px.colors.sequential.Purples)
        
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col,
            title=title,
            color=y_col,
            color_continuous_scale=color,
            height=500,
            labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()}
        )
        
        fig.update_layout(
            hovermode='x unified',
            showlegend=False,
            font=dict(size=11),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    def create_choropleth_map(self, df: pd.DataFrame, color_col: str, 
                             title: str, color_scale: str = "Viridis") -> go.Figure:
        """
        Create a choropleth map of India.
        
        Args:
            df: Input dataframe with 'States' column
            color_col: Column to use for coloring
            title: Map title
            color_scale: Plotly color scale
            
        Returns:
            Plotly figure
        """
        if not validate_dataframe(df, required_columns=['States', color_col]):
            return go.Figure().add_annotation(text="No data available")
        
        geojson = self._get_geojson()
        if geojson is None:
            logger.warning("GeoJSON data not available, creating simple map")
            return go.Figure().add_annotation(text="Map data unavailable")
        
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations='States',
            featureidkey='properties.ST_NM',
            color=color_col,
            color_continuous_scale=color_scale,
            hover_name='States',
            title=title,
            scope='asia',
            height=600,
            labels={color_col: color_col.replace('_', ' ').title()}
        )
        
        fig.update_geos(
            visible=False,
            projection_type="mercator",
            lataxis_range=[8, 35],
            lonaxis_range=[68, 97]
        )
        
        fig.update_layout(
            font=dict(size=11),
            margin=dict(l=0, r=0, t=80, b=0),
            coloraxis_colorbar=dict(thickness=20)
        )
        
        return fig
    
    def create_pie_chart(self, df: pd.DataFrame, names_col: str, values_col: str,
                        title: str) -> go.Figure:
        """
        Create a pie chart.
        
        Args:
            df: Input dataframe
            names_col: Column for pie slice labels
            values_col: Column for pie slice values
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not validate_dataframe(df, required_columns=[names_col, values_col]):
            return go.Figure().add_annotation(text="No data available")
        
        fig = px.pie(
            df,
            names=names_col,
            values=values_col,
            title=title,
            height=500
        )
        
        fig.update_layout(
            font=dict(size=11),
            margin=dict(l=20, r=20, t=80, b=20)
        )
        
        return fig
    
    def create_line_chart(self, df: pd.DataFrame, x_col: str, y_col: str,
                         title: str, group_col: Optional[str] = None) -> go.Figure:
        """
        Create a line chart.
        
        Args:
            df: Input dataframe
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
            group_col: Optional column for grouping lines
            
        Returns:
            Plotly figure
        """
        if not validate_dataframe(df, required_columns=[x_col, y_col]):
            return go.Figure().add_annotation(text="No data available")
        
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=group_col,
            title=title,
            height=500,
            markers=True
        )
        
        fig.update_layout(
            hovermode='x unified',
            font=dict(size=11),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    def create_scatter_chart(self, df: pd.DataFrame, x_col: str, y_col: str,
                            title: str, size_col: Optional[str] = None,
                            color_col: Optional[str] = None) -> go.Figure:
        """
        Create a scatter chart.
        
        Args:
            df: Input dataframe
            x_col: Column for x-axis
            y_col: Column for y-axis
            title: Chart title
            size_col: Optional column for bubble size
            color_col: Optional column for color
            
        Returns:
            Plotly figure
        """
        if not validate_dataframe(df, required_columns=[x_col, y_col]):
            return go.Figure().add_annotation(text="No data available")
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            size=size_col,
            color=color_col,
            title=title,
            height=500
        )
        
        fig.update_layout(
            hovermode='closest',
            font=dict(size=11),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    def create_comparison_bars(self, df: pd.DataFrame, category_col: str,
                              value_cols: List[str], title: str) -> go.Figure:
        """
        Create a grouped bar chart for comparing multiple values.
        
        Args:
            df: Input dataframe
            category_col: Column with categories
            value_cols: List of columns to compare
            title: Chart title
            
        Returns:
            Plotly figure
        """
        if not validate_dataframe(df, required_columns=[category_col] + value_cols):
            return go.Figure().add_annotation(text="No data available")
        
        fig = go.Figure()
        
        for col in value_cols:
            fig.add_trace(go.Bar(
                x=df[category_col],
                y=df[col],
                name=col.replace('_', ' ').title()
            ))
        
        fig.update_layout(
            title=title,
            barmode='group',
            height=500,
            hovermode='x unified',
            font=dict(size=11),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig


# Helper functions for quick visualization creation
def create_visualization_dashboard(df: pd.DataFrame, metric_cols: List[str],
                                  chart_type: str = 'bar') -> Dict:
    """
    Create a complete visualization dashboard.
    
    Args:
        df: Input dataframe
        metric_cols: Columns to visualize
        chart_type: Type of chart ('bar', 'pie', 'line')
        
    Returns:
        Dictionary with visualizations
    """
    visualizations = {}
    
    if df.empty:
        return visualizations
    
    viz = DashboardVisualizations("")
    
    for col in metric_cols:
        if col not in df.columns:
            continue
        
        try:
            if chart_type == 'bar':
                visualizations[col] = viz.create_bar_chart(df, 'States', col, col.title())
            elif chart_type == 'pie':
                visualizations[col] = viz.create_pie_chart(df, 'States', col, col.title())
            elif chart_type == 'line':
                visualizations[col] = viz.create_line_chart(df, 'Years', col, col.title())
        except Exception as e:
            logger.error(f"Error creating visualization for {col}: {str(e)}")
    
    return visualizations
