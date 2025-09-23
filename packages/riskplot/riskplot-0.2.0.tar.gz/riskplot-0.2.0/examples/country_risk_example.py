#!/usr/bin/env python3
"""
Country Risk Example - Geographic risk visualization
"""
import pandas as pd
import matplotlib.pyplot as plt
import riskplot

def create_sample_data():
    """Generate sample country risk data"""
    # Country risk scores (0-100, higher = riskier)
    data = pd.DataFrame({
        'Country': ['USA', 'Germany', 'China', 'Japan', 'UK', 'France',
                   'Brazil', 'India', 'Russia', 'South Africa'],
        'ISO_Code': ['USA', 'DEU', 'CHN', 'JPN', 'GBR', 'FRA',
                    'BRA', 'IND', 'RUS', 'ZAF'],
        'Risk_Score': [25, 18, 45, 22, 28, 20, 52, 48, 68, 44],
        'GDP_Growth': [2.1, 1.8, 6.2, 0.9, 1.5, 1.7, 2.8, 6.8, -0.2, 1.2],
        'Debt_to_GDP': [108, 69, 67, 256, 102, 115, 89, 74, 18, 70]
    })
    return data

def main():
    # Create sample country risk data
    data = create_sample_data()

    # Try globe visualization first (requires plotly)
    try:
        fig = riskplot.country_risk_globe(
            data,
            country_col='ISO_Code',
            risk_col='Risk_Score',
            title='Global Country Risk Assessment'
        )

        # Save as HTML
        fig.write_html('country_risk_globe.html')
        fig.show()

    except ImportError:
        print("Plotly not installed for globe. Creating bar chart alternative...")

        # Create bar chart alternative
        fig, ax = plt.subplots(figsize=(12, 6))

        # Sort by risk score
        data_sorted = data.sort_values('Risk_Score')

        # Color bars by risk level
        colors = ['green' if score < 30 else 'yellow' if score < 50 else 'red'
                 for score in data_sorted['Risk_Score']]

        bars = ax.bar(data_sorted['Country'], data_sorted['Risk_Score'], color=colors, alpha=0.7)

        # Add value labels on bars
        for bar, score in zip(bars, data_sorted['Risk_Score']):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{score}', ha='center', va='bottom', fontweight='bold')

        ax.set_title('Country Risk Scores', fontsize=14, fontweight='bold')
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

        plt.savefig('country_risk_example.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    main()