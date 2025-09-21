# 🔵 Vizly .NET SDK

## **Professional Visualization for .NET Applications**

The **Vizly .NET SDK** brings GPU-accelerated visualization, VR/AR capabilities, and real-time streaming to .NET 6.0+ applications. Built with enterprise-grade architecture and seamless Python interop.

[![NuGet Package](https://img.shields.io/badge/NuGet-Vizly.SDK-blue)](mailto:durai@infinidatum.net)
[![.NET 6.0+](https://img.shields.io/badge/.NET-6.0%2B-purple)](https://dotnet.microsoft.com/)
[![Commercial License](https://img.shields.io/badge/License-Commercial-green)](mailto:durai@infinidatum.net)

---

## 🚀 **Quick Start**

### **Installation**
```bash
# Via NuGet Package Manager
dotnet add package Vizly.SDK

# Via Package Manager Console
Install-Package Vizly.SDK
```

### **Hello World Example**
```csharp
using Vizly.SDK;
using Microsoft.Extensions.Logging;

// Setup logging
using var loggerFactory = LoggerFactory.Create(builder =>
    builder.AddConsole().SetMinimumLevel(LogLevel.Information));
var logger = loggerFactory.CreateLogger<Program>();

// Create chart configuration
var config = new ChartConfig
{
    Width = 800,
    Height = 600,
    EnableGpu = Extensions.IsGpuAvailable()
};

// Create and use chart
using var chart = new LineChart(config, logger);

// Generate data
var x = Enumerable.Range(0, 100).Select(i => i * Math.PI / 50.0).ToArray();
var y = x.Select(Math.Sin).ToArray();

// Plot and save
chart.Plot(x, y, "blue", 2.0, "sin(x)");
chart.SetTitle("Vizly .NET SDK - Hello World");
await chart.SaveAsync("hello_world.png");

Console.WriteLine("✅ Chart created successfully!");
```

---

## 🌟 **Key Features**

### **🚀 High Performance**
- **GPU Acceleration**: CUDA/OpenCL support with automatic backend selection
- **Async Operations**: Non-blocking chart operations with `async/await` patterns
- **Memory Efficient**: Smart resource management and disposal patterns
- **Multi-threading**: Safe for concurrent operations

### **🎨 Rich Visualization**
- **Multiple Chart Types**: Line, Scatter, Bar, Surface, Heatmap
- **Advanced Styling**: Professional themes and customization
- **Export Formats**: PNG, SVG with high DPI support
- **Interactive Elements**: Real-time updates and streaming

### **🔧 Enterprise Integration**
- **Dependency Injection**: Full support for .NET DI containers
- **Logging Integration**: Microsoft.Extensions.Logging compatible
- **Configuration**: Strongly-typed configuration objects
- **Error Handling**: Comprehensive exception handling

---

## 📊 **Chart Types & Examples**

### **LineChart - Time Series Visualization**
```csharp
using var chart = new LineChart(config);

// Single series
chart.Plot(timeData, priceData, "blue", 2.0, "Stock Price");

// Multiple series
var series = new[]
{
    new LineSeriesData
    {
        X = timeData,
        Y = priceData,
        Color = "blue",
        LineWidth = 2.0,
        Label = "Price"
    },
    new LineSeriesData
    {
        X = timeData,
        Y = volumeData,
        Color = "red",
        LineWidth = 1.5,
        Label = "Volume"
    }
};

chart.PlotMultiple(series);
chart.SetTitle("Financial Data Analysis");
chart.SetLabels("Time", "Value");
chart.AddGrid();
chart.AddLegend();

await chart.SaveAsync("financial_chart.png");
```

### **ScatterChart - Correlation Analysis**
```csharp
using var scatter = new ScatterChart(config);

// Generate sample data
var random = new Random(42);
var x = Enumerable.Range(0, 1000).Select(_ => random.NextGaussian()).ToArray();
var y = x.Select(val => 2 * val + random.NextGaussian() * 0.5).ToArray();

scatter.Plot(x, y, "red", 5.0, "Correlation Data");
scatter.SetTitle("Correlation Analysis");
scatter.SetLabels("X Variable", "Y Variable");

// Add trend line
scatter.AddTrendLine(x, y, TrendLineType.Linear, "blue");

await scatter.SaveAsync("correlation_analysis.png");
```

### **Async Operations**
```csharp
// Create multiple charts concurrently
var tasks = new[]
{
    CreateLineChartAsync(data1, "chart1.png"),
    CreateScatterChartAsync(data2, "chart2.png"),
    CreateBarChartAsync(data3, "chart3.png")
};

await Task.WhenAll(tasks);
Console.WriteLine("All charts created!");

async Task CreateLineChartAsync(double[] data, string filename)
{
    using var chart = new LineChart(config);
    chart.Plot(Enumerable.Range(0, data.Length).Select(i => (double)i).ToArray(),
               data, "blue", 2.0);
    await chart.SaveAsync(filename);
}
```

---

## 🚀 **Advanced Features**

### **GPU Acceleration**
```csharp
// Check GPU availability
if (Extensions.IsGpuAvailable())
{
    var gpuConfig = new ChartConfig
    {
        Width = 1200,
        Height = 800,
        EnableGpu = true
    };

    using var chart = new LineChart(gpuConfig);

    // Process large dataset with GPU acceleration
    var largeX = Enumerable.Range(0, 100000).Select(i => i / 1000.0).ToArray();
    var largeY = largeX.Select(x => Math.Sin(x) + random.NextGaussian() * 0.1).ToArray();

    var stopwatch = Stopwatch.StartTime();
    chart.Plot(largeX, largeY, "purple", 1.0, "Large Dataset");
    var elapsed = stopwatch.Elapsed;

    logger.LogInformation("GPU rendering completed in {Elapsed}ms", elapsed.TotalMilliseconds);
    await chart.SaveAsync("gpu_accelerated.png");
}
```

### **System Information**
```csharp
var sysInfo = Extensions.GetSystemInfo();
Console.WriteLine($"Vizly Version: {sysInfo.Version}");
Console.WriteLine($"GPU Available: {sysInfo.GpuAvailable}");
Console.WriteLine($"VR Available: {sysInfo.VrAvailable}");
Console.WriteLine($"Streaming Available: {sysInfo.StreamingAvailable}");
Console.WriteLine($"Platform: {sysInfo.Platform}");
```

### **Memory Management**
```csharp
// Proper resource disposal
using var chart = new LineChart(config);
// Chart automatically disposed when leaving scope

// Manual disposal if needed
chart.Dispose();

// Bulk operations with automatic cleanup
await ProcessMultipleChartsAsync(datasets);

async Task ProcessMultipleChartsAsync(IEnumerable<double[]> datasets)
{
    foreach (var data in datasets)
    {
        using var chart = new LineChart(config);
        chart.Plot(GenerateXData(data.Length), data);
        await chart.SaveAsync($"chart_{Guid.NewGuid()}.png");
        // Chart automatically disposed each iteration
    }
}
```

---

## 🛠️ **Configuration & Setup**

### **Dependency Injection Setup**
```csharp
// Program.cs or Startup.cs
services.AddLogging(builder => builder.AddConsole());
services.AddSingleton<ChartConfig>(provider => new ChartConfig
{
    Width = 800,
    Height = 600,
    EnableGpu = Extensions.IsGpuAvailable(),
    Theme = "professional"
});

// Usage in controllers/services
public class ChartService
{
    private readonly ChartConfig _config;
    private readonly ILogger<ChartService> _logger;

    public ChartService(ChartConfig config, ILogger<ChartService> logger)
    {
        _config = config;
        _logger = logger;
    }

    public async Task<byte[]> CreateChartAsync(double[] x, double[] y)
    {
        using var chart = new LineChart(_config, _logger);
        chart.Plot(x, y);

        // Export as base64 for web integration
        var base64Data = await chart.ExportBase64Async();
        return Convert.FromBase64String(base64Data);
    }
}
```

### **Configuration Options**
```csharp
public class ChartConfig
{
    public int Width { get; set; } = 800;
    public int Height { get; set; } = 600;
    public string BackgroundColor { get; set; } = "white";
    public bool EnableGpu { get; set; } = false;
    public bool EnableVr { get; set; } = false;
    public string Theme { get; set; } = "default";
}

// Usage
var config = new ChartConfig
{
    Width = 1920,
    Height = 1080,
    BackgroundColor = "#f8f9fa",
    EnableGpu = true,
    Theme = "dark"
};
```

---

## 📚 **API Reference**

### **VizlyChart (Base Class)**
```csharp
public abstract class VizlyChart : IDisposable
{
    // Core methods
    public void SetTitle(string title);
    public async Task SaveAsync(string filePath, int dpi = 300);
    public async Task<string> ExportBase64Async(int dpi = 300);
    public (int Width, int Height) GetDimensions();

    // Resource management
    public virtual void Dispose();
}
```

### **LineChart**
```csharp
public class LineChart : VizlyChart
{
    // Constructors
    public LineChart(ChartConfig config = null, ILogger logger = null);

    // Plotting methods
    public void Plot(double[] x, double[] y, string color = "blue",
                     double lineWidth = 2.0, string label = "");
    public void PlotMultiple(LineSeriesData[] series);

    // Enhancement methods
    public void AddTrendLine(double[] x, double[] y, string color = "red",
                            TrendLineType type = TrendLineType.Linear);
    public void SetLabels(string xLabel, string yLabel);
    public void AddLegend(LegendPosition position = LegendPosition.TopRight);
    public void AddGrid(bool major = true, bool minor = false, double alpha = 0.3);
}
```

### **Extensions & Utilities**
```csharp
public static class Extensions
{
    // NumPy integration
    public static PyObject ToNumpyArray(this double[] array);
    public static PyObject ToNumpyArray(this double[,] array);
    public static double[] ToDoubleArray(this PyObject npArray);

    // System information
    public static bool IsGpuAvailable();
    public static bool IsVrAvailable();
    public static string GetVizlyVersion();
    public static VizlySystemInfo GetSystemInfo();
}
```

---

## 🔧 **Performance Optimization**

### **Best Practices**
```csharp
// 1. Use GPU acceleration for large datasets
var config = new ChartConfig { EnableGpu = Extensions.IsGpuAvailable() };

// 2. Dispose charts properly
using var chart = new LineChart(config);

// 3. Use async operations for I/O
await chart.SaveAsync("output.png");

// 4. Pre-allocate arrays for better performance
var x = new double[dataSize];
var y = new double[dataSize];
// ... populate arrays
chart.Plot(x, y);

// 5. Use appropriate data types
double[] data = GetDoubleData(); // Preferred over object[]
```

### **Memory Optimization**
```csharp
// Process large datasets in chunks
await ProcessDataInChunksAsync(largeDataset, chunkSize: 10000);

async Task ProcessDataInChunksAsync(double[] data, int chunkSize)
{
    for (int i = 0; i < data.Length; i += chunkSize)
    {
        var chunk = data.Skip(i).Take(chunkSize).ToArray();
        using var chart = new LineChart(config);
        chart.Plot(GenerateXData(chunk.Length), chunk);
        await chart.SaveAsync($"chunk_{i / chunkSize}.png");

        // Force garbage collection if needed
        if (i % (chunkSize * 10) == 0)
        {
            GC.Collect();
            GC.WaitForPendingFinalizers();
        }
    }
}
```

---

## 🧪 **Testing**

### **Unit Testing Example**
```csharp
[Test]
public async Task LineChart_Plot_CreatesValidChart()
{
    // Arrange
    var config = new ChartConfig { Width = 400, Height = 300 };
    using var chart = new LineChart(config);
    var x = new double[] { 1, 2, 3, 4, 5 };
    var y = new double[] { 2, 4, 6, 8, 10 };

    // Act
    chart.Plot(x, y, "blue", 2.0, "test");
    var (width, height) = chart.GetDimensions();

    // Assert
    Assert.AreEqual(400, width);
    Assert.AreEqual(300, height);

    // Test export
    var base64 = await chart.ExportBase64Async();
    Assert.IsNotEmpty(base64);
}

[Test]
public void Extensions_IsGpuAvailable_ReturnsBoolean()
{
    // Act
    var gpuAvailable = Extensions.IsGpuAvailable();

    // Assert
    Assert.IsInstanceOf<bool>(gpuAvailable);
}
```

---

## 💼 **Enterprise Features**

### **Commercial Licensing**
- **Professional Support**: Email support with 48-hour response time
- **Enterprise Support**: 24/7 phone/video support with SLA guarantees
- **Custom Development**: Tailored features and integrations
- **Training**: Professional .NET SDK training programs

### **Security & Compliance**
- **Data Security**: No data leaves your environment
- **Compliance**: GDPR, HIPAA, SOX compatible
- **Audit Logging**: Comprehensive operation logging
- **Access Control**: Role-based access management

### **Scalability**
- **Cloud Deployment**: Azure, AWS, GCP compatible
- **Containerization**: Docker and Kubernetes ready
- **Load Balancing**: Multi-instance chart generation
- **Caching**: Intelligent chart caching strategies

---

## 📞 **Support & Resources**

### **Documentation**
- **API Reference**: Complete method documentation
- **Examples**: Comprehensive example gallery
- **Best Practices**: Performance and architecture guides
- **Migration Guide**: From other charting libraries

### **Community & Support**
- **Email**: durai@infinidatum.net
- **Subject Line**: ".NET SDK Support Request"
- **Include**: .NET version, Vizly version, issue description

### **Training & Consulting**
- **SDK Training**: 2-day intensive .NET SDK training
- **Architecture Review**: Best practices for enterprise deployment
- **Custom Development**: Tailored chart types and features
- **Integration Support**: End-to-end implementation assistance

---

## 🚀 **Getting Started Checklist**

- [ ] Install Vizly.SDK NuGet package
- [ ] Verify Python environment and Vizly core package
- [ ] Run basic LineChart example
- [ ] Test GPU acceleration (if available)
- [ ] Explore async operations
- [ ] Implement proper disposal patterns
- [ ] Set up logging and configuration
- [ ] Contact for enterprise licensing if needed

### **Next Steps**
1. **Evaluate**: Test with your data and use cases
2. **Integrate**: Add to your .NET applications
3. **Optimize**: Implement performance best practices
4. **Scale**: Deploy to production environments
5. **Support**: Contact for enterprise features and support

---

**🔵 Transform your .NET applications with professional visualization capabilities.**

**Contact durai@infinidatum.net for enterprise licensing and support.**

---

*© 2024 Infinidatum Corporation. All rights reserved. Commercial license required for enterprise use.*