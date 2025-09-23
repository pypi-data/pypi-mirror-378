#!/usr/bin/env python3
"""
Surface Plot Example - Risk landscape visualization
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import riskplot

def create_sample_data():
    """Generate sample surface data for risk landscape"""
    # Create grid for volatility and time horizon
    volatility = np.linspace(0.1, 0.5, 20)
    time_horizon = np.linspace(1, 365, 20)

    # Create meshgrid
    vol_grid, time_grid = np.meshgrid(volatility, time_horizon)

    # Calculate VaR surface (simplified model)
    var_surface = 2.33 * vol_grid * np.sqrt(time_grid / 365)  # 99% VaR

    # Flatten for DataFrame
    data = pd.DataFrame({
        'Volatility': vol_grid.flatten(),
        'Time_Horizon': time_grid.flatten(),
        'VaR': var_surface.flatten()
    })

    return data

def main():
    # Create sample surface data
    data = create_sample_data()

    # Create surface plot (requires plotly for 3D)
    try:
        fig = riskplot.risk_landscape(
            data,
            x_col='Time_Horizon',
            y_col='Volatility',
            risk_col='VaR',
            title='VaR Risk Landscape'
        )

        # Save as HTML
        fig.write_html('surface_plot_example.html')
        fig.show()

    except ImportError:
        print("Plotly not installed. Install with: pip install riskplot[globe]")

        # Create 2D contour plot as alternative
        fig, ax = plt.subplots(figsize=(10, 8))

        # Reshape data for contour plot
        vol_unique = sorted(data['Volatility'].unique())
        time_unique = sorted(data['Time_Horizon'].unique())

        var_matrix = data.pivot(index='Volatility', columns='Time_Horizon', values='VaR')

        # Create contour plot
        contour = ax.contourf(time_unique, vol_unique, var_matrix.values, levels=20, cmap='YlOrRd')
        plt.colorbar(contour, ax=ax, label='VaR')

        ax.set_xlabel('Time Horizon (days)')
        ax.set_ylabel('Volatility')
        ax.set_title('VaR Risk Landscape (2D Contour)')

        plt.tight_layout()
        plt.savefig('surface_plot_example.png', dpi=300, bbox_inches='tight')
        plt.show()

if __name__ == "__main__":
    main()