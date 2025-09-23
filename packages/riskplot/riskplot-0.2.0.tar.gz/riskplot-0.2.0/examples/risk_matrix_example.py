#!/usr/bin/env python3
"""
Risk Matrix Example - Probability vs Impact visualization
"""
import pandas as pd
import matplotlib.pyplot as plt
import riskplot

def create_sample_data():
    """Generate sample risk data"""
    # Risk events with probability and impact
    data = pd.DataFrame({
        'Risk_Event': ['Market Crash', 'Credit Event', 'Operational Risk',
                      'Regulatory Change', 'Cyber Attack', 'Liquidity Crisis',
                      'Interest Rate Shock', 'Currency Crisis'],
        'Probability': [0.2, 0.1, 0.4, 0.6, 0.3, 0.15, 0.5, 0.25],
        'Impact': [0.9, 0.8, 0.3, 0.4, 0.6, 0.7, 0.5, 0.8]
    })
    return data

def main():
    # Create sample risk data
    data = create_sample_data()

    # Create risk matrix
    fig, ax = riskplot.risk_matrix(
        data,
        x_col='Probability',
        y_col='Impact',
        label_col='Risk_Event',
        title='Risk Assessment Matrix'
    )

    # Customize plot
    ax.set_xlabel('Probability of Occurrence')
    ax.set_ylabel('Impact Severity')
    plt.tight_layout()

    # Save plot
    plt.savefig('risk_matrix_example.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    main()