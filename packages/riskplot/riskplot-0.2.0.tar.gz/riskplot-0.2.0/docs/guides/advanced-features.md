---
title: Advanced Features
layout: default
---

# Advanced Features

Unlock the full potential of RiskPlot with these advanced techniques and features.

## Custom Visualization Classes

### Creating Custom Visualizations

Extend RiskPlot by creating your own visualization classes:

```python
from riskplot.base import RiskVisualization, PlotConfig
import matplotlib.pyplot as plt
import pandas as pd

class CustomRiskPlot(RiskVisualization):
    """Custom risk visualization class."""

    def __init__(self, config=None):
        super().__init__(config)

    def plot(self, data, **kwargs):
        fig, ax = self._setup_figure(**kwargs)

        # Your custom plotting logic here
        ax.scatter(data['x'], data['y'], c=data['risk'])

        # Apply risk color scheme
        colors = self._apply_color_scheme(data['risk'].values)

        ax.set_title(kwargs.get('title', 'Custom Risk Plot'))
        return fig, ax

# Use your custom class
custom_plot = CustomRiskPlot()
fig, ax = custom_plot.plot(data)
```

### Inheriting from Existing Classes

```python
from riskplot.network import NetworkRiskPlot

class EnhancedNetworkPlot(NetworkRiskPlot):
    """Enhanced network plot with custom features."""

    def plot_with_communities(self, data, **kwargs):
        # First create the standard network plot
        fig, ax = self.plot(data, **kwargs)

        # Add community detection
        import networkx as nx
        communities = nx.community.greedy_modularity_communities(self.graph)

        # Color nodes by community
        node_colors = {}
        for i, community in enumerate(communities):
            for node in community:
                node_colors[node] = i

        # Update visualization with community colors
        # ... custom community visualization logic

        return fig, ax
```

## Interactive Plotly Integration

### Advanced Globe Visualizations

```python
from riskplot.globe import GlobeRiskPlot
import plotly.graph_objects as go

class InteractiveGlobe(GlobeRiskPlot):
    """Enhanced interactive globe with animations."""

    def plot_time_evolution(self, data, time_col='date', **kwargs):
        """Create animated globe showing risk evolution."""

        # Group data by time periods
        time_periods = sorted(data[time_col].unique())

        # Create frames for animation
        frames = []
        for period in time_periods:
            period_data = data[data[time_col] == period]

            frame = go.Frame(
                data=[go.Choropleth(
                    locations=period_data['country'],
                    z=period_data['risk_score'],
                    locationmode='ISO-3',
                    colorscale='RdYlGn_r'
                )],
                name=str(period)
            )
            frames.append(frame)

        # Create figure with animation
        fig = go.Figure(
            data=frames[0].data,
            frames=frames
        )

        # Add animation controls
        fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {'label': 'Play', 'method': 'animate', 'args': [None]},
                    {'label': 'Pause', 'method': 'animate', 'args': [None, {'mode': 'immediate'}]}
                ]
            }],
            sliders=[{
                'steps': [
                    {'label': str(period), 'method': 'animate', 'args': [[str(period)]]}
                    for period in time_periods
                ]
            }]
        )

        return fig
```

### Interactive Surface Analysis

Create dashboard with multiple interactive surfaces:

```python
from riskplot.surface import SurfaceRiskPlot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_multi_surface_dashboard(datasets, titles):
    """Create dashboard with multiple interactive surfaces."""

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=titles,
        specs=[[{'type': 'surface'}, {'type': 'surface'}],
               [{'type': 'surface'}, {'type': 'surface'}]]
    )

    positions = [(1,1), (1,2), (2,1), (2,2)]

    for i, (data, pos) in enumerate(zip(datasets, positions)):
        surface_plot = SurfaceRiskPlot()

        # Create surface data
        surface_fig = surface_plot.plot_interactive(
            data, 'x', 'y', 'z'
        )

        # Add to subplot
        fig.add_trace(
            surface_fig.data[0],
            row=pos[0], col=pos[1]
        )

    fig.update_layout(
        title="Risk Surface Dashboard",
        height=800
    )

    return fig
```

