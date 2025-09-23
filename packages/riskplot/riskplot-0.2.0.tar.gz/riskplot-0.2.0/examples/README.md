# RiskPlot Examples

This directory contains complete, runnable examples demonstrating all RiskPlot visualization capabilities.

## Quick Start

```bash
# Install RiskPlot with all dependencies
pip install riskplot[all]

# Run any example
python ridge_plot_example.py
python correlation_heatmap_example.py
python waterfall_chart_example.py
```

## Example Files

### Core Visualizations
- `ridge_plot_example.py` - Distribution comparison across categories
- `correlation_heatmap_example.py` - Asset correlation matrices
- `waterfall_chart_example.py` - Return attribution analysis

### Risk Analysis
- `risk_matrix_example.py` - Probability vs impact assessment
- `var_timeseries_example.py` - Value at Risk monitoring
- `drawdown_chart_example.py` - Portfolio drawdown analysis

### Advanced Features
- `network_analysis_example.py` - Financial network visualization
- `surface_plot_example.py` - 3D risk landscapes
- `country_risk_example.py` - Geographic risk assessment

### Utilities
- `generate_all_examples.py` - Generate all visualization images
- `basic_usage.py` - Original basic usage examples
- `comprehensive_demo.py` - Full feature demonstration

## Dependencies

### Core Features
- matplotlib
- pandas
- numpy
- scipy

### Optional Features
- networkx (for network visualizations)
- plotly (for 3D and interactive plots)

## Usage Notes

Each example:
1. Generates realistic sample data
2. Creates the visualization
3. Saves output as PNG/HTML
4. Shows the plot interactively

Examples are designed to be:
- **Self-contained** - Run independently
- **Educational** - Clear, commented code
- **Realistic** - Using financial data patterns
- **Customizable** - Easy to modify parameters

## Running Examples

Individual examples:
```bash
python ridge_plot_example.py
```

Generate all documentation images:
```bash
python generate_all_examples.py
```

## Customization

All examples accept modifications:

```python
# Modify data parameters
np.random.seed(123)  # Different random seed
portfolios = ['Your', 'Custom', 'Names']  # Custom labels

# Modify plot styling
fig, ax = riskplot.ridge_plot(
    data,
    title='Your Custom Title',
    figsize=(12, 8),
    colormap='viridis'
)
```

## Output

Examples save files as:
- `{example_name}_example.png` - Static images
- `{example_name}_example.html` - Interactive plots (Plotly)

## Support

- 📚 [Full Documentation](https://owendinsmore.github.io/riskplot)
- 🐛 [Issues](https://github.com/OwenDinsmore/riskplot/issues)
- 💬 [Discussions](https://github.com/OwenDinsmore/riskplot/discussions)