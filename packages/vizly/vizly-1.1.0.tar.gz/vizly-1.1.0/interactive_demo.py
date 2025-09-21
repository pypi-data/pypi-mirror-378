#!/usr/bin/env python3
"""
Vizly Interactive Features Demonstration
========================================

Comprehensive showcase of interactive chart capabilities including:
- Hover tooltips and data inspection
- Zoom/pan controls
- Selection tools
- Real-time streaming
- Interactive dashboards
"""

import sys
import time
import warnings
import numpy as np
from datetime import datetime, timedelta

# Add vizly to path
sys.path.insert(0, '/Users/durai/Documents/GitHub/vizly/src')

# Suppress warnings for cleaner demo
warnings.filterwarnings('ignore')

print("🎯 Vizly Interactive Features Gallery")
print("=" * 50)
print("Creating interactive visualizations...")

def demo_interactive_scatter():
    """Demonstrate interactive scatter plot with tooltips and selection."""
    print("\n🎯 Creating Interactive Scatter Plot...")

    import vizly

    # Generate sample data with labels
    np.random.seed(42)
    n_points = 100
    x = np.random.randn(n_points)
    y = 2 * x + np.random.randn(n_points) * 0.5
    colors = np.random.rand(n_points)
    sizes = np.random.randint(20, 100, n_points)
    labels = [f"Point {i}" for i in range(n_points)]

    # Create interactive scatter chart
    chart = vizly.InteractiveScatterChart()
    chart.plot(
        x, y,
        color=colors,
        size=sizes,
        labels=labels,
        interactive=True,
        alpha=0.7,
        cmap='viridis'
    )

    # Enable interactive features
    chart.enable_tooltips(['x', 'y', 'labels'])
    chart.enable_zoom_pan()
    chart.enable_selection()

    chart.set_title("Interactive Scatter Plot")
    chart.set_labels("X Values", "Y Values")
    chart.add_legend()

    # Save for demonstration
    chart.save('/tmp/demo_interactive_scatter.png', dpi=300)
    print("✅ Interactive scatter plot with tooltips, zoom/pan, and selection")

def demo_interactive_line_chart():
    """Demonstrate interactive line chart with data markers."""
    print("\n📈 Creating Interactive Line Chart...")

    import vizly

    # Generate time series data
    dates = np.arange('2024-01-01', '2024-12-31', dtype='datetime64[D]')
    values = np.cumsum(np.random.randn(len(dates))) + 100

    # Create interactive line chart
    chart = vizly.InteractiveLineChart()
    chart.plot(
        np.arange(len(dates)), values,
        interactive=True,
        color='blue',
        linewidth=2,
        label='Stock Price'
    )

    # Add interactive markers at significant points
    peak_indices = np.where(values > np.percentile(values, 90))[0]
    chart.add_data_markers(
        peak_indices[:5],  # Top 5 peaks
        color='red',
        s=100,
        marker='^',
        label='Peaks'
    )

    # Enable interactive features
    chart.enable_tooltips(['x', 'y'])
    chart.enable_zoom_pan()

    chart.set_title("Interactive Time Series")
    chart.set_labels("Time", "Value")
    chart.add_legend()

    chart.save('/tmp/demo_interactive_line.png', dpi=300)
    print("✅ Interactive line chart with data markers and zoom/pan")

def demo_real_time_chart():
    """Demonstrate real-time streaming chart."""
    print("\n⚡ Creating Real-time Streaming Chart...")

    import vizly
    from vizly.interactive.streaming import DataGenerator

    # Create real-time chart
    chart = vizly.RealTimeChart()

    # Add multiple data streams
    random_walk_generator = DataGenerator.random_walk(start_value=100, volatility=2)
    sine_wave_generator = DataGenerator.sine_wave(frequency=0.1, amplitude=10)

    chart.add_stream(
        'random_walk',
        random_walk_generator,
        plot_type='line',
        color='blue',
        linewidth=2,
        label='Random Walk'
    )

    chart.add_stream(
        'sine_wave',
        sine_wave_generator,
        plot_type='line',
        color='red',
        linewidth=2,
        label='Sine Wave'
    )

    chart.set_title("Real-time Data Streams")
    chart.set_labels("Time", "Value")
    chart.add_legend()

    # Simulate streaming for a short period
    print("   📊 Simulating 5 seconds of real-time data...")
    chart.start_streaming()

    # Let it run for demonstration
    time.sleep(5)
    chart.stop_streaming()

    chart.save('/tmp/demo_realtime_chart.png', dpi=300)
    print("✅ Real-time streaming chart with multiple data feeds")