## Performance Optimization

### Large Dataset Handling

Optimize large datasets for visualization:

```python
import numpy as np
from riskplot.base import DataProcessor

def optimize_large_dataset(data, max_points=10000):
    """Optimize large datasets for visualization."""

    if len(data) > max_points:
        # Intelligent sampling
        if 'risk_level' in data.columns:
            # Stratified sampling by risk level
            sampled_data = data.groupby('risk_level').apply(
                lambda x: x.sample(min(len(x), max_points // data['risk_level'].nunique()))
            ).reset_index(drop=True)
        else:
            # Random sampling
            sampled_data = data.sample(n=max_points)

        print(f"Sampled {len(sampled_data)} points from {len(data)} total")
        return sampled_data

    return data

# Usage
optimized_data = optimize_large_dataset(large_dataset)
fig, ax = riskplot.ridge_plot(optimized_data)
```

### Caching and Memoization

```python
from functools import lru_cache
import hashlib
import pickle

class CachedVisualization:
    """Visualization class with result caching."""

    @staticmethod
    def _hash_dataframe(df):
        """Create hash of dataframe for caching."""
        return hashlib.md5(pickle.dumps(df.values)).hexdigest()

    @lru_cache(maxsize=32)
    def _cached_plot(self, data_hash, plot_type, **kwargs):
        """Cached plotting function."""
        # Reconstruct data and create plot
        # This is a simplified example
        pass

    def plot_with_cache(self, data, plot_type='ridge', **kwargs):
        """Plot with caching for repeated calls."""
        data_hash = self._hash_dataframe(data)
        return self._cached_plot(data_hash, plot_type, **kwargs)
```

## Statistical Analysis Integration

### Advanced Risk Metrics

```python
from riskplot.base import DataProcessor
import scipy.stats as stats

class AdvancedRiskAnalysis:
    """Advanced risk analysis with statistical testing."""

    @staticmethod
    def distribution_comparison(data, group_col, value_col):
        """Compare distributions with statistical tests."""
        groups = data.groupby(group_col)[value_col].apply(list)
        results = {}

        # Kolmogorov-Smirnov test for normality
        for group_name, values in groups.items():
            ks_stat, ks_p = stats.kstest(values, 'norm')
            results[f'{group_name}_normality'] = {
                'statistic': ks_stat,
                'p_value': ks_p,
                'is_normal': ks_p > 0.05
            }

        # Compare distributions between groups
        group_names = list(groups.keys())
        for i in range(len(group_names)):
            for j in range(i+1, len(group_names)):
                group1, group2 = group_names[i], group_names[j]

                # Mann-Whitney U test
                u_stat, u_p = stats.mannwhitneyu(
                    groups[group1], groups[group2]
                )

                results[f'{group1}_vs_{group2}'] = {
                    'test': 'mann_whitney',
                    'statistic': u_stat,
                    'p_value': u_p,
                    'significant': u_p < 0.05
                }

        return results

    @staticmethod
    def plot_with_statistics(data, **kwargs):
        """Create plot with statistical annotations."""
        # Run statistical analysis
        stats_results = AdvancedRiskAnalysis.distribution_comparison(
            data, 'category', 'values'
        )

        # Create visualization
        fig, ax = riskplot.ridge_plot(data, **kwargs)

        # Add statistical annotations
        y_pos = 0.95
        for test_name, result in stats_results.items():
            if 'vs' in test_name and result['significant']:
                ax.text(0.02, y_pos, f"{test_name}: p={result['p_value']:.3f}*",
                       transform=ax.transAxes, fontsize=8)
                y_pos -= 0.05

        return fig, ax
```

### Monte Carlo Simulations

