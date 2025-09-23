"""
Distribution plots including violin plots, box plots, and density comparisons.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import gaussian_kde
from typing import Optional, List, Dict, Tuple, Union
from .base import RiskVisualization, PlotConfig, ColorScheme


class DistributionPlot(RiskVisualization):
    """Base class for distribution visualizations."""

    def _calculate_kde(self, data: np.ndarray, bandwidth: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate kernel density estimation."""
        if len(data) == 0:
            return np.array([]), np.array([])

        kde = gaussian_kde(data, bw_method=bandwidth)
        x_range = np.linspace(data.min(), data.max(), 200)
        density = kde(x_range)
        return x_range, density


class ViolinPlot(DistributionPlot):
    """Enhanced violin plots for risk distribution analysis."""

    def plot(
        self,
        data: pd.DataFrame,
        category_col: str,
        value_col: str,
        group_col: Optional[str] = None,
        show_box: bool = True,
        show_median: bool = True,
        show_mean: bool = True,
        show_outliers: bool = True,
        bandwidth: float = 0.1,
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create violin plots for distribution comparison.

        Parameters
        ----------
        data : pd.DataFrame
            Input data
        category_col : str
            Column for categories (x-axis)
        value_col : str
            Column for values (y-axis)
        group_col : str, optional
            Column for grouping (creates split violins)
        show_box : bool, default True
            Whether to show box plot inside violin
        show_median : bool, default True
            Whether to show median line
        show_mean : bool, default True
            Whether to show mean marker
        show_outliers : bool, default True
            Whether to show outliers
        bandwidth : float, default 0.1
            KDE bandwidth parameter
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        fig, ax = self._setup_figure(**kwargs)
        self._validate_data(data, [category_col, value_col])

        categories = data[category_col].unique()
        n_categories = len(categories)

        if group_col:
            groups = data[group_col].unique()
            n_groups = len(groups)
            width = 0.35
            positions = []

            for i, category in enumerate(categories):
                for j, group in enumerate(groups):
                    pos = i + (j - n_groups/2 + 0.5) * width
                    positions.append(pos)

                    subset = data[(data[category_col] == category) & (data[group_col] == group)]
                    if not subset.empty:
                        values = subset[value_col].dropna().values
                        self._create_violin(ax, pos, values, width/2,
                                          color=plt.cm.Set1(j), label=group if i == 0 else "")

        else:
            for i, category in enumerate(categories):
                subset = data[data[category_col] == category]
                if not subset.empty:
                    values = subset[value_col].dropna().values
                    self._create_violin(ax, i, values, 0.4, color=plt.cm.Set1(0))

        # Customize plot
        ax.set_xticks(range(n_categories))
        ax.set_xticklabels(categories)
        ax.set_xlabel(category_col.replace('_', ' ').title())
        ax.set_ylabel(value_col.replace('_', ' ').title())
        ax.set_title(kwargs.get('title', 'Distribution Comparison'))

        if group_col:
            ax.legend()

        plt.tight_layout()
        return fig, ax

    def _create_violin(self, ax, position, values, width, color, label=""):
        """Create a single violin plot."""
        if len(values) == 0:
            return

        # Calculate KDE
        x_range, density = self._calculate_kde(values)
        if len(density) == 0:
            return

        # Normalize density for width
        density_norm = density / density.max() * width

        # Create violin shape
        ax.fill_betweenx(x_range, position - density_norm, position + density_norm,
                        alpha=0.7, color=color, label=label)

        # Add statistics
        q25, median, q75 = np.percentile(values, [25, 50, 75])
        mean_val = np.mean(values)

        # Box plot elements
        ax.plot([position - width/4, position + width/4], [q25, q25], 'k-', linewidth=1)
        ax.plot([position - width/4, position + width/4], [q75, q75], 'k-', linewidth=1)
        ax.plot([position, position], [q25, q75], 'k-', linewidth=2)

        # Median line
        ax.plot([position - width/3, position + width/3], [median, median], 'w-', linewidth=2)

        # Mean marker
        ax.scatter(position, mean_val, s=50, c='red', marker='D', zorder=3)


class BoxPlot(DistributionPlot):
    """Enhanced box plots with risk-specific features."""

    def plot(
        self,
        data: pd.DataFrame,
        category_col: str,
        value_col: str,
        group_col: Optional[str] = None,
        show_fliers: bool = True,
        notch: bool = False,
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Create enhanced box plots."""
        fig, ax = self._setup_figure(**kwargs)
        self._validate_data(data, [category_col, value_col])

        if group_col:
            categories = data[category_col].unique()
            groups = data[group_col].unique()

            box_data = []
            labels = []
            colors = []

            for category in categories:
                for group in groups:
                    subset = data[(data[category_col] == category) & (data[group_col] == group)]
                    if not subset.empty:
                        box_data.append(subset[value_col].dropna().values)
                        labels.append(f"{category}\n{group}")
                        colors.append(plt.cm.Set1(list(groups).index(group)))

            bp = ax.boxplot(box_data, labels=labels, patch_artist=True, showfliers=show_fliers, notch=notch)

            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

        else:
            categories = data[category_col].unique()
            box_data = [data[data[category_col] == cat][value_col].dropna().values for cat in categories]

            bp = ax.boxplot(box_data, labels=categories, patch_artist=True, showfliers=show_fliers, notch=notch)

            for patch in bp['boxes']:
                patch.set_facecolor(plt.cm.Set1(0))
                patch.set_alpha(0.7)

        ax.set_xlabel(category_col.replace('_', ' ').title())
        ax.set_ylabel(value_col.replace('_', ' ').title())
        ax.set_title(kwargs.get('title', 'Box Plot Comparison'))

        plt.tight_layout()
        return fig, ax


class DensityComparison(DistributionPlot):
    """Compare multiple distributions using density plots."""

    def plot(
        self,
        data: pd.DataFrame,
        category_col: str,
        value_col: str,
        normalize: bool = True,
        fill_alpha: float = 0.3,
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create overlapping density plots.

        Parameters
        ----------
        data : pd.DataFrame
            Input data
        category_col : str
            Column for categories
        value_col : str
            Column for values
        normalize : bool, default True
            Whether to normalize densities
        fill_alpha : float, default 0.3
            Transparency for filled areas
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        fig, ax = self._setup_figure(**kwargs)
        self._validate_data(data, [category_col, value_col])

        categories = data[category_col].unique()
        colors = plt.cm.Set1(np.linspace(0, 1, len(categories)))

        for i, (category, color) in enumerate(zip(categories, colors)):
            subset = data[data[category_col] == category]
            values = subset[value_col].dropna().values

            if len(values) > 1:
                x_range, density = self._calculate_kde(values)

                if normalize:
                    density = density / np.trapz(density, x_range)

                ax.plot(x_range, density, color=color, linewidth=2, label=category)
                ax.fill_between(x_range, density, alpha=fill_alpha, color=color)

        ax.set_xlabel(value_col.replace('_', ' ').title())
        ax.set_ylabel('Density')
        ax.set_title(kwargs.get('title', 'Density Comparison'))
        ax.legend()

        plt.tight_layout()
        return fig, ax


class QQPlot(DistributionPlot):
    """Q-Q plots for distribution analysis."""

    def plot(
        self,
        data: pd.DataFrame,
        value_col: str,
        distribution: str = 'norm',
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create Q-Q plot against theoretical distribution.

        Parameters
        ----------
        data : pd.DataFrame
            Input data
        value_col : str
            Column for values
        distribution : str, default 'norm'
            Theoretical distribution ('norm', 't', 'lognorm', etc.)
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        fig, ax = self._setup_figure(**kwargs)
        self._validate_data(data, [value_col])

        values = data[value_col].dropna().values

        if distribution == 'norm':
            stats.probplot(values, dist="norm", plot=ax)
        elif distribution == 't':
            # Estimate degrees of freedom
            _, df_est = stats.t.fit(values)
            stats.probplot(values, dist=stats.t, sparams=(df_est,), plot=ax)
        else:
            dist = getattr(stats, distribution)
            stats.probplot(values, dist=dist, plot=ax)

        ax.set_title(f'Q-Q Plot vs {distribution.title()} Distribution')
        plt.tight_layout()
        return fig, ax


def risk_distribution_summary(
    data: pd.DataFrame,
    value_col: str,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a comprehensive risk distribution summary.

    Parameters
    ----------
    data : pd.DataFrame
        Input data
    value_col : str
        Column for values
    **kwargs
        Additional arguments

    Returns
    -------
    fig, ax : matplotlib Figure and Axes (2x2 subplot)
    """
    fig, axes = plt.subplots(2, 2, figsize=kwargs.get('figsize', (12, 10)))
    fig.suptitle(f'Risk Distribution Summary: {value_col}', fontsize=14)

    values = data[value_col].dropna().values

    # Histogram
    axes[0, 0].hist(values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].axvline(np.mean(values), color='red', linestyle='--', label='Mean')
    axes[0, 0].axvline(np.median(values), color='green', linestyle='--', label='Median')
    axes[0, 0].set_title('Histogram')
    axes[0, 0].legend()

    # Box plot
    bp = axes[0, 1].boxplot(values, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightcoral')
    axes[0, 1].set_title('Box Plot')

    # Q-Q plot
    stats.probplot(values, dist="norm", plot=axes[1, 0])
    axes[1, 0].set_title('Q-Q Plot (Normal)')

    # Density plot
    kde = gaussian_kde(values)
    x_range = np.linspace(values.min(), values.max(), 200)
    density = kde(x_range)
    axes[1, 1].plot(x_range, density, 'b-', linewidth=2)
    axes[1, 1].fill_between(x_range, density, alpha=0.3)
    axes[1, 1].set_title('Kernel Density')

    # Add statistics text
    stats_text = f"""Statistics:
Mean: {np.mean(values):.3f}
Std: {np.std(values):.3f}
Skew: {stats.skew(values):.3f}
Kurt: {stats.kurtosis(values):.3f}
VaR 95%: {np.percentile(values, 5):.3f}
VaR 99%: {np.percentile(values, 1):.3f}"""

    fig.text(0.02, 0.02, stats_text, fontsize=10, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    plt.tight_layout()
    return fig, axes