"""
Basic usage examples for riskplot.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import riskplot as rp


def create_sample_rating_data():
    """Create sample credit rating data similar to the original example."""
    np.random.seed(42)

    companies = ['CompanyA', 'CompanyB', 'CompanyC', 'CompanyD', 'CompanyE']
    rating_order = ['c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa']

    data = []

    for company in companies:
        # Generate different rating distributions for CB and SP
        for source in ['cb', 'sp']:
            # Create more data for lower-rated companies
            if 'A' in company or 'B' in company:
                # Higher quality companies
                ratings = np.random.choice(rating_order[3:], size=50,
                                         p=[0.1, 0.2, 0.3, 0.4])
            else:
                # Lower quality companies
                ratings = np.random.choice(rating_order[:5], size=40,
                                         p=[0.1, 0.2, 0.3, 0.25, 0.15])

            for rating in ratings:
                data.append({
                    'company': company,
                    'rating': rating,
                    'source': source
                })

    return pd.DataFrame(data)


def example_single_group():
    """Example with single group ridge plot."""
    print("Creating single group ridge plot...")

    # Create simple data
    df = pd.DataFrame({
        'category': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C'],
        'value': ['high', 'medium', 'high', 'low', 'medium', 'low', 'high', 'medium']
    })

    fig, ax = rp.ridge_plot(df, 'category', 'value')
    plt.title('Single Group Ridge Plot Example')
    plt.show()


def example_dual_group():
    """Example with dual group ridge plot (similar to original CB vs SP)."""
    print("Creating dual group ridge plot...")

    # Use the sample rating data
    df = create_sample_rating_data()

    fig, ax = rp.ridge_plot(
        df,
        category_col='company',
        value_col='rating',
        group_col='source',
        figsize=(12, 8),
        colormap1='plasma',
        colormap2='viridis'
    )

    plt.title('Credit Rating Distributions: CB vs SP')
    plt.show()


def example_custom_order():
    """Example with custom category ordering."""
    print("Creating ridge plot with custom ordering...")

    df = create_sample_rating_data()

    # Custom order (reverse alphabetical)
    custom_order = ['c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa']

    fig, ax = rp.ridge_plot(
        df,
        category_col='company',
        value_col='rating',
        group_col='source',
        category_order=custom_order,
        sort_by_mean=False
    )

    plt.title('Custom Ordered Ridge Plot')
    plt.show()


def example_numeric_data():
    """Example with numeric data."""
    print("Creating ridge plot with numeric data...")

    np.random.seed(42)

    # Generate numeric data
    data = []
    categories = ['Group1', 'Group2', 'Group3']

    for cat in categories:
        if cat == 'Group1':
            values = np.random.normal(5, 1.5, 100)
        elif cat == 'Group2':
            values = np.random.normal(7, 2, 100)
        else:
            values = np.random.normal(3, 1, 100)

        for val in values:
            data.append({'category': cat, 'score': val})

    df = pd.DataFrame(data)

    fig, ax = rp.ridge_plot(df, 'category', 'score')
    plt.title('Numeric Data Ridge Plot')
    plt.show()


if __name__ == "__main__":
    # Run examples
    example_single_group()
    example_dual_group()
    example_custom_order()
    example_numeric_data()

    print("All examples completed!")