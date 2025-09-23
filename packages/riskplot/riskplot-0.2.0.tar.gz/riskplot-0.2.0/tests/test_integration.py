"""Integration tests for the complete RiskPlot package."""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch
import sys
from io import StringIO

# Core imports
import riskplot
from riskplot.base import PlotConfig, ColorScheme


class TestPackageStructure:
    """Test package structure and imports."""

    def test_main_imports(self):
        """Test that main functions are importable."""
        # Core functions should always be available
        assert hasattr(riskplot, 'ridge_plot')
        assert hasattr(riskplot, 'correlation_heatmap')
        assert hasattr(riskplot, 'pnl_waterfall')
        assert hasattr(riskplot, 'rolling_risk_metrics')

    def test_optional_imports(self):
        """Test optional module availability flags."""
        # These attributes should exist regardless of dependencies
        assert hasattr(riskplot, '_NETWORK_AVAILABLE')
        assert hasattr(riskplot, '_GLOBE_AVAILABLE')
        assert hasattr(riskplot, '_SURFACE_AVAILABLE')

        # Types should be boolean
        assert isinstance(riskplot._NETWORK_AVAILABLE, bool)
        assert isinstance(riskplot._GLOBE_AVAILABLE, bool)
        assert isinstance(riskplot._SURFACE_AVAILABLE, bool)

    def test_conditional_imports(self):
        """Test that functions are only available when dependencies exist."""
        if riskplot._NETWORK_AVAILABLE:
            assert hasattr(riskplot, 'country_network')
            assert hasattr(riskplot, 'NetworkRiskPlot')

        if riskplot._GLOBE_AVAILABLE:
            assert hasattr(riskplot, 'country_risk_globe')
            assert hasattr(riskplot, 'GlobeRiskPlot')

        if riskplot._SURFACE_AVAILABLE:
            assert hasattr(riskplot, 'risk_landscape')
            assert hasattr(riskplot, 'SurfaceRiskPlot')

    def test_version_attribute(self):
        """Test package version is available."""
        assert hasattr(riskplot, '__version__')
        assert isinstance(riskplot.__version__, str)

    def test_all_list(self):
        """Test __all__ list completeness."""
        assert hasattr(riskplot, '__all__')
        assert isinstance(riskplot.__all__, list)
        assert len(riskplot.__all__) > 10  # Should have many exports


