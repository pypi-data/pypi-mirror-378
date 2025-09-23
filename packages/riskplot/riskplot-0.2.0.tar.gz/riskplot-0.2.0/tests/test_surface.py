"""Tests for surface visualization module."""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from riskplot.surface import SurfaceRiskPlot, CorrelationSurface, risk_landscape


class TestSurfaceRiskPlot:
    """Test SurfaceRiskPlot class."""

    @pytest.fixture
    def surface_data(self):
        """Sample 3D surface data."""
        np.random.seed(42)
        n = 50
        x = np.random.uniform(0, 5, n)
        y = np.random.uniform(0, 3, n)
        z = x * 0.5 + y * 0.3 + np.random.normal(0, 0.1, n)

        return pd.DataFrame({'x': x, 'y': y, 'z': z})

    @pytest.fixture
    def grid_data(self):
        """Regular grid data."""
        x = np.linspace(0, 5, 20)
        y = np.linspace(0, 3, 15)
        X, Y = np.meshgrid(x, y)
        Z = X * 0.5 + Y * 0.3 + 0.1 * np.sin(X) * np.cos(Y)

        # Flatten for DataFrame
        data = []
        for i in range(len(x)):
            for j in range(len(y)):
                data.append({'x': X[j, i], 'y': Y[j, i], 'z': Z[j, i]})

        return pd.DataFrame(data)

    @pytest.fixture
    def risk_landscape_data(self):
        """Risk landscape data."""
        np.random.seed(42)
        n = 100
        time_horizon = np.random.uniform(0, 5, n)
        volatility = np.random.uniform(0.1, 0.5, n)
        risk_metric = (time_horizon * 0.1 +
                      volatility * 2 +
                      np.random.normal(0, 0.1, n))

        return pd.DataFrame({
            'time_horizon': time_horizon,
            'volatility': volatility,
            'risk_metric': risk_metric
        })

    def test_init(self):
        """Test SurfaceRiskPlot initialization."""
        plot = SurfaceRiskPlot()
        assert plot.surface_data is None
        assert plot.config is not None

    def test_contour_plot(self, surface_data):
        """Test contour surface plot."""
        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(surface_data, 'x', 'y', 'z', surface_type='contour')

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        assert plot.surface_data is not None

    def test_contourf_plot(self, surface_data):
        """Test filled contour plot."""
        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(surface_data, 'x', 'y', 'z', surface_type='contourf')

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)

    def test_3d_surface_plot(self, surface_data):
        """Test 3D surface plot."""
        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(surface_data, 'x', 'y', 'z', surface_type='surface')

        assert isinstance(fig, plt.Figure)
        # 3D axes have different type
        assert hasattr(ax, 'zaxis')

    def test_wireframe_plot(self, surface_data):
        """Test wireframe plot."""
        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(surface_data, 'x', 'y', 'z', surface_type='wireframe')

        assert isinstance(fig, plt.Figure)
        assert hasattr(ax, 'zaxis')

    def test_custom_interpolation(self, surface_data):
        """Test different interpolation methods."""
        plot = SurfaceRiskPlot()

        # Linear interpolation
        fig1, ax1 = plot.plot(surface_data, 'x', 'y', 'z',
                             interpolation_method='linear')
        assert isinstance(fig1, plt.Figure)

        # Nearest neighbor
        fig2, ax2 = plot.plot(surface_data, 'x', 'y', 'z',
                             interpolation_method='nearest')
        assert isinstance(fig2, plt.Figure)

    def test_custom_grid_resolution(self, surface_data):
        """Test custom grid resolution."""
        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(surface_data, 'x', 'y', 'z',
                           grid_resolution=30)

        assert isinstance(fig, plt.Figure)

    def test_missing_columns(self):
        """Test error with missing columns."""
        plot = SurfaceRiskPlot()
        bad_data = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})

        with pytest.raises(ValueError):
            plot.plot(bad_data, 'x', 'y', 'z')

    @pytest.mark.skipif(not HAS_PLOTLY, reason="Plotly not available")
    def test_interactive_plot(self, surface_data):
        """Test interactive plotly surface."""
        plot = SurfaceRiskPlot()
        fig = plot.plot_interactive(surface_data, 'x', 'y', 'z')

        assert isinstance(fig, go.Figure)

    def test_interactive_plot_no_plotly(self, surface_data):
        """Test interactive plot without plotly."""
        with patch('riskplot.surface.HAS_PLOTLY', False):
            plot = SurfaceRiskPlot()
            with pytest.raises(ImportError, match="Plotly required"):
                plot.plot_interactive(surface_data, 'x', 'y', 'z')

    def test_surface_metrics(self, surface_data):
        """Test surface metrics calculation."""
        plot = SurfaceRiskPlot()
        plot.plot(surface_data, 'x', 'y', 'z')

        metrics = plot.calculate_surface_metrics()
        assert 'surface_mean' in metrics
        assert 'surface_std' in metrics
        assert 'surface_min' in metrics
        assert 'surface_max' in metrics
        assert isinstance(metrics['surface_mean'], float)

    def test_metrics_no_surface(self):
        """Test metrics without surface data."""
        plot = SurfaceRiskPlot()

        with pytest.raises(ValueError, match="No surface data"):
            plot.calculate_surface_metrics()


