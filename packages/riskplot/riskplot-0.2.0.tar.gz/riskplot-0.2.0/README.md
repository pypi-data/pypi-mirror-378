# RiskPlot

[![PyPI version](https://badge.fury.io/py/riskplot.svg)](https://badge.fury.io/py/riskplot)
[![Tests](https://github.com/yourusername/riskplot/workflows/Tests/badge.svg)](https://github.com/yourusername/riskplot/actions)
[![Documentation](https://github.com/yourusername/riskplot/workflows/Deploy%20Documentation/badge.svg)](https://yourusername.github.io/riskplot)
[![Coverage](https://codecov.io/gh/yourusername/riskplot/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/riskplot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python package for risk analysis visualization, featuring ridge plots, heatmaps, waterfall charts, network diagrams, globe visualizations, and surface plots.

## 🚀 Features

### Core Visualizations
- **Ridge Plots**: Distribution comparisons across categories
- **Heatmaps**: Correlation matrices and risk matrices
- **Waterfall Charts**: Risk attribution and P&L decomposition
- **Time Series**: VaR tracking and drawdown analysis

### Advanced Visualizations ✨
- **Network Plots**: Entity relationship networks (requires `networkx`)
- **Globe Visualizations**: Interactive geographic risk mapping (requires `plotly`)
- **Surface Plots**: 2D/3D risk landscapes (requires `plotly`, `scipy`)

## 🎯 Use Cases

- **Financial Risk Management**: Portfolio analysis, VaR calculations, stress testing
- **Country Risk Analysis**: Geographic risk assessment and monitoring
- **Network Analysis**: Financial interconnectedness, trade relationships
- **Regulatory Reporting**: Risk visualization for compliance and reporting

## 📦 Installation

### Basic Installation
```bash
pip install riskplot
```

### With Optional Dependencies
```bash
# For network visualizations
pip install riskplot[network]

# For globe visualizations
pip install riskplot[globe]

# For all features
pip install riskplot[all]
```

## ⚡ Quick Start

```python
import riskplot
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'category': ['Portfolio A', 'Portfolio B', 'Portfolio C'],
    'returns': [np.random.normal(0.05, 0.1, 100),
                np.random.normal(0.03, 0.08, 100),
                np.random.normal(0.07, 0.15, 100)]
})

# Ridge plot
fig, ax = riskplot.ridge_plot(data, 'category', 'returns')

# Correlation heatmap
correlation_matrix = pd.DataFrame(np.random.rand(5, 5))
fig, ax = riskplot.correlation_heatmap(correlation_matrix)

# Network visualization (requires networkx)
network_data = pd.DataFrame({
    'source': ['A', 'B', 'C'],
    'target': ['B', 'C', 'A'],
    'weight': [0.8, 1.2, 0.5]
})
fig, ax = riskplot.country_interaction_network(network_data)

# Interactive globe (requires plotly)
country_data = pd.DataFrame({
    'country': ['USA', 'CHN', 'GBR'],
    'risk_score': [0.3, 0.7, 0.4]
})
fig = riskplot.country_risk_globe(country_data)
fig.show()
```

## Chart Types

### Ridge Plots
```python
# Basic ridge plot
rp.ridge_plot(data, 'category', 'value')

# Dual group comparison
rp.ridge_plot(data, 'category', 'value', 'group')
```

### Heatmaps
```python
# Correlation matrix
rp.correlation_heatmap(data)

# Risk matrix
rp.risk_matrix(data, 'probability', 'impact', 'label')

# Exposure heatmap
rp.exposure_heatmap(data, 'entity', 'sector', 'exposure')
```

### Waterfall Charts
```python
# Risk attribution
rp.risk_attribution_waterfall(data, 'factor', 'contribution')

# P&L waterfall
rp.pnl_waterfall(data, 'component', 'amount')

# VaR decomposition
rp.var_decomposition(data, 'component', 'var_contribution')
```

### Distribution Plots
```python
# Violin plots
violin = rp.ViolinPlot()
fig, ax = violin.plot(data, 'category', 'value')

# Distribution summary
rp.risk_distribution_summary(data, 'returns')
```

### Time Series
```python
# Rolling risk metrics
rp.rolling_risk_metrics(data, 'date', 'returns')

# Drawdown analysis
drawdown = rp.DrawdownChart()
fig, axes = drawdown.plot(data, 'date', 'value', show_underwater=True)
```

## Advanced Usage

### Custom Configuration
```python
config = rp.PlotConfig(
    figsize=(12, 8),
    colormap='plasma',
    style='seaborn'
)

# Use with any visualization class
heatmap = rp.RiskHeatmap(config=config)
```

### Extending the Framework
```python
class CustomRiskPlot(rp.RiskVisualization):
    def plot(self, data, **kwargs):
        fig, ax = self._setup_figure(**kwargs)
        # Your custom plotting logic
        return fig, ax
```

## Examples

- `examples/basic_usage.py` - Basic functionality demonstration
- `examples/recreate_original.py` - Recreates original ridge plot example
- `examples/comprehensive_demo.py` - Complete feature showcase

## 📚 Documentation

- **[Getting Started Guide](https://yourusername.github.io/riskplot/guides/getting-started)**: Installation and basic usage
- **[API Reference](https://yourusername.github.io/riskplot/api/)**: Complete function documentation
- **[Examples Gallery](https://yourusername.github.io/riskplot/examples/)**: Comprehensive examples
- **[Advanced Features](https://yourusername.github.io/riskplot/guides/advanced-features)**: Power user techniques

## 🧪 Dependencies

### Core Dependencies
- `matplotlib >= 3.5.0`
- `pandas >= 1.3.0`
- `numpy >= 1.20.0`
- `scipy >= 1.7.0`

### Optional Dependencies
- `networkx >= 2.6.0` (for network visualizations)
- `plotly >= 5.0.0` (for globe and interactive surface plots)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **[PyPI Package](https://pypi.org/project/riskplot/)**
- **[Documentation](https://yourusername.github.io/riskplot)**
- **[GitHub Repository](https://github.com/yourusername/riskplot)**
- **[Issue Tracker](https://github.com/yourusername/riskplot/issues)**

---

**Made with ❤️ for the risk management community**