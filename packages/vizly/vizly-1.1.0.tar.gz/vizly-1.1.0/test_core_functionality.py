#!/usr/bin/env python3
"""Test core Vizly functionality as requested by user."""

import vizly
import numpy as np

print("🧪 Testing Vizly Core Functionality")
print("=" * 50)

try:
    # Create sample data for line chart
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    print("📈 Testing Line Chart...")
    # Line charts
    chart = vizly.LineChart()
    chart.plot(x, y, color='blue', linewidth=2)
    chart.set_title("Line Chart Test")
    chart.save("test_line_chart.png")
    print("✓ Line chart created and saved successfully")

except Exception as e:
    print(f"❌ Line chart failed: {e}")

try:
    print("\n📊 Testing Financial Chart...")
    # Financial analysis - create sample OHLC data
    dates = np.arange(30)  # 30 days
    opens = 100 + np.random.randn(30).cumsum() * 2
    highs = opens + np.random.rand(30) * 5
    lows = opens - np.random.rand(30) * 5
    closes = opens + np.random.randn(30) * 2
    volume = np.random.randint(1000, 10000, 30)

    candlestick = vizly.CandlestickChart()
    candlestick.plot(dates, opens, highs, lows, closes, volume)
    candlestick.set_title("Candlestick Chart Test")
    candlestick.save("test_candlestick.png")
    print("✓ Candlestick chart created and saved successfully")

except Exception as e:
    print(f"❌ Candlestick chart failed: {e}")

try:
    print("\n🌄 Testing 3D Surface Chart...")
    # 3D visualization - create sample surface data
    x_3d = np.linspace(-5, 5, 30)
    y_3d = np.linspace(-5, 5, 30)
    X, Y = np.meshgrid(x_3d, y_3d)
    Z = np.sin(np.sqrt(X**2 + Y**2))

    surface = vizly.SurfaceChart()
    surface.plot_surface(X, Y, Z, cmap='viridis')
    surface.set_title("3D Surface Test")
    surface.save("test_surface.png")
    print("✓ 3D surface chart created and saved successfully")

except Exception as e:
    print(f"❌ 3D surface chart failed: {e}")

print("\n🎉 Core functionality test completed!")
print("\nGenerated files:")
print("  - test_line_chart.png")
print("  - test_candlestick.png")
print("  - test_surface.png")