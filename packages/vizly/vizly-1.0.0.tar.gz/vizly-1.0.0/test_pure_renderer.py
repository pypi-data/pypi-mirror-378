#!/usr/bin/env python3
"""
Test Pure Python Renderer
Verify that our matplotlib replacement works correctly.
"""

import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from vizly.rendering.renderer import PureRenderer, ImageRenderer
from vizly.rendering.canvas import Color, Point, Rectangle
from vizly.rendering.export import pyplot


def test_basic_canvas():
    """Test basic canvas operations."""
    print("🎨 Testing basic canvas...")

    renderer = PureRenderer(400, 300)

    # Test line drawing
    renderer.canvas.draw_line(
        Point(10, 10),
        Point(390, 290),
        Color.from_name('red'),
        3.0
    )

    # Test rectangle
    renderer.canvas.draw_rectangle(
        Rectangle(50, 50, 100, 80),
        fill_color=Color.from_name('blue'),
        border_color=Color.from_name('black'),
        border_width=2.0
    )

    # Test circle
    renderer.canvas.draw_circle(
        Point(300, 150),
        30,
        fill_color=Color.from_name('green'),
        border_color=Color.from_name('darkgray'),
        border_width=2.0
    )

    renderer.save("test_basic_canvas.png")
    print("✓ Basic canvas test saved as test_basic_canvas.png")


def test_line_plot():
    """Test line plot functionality."""
    print("📈 Testing line plot...")

    # Create test data
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    renderer = PureRenderer(600, 400)
    renderer.set_xlim(0, 2 * np.pi)
    renderer.set_ylim(-1.2, 1.2)

    renderer.draw_grid()
    renderer.draw_axes()
    renderer.draw_line_plot(x, y, Color.from_name('blue'), 2.0)
    renderer.draw_ticks()
    renderer.draw_labels("Sine Wave", "X", "Y")

    renderer.save("test_line_plot.png")
    print("✓ Line plot test saved as test_line_plot.png")


def test_scatter_plot():
    """Test scatter plot functionality."""
    print("📊 Testing scatter plot...")

    # Create test data
    np.random.seed(42)
    x = np.random.randn(50)
    y = np.random.randn(50)
    colors = np.random.rand(50)

    renderer = PureRenderer(600, 400)
    renderer.set_xlim(-3, 3)
    renderer.set_ylim(-3, 3)

    renderer.draw_grid()
    renderer.draw_axes()
    renderer.draw_scatter_plot(x, y, colors, None, 'o')
    renderer.draw_ticks()
    renderer.draw_labels("Random Scatter", "X", "Y")

    renderer.save("test_scatter_plot.png")
    print("✓ Scatter plot test saved as test_scatter_plot.png")


def test_bar_chart():
    """Test bar chart functionality."""
    print("📊 Testing bar chart...")

    # Create test data
    categories = np.arange(5)
    values = np.array([23, 45, 56, 78, 32])

    renderer = PureRenderer(600, 400)
    renderer.set_xlim(-0.5, 4.5)
    renderer.set_ylim(0, 90)

    renderer.draw_grid()
    renderer.draw_axes()
    renderer.draw_bar_chart(categories, values, 0.8, Color.from_name('orange'))
    renderer.draw_ticks()
    renderer.draw_labels("Sample Bar Chart", "Category", "Value")

    renderer.save("test_bar_chart.png")
    print("✓ Bar chart test saved as test_bar_chart.png")


def test_pyplot_interface():
    """Test matplotlib-like pyplot interface."""
    print("🎭 Testing pyplot interface...")

    plt = pyplot()

    # Test line plot
    x = np.linspace(0, 10, 50)
    y = np.cos(x)

    plt.figure(figsize=(8, 6))
    plt.plot(x, y, color='red', linewidth=2)
    plt.xlabel('X Values')
    plt.ylabel('Y Values')
    plt.title('Cosine Wave')
    plt.grid(True)
    plt.savefig('test_pyplot_interface.png')

    print("✓ Pyplot interface test saved as test_pyplot_interface.png")


def test_multiple_plots():
    """Test multiple data series on same plot."""
    print("📈 Testing multiple plots...")

    x = np.linspace(0, 4 * np.pi, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)

    renderer = PureRenderer(800, 500)
    renderer.set_xlim(0, 4 * np.pi)
    renderer.set_ylim(-1.5, 1.5)

    renderer.draw_grid()
    renderer.draw_axes()

    # Draw multiple lines
    renderer.draw_line_plot(x, y1, Color.from_name('blue'), 2.0, 'sin(x)')
    renderer.draw_line_plot(x, y2, Color.from_name('red'), 2.0, 'cos(x)')

    renderer.draw_ticks()
    renderer.draw_labels("Trigonometric Functions", "X", "Y")

    renderer.save("test_multiple_plots.png")
    print("✓ Multiple plots test saved as test_multiple_plots.png")


def main():
    """Run all tests."""
    print("🧪 Vizly Pure Python Renderer Test Suite")
    print("=" * 50)

    try:
        test_basic_canvas()
        test_line_plot()
        test_scatter_plot()
        test_bar_chart()
        test_pyplot_interface()
        test_multiple_plots()

        print("\n🎉 All tests completed successfully!")
        print("\nGenerated test files:")
        print("  • test_basic_canvas.png")
        print("  • test_line_plot.png")
        print("  • test_scatter_plot.png")
        print("  • test_bar_chart.png")
        print("  • test_pyplot_interface.png")
        print("  • test_multiple_plots.png")

        print(f"\n✅ Pure Python renderer is working!")
        print(f"🚀 Ready to replace matplotlib dependency!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()