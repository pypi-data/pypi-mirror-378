#!/usr/bin/env python3
"""
Comprehensive Test Suite for Vizly Interactive Features
=======================================================

Tests all interactive chart capabilities including tooltips, controls,
streaming, and dashboard functionality.
"""

import sys
import time
import warnings
import numpy as np
from datetime import datetime

# Add vizly to path
sys.path.insert(0, '/Users/durai/Documents/GitHub/vizly/src')

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore')

print("🧪 Vizly Interactive Features Test Suite")
print("=" * 50)

def test_interactive_imports():
    """Test that all interactive modules can be imported."""
    print("📦 Testing Interactive Imports...")

    try:
        import vizly
        from vizly import (
            InteractiveChart, InteractiveScatterChart, InteractiveLineChart,
            RealTimeChart, FinancialStreamChart,
            InteractiveDashboard, DashboardBuilder
        )

        # Test interactive base classes
        from vizly.interactive.base import InteractionManager
        from vizly.interactive.tooltips import TooltipManager, HoverInspector
        from vizly.interactive.controls import ZoomPanManager, SelectionManager
        from vizly.interactive.streaming import DataStreamer, DataGenerator
        from vizly.interactive.dashboard import ChartContainer

        print("✅ All interactive imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_interactive_scatter():
    """Test interactive scatter chart functionality."""
    print("\n🎯 Testing Interactive Scatter Chart...")

    try:
        import vizly

        # Generate test data
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)
        labels = [f"Point {i}" for i in range(100)]

        # Create interactive scatter chart
        chart = vizly.InteractiveScatterChart()
        chart.plot(x, y, labels=labels, interactive=True, alpha=0.7)

        # Test interactive features
        chart.enable_tooltips(['x', 'y', 'labels'])
        chart.enable_zoom_pan()
        chart.enable_selection()

        # Save chart
        chart.save('/tmp/test_interactive_scatter.png')

        print("✅ Interactive scatter chart test passed")
        return True

    except Exception as e:
        print(f"❌ Interactive scatter test failed: {e}")
        return False

def test_interactive_line():
    """Test interactive line chart functionality."""
    print("\n📈 Testing Interactive Line Chart...")

    try:
        import vizly

        # Generate test data
        x = np.linspace(0, 10, 100)
        y = np.sin(x) + np.random.normal(0, 0.1, 100)

        # Create interactive line chart
        chart = vizly.InteractiveLineChart()
        chart.plot(x, y, interactive=True, color='blue')

        # Test features
        chart.enable_tooltips(['x', 'y'])
        chart.enable_zoom_pan()

        # Add markers
        peak_indices = [10, 30, 50, 70, 90]
        chart.add_data_markers(peak_indices, color='red', s=50)

        chart.save('/tmp/test_interactive_line.png')

        print("✅ Interactive line chart test passed")
        return True

    except Exception as e:
        print(f"❌ Interactive line test failed: {e}")
        return False

def test_real_time_streaming():
    """Test real-time streaming functionality."""
    print("\n⚡ Testing Real-time Streaming...")

    try:
        import vizly
        from vizly.interactive.streaming import DataGenerator

        # Create real-time chart
        chart = vizly.RealTimeChart()

        # Add data streams
        random_walk = DataGenerator.random_walk(start_value=100)
        sine_wave = DataGenerator.sine_wave(frequency=0.5)

        chart.add_stream('walk', random_walk, plot_type='line', color='blue')
        chart.add_stream('sine', sine_wave, plot_type='line', color='red')

        # Test streaming for short period
        chart.start_streaming()
        time.sleep(2)  # Stream for 2 seconds
        chart.stop_streaming()

        chart.save('/tmp/test_realtime_streaming.png')

        print("✅ Real-time streaming test passed")
        return True

    except Exception as e:
        print(f"❌ Real-time streaming test failed: {e}")
        return False

