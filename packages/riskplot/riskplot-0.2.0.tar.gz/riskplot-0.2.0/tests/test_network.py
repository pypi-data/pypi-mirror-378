"""Tests for network visualization module."""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from riskplot.network import NetworkRiskPlot, country_network, financial_network


class TestNetworkRiskPlot:
    """Test NetworkRiskPlot class."""

    @pytest.fixture
    def sample_network_data(self):
        """Sample network data for testing."""
        return pd.DataFrame({
            'source': ['A', 'B', 'C', 'A', 'B'],
            'target': ['B', 'C', 'D', 'C', 'D'],
            'weight': [0.8, 1.2, 0.5, 0.9, 0.7],
            'risk': ['low', 'high', 'medium', 'low', 'high'],
            'size': [1.0, 2.0, 1.5, 1.0, 2.5]
        })

    @pytest.fixture
    def country_data(self):
        """Country trade data."""
        return pd.DataFrame({
            'country': ['USA', 'CHN', 'GBR', 'USA', 'CHN'],
            'partner': ['CHN', 'GBR', 'USA', 'GBR', 'USA'],
            'strength': [100, 80, 60, 90, 85],
            'risk': ['low', 'medium', 'low', 'low', 'medium']
        })

    @pytest.fixture
    def financial_data(self):
        """Financial network data."""
        return pd.DataFrame({
            'bank': ['JPM', 'BAC', 'WFC', 'JPM'],
            'counterparty': ['BAC', 'WFC', 'C', 'C'],
            'exposure': [50.0, 30.0, 25.0, 40.0],
            'rating': ['AA', 'A', 'BBB', 'AA']
        })

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_init_success(self):
        """Test successful initialization."""
        plot = NetworkRiskPlot()
        assert plot.graph is None
        assert plot.config is not None

    def test_init_no_networkx(self):
        """Test initialization fails without NetworkX."""
        with patch('riskplot.network.HAS_NETWORKX', False):
            with pytest.raises(ImportError, match="NetworkX required"):
                NetworkRiskPlot()

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_basic_plot(self, sample_network_data):
        """Test basic network plotting."""
        plot = NetworkRiskPlot()
        fig, ax = plot.plot(sample_network_data)

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)
        assert plot.graph is not None
        assert plot.graph.number_of_nodes() == 4  # A, B, C, D
        assert plot.graph.number_of_edges() == 5

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_plot_with_risk_colors(self, sample_network_data):
        """Test plotting with risk-based coloring."""
        plot = NetworkRiskPlot()
        fig, ax = plot.plot(sample_network_data, risk='risk', title='Risk Network')

        assert isinstance(fig, plt.Figure)
        assert ax.get_title() == 'Risk Network'

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_plot_with_node_sizes(self, sample_network_data):
        """Test plotting with variable node sizes."""
        plot = NetworkRiskPlot()
        fig, ax = plot.plot(sample_network_data, node_size='size')

        assert isinstance(fig, plt.Figure)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_different_layouts(self, sample_network_data):
        """Test different layout algorithms."""
        plot = NetworkRiskPlot()

        # Spring layout
        fig1, ax1 = plot.plot(sample_network_data, layout='spring')
        assert isinstance(fig1, plt.Figure)

        # Circular layout
        fig2, ax2 = plot.plot(sample_network_data, layout='circular')
        assert isinstance(fig2, plt.Figure)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_missing_columns(self):
        """Test error handling for missing columns."""
        plot = NetworkRiskPlot()
        bad_data = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})

        with pytest.raises(ValueError, match="Missing columns"):
            plot.plot(bad_data)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_get_metrics(self, sample_network_data):
        """Test network metrics calculation."""
        plot = NetworkRiskPlot()
        plot.plot(sample_network_data)

        metrics = plot.get_metrics()
        assert 'nodes' in metrics
        assert 'edges' in metrics
        assert 'density' in metrics
        assert 'clustering' in metrics
        assert metrics['nodes'] == 4
        assert metrics['edges'] == 5

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_get_metrics_no_graph(self):
        """Test metrics calculation without graph."""
        plot = NetworkRiskPlot()

        with pytest.raises(ValueError, match="No graph"):
            plot.get_metrics()

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_get_central_nodes(self, sample_network_data):
        """Test centrality calculation."""
        plot = NetworkRiskPlot()
        plot.plot(sample_network_data)

        # Test different centrality measures
        between = plot.get_central_nodes('betweenness')
        close = plot.get_central_nodes('closeness')
        degree = plot.get_central_nodes('degree')

        assert isinstance(between, dict)
        assert isinstance(close, dict)
        assert isinstance(degree, dict)
        assert len(between) == 4  # 4 nodes

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_invalid_centrality(self, sample_network_data):
        """Test invalid centrality method."""
        plot = NetworkRiskPlot()
        plot.plot(sample_network_data)

        with pytest.raises(ValueError, match="Unknown method"):
            plot.get_central_nodes('invalid')


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def country_data(self):
        """Country trade data."""
        return pd.DataFrame({
            'country': ['USA', 'CHN', 'GBR'],
            'partner': ['CHN', 'GBR', 'USA'],
            'strength': [100, 80, 60],
            'risk': ['low', 'medium', 'low']
        })

    @pytest.fixture
    def financial_data(self):
        """Financial network data."""
        return pd.DataFrame({
            'bank': ['JPM', 'BAC', 'WFC'],
            'counterparty': ['BAC', 'WFC', 'JPM'],
            'exposure': [50.0, 30.0, 25.0],
            'rating': ['AA', 'A', 'BBB']
        })

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_country_network(self, country_data):
        """Test country network function."""
        fig, ax = country_network(country_data)

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_country_network_with_risk(self, country_data):
        """Test country network with risk coloring."""
        fig, ax = country_network(country_data, risk='risk')

        assert isinstance(fig, plt.Figure)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_financial_network(self, financial_data):
        """Test financial network function."""
        fig, ax = financial_network(financial_data)

        assert isinstance(fig, plt.Figure)
        assert isinstance(ax, plt.Axes)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_financial_network_with_rating(self, financial_data):
        """Test financial network with rating coloring."""
        fig, ax = financial_network(financial_data, rating='rating')

        assert isinstance(fig, plt.Figure)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_empty_data(self):
        """Test with empty dataframe."""
        plot = NetworkRiskPlot()
        empty_data = pd.DataFrame(columns=['source', 'target', 'weight'])

        fig, ax = plot.plot(empty_data)
        assert isinstance(fig, plt.Figure)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_single_edge(self):
        """Test with single edge."""
        plot = NetworkRiskPlot()
        single_data = pd.DataFrame({
            'source': ['A'],
            'target': ['B'],
            'weight': [1.0]
        })

        fig, ax = plot.plot(single_data)
        assert isinstance(fig, plt.Figure)
        assert plot.graph.number_of_nodes() == 2
        assert plot.graph.number_of_edges() == 1

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_self_loops(self):
        """Test with self-loops."""
        plot = NetworkRiskPlot()
        loop_data = pd.DataFrame({
            'source': ['A', 'A'],
            'target': ['A', 'B'],
            'weight': [1.0, 0.5]
        })

        fig, ax = plot.plot(loop_data)
        assert isinstance(fig, plt.Figure)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_duplicate_edges(self):
        """Test with duplicate edges."""
        plot = NetworkRiskPlot()
        dup_data = pd.DataFrame({
            'source': ['A', 'A', 'B'],
            'target': ['B', 'B', 'C'],
            'weight': [1.0, 2.0, 1.5]
        })

        fig, ax = plot.plot(dup_data)
        assert isinstance(fig, plt.Figure)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_numeric_risk_values(self):
        """Test with numeric risk values."""
        plot = NetworkRiskPlot()
        numeric_data = pd.DataFrame({
            'source': ['A', 'B', 'C'],
            'target': ['B', 'C', 'A'],
            'weight': [1.0, 2.0, 1.5],
            'risk': [0.1, 0.8, 0.5]
        })

        fig, ax = plot.plot(numeric_data, risk='risk')
        assert isinstance(fig, plt.Figure)

    @pytest.mark.skipif(not HAS_NETWORKX, reason="NetworkX not available")
    def test_missing_risk_values(self):
        """Test with missing risk values."""
        plot = NetworkRiskPlot()
        missing_data = pd.DataFrame({
            'source': ['A', 'B', 'C'],
            'target': ['B', 'C', 'A'],
            'weight': [1.0, 2.0, 1.5],
            'risk': ['low', np.nan, 'high']
        })

        fig, ax = plot.plot(missing_data, risk='risk')
        assert isinstance(fig, plt.Figure)


if __name__ == '__main__':
    pytest.main([__file__])