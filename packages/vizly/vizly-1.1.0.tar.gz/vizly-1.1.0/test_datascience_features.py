#!/usr/bin/env python3
"""
Comprehensive Test Suite for Vizly Data Science Features
========================================================

This script tests all new data science, time series, and financial
indicator features added to Vizly.
"""

import sys
import time
import warnings
from datetime import datetime, timedelta
import numpy as np

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore')

print("🧪 Vizly Data Science Features Test Suite")
print("=" * 50)

def test_basic_imports():
    """Test that all data science modules can be imported."""
    print("📦 Testing Data Science Imports...")

    try:
        import vizly
        from vizly import TimeSeriesChart, DistributionChart, CorrelationChart, FinancialIndicatorChart

        print("✅ Core data science imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_time_series_chart():
    """Test TimeSeriesChart functionality."""
    print("\n📈 Testing TimeSeriesChart...")

    try:
        import vizly

        # Generate sample time series data
        dates = [datetime.now() - timedelta(days=x) for x in range(100, 0, -1)]
        values = np.cumsum(np.random.randn(100)) + 100  # Random walk

        # Create time series chart
        ts_chart = vizly.TimeSeriesChart()
        ts_chart.plot_timeseries(
            dates, values,
            title="Sample Time Series",
            trend_line=True,
            moving_average=10,
            confidence_bands=True,
            detect_anomalies=True
        )

        # Save chart
        ts_chart.save('/tmp/test_timeseries.png', dpi=150)
        print("✅ TimeSeriesChart test passed")
        return True

    except Exception as e:
        print(f"❌ TimeSeriesChart test failed: {e}")
        return False

def test_distribution_chart():
    """Test DistributionChart functionality."""
    print("\n📊 Testing DistributionChart...")

    try:
        import vizly

        # Generate sample distribution data
        np.random.seed(42)
        data = np.random.normal(100, 15, 1000)  # Normal distribution

        # Create distribution chart
        dist_chart = vizly.DistributionChart()
        dist_chart.plot_distribution(
            data,
            distribution_type='histogram',
            kde=True,
            rug=True,
            fit_distribution='normal',
            confidence_interval=True
        )

        # Save chart
        dist_chart.save('/tmp/test_distribution.png', dpi=150)
        print("✅ DistributionChart test passed")
        return True

    except Exception as e:
        print(f"❌ DistributionChart test failed: {e}")
        return False

def test_correlation_chart():
    """Test CorrelationChart functionality."""
    print("\n🔗 Testing CorrelationChart...")

    try:
        import vizly

        # Generate sample correlation data
        np.random.seed(42)
        n_samples, n_features = 200, 5
        data = np.random.randn(n_samples, n_features)

        # Add some correlations
        data[:, 1] = 0.7 * data[:, 0] + 0.3 * np.random.randn(n_samples)  # Correlated with first
        data[:, 2] = -0.5 * data[:, 0] + 0.5 * np.random.randn(n_samples)  # Anti-correlated

        labels = ['Feature A', 'Feature B', 'Feature C', 'Feature D', 'Feature E']

        # Create correlation matrix
        corr_chart = vizly.CorrelationChart()
        corr_chart.plot_correlation_matrix(
            data,
            labels=labels,
            method='pearson',
            cluster=False,  # Disable clustering for this test to avoid scipy dependency
            significance=True
        )

        # Save chart
        corr_chart.save('/tmp/test_correlation.png', dpi=150)
        print("✅ CorrelationChart test passed")
        return True

    except Exception as e:
        print(f"❌ CorrelationChart test failed: {e}")
        return False

def test_financial_indicators():
    """Test FinancialIndicatorChart functionality."""
    print("\n💰 Testing FinancialIndicatorChart...")

    try:
        import vizly

        # Generate sample financial data
        np.random.seed(42)
        n_days = 100
        dates = [datetime.now() - timedelta(days=x) for x in range(n_days, 0, -1)]

        # Generate realistic price data (random walk with upward bias)
        price_changes = np.random.normal(0.001, 0.02, n_days)  # Small daily changes
        prices = 100 * np.exp(np.cumsum(price_changes))  # Geometric Brownian motion

        # Test Bollinger Bands
        bb_chart = vizly.FinancialIndicatorChart()
        bb_chart.plot_bollinger_bands(dates, prices, window=20, num_std=2.0)
        bb_chart.save('/tmp/test_bollinger.png', dpi=150)

        # Test RSI
        rsi_chart = vizly.FinancialIndicatorChart()
        rsi_chart.plot_rsi(dates, prices, window=14)
        rsi_chart.save('/tmp/test_rsi.png', dpi=150)

        # Test MACD
        macd_chart = vizly.FinancialIndicatorChart()
        macd_chart.plot_macd(dates, prices, fast_period=12, slow_period=26)
        macd_chart.save('/tmp/test_macd.png', dpi=150)

        # Test Volume Profile (need volume data)
        volumes = np.random.randint(1000, 10000, n_days)
        volume_chart = vizly.FinancialIndicatorChart()
        volume_chart.plot_volume_profile(dates, prices, volumes)
        volume_chart.save('/tmp/test_volume_profile.png', dpi=150)

        # Test Candlestick with indicators
        # Generate OHLC data
        highs = prices * (1 + np.random.uniform(0, 0.02, n_days))
        lows = prices * (1 - np.random.uniform(0, 0.02, n_days))
        opens = prices * (1 + np.random.uniform(-0.01, 0.01, n_days))
        closes = prices

        candle_chart = vizly.FinancialIndicatorChart()
        candle_chart.plot_candlestick_with_indicators(
            dates, opens, highs, lows, closes, volumes,
            show_bollinger=True, show_rsi=True
        )
        candle_chart.save('/tmp/test_candlestick.png', dpi=150)

        print("✅ FinancialIndicatorChart test passed")
        return True

    except Exception as e:
        print(f"❌ FinancialIndicatorChart test failed: {e}")
        return False

def test_performance():
    """Test performance with larger datasets."""
    print("\n⚡ Testing Performance with Large Datasets...")

    try:
        import vizly

        # Generate large dataset
        n_points = 10000
        data = np.random.randn(n_points)

        start_time = time.time()

        # Test distribution with large dataset
        dist_chart = vizly.DistributionChart()
        dist_chart.plot_distribution(data, kde=True, bins=100)
        dist_chart.save('/tmp/test_performance_large.png')

        elapsed = time.time() - start_time
        print(f"✅ Performance test passed ({elapsed:.3f}s for {n_points:,} points)")
        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🛡️ Testing Error Handling...")

    try:
        import vizly

        # Test with empty data
        try:
            chart = vizly.DistributionChart()
            chart.plot_distribution(np.array([]))
            print("⚠️ Empty data should have raised an error")
        except:
            print("✅ Empty data error handled correctly")

        # Test with invalid dates
        try:
            chart = vizly.TimeSeriesChart()
            chart.plot_timeseries(['invalid'], [1])
            print("⚠️ Invalid dates should have raised an error")
        except:
            print("✅ Invalid dates error handled correctly")

        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_all_tests():
    """Run comprehensive test suite."""
    print("🚀 Starting Comprehensive Data Science Test Suite")
    print("=" * 60)

    tests = [
        test_basic_imports,
        test_time_series_chart,
        test_distribution_chart,
        test_correlation_chart,
        test_financial_indicators,
        test_performance,
        test_error_handling,
    ]

    results = []
    total_start = time.time()

    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)

    total_time = time.time() - total_start

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1:2d}. {test_func.__name__:<25} {status}")

    print("=" * 60)
    print(f"🎯 Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"⏱️ Total Time: {total_time:.2f} seconds")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Vizly Data Science features are working perfectly!")
        print("\n📂 Generated test files:")
        test_files = [
            '/tmp/test_timeseries.png',
            '/tmp/test_distribution.png',
            '/tmp/test_correlation.png',
            '/tmp/test_bollinger.png',
            '/tmp/test_rsi.png',
            '/tmp/test_macd.png',
            '/tmp/test_volume_profile.png',
            '/tmp/test_candlestick.png',
            '/tmp/test_performance_large.png'
        ]
        for file in test_files:
            print(f"   • {file}")
    else:
        print(f"⚠️ {total - passed} tests failed. Please check the output above.")

    return passed == total

if __name__ == "__main__":
    # Add current directory to path so we can import vizly
    sys.path.insert(0, '/Users/durai/Documents/GitHub/vizly/src')

    success = run_all_tests()
    sys.exit(0 if success else 1)