#!/usr/bin/env python3
"""
Correlation Heatmap Example - Visualize asset correlations
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import riskplot

def create_sample_data():
    """Generate sample correlation matrix data"""
    np.random.seed(42)

    # Asset names
    assets = ['US Stocks', 'EU Stocks', 'EM Stocks', 'Bonds', 'Gold', 'Oil', 'REITs']

    # Create realistic correlation matrix
    n_assets = len(assets)
    correlation_matrix = np.random.randn(n_assets, n_assets)
    correlation_matrix = np.dot(correlation_matrix, correlation_matrix.T)

    # Normalize to correlation matrix
    d = np.sqrt(np.diag(correlation_matrix))
    correlation_matrix = correlation_matrix / np.outer(d, d)

    # Ensure diagonal is 1
    np.fill_diagonal(correlation_matrix, 1.0)

    return pd.DataFrame(correlation_matrix, index=assets, columns=assets)

def main():
    # Create sample correlation data
    correlation_data = create_sample_data()

    # Create correlation heatmap
    fig, ax = riskplot.correlation_heatmap(
        correlation_data,
        title='Asset Class Correlation Matrix'
    )

    # Save plot
    plt.savefig('correlation_heatmap_example.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()