class TestRealWorldScenarios:
    """Test with realistic financial data scenarios."""

    @pytest.fixture
    def portfolio_returns(self):
        """Realistic portfolio returns data."""
        np.random.seed(42)
        assets = ['US_Equity', 'EU_Equity', 'EM_Equity', 'US_Bonds', 'EU_Bonds',
                 'Commodities', 'Real_Estate', 'Cash']
        dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')

        # Generate correlated returns
        n_assets = len(assets)
        correlation = np.eye(n_assets) * 0.7 + 0.3  # Moderate correlation
        np.fill_diagonal(correlation, 1.0)

        # Asset-specific parameters
        mean_returns = [0.0008, 0.0006, 0.0005, 0.0002, 0.0001, 0.0003, 0.0004, 0.0001]
        volatilities = [0.02, 0.025, 0.035, 0.008, 0.01, 0.03, 0.015, 0.001]

        cov_matrix = np.outer(volatilities, volatilities) * correlation

        returns = np.random.multivariate_normal(mean_returns, cov_matrix, len(dates))

        data = []
        for i, date in enumerate(dates):
            for j, asset in enumerate(assets):
                data.append({
                    'date': date,
                    'asset': asset,
                    'return': returns[i, j],
                    'sector': 'Equity' if 'Equity' in asset else
                            'Fixed_Income' if 'Bonds' in asset else 'Alternative'
                })

        return pd.DataFrame(data)

    @pytest.fixture
    def country_risk_data(self):
        """Country risk assessment data."""
        countries = ['USA', 'GBR', 'DEU', 'FRA', 'JPN', 'CHN', 'IND', 'BRA', 'RUS', 'ZAF']
        sectors = ['Sovereign', 'Banking', 'Corporate', 'Real_Estate']

        data = []
        np.random.seed(42)
        for country in countries:
            base_risk = np.random.uniform(0.1, 0.8)
            for sector in sectors:
                risk_score = max(0, min(1, base_risk + np.random.normal(0, 0.1)))
                data.append({
                    'country': country,
                    'sector': sector,
                    'risk_score': risk_score,
                    'risk_level': 'low' if risk_score < 0.3 else
                                'medium' if risk_score < 0.7 else 'high'
                })

        return pd.DataFrame(data)

    @pytest.fixture
    def network_data(self):
        """Financial network data."""
        banks = ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TD', 'BMO']
        data = []
        np.random.seed(42)

        for i, bank1 in enumerate(banks):
            for j, bank2 in enumerate(banks):
                if i != j and np.random.random() > 0.7:  # 30% connectivity
                    exposure = np.random.lognormal(15, 1)  # Log-normal distribution
                    data.append({
                        'bank': bank1,
                        'counterparty': bank2,
                        'exposure': exposure,
                        'rating': np.random.choice(['AAA', 'AA', 'A', 'BBB'], p=[0.1, 0.3, 0.4, 0.2])
                    })

        return pd.DataFrame(data)

    def test_portfolio_analysis_workflow(self, portfolio_returns):
        """Test complete portfolio analysis workflow."""
        # 1. Distribution analysis by asset
        fig1, ax1 = riskplot.ridge_plot(portfolio_returns, 'asset', 'return')
        assert isinstance(fig1, plt.Figure)
        plt.close(fig1)

        # 2. Sector comparison
        fig2, ax2 = riskplot.ridge_plot(portfolio_returns, 'sector', 'return')
        assert isinstance(fig2, plt.Figure)
        plt.close(fig2)

        # 3. Correlation analysis
        returns_pivot = portfolio_returns.pivot_table(
            values='return', index='date', columns='asset', aggfunc='first'
        )
        corr_matrix = returns_pivot.corr()
        fig3, ax3 = riskplot.correlation_heatmap(corr_matrix)
        assert isinstance(fig3, plt.Figure)
        plt.close(fig3)

        # 4. Time series analysis for one asset
        us_equity = portfolio_returns[portfolio_returns['asset'] == 'US_Equity'].copy()
        us_equity = us_equity.sort_values('date')

        fig4, axes4 = riskplot.rolling_risk_metrics(us_equity, 'date', 'return')
        assert isinstance(fig4, plt.Figure)
        plt.close(fig4)

    def test_risk_attribution_analysis(self, portfolio_returns):
        """Test risk attribution analysis."""
        # Create factor attribution data
        factors = ['Market_Beta', 'Size', 'Value', 'Momentum', 'Quality', 'Alpha']
        contributions = [2.3, -0.5, 0.8, 1.2, -0.3, 0.1]

        attribution_data = pd.DataFrame({
            'factor': factors,
            'contribution': contributions
        })

        fig, ax = riskplot.pnl_waterfall(attribution_data, 'factor', 'contribution')
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    @pytest.mark.skipif(not riskplot._NETWORK_AVAILABLE, reason="NetworkX not available")
    def test_financial_network_analysis(self, network_data):
        """Test financial network analysis."""
        fig, ax = riskplot.financial_network(network_data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

        # Test with risk coloring
        fig2, ax2 = riskplot.financial_network(network_data, rating='rating')
        assert isinstance(fig2, plt.Figure)
        plt.close(fig2)

    @pytest.mark.skipif(not riskplot._GLOBE_AVAILABLE, reason="Plotly not available")
    def test_geographic_risk_analysis(self, country_risk_data):
        """Test geographic risk visualization."""
        # Aggregate by country
        country_agg = country_risk_data.groupby('country')['risk_score'].mean().reset_index()

        fig = riskplot.country_risk_globe(country_agg, 'country', 'risk_score')
        assert hasattr(fig, 'show')  # Plotly figure

    @pytest.mark.skipif(not riskplot._SURFACE_AVAILABLE, reason="Plotly/scipy not available")
    def test_risk_surface_analysis(self):
        """Test risk surface visualization."""
        # Create risk landscape data
        np.random.seed(42)
        n = 200
        time_horizon = np.random.uniform(0.25, 5.0, n)
        volatility = np.random.uniform(0.05, 0.5, n)
        var_estimate = (time_horizon * 0.05 +
                       volatility * 3.0 +
                       np.random.normal(0, 0.1, n))

        surface_data = pd.DataFrame({
            'time_horizon': time_horizon,
            'volatility': volatility,
            'var_estimate': var_estimate
        })

        fig, ax = riskplot.risk_landscape(surface_data, 'time_horizon',
                                        'volatility', 'var_estimate')
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestConfigurationManagement:
    """Test configuration and customization."""

    def test_global_config_usage(self):
        """Test using global configuration."""
        config = PlotConfig(figsize=(12, 8), colormap='plasma', dpi=150)

        # Note: Current convenience functions don't accept config
        # This test documents the current state
        data = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value': [1, 2, 3]
        })

        fig, ax = riskplot.ridge_plot(data, 'category', 'value')
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_color_scheme_consistency(self):
        """Test color scheme across different plots."""
        # Test that color schemes are consistent
        risk_colors = ColorScheme.get_risk_palette(4)
        rating_colors = ColorScheme.get_rating_palette()

        assert len(risk_colors) == 4
        assert isinstance(rating_colors, dict)
        assert 'aaa' in rating_colors


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_dependencies_error_messages(self):
        """Test that missing dependencies give helpful errors."""
        with patch('riskplot.network.HAS_NETWORKX', False):
            with pytest.raises(ImportError, match="NetworkX required"):
                from riskplot.network import NetworkRiskPlot
                NetworkRiskPlot()

        with patch('riskplot.globe.HAS_PLOTLY', False):
            with pytest.raises(ImportError, match="Plotly required"):
                from riskplot.globe import GlobeRiskPlot
                GlobeRiskPlot()

    def test_invalid_data_handling(self):
        """Test handling of various invalid data scenarios."""
        # Empty dataframe
        empty_df = pd.DataFrame()
        with pytest.raises((ValueError, KeyError, IndexError)):
            riskplot.ridge_plot(empty_df, 'x', 'y')

        # Wrong column names
        good_data = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        with pytest.raises((ValueError, KeyError)):
            riskplot.ridge_plot(good_data, 'wrong_col', 'b')

    def test_memory_cleanup(self):
        """Test that plots don't leak memory."""
        initial_figures = len(plt.get_fignums())

        data = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value': np.random.normal(0, 1, 3)
        })

        # Create and close multiple figures
        for i in range(10):
            fig, ax = riskplot.ridge_plot(data, 'category', 'value')
            plt.close(fig)

        # Should not accumulate figures
        final_figures = len(plt.get_fignums())
        assert final_figures <= initial_figures + 1  # Allow some tolerance


