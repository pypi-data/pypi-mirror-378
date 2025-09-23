#!/usr/bin/env python3
"""
Network Analysis Example - Financial institution connections
"""
import pandas as pd
import matplotlib.pyplot as plt
import riskplot

def create_sample_data():
    """Generate sample network data"""
    # Financial institution connections (exposures)
    data = pd.DataFrame({
        'Source': ['Bank A', 'Bank A', 'Bank B', 'Bank B', 'Bank C',
                  'Bank C', 'Bank D', 'Bank D', 'Bank E'],
        'Target': ['Bank B', 'Bank C', 'Bank C', 'Bank D', 'Bank D',
                  'Bank E', 'Bank E', 'Bank A', 'Bank A'],
        'Exposure': [50, 30, 40, 60, 25, 35, 45, 20, 15]  # Millions USD
    })
    return data

def main():
    # Create sample network data
    data = create_sample_data()

    # Create network plot (requires networkx)
    try:
        fig, ax = riskplot.financial_network(
            data,
            source_col='Source',
            target_col='Target',
            weight_col='Exposure',
            title='Financial Institution Network'
        )

        # Save plot
        plt.savefig('network_analysis_example.png', dpi=300, bbox_inches='tight')
        plt.show()

    except ImportError:
        print("NetworkX not installed. Install with: pip install riskplot[network]")

        # Create simple alternative visualization
        fig, ax = plt.subplots(figsize=(10, 6))

        # Aggregate exposures by source
        source_totals = data.groupby('Source')['Exposure'].sum()

        ax.bar(source_totals.index, source_totals.values)
        ax.set_title('Total Exposures by Institution')
        ax.set_ylabel('Exposure (Millions USD)')
        plt.xticks(rotation=45)
        plt.tight_layout()

        plt.savefig('network_analysis_example.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    main()