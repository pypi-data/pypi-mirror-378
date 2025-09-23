"""
Ridge plot functionality for categorical data visualization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import colors
from scipy.stats import gaussian_kde
from typing import Dict, List, Optional, Tuple, Union


def ridge_plot(
    data: pd.DataFrame,
    category_col: str,
    value_col: str,
    group_col: Optional[str] = None,
    category_order: Optional[List[str]] = None,
    sort_by_mean: bool = True,
    figsize: Tuple[int, int] = (10, 6),
    y_spacing: float = 0.8,
    group_offset: float = 0.2,
    colormap1: str = 'plasma',
    colormap2: str = 'viridis',
    bandwidth: float = 0.39,
    show_mean: bool = True,
    show_count: bool = True,
    alpha: float = 0.7,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create ridge plots for categorical data.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the data to plot
    category_col : str
        Name of column containing categories (will be y-axis labels)
    value_col : str
        Name of column containing values to plot distributions for
    group_col : str, optional
        Name of column containing group information for dual ridges
    category_order : list, optional
        Custom order for categories. If None, will be determined by sort_by_mean
    sort_by_mean : bool, default True
        Whether to sort categories by mean value
    figsize : tuple, default (10, 6)
        Figure size (width, height)
    y_spacing : float, default 0.8
        Vertical spacing between ridge plots
    group_offset : float, default 0.2
        Vertical offset between groups when group_col is specified
    colormap1 : str, default 'plasma'
        Colormap for first group or single group
    colormap2 : str, default 'viridis'
        Colormap for second group
    bandwidth : float, default 0.39
        Bandwidth for kernel density estimation
    show_mean : bool, default True
        Whether to show mean markers
    show_count : bool, default True
        Whether to show count labels
    alpha : float, default 0.7
        Grid transparency
    **kwargs
        Additional arguments passed to matplotlib

    Returns
    -------
    fig, ax : matplotlib figure and axes objects

    Examples
    --------
    >>> import pandas as pd
    >>> import riskplot as rp
    >>>
    >>> # Single group ridge plot
    >>> df = pd.DataFrame({
    ...     'company': ['A', 'A', 'B', 'B', 'C', 'C'],
    ...     'rating': ['aaa', 'aa', 'bbb', 'bb', 'a', 'aa']
    ... })
    >>> fig, ax = rp.ridge_plot(df, 'company', 'rating')
    >>>
    >>> # Dual group ridge plot
    >>> df = pd.DataFrame({
    ...     'company': ['A', 'A', 'A', 'A'],
    ...     'rating': ['aaa', 'aa', 'bbb', 'bb'],
    ...     'source': ['cb', 'cb', 'sp', 'sp']
    ... })
    >>> fig, ax = rp.ridge_plot(df, 'company', 'rating', 'source')
    """

    # Validate inputs
    if category_col not in data.columns:
        raise ValueError(f"Category column '{category_col}' not found in data")
    if value_col not in data.columns:
        raise ValueError(f"Value column '{value_col}' not found in data")
    if group_col and group_col not in data.columns:
        raise ValueError(f"Group column '{group_col}' not found in data")

    # Create mapping for categorical values if they're strings
    if data[value_col].dtype == 'object':
        if category_order is None:
            unique_values = data[value_col].unique()
            # Try to sort intelligently for rating-like data
            if all(isinstance(v, str) for v in unique_values):
                # Handle rating-like strings
                try:
                    sorted_values = _sort_rating_strings(unique_values)
                    value_mapping = {v: i+1 for i, v in enumerate(sorted_values)}
                except:
                    # Fallback to alphabetical
                    sorted_values = sorted(unique_values)
                    value_mapping = {v: i+1 for i, v in enumerate(sorted_values)}
            else:
                sorted_values = sorted(unique_values)
                value_mapping = {v: i+1 for i, v in enumerate(sorted_values)}
        else:
            value_mapping = {v: i+1 for i, v in enumerate(category_order)}

        # Convert categorical values to numeric
        data = data.copy()
        data[value_col] = data[value_col].map(value_mapping)
        value_min, value_max = 1, len(value_mapping)
        value_labels = list(value_mapping.keys())
        value_positions = list(value_mapping.values())
    else:
        value_min, value_max = data[value_col].min(), data[value_col].max()
        value_labels = None
        value_positions = None

    # Determine category order
    if category_order is None:
        if sort_by_mean:
            if group_col:
                # Sort by mean of first group
                first_group = data[group_col].iloc[0]
                group_data = data[data[group_col] == first_group]
                means = group_data.groupby(category_col)[value_col].mean()
            else:
                means = data.groupby(category_col)[value_col].mean()
            category_order = list(means.sort_values().index)
        else:
            category_order = sorted(data[category_col].unique())

    # Set up the plot
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_facecolor('darkgrey')
    ax.patch.set_alpha(0.05)
    ax.grid(axis='x', linestyle='--', alpha=alpha)
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    plt.margins(x=0)

    # Set up colormaps
    cmap1 = getattr(cm, colormap1)
    cmap2 = getattr(cm, colormap2) if group_col else cmap1
    norm = colors.Normalize(vmin=value_min, vmax=value_max)

    # Determine groups
    if group_col:
        groups = data[group_col].unique()
        if len(groups) > 2:
            raise ValueError("Currently supports maximum 2 groups")
        group_configs = [
            (groups[0], cmap1, 0),
            (groups[1] if len(groups) > 1 else groups[0], cmap2, group_offset)
        ]
    else:
        group_configs = [(None, cmap1, 0)]

    # Set axis limits
    ax.set_xlim(value_max, value_min)
    ax.set_ylim(0, len(category_order) * y_spacing + 1.0)

    # Plot ridges for each category
    for i, category in enumerate(category_order):
        y_base = i * y_spacing

        for group, cmap, y_shift in group_configs:
            # Filter data
            if group_col:
                subset = data[(data[category_col] == category) & (data[group_col] == group)]
            else:
                subset = data[data[category_col] == category]

            if subset.empty:
                continue

            values = subset[value_col].values

            # Create KDE
            kde = gaussian_kde(values, bw_method=bandwidth)
            x = np.linspace(value_min, value_max, 200)
            y = kde(x) / kde(x).max() + y_base + y_shift

            # Fill with gradient colors
            for j in range(len(x) - 1):
                mid = 0.5 * (x[j] + x[j + 1])
                color = cmap(1 - norm(mid))
                ax.fill_between([x[j], x[j + 1]],
                              [y_base + y_shift] * 2,
                              [y[j], y[j + 1]],
                              color=color,
                              step='mid',
                              linewidth=0)

            # Outline
            ax.plot(x, y, color='black', linewidth=1.2, zorder=2)

            # Mean marker
            if show_mean:
                mean_val = values.mean()
                y_mean = kde(mean_val) / kde(x).max() + y_base + y_shift
                ax.scatter(mean_val, y_mean, s=30, facecolor='white',
                          edgecolor='black', zorder=3)

            # Count label
            if show_count and (not group_col or group == group_configs[0][0]):
                y_count = kde(value_max) / kde(x).max() + y_base
                ax.text(value_max, y_count + 0.05, str(len(values)),
                       ha='center', va='bottom', fontsize=8,
                       color='black', zorder=5)

        # Category label (positioned at mean of first group)
        if group_col:
            first_group_data = data[(data[category_col] == category) &
                                  (data[group_col] == group_configs[0][0])]
            if not first_group_data.empty:
                mean_pos = first_group_data[value_col].mean()
            else:
                mean_pos = (value_min + value_max) / 2
        else:
            mean_pos = data[data[category_col] == category][value_col].mean()

        ax.text(mean_pos, y_base + group_offset + 0.5, str(category),
               ha='center', va='center', fontsize=8, fontweight='bold',
               color='white', zorder=4)

    # Set labels and ticks
    if value_labels:
        ax.set_xticks(value_positions)
        ax.set_xticklabels([str(label).upper() for label in value_labels])

    ax.set_yticks([])
    ax.set_xlabel(value_col.replace('_', ' ').title())

    # Set title
    if group_col:
        title = f'{value_col.title()} Distributions by {category_col.title()} (by {group_col.title()})'
    else:
        title = f'{value_col.title()} Distributions by {category_col.title()}'
    ax.set_title(title)

    plt.tight_layout()
    return fig, ax


