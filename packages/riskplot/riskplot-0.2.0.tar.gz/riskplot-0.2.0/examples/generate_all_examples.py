#!/usr/bin/env python3
"""
Generate all visualization examples for RiskPlot documentation and testing
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Ensure we can import riskplot
sys.path.insert(0, '/home/ocedi/projects/riskplot')

# Set style for professional-looking plots
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def create_sample_data():
    """Create realistic financial sample data"""
    np.random.seed(42)

    # Portfolio returns data
    dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
    portfolios = ['US Equity', 'European Equity', 'Emerging Markets', 'Fixed Income', 'Commodities']

    returns_data = []
    for portfolio in portfolios:
        if 'Equity' in portfolio:
            mean_return = 0.0008 + np.random.normal(0, 0.0002)
            volatility = 0.015 + np.random.normal(0, 0.003)
        elif 'Fixed Income' in portfolio:
            mean_return = 0.0003 + np.random.normal(0, 0.0001)
            volatility = 0.005 + np.random.normal(0, 0.001)
        else:  # Commodities
            mean_return = 0.0005 + np.random.normal(0, 0.0003)
            volatility = 0.025 + np.random.normal(0, 0.005)

        returns = np.random.normal(mean_return, volatility, len(dates))

        for i, (date, ret) in enumerate(zip(dates, returns)):
            returns_data.append({
                'date': date,
                'portfolio': portfolio,
                'return': ret,
                'cumulative_return': np.sum(returns[:i+1])
            })

    returns_df = pd.DataFrame(returns_data)

    # Risk metrics data
    risk_data = pd.DataFrame({
        'portfolio': portfolios,
        'var_95': [-0.024, -0.022, -0.035, -0.008, -0.041],
        'expected_shortfall': [-0.035, -0.032, -0.052, -0.012, -0.061],
        'max_drawdown': [-0.185, -0.156, -0.287, -0.043, -0.312],
        'sharpe_ratio': [0.85, 0.72, 0.58, 0.45, 0.31],
        'volatility': [0.158, 0.142, 0.235, 0.048, 0.278]
    })

    # Country risk data
    countries = ['USA', 'DEU', 'CHN', 'JPN', 'GBR', 'FRA', 'BRA', 'IND', 'RUS', 'ZAF']
    country_data = pd.DataFrame({
        'country': countries,
        'risk_score': [25, 18, 45, 22, 28, 20, 52, 48, 68, 44],
        'gdp_growth': [2.1, 1.8, 6.2, 0.9, 1.5, 1.7, 2.8, 6.8, -0.2, 1.2],
        'debt_to_gdp': [108, 69, 67, 256, 102, 115, 89, 74, 18, 70]
    })

    return returns_df, risk_data, country_data

def create_ridge_plot_example(returns_df, output_dir):
    """Create ridge plot example"""
    fig, axes = plt.subplots(len(returns_df['portfolio'].unique()), 1,
                            figsize=(10, 8), sharex=True)

    portfolios = returns_df['portfolio'].unique()
    colors = sns.color_palette("husl", len(portfolios))

    for i, (portfolio, color) in enumerate(zip(portfolios, colors)):
        data = returns_df[returns_df['portfolio'] == portfolio]['return']

        # Create density plot
        axes[i].fill_between(np.linspace(data.min(), data.max(), 100),
                           0,
                           np.histogram(data, bins=100, density=True)[0].max() *
                           np.exp(-0.5 * ((np.linspace(data.min(), data.max(), 100) - data.mean()) / data.std())**2),
                           alpha=0.7, color=color)

        axes[i].axvline(data.mean(), color='black', linestyle='--', alpha=0.8, linewidth=1)
        axes[i].set_ylabel(portfolio, rotation=0, ha='right', va='center')
        axes[i].set_ylim(0, None)
        axes[i].grid(True, alpha=0.3)

        if i < len(portfolios) - 1:
            axes[i].set_xticks([])

    axes[-1].set_xlabel('Daily Returns')
    plt.suptitle('Return Distribution Comparison Across Portfolios', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'ridge_plot_example.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_heatmap_example(returns_df, output_dir):
    """Create correlation heatmap example"""
    # Create correlation matrix
    pivot_data = returns_df.pivot_table(values='return',
                                      index='date',
                                      columns='portfolio')
    correlation_matrix = pivot_data.corr()

    fig, ax = plt.subplots(figsize=(8, 6))

    # Create heatmap
    im = ax.imshow(correlation_matrix.values, cmap='RdYlBu_r',
                  vmin=-1, vmax=1, aspect='auto')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20)

    # Set ticks and labels
    ax.set_xticks(range(len(correlation_matrix.columns)))
    ax.set_yticks(range(len(correlation_matrix.index)))
    ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
    ax.set_yticklabels(correlation_matrix.index)

    # Add correlation values
    for i in range(len(correlation_matrix.index)):
        for j in range(len(correlation_matrix.columns)):
            text = ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                         ha="center", va="center", color="white" if abs(correlation_matrix.iloc[i, j]) > 0.5 else "black",
                         fontweight='bold')

    ax.set_title('Portfolio Correlation Matrix', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'heatmap_example.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_waterfall_example(risk_data, output_dir):
    """Create waterfall chart example"""
    # Create P&L attribution data
    factors = ['Market Return', 'Sector Allocation', 'Security Selection', 'Currency', 'Other']
    contributions = [0.045, 0.012, -0.008, 0.003, -0.002]

    fig, ax = plt.subplots(figsize=(10, 6))

    cumulative = 0
    colors = ['green' if x > 0 else 'red' for x in contributions]

    x_positions = range(len(factors))

    for i, (factor, contrib, color) in enumerate(zip(factors, contributions, colors)):
        ax.bar(i, contrib, bottom=cumulative, color=color, alpha=0.7,
               edgecolor='black', linewidth=1)

        # Add value labels
        ax.text(i, cumulative + contrib/2, f'{contrib:+.1%}',
                ha='center', va='center', fontweight='bold', color='white')

        cumulative += contrib

    # Add total bar
    ax.bar(len(factors), cumulative, color='darkblue', alpha=0.8,
           edgecolor='black', linewidth=1)
    ax.text(len(factors), cumulative/2, f'{cumulative:+.1%}',
            ha='center', va='center', fontweight='bold', color='white')

    # Customize plot
    ax.set_xticks(list(x_positions) + [len(factors)])
    ax.set_xticklabels(factors + ['Total Return'], rotation=45, ha='right')
    ax.set_ylabel('Contribution to Return')
    ax.set_title('Portfolio Return Attribution Analysis', fontsize=14, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.axhline(y=0, color='black', linewidth=0.8)

    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'waterfall_example.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_timeseries_example(returns_df, output_dir):
    """Create time series risk plot example"""
    # Calculate rolling VaR
    portfolio_data = returns_df[returns_df['portfolio'] == 'US Equity'].copy()
    portfolio_data['rolling_var'] = portfolio_data['return'].rolling(window=30).quantile(0.05)
    portfolio_data['rolling_vol'] = portfolio_data['return'].rolling(window=30).std()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot 1: Returns and VaR
    ax1.plot(portfolio_data['date'], portfolio_data['return'],
             alpha=0.6, color='blue', linewidth=0.5, label='Daily Returns')
    ax1.plot(portfolio_data['date'], portfolio_data['rolling_var'],
             color='red', linewidth=2, label='30-day VaR (95%)')
    ax1.fill_between(portfolio_data['date'], portfolio_data['rolling_var'], 0,
                     alpha=0.3, color='red')
    ax1.set_ylabel('Returns')
    ax1.set_title('US Equity Portfolio: Returns and Value at Risk', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))

    # Plot 2: Rolling volatility
    ax2.plot(portfolio_data['date'], portfolio_data['rolling_vol'],
             color='orange', linewidth=2, label='30-day Volatility')
    ax2.fill_between(portfolio_data['date'], portfolio_data['rolling_vol'], 0,
                     alpha=0.3, color='orange')
    ax2.set_ylabel('Volatility')
    ax2.set_xlabel('Date')
    ax2.set_title('Rolling 30-day Volatility', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'timeseries_example.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_risk_matrix_example(output_dir):
    """Create risk matrix example"""
    # Risk events data
    data = pd.DataFrame({
        'Risk_Event': ['Market Crash', 'Credit Event', 'Operational Risk',
                      'Regulatory Change', 'Cyber Attack', 'Liquidity Crisis'],
        'Probability': [0.2, 0.1, 0.4, 0.6, 0.3, 0.15],
        'Impact': [0.9, 0.8, 0.3, 0.4, 0.6, 0.7]
    })

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create scatter plot with size based on combined risk
    combined_risk = data['Probability'] * data['Impact']
    colors = ['red' if risk > 0.3 else 'yellow' if risk > 0.15 else 'green' for risk in combined_risk]

    scatter = ax.scatter(data['Probability'], data['Impact'],
                        s=combined_risk * 1000, c=colors, alpha=0.7, edgecolors='black')

    # Add labels for each point
    for i, event in enumerate(data['Risk_Event']):
        ax.annotate(event, (data['Probability'].iloc[i], data['Impact'].iloc[i]),
                   xytext=(5, 5), textcoords='offset points', fontsize=10, fontweight='bold')

    # Add grid zones
    ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)

    # Zone labels
    ax.text(0.25, 0.75, 'Low Probability\nHigh Impact', ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    ax.text(0.75, 0.75, 'High Probability\nHigh Impact', ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))
    ax.text(0.25, 0.25, 'Low Probability\nLow Impact', ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))
    ax.text(0.75, 0.25, 'High Probability\nLow Impact', ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='orange', alpha=0.3))

    ax.set_xlabel('Probability of Occurrence', fontsize=12, fontweight='bold')
    ax.set_ylabel('Impact Severity', fontsize=12, fontweight='bold')
    ax.set_title('Risk Assessment Matrix', fontsize=14, fontweight='bold')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'risk_matrix_example.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_drawdown_example(returns_df, output_dir):
    """Create drawdown chart example"""
    # Use US Equity data for drawdown calculation
    portfolio_data = returns_df[returns_df['portfolio'] == 'US Equity'].copy()

    # Calculate cumulative returns and drawdowns
    portfolio_data['cumulative_return'] = (1 + portfolio_data['return']).cumprod()
    portfolio_data['running_max'] = portfolio_data['cumulative_return'].expanding().max()
    portfolio_data['drawdown'] = (portfolio_data['cumulative_return'] - portfolio_data['running_max']) / portfolio_data['running_max']

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Plot 1: Cumulative returns
    ax1.plot(portfolio_data['date'], portfolio_data['cumulative_return'],
             color='blue', linewidth=2, label='Cumulative Returns')
    ax1.plot(portfolio_data['date'], portfolio_data['running_max'],
             color='green', linewidth=2, alpha=0.7, label='High Water Mark')
    ax1.set_ylabel('Cumulative Return')
    ax1.set_title('Portfolio Performance and Drawdowns', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot 2: Drawdowns
    ax2.fill_between(portfolio_data['date'], portfolio_data['drawdown'], 0,
                     color='red', alpha=0.7, label='Drawdown')
    ax2.plot(portfolio_data['date'], portfolio_data['drawdown'],
             color='darkred', linewidth=1)
    ax2.set_ylabel('Drawdown')
    ax2.set_xlabel('Date')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'drawdown_example.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def create_country_risk_example(country_data, output_dir):
    """Create country risk bar chart"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Sort by risk score
    data_sorted = country_data.sort_values('risk_score')

    # Color bars by risk level
    colors = ['green' if score < 30 else 'yellow' if score < 50 else 'red'
             for score in data_sorted['risk_score']]

    bars = ax.bar(data_sorted['country'], data_sorted['risk_score'],
                  color=colors, alpha=0.7, edgecolor='black')

    # Add value labels on bars
    for bar, score in zip(bars, data_sorted['risk_score']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
               f'{score}', ha='center', va='bottom', fontweight='bold')

    ax.set_title('Country Risk Assessment', fontsize=14, fontweight='bold')
    ax.set_ylabel('Risk Score (0-100)')
    ax.set_xlabel('Country')
    plt.xticks(rotation=45, ha='right')

    # Add risk level legend
    import matplotlib.patches as mpatches
    green_patch = mpatches.Patch(color='green', alpha=0.7, label='Low Risk (<30)')
    yellow_patch = mpatches.Patch(color='yellow', alpha=0.7, label='Medium Risk (30-50)')
    red_patch = mpatches.Patch(color='red', alpha=0.7, label='High Risk (>50)')
    ax.legend(handles=[green_patch, yellow_patch, red_patch])

    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'country_risk_example.png'),
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

def main():
    """Generate all documentation images"""
    output_dir = '/home/ocedi/projects/riskplot/docs/assets/images'
    os.makedirs(output_dir, exist_ok=True)

    print("Generating sample data...")
    returns_df, risk_data, country_data = create_sample_data()

    print("Creating ridge plot example...")
    create_ridge_plot_example(returns_df, output_dir)

    print("Creating heatmap example...")
    create_heatmap_example(returns_df, output_dir)

    print("Creating waterfall chart example...")
    create_waterfall_example(risk_data, output_dir)

    print("Creating time series example...")
    create_timeseries_example(returns_df, output_dir)

    print("Creating risk matrix example...")
    create_risk_matrix_example(output_dir)

    print("Creating drawdown example...")
    create_drawdown_example(returns_df, output_dir)

    print("Creating country risk example...")
    create_country_risk_example(country_data, output_dir)

    print(f"All visualization examples saved to {output_dir}")

if __name__ == "__main__":
    main()