```python
def monte_carlo_risk_simulation(params, n_simulations=10000):
    """Run Monte Carlo simulation for risk analysis."""

    np.random.seed(42)
    results = []

    for i in range(n_simulations):
        # Simulate risk factors
        market_shock = np.random.normal(params['market_mean'], params['market_std'])
        credit_spread = np.random.exponential(params['credit_lambda'])
        liquidity_factor = np.random.beta(params['liquidity_alpha'], params['liquidity_beta'])

        # Calculate portfolio impact
        portfolio_loss = (
            market_shock * params['market_exposure'] +
            credit_spread * params['credit_exposure'] +
            liquidity_factor * params['liquidity_exposure']
        )

        results.append({
            'simulation': i,
            'market_shock': market_shock,
            'credit_spread': credit_spread,
            'liquidity_factor': liquidity_factor,
            'portfolio_loss': portfolio_loss
        })

    return pd.DataFrame(results)

# Visualize simulation results
simulation_data = monte_carlo_risk_simulation({
    'market_mean': 0, 'market_std': 0.02, 'market_exposure': 1000000,
    'credit_lambda': 0.01, 'credit_exposure': 500000,
    'liquidity_alpha': 2, 'liquidity_beta': 5, 'liquidity_exposure': 200000
})

# Create surface plot of results
fig, ax = riskplot.risk_landscape(
    simulation_data,
    x_col='market_shock',
    y_col='credit_spread',
    risk_col='portfolio_loss',
    title='Portfolio Loss Surface - Monte Carlo Simulation'
)
```

## Custom Data Processing

### Risk Data Pipeline

```python
from riskplot.base import DataProcessor, ValidationHelper

class RiskDataPipeline:
    """Complete data processing pipeline for risk analysis."""

    def __init__(self):
        self.processors = []
        self.validators = []

    def add_processor(self, func):
        """Add data processing function."""
        self.processors.append(func)
        return self

    def add_validator(self, func):
        """Add data validation function."""
        self.validators.append(func)
        return self

    def process(self, data):
        """Execute complete pipeline."""
        current_data = data.copy()

        # Validation
        for validator in self.validators:
            validation_result = validator(current_data)
            if not validation_result['is_valid']:
                raise ValueError(f"Validation failed: {validation_result['issues']}")

        # Processing
        for processor in self.processors:
            current_data = processor(current_data)

        return current_data

# Define processing functions
def clean_outliers(data, columns=['return'], method='iqr'):
    """Remove outliers from specified columns."""
    cleaned_data = data.copy()

    for col in columns:
        if col in data.columns:
            outliers = DataProcessor.detect_outliers(data[col], method=method)
            cleaned_data = cleaned_data[~outliers]

    return cleaned_data

def normalize_risk_scores(data, risk_cols=['risk_score']):
    """Normalize risk scores to range."""
    normalized_data = data.copy()

    for col in risk_cols:
        if col in data.columns:
            min_val = data[col].min()
            max_val = data[col].max()
            normalized_data[col] = (data[col] - min_val) / (max_val - min_val)

    return normalized_data

# Create and use pipeline
pipeline = RiskDataPipeline()
pipeline.add_validator(ValidationHelper.validate_risk_data)
pipeline.add_processor(lambda x: clean_outliers(x, ['returns']))
pipeline.add_processor(lambda x: normalize_risk_scores(x, ['risk_score']))

processed_data = pipeline.process(raw_data)
```

## Export and Integration

### Multi-format Export

```python
def export_visualization(fig, basename, formats=['png', 'pdf', 'svg', 'html']):
    """Export visualization in multiple formats."""

    for fmt in formats:
        filename = f"{basename}.{fmt}"

        if fmt == 'html' and hasattr(fig, 'write_html'):
            # Plotly figure
            fig.write_html(filename)
        elif fmt in ['png', 'pdf', 'svg']:
            # Matplotlib figure
            fig.savefig(filename, format=fmt, dpi=300, bbox_inches='tight')

        print(f"Exported {filename}")

# Usage
fig, ax = riskplot.ridge_plot(data)
export_visualization(fig, 'risk_analysis')
```

### Report Generation

Generate comprehensive risk reports with saved images:

