"""
Time series visualizations for risk monitoring and analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Union
from .base import RiskVisualization, PlotConfig, ColorScheme, DataProcessor


class TimeSeriesRiskPlot(RiskVisualization):
    """Time series plots for risk monitoring."""

    def plot(
        self,
        data: pd.DataFrame,
        date_col: str,
        value_col: str,
        group_col: Optional[str] = None,
        rolling_window: Optional[int] = None,
        show_trend: bool = False,
        show_volatility: bool = False,
        highlight_events: Optional[Dict] = None,
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create time series risk plots.

        Parameters
        ----------
        data : pd.DataFrame
            Time series data
        date_col : str
            Column containing dates
        value_col : str
            Column containing values to plot
        group_col : str, optional
            Column for grouping multiple series
        rolling_window : int, optional
            Window size for rolling statistics
        show_trend : bool, default False
            Whether to show trend line
        show_volatility : bool, default False
            Whether to show volatility bands
        highlight_events : dict, optional
            Dictionary of events to highlight {date: label}
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        fig, ax = self._setup_figure(**kwargs)
        self._validate_data(data, [date_col, value_col])

        # Convert date column to datetime
        data = data.copy()
        data[date_col] = pd.to_datetime(data[date_col])
        data = data.sort_values(date_col)

        if group_col:
            groups = data[group_col].unique()
            colors = plt.cm.Set1(np.linspace(0, 1, len(groups)))

            for group, color in zip(groups, colors):
                subset = data[data[group_col] == group]
                ax.plot(subset[date_col], subset[value_col],
                       label=group, color=color, linewidth=2)

                # Add rolling statistics if requested
                if rolling_window:
                    rolling_mean = subset[value_col].rolling(window=rolling_window).mean()
                    ax.plot(subset[date_col], rolling_mean,
                           '--', color=color, alpha=0.7,
                           label=f'{group} ({rolling_window}d MA)')

        else:
            ax.plot(data[date_col], data[value_col], 'b-', linewidth=2)

            # Add rolling statistics
            if rolling_window:
                rolling_mean = data[value_col].rolling(window=rolling_window).mean()
                ax.plot(data[date_col], rolling_mean, 'r--', alpha=0.7,
                       label=f'{rolling_window}-period MA')

                if show_volatility:
                    rolling_std = data[value_col].rolling(window=rolling_window).std()
                    upper_band = rolling_mean + 2 * rolling_std
                    lower_band = rolling_mean - 2 * rolling_std

                    ax.fill_between(data[date_col], lower_band, upper_band,
                                   alpha=0.2, color='gray', label='±2σ bands')

        # Add trend line
        if show_trend:
            x_numeric = mdates.date2num(data[date_col])
            z = np.polyfit(x_numeric, data[value_col], 1)
            p = np.poly1d(z)
            ax.plot(data[date_col], p(x_numeric), 'g--', alpha=0.8, label='Trend')

        # Highlight events
        if highlight_events:
            for event_date, label in highlight_events.items():
                ax.axvline(pd.to_datetime(event_date), color='red',
                          linestyle=':', alpha=0.8)
                ax.text(pd.to_datetime(event_date), ax.get_ylim()[1],
                       label, rotation=90, ha='right', va='top')

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        ax.set_xlabel('Date')
        ax.set_ylabel(value_col.replace('_', ' ').title())
        ax.set_title(kwargs.get('title', 'Time Series Risk Plot'))

        if group_col or rolling_window or show_trend:
            ax.legend()

        plt.tight_layout()
        return fig, ax


class VaRTimeSeries(TimeSeriesRiskPlot):
    """Value at Risk time series visualization."""

    def plot(
        self,
        data: pd.DataFrame,
        date_col: str,
        returns_col: str,
        confidence_levels: List[float] = [0.95, 0.99],
        window: int = 252,
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Plot VaR time series.

        Parameters
        ----------
        data : pd.DataFrame
            Returns data
        date_col : str
            Date column
        returns_col : str
            Returns column
        confidence_levels : list, default [0.95, 0.99]
            VaR confidence levels
        window : int, default 252
            Rolling window for VaR calculation
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        fig, ax = self._setup_figure(**kwargs)

        data = data.copy()
        data[date_col] = pd.to_datetime(data[date_col])
        data = data.sort_values(date_col)

        colors = ['red', 'darkred', 'maroon']

        for i, conf_level in enumerate(confidence_levels):
            var_values = data[returns_col].rolling(window=window).quantile(1 - conf_level)
            label = f'VaR {conf_level:.0%}'

            ax.plot(data[date_col], var_values, color=colors[i],
                   linewidth=2, label=label)

            # Fill area for extreme losses
            ax.fill_between(data[date_col], var_values, ax.get_ylim()[0],
                           alpha=0.1, color=colors[i])

        # Plot actual returns
        ax.scatter(data[date_col], data[returns_col], alpha=0.3, s=10, color='blue')

        # Highlight VaR breaches
        for i, conf_level in enumerate(confidence_levels):
            var_values = data[returns_col].rolling(window=window).quantile(1 - conf_level)
            breaches = data[returns_col] < var_values
            if breaches.any():
                breach_dates = data[date_col][breaches]
                breach_returns = data[returns_col][breaches]
                ax.scatter(breach_dates, breach_returns, color=colors[i],
                          s=50, marker='x', label=f'VaR {conf_level:.0%} Breaches')

        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.set_xlabel('Date')
        ax.set_ylabel('Returns')
        ax.set_title('Value at Risk Time Series')
        ax.legend()

        # Format dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        return fig, ax


class DrawdownChart(TimeSeriesRiskPlot):
    """Drawdown analysis visualization."""

    def plot(
        self,
        data: pd.DataFrame,
        date_col: str,
        value_col: str,
        show_underwater: bool = True,
        highlight_max_dd: bool = True,
        **kwargs
    ) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create drawdown chart.

        Parameters
        ----------
        data : pd.DataFrame
            Price or value data
        date_col : str
            Date column
        value_col : str
            Value column
        show_underwater : bool, default True
            Whether to show underwater plot
        highlight_max_dd : bool, default True
            Whether to highlight maximum drawdown
        **kwargs
            Additional arguments

        Returns
        -------
        fig, ax : matplotlib Figure and Axes
        """
        if show_underwater:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=kwargs.get('figsize', (12, 10)),
                                          sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        else:
            fig, ax1 = plt.subplots(figsize=kwargs.get('figsize', (12, 6)))

        data = data.copy()
        data[date_col] = pd.to_datetime(data[date_col])
        data = data.sort_values(date_col)

        # Calculate cumulative values and drawdowns
        cumulative = data[value_col].cumprod() if data[value_col].min() > 0 else data[value_col].cumsum()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max

        # Main price chart
        ax1.plot(data[date_col], cumulative, 'b-', linewidth=2, label='Cumulative Value')
        ax1.plot(data[date_col], running_max, 'g--', alpha=0.7, label='Running Maximum')

        # Highlight maximum drawdown period
        if highlight_max_dd:
            max_dd_idx = drawdown.idxmin()
            max_dd_start = running_max[:max_dd_idx].idxmax()
            max_dd_end = cumulative[max_dd_idx:].idxmax()

            ax1.axvspan(data[date_col].iloc[max_dd_start],
                       data[date_col].iloc[max_dd_end],
                       alpha=0.2, color='red', label='Max Drawdown Period')

        ax1.set_ylabel('Cumulative Value')
        ax1.set_title('Drawdown Analysis')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Underwater plot
        if show_underwater:
            ax2.fill_between(data[date_col], drawdown * 100, 0,
                            color='red', alpha=0.7)
            ax2.set_ylabel('Drawdown (%)')
            ax2.set_xlabel('Date')
            ax2.grid(True, alpha=0.3)

            # Add statistics
            max_dd = drawdown.min() * 100
            avg_dd = drawdown[drawdown < 0].mean() * 100 if (drawdown < 0).any() else 0

            stats_text = f'Max DD: {max_dd:.1f}%\nAvg DD: {avg_dd:.1f}%'
            ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes,
                    verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # Format dates
        bottom_ax = ax2 if show_underwater else ax1
        bottom_ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(bottom_ax.xaxis.get_majorticklabels(), rotation=45)

        plt.tight_layout()
        return fig, (ax1, ax2) if show_underwater else (fig, ax1)


