#!/usr/bin/env python3
"""
Ridge Plot Example - Compare distributions across categories
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import riskplot

def create_sample_data():
    """Generate sample portfolio return data"""
    np.random.seed(42)

    # Portfolio return data
    portfolios = ['US Equity', 'European Equity', 'Emerging Markets', 'Fixed Income']
    data = []

    for portfolio in portfolios:
        # Different risk/return profiles
        if 'Fixed Income' in portfolio:
            returns = np.random.normal(0.03, 0.05, 1000)  # Lower risk/return
        elif 'Emerging' in portfolio:
            returns = np.random.normal(0.08, 0.20, 1000)  # Higher risk/return
        else:
            returns = np.random.normal(0.06, 0.15, 1000)  # Moderate risk/return

        for ret in returns:
            data.append({'Portfolio': portfolio, 'Return': ret})

    return pd.DataFrame(data)

def main():
    # Create sample data
    data = create_sample_data()

    # Create ridge plot
    fig, ax = riskplot.ridge_plot(
        data,
        category_col='Portfolio',
        value_col='Return',
        title='Portfolio Return Distributions'
    )

    # Customize plot
    ax.set_xlabel('Daily Return (%)')
    plt.tight_layout()

    # Save plot
    plt.savefig('ridge_plot_example.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()