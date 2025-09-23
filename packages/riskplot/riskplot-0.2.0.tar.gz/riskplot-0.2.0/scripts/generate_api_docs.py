#!/usr/bin/env python3
"""
Generate API documentation for RiskPlot modules.
"""

import os
import sys
import inspect
import importlib
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import riskplot
from riskplot.base import RiskVisualization


def get_class_methods(cls):
    """Get public methods of a class."""
    methods = []
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if not name.startswith('_'):
            methods.append((name, method))
    return methods


def get_function_signature(func):
    """Get function signature as string."""
    try:
        sig = inspect.signature(func)
        return str(sig)
    except:
        return "()"


def get_docstring(obj):
    """Get cleaned docstring."""
    doc = inspect.getdoc(obj)
    return doc if doc else "No documentation available."


def generate_module_doc(module_name, output_dir):
    """Generate documentation for a specific module."""
    try:
        module = importlib.import_module(f'riskplot.{module_name}')
    except ImportError:
        print(f"Could not import riskplot.{module_name}")
        return

    doc_path = output_dir / f"{module_name}.md"

    with open(doc_path, 'w') as f:
        f.write(f"---\n")
        f.write(f"title: {module_name.title()} Module\n")
        f.write(f"layout: default\n")
        f.write(f"---\n\n")

        f.write(f"# {module_name.title()} Module\n\n")

        # Module docstring
        module_doc = get_docstring(module)
        f.write(f"{module_doc}\n\n")

        # Get all classes and functions
        classes = []
        functions = []

        for name, obj in inspect.getmembers(module):
            if not name.startswith('_'):
                if inspect.isclass(obj) and obj.__module__ == module.__name__:
                    classes.append((name, obj))
                elif inspect.isfunction(obj) and obj.__module__ == module.__name__:
                    functions.append((name, obj))

        # Document classes
        if classes:
            f.write("## Classes\n\n")
            for class_name, cls in classes:
                f.write(f"### {class_name}\n\n")
                f.write(f"```python\n")
                f.write(f"class {class_name}\n")
                f.write(f"```\n\n")

                class_doc = get_docstring(cls)
                f.write(f"{class_doc}\n\n")

                # Document methods
                methods = get_class_methods(cls)
                if methods:
                    f.write(f"#### Methods\n\n")
                    for method_name, method in methods:
                        f.write(f"##### {method_name}\n\n")
                        f.write(f"```python\n")
                        f.write(f"{method_name}{get_function_signature(method)}\n")
                        f.write(f"```\n\n")

                        method_doc = get_docstring(method)
                        f.write(f"{method_doc}\n\n")

        # Document functions
        if functions:
            f.write("## Functions\n\n")
            for func_name, func in functions:
                f.write(f"### {func_name}\n\n")
                f.write(f"```python\n")
                f.write(f"{func_name}{get_function_signature(func)}\n")
                f.write(f"```\n\n")

                func_doc = get_docstring(func)
                f.write(f"{func_doc}\n\n")

    print(f"Generated documentation for {module_name}")


def main():
    """Generate API documentation for all modules."""
    # Create output directory
    docs_dir = Path("docs")
    api_dir = docs_dir / "api"
    api_dir.mkdir(exist_ok=True)

    # Generate main API index
    with open(api_dir / "index.md", 'w') as f:
        f.write("---\n")
        f.write("title: API Reference\n")
        f.write("layout: default\n")
        f.write("---\n\n")
        f.write("# API Reference\n\n")
        f.write("Complete API documentation for RiskPlot.\n\n")
        f.write("## Modules\n\n")

        modules = ['base', 'ridge', 'heatmap', 'waterfall', 'distributions',
                  'timeseries', 'network', 'globe', 'surface']

        for module in modules:
            f.write(f"- [{module.title()}]({module}): {module.replace('_', ' ').title()} functionality\n")

        f.write("\n## Quick Reference\n\n")
        f.write("### Main Functions\n\n")

        # List main functions from __all__
        if hasattr(riskplot, '__all__'):
            for func_name in sorted(riskplot.__all__):
                if not func_name[0].isupper():  # Skip classes
                    f.write(f"- `{func_name}`\n")

        f.write("\n### Classes\n\n")

        # List main classes
        if hasattr(riskplot, '__all__'):
            for class_name in sorted(riskplot.__all__):
                if class_name[0].isupper():  # Classes start with uppercase
                    f.write(f"- `{class_name}`\n")

    # Generate documentation for each module
    modules = ['base', 'ridge', 'heatmap', 'waterfall', 'distributions',
              'timeseries', 'network', 'globe', 'surface']

    for module in modules:
        generate_module_doc(module, api_dir)

    print("API documentation generation complete!")


if __name__ == "__main__":
    main()