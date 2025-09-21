using System;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Vizly.SDK;

namespace Vizly.SDK.Examples
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Setup logging
            using var loggerFactory = LoggerFactory.Create(builder =>
                builder.AddConsole().SetMinimumLevel(LogLevel.Information));
            var logger = loggerFactory.CreateLogger<Program>();

            logger.LogInformation("🚀 Vizly .NET SDK Example Application");
            logger.LogInformation("=" * 50);

            try
            {
                // Check system info
                var sysInfo = Extensions.GetSystemInfo();
                logger.LogInformation("System Info: {SystemInfo}", sysInfo);

                // Basic line chart example
                await CreateBasicLineChart(logger);

                // Multi-series chart example
                await CreateMultiSeriesChart(logger);

                // Advanced features example
                await DemonstrateAdvancedFeatures(logger);

                logger.LogInformation("✅ All examples completed successfully!");
            }
            catch (Exception ex)
            {
                logger.LogError(ex, "❌ Error running examples");
            }
        }

        static async Task CreateBasicLineChart(ILogger logger)
        {
            logger.LogInformation("📈 Creating Basic Line Chart...");

            var config = new ChartConfig
            {
                Width = 800,
                Height = 600,
                BackgroundColor = "white"
            };

            using var chart = new LineChart(config, logger);

            // Generate sine wave data
            var x = Enumerable.Range(0, 100)
                .Select(i => i * Math.PI / 50.0)
                .ToArray();
            var y = x.Select(Math.Sin).ToArray();

            // Plot the data
            chart.Plot(x, y, "blue", 2.0, "sin(x)");
            chart.SetTitle("Basic Sine Wave - Vizly .NET SDK");
            chart.SetLabels("X", "Y");
            chart.AddGrid();
            chart.AddLegend();

            // Save the chart
            await chart.SaveAsync("basic_line_chart.png");
            logger.LogInformation("✅ Basic line chart saved as 'basic_line_chart.png'");
        }

        static async Task CreateMultiSeriesChart(ILogger logger)
        {
            logger.LogInformation("📊 Creating Multi-Series Chart...");

            var config = new ChartConfig
            {
                Width = 1000,
                Height = 600,
                EnableGpu = Extensions.IsGpuAvailable()
            };

            using var chart = new LineChart(config, logger);

            // Generate multiple series
            var x = Enumerable.Range(0, 200)
                .Select(i => i * Math.PI / 100.0)
                .ToArray();

            var series = new[]
            {
                new LineSeriesData
                {
                    X = x,
                    Y = x.Select(Math.Sin).ToArray(),
                    Color = "blue",
                    LineWidth = 2.0,
                    Label = "sin(x)"
                },
                new LineSeriesData
                {
                    X = x,
                    Y = x.Select(Math.Cos).ToArray(),
                    Color = "red",
                    LineWidth = 2.0,
                    Label = "cos(x)"
                },
                new LineSeriesData
                {
                    X = x,
                    Y = x.Select(v => Math.Sin(2 * v)).ToArray(),
                    Color = "green",
                    LineWidth = 1.5,
                    Label = "sin(2x)"
                }
            };

            chart.PlotMultiple(series);
            chart.SetTitle("Multi-Series Chart - Trigonometric Functions");
            chart.SetLabels("X (radians)", "Y");
            chart.AddGrid(true, false, 0.3);
            chart.AddLegend(LegendPosition.TopRight);

            // Add trend line for sin(x)
            chart.AddTrendLine(x, series[0].Y, "orange", TrendLineType.Polynomial);

            await chart.SaveAsync("multi_series_chart.png");
            logger.LogInformation("✅ Multi-series chart saved as 'multi_series_chart.png'");
        }

        static async Task DemonstrateAdvancedFeatures(ILogger logger)
        {
            logger.LogInformation("🚀 Demonstrating Advanced Features...");

            // Check available features
            var gpuAvailable = Extensions.IsGpuAvailable();
            var vrAvailable = Extensions.IsVrAvailable();
            var version = Extensions.GetVizlyVersion();

            logger.LogInformation("Vizly Version: {Version}", version);
            logger.LogInformation("GPU Available: {GpuAvailable}", gpuAvailable);
            logger.LogInformation("VR Available: {VrAvailable}", vrAvailable);

            if (gpuAvailable)
            {
                logger.LogInformation("🚀 Creating GPU-accelerated chart...");

                var config = new ChartConfig
                {
                    Width = 1200,
                    Height = 800,
                    EnableGpu = true
                };

                using var gpuChart = new LineChart(config, logger);

                // Large dataset for GPU demonstration
                var random = new Random(42);
                var largeX = Enumerable.Range(0, 10000)
                    .Select(i => i / 1000.0)
                    .ToArray();
                var largeY = largeX.Select(x =>
                    Math.Sin(x) + 0.1 * random.NextDouble())
                    .ToArray();

                gpuChart.Plot(largeX, largeY, "purple", 1.0, "Noisy Signal");
                gpuChart.SetTitle("GPU-Accelerated Rendering - 10K Points");
                gpuChart.SetLabels("Time", "Signal");
                gpuChart.AddGrid();

                await gpuChart.SaveAsync("gpu_accelerated_chart.png");
                logger.LogInformation("✅ GPU-accelerated chart saved");
            }

            // Export as base64 for web integration
            var webChart = new LineChart(new ChartConfig { Width = 600, Height = 400 }, logger);
            var webX = Enumerable.Range(0, 50).Select(i => i / 10.0).ToArray();
            var webY = webX.Select(x => Math.Exp(-x) * Math.Cos(x)).ToArray();

            webChart.Plot(webX, webY, "red", 2.5, "Damped Oscillation");
            webChart.SetTitle("Web Integration Example");

            var base64Data = await webChart.ExportBase64Async();
            logger.LogInformation("✅ Chart exported as base64 (length: {Length})", base64Data.Length);

            webChart.Dispose();
        }
    }
}