```python
def generate_risk_report(data, output_file='risk_report.html', image_dir='images'):
    """Generate comprehensive risk report with local images."""

    import os
    from jinja2 import Template

    # Create images directory
    os.makedirs(image_dir, exist_ok=True)

    # Create and save visualizations
    plot_files = {}

    # Ridge plot
    fig1, ax1 = riskplot.ridge_plot(data)
    ridge_file = f"{image_dir}/ridge_plot.png"
    fig1.savefig(ridge_file, dpi=300, bbox_inches='tight')
    plot_files['ridge'] = ridge_file

    # Risk matrix (if applicable columns exist)
    if 'probability' in data.columns and 'impact' in data.columns:
        fig2, ax2 = riskplot.risk_matrix(data, 'probability', 'impact')
        matrix_file = f"{image_dir}/risk_matrix.png"
        fig2.savefig(matrix_file, dpi=300, bbox_inches='tight')
        plot_files['matrix'] = matrix_file

    # Calculate summary statistics
    summary = {
        'total_risks': len(data),
        'high_risk_count': len(data[data['risk_score'] > 0.7]) if 'risk_score' in data.columns else 0,
        'avg_risk_score': data['risk_score'].mean() if 'risk_score' in data.columns else 0
    }

    # Generate HTML report
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Risk Analysis Report</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 40px;
                background-color: #f8f9fa;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 40px 20px;
                margin: 0;
            }
            .header h1 { margin: 0 0 10px 0; font-size: 2.5em; }
            .header p { margin: 0; opacity: 0.9; }
            .content { padding: 40px; }
            .summary {
                background: #e3f2fd;
                padding: 30px;
                border-radius: 8px;
                margin-bottom: 40px;
                border-left: 4px solid #2196f3;
            }
            .summary h2 { margin-top: 0; color: #1976d2; }
            .summary ul { list-style: none; padding: 0; }
            .summary li {
                padding: 8px 0;
                border-bottom: 1px solid #bbdefb;
                font-size: 1.1em;
            }
            .summary li:last-child { border-bottom: none; }
            .plot-section {
                margin: 40px 0;
                text-align: center;
                background: #f5f5f5;
                border-radius: 8px;
                padding: 30px;
            }
            .plot-section h3 {
                color: #333;
                margin-bottom: 20px;
                font-size: 1.5em;
            }
            .plot-section img {
                max-width: 100%;
                height: auto;
                border-radius: 4px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Risk Analysis Report</h1>
                <p>Generated on {{ date }}</p>
            </div>

            <div class="content">
                <div class="summary">
                    <h2>Summary Statistics</h2>
                    <ul>
                        <li><strong>Total Risks:</strong> {{ summary.total_risks }}</li>
                        <li><strong>High Risk Items:</strong> {{ summary.high_risk_count }}</li>
                        <li><strong>Average Risk Score:</strong> {{ "%.2f"|format(summary.avg_risk_score) }}</li>
                    </ul>
                </div>

                {% for plot_name, plot_file in plots.items() %}
                <div class="plot-section">
                    <h3>{{ plot_name.title() }} Analysis</h3>
                    <img src="{{ plot_file }}" alt="{{ plot_name }} visualization">
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    """

    template = Template(html_template)
    html_content = template.render(
        date=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M'),
        summary=summary,
        plots=plot_files
    )

    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"Report saved to {output_file}")
    print(f"Images saved to {image_dir}/")
```

## Best Practices

### Memory Management
```python
import matplotlib.pyplot as plt

# Clear figures to prevent memory leaks
fig, ax = riskplot.ridge_plot(data)
plt.show()
plt.close(fig)  # Important for large datasets
```

### Parallel Processing
```python
from multiprocessing import Pool

def parallel_risk_analysis(datasets):
    """Process multiple datasets in parallel."""

    def process_single_dataset(data):
        fig, ax = riskplot.ridge_plot(data)
        return fig

    with Pool() as pool:
        results = pool.map(process_single_dataset, datasets)

    return results
```

### Configuration Management
```python
import yaml
from riskplot.base import PlotConfig

def load_visualization_config(config_file):
    """Load visualization configuration from YAML."""

    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f)

    return PlotConfig(**config_dict['plot_settings'])

# Example config.yaml:
# plot_settings:
#   figsize: [12, 8]
#   colormap: 'RdYlGn_r'
#   dpi: 300
```

These advanced features enable sophisticated risk analysis workflows and custom visualizations tailored to your specific requirements.