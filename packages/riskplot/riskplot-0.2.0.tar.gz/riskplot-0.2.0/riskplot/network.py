"""Network plots for risk analysis."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .base import RiskVisualization, PlotConfig, ColorScheme

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    nx = None


class NetworkRiskPlot(RiskVisualization):
    """Network plot for relationships between entities."""

    def __init__(self, config=None):
        if not HAS_NETWORKX:
            raise ImportError("NetworkX required. Install with: pip install networkx")
        super().__init__(config)
        self.graph = None

    def plot(self, data, source='source', target='target', weight='weight',
             risk=None, layout='spring', node_size=None, **kwargs):
        """Create network plot."""
        required = [source, target, weight]
        missing = [col for col in required if col not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Build graph
        self.graph = nx.from_pandas_edgelist(
            data, source=source, target=target,
            edge_attr=weight, create_using=nx.Graph()
        )

        fig, ax = self._setup_figure(**kwargs)

        # Layout
        if layout == 'spring':
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)

        # Node properties
        nodes = list(self.graph.nodes())
        colors = self._get_colors(nodes, data, risk)
        sizes = self._get_sizes(nodes, data, node_size)
        edge_weights = [self.graph[u][v][weight] for u, v in self.graph.edges()]

        # Edge widths
        if edge_weights:
            min_w, max_w = min(edge_weights), max(edge_weights)
            if max_w > min_w:
                widths = [1 + 4 * (w - min_w) / (max_w - min_w) for w in edge_weights]
            else:
                widths = [2.0] * len(edge_weights)
        else:
            widths = [1.0]

        # Draw
        nx.draw_networkx_nodes(self.graph, pos, node_color=colors,
                              node_size=sizes, alpha=self.config.alpha, ax=ax)
        nx.draw_networkx_edges(self.graph, pos, width=widths,
                              alpha=0.6, edge_color='gray', ax=ax)
        nx.draw_networkx_labels(self.graph, pos, font_size=self.config.font_size,
                               font_color=self.config.text_color, ax=ax)

        ax.set_title(kwargs.get('title', 'Network Plot'), fontsize=self.config.title_size)
        ax.axis('off')

        if risk is not None:
            self._add_legend(ax, data, risk)

        plt.tight_layout()
        return fig, ax

    def _get_colors(self, nodes, data, risk_col):
        """Get node colors."""
        if risk_col is None:
            return [ColorScheme.RISK_COLORS['medium']] * len(nodes)

        # Map nodes to risk values
        risk_map = {}
        if risk_col in data.columns:
            for _, row in data.iterrows():
                src, tgt = row.get('source'), row.get('target')
                risk = row.get(risk_col)
                if src and src not in risk_map:
                    risk_map[src] = risk
                if tgt and tgt not in risk_map:
                    risk_map[tgt] = risk

        colors = []
        for node in nodes:
            risk = risk_map.get(node, 'medium')
            if isinstance(risk, str):
                colors.append(ColorScheme.RISK_COLORS.get(risk.lower(),
                                                        ColorScheme.RISK_COLORS['medium']))
            else:
                # Numeric risk - handle mixed types and NaN
                try:
                    values = [v for v in risk_map.values() if isinstance(v, (int, float)) and not np.isnan(v)]
                    if len(values) > 1:
                        norm = (risk - min(values)) / (max(values) - min(values))
                    else:
                        norm = 0.5
                    colors.append(plt.cm.RdYlGn_r(norm))
                except (TypeError, ValueError):
                    # Fall back to medium risk color
                    colors.append(ColorScheme.RISK_COLORS['medium'])
        return colors

    def _get_sizes(self, nodes, data, size_col):
        """Get node sizes."""
        if size_col is None:
            return [300] * len(nodes)

        size_map = {}
        if size_col in data.columns:
            for _, row in data.iterrows():
                src, tgt = row.get('source'), row.get('target')
                size = row.get(size_col, 1)
                if src and src not in size_map:
                    size_map[src] = size
                if tgt and tgt not in size_map:
                    size_map[tgt] = size

        return [100 + size_map.get(node, 1) * 200 for node in nodes]

    def _add_legend(self, ax, data, risk_col):
        """Add risk legend."""
        from matplotlib.patches import Patch

        risks = data[risk_col].unique()
        patches = []
        for risk in risks:
            if isinstance(risk, str):
                color = ColorScheme.RISK_COLORS.get(risk.lower(),
                                                  ColorScheme.RISK_COLORS['medium'])
                patches.append(Patch(facecolor=color, label=risk.title()))

        if patches:
            ax.legend(handles=patches, loc='upper right', bbox_to_anchor=(1.15, 1))

    def get_metrics(self):
        """Get basic network metrics."""
        if self.graph is None:
            raise ValueError("No graph. Call plot() first.")

        connected = nx.is_connected(self.graph)
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'clustering': nx.average_clustering(self.graph),
            'components': nx.number_connected_components(self.graph),
            'diameter': nx.diameter(self.graph) if connected else float('inf'),
            'avg_path': nx.average_shortest_path_length(self.graph) if connected else float('inf')
        }

    def get_central_nodes(self, method='betweenness'):
        """Get most central nodes."""
        if self.graph is None:
            raise ValueError("No graph. Call plot() first.")

        if method == 'betweenness':
            return nx.betweenness_centrality(self.graph)
        elif method == 'closeness':
            return nx.closeness_centrality(self.graph)
        elif method == 'degree':
            return nx.degree_centrality(self.graph)
        else:
            raise ValueError(f"Unknown method: {method}")


def country_network(data, country='country', partner='partner',
                   strength='strength', risk=None, **kwargs):
    """Country interaction network."""
    plot = NetworkRiskPlot()
    return plot.plot(data, source=country, target=partner,
                    weight=strength, risk=risk, **kwargs)


def financial_network(data, bank='bank', counterparty='counterparty',
                     exposure='exposure', rating=None, **kwargs):
    """Financial institution network."""
    plot = NetworkRiskPlot()
    return plot.plot(data, source=bank, target=counterparty,
                    weight=exposure, risk=rating, layout='circular', **kwargs)