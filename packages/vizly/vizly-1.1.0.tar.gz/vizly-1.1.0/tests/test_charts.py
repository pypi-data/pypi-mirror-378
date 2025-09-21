import sys

sys.path.insert(0, "src")

import numpy as np
import pytest

from vizly import (
    ChartValidationError,
    InteractiveSurfaceChart,
    LineChart,
    VizlyFigure,
    ScatterChart,
)


def test_line_chart_plots_line() -> None:
    fig = VizlyFigure(style="light")
    chart = LineChart(fig, label="demo")
    line = chart.plot([0, 1, 2], [0, 1, 0])
    assert line.get_label() == "demo"
    assert len(fig.axes.lines) == 1


def test_line_chart_validates_lengths() -> None:
    chart = LineChart(VizlyFigure())
    with pytest.raises(ChartValidationError):
        chart.plot([0, 1], [1])


def test_scatter_chart_accepts_numpy_arrays() -> None:
    fig = VizlyFigure(style="dark")
    scatter = ScatterChart(fig)
    x = np.linspace(0, 1, 5)
    y = x**2
    scatter.plot(x, y)
    assert len(fig.axes.collections) == 1


def test_interactive_surface_export_mesh() -> None:
    fig = VizlyFigure(style="light")
    chart = InteractiveSurfaceChart(fig)
    x = np.linspace(-1, 1, 5)
    y = np.linspace(-1, 1, 5)
    xv, yv = np.meshgrid(x, y)
    zv = np.sin(xv) * np.cos(yv)
    chart.plot(xv, yv, zv, enable_interaction=False)
    mesh = chart.export_mesh()
    assert mesh["rows"] == 5
    assert mesh["cols"] == 5
    assert len(mesh["x"]) == 25
    assert mesh["zmin"] <= mesh["zmax"]
