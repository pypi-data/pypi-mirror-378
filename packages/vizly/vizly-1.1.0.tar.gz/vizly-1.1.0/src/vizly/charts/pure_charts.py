"""
Pure Python Chart Implementations
================================

Chart classes built with zero external dependencies except NumPy.
No matplotlib, plotly, or other heavy dependencies.
"""

from __future__ import annotations

from typing import Optional, Tuple, List, Union
import warnings

import numpy as np

from ..rendering.pure_engine import PureRenderer, Color


class PureChart:
    """Base class for pure Python charts."""

    def __init__(self, width: int = 800, height: int = 600, title: str = ""):
        self.width = width
        self.height = height
        self.title = title
        self.renderer = PureRenderer(width, height)

        # Chart styling
        self.background_color = "white"
        self.title_color = "black"
        self.grid_color = "lightgray"
        self.border_color = "black"

        # Data storage
        self.data_series = []

    def set_title(self, title: str):
        """Set chart title."""
        self.title = title
        return self

    def set_background_color(self, color: str):
        """Set background color."""
        self.background_color = color
        return self

    def add_grid(self, alpha: float = 0.3):
        """Add grid to chart (placeholder for now)."""
        # Grid implementation would go here
        return self

    def set_labels(self, xlabel: str = "", ylabel: str = ""):
        """Set axis labels (placeholder for now)."""
        # Label implementation would go here
        return self

    def add_legend(self):
        """Add legend (placeholder for now)."""
        # Legend implementation would go here
        return self

    def save(self, filename: str, dpi: int = 300):
        """Save chart to file."""
        self.renderer.save(filename, dpi)

    def show(self):
        """Display chart."""
        self.renderer.show()


class LineChart(PureChart):
    """Pure Python line chart implementation."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)
        self.lines = []

    def plot(self, x: np.ndarray, y: np.ndarray, color: str = 'blue',
             linewidth: float = 2.0, label: str = ""):
        """Plot a line."""
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        self.lines.append({
            'x': x,
            'y': y,
            'color': color,
            'linewidth': linewidth,
            'label': label
        })

        # Render the line
        self.renderer.plot(x, y, color, linewidth)
        return self

    def clear(self):
        """Clear all lines."""
        self.lines = []
        self.renderer = PureRenderer(self.width, self.height)
        return self


class ScatterChart(PureChart):
    """Pure Python scatter chart implementation."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)
        self.points = []

    def plot(self, x: np.ndarray, y: np.ndarray, color: str = 'blue',
             size: float = 20, alpha: float = 1.0, label: str = ""):
        """Plot scatter points."""
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        self.points.append({
            'x': x,
            'y': y,
            'color': color,
            'size': size,
            'alpha': alpha,
            'label': label
        })

        # Render the points
        self.renderer.scatter(x, y, color, size)
        return self

    def scatter(self, x: np.ndarray, y: np.ndarray, **kwargs):
        """Alias for plot method."""
        return self.plot(x, y, **kwargs)


