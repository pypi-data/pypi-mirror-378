#!/usr/bin/env python3
"""
Convert Python examples to Markdown documentation.
"""

import os
import re
from pathlib import Path


def extract_docstring(file_content):
    """Extract module docstring from Python file."""
    # Look for triple-quoted strings at the beginning
    pattern = r'"""(.*?)"""'
    match = re.search(pattern, file_content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def extract_functions(file_content):
    """Extract function definitions and their docstrings."""
    functions = []

    # Pattern to match function definitions
    func_pattern = r'def\s+(\w+)\([^)]*\):[^"]*"""([^"]*?)"""'
    matches = re.finditer(func_pattern, file_content, re.DOTALL)

    for match in matches:
        func_name = match.group(1)
        docstring = match.group(2).strip()
        functions.append((func_name, docstring))

    return functions


def convert_python_to_markdown(python_file, output_dir):
    """Convert a Python example file to Markdown documentation."""
    with open(python_file, 'r') as f:
        content = f.read()

    # Extract filename without extension
    file_stem = python_file.stem

    # Create markdown file
    md_file = output_dir / f"{file_stem}.md"

    with open(md_file, 'w') as f:
        f.write("---\n")
        f.write(f"title: {file_stem.replace('_', ' ').title()}\n")
        f.write("layout: default\n")
        f.write("---\n\n")

        # Extract and write module docstring
        docstring = extract_docstring(content)
        if docstring:
            f.write(f"# {file_stem.replace('_', ' ').title()}\n\n")
            f.write(f"{docstring}\n\n")

        # Write download link
        f.write(f"## Download\n\n")
        f.write(f"📥 [Download {python_file.name}](https://github.com/yourusername/riskplot/blob/main/examples/{python_file.name})\n\n")

        # Extract functions for table of contents
        functions = extract_functions(content)
        if functions:
            f.write("## Functions\n\n")
            for func_name, func_doc in functions:
                f.write(f"- [{func_name}](#{func_name.lower()}): {func_doc.split('.')[0]}\n")
            f.write("\n")

        # Write full source code
        f.write("## Source Code\n\n")
        f.write("```python\n")
        f.write(content)
        f.write("\n```\n\n")

        # Write function details
        if functions:
            f.write("## Function Details\n\n")
            for func_name, func_doc in functions:
                f.write(f"### {func_name}\n\n")
                f.write(f"{func_doc}\n\n")

    print(f"Converted {python_file.name} to {md_file.name}")


def main():
    """Convert all Python examples to Markdown."""
    # Create examples directory in docs
    docs_dir = Path("docs")
    examples_dir = docs_dir / "examples"
    examples_dir.mkdir(exist_ok=True)

    # Create examples index
    with open(examples_dir / "index.md", 'w') as f:
        f.write("---\n")
        f.write("title: Examples Gallery\n")
        f.write("layout: default\n")
        f.write("---\n\n")
        f.write("# Examples Gallery\n\n")
        f.write("Comprehensive examples demonstrating RiskPlot capabilities.\n\n")
        f.write("## Available Examples\n\n")

    # Process all Python files in examples directory
    examples_source = Path("examples")
    if examples_source.exists():
        python_files = list(examples_source.glob("*.py"))

        # Update index with examples list
        with open(examples_dir / "index.md", 'a') as f:
            for py_file in python_files:
                title = py_file.stem.replace('_', ' ').title()
                f.write(f"- [{title}]({py_file.stem}): ")

                # Get first line of docstring as description
                with open(py_file, 'r') as py_f:
                    content = py_f.read()
                    docstring = extract_docstring(content)
                    if docstring:
                        first_line = docstring.split('\n')[0].strip()
                        f.write(f"{first_line}\n")
                    else:
                        f.write(f"Example using {py_file.stem}\n")

        # Convert each Python file
        for py_file in python_files:
            convert_python_to_markdown(py_file, examples_dir)

    print("Example conversion complete!")


if __name__ == "__main__":
    main()