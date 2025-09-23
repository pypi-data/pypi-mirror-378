"""Surface plots for risk analysis."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata
from .base import RiskVisualization

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None


class SurfaceRiskPlot(RiskVisualization):
    """Surface plot for risk landscapes."""

    def __init__(self, config=None):
        super().__init__(config)
        self.surface_data = None

    def plot(self, data, x_col, y_col, z_col, surface_type='contour',
             grid_resolution=50, **kwargs):
        """Create surface plot."""
        # Validate columns
        missing = [c for c in [x_col, y_col, z_col] if c not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Extract coordinates
        x, y, z = data[x_col].values, data[y_col].values, data[z_col].values

        # Create grid
        xi = np.linspace(x.min(), x.max(), grid_resolution)
        yi = np.linspace(y.min(), y.max(), grid_resolution)
        xi_grid, yi_grid = np.meshgrid(xi, yi)
        zi_grid = griddata((x, y), z, (xi_grid, yi_grid), method='linear')

        self.surface_data = {'x_grid': xi_grid, 'y_grid': yi_grid, 'z_grid': zi_grid}

        # Plot
        if surface_type in ['surface', 'wireframe']:
            fig = plt.figure(figsize=self.config.figsize, dpi=self.config.dpi)
            ax = fig.add_subplot(111, projection='3d')

            if surface_type == 'surface':
                surf = ax.plot_surface(xi_grid, yi_grid, zi_grid,
                                     cmap=self.config.colormap, alpha=self.config.alpha)
                fig.colorbar(surf, ax=ax, shrink=0.5)
            else:
                ax.plot_wireframe(xi_grid, yi_grid, zi_grid, alpha=self.config.alpha)

            ax.set_xlabel(kwargs.get('x_label', x_col))
            ax.set_ylabel(kwargs.get('y_label', y_col))
            ax.set_zlabel(kwargs.get('z_label', z_col))
        else:
            fig, ax = self._setup_figure(**kwargs)

            if surface_type == 'contour':
                contour = ax.contour(xi_grid, yi_grid, zi_grid, levels=20,
                                   cmap=self.config.colormap)
                ax.clabel(contour, inline=True, fontsize=8)
            else:  # contourf
                contour = ax.contourf(xi_grid, yi_grid, zi_grid, levels=20,
                                    cmap=self.config.colormap)
                fig.colorbar(contour, ax=ax)

            ax.set_xlabel(kwargs.get('x_label', x_col))
            ax.set_ylabel(kwargs.get('y_label', y_col))

        ax.set_title(kwargs.get('title', 'Risk Surface'))
        return fig, ax

    def plot_interactive(self, data, x_col, y_col, z_col, **kwargs):
        """Interactive plotly surface."""
        if not HAS_PLOTLY:
            raise ImportError("Plotly required. Install with: pip install plotly")

        missing = [c for c in [x_col, y_col, z_col] if c not in data.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        x, y, z = data[x_col].values, data[y_col].values, data[z_col].values

        # Create grid
        xi = np.linspace(x.min(), x.max(), 50)
        yi = np.linspace(y.min(), y.max(), 50)
        xi_grid, yi_grid = np.meshgrid(xi, yi)
        zi_grid = griddata((x, y), z, (xi_grid, yi_grid), method='linear')

        fig = go.Figure(data=[go.Surface(x=xi_grid, y=yi_grid, z=zi_grid)])
        fig.update_layout(title=kwargs.get('title', 'Interactive Surface'))
        return fig

    def get_metrics(self):
        """Get surface metrics."""
        if self.surface_data is None:
            raise ValueError("No surface data. Call plot() first.")

        zi = self.surface_data['z_grid'][~np.isnan(self.surface_data['z_grid'])]
        return {
            'mean': np.mean(zi),
            'std': np.std(zi),
            'min': np.min(zi),
            'max': np.max(zi)
        }

    def calculate_surface_metrics(self):
        """Calculate surface metrics."""
        if self.surface_data is None:
            raise ValueError("No surface data available. Call plot() first.")

        zi_grid = self.surface_data['z_grid']
        zi_flat = zi_grid[~np.isnan(zi_grid)]

        return {
            'surface_mean': np.mean(zi_flat),
            'surface_std': np.std(zi_flat),
            'surface_min': np.min(zi_flat),
            'surface_max': np.max(zi_flat),
            'surface_range': np.max(zi_flat) - np.min(zi_flat)
        }


class CorrelationSurface(SurfaceRiskPlot):
    """Correlation surface visualization."""

    def plot_correlation_surface(self, corr_matrix, **kwargs):
        """Plot correlation matrix as surface."""
        if not HAS_PLOTLY:
            raise ImportError("Plotly required for correlation surface")

        x = np.arange(len(corr_matrix.columns))
        y = np.arange(len(corr_matrix.index))
        x_grid, y_grid = np.meshgrid(x, y)

        fig = go.Figure(data=[go.Surface(
            x=x_grid, y=y_grid, z=corr_matrix.values,
            colorscale='RdBu', zmid=0
        )])

        fig.update_layout(
            title=kwargs.get('title', 'Correlation Surface'),
            scene=dict(
                xaxis=dict(tickvals=x, ticktext=list(corr_matrix.columns)),
                yaxis=dict(tickvals=y, ticktext=list(corr_matrix.index)),
                zaxis_title='Correlation'
            )
        )
        return fig


def risk_landscape(data, x_col, y_col, risk_col, **kwargs):
    """Risk landscape plot."""
    plot = SurfaceRiskPlot()
    return plot.plot(data, x_col, y_col, risk_col, surface_type='contourf', **kwargs)


def portfolio_optimization_surface(returns, risk_range=(0.05, 0.25),
                                  return_range=(0.02, 0.15), **kwargs):
    """Portfolio optimization surface."""
    risks = np.linspace(risk_range[0], risk_range[1], 50)
    target_returns = np.linspace(return_range[0], return_range[1], 50)
    risk_grid, return_grid = np.meshgrid(risks, target_returns)

    # Simple Sharpe ratio calculation
    risk_free = kwargs.get('risk_free_rate', 0.02)
    sharpe_grid = (return_grid - risk_free) / risk_grid

    plot_data = pd.DataFrame({
        'risk': risk_grid.flatten(),
        'return': return_grid.flatten(),
        'sharpe': sharpe_grid.flatten()
    })

    plot = SurfaceRiskPlot()
    return plot.plot_interactive(
        plot_data, 'risk', 'return', 'sharpe',
        title='Portfolio Optimization Surface', **kwargs
    )