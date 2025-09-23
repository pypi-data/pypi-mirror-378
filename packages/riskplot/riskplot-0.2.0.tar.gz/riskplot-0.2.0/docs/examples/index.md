---
title: Example Gallery
layout: default
---

# Example Gallery

Complete examples demonstrating RiskPlot's visualization capabilities. All code examples are available in the `/examples` directory of the repository.

## Core Visualizations

### Ridge Plots
Compare return distributions across multiple portfolios or asset classes.

```python
import riskplot
import pandas as pd
import numpy as np

# Create sample data
data = pd.DataFrame({
    'Portfolio': ['US Equity', 'EU Equity', 'EM Equity', 'Fixed Income'],
    'Return': [np.random.normal(0.06, 0.15, 1000) for _ in range(4)]
})

# Create ridge plot
fig, ax = riskplot.ridge_plot(
    data,
    category_col='Portfolio',
    value_col='Return',
    title='Portfolio Return Distributions'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/ridge_plot_example.py)

### Correlation Heatmaps
Visualize correlations between assets with clear color coding.

```python
# Create correlation heatmap
fig, ax = riskplot.correlation_heatmap(
    correlation_data,
    title='Asset Class Correlation Matrix'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/correlation_heatmap_example.py)

### Waterfall Charts
Show return attribution and factor decomposition.

```python
# Portfolio attribution analysis
fig, ax = riskplot.pnl_waterfall(
    attribution_data,
    category_col='Factor',
    value_col='Contribution',
    title='Portfolio Return Attribution'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/waterfall_chart_example.py)

## Risk Analysis

### Risk Matrix
Assess risks by probability and impact.

```python
# Risk assessment matrix
fig, ax = riskplot.risk_matrix(
    risk_data,
    x_col='Probability',
    y_col='Impact',
    label_col='Risk_Event',
    title='Risk Assessment Matrix'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/risk_matrix_example.py)

### VaR Time Series
Track Value at Risk over time.

```python
# VaR monitoring
fig, ax = riskplot.VaRTimeSeries(
    var_data,
    date_col='Date',
    return_col='Return',
    var_col='VaR_95',
    title='Portfolio VaR Monitoring'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/var_timeseries_example.py)

### Drawdown Analysis
Analyze portfolio drawdowns and recovery periods.

```python
# Drawdown analysis
fig, ax = riskplot.DrawdownChart(
    portfolio_data,
    date_col='Date',
    drawdown_col='Drawdown',
    title='Portfolio Drawdown Analysis'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/drawdown_chart_example.py)

## Advanced Visualizations

### Network Analysis
Visualize interconnections between financial institutions.

```python
# Financial network (requires networkx)
fig, ax = riskplot.financial_network(
    network_data,
    source_col='Source',
    target_col='Target',
    weight_col='Exposure',
    title='Financial Institution Network'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/network_analysis_example.py)

### Surface Plots
Create 3D risk landscapes and optimization surfaces.

```python
# Risk landscape (requires plotly)
fig = riskplot.risk_landscape(
    surface_data,
    x_col='Time_Horizon',
    y_col='Volatility',
    risk_col='VaR',
    title='VaR Risk Landscape'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/surface_plot_example.py)

### Geographic Risk
Visualize country-level risk assessments.

```python
# Country risk visualization
fig = riskplot.country_risk_globe(
    country_data,
    country_col='ISO_Code',
    risk_col='Risk_Score',
    title='Global Country Risk Assessment'
)
```

[View complete example →](https://github.com/OwenDinsmore/riskplot/blob/master/examples/country_risk_example.py)

## Usage Patterns

### Portfolio Risk Workflow
```python
# Complete portfolio analysis
import riskplot

# 1. Distribution analysis
riskplot.ridge_plot(returns, 'asset', 'return')

# 2. Correlation analysis
riskplot.correlation_heatmap(returns.corr())

# 3. Risk attribution
riskplot.pnl_waterfall(attribution, 'factor', 'contribution')

# 4. Risk monitoring
riskplot.rolling_risk_metrics(returns, window=30)
```

### Risk Management Dashboard
```python
# Multi-chart risk dashboard
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# VaR tracking
riskplot.VaRTimeSeries(data, ax=axes[0,0])

# Correlation monitoring
riskplot.correlation_heatmap(corr_data, ax=axes[0,1])

# Risk matrix
riskplot.risk_matrix(risk_events, ax=axes[1,0])

# Drawdown analysis
riskplot.DrawdownChart(portfolio, ax=axes[1,1])
```

## Running Examples

All examples are self-contained and can be run directly:

```bash
# Clone the repository
git clone https://github.com/OwenDinsmore/riskplot.git
cd riskplot

# Install with examples dependencies
pip install -e .[all]

# Run any example
python examples/ridge_plot_example.py
```

Each example includes:
- Sample data generation
- Complete visualization code
- Customization options
- Output saving functionality