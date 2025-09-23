"""
Tests for ridge plot functionality.
"""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from riskplot.ridge import ridge_plot, _sort_rating_strings


class TestRidgePlot:
    """Test cases for ridge_plot function."""

    def setup_method(self):
        """Set up test data."""
        self.simple_data = pd.DataFrame({
            'category': ['A', 'A', 'B', 'B', 'C', 'C'],
            'value': ['high', 'medium', 'low', 'medium', 'high', 'low']
        })

        self.numeric_data = pd.DataFrame({
            'category': ['A', 'A', 'B', 'B', 'C', 'C'],
            'value': [1, 2, 3, 4, 5, 6]
        })

        self.grouped_data = pd.DataFrame({
            'category': ['A', 'A', 'A', 'A', 'B', 'B'],
            'value': ['high', 'low', 'high', 'low', 'medium', 'high'],
            'group': ['G1', 'G1', 'G2', 'G2', 'G1', 'G2']
        })

    def test_basic_ridge_plot(self):
        """Test basic ridge plot creation."""
        fig, ax = ridge_plot(self.simple_data, 'category', 'value')
        assert isinstance(fig, plt.Figure)
        assert len(ax.get_lines()) > 0  # Should have some plotted lines
        plt.close(fig)

    def test_numeric_data(self):
        """Test ridge plot with numeric data."""
        fig, ax = ridge_plot(self.numeric_data, 'category', 'value')
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_grouped_ridge_plot(self):
        """Test ridge plot with groups."""
        fig, ax = ridge_plot(self.grouped_data, 'category', 'value', 'group')
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_custom_parameters(self):
        """Test ridge plot with custom parameters."""
        fig, ax = ridge_plot(
            self.simple_data,
            'category',
            'value',
            figsize=(8, 4),
            y_spacing=1.0,
            colormap1='Blues',
            show_mean=False,
            show_count=False
        )
        assert isinstance(fig, plt.Figure)
        assert fig.get_figwidth() == 8
        assert fig.get_figheight() == 4
        plt.close(fig)

    def test_invalid_columns(self):
        """Test error handling for invalid column names."""
        with pytest.raises(ValueError, match="Category column 'invalid' not found"):
            ridge_plot(self.simple_data, 'invalid', 'value')

        with pytest.raises(ValueError, match="Value column 'invalid' not found"):
            ridge_plot(self.simple_data, 'category', 'invalid')

    def test_custom_category_order(self):
        """Test custom category ordering."""
        custom_order = ['C', 'A', 'B']
        fig, ax = ridge_plot(
            self.simple_data,
            'category',
            'value',
            category_order=custom_order,
            sort_by_mean=False
        )
        assert isinstance(fig, plt.Figure)
        plt.close(fig)

    def test_empty_data(self):
        """Test handling of empty data."""
        empty_df = pd.DataFrame(columns=['category', 'value'])
        fig, ax = ridge_plot(empty_df, 'category', 'value')
        assert isinstance(fig, plt.Figure)
        plt.close(fig)


class TestSortRatingStrings:
    """Test cases for _sort_rating_strings helper function."""

    def test_credit_ratings(self):
        """Test sorting of credit rating strings."""
        ratings = ['a', 'bbb', 'aa', 'b', 'aaa', 'bb', 'c']
        sorted_ratings = _sort_rating_strings(ratings)
        expected = ['c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa']
        assert sorted_ratings == expected

    def test_detailed_credit_ratings(self):
        """Test sorting of detailed credit ratings with +/-."""
        ratings = ['a+', 'bbb-', 'aa', 'b+', 'aaa-', 'bb+', 'c-']
        sorted_ratings = _sort_rating_strings(ratings)
        # Should handle the detailed ratings
        assert 'c-' in sorted_ratings
        assert 'aaa-' in sorted_ratings
        assert sorted_ratings.index('c-') < sorted_ratings.index('aaa-')

    def test_letter_grades(self):
        """Test sorting of letter grades."""
        grades = ['a', 'c+', 'b-', 'f', 'd']
        sorted_grades = _sort_rating_strings(grades)
        # Should recognize as grades pattern
        assert sorted_grades.index('f') < sorted_grades.index('a')

    def test_unknown_pattern(self):
        """Test fallback to alphabetical sorting."""
        random_strings = ['zebra', 'apple', 'banana']
        sorted_strings = _sort_rating_strings(random_strings)
        expected = ['apple', 'banana', 'zebra']
        assert sorted_strings == expected

    def test_risk_levels(self):
        """Test sorting of risk level strings."""
        risk_levels = ['high', 'low', 'medium']
        sorted_levels = _sort_rating_strings(risk_levels)
        assert sorted_levels.index('low') < sorted_levels.index('high')


if __name__ == "__main__":
    pytest.main([__file__])