class TestCorrelationSurface:
    """Test CorrelationSurface class."""

    @pytest.fixture
    def correlation_matrix(self):
        """Sample correlation matrix."""
        np.random.seed(42)
        assets = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        n = len(assets)

        # Generate positive definite correlation matrix
        A = np.random.randn(n, n)
        corr = np.dot(A, A.T)
        corr = corr / np.sqrt(np.diag(corr)[:, None])
        corr = corr / np.sqrt(np.diag(corr)[None, :])

        return pd.DataFrame(corr, index=assets, columns=assets)

    @pytest.mark.skipif(not HAS_PLOTLY, reason="Plotly not available")
    def test_correlation_surface(self, correlation_matrix):
        """Test correlation surface plot."""
        surface = CorrelationSurface()
        fig = surface.plot_correlation_surface(correlation_matrix)

        assert isinstance(fig, go.Figure)

    def test_correlation_surface_no_plotly(self, correlation_matrix):
        """Test correlation surface without plotly."""
        with patch('riskplot.surface.HAS_PLOTLY', False):
            with pytest.raises(ImportError):
                from riskplot.surface import CorrelationSurface
                surface = CorrelationSurface()


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def risk_data(self):
        """Risk landscape data."""
        np.random.seed(42)
        n = 100
        time = np.random.uniform(0, 5, n)
        vol = np.random.uniform(0.1, 0.5, n)
        risk = time * 0.1 + vol * 2 + np.random.normal(0, 0.1, n)

        return pd.DataFrame({
            'time': time,
            'volatility': vol,
            'risk': risk
        })

    def test_risk_landscape(self, risk_data):
        """Test risk landscape function."""
        fig, ax = risk_landscape(risk_data, 'time', 'volatility', 'risk')

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)

    def test_risk_landscape_custom_title(self, risk_data):
        """Test risk landscape with custom title."""
        fig, ax = risk_landscape(risk_data, 'time', 'volatility', 'risk',
                               title='Custom Risk Surface')

        assert 'Custom Risk Surface' in ax.get_title()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_minimal_data(self):
        """Test with minimal data points."""
        minimal_data = pd.DataFrame({
            'x': [0, 1, 0],
            'y': [0, 0, 1],
            'z': [1, 2, 3]
        })

        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(minimal_data, 'x', 'y', 'z')
        assert isinstance(fig, plt.Figure)

    def test_duplicate_points(self):
        """Test with duplicate x,y coordinates."""
        dup_data = pd.DataFrame({
            'x': [0, 0, 1, 1],
            'y': [0, 0, 1, 1],
            'z': [1, 2, 3, 4]
        })

        plot = SurfaceRiskPlot()
        # Should handle gracefully (might average or use first value)
        fig, ax = plot.plot(dup_data, 'x', 'y', 'z')
        assert isinstance(fig, plt.Figure)

    def test_collinear_points(self):
        """Test with collinear points."""
        collinear_data = pd.DataFrame({
            'x': [0, 1, 2, 3],
            'y': [0, 0, 0, 0],  # All on same line
            'z': [1, 2, 3, 4]
        })

        plot = SurfaceRiskPlot()
        # Should handle gracefully
        fig, ax = plot.plot(collinear_data, 'x', 'y', 'z')
        assert isinstance(fig, plt.Figure)

    def test_constant_z_values(self):
        """Test with constant z values."""
        constant_data = pd.DataFrame({
            'x': [0, 1, 2],
            'y': [0, 1, 2],
            'z': [5, 5, 5]  # All same value
        })

        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(constant_data, 'x', 'y', 'z')
        assert isinstance(fig, plt.Figure)

    def test_extreme_aspect_ratio(self):
        """Test with extreme aspect ratio data."""
        extreme_data = pd.DataFrame({
            'x': [0, 1000, 2000],
            'y': [0, 0.001, 0.002],
            'z': [1, 2, 3]
        })

        plot = SurfaceRiskPlot()
        fig, ax = plot.plot(extreme_data, 'x', 'y', 'z')
        assert isinstance(fig, plt.Figure)

    def test_nan_in_data(self):
        """Test with NaN values."""
        nan_data = pd.DataFrame({
            'x': [0, 1, 2, np.nan],
            'y': [0, 1, 2, 3],
            'z': [1, 2, np.nan, 4]
        })

        plot = SurfaceRiskPlot()
        # Should handle NaN values gracefully
        fig, ax = plot.plot(nan_data, 'x', 'y', 'z')
        assert isinstance(fig, plt.Figure)


class TestPerformance:
    """Test performance with various data sizes."""

    def test_large_dataset(self):
        """Test with large dataset."""
        np.random.seed(42)
        n = 1000
        large_data = pd.DataFrame({
            'x': np.random.uniform(0, 10, n),
            'y': np.random.uniform(0, 10, n),
            'z': np.random.uniform(0, 10, n)
        })

        plot = SurfaceRiskPlot()
        # Should complete in reasonable time
        fig, ax = plot.plot(large_data, 'x', 'y', 'z')
        assert isinstance(fig, plt.Figure)

    def test_high_resolution_grid(self):
        """Test with high resolution grid."""
        np.random.seed(42)
        small_data = pd.DataFrame({
            'x': [0, 1, 2],
            'y': [0, 1, 2],
            'z': [1, 2, 3]
        })

        plot = SurfaceRiskPlot()
        # High resolution should work but may be slow
        fig, ax = plot.plot(small_data, 'x', 'y', 'z', grid_resolution=100)
        assert isinstance(fig, plt.Figure)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])