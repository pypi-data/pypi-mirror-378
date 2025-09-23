"""
Demonstration of new visualization features in RiskPlot.

This script showcases the Network, Globe, and Surface visualization capabilities
added to the RiskPlot package.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from riskplot import (
    # Network visualizations
    NetworkRiskPlot, country_interaction_network, financial_network,
    # Globe visualizations
    GlobeRiskPlot, country_risk_globe, trade_flow_globe,
    # Surface visualizations
    SurfaceRiskPlot, CorrelationSurface, risk_landscape,
    portfolio_optimization_surface
)


def generate_sample_data():
    """Generate sample data for demonstrations."""
    np.random.seed(42)

    # Network data: country interactions
    countries = ['USA', 'CHN', 'GBR', 'DEU', 'FRA', 'JPN', 'ITA', 'CAN', 'AUS', 'BRA']
    network_data = []

    for i, source in enumerate(countries):
        for j, target in enumerate(countries):
            if i != j and np.random.random() > 0.7:  # 30% chance of connection
                network_data.append({
                    'source': source,
                    'target': target,
                    'weight': np.random.uniform(0.1, 1.0),
                    'risk_level': np.random.choice(['low', 'medium', 'high'])
                })

    network_df = pd.DataFrame(network_data)

    # Globe data: country risk scores
    country_codes = ['USA', 'CHN', 'GBR', 'DEU', 'FRA', 'JPN', 'ITA', 'CAN', 'AUS', 'BRA']
    globe_data = pd.DataFrame({
        'country': country_codes,
        'risk_score': np.random.uniform(0.2, 0.9, len(country_codes)),
        'economic_indicator': np.random.uniform(50, 150, len(country_codes))
    })

    # Surface data: risk landscape
    n_points = 100
    surface_data = pd.DataFrame({
        'time_horizon': np.random.uniform(0, 5, n_points),  # 0-5 years
        'volatility': np.random.uniform(0.1, 0.5, n_points),  # 10-50% volatility
        'risk_metric': np.random.uniform(0, 1, n_points)
    })

    # Add some structure to the surface data
    surface_data['risk_metric'] = (
        surface_data['time_horizon'] * 0.1 +
        surface_data['volatility'] * 2 +
        np.random.normal(0, 0.1, n_points)
    )

    # Portfolio returns for correlation surface
    assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')

    portfolio_returns = pd.DataFrame(
        np.random.multivariate_normal(
            mean=[0.001] * len(assets),
            cov=np.random.uniform(0.0001, 0.01, (len(assets), len(assets))),
            size=len(dates)
        ),
        index=dates,
        columns=assets
    )

    # Make correlation matrix symmetric and positive definite
    correlation_matrix = portfolio_returns.corr()

    return network_df, globe_data, surface_data, portfolio_returns, correlation_matrix


def demo_network_visualizations(network_df):
    """Demonstrate network visualization capabilities."""
    print("=== Network Visualizations Demo ===")

    # 1. Basic network plot
    print("1. Creating basic network visualization...")
    network_plot = NetworkRiskPlot()
    fig, ax = network_plot.plot(
        network_df,
        source_col='source',
        target_col='target',
        weight_col='weight',
        risk_col='risk_level',
        title='Country Risk Interaction Network'
    )
    plt.savefig('country_network.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 2. Country interaction network (convenience function)
    print("2. Creating country interaction network...")
    fig, ax = country_interaction_network(
        network_df,
        country_col='source',
        partner_col='target',
        interaction_col='weight',
        risk_col='risk_level',
        title='Global Trade Risk Network'
    )
    plt.savefig('country_interactions.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 3. Network metrics
    print("3. Calculating network metrics...")
    metrics = network_plot.get_network_metrics()
    print("Network Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.3f}")

    # 4. Central nodes analysis
    print("4. Identifying central nodes...")
    centrality = network_plot.identify_central_nodes('betweenness')
    print("Most central countries (betweenness centrality):")
    sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    for country, score in sorted_centrality[:5]:
        print(f"  {country}: {score:.3f}")


def demo_globe_visualizations(globe_data):
    """Demonstrate globe visualization capabilities."""
    print("\n=== Globe Visualizations Demo ===")

    # 1. Basic country risk globe
    print("1. Creating country risk globe...")
    globe_plot = GlobeRiskPlot()
    fig = globe_plot.plot(
        globe_data,
        country_col='country',
        value_col='risk_score',
        title='Global Country Risk Distribution'
    )
    fig.write_html('country_risk_globe.html')
    print("   Globe saved as 'country_risk_globe.html' - open in browser to view")

    # 2. Economic indicators globe
    print("2. Creating economic indicators globe...")
    fig = country_risk_globe(
        globe_data,
        country_col='country',
        risk_col='economic_indicator',
        title='Global Economic Indicators'
    )
    fig.write_html('economic_indicators_globe.html')
    print("   Globe saved as 'economic_indicators_globe.html'")

    # 3. Interactive globe with custom settings
    print("3. Creating customized interactive globe...")
    fig = globe_plot.plot(
        globe_data,
        country_col='country',
        value_col='risk_score',
        title='Custom Risk Globe',
        color_scale='Viridis',
        center_lon=0,
        center_lat=20
    )

    # Add some markers for high-risk countries
    high_risk_countries = globe_data[globe_data['risk_score'] > 0.7]
    if not high_risk_countries.empty:
        # Note: This would require lat/lon data for markers
        print(f"   High-risk countries identified: {list(high_risk_countries['country'])}")

    fig.write_html('custom_risk_globe.html')
    print("   Custom globe saved as 'custom_risk_globe.html'")


def demo_surface_visualizations(surface_data, portfolio_returns, correlation_matrix):
    """Demonstrate surface visualization capabilities."""
    print("\n=== Surface Visualizations Demo ===")

    # 1. Risk landscape contour plot
    print("1. Creating risk landscape...")
    fig, ax = risk_landscape(
        surface_data,
        x_col='time_horizon',
        y_col='volatility',
        risk_col='risk_metric',
        title='Risk Landscape: Time vs Volatility'
    )
    ax.set_xlabel('Time Horizon (years)')
    ax.set_ylabel('Volatility')
    plt.savefig('risk_landscape.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 2. 3D surface plot
    print("2. Creating 3D risk surface...")
    surface_plot = SurfaceRiskPlot()
    fig, ax = surface_plot.plot(
        surface_data,
        x_col='time_horizon',
        y_col='volatility',
        z_col='risk_metric',
        surface_type='surface',
        title='3D Risk Surface'
    )
    plt.savefig('risk_surface_3d.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 3. Interactive surface plot
    print("3. Creating interactive surface plot...")
    fig = surface_plot.plot_interactive(
        surface_data,
        x_col='time_horizon',
        y_col='volatility',
        z_col='risk_metric',
        title='Interactive Risk Surface',
        x_label='Time Horizon (years)',
        y_label='Volatility',
        z_label='Risk Metric'
    )
    fig.write_html('interactive_risk_surface.html')
    print("   Interactive surface saved as 'interactive_risk_surface.html'")

    # 4. Correlation surface
    print("4. Creating correlation surface...")
    corr_surface = CorrelationSurface()
    fig = corr_surface.plot_correlation_surface(
        correlation_matrix,
        title='Asset Correlation Surface'
    )
    fig.write_html('correlation_surface.html')
    print("   Correlation surface saved as 'correlation_surface.html'")

    # 5. Portfolio optimization surface
    print("5. Creating portfolio optimization surface...")
    fig = portfolio_optimization_surface(
        portfolio_returns,
        risk_range=(0.05, 0.25),
        return_range=(0.02, 0.15),
        title='Portfolio Risk-Return Surface'
    )
    fig.write_html('portfolio_optimization_surface.html')
    print("   Portfolio surface saved as 'portfolio_optimization_surface.html'")

    # 6. Surface metrics
    print("6. Calculating surface metrics...")
    metrics = surface_plot.calculate_surface_metrics()
    print("Surface Metrics:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value:.3f}")


def main():
    """Run all visualization demos."""
    print("RiskPlot New Visualizations Demo")
    print("=" * 40)

    # Generate sample data
    print("Generating sample data...")
    network_df, globe_data, surface_data, portfolio_returns, correlation_matrix = generate_sample_data()

    # Run demos
    try:
        demo_network_visualizations(network_df)
        demo_globe_visualizations(globe_data)
        demo_surface_visualizations(surface_data, portfolio_returns, correlation_matrix)

        print("\n" + "=" * 40)
        print("Demo completed successfully!")
        print("\nGenerated files:")
        print("  - country_network.png")
        print("  - country_interactions.png")
        print("  - country_risk_globe.html")
        print("  - economic_indicators_globe.html")
        print("  - custom_risk_globe.html")
        print("  - risk_landscape.png")
        print("  - risk_surface_3d.png")
        print("  - interactive_risk_surface.html")
        print("  - correlation_surface.html")
        print("  - portfolio_optimization_surface.html")
        print("\nOpen the .html files in a web browser for interactive visualizations!")

    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()