class BarChart(PureChart):
    """Pure Python bar chart implementation."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)
        self.bars = []

    def bar(self, x: Union[np.ndarray, List], height: Union[np.ndarray, List],
            color: str = 'blue', width: float = 0.8, label: str = ""):
        """Plot bars."""
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(height, np.ndarray):
            height = np.array(height)

        # If x contains strings, convert to numeric indices
        if x.dtype.kind in ['U', 'S', 'O']:  # String types
            x_labels = x.copy()
            x = np.arange(len(x))
        else:
            x_labels = None

        self.bars.append({
            'x': x,
            'height': height,
            'x_labels': x_labels,
            'color': color,
            'width': width,
            'label': label
        })

        # Render the bars
        self.renderer.bar(x, height, color, width)
        return self

    def barh(self, y: Union[np.ndarray, List], width: Union[np.ndarray, List],
             color: str = 'blue', height: float = 0.8, label: str = ""):
        """Plot horizontal bars (simplified implementation)."""
        # For now, just convert to vertical bars
        # Full horizontal bar implementation would require renderer updates
        return self.bar(y, width, color, height, label)


class SurfaceChart(PureChart):
    """Pure Python 3D surface chart (simplified 2D projection)."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)
        self.surfaces = []

    def plot_surface(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                    cmap: str = 'viridis', alpha: float = 1.0):
        """Plot 3D surface as 2D contour-like visualization."""
        if X.shape != Y.shape or X.shape != Z.shape:
            raise ValueError("X, Y, and Z must have the same shape")

        self.surfaces.append({
            'X': X,
            'Y': Y,
            'Z': Z,
            'cmap': cmap,
            'alpha': alpha
        })

        # Simplified surface rendering as contour lines
        # Get contour levels
        z_min, z_max = np.min(Z), np.max(Z)
        levels = np.linspace(z_min, z_max, 10)

        # Set viewport based on X, Y ranges
        x_min, x_max = np.min(X), np.max(X)
        y_min, y_max = np.min(Y), np.max(Y)
        self.renderer.canvas.set_viewport(x_min, x_max, y_min, y_max)

        # Draw simplified contour representation
        colors = ['blue', 'green', 'yellow', 'orange', 'red']
        for i, level in enumerate(levels[::2]):  # Every other level
            color = colors[i % len(colors)]
            self.renderer.canvas.set_stroke_color(color)

            # Find points close to this level
            mask = np.abs(Z - level) < (z_max - z_min) / 20
            x_points = X[mask]
            y_points = Y[mask]

            # Draw points at this level
            for j in range(len(x_points)):
                if j < len(x_points) - 1:
                    self.renderer.canvas.draw_line(
                        float(x_points[j]), float(y_points[j]),
                        float(x_points[j+1]), float(y_points[j+1])
                    )

        return self

    def plot(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, **kwargs):
        """Alias for plot_surface."""
        return self.plot_surface(X, Y, Z, **kwargs)

    def export_mesh(self, filename: str = "surface_mesh.json"):
        """Export surface mesh data."""
        if not self.surfaces:
            return {"rows": 0, "cols": 0, "x": [], "zmin": 0, "zmax": 0}

        surface = self.surfaces[0]
        X, Y, Z = surface['X'], surface['Y'], surface['Z']

        mesh_data = {
            "rows": Z.shape[0],
            "cols": Z.shape[1],
            "x": X.flatten().tolist(),
            "y": Y.flatten().tolist(),
            "z": Z.flatten().tolist(),
            "zmin": float(np.min(Z)),
            "zmax": float(np.max(Z))
        }

        if filename:
            import json
            with open(filename, 'w') as f:
                json.dump(mesh_data, f, indent=2)

        return mesh_data


class HeatmapChart(PureChart):
    """Pure Python heatmap implementation."""

    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)

    def heatmap(self, data: np.ndarray, cmap: str = 'viridis',
                xticklabels: Optional[List] = None,
                yticklabels: Optional[List] = None):
        """Create heatmap from 2D array."""
        if data.ndim != 2:
            raise ValueError("Data must be 2D array")

        rows, cols = data.shape
        cell_width = self.width / cols
        cell_height = self.height / rows

        # Normalize data to 0-1 range for color mapping
        data_norm = (data - np.min(data)) / (np.max(data) - np.min(data))

        # Simple grayscale colormap
        for i in range(rows):
            for j in range(cols):
                intensity = data_norm[i, j]
                if cmap == 'viridis':
                    # Simplified viridis: blue to yellow
                    color = Color(intensity, intensity, 1.0 - intensity)
                elif cmap == 'hot':
                    # Hot colormap: black to red to yellow to white
                    if intensity < 0.33:
                        color = Color(intensity * 3, 0, 0)
                    elif intensity < 0.66:
                        color = Color(1.0, (intensity - 0.33) * 3, 0)
                    else:
                        color = Color(1.0, 1.0, (intensity - 0.66) * 3)
                else:
                    # Default grayscale
                    color = Color(intensity, intensity, intensity)

                # Draw cell
                x = j * cell_width
                y = i * cell_height
                self.renderer.canvas.set_fill_color(color)
                self.renderer.canvas.draw_rectangle(x, y, cell_width, cell_height, fill=True)

        return self


# For backward compatibility with existing code
InteractiveSurfaceChart = SurfaceChart