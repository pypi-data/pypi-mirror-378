"""
Comprehensive demonstration of all riskplot features.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import riskplot as rp


def create_sample_data():
    """Create comprehensive sample datasets."""
    np.random.seed(42)

    # 1. Credit rating data (for ridge plots)
    companies = ['CompanyA', 'CompanyB', 'CompanyC', 'CompanyD', 'CompanyE']
    rating_order = ['c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa']

    ridge_data = []
    for company in companies:
        for source in ['cb', 'sp']:
            if 'A' in company or 'B' in company:
                ratings = np.random.choice(rating_order[3:], size=50, p=[0.1, 0.2, 0.3, 0.4])
            else:
                ratings = np.random.choice(rating_order[:5], size=40, p=[0.1, 0.2, 0.3, 0.25, 0.15])

            for rating in ratings:
                ridge_data.append({'company': company, 'rating': rating, 'source': source})

    ridge_df = pd.DataFrame(ridge_data)

    # 2. Risk attribution data (for waterfall charts)
    attribution_data = pd.DataFrame({
        'factor': ['Equity Risk', 'Credit Risk', 'FX Risk', 'Interest Rate Risk', 'Idiosyncratic'],
        'contribution': [0.025, -0.015, 0.008, -0.012, 0.003]
    })

    # 3. Correlation matrix data (for heatmaps)
    asset_returns = pd.DataFrame({
        'Equities': np.random.normal(0.08, 0.15, 252),
        'Bonds': np.random.normal(0.04, 0.08, 252),
        'Commodities': np.random.normal(0.06, 0.20, 252),
        'Real Estate': np.random.normal(0.07, 0.12, 252),
        'Cash': np.random.normal(0.02, 0.01, 252)
    })

    # Add some correlation structure
    asset_returns['Bonds'] = 0.3 * asset_returns['Equities'] + 0.7 * asset_returns['Bonds']
    asset_returns['Real Estate'] = 0.6 * asset_returns['Equities'] + 0.4 * asset_returns['Real Estate']

    # 4. Risk matrix data
    risk_events = pd.DataFrame({
        'event': ['Cyber Attack', 'Market Crash', 'Regulatory Change', 'Credit Event', 'Operational Risk'],
        'probability': [0.7, 0.2, 0.8, 0.3, 0.6],
        'impact': [0.8, 0.9, 0.4, 0.7, 0.5]
    })

    # 5. Time series data
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    portfolio_returns = np.random.normal(0.0005, 0.012, len(dates))

    # Add some regime changes and volatility clustering
    portfolio_returns[500:600] = np.random.normal(-0.002, 0.025, 100)  # Crisis period
    portfolio_returns[1000:1100] = np.random.normal(0.001, 0.008, 100)  # Low vol period

    timeseries_df = pd.DataFrame({
        'date': dates,
        'returns': portfolio_returns,
        'portfolio_value': (1 + pd.Series(portfolio_returns)).cumprod() * 100
    })

    return ridge_df, attribution_data, asset_returns, risk_events, timeseries_df


def demo_ridge_plots(ridge_df):
    """Demonstrate ridge plot functionality."""
    print("Creating ridge plots...")

    # Basic ridge plot
    fig1, ax1 = rp.ridge_plot(
        ridge_df,
        category_col='company',
        value_col='rating',
        group_col='source',
        figsize=(12, 8),
        title='Credit Rating Distributions: CB vs SP'
    )
    plt.show()

    # Single group ridge plot
    cb_only = ridge_df[ridge_df['source'] == 'cb']
    fig2, ax2 = rp.ridge_plot(
        cb_only,
        category_col='company',
        value_col='rating',
        figsize=(10, 6),
        title='CB Credit Rating Distributions'
    )
    plt.show()


def demo_heatmaps(asset_returns, risk_events):
    """Demonstrate heatmap functionality."""
    print("Creating heatmaps...")

    # Correlation heatmap
    fig1, ax1 = rp.correlation_heatmap(
        asset_returns,
        figsize=(8, 6),
        title='Asset Class Correlation Matrix'
    )
    plt.show()

    # Risk matrix
    fig2, ax2 = rp.risk_matrix(
        risk_events,
        probability_col='probability',
        impact_col='impact',
        label_col='event',
        figsize=(10, 8)
    )
    plt.show()


def demo_waterfall_charts(attribution_data):
    """Demonstrate waterfall chart functionality."""
    print("Creating waterfall charts...")

    # Risk attribution waterfall
    fig1, ax1 = rp.risk_attribution_waterfall(
        attribution_data,
        factor_col='factor',
        contribution_col='contribution',
        base_return=0.05,
        figsize=(12, 6)
    )
    plt.show()

    # P&L waterfall example
    pnl_data = pd.DataFrame({
        'component': ['Interest Income', 'Credit Losses', 'Trading Income', 'Operating Expenses'],
        'amount': [125, -45, 78, -95]
    })

    fig2, ax2 = rp.pnl_waterfall(
        pnl_data,
        component_col='component',
        pnl_col='amount',
        starting_value=1000,
        figsize=(10, 6)
    )
    plt.show()


def demo_distribution_plots(asset_returns):
    """Demonstrate distribution plot functionality."""
    print("Creating distribution plots...")

    # Violin plots
    returns_long = pd.melt(asset_returns.reset_index(), id_vars=['index'],
                          var_name='asset', value_name='returns')

    violin_plot = rp.ViolinPlot()
    fig1, ax1 = violin_plot.plot(
        returns_long,
        category_col='asset',
        value_col='returns',
        figsize=(12, 6),
        title='Asset Return Distributions'
    )
    plt.show()

    # Distribution summary for one asset
    equity_df = pd.DataFrame({'returns': asset_returns['Equities']})
    fig2, axes2 = rp.risk_distribution_summary(
        equity_df,
        value_col='returns',
        figsize=(12, 10)
    )
    plt.show()


def demo_timeseries_plots(timeseries_df):
    """Demonstrate time series plot functionality."""
    print("Creating time series plots...")

    # Basic time series with rolling statistics
    ts_plot = rp.TimeSeriesRiskPlot()
    fig1, ax1 = ts_plot.plot(
        timeseries_df,
        date_col='date',
        value_col='returns',
        rolling_window=30,
        show_volatility=True,
        figsize=(14, 6),
        title='Portfolio Returns with 30-day Moving Average'
    )
    plt.show()

    # VaR time series
    var_plot = rp.VaRTimeSeries()
    fig2, ax2 = var_plot.plot(
        timeseries_df,
        date_col='date',
        returns_col='returns',
        confidence_levels=[0.95, 0.99],
        window=60,
        figsize=(14, 8)
    )
    plt.show()

    # Drawdown analysis
    drawdown_plot = rp.DrawdownChart()
    fig3, (ax3, ax4) = drawdown_plot.plot(
        timeseries_df,
        date_col='date',
        value_col='portfolio_value',
        show_underwater=True,
        figsize=(14, 10)
    )
    plt.show()

    # Rolling risk metrics
    fig4, axes4 = rp.rolling_risk_metrics(
        timeseries_df,
        date_col='date',
        returns_col='returns',
        window=60,
        figsize=(15, 10)
    )
    plt.show()


def demo_advanced_features():
    """Demonstrate advanced framework features."""
    print("Demonstrating advanced features...")

    # Custom plot configuration
    custom_config = rp.PlotConfig(
        figsize=(12, 8),
        style='seaborn',
        colormap='plasma',
        alpha=0.8,
        font_size=12
    )

    # Using base class directly
    class CustomRiskPlot(rp.RiskVisualization):
        def plot(self, data, **kwargs):
            fig, ax = self._setup_figure(**kwargs)
            # Custom plotting logic here
            ax.text(0.5, 0.5, 'Custom Risk Visualization',
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=16)
            return fig, ax

    custom_plot = CustomRiskPlot(config=custom_config)
    fig, ax = custom_plot.plot(pd.DataFrame(), title='Custom Plot')
    plt.show()

    # Color scheme utilities
    risk_colors = rp.ColorScheme.get_risk_palette(5)
    print(f"Risk color palette: {risk_colors}")

    rating_colors = rp.ColorScheme.get_rating_palette()
    print(f"Rating colors: {rating_colors}")


if __name__ == "__main__":
    print("RiskPlot Comprehensive Demo")
    print("=" * 40)

    # Create sample data
    ridge_df, attribution_data, asset_returns, risk_events, timeseries_df = create_sample_data()

    # Run all demonstrations
    demo_ridge_plots(ridge_df)
    demo_heatmaps(asset_returns, risk_events)
    demo_waterfall_charts(attribution_data)
    demo_distribution_plots(asset_returns)
    demo_timeseries_plots(timeseries_df)
    demo_advanced_features()

    print("\nDemo completed! All chart types demonstrated.")