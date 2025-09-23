"""Interactive globe plots using Plotly."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from .base import ColorScheme

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
    PlotlyFig = go.Figure
except ImportError:
    HAS_PLOTLY = False
    go = None
    px = None
    PlotlyFig = type('Figure', (), {})


class GlobeRiskPlot:
    """Interactive globe for geographic risk data."""

    def __init__(self):
        if not HAS_PLOTLY:
            raise ImportError("Plotly required. Install with: pip install plotly")
        self.fig = None

    def plot(self, data, country='country', value='value',
             risk=None, title='Global Risk Distribution',
             color_scale='RdYlGn_r', **kwargs):
        """Create globe visualization."""
        required = [country, value]
        missing = [col for col in required if col not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Create choropleth map
        fig = go.Figure(data=go.Choropleth(
            locations=data[country],
            z=data[value],
            locationmode='ISO-3',
            colorscale=color_scale,
            autocolorscale=False,
            text=data[country],
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_title=kwargs.get('colorbar_title', value.title()),
        ))

        # Update layout for globe projection
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16)
            ),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='orthographic',
                projection_rotation=dict(
                    lon=kwargs.get('center_lon', 0),
                    lat=kwargs.get('center_lat', 0)
                ),
                bgcolor='rgba(0,0,0,0)',
                showlakes=True,
                lakecolor='lightblue',
                showocean=True,
                oceancolor='lightblue'
            ),
            width=kwargs.get('width', 800),
            height=kwargs.get('height', 600),
            margin=dict(l=0, r=0, t=50, b=0)
        )

        self.fig = fig
        return fig

    def plot_connections(self, data, src_country='source_country',
                        tgt_country='target_country', strength='strength',
                        src_lat='source_lat', src_lon='source_lon',
                        tgt_lat='target_lat', tgt_lon='target_lon',
                        title='Global Risk Connections', **kwargs):
        """Create globe with connections between countries."""
        fig = go.Figure()

        # Add connection lines
        for _, row in data.iterrows():
            fig.add_trace(go.Scattergeo(
                lon=[row[src_lon], row[tgt_lon]],
                lat=[row[src_lat], row[tgt_lat]],
                mode='lines',
                line=dict(
                    width=max(1, row[strength] * 5),
                    color='red' if row[strength] > 0.7 else 'orange' if row[strength] > 0.4 else 'green'
                ),
                opacity=0.6,
                showlegend=False,
                hoverinfo='text',
                text=f"{row[src_country]} → {row[tgt_country]}<br>Strength: {row[strength]:.2f}"
            ))

        # Add source points
        source_points = data[[src_country, src_lat, src_lon, strength]].drop_duplicates()
        fig.add_trace(go.Scattergeo(
            lon=source_points[src_lon],
            lat=source_points[src_lat],
            text=source_points[src_country],
            mode='markers',
            marker=dict(size=8, color='blue', sizemode='diameter'),
            name='Source Countries'
        ))

        # Update layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16)
            ),
            geo=dict(
                projection_type='orthographic',
                showland=True,
                landcolor='lightgray',
                showocean=True,
                oceancolor='lightblue',
                showlakes=True,
                lakecolor='lightblue',
                showframe=False,
                showcoastlines=True
            ),
            width=kwargs.get('width', 800),
            height=kwargs.get('height', 600),
            margin=dict(l=0, r=0, t=50, b=0)
        )

        self.fig = fig
        return fig

    def plot_time_series(self, data: pd.DataFrame,
                        country_col: str = 'country',
                        value_col: str = 'value',
                        time_col: str = 'date',
                        title: str = 'Global Risk Over Time',
                        **kwargs):
        """
        Create an animated globe showing risk evolution over time.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing time series data
        country_col : str
            Column name for countries
        value_col : str
            Column name for values
        time_col : str
            Column name for time periods
        title : str
            Plot title
        **kwargs
            Additional plotting parameters

        Returns
        -------
        fig : plotly.graph_objects.Figure
            Plotly figure object with animation
        """
        # Create animated choropleth
        fig = px.choropleth(
            data,
            locations=country_col,
            color=value_col,
            animation_frame=time_col,
            color_continuous_scale='RdYlGn_r',
            title=title,
            **kwargs
        )

        # Update layout for globe
        fig.update_layout(
            geo=dict(
                projection_type='orthographic',
                showframe=False,
                showcoastlines=True,
                showlakes=True,
                lakecolor='lightblue',
                showocean=True,
                oceancolor='lightblue'
            ),
            width=kwargs.get('width', 800),
            height=kwargs.get('height', 600)
        )

        self.fig = fig
        return fig

    def add_markers(self, locations: pd.DataFrame,
                   lat_col: str = 'latitude',
                   lon_col: str = 'longitude',
                   text_col: str = 'text',
                   size_col: Optional[str] = None,
                   color_col: Optional[str] = None) -> None:
        """
        Add markers to existing globe plot.

        Parameters
        ----------
        locations : pd.DataFrame
            DataFrame with location data
        lat_col : str
            Column name for latitude
        lon_col : str
            Column name for longitude
        text_col : str
            Column name for marker text
        size_col : str, optional
            Column name for marker sizes
        color_col : str, optional
            Column name for marker colors
        """
        if self.fig is None:
            raise ValueError("No figure available. Call plot() first.")

        marker_config = dict(
            size=locations[size_col] * 10 if size_col else 8,
            color=locations[color_col] if color_col else 'red',
            sizemode='diameter'
        )

        self.fig.add_trace(go.Scattergeo(
            lon=locations[lon_col],
            lat=locations[lat_col],
            text=locations[text_col],
            mode='markers',
            marker=marker_config,
            showlegend=True,
            name='Risk Markers'
        ))

    def save_html(self, filename: str) -> None:
        """Save the interactive plot as HTML."""
        if self.fig is None:
            raise ValueError("No figure to save. Call plot() first.")
        self.fig.write_html(filename)

    def show(self) -> None:
        """Display the interactive plot."""
        if self.fig is None:
            raise ValueError("No figure to show. Call plot() first.")
        self.fig.show()


def country_risk_globe(data, country='country', risk='risk_score',
                      title='Global Country Risk Distribution', **kwargs):
    """Country risk globe."""
    globe_plot = GlobeRiskPlot()
    return globe_plot.plot(data, country=country, value=risk,
                          title=title, color_scale='RdYlGn_r', **kwargs)


def trade_flow_globe(data, source='source_country', target='target_country',
                    volume='trade_volume', title='Global Trade Flow Risks',
                    **kwargs):
    """Trade flow globe."""
    globe_plot = GlobeRiskPlot()

    # Aggregate trade volumes by country
    source_agg = data.groupby(source)[volume].sum().reset_index()
    source_agg.columns = ['country', 'total_volume']

    target_agg = data.groupby(target)[volume].sum().reset_index()
    target_agg.columns = ['country', 'total_volume']

    # Combine and aggregate
    combined = pd.concat([source_agg, target_agg]).groupby('country')['total_volume'].sum().reset_index()

    return globe_plot.plot(combined, country='country', value='total_volume',
                          title=title, colorbar_title='Trade Volume', **kwargs)