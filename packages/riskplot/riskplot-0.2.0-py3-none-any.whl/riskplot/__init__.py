"""
RiskPlot: A comprehensive visualization package for risk analysis

Provides a wide range of risk visualization tools including ridge plots,
heatmaps, waterfall charts, distribution plots, and time series analysis.
"""

# Core visualization functions
from .ridge import ridge_plot
from .heatmap import (
    RiskHeatmap, correlation_heatmap, risk_matrix, exposure_heatmap
)
from .waterfall import (
    WaterfallChart, risk_attribution_waterfall, pnl_waterfall,
    var_decomposition, stress_test_waterfall
)
from .distributions import (
    ViolinPlot, BoxPlot, DensityComparison, QQPlot,
    risk_distribution_summary
)
from .timeseries import (
    TimeSeriesRiskPlot, VaRTimeSeries, DrawdownChart,
    rolling_risk_metrics
)
# Optional visualization modules (require additional dependencies)
try:
    from .network import (
        NetworkRiskPlot, country_network, financial_network
    )
    from .network import HAS_NETWORKX
    _NETWORK_AVAILABLE = HAS_NETWORKX
except ImportError:
    _NETWORK_AVAILABLE = False

try:
    from .globe import (
        GlobeRiskPlot, country_risk_globe, trade_flow_globe
    )
    from .globe import HAS_PLOTLY
    _GLOBE_AVAILABLE = HAS_PLOTLY
except ImportError:
    _GLOBE_AVAILABLE = False

try:
    from .surface import (
        SurfaceRiskPlot, CorrelationSurface, risk_landscape,
        portfolio_optimization_surface
    )
    from .surface import HAS_PLOTLY
    _SURFACE_AVAILABLE = HAS_PLOTLY
except ImportError:
    _SURFACE_AVAILABLE = False

# Base classes and utilities
from .base import (
    RiskVisualization, PlotConfig, ColorScheme,
    DataProcessor, ValidationHelper
)

__version__ = "0.2.0"

# Build __all__ list dynamically based on available modules
__all__ = [
    # Ridge plots
    "ridge_plot",

    # Heatmaps
    "correlation_heatmap",
    "risk_matrix",
    "exposure_heatmap",

    # Waterfall charts
    "risk_attribution_waterfall",
    "pnl_waterfall",
    "var_decomposition",
    "stress_test_waterfall",

    # Distribution plots
    "risk_distribution_summary",

    # Time series
    "rolling_risk_metrics",

    # Classes for advanced usage
    "RiskHeatmap",
    "WaterfallChart",
    "ViolinPlot",
    "BoxPlot",
    "DensityComparison",
    "QQPlot",
    "TimeSeriesRiskPlot",
    "VaRTimeSeries",
    "DrawdownChart",

    # Base utilities
    "RiskVisualization",
    "PlotConfig",
    "ColorScheme",
    "DataProcessor",
    "ValidationHelper"
]

# Add optional modules to __all__ if available
if _NETWORK_AVAILABLE:
    __all__.extend([
        "country_network",
        "financial_network",
        "NetworkRiskPlot"
    ])

if _GLOBE_AVAILABLE:
    __all__.extend([
        "country_risk_globe",
        "trade_flow_globe",
        "GlobeRiskPlot"
    ])

if _SURFACE_AVAILABLE:
    __all__.extend([
        "risk_landscape",
        "portfolio_optimization_surface",
        "SurfaceRiskPlot",
        "CorrelationSurface"
    ])