import sys

sys.path.insert(0, "src")

import numpy as np

from vizly import BodePlot, StressStrainChart


def test_bode_plot_returns_figure() -> None:
    bode = BodePlot()
    fig = bode.plot([1], [1, 1])
    assert fig.figure is not None
    assert len(fig.figure.axes) == 2


def test_stress_strain_annotations() -> None:
    strain = np.linspace(0, 0.1, 10)
    stress = 200e3 * strain

    chart = StressStrainChart()
    chart.plot(strain, stress / 1e6, yield_point=(0.02, 4.0))
    labels = [handle.get_label() for handle in chart.axes.get_legend().legend_handles]
    assert "Yield Point" in labels