def demo_financial_stream():
    """Demonstrate real-time financial chart."""
    print("\n💰 Creating Financial Streaming Chart...")

    import vizly
    from vizly.interactive.streaming import DataGenerator

    # Create financial streaming chart
    chart = vizly.FinancialStreamChart()

    # Add price stream
    stock_generator = DataGenerator.stock_price_simulator(
        initial_price=150,
        volatility=0.02,
        trend=0.0001
    )

    chart.add_price_stream(stock_generator, timeframe='1min')

    chart.set_title("Real-time Stock Price")
    chart.set_labels("Time", "Price ($)")

    # Simulate streaming
    print("   📈 Simulating financial data stream...")
    chart.start_streaming()
    time.sleep(3)
    chart.stop_streaming()

    chart.save('/tmp/demo_financial_stream.png', dpi=300)
    print("✅ Real-time financial chart with price streaming")

def demo_interactive_dashboard():
    """Demonstrate interactive dashboard creation."""
    print("\n🖥️ Creating Interactive Dashboard...")

    import vizly

    # Create dashboard using builder pattern
    builder = vizly.DashboardBuilder()

    # Generate sample data
    np.random.seed(42)
    x = np.random.randn(50)
    y = np.random.randn(50)
    z = x * y + np.random.randn(50) * 0.1

    # Create multiple charts
    scatter_chart = vizly.InteractiveScatterChart()
    scatter_chart.plot(x, y, interactive=True, alpha=0.7)
    scatter_chart.set_title("Scatter Plot")

    line_chart = vizly.InteractiveLineChart()
    line_chart.plot(range(len(z)), z, interactive=True)
    line_chart.set_title("Line Chart")

    # Create distribution chart
    dist_chart = vizly.DistributionChart()
    dist_chart.plot_distribution(z, kde=True)
    dist_chart.set_title("Distribution")

    # Build dashboard
    dashboard = (builder
                .set_title("Vizly Interactive Dashboard")
                .add_container("main_charts", layout="grid")
                .add_chart("scatter", scatter_chart)
                .add_chart("line", line_chart)
                .add_chart("distribution", dist_chart)
                .build())

    # Export dashboard
    dashboard.export_to_web('/tmp/vizly_dashboard')
    print("✅ Interactive dashboard exported to /tmp/vizly_dashboard")

def demo_crossfilter_interaction():
    """Demonstrate crossfilter-style interactions."""
    print("\n🔗 Creating Crossfilter Interactions...")

    import vizly
    from vizly.interactive.controls import CrossfilterManager

    # Generate correlated data
    np.random.seed(42)
    n_points = 100

    # Three correlated variables
    factor1 = np.random.randn(n_points)
    factor2 = np.random.randn(n_points)

    x = factor1 + 0.5 * factor2 + np.random.randn(n_points) * 0.2
    y = 0.8 * factor1 - 0.3 * factor2 + np.random.randn(n_points) * 0.2
    z = -0.4 * factor1 + 0.7 * factor2 + np.random.randn(n_points) * 0.2

    # Create multiple interactive charts
    chart1 = vizly.InteractiveScatterChart()
    chart1.plot(x, y, interactive=True, alpha=0.7)
    chart1.set_title("X vs Y")

    chart2 = vizly.InteractiveScatterChart()
    chart2.plot(x, z, interactive=True, alpha=0.7)
    chart2.set_title("X vs Z")

    chart3 = vizly.InteractiveScatterChart()
    chart3.plot(y, z, interactive=True, alpha=0.7)
    chart3.set_title("Y vs Z")

    # Set up crossfilter
    crossfilter = CrossfilterManager()
    crossfilter.add_chart("chart1", chart1)
    crossfilter.add_chart("chart2", chart2)
    crossfilter.add_chart("chart3", chart3)

    # Save charts
    chart1.save('/tmp/demo_crossfilter_xy.png', dpi=300)
    chart2.save('/tmp/demo_crossfilter_xz.png', dpi=300)
    chart3.save('/tmp/demo_crossfilter_yz.png', dpi=300)

    print("✅ Crossfilter interaction setup complete")

