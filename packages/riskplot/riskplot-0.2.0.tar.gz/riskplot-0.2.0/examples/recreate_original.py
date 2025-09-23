"""
Recreate the original ridge plot example using riskplot.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import riskplot as rp


def create_original_style_data():
    """
    Create data in the format similar to the original example.
    This simulates the aggregated count data that was expanded.
    """
    np.random.seed(42)

    # Define rating scales like in original
    rating_order = ['c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa']

    # Sample companies
    companies = ['cb_agg', 'company_alpha', 'company_beta', 'company_gamma', 'company_delta']

    # Create expanded data (similar to what was done in original)
    rows = []

    for company in companies:
        # Generate different distributions for each company
        if company == 'cb_agg':
            # CB aggregate should have different distribution
            cb_weights = [0.05, 0.1, 0.15, 0.25, 0.25, 0.15, 0.05]
            sp_weights = [0.1, 0.15, 0.2, 0.25, 0.2, 0.08, 0.02]
        else:
            # Individual companies
            cb_weights = np.random.dirichlet(np.ones(7) * 2)
            sp_weights = np.random.dirichlet(np.ones(7) * 2)

        # Generate counts for each rating
        total_cb = np.random.randint(50, 200)
        total_sp = np.random.randint(40, 180)

        cb_counts = np.random.multinomial(total_cb, cb_weights)
        sp_counts = np.random.multinomial(total_sp, sp_weights)

        # Expand into individual rows (like original code did)
        for i, rating in enumerate(rating_order):
            # Add CB entries
            for _ in range(cb_counts[i]):
                rows.append({
                    'company': company,
                    'rating': rating,
                    'source': 'cb'
                })

            # Add SP entries
            for _ in range(sp_counts[i]):
                rows.append({
                    'company': company,
                    'rating': rating,
                    'source': 'sp'
                })

    return pd.DataFrame(rows)


def plot_original_style():
    """Create a plot in the original style."""
    print("Creating ridge plot in original style...")

    # Create the data
    df = create_original_style_data()

    # Create the ridge plot with similar styling to original
    fig, ax = rp.ridge_plot(
        data=df,
        category_col='company',
        value_col='rating',
        group_col='source',
        figsize=(12, 6),
        y_spacing=0.8,
        group_offset=0.15,
        colormap1='plasma',
        colormap2='viridis',
        bandwidth=0.39,
        sort_by_mean=True
    )

    # Customize to match original style
    ax.set_facecolor('darkgrey')
    ax.patch.set_alpha(0.05)
    ax.grid(axis='x', linestyle='-', alpha=0.7)
    ax.grid(axis='y', linestyle='-', alpha=0.3)

    # Set title like original
    plt.title('Comparison of CB and SP credit rating distributions (fine-grained)')

    plt.tight_layout()
    plt.show()

    return fig, ax


def analyze_data_structure(df):
    """Analyze the structure of our recreated data."""
    print("Data Analysis:")
    print(f"Total rows: {len(df)}")
    print(f"Companies: {df['company'].nunique()}")
    print(f"Sources: {df['source'].unique()}")
    print(f"Ratings: {sorted(df['rating'].unique())}")

    print("\nCompany-Source counts:")
    print(df.groupby(['company', 'source']).size().unstack(fill_value=0))

    print("\nRating distributions by source:")
    rating_dist = df.groupby(['source', 'rating']).size().unstack(fill_value=0)
    print(rating_dist)


if __name__ == "__main__":
    # Create and analyze the data
    df = create_original_style_data()
    analyze_data_structure(df)

    # Create the plot
    fig, ax = plot_original_style()

    print("Original style recreation completed!")