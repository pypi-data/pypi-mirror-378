#!/usr/bin/env python3
"""
VaR Time Series Example - Track Value at Risk over time
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import riskplot

def create_sample_data():
    """Generate sample VaR time series data"""
    np.random.seed(42)

    # Generate daily data for 2 years
    dates = pd.date_range(start='2022-01-01', end='2023-12-31', freq='D')

    # Simulate returns and VaR
    returns = np.random.normal(0.0005, 0.02, len(dates))

    # Calculate rolling VaR (5th percentile)
    var_data = []
    for i in range(30, len(dates)):  # Start after 30-day window
        window_returns = returns[i-30:i]
        var_95 = np.percentile(window_returns, 5)
        var_data.append({
            'Date': dates[i],
            'Return': returns[i],
            'VaR_95': var_95,
            'Portfolio_Value': 1000000  # $1M portfolio
        })

    return pd.DataFrame(var_data)

def main():
    # Create sample VaR data
    data = create_sample_data()

    # Create VaR time series plot
    fig, ax = riskplot.VaRTimeSeries(
        data,
        date_col='Date',
        return_col='Return',
        var_col='VaR_95',
        title='Portfolio VaR Monitoring (95% Confidence)'
    )

    # Customize plot
    ax.set_ylabel('Daily Return / VaR')
    plt.tight_layout()

    # Save plot
    plt.savefig('var_timeseries_example.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()