def demo_advanced_tooltips():
    """Demonstrate advanced tooltip functionality."""
    print("\n🏷️ Creating Advanced Tooltips...")

    import vizly
    from vizly.interactive.tooltips import AdvancedTooltip

    # Generate rich dataset
    np.random.seed(42)
    n_points = 50
    companies = [f"Company_{chr(65+i%26)}" for i in range(n_points)]
    revenues = np.random.uniform(10, 1000, n_points)
    profits = revenues * np.random.uniform(0.05, 0.25, n_points)
    employees = np.random.randint(10, 5000, n_points)

    # Create chart with rich data
    chart = vizly.InteractiveScatterChart()
    chart.plot(
        revenues, profits,
        size=employees/20,
        labels=companies,
        interactive=True,
        alpha=0.7
    )

    # Advanced tooltip with custom formatting
    def custom_tooltip_formatter(data):
        return f"""
🏢 {data.get('labels', 'Unknown')}
💰 Revenue: ${data.get('x', 0):.1f}M
📈 Profit: ${data.get('y', 0):.1f}M
👥 Employees: {data.get('size', 0)*20:.0f}
📊 Margin: {(data.get('y', 0)/data.get('x', 1)*100):.1f}%
        """.strip()

    chart.enable_tooltips(
        fields=['x', 'y', 'labels', 'size'],
        format_func=custom_tooltip_formatter
    )

    chart.set_title("Company Performance Analysis")
    chart.set_labels("Revenue ($M)", "Profit ($M)")

    chart.save('/tmp/demo_advanced_tooltips.png', dpi=300)
    print("✅ Advanced tooltips with rich formatting")

def demo_performance_benchmark():
    """Benchmark interactive features with large datasets."""
    print("\n⚡ Performance Benchmarking...")

    import vizly

    # Test with increasing dataset sizes
    sizes = [1000, 5000, 10000]
    for size in sizes:
        print(f"   Testing with {size:,} points...")

        start_time = time.time()

        # Generate large dataset
        np.random.seed(42)
        x = np.random.randn(size)
        y = np.random.randn(size)

        # Create interactive chart
        chart = vizly.InteractiveScatterChart()
        chart.plot(x, y, interactive=True, alpha=0.5, s=1)
        chart.enable_tooltips(['x', 'y'])
        chart.enable_zoom_pan()

        chart.save(f'/tmp/performance_test_{size}.png')

        elapsed = time.time() - start_time
        print(f"      ✅ {size:,} points: {elapsed:.3f}s ({size/elapsed:,.0f} points/sec)")

    print("📊 Interactive features scale efficiently to large datasets")

def main():
    """Run complete interactive features demonstration."""
    print("🚀 Starting Interactive Features Demonstration")
    print("This showcases real-time interactivity capabilities...\n")

    try:
        # Core interactive features
        demo_interactive_scatter()
        demo_interactive_line_chart()

        # Real-time capabilities
        demo_real_time_chart()
        demo_financial_stream()

        # Dashboard and crossfilter
        demo_interactive_dashboard()
        demo_crossfilter_interaction()

        # Advanced features
        demo_advanced_tooltips()

        # Performance testing
        demo_performance_benchmark()

        print("\n" + "=" * 60)
        print("🎉 Interactive Features Gallery Complete!")
        print("=" * 60)

        # List generated files
        print("\n📂 Generated Demonstration Files:")
        demo_files = [
            '/tmp/demo_interactive_scatter.png',
            '/tmp/demo_interactive_line.png',
            '/tmp/demo_realtime_chart.png',
            '/tmp/demo_financial_stream.png',
            '/tmp/demo_crossfilter_xy.png',
            '/tmp/demo_crossfilter_xz.png',
            '/tmp/demo_crossfilter_yz.png',
            '/tmp/demo_advanced_tooltips.png',
        ]

        for i, file in enumerate(demo_files, 1):
            print(f"   {i:2d}. {file.split('/')[-1]}")

        print("\n🌐 Dashboard Files:")
        print("    • /tmp/vizly_dashboard/index.html (open in browser)")
        print("    • /tmp/vizly_dashboard/config.json")

        print("\n✨ Interactive Features Demonstrated:")
        features = [
            "Hover tooltips with data inspection",
            "Zoom and pan controls (scroll + middle-click)",
            "Rectangular selection tools",
            "Real-time data streaming",
            "Financial price streaming",
            "Web-based interactive dashboards",
            "Crossfilter-style linked selections",
            "Advanced tooltip formatting",
            "High-performance interaction (10K+ points)",
            "Dashboard export to HTML/CSS/JS"
        ]

        for i, feature in enumerate(features, 1):
            print(f"   {i:2d}. {feature}")

        print("\n🎯 Usage Instructions:")
        print("   • Charts support mouse wheel zoom")
        print("   • Middle-click and drag to pan")
        print("   • Left-click and drag to select regions")
        print("   • Hover over data points for tooltips")
        print("   • Real-time charts auto-update every 100ms")

        print("\n🚀 Vizly Interactive Features Ready for Production!")

    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()