class TestBackwardCompatibility:
    """Test backward compatibility and API stability."""

    def test_function_signatures(self):
        """Test that core function signatures haven't broken."""
        data = pd.DataFrame({
            'category': ['A', 'B'],
            'value': [1, 2]
        })

        # Core functions should accept basic parameters
        fig1, ax1 = riskplot.ridge_plot(data, 'category', 'value')
        assert isinstance(fig1, plt.Figure)
        plt.close(fig1)

        # Matrix data
        matrix = pd.DataFrame([[1, 0.5], [0.5, 1]], columns=['A', 'B'], index=['A', 'B'])
        fig2, ax2 = riskplot.correlation_heatmap(matrix)
        assert isinstance(fig2, plt.Figure)
        plt.close(fig2)

    def test_return_types(self):
        """Test that return types are consistent."""
        data = pd.DataFrame({
            'category': ['A', 'B'],
            'value': [1, 2]
        })

        # Most functions should return (Figure, Axes)
        result = riskplot.ridge_plot(data, 'category', 'value')
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], plt.Figure)
        plt.close(result[0])


class TestDocumentationExamples:
    """Test examples from documentation work correctly."""

    def test_readme_examples(self):
        """Test examples from README work."""
        # Basic example from README
        data = pd.DataFrame({
            'category': ['Portfolio A', 'Portfolio B', 'Portfolio C'],
            'returns': [np.random.normal(0.05, 0.1, 100),
                       np.random.normal(0.03, 0.08, 100),
                       np.random.normal(0.07, 0.15, 100)]
        })

        # This should work without error
        fig, ax = riskplot.ridge_plot(data, 'category', 'returns')
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

        # Correlation example
        correlation_matrix = pd.DataFrame(np.random.rand(5, 5))
        fig, ax = riskplot.correlation_heatmap(correlation_matrix)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    @pytest.mark.skipif(not riskplot._NETWORK_AVAILABLE, reason="NetworkX not available")
    def test_network_example(self):
        """Test network example from docs."""
        network_data = pd.DataFrame({
            'source': ['A', 'B', 'C'],
            'target': ['B', 'C', 'A'],
            'weight': [0.8, 1.2, 0.5]
        })

        fig, ax = riskplot.country_network(network_data)
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestPerformance:
    """Test performance characteristics."""

    def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        np.random.seed(42)

        # Large dataset
        n = 10000
        large_data = pd.DataFrame({
            'category': np.random.choice(['A', 'B', 'C', 'D', 'E'], n),
            'value': np.random.normal(0, 1, n)
        })

        # Should complete in reasonable time
        import time
        start = time.time()
        fig, ax = riskplot.ridge_plot(large_data, 'category', 'value')
        end = time.time()

        assert isinstance(fig, plt.Figure)
        assert (end - start) < 10  # Should take less than 10 seconds
        plt.close(fig)

    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively."""
        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        data = pd.DataFrame({
            'category': ['A', 'B', 'C'],
            'value': np.random.normal(0, 1, 1000)
        })

        # Create many plots
        for i in range(50):
            fig, ax = riskplot.ridge_plot(data, 'category', 'value')
            plt.close(fig)

        gc.collect()
        final_memory = process.memory_info().rss
        memory_growth = (final_memory - initial_memory) / 1024 / 1024  # MB

        # Should not grow by more than 100MB
        assert memory_growth < 100


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])