def _sort_rating_strings(values: List[str]) -> List[str]:
    """Sort rating-like strings intelligently."""

    # Common rating patterns
    rating_orders = {
        # Credit ratings
        'credit': ['c-', 'c', 'c+', 'b-', 'b', 'b+', 'bb-', 'bb', 'bb+',
                  'bbb-', 'bbb', 'bbb+', 'a-', 'a', 'a+', 'aa-', 'aa', 'aa+',
                  'aaa-', 'aaa', 'aaa+'],
        'credit_simple': ['c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa'],
        # Letter grades
        'grades': ['f', 'd-', 'd', 'd+', 'c-', 'c', 'c+', 'b-', 'b', 'b+',
                  'a-', 'a', 'a+'],
        # Risk levels
        'risk': ['low', 'medium', 'high', 'very high', 'extreme'],
        'risk_short': ['low', 'med', 'high']
    }

    # Normalize values for comparison
    normalized = [v.lower().strip() for v in values]

    # Try each pattern
    for pattern_name, pattern in rating_orders.items():
        if all(v in pattern for v in normalized):
            # Sort according to this pattern
            value_to_norm = {orig: norm for orig, norm in zip(values, normalized)}
            norm_to_orig = {norm: orig for orig, norm in zip(values, normalized)}

            sorted_normalized = [v for v in pattern if v in normalized]
            return [norm_to_orig[v] for v in sorted_normalized]

    # Fallback: alphabetical sort
    return sorted(values)