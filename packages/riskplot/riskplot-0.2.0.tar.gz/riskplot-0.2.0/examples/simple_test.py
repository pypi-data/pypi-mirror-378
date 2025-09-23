#!/usr/bin/env python3
"""
Simple test to verify RiskPlot functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import riskplot

def test_basic_functionality():
    """Test basic RiskPlot functions"""
    print("Testing RiskPlot basic functionality...")

    # Test 1: Ridge plot
    print("1. Testing ridge plot...")
    np.random.seed(42)
    data = pd.DataFrame({
        'category': ['A', 'B', 'C'] * 100,
        'values': np.random.normal(0, 1, 300)
    })

    try:
        fig, ax = riskplot.ridge_plot(data, 'category', 'values')
        plt.close(fig)
        print("   ✓ Ridge plot works")
    except Exception as e:
        print(f"   ✗ Ridge plot failed: {e}")

    # Test 2: Correlation heatmap
    print("2. Testing correlation heatmap...")
    try:
        corr_data = pd.DataFrame(np.random.randn(50, 5), columns=list('ABCDE')).corr()
        fig, ax = riskplot.correlation_heatmap(corr_data)
        plt.close(fig)
        print("   ✓ Correlation heatmap works")
    except Exception as e:
        print(f"   ✗ Correlation heatmap failed: {e}")

    # Test 3: Waterfall chart
    print("3. Testing waterfall chart...")
    try:
        waterfall_data = pd.DataFrame({
            'factor': ['A', 'B', 'C'],
            'contribution': [0.05, -0.02, 0.03]
        })
        fig, ax = riskplot.pnl_waterfall(waterfall_data, 'factor', 'contribution')
        plt.close(fig)
        print("   ✓ Waterfall chart works")
    except Exception as e:
        print(f"   ✗ Waterfall chart failed: {e}")

    print("Basic functionality test complete!")

if __name__ == "__main__":
    test_basic_functionality()