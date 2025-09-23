#!/usr/bin/env python3
"""
Generate comprehensive visualization examples for RiskPlot documentation
Creates 20 different visualization examples covering all package features
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for professional-looking plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_comprehensive_sample_data():
    """Create extensive realistic financial sample data"""
    np.random.seed(42)

    # Extended portfolio data
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    portfolios = ['US Large Cap', 'US Small Cap', 'European Equity', 'Emerging Markets',
                 'Fixed Income', 'High Yield', 'Commodities', 'REITs', 'Infrastructure']

    # Risk factors
    risk_factors = ['Market', 'Value', 'Momentum', 'Size', 'Quality', 'Volatility', 'Currency']

    # Countries with risk data
    countries = ['USA', 'DEU', 'CHN', 'JPN', 'GBR', 'FRA', 'BRA', 'IND', 'RUS', 'ZAF',
                'CAN', 'AUS', 'KOR', 'MEX', 'IDN', 'TUR', 'POL', 'NLD', 'BEL', 'ESP']

    # Sectors
    sectors = ['Technology', 'Healthcare', 'Financials', 'Consumer Discretionary',
               'Communication Services', 'Industrials', 'Consumer Staples', 'Energy',
               'Utilities', 'Real Estate', 'Materials']

    return {
        'dates': dates,
        'portfolios': portfolios,
        'risk_factors': risk_factors,
        'countries': countries,
        'sectors': sectors
    }

def create_ridge_plots(data, output_dir):
    """Create multiple ridge plot variations"""

    # 1. Portfolio Returns Ridge Plot
    portfolio_data = []
    for portfolio in data['portfolios'][:6]:  # Use subset for clarity
        if 'Fixed Income' in portfolio:
            returns = np.random.normal(0.0003, 0.008, 1000)
        elif 'Emerging' in portfolio:
            returns = np.random.normal(0.0008, 0.025, 1000)
        elif 'Commodities' in portfolio:
            returns = np.random.normal(0.0005, 0.030, 1000)
        else:
            returns = np.random.normal(0.0006, 0.018, 1000)

        for ret in returns:
            portfolio_data.append({'Portfolio': portfolio, 'Return': ret})

    df = pd.DataFrame(portfolio_data)

    fig, axes = plt.subplots(len(df['Portfolio'].unique()), 1, figsize=(12, 10), sharex=True)
    portfolios = df['Portfolio'].unique()
    colors = sns.color_palette("viridis", len(portfolios))

    for i, (portfolio, color) in enumerate(zip(portfolios, colors)):
        data_subset = df[df['Portfolio'] == portfolio]['Return']

        # Create density using numpy histogram
        hist, bin_edges = np.histogram(data_subset, bins=50, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Simple density approximation
        kde_x = np.linspace(data_subset.min(), data_subset.max(), 200)
        kde_y = np.interp(kde_x, bin_centers, hist)

        axes[i].fill_between(kde_x, 0, kde_y, alpha=0.7, color=color)
        axes[i].axvline(data_subset.mean(), color='red', linestyle='--', alpha=0.8, linewidth=2)
        axes[i].set_ylabel(portfolio.replace(' ', '\n'), rotation=0, ha='right', va='center', fontsize=10)
        axes[i].set_ylim(0, kde_y.max() * 1.1)
        axes[i].grid(True, alpha=0.3)

        if i < len(portfolios) - 1:
            axes[i].set_xticks([])

    axes[-1].set_xlabel('Daily Returns')
    plt.suptitle('Return Distribution Comparison Across Asset Classes', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ridge_plot_portfolios.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # 2. Sector Performance Ridge Plot
    sector_data = []
    for sector in data['sectors'][:8]:
        if sector in ['Technology', 'Healthcare']:
            returns = np.random.normal(0.0012, 0.022, 800)
        elif sector in ['Utilities', 'Consumer Staples']:
            returns = np.random.normal(0.0004, 0.012, 800)
        elif sector == 'Energy':
            returns = np.random.normal(0.0002, 0.035, 800)
        else:
            returns = np.random.normal(0.0007, 0.018, 800)

        for ret in returns:
            sector_data.append({'Sector': sector, 'Return': ret})

    df_sectors = pd.DataFrame(sector_data)

    fig, axes = plt.subplots(len(df_sectors['Sector'].unique()), 1, figsize=(12, 12), sharex=True)
    sectors = df_sectors['Sector'].unique()
    colors = sns.color_palette("plasma", len(sectors))

    for i, (sector, color) in enumerate(zip(sectors, colors)):
        data_subset = df_sectors[df_sectors['Sector'] == sector]['Return']

        # Create density using numpy histogram
        hist, bin_edges = np.histogram(data_subset, bins=50, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        # Simple density approximation
        kde_x = np.linspace(data_subset.min(), data_subset.max(), 200)
        kde_y = np.interp(kde_x, bin_centers, hist)

        axes[i].fill_between(kde_x, 0, kde_y, alpha=0.7, color=color)
        axes[i].axvline(data_subset.mean(), color='darkred', linestyle='--', alpha=0.8, linewidth=2)
        axes[i].set_ylabel(sector.replace(' ', '\n'), rotation=0, ha='right', va='center', fontsize=9)
        axes[i].set_ylim(0, kde_y.max() * 1.1)
        axes[i].grid(True, alpha=0.3)

        if i < len(sectors) - 1:
            axes[i].set_xticks([])

    axes[-1].set_xlabel('Daily Returns')
    plt.suptitle('Sector Return Distributions', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ridge_plot_sectors.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_heatmaps(data, output_dir):
    """Create various heatmap visualizations"""

    # 1. Asset Correlation Heatmap
    np.random.seed(42)
    n_assets = len(data['portfolios'])
    correlation_matrix = np.random.randn(n_assets, n_assets)
    correlation_matrix = np.dot(correlation_matrix, correlation_matrix.T)
    d = np.sqrt(np.diag(correlation_matrix))
    correlation_matrix = correlation_matrix / np.outer(d, d)
    np.fill_diagonal(correlation_matrix, 1.0)

    correlation_df = pd.DataFrame(correlation_matrix,
                                 index=data['portfolios'],
                                 columns=data['portfolios'])

    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(correlation_df.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)

    ax.set_xticks(range(len(correlation_df.columns)))
    ax.set_yticks(range(len(correlation_df.index)))
    ax.set_xticklabels(correlation_df.columns, rotation=45, ha='right')
    ax.set_yticklabels(correlation_df.index)

    # Add correlation values
    for i in range(len(correlation_df.index)):
        for j in range(len(correlation_df.columns)):
            value = correlation_df.iloc[i, j]
            color = "white" if abs(value) > 0.6 else "black"
            ax.text(j, i, f'{value:.2f}', ha="center", va="center",
                   color=color, fontweight='bold', fontsize=8)

    ax.set_title('Asset Class Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'heatmap_correlations.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # 2. Risk Factor Heatmap
    factor_data = np.random.randn(len(data['risk_factors']), len(data['portfolios'][:7]))
    factor_df = pd.DataFrame(factor_data,
                           index=data['risk_factors'],
                           columns=data['portfolios'][:7])

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(factor_df.values, cmap='RdYlGn', vmin=-2, vmax=2, aspect='auto')

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Factor Exposure', rotation=270, labelpad=20)

    ax.set_xticks(range(len(factor_df.columns)))
    ax.set_yticks(range(len(factor_df.index)))
    ax.set_xticklabels(factor_df.columns, rotation=45, ha='right')
    ax.set_yticklabels(factor_df.index)

    # Add exposure values
    for i in range(len(factor_df.index)):
        for j in range(len(factor_df.columns)):
            value = factor_df.iloc[i, j]
            color = "white" if abs(value) > 1.2 else "black"
            ax.text(j, i, f'{value:.1f}', ha="center", va="center",
                   color=color, fontweight='bold', fontsize=9)

    ax.set_title('Risk Factor Exposure Heatmap', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'heatmap_risk_factors.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # 3. Country Risk Heatmap
    country_metrics = ['Political Risk', 'Economic Risk', 'Financial Risk', 'Composite Risk']
    country_data = np.random.uniform(20, 80, (len(country_metrics), len(data['countries'][:15])))
    country_df = pd.DataFrame(country_data,
                            index=country_metrics,
                            columns=data['countries'][:15])

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(country_df.values, cmap='RdYlGn_r', vmin=20, vmax=80, aspect='auto')

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Risk Score (0-100)', rotation=270, labelpad=20)

    ax.set_xticks(range(len(country_df.columns)))
    ax.set_yticks(range(len(country_df.index)))
    ax.set_xticklabels(country_df.columns, rotation=45, ha='right')
    ax.set_yticklabels(country_df.index)

    # Add risk scores
    for i in range(len(country_df.index)):
        for j in range(len(country_df.columns)):
            value = country_df.iloc[i, j]
            color = "white" if value > 60 else "black"
            ax.text(j, i, f'{value:.0f}', ha="center", va="center",
                   color=color, fontweight='bold', fontsize=8)

    ax.set_title('Country Risk Assessment Matrix', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'heatmap_country_risk.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_waterfall_charts(data, output_dir):
    """Create various waterfall chart examples"""

    # 1. Portfolio Return Attribution
    factors = ['Market Beta', 'Size Factor', 'Value Factor', 'Momentum', 'Quality', 'Low Vol', 'Currency', 'Alpha']
    contributions = [0.045, 0.012, -0.008, 0.015, 0.003, -0.002, -0.005, 0.008]

    fig, ax = plt.subplots(figsize=(12, 8))

    cumulative = 0
    x_positions = range(len(factors) + 1)  # +1 for total

    for i, (factor, contrib) in enumerate(zip(factors, contributions)):
        color = 'green' if contrib > 0 else 'red'
        ax.bar(i, contrib, bottom=cumulative, color=color, alpha=0.7,
               edgecolor='black', linewidth=1, width=0.6)

        # Add value labels
        ax.text(i, cumulative + contrib/2, f'{contrib:+.1%}',
                ha='center', va='center', fontweight='bold', color='white', fontsize=10)

        cumulative += contrib

    # Add total bar
    ax.bar(len(factors), cumulative, color='darkblue', alpha=0.8,
           edgecolor='black', linewidth=1, width=0.6)
    ax.text(len(factors), cumulative/2, f'{cumulative:+.1%}',
            ha='center', va='center', fontweight='bold', color='white', fontsize=12)

    # Customize plot
    ax.set_xticks(list(range(len(factors))) + [len(factors)])
    ax.set_xticklabels(factors + ['Total Return'], rotation=45, ha='right')
    ax.set_ylabel('Contribution to Return')
    ax.set_title('Portfolio Return Attribution Analysis', fontsize=16, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.axhline(y=0, color='black', linewidth=0.8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'waterfall_attribution.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    # 2. Risk Budget Decomposition
    risk_sources = ['Equity Risk', 'Credit Risk', 'Interest Rate Risk', 'Currency Risk', 'Commodity Risk', 'Concentration Risk']
    risk_contributions = [0.012, 0.008, 0.003, 0.002, 0.004, 0.001]

    fig, ax = plt.subplots(figsize=(10, 6))

    cumulative = 0
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']

    for i, (source, contrib, color) in enumerate(zip(risk_sources, risk_contributions, colors)):
        ax.bar(i, contrib, bottom=cumulative, color=color, alpha=0.8,
               edgecolor='black', linewidth=1, width=0.7)

        ax.text(i, cumulative + contrib/2, f'{contrib:.1%}',
                ha='center', va='center', fontweight='bold', color='black', fontsize=10)

        cumulative += contrib

    # Add total risk bar
    ax.bar(len(risk_sources), cumulative, color='darkred', alpha=0.9,
           edgecolor='black', linewidth=2, width=0.7)
    ax.text(len(risk_sources), cumulative/2, f'{cumulative:.1%}',
            ha='center', va='center', fontweight='bold', color='white', fontsize=12)

    ax.set_xticks(list(range(len(risk_sources))) + [len(risk_sources)])
    ax.set_xticklabels(risk_sources + ['Total Risk'], rotation=45, ha='right')
    ax.set_ylabel('Risk Contribution (VaR)')
    ax.set_title('Portfolio Risk Budget Decomposition', fontsize=16, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'waterfall_risk_budget.png'), dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def main():
    """Generate all comprehensive visualizations"""
    output_dir = '/home/ocedi/projects/riskplot/docs/assets/images'
    os.makedirs(output_dir, exist_ok=True)

    print("Creating comprehensive sample data...")
    data = create_comprehensive_sample_data()

    print("Generating ridge plots...")
    create_ridge_plots(data, output_dir)

    print("Generating heatmaps...")
    create_heatmaps(data, output_dir)

    print("Generating waterfall charts...")
    create_waterfall_charts(data, output_dir)

    print(f"Comprehensive visualizations saved to {output_dir}")

if __name__ == "__main__":
    main()