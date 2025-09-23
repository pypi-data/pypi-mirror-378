"""
Base classes and utilities for riskplot framework.

This module provides the foundation for all risk visualization charts,
ensuring consistency and extensibility across different chart types.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass


@dataclass
class PlotConfig:
    """Configuration settings for plots."""
    figsize: Tuple[int, int] = (10, 6)
    dpi: int = 100
    style: str = 'default'
    colormap: str = 'viridis'
    alpha: float = 0.7
    grid: bool = True
    grid_alpha: float = 0.3
    background_color: str = 'white'
    text_color: str = 'black'
    font_size: int = 10
    title_size: int = 12
    label_size: int = 10


class RiskVisualization(ABC):
    """
    Abstract base class for all risk visualization charts.

    This class defines the interface and common functionality
    for all chart types in the riskplot package.
    """

    def __init__(self, config: Optional[PlotConfig] = None):
        """Initialize with configuration."""
        self.config = config or PlotConfig()
        self.fig = None
        self.ax = None

    @abstractmethod
    def plot(self, data: pd.DataFrame, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create the visualization.

        Parameters
        ----------
        data : pd.DataFrame
            The data to visualize
        **kwargs
            Additional plotting parameters

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        pass

    def _setup_figure(self, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """Set up the matplotlib figure and axes."""
        figsize = kwargs.get('figsize', self.config.figsize)
        fig, ax = plt.subplots(figsize=figsize, dpi=self.config.dpi)

        # Apply styling
        ax.set_facecolor(self.config.background_color)

        if self.config.grid:
            ax.grid(True, alpha=self.config.grid_alpha)

        self.fig = fig
        self.ax = ax
        return fig, ax

    def _validate_data(self, data: pd.DataFrame, required_cols: List[str]) -> None:
        """Validate that required columns exist in the data."""
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    def _apply_color_scheme(self, values: np.ndarray, colormap: str = None) -> np.ndarray:
        """Apply color scheme to values."""
        cmap = plt.cm.get_cmap(colormap or self.config.colormap)
        norm = mcolors.Normalize(vmin=values.min(), vmax=values.max())
        return cmap(norm(values))

    def save(self, filename: str, **kwargs) -> None:
        """Save the plot to file."""
        if self.fig is None:
            raise ValueError("No plot to save. Call plot() first.")
        self.fig.savefig(filename, **kwargs)


class ColorScheme:
    """Color scheme utilities for risk visualizations."""

    # Risk-specific color palettes
    RISK_COLORS = {
        'low': '#2E8B57',      # Sea Green
        'medium': '#FFD700',    # Gold
        'high': '#FF6347',      # Tomato
        'critical': '#DC143C'   # Crimson
    }

    RATING_COLORS = {
        'aaa': '#006400',  # Dark Green
        'aa': '#32CD32',   # Lime Green
        'a': '#9ACD32',    # Yellow Green
        'bbb': '#FFD700',  # Gold
        'bb': '#FFA500',   # Orange
        'b': '#FF6347',    # Tomato
        'c': '#DC143C'     # Crimson
    }

    @staticmethod
    def get_risk_palette(n_colors: int = 4) -> List[str]:
        """Get a risk-appropriate color palette."""
        colors = list(ColorScheme.RISK_COLORS.values())
        if n_colors <= len(colors):
            return colors[:n_colors]
        # Interpolate for more colors
        return plt.cm.RdYlGn_r(np.linspace(0, 1, n_colors))

    @staticmethod
    def get_rating_palette() -> Dict[str, str]:
        """Get credit rating color palette."""
        return ColorScheme.RATING_COLORS.copy()


class DataProcessor:
    """Utilities for processing and transforming data for risk visualizations."""

    @staticmethod
    def aggregate_by_categories(
        data: pd.DataFrame,
        category_col: str,
        value_col: str,
        agg_func: str = 'mean'
    ) -> pd.DataFrame:
        """Aggregate data by categories."""
        return data.groupby(category_col)[value_col].agg(agg_func).reset_index()

    @staticmethod
    def calculate_risk_metrics(data: pd.DataFrame, value_col: str) -> Dict[str, float]:
        """Calculate common risk metrics."""
        values = data[value_col].dropna()
        return {
            'mean': values.mean(),
            'std': values.std(),
            'var': values.var(),
            'skew': values.skew() if len(values) > 2 else np.nan,
            'kurt': values.kurtosis() if len(values) > 3 else np.nan,
            'var_95': values.quantile(0.05),  # 5% VaR
            'var_99': values.quantile(0.01),  # 1% VaR
            'cvar_95': values[values <= values.quantile(0.05)].mean(),
            'max_drawdown': DataProcessor._max_drawdown(values)
        }

    @staticmethod
    def _max_drawdown(returns: pd.Series) -> float:
        """Calculate maximum drawdown."""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()

    @staticmethod
    def detect_outliers(data: pd.Series, method: str = 'iqr') -> pd.Series:
        """Detect outliers using various methods."""
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return (data < lower_bound) | (data > upper_bound)
        elif method == 'zscore':
            z_scores = np.abs((data - data.mean()) / data.std())
            return z_scores > 3
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")


class LegendBuilder:
    """Utilities for building consistent legends across chart types."""

    @staticmethod
    def create_risk_legend(ax: plt.Axes, risk_levels: List[str], colors: List[str]) -> None:
        """Create a risk level legend."""
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, label=level)
                          for level, color in zip(risk_levels, colors)]
        ax.legend(handles=legend_elements, loc='best')

    @staticmethod
    def create_colorbar(fig: plt.Figure, ax: plt.Axes, mappable, label: str = '') -> None:
        """Create a colorbar for continuous color mappings."""
        cbar = fig.colorbar(mappable, ax=ax)
        cbar.set_label(label, rotation=270, labelpad=15)


class AnnotationHelper:
    """Utilities for adding annotations and labels to plots."""

    @staticmethod
    def add_value_labels(ax: plt.Axes, x: np.ndarray, y: np.ndarray,
                        values: np.ndarray, format_str: str = '{:.2f}') -> None:
        """Add value labels to data points."""
        for i, (xi, yi, val) in enumerate(zip(x, y, values)):
            ax.annotate(format_str.format(val), (xi, yi),
                       textcoords="offset points", xytext=(0,10), ha='center')

    @staticmethod
    def add_threshold_lines(ax: plt.Axes, thresholds: Dict[str, float],
                           orientation: str = 'horizontal') -> None:
        """Add threshold lines to plots."""
        for label, value in thresholds.items():
            if orientation == 'horizontal':
                ax.axhline(y=value, linestyle='--', alpha=0.7, label=f'{label}: {value}')
            else:
                ax.axvline(x=value, linestyle='--', alpha=0.7, label=f'{label}: {value}')


class ValidationHelper:
    """Data validation utilities."""

    @staticmethod
    def validate_risk_data(data: pd.DataFrame) -> Dict[str, Any]:
        """Validate risk data and return quality metrics."""
        validation = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'shape': data.shape,
            'missing_data': data.isnull().sum().to_dict(),
            'data_types': data.dtypes.to_dict()
        }

        # Check for missing data
        missing_pct = (data.isnull().sum() / len(data)) * 100
        high_missing = missing_pct[missing_pct > 50]
        if not high_missing.empty:
            validation['warnings'].append(f"High missing data: {high_missing.to_dict()}")

        # Check for constant columns
        constant_cols = [col for col in data.columns if data[col].nunique() <= 1]
        if constant_cols:
            validation['warnings'].append(f"Constant columns: {constant_cols}")

        # Check data ranges
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if data[col].std() == 0:
                validation['warnings'].append(f"Zero variance in column: {col}")

        return validation