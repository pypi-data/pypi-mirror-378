using System;
using System.Linq;
using Microsoft.Extensions.Logging;
using Python.Runtime;

namespace Vizly.SDK
{
    /// <summary>
    /// Vizly Line Chart for .NET applications
    /// </summary>
    public class LineChart : VizlyChart
    {
        public LineChart(ChartConfig? config = null, ILogger? logger = null)
            : base(logger ?? Microsoft.Extensions.Logging.Abstractions.NullLogger.Instance)
        {
            config ??= new ChartConfig();
            InitializeChart(config);
        }

        private void InitializeChart(ChartConfig config)
        {
            using (Py.GIL())
            {
                dynamic vizly = Py.Import("vizly");
                _chart = vizly.LineChart(
                    width: config.Width,
                    height: config.Height,
                    background_color: config.BackgroundColor
                );

                if (config.EnableGpu)
                {
                    _chart.set_backend("gpu");
                }

                _logger.LogInfo("LineChart initialized with dimensions: {Width}x{Height}",
                    config.Width, config.Height);
            }
        }

        /// <summary>
        /// Plot line data
        /// </summary>
        public void Plot(double[] x, double[] y, string color = "blue", double lineWidth = 2.0, string label = "")
        {
            ThrowIfDisposed();

            if (x.Length != y.Length)
                throw new ArgumentException("X and Y arrays must have the same length");

            using (Py.GIL())
            {
                var xArray = x.ToNumpyArray();
                var yArray = y.ToNumpyArray();

                var kwargs = new PyDict();
                kwargs["color"] = color.ToPython();
                kwargs["linewidth"] = lineWidth.ToPython();
                if (!string.IsNullOrEmpty(label))
                    kwargs["label"] = label.ToPython();

                _chart?.InvokeMethod("plot", new PyObject[] { xArray, yArray }, kwargs);

                _logger.LogDebug("Plotted line with {Count} points, color: {Color}",
                    x.Length, color);
            }
        }

        /// <summary>
        /// Plot multiple series
        /// </summary>
        public void PlotMultiple(LineSeriesData[] series)
        {
            ThrowIfDisposed();

            foreach (var s in series)
            {
                Plot(s.X, s.Y, s.Color, s.LineWidth, s.Label);
            }

            _logger.LogInfo("Plotted {Count} line series", series.Length);
        }

        /// <summary>
        /// Add trend line
        /// </summary>
        public void AddTrendLine(double[] x, double[] y, string color = "red",
            TrendLineType type = TrendLineType.Linear)
        {
            ThrowIfDisposed();

            using (Py.GIL())
            {
                var xArray = x.ToNumpyArray();
                var yArray = y.ToNumpyArray();

                _chart?.InvokeMethod("add_trendline",
                    xArray, yArray, color.ToPython(), type.ToString().ToLower().ToPython());

                _logger.LogDebug("Added {Type} trend line", type);
            }
        }

        /// <summary>
        /// Set axis labels
        /// </summary>
        public void SetLabels(string xLabel, string yLabel)
        {
            ThrowIfDisposed();
            _chart?.InvokeMethod("set_labels", xLabel.ToPython(), yLabel.ToPython());
            _logger.LogDebug("Set axis labels: X='{XLabel}', Y='{YLabel}'", xLabel, yLabel);
        }

        /// <summary>
        /// Add legend
        /// </summary>
        public void AddLegend(LegendPosition position = LegendPosition.TopRight)
        {
            ThrowIfDisposed();
            _chart?.InvokeMethod("add_legend", position.ToString().ToLower().ToPython());
            _logger.LogDebug("Added legend at position: {Position}", position);
        }

        /// <summary>
        /// Add grid
        /// </summary>
        public void AddGrid(bool major = true, bool minor = false, double alpha = 0.3)
        {
            ThrowIfDisposed();
            _chart?.InvokeMethod("add_grid",
                major.ToPython(), minor.ToPython(), alpha.ToPython());
            _logger.LogDebug("Added grid: major={Major}, minor={Minor}, alpha={Alpha}",
                major, minor, alpha);
        }
    }

    /// <summary>
    /// Data for a line series
    /// </summary>
    public class LineSeriesData
    {
        public double[] X { get; set; } = Array.Empty<double>();
        public double[] Y { get; set; } = Array.Empty<double>();
        public string Color { get; set; } = "blue";
        public double LineWidth { get; set; } = 2.0;
        public string Label { get; set; } = "";
    }

    /// <summary>
    /// Trend line types
    /// </summary>
    public enum TrendLineType
    {
        Linear,
        Polynomial,
        Exponential,
        Logarithmic
    }

    /// <summary>
    /// Legend positions
    /// </summary>
    public enum LegendPosition
    {
        TopLeft,
        TopRight,
        BottomLeft,
        BottomRight,
        Center
    }
}