def rolling_risk_metrics(
    data: pd.DataFrame,
    date_col: str,
    returns_col: str,
    window: int = 252,
    **kwargs
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot rolling risk metrics.

    Parameters
    ----------
    data : pd.DataFrame
        Returns data
    date_col : str
        Date column
    returns_col : str
        Returns column
    window : int, default 252
        Rolling window size
    **kwargs
        Additional arguments

    Returns
    -------
    fig, ax : matplotlib Figure and Axes (2x2 subplot)
    """
    fig, axes = plt.subplots(2, 2, figsize=kwargs.get('figsize', (15, 10)))
    fig.suptitle(f'Rolling Risk Metrics ({window}-day window)', fontsize=14)

    data = data.copy()
    data[date_col] = pd.to_datetime(data[date_col])
    data = data.sort_values(date_col)

    # Rolling volatility
    rolling_vol = data[returns_col].rolling(window=window).std() * np.sqrt(252) * 100
    axes[0, 0].plot(data[date_col], rolling_vol, 'b-', linewidth=2)
    axes[0, 0].set_title('Rolling Volatility (%)')
    axes[0, 0].grid(True, alpha=0.3)

    # Rolling Sharpe ratio (assuming 0% risk-free rate)
    rolling_sharpe = (data[returns_col].rolling(window=window).mean() /
                     data[returns_col].rolling(window=window).std()) * np.sqrt(252)
    axes[0, 1].plot(data[date_col], rolling_sharpe, 'g-', linewidth=2)
    axes[0, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[0, 1].set_title('Rolling Sharpe Ratio')
    axes[0, 1].grid(True, alpha=0.3)

    # Rolling VaR 95%
    rolling_var = data[returns_col].rolling(window=window).quantile(0.05) * 100
    axes[1, 0].plot(data[date_col], rolling_var, 'r-', linewidth=2)
    axes[1, 0].set_title('Rolling VaR 95% (%)')
    axes[1, 0].grid(True, alpha=0.3)

    # Rolling skewness
    rolling_skew = data[returns_col].rolling(window=window).skew()
    axes[1, 1].plot(data[date_col], rolling_skew, 'purple', linewidth=2)
    axes[1, 1].axhline(y=0, color='black', linestyle='--', alpha=0.5)
    axes[1, 1].set_title('Rolling Skewness')
    axes[1, 1].grid(True, alpha=0.3)

    # Format all x-axes
    for ax in axes.flat:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

    plt.tight_layout()
    return fig, axes