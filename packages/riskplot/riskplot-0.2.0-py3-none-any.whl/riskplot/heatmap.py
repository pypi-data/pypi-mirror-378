"""
Risk heatmap visualizations for correlation matrices and risk grids.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from typing import Optional, List, Dict, Tuple, Union
from .base import RiskVisualization, PlotConfig, ColorScheme


class RiskHeatmap(RiskVisualization):
    """Risk heatmap for correlation matrices, risk grids, and exposure maps."""

    def plot(
        self,
        data: pd.DataFrame,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        value_col: Optional[str] = None,
        annot: bool = True,
        fmt: str = '.2f',
        cmap: str = 'RdYlGn_r',
        center: Optional[float] = None,
        square: bool = True,
        linewidths: float = 0.5,
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create a risk heatmap.

        Parameters
        ----------
        data : pd.DataFrame
            Data for heatmap. Can be:
            - Correlation matrix (square DataFrame)
            - Long format with x_col, y_col, value_col
            - Pivot table format
        x_col : str, optional
            Column for x-axis (required for long format)
        y_col : str, optional
            Column for y-axis (required for long format)
        value_col : str, optional
            Column for values (required for long format)
        annot : bool, default True
            Whether to annotate cells with values
        fmt : str, default '.2f'
            Format string for annotations
        cmap : str, default 'RdYlGn_r'
            Colormap name
        center : float, optional
            Value at which to center the colormap
        square : bool, default True
            Whether to make cells square
        linewidths : float, default 0.5
            Width of lines between cells
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        fig, ax = self._setup_figure(**kwargs)

        # Process data based on format
        if x_col and y_col and value_col:
            # Long format - pivot to matrix
            heatmap_data = data.pivot(index=y_col, columns=x_col, values=value_col)
        elif data.index.equals(data.columns):
            # Already a correlation matrix
            heatmap_data = data
        else:
            # Assume it's already in the right format
            heatmap_data = data

        # Create heatmap
        im = ax.imshow(
            heatmap_data.values,
            cmap=cmap,
            aspect='auto' if not square else 'equal',
            interpolation='nearest'
        )

        # Center colormap if requested
        if center is not None:
            vmax = max(abs(heatmap_data.values.min() - center),
                      abs(heatmap_data.values.max() - center))
            im.set_clim(center - vmax, center + vmax)

        # Set ticks and labels
        ax.set_xticks(range(len(heatmap_data.columns)))
        ax.set_yticks(range(len(heatmap_data.index)))
        ax.set_xticklabels(heatmap_data.columns, rotation=45, ha='right')
        ax.set_yticklabels(heatmap_data.index)

        # Add grid lines
        if linewidths > 0:
            for i in range(len(heatmap_data.index) + 1):
                ax.axhline(i - 0.5, color='white', linewidth=linewidths)
            for j in range(len(heatmap_data.columns) + 1):
                ax.axvline(j - 0.5, color='white', linewidth=linewidths)

        # Annotations
        if annot:
            for i in range(len(heatmap_data.index)):
                for j in range(len(heatmap_data.columns)):
                    value = heatmap_data.iloc[i, j]
                    if not np.isnan(value):
                        text_color = 'white' if abs(value) > 0.5 else 'black'
                        ax.text(j, i, format(value, fmt),
                               ha='center', va='center', color=text_color)

        # Colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Value', rotation=270, labelpad=15)

        # Title
        title = kwargs.get('title', 'Risk Heatmap')
        ax.set_title(title)

        plt.tight_layout()
        return fig, ax


def correlation_heatmap(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = 'pearson',
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a correlation heatmap.

    Parameters
    ----------
    data : pd.DataFrame
        Input data
    columns : list, optional
        Columns to include in correlation
    method : str, default 'pearson'
        Correlation method ('pearson', 'spearman', 'kendall')
    **kwargs
        Arguments passed to RiskHeatmap.plot()

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    if columns:
        corr_data = data[columns].corr(method=method)
    else:
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        corr_data = data[numeric_cols].corr(method=method)

    heatmap = RiskHeatmap()
    return heatmap.plot(
        corr_data,
        center=0,
        cmap='RdBu_r',
        title=f'{method.title()} Correlation Matrix',
        **kwargs
    )


def risk_matrix(
    data: pd.DataFrame,
    probability_col: str,
    impact_col: str,
    label_col: Optional[str] = None,
    prob_bins: Optional[List[str]] = None,
    impact_bins: Optional[List[str]] = None,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a risk matrix (probability vs impact).

    Parameters
    ----------
    data : pd.DataFrame
        Risk data
    probability_col : str
        Column containing probability values
    impact_col : str
        Column containing impact values
    label_col : str, optional
        Column containing risk labels
    prob_bins : list, optional
        Custom probability bin labels
    impact_bins : list, optional
        Custom impact bin labels
    **kwargs
        Additional arguments

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    fig, ax = plt.subplots(figsize=kwargs.get('figsize', (10, 8)))

    # Define default bins if not provided
    if prob_bins is None:
        prob_bins = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
    if impact_bins is None:
        impact_bins = ['Negligible', 'Minor', 'Moderate', 'Major', 'Severe']

    # Create risk level matrix
    n_prob = len(prob_bins)
    n_impact = len(impact_bins)
    risk_matrix_values = np.zeros((n_impact, n_prob))

    # Calculate risk levels (simple multiplication)
    for i in range(n_impact):
        for j in range(n_prob):
            risk_matrix_values[i, j] = (i + 1) * (j + 1)

    # Create color map
    colors = ['#2E8B57', '#9ACD32', '#FFD700', '#FFA500', '#FF6347', '#DC143C']
    risk_cmap = LinearSegmentedColormap.from_list('risk', colors, N=n_prob * n_impact)

    # Plot matrix
    im = ax.imshow(risk_matrix_values, cmap=risk_cmap, aspect='equal')

    # Add grid and labels
    ax.set_xticks(range(n_prob))
    ax.set_yticks(range(n_impact))
    ax.set_xticklabels(prob_bins, rotation=45, ha='right')
    ax.set_yticklabels(impact_bins)

    # Add risk level annotations
    for i in range(n_impact):
        for j in range(n_prob):
            risk_level = int(risk_matrix_values[i, j])
            ax.text(j, i, str(risk_level), ha='center', va='center',
                   color='white', fontweight='bold')

    # Plot actual data points
    if not data.empty:
        # Bin the actual data
        prob_values = pd.cut(data[probability_col], bins=n_prob, labels=range(n_prob))
        impact_values = pd.cut(data[impact_col], bins=n_impact, labels=range(n_impact))

        for idx, row in data.iterrows():
            x = prob_values.iloc[idx] if not pd.isna(prob_values.iloc[idx]) else 0
            y = impact_values.iloc[idx] if not pd.isna(impact_values.iloc[idx]) else 0

            # Add scatter point
            ax.scatter(x, y, s=100, c='black', marker='o', alpha=0.7, edgecolors='white')

            # Add label if provided
            if label_col and not pd.isna(row[label_col]):
                ax.annotate(str(row[label_col]), (x, y),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, ha='left')

    ax.set_xlabel('Probability')
    ax.set_ylabel('Impact')
    ax.set_title('Risk Matrix')

    # Add colorbar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Risk Level', rotation=270, labelpad=15)

    plt.tight_layout()
    return fig, ax


def exposure_heatmap(
    data: pd.DataFrame,
    entity_col: str,
    sector_col: str,
    exposure_col: str,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create an exposure heatmap showing concentration risk.

    Parameters
    ----------
    data : pd.DataFrame
        Exposure data
    entity_col : str
        Column containing entity names
    sector_col : str
        Column containing sector information
    exposure_col : str
        Column containing exposure amounts
    **kwargs
        Additional arguments

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    # Aggregate exposures
    exposure_matrix = data.pivot_table(
        index=entity_col,
        columns=sector_col,
        values=exposure_col,
        aggfunc='sum',
        fill_value=0
    )

    # Sort by total exposure
    total_exposure = exposure_matrix.sum(axis=1).sort_values(ascending=False)
    exposure_matrix = exposure_matrix.loc[total_exposure.index]

    heatmap = RiskHeatmap()
    return heatmap.plot(
        exposure_matrix,
        cmap='Reds',
        title='Exposure Concentration by Entity and Sector',
        **kwargs
    )