#!/usr/bin/env python3
"""
Waterfall Chart Example - Portfolio return attribution
"""
import pandas as pd
import matplotlib.pyplot as plt
import riskplot

def create_sample_data():
    """Generate sample attribution data"""
    # P&L attribution factors
    data = pd.DataFrame({
        'Factor': ['Market Return', 'Sector Allocation', 'Security Selection',
                  'Currency Impact', 'Fees & Other'],
        'Contribution': [0.045, 0.012, -0.008, 0.003, -0.002]
    })
    return data

def main():
    # Create sample attribution data
    data = create_sample_data()

    # Create waterfall chart
    fig, ax = riskplot.pnl_waterfall(
        data,
        category_col='Factor',
        value_col='Contribution',
        title='Portfolio Return Attribution'
    )

    # Customize plot
    ax.set_ylabel('Contribution to Return (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save plot
    plt.savefig('waterfall_chart_example.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()