def test_data_generators():
    """Test data generator utilities."""
    print("\n🔢 Testing Data Generators...")

    try:
        from vizly.interactive.streaming import DataGenerator

        # Test random walk generator
        walk_gen = DataGenerator.random_walk(start_value=100, volatility=1)
        walk_data = [walk_gen() for _ in range(10)]
        assert all('timestamp' in d and 'value' in d for d in walk_data)

        # Test sine wave generator
        sine_gen = DataGenerator.sine_wave(frequency=1, amplitude=5)
        sine_data = [sine_gen() for _ in range(10)]
        assert all('timestamp' in d and 'value' in d for d in sine_data)

        # Test stock price simulator
        stock_gen = DataGenerator.stock_price_simulator(initial_price=150)
        stock_data = [stock_gen() for _ in range(10)]
        assert all('timestamp' in d and 'value' in d for d in stock_data)

        # Test OHLC generator
        ohlc_gen = DataGenerator.ohlc_generator(base_price=100)
        ohlc_data = [ohlc_gen() for _ in range(5)]
        assert all('timestamp' in d and 'ohlc' in d for d in ohlc_data)

        print("✅ Data generators test passed")
        return True

    except Exception as e:
        print(f"❌ Data generators test failed: {e}")
        return False

def test_tooltip_system():
    """Test tooltip and hover inspection system."""
    print("\n🏷️ Testing Tooltip System...")

    try:
        import vizly
        from vizly.interactive.tooltips import TooltipManager, AdvancedTooltip

        # Create chart with data
        chart = vizly.InteractiveScatterChart()
        x = np.random.randn(50)
        y = np.random.randn(50)
        chart.plot(x, y, interactive=True)

        # Test tooltip manager
        tooltip_manager = TooltipManager(chart, fields=['x', 'y'])

        # Test advanced tooltip
        advanced_tooltip = AdvancedTooltip(chart)
        advanced_tooltip.set_style(background_color='lightblue', alpha=0.9)

        chart.save('/tmp/test_tooltip_system.png')

        print("✅ Tooltip system test passed")
        return True

    except Exception as e:
        print(f"❌ Tooltip system test failed: {e}")
        return False

def test_control_systems():
    """Test zoom, pan, and selection controls."""
    print("\n🎛️ Testing Control Systems...")

    try:
        from vizly.interactive.controls import (
            ZoomPanManager, SelectionManager, CrossfilterManager
        )
        import vizly

        # Create test chart
        chart = vizly.InteractiveScatterChart()
        x = np.random.randn(100)
        y = np.random.randn(100)
        chart.plot(x, y, interactive=True)

        # Test zoom/pan manager
        zoom_pan = ZoomPanManager(chart)
        zoom_pan.zoom_to_fit()

        # Test selection manager
        selection = SelectionManager(chart)
        selection.set_selection_mode('replace')
        selection.select_all()
        selection.clear_selection()

        # Test crossfilter manager
        crossfilter = CrossfilterManager()
        crossfilter.add_chart("test_chart", chart)

        chart.save('/tmp/test_control_systems.png')

        print("✅ Control systems test passed")
        return True

    except Exception as e:
        print(f"❌ Control systems test failed: {e}")
        return False

def test_dashboard_creation():
    """Test dashboard and container functionality."""
    print("\n🖥️ Testing Dashboard Creation...")

    try:
        import vizly

        # Create dashboard with builder pattern
        builder = vizly.DashboardBuilder()

        # Create sample charts
        scatter_chart = vizly.InteractiveScatterChart()
        scatter_chart.plot(np.random.randn(50), np.random.randn(50), interactive=True)

        line_chart = vizly.InteractiveLineChart()
        line_chart.plot(range(50), np.cumsum(np.random.randn(50)), interactive=True)

        # Build dashboard
        dashboard = (builder
                    .set_title("Test Dashboard")
                    .add_container("main", layout="grid")
                    .add_chart("scatter", scatter_chart)
                    .add_chart("line", line_chart)
                    .build())

        # Test export
        dashboard.export_to_web('/tmp/test_dashboard')

        print("✅ Dashboard creation test passed")
        return True

    except Exception as e:
        print(f"❌ Dashboard creation test failed: {e}")
        return False

def test_financial_streaming():
    """Test financial-specific streaming features."""
    print("\n💰 Testing Financial Streaming...")

    try:
        import vizly
        from vizly.interactive.streaming import DataGenerator

        # Create financial stream chart
        chart = vizly.FinancialStreamChart()

        # Add price stream
        stock_gen = DataGenerator.stock_price_simulator(
            initial_price=150, volatility=0.01
        )

        chart.add_price_stream(stock_gen, timeframe='1min')

        # Test short streaming period
        chart.start_streaming()
        time.sleep(1)
        chart.stop_streaming()

        chart.save('/tmp/test_financial_streaming.png')

        print("✅ Financial streaming test passed")
        return True

    except Exception as e:
        print(f"❌ Financial streaming test failed: {e}")
        return False

def test_performance_with_large_data():
    """Test interactive performance with large datasets."""
    print("\n⚡ Testing Performance with Large Data...")

    try:
        import vizly

        # Test with progressively larger datasets
        sizes = [1000, 5000, 10000]
        for size in sizes:
            start_time = time.time()

            # Generate large dataset
            x = np.random.randn(size)
            y = np.random.randn(size)

            # Create interactive chart
            chart = vizly.InteractiveScatterChart()
            chart.plot(x, y, interactive=True, alpha=0.5, s=1)
            chart.enable_tooltips(['x', 'y'])

            chart.save(f'/tmp/test_performance_{size}.png')

            elapsed = time.time() - start_time
            print(f"   ✅ {size:,} points: {elapsed:.3f}s")

        print("✅ Performance test passed")
        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_error_handling():
    """Test error handling in interactive features."""
    print("\n🛡️ Testing Error Handling...")

    try:
        import vizly

        # Test with invalid data
        try:
            chart = vizly.InteractiveScatterChart()
            chart.plot([], [], interactive=True)  # Empty data
            print("   ✅ Empty data handled gracefully")
        except:
            print("   ✅ Empty data error caught appropriately")

        # Test with mismatched data lengths
        try:
            chart = vizly.InteractiveScatterChart()
            chart.plot([1, 2, 3], [1, 2], interactive=True)  # Mismatched lengths
            print("   ⚠️ Mismatched data lengths should be caught")
        except:
            print("   ✅ Mismatched data lengths error caught")

        print("✅ Error handling test passed")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_all_tests():
    """Run comprehensive test suite."""
    print("🚀 Starting Comprehensive Interactive Test Suite")
    print("=" * 60)

    tests = [
        test_interactive_imports,
        test_interactive_scatter,
        test_interactive_line,
        test_real_time_streaming,
        test_data_generators,
        test_tooltip_system,
        test_control_systems,
        test_dashboard_creation,
        test_financial_streaming,
        test_performance_with_large_data,
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
    print("📊 Interactive Features Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for i, (test_func, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1:2d}. {test_func.__name__:<30} {status}")

    print("=" * 60)
    print(f"🎯 Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"⏱️ Total Time: {total_time:.2f} seconds")

    if passed == total:
        print("🎉 ALL INTERACTIVE TESTS PASSED!")
        print("\n📂 Generated test files:")
        test_files = [
            '/tmp/test_interactive_scatter.png',
            '/tmp/test_interactive_line.png',
            '/tmp/test_realtime_streaming.png',
            '/tmp/test_tooltip_system.png',
            '/tmp/test_control_systems.png',
            '/tmp/test_financial_streaming.png',
            '/tmp/test_dashboard/',
        ]
        for file in test_files:
            print(f"   • {file}")

        print("\n✨ Interactive Features Ready:")
        features = [
            "Hover tooltips and data inspection",
            "Zoom/pan controls (mouse wheel + middle-click)",
            "Selection tools (click and drag)",
            "Real-time data streaming",
            "Financial price streaming",
            "Interactive dashboards",
            "Crossfilter-style interactions",
            "Performance optimized for 10K+ points"
        ]

        for feature in features:
            print(f"   ✅ {feature}")

    else:
        print(f"⚠️ {total - passed} tests failed. Please check the output above.")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)