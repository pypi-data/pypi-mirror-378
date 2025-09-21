using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Python.Runtime;
using Microsoft.Extensions.Logging;

namespace Vizly.SDK
{
    /// <summary>
    /// Base class for all Vizly charts providing common functionality
    /// </summary>
    public abstract class VizlyChart : IDisposable
    {
        protected PyObject? _chart;
        protected readonly ILogger _logger;
        protected bool _disposed = false;

        protected VizlyChart(ILogger logger)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            InitializePython();
        }

        /// <summary>
        /// Initialize Python runtime and import Vizly
        /// </summary>
        private static void InitializePython()
        {
            if (!PythonEngine.IsInitialized)
            {
                PythonEngine.Initialize();
            }
        }

        /// <summary>
        /// Set chart title
        /// </summary>
        public void SetTitle(string title)
        {
            ThrowIfDisposed();
            _chart?.InvokeMethod("set_title", title.ToPython());
            _logger.LogDebug("Chart title set to: {Title}", title);
        }

        /// <summary>
        /// Save chart to file
        /// </summary>
        public async Task SaveAsync(string filePath, int dpi = 300)
        {
            ThrowIfDisposed();
            await Task.Run(() =>
            {
                _chart?.InvokeMethod("save", filePath.ToPython(), dpi.ToPython());
                _logger.LogInfo("Chart saved to: {FilePath} with DPI: {Dpi}", filePath, dpi);
            });
        }

        /// <summary>
        /// Export chart as base64 PNG
        /// </summary>
        public async Task<string> ExportBase64Async(int dpi = 300)
        {
            ThrowIfDisposed();
            return await Task.Run(() =>
            {
                using var result = _chart?.InvokeMethod("export_base64", dpi.ToPython());
                var base64 = result?.ToString() ?? string.Empty;
                _logger.LogDebug("Chart exported as base64, length: {Length}", base64.Length);
                return base64;
            });
        }

        /// <summary>
        /// Get chart dimensions
        /// </summary>
        public (int Width, int Height) GetDimensions()
        {
            ThrowIfDisposed();
            using var width = _chart?.GetAttr("width");
            using var height = _chart?.GetAttr("height");
            return (width?.As<int>() ?? 0, height?.As<int>() ?? 0);
        }

        protected void ThrowIfDisposed()
        {
            if (_disposed)
                throw new ObjectDisposedException(GetType().Name);
        }

        public virtual void Dispose()
        {
            if (!_disposed)
            {
                _chart?.Dispose();
                _chart = null;
                _disposed = true;
                _logger.LogDebug("Chart disposed");
            }
        }
    }

    /// <summary>
    /// Configuration for Vizly charts
    /// </summary>
    public class ChartConfig
    {
        public int Width { get; set; } = 800;
        public int Height { get; set; } = 600;
        public string BackgroundColor { get; set; } = "white";
        public bool EnableGpu { get; set; } = false;
        public bool EnableVr { get; set; } = false;
        public string Theme { get; set; } = "default";

        public PyDict ToPython()
        {
            var config = new PyDict();
            config["width"] = Width.ToPython();
            config["height"] = Height.ToPython();
            config["background_color"] = BackgroundColor.ToPython();
            config["enable_gpu"] = EnableGpu.ToPython();
            config["enable_vr"] = EnableVr.ToPython();
            config["theme"] = Theme.ToPython();
            return config;
        }
    }
}