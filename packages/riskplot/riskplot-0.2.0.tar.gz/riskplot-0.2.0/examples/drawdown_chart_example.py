#!/usr/bin/env python3
"""
Drawdown Chart Example - Visualize portfolio drawdowns
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import riskplot

def create_sample_data():
    """Generate sample portfolio data with drawdowns"""
    np.random.seed(42)

    # Generate daily data for 3 years
    dates = pd.date_range(start='2021-01-01', end='2023-12-31', freq='D')

    # Simulate portfolio returns
    returns = np.random.normal(0.0008, 0.018, len(dates))

    # Calculate cumulative returns and drawdowns
    cumulative_returns = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative_returns)
    drawdown = (cumulative_returns - running_max) / running_max

    data = pd.DataFrame({
        'Date': dates,
        'Cumulative_Return': cumulative_returns,
        'Drawdown': drawdown,
        'Portfolio_Value': 1000000 * cumulative_returns
    })

    return data

def main():
    # Create sample drawdown data
    data = create_sample_data()

    # Create drawdown chart
    fig, ax = riskplot.DrawdownChart(
        data,
        date_col='Date',
        drawdown_col='Drawdown',
        title='Portfolio Drawdown Analysis'
    )

    # Customize plot
    ax.set_ylabel('Drawdown (%)')
    plt.tight_layout()

    # Save plot
    plt.savefig('drawdown_chart_example.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()