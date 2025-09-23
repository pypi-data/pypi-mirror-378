---
title: Getting Started with RiskPlot
layout: default
---

# Getting Started with RiskPlot

Welcome to RiskPlot! This guide will help you get up and running quickly with risk visualization.

## Installation

### Basic Installation

```bash
pip install riskplot
```

### Optional Dependencies

RiskPlot has modular dependencies. Install only what you need:

```bash
# For network visualizations
pip install riskplot[network]

# For globe visualizations
pip install riskplot[globe]

# For all features
pip install riskplot[all]
```

### Development Installation

```bash
git clone https://github.com/OwenDinsmore/riskplot.git
cd riskplot
pip install -e .[dev]
```

## Quick Start

### Your First Plot

```python
import riskplot
import pandas as pd
import numpy as np

# Create sample data
np.random.seed(42)
data = pd.DataFrame({
    'category': ['Portfolio A', 'Portfolio B', 'Portfolio C'],
    'returns': [np.random.normal(0.05, 0.1, 100),
                np.random.normal(0.03, 0.08, 100),
                np.random.normal(0.07, 0.15, 100)]
})

# Create a ridge plot
fig, ax = riskplot.ridge_plot(data, 'category', 'returns')
plt.show()
```

### Core Visualization Types

#### 1. Ridge Plots
Perfect for comparing distributions across categories:

```python
# Financial returns comparison
fig, ax = riskplot.ridge_plot(
    returns_data,
    category_col='asset_class',
    value_col='daily_returns',
    title='Return Distributions by Asset Class'
)
```

#### 2. Risk Heatmaps
Visualize correlation matrices and risk exposures:

```python
# Correlation heatmap
fig, ax = riskplot.correlation_heatmap(
    correlation_matrix,
    title='Asset Correlation Matrix'
)

# Risk matrix
fig, ax = riskplot.risk_matrix(
    risk_data,
    x_col='probability',
    y_col='impact',
    label_col='risk_name'
)
```

#### 3. Waterfall Charts
Show risk attribution and decomposition:

```python
# P&L waterfall
fig, ax = riskplot.pnl_waterfall(
    pnl_data,
    category_col='factor',
    value_col='contribution'
)
```

#### 4. Network Visualizations
Display entity relationships and interactions:

```python
# Country interaction network
fig, ax = riskplot.country_interaction_network(
    trade_data,
    country_col='source_country',
    partner_col='target_country',
    interaction_col='trade_volume'
)
```

#### 5. Globe Visualizations
Interactive geographic risk mapping:

```python
# Country risk globe
fig = riskplot.country_risk_globe(
    country_data,
    country_col='iso_code',
    risk_col='risk_score'
)
fig.show()
```

#### 6. Surface Plots
3D risk landscapes and optimization surfaces:

```python
# Risk landscape
fig, ax = riskplot.risk_landscape(
    surface_data,
    x_col='time_horizon',
    y_col='volatility',
    risk_col='var_estimate'
)
```

## Configuration

### Plot Configuration

Customize your visualizations with `PlotConfig`:

```python
from riskplot import PlotConfig

config = PlotConfig(
    figsize=(12, 8),
    colormap='RdYlGn_r',
    style='seaborn',
    dpi=300
)

# Use with any visualization
fig, ax = riskplot.ridge_plot(data, config=config)
```

### Color Schemes

Use risk-appropriate color palettes:

```python
from riskplot import ColorScheme

# Get risk color palette
colors = ColorScheme.get_risk_palette(4)

# Get rating colors
rating_colors = ColorScheme.get_rating_palette()
```

## Data Requirements

### Basic Data Format

Most RiskPlot functions expect pandas DataFrames with specific column structures:

```python
# Ridge plot data
ridge_data = pd.DataFrame({
    'category': ['A', 'B', 'C'],  # Categorical variable
    'values': [1.2, 2.3, 1.8]     # Numeric values
})

# Network data
network_data = pd.DataFrame({
    'source': ['A', 'B', 'C'],     # Source nodes
    'target': ['B', 'C', 'A'],     # Target nodes
    'weight': [0.8, 1.2, 0.5]      # Edge weights
})

# Surface data
surface_data = pd.DataFrame({
    'x': [1, 2, 3],               # X coordinates
    'y': [1, 2, 3],               # Y coordinates
    'z': [0.5, 0.8, 1.2]          # Z values (surface height)
})
```

### Missing Data Handling

RiskPlot automatically handles missing data:

```python
# Data with NaN values
data_with_missing = pd.DataFrame({
    'category': ['A', 'B', 'C'],
    'values': [1.2, np.nan, 1.8]
})

# Will automatically exclude NaN values
fig, ax = riskplot.ridge_plot(data_with_missing)
```

## Best Practices

### 1. Data Preparation

```python
# Clean and validate data
from riskplot import ValidationHelper

validation = ValidationHelper.validate_risk_data(your_data)
if validation['is_valid']:
    print("Data is ready for visualization")
else:
    print("Issues found:", validation['issues'])
```

### 2. Performance Optimization

```python
# For large datasets, consider sampling
large_data_sample = large_data.sample(n=1000)

# Use appropriate figure sizes
config = PlotConfig(figsize=(10, 6))  # Don't make too large
```

### 3. Color Usage

```python
# Use consistent color schemes
risk_colors = ColorScheme.get_risk_palette()

# For colorblind accessibility
config = PlotConfig(colormap='viridis')  # Colorblind-friendly
```

## Common Patterns

### Portfolio Risk Analysis

```python
# Complete portfolio analysis workflow
import riskplot

# 1. Return distributions
fig, ax = riskplot.ridge_plot(returns, 'asset', 'return')

# 2. Correlation analysis
fig, ax = riskplot.correlation_heatmap(returns.corr())

# 3. Risk attribution
fig, ax = riskplot.pnl_waterfall(attribution, 'factor', 'contribution')

# 4. Time series risk metrics
fig, ax = riskplot.rolling_risk_metrics(returns, window=30)
```

### Geographic Risk Assessment

```python
# Geographic risk workflow

# 1. Country risk globe
fig = riskplot.country_risk_globe(country_data, 'iso', 'risk_score')

# 2. Regional risk matrix
fig, ax = riskplot.risk_matrix(regional_data, 'probability', 'impact')

# 3. Trade network analysis
fig, ax = riskplot.country_interaction_network(trade_data)
```

## Next Steps

- [API Reference](../api/): Complete function documentation
- [Examples Gallery](../examples/): Comprehensive examples
- [Advanced Features](advanced-features): Power user techniques
- [Contributing](https://github.com/OwenDinsmore/riskplot/blob/main/CONTRIBUTING.md): Help improve RiskPlot

## Getting Help

- 📚 [Documentation](https://owendinsmore.github.io/riskplot)
- 🐛 [Issues](https://github.com/OwenDinsmore/riskplot/issues)
- 💬 [Discussions](https://github.com/OwenDinsmore/riskplot/discussions)