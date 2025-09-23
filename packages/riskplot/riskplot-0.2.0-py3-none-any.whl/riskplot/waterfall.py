"""
Waterfall charts for risk attribution and decomposition analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Optional, List, Dict, Tuple, Union
from .base import RiskVisualization, PlotConfig, ColorScheme


class WaterfallChart(RiskVisualization):
    """Waterfall chart for showing risk attribution and decomposition."""

    def plot(
        self,
        data: pd.DataFrame,
        category_col: str,
        value_col: str,
        start_value: Optional[float] = None,
        end_value: Optional[float] = None,
        positive_color: str = '#2E8B57',
        negative_color: str = '#DC143C',
        total_color: str = '#4682B4',
        connector_color: str = '#808080',
        show_connectors: bool = True,
        show_values: bool = True,
        value_format: str = '{:.2f}',
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create a waterfall chart.

        Parameters
        ----------
        data : pd.DataFrame
            Data containing categories and values
        category_col : str
            Column containing category names
        value_col : str
            Column containing values (can be positive or negative)
        start_value : float, optional
            Starting value (if not provided, starts at 0)
        end_value : float, optional
            Expected ending value for validation
        positive_color : str, default '#2E8B57'
            Color for positive values
        negative_color : str, default '#DC143C'
            Color for negative values
        total_color : str, default '#4682B4'
            Color for total/cumulative bars
        connector_color : str, default '#808080'
            Color for connector lines
        show_connectors : bool, default True
            Whether to show connector lines
        show_values : bool, default True
            Whether to show value labels
        value_format : str, default '{:.2f}'
            Format string for value labels
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        fig, ax = self._setup_figure(**kwargs)

        # Validate data
        self._validate_data(data, [category_col, value_col])

        # Prepare data
        categories = data[category_col].tolist()
        values = data[value_col].tolist()

        # Add start and end if specified
        if start_value is not None:
            categories.insert(0, 'Start')
            values.insert(0, start_value)

        if end_value is not None:
            categories.append('Total')
            values.append(end_value)
        else:
            # Calculate total
            total = (start_value or 0) + sum(values[1:] if start_value else values)
            categories.append('Total')
            values.append(total)

        # Calculate cumulative positions
        n_categories = len(categories)
        x_positions = np.arange(n_categories)
        cumulative = np.zeros(n_categories)

        if start_value is not None:
            cumulative[0] = start_value
            for i in range(1, n_categories - 1):
                cumulative[i] = cumulative[i-1] + values[i]
            cumulative[-1] = values[-1]  # Total
        else:
            cumulative[0] = values[0]
            for i in range(1, n_categories - 1):
                cumulative[i] = cumulative[i-1] + values[i]
            cumulative[-1] = cumulative[-2]  # Total equals last cumulative

        # Determine bar colors and bottom positions
        colors = []
        bottoms = []

        for i, value in enumerate(values):
            if i == 0 and start_value is not None:  # Start bar
                colors.append(total_color)
                bottoms.append(0)
            elif i == len(values) - 1:  # Total bar
                colors.append(total_color)
                bottoms.append(0)
            else:  # Regular bars
                if value >= 0:
                    colors.append(positive_color)
                    bottoms.append(cumulative[i-1] if i > 0 else 0)
                else:
                    colors.append(negative_color)
                    bottoms.append(cumulative[i])

        # Create bars
        bars = ax.bar(x_positions, [abs(v) for v in values], bottom=bottoms, color=colors)

        # Add connector lines
        if show_connectors and n_categories > 2:
            for i in range(n_categories - 2):
                if i == 0 and start_value is not None:
                    start_y = cumulative[i]
                    end_y = cumulative[i+1] if values[i+1] >= 0 else cumulative[i+1]
                else:
                    start_y = cumulative[i]
                    end_y = cumulative[i+1] if values[i+1] >= 0 else cumulative[i+1]

                ax.plot([i + 0.4, i + 1 - 0.4], [start_y, start_y],
                       color=connector_color, linestyle='--', alpha=0.7, linewidth=1)

        # Add value labels
        if show_values:
            for i, (bar, value) in enumerate(zip(bars, values)):
                height = bar.get_height()
                y_pos = bar.get_y() + height / 2

                label = value_format.format(value)
                if i == len(values) - 1:  # Total
                    label = f'Total: {value_format.format(value)}'

                ax.text(bar.get_x() + bar.get_width()/2, y_pos, label,
                       ha='center', va='center', fontweight='bold',
                       color='white' if height > max(values) * 0.1 else 'black')

        # Customize plot
        ax.set_xticks(x_positions)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_ylabel('Value')
        ax.set_title(kwargs.get('title', 'Waterfall Chart'))

        # Add zero line
        ax.axhline(y=0, color='black', linewidth=0.8)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor=positive_color, label='Positive'),
            Patch(facecolor=negative_color, label='Negative'),
            Patch(facecolor=total_color, label='Total')
        ]
        ax.legend(handles=legend_elements, loc='best')

        plt.tight_layout()
        return fig, ax


def risk_attribution_waterfall(
    data: pd.DataFrame,
    factor_col: str,
    contribution_col: str,
    base_return: float = 0,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a risk attribution waterfall chart.

    Parameters
    ----------
    data : pd.DataFrame
        Risk attribution data
    factor_col : str
        Column containing risk factor names
    contribution_col : str
        Column containing contribution values
    base_return : float, default 0
        Base return or starting value
    **kwargs
        Additional arguments passed to WaterfallChart.plot()

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    waterfall = WaterfallChart()
    return waterfall.plot(
        data,
        category_col=factor_col,
        value_col=contribution_col,
        start_value=base_return,
        title='Risk Attribution Analysis',
        **kwargs
    )


def pnl_waterfall(
    data: pd.DataFrame,
    component_col: str,
    pnl_col: str,
    starting_value: Optional[float] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a P&L waterfall chart.

    Parameters
    ----------
    data : pd.DataFrame
        P&L data
    component_col : str
        Column containing P&L component names
    pnl_col : str
        Column containing P&L values
    starting_value : float, optional
        Starting portfolio value
    **kwargs
        Additional arguments

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    waterfall = WaterfallChart()
    return waterfall.plot(
        data,
        category_col=component_col,
        value_col=pnl_col,
        start_value=starting_value,
        title='P&L Attribution',
        positive_color='#4CAF50',
        negative_color='#F44336',
        **kwargs
    )


def var_decomposition(
    data: pd.DataFrame,
    component_col: str,
    var_col: str,
    total_var: Optional[float] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a VaR decomposition waterfall chart.

    Parameters
    ----------
    data : pd.DataFrame
        VaR decomposition data
    component_col : str
        Column containing component names
    var_col : str
        Column containing VaR contributions
    total_var : float, optional
        Total portfolio VaR for validation
    **kwargs
        Additional arguments

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    waterfall = WaterfallChart()
    return waterfall.plot(
        data,
        category_col=component_col,
        value_col=var_col,
        end_value=total_var,
        title='VaR Decomposition',
        positive_color='#FF9800',
        negative_color='#2196F3',
        **kwargs
    )


def stress_test_waterfall(
    data: pd.DataFrame,
    scenario_col: str,
    impact_col: str,
    base_value: float = 0,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a stress test waterfall chart.

    Parameters
    ----------
    data : pd.DataFrame
        Stress test results
    scenario_col : str
        Column containing scenario names
    impact_col : str
        Column containing impact values
    base_value : float, default 0
        Base case value
    **kwargs
        Additional arguments

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    waterfall = WaterfallChart()
    return waterfall.plot(
        data,
        category_col=scenario_col,
        value_col=impact_col,
        start_value=base_value,
        title='Stress Test Impact Analysis',
        positive_color='#8BC34A',
        negative_color='#E91E63',
        **kwargs
    )