# ⚡ Vizly C++ SDK

## **High-Performance Native Visualization Library**

The **Vizly C++ SDK** delivers maximum performance with native GPU acceleration, VR/AR capabilities, and enterprise-grade memory management. Built with modern C++17 standards and cross-platform compatibility.

[![vcpkg Package](https://img.shields.io/badge/vcpkg-Ready-blue)](mailto:durai@infinidatum.net)
[![C++17](https://img.shields.io/badge/C%2B%2B-17-red)](https://en.cppreference.com/w/cpp/17)
[![Cross Platform](https://img.shields.io/badge/Platform-Linux%2FWindows%2FmacOS-green)](mailto:durai@infinidatum.net)

---

## 🚀 **Quick Start**

### **Installation via CMake**
```cmake
# CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(MyVizlyApp)

# Find Vizly SDK
find_package(Vizly REQUIRED)

# Create executable
add_executable(my_app main.cpp)
target_link_libraries(my_app Vizly::vizly)
```

### **Installation via vcpkg**
```bash
# Install via vcpkg
vcpkg install vizly

# Or build from source
git clone https://github.com/infinidatum/vizly-cpp-sdk
cd vizly-cpp-sdk
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
cmake --build .
cmake --install .
```

### **Hello World Example**
```cpp
#include <vizly/Vizly.h>
#include <iostream>
#include <vector>
#include <cmath>

int main() {
    try {
        // Initialize Vizly engine
        vizly::EngineConfig config;
        config.verbose = true;

        if (!vizly::Initialize(config)) {
            std::cerr << "Failed to initialize Vizly engine" << std::endl;
            return 1;
        }

        // Create chart configuration
        vizly::ChartConfig chart_config;
        chart_config.width = 800;
        chart_config.height = 600;
        chart_config.enable_gpu = vizly::IsGpuAvailable();

        // Create line chart
        auto chart = vizly::CreateLineChart(chart_config);

        // Generate sine wave data
        std::vector<double> x, y;
        for (int i = 0; i < 100; ++i) {
            double x_val = i * M_PI / 50.0;
            x.push_back(x_val);
            y.push_back(std::sin(x_val));
        }

        // Plot data
        chart->Plot(x, y, vizly::Color::FromName("blue"), 2.0, "sin(x)");
        chart->SetTitle("Vizly C++ SDK - Hello World");
        chart->SetAxisLabels("X", "Y");
        chart->ShowGrid(true);
        chart->ShowLegend(true);

        // Save chart
        chart->Save("hello_world.png");

        std::cout << "✅ Chart created successfully!" << std::endl;

        // Cleanup
        vizly::Shutdown();
        return 0;

    } catch (const vizly::VizlyException& e) {
        std::cerr << "Vizly Error: " << e.what() << std::endl;
        return 1;
    }
}
```

---

## 🌟 **Key Features**

### **🚀 Maximum Performance**
- **Native GPU Acceleration**: Direct CUDA/OpenCL integration
- **Zero-Copy Operations**: Efficient memory management
- **SIMD Optimization**: Vectorized operations for large datasets
- **Multi-threading**: Thread-safe operations with parallel processing

### **🎨 Professional Visualization**
- **Multiple Chart Types**: Line, Scatter, Bar, Surface, Heatmap
- **Advanced Rendering**: Anti-aliasing, high-DPI support
- **Export Formats**: PNG, SVG, PDF with configurable quality
- **Real-time Updates**: Live data streaming capabilities

### **🔧 Enterprise Architecture**
- **Modern C++17**: Smart pointers, RAII, type safety
- **Cross-Platform**: Linux, Windows, macOS support
- **CMake Integration**: Standard build system support
- **Package Managers**: vcpkg, Conan compatibility

---

## 📊 **Chart Types & Examples**

### **LineChart - Time Series Analysis**
```cpp
#include <vizly/LineChart.h>

// Create high-performance line chart
vizly::ChartConfig config;
config.enable_gpu = true;
config.width = 1200;
config.height = 800;

auto chart = vizly::CreateLineChart(config);

// Financial time series example
std::vector<double> timestamps, prices, volumes;
LoadFinancialData(timestamps, prices, volumes); // Your data loading

// Plot multiple series
vizly::LineSeriesData price_series;
price_series.x = timestamps;
price_series.y = prices;
price_series.color = vizly::Color::FromHex("#2E86AB");
price_series.line_width = 2.0;
price_series.label = "Price";

vizly::LineSeriesData volume_series;
volume_series.x = timestamps;
volume_series.y = volumes;
volume_series.color = vizly::Color::FromHex("#A23B72");
volume_series.line_width = 1.5;
volume_series.label = "Volume";

chart->PlotMultiple({price_series, volume_series});

// Add technical indicators
chart->AddTrendLine(timestamps, prices, "exponential",
                   vizly::Color::FromName("orange"));

// Configure and save
chart->SetTitle("Financial Analysis - Real-time Data");
chart->SetLimits(timestamps.front(), timestamps.back(),
                *std::min_element(prices.begin(), prices.end()),
                *std::max_element(prices.begin(), prices.end()));
chart->Save("financial_analysis.png");
```

### **ScatterChart - Scientific Data**
```cpp
#include <vizly/ScatterChart.h>

// Large dataset scatter plot
auto scatter = vizly::CreateScatterChart(config);

// Generate scientific dataset
const int num_points = 1000000; // 1 million points
std::vector<double> x_data(num_points), y_data(num_points);

std::random_device rd;
std::mt19937 gen(rd());
std::normal_distribution<> d(0, 1);

for (int i = 0; i < num_points; ++i) {
    x_data[i] = d(gen);
    y_data[i] = 2 * x_data[i] + d(gen) * 0.5; // Linear relationship with noise
}

// GPU-accelerated rendering
scatter->Plot(x_data, y_data, vizly::Color::FromName("red"), 3.0, "Experimental Data");
scatter->SetTitle("Large-Scale Scientific Analysis (1M Points)");
scatter->SetAxisLabels("Independent Variable", "Dependent Variable");

// Performance measurement
auto start = std::chrono::high_resolution_clock::now();
scatter->Save("scientific_scatter.png");
auto end = std::chrono::high_resolution_clock::now();

auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
std::cout << "GPU rendering completed in " << duration.count() << "ms" << std::endl;
```

### **SurfaceChart - 3D Visualization**
```cpp
#include <vizly/SurfaceChart.h>

// 3D mathematical surface
auto surface = vizly::CreateSurfaceChart(config);

// Create mesh grid
int resolution = 50;
std::vector<std::vector<double>> X(resolution, std::vector<double>(resolution));
std::vector<std::vector<double>> Y(resolution, std::vector<double>(resolution));
std::vector<std::vector<double>> Z(resolution, std::vector<double>(resolution));

for (int i = 0; i < resolution; ++i) {
    for (int j = 0; j < resolution; ++j) {
        double x = -3.0 + (6.0 * i) / (resolution - 1);
        double y = -3.0 + (6.0 * j) / (resolution - 1);

        X[i][j] = x;
        Y[i][j] = y;
        Z[i][j] = std::sin(std::sqrt(x*x + y*y)) * std::exp(-std::sqrt(x*x + y*y)/3);
    }
}

// Create surface data
vizly::SurfaceData surf_data;
surf_data.x = X;
surf_data.y = Y;
surf_data.z = Z;
surf_data.colormap = "plasma";

surface->PlotSurface(surf_data);
surface->SetTitle("3D Mathematical Function");

// Enable VR if available
if (vizly::IsVrAvailable()) {
    vizly::VrConfig vr_config;
    vr_config.enable_hand_tracking = true;
    surface->EnableVr(vr_config);
    std::cout << "VR mode enabled - put on your headset!" << std::endl;
}

surface->Save("3d_surface.png");
```

---

## 🚀 **Advanced Features**

### **GPU Acceleration**
```cpp
#include <vizly/GPU.h>

// Check GPU capabilities
auto gpu_info = vizly::GetGpuInfo();
std::cout << "GPU Backend: " << gpu_info.backend_name << std::endl;
std::cout << "Memory: " << gpu_info.total_memory_mb << " MB" << std::endl;
std::cout << "Compute Units: " << gpu_info.compute_units << std::endl;

// Configure GPU processing
vizly::GpuConfig gpu_config;
gpu_config.backend = vizly::GpuConfig::Backend::AUTO; // or CUDA/OPENCL
gpu_config.device_id = 0;
gpu_config.enable_profiling = true;

// Create GPU-accelerated chart
vizly::ChartConfig config;
config.enable_gpu = true;
config.gpu_config = gpu_config;

auto chart = vizly::CreateLineChart(config);

// Process massive dataset
const int dataset_size = 10000000; // 10 million points
std::vector<double> large_x(dataset_size), large_y(dataset_size);

// Fill with data...
GenerateLargeDataset(large_x, large_y);

// GPU-accelerated plotting
auto start = std::chrono::high_resolution_clock::now();
chart->Plot(large_x, large_y, vizly::Color::FromName("blue"));
auto end = std::chrono::high_resolution_clock::now();

auto gpu_time = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
std::cout << "GPU processing time: " << gpu_time.count() << "ms" << std::endl;
```

### **Real-time Streaming**
```cpp
#include <vizly/Streaming.h>

class DataStreamHandler {
public:
    DataStreamHandler() {
        // Configure streaming
        vizly::StreamingConfig stream_config;
        stream_config.buffer_size = 1000;
        stream_config.update_interval = 0.016; // 60 FPS

        chart_ = vizly::CreateLineChart(config);
        chart_->EnableStreaming(stream_config);
    }

    void OnNewData(const std::vector<double>& timestamps,
                   const std::vector<double>& values) {
        // Update chart with new data
        chart_->UpdateStreamingData(timestamps, values);

        // Optional: Save snapshot
        if (timestamps.size() % 1000 == 0) {
            std::string filename = "snapshot_" +
                std::to_string(timestamps.size()) + ".png";
            chart_->Save(filename);
        }
    }

private:
    std::unique_ptr<vizly::LineChart> chart_;
    vizly::ChartConfig config;
};

// Usage with real-time data source
DataStreamHandler handler;

// Simulate real-time data
std::thread data_thread([&handler]() {
    std::vector<double> timestamps, values;

    for (int i = 0; i < 10000; ++i) {
        timestamps.push_back(i * 0.1);
        values.push_back(std::sin(i * 0.1) + RandomNoise());

        if (i % 10 == 0) { // Update every 10 points
            handler.OnNewData(timestamps, values);
            std::this_thread::sleep_for(std::chrono::milliseconds(16)); // 60 FPS
        }
    }
});

data_thread.join();
```

### **Memory Management**
```cpp
#include <vizly/Memory.h>

// RAII-based resource management
class ChartProcessor {
public:
    ChartProcessor(const vizly::ChartConfig& config)
        : config_(config) {
        // Resources automatically managed
    }

    void ProcessDatasets(const std::vector<Dataset>& datasets) {
        for (const auto& dataset : datasets) {
            // Smart pointer automatically manages lifetime
            auto chart = vizly::CreateLineChart(config_);

            chart->Plot(dataset.x, dataset.y);
            chart->Save(dataset.output_filename);

            // Chart automatically destroyed when out of scope
        }
    }

    // Custom memory pool for high-frequency operations
    void ProcessWithMemoryPool() {
        vizly::MemoryPool pool(1024 * 1024 * 100); // 100MB pool

        auto chart = vizly::CreateLineChart(config_, &pool);

        // All allocations use the memory pool
        // Pool automatically cleaned up when destroyed
    }

private:
    vizly::ChartConfig config_;
};
```

---

## 🛠️ **Build System Integration**

### **CMake Configuration**
```cmake
# Modern CMake setup
cmake_minimum_required(VERSION 3.16)
project(VizlyApp VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Vizly REQUIRED)
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# Create executable
add_executable(vizly_app
    src/main.cpp
    src/data_processor.cpp
    src/chart_generator.cpp
)

# Link libraries
target_link_libraries(vizly_app
    PRIVATE
    Vizly::vizly
    Python::Python
)

# Set properties
set_target_properties(vizly_app PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
)

# Install targets
install(TARGETS vizly_app
    RUNTIME DESTINATION bin
)
```

### **vcpkg Integration**
```json
// vcpkg.json
{
    "name": "my-vizly-app",
    "version": "1.0.0",
    "dependencies": [
        "vizly",
        "python3"
    ],
    "features": {
        "gpu": {
            "description": "GPU acceleration support",
            "dependencies": [
                "cuda",
                "opencl"
            ]
        },
        "vr": {
            "description": "VR/AR visualization support",
            "dependencies": [
                "openvr",
                "openxr"
            ]
        }
    }
}
```

### **Conan Integration**
```python
# conanfile.py
from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout

class VizlyAppConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires("vizly/1.0.0@infinidatum/stable")
        self.requires("python/3.11.0")

    def build_requirements(self):
        self.tool_requires("cmake/3.25.0")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
```

---

## 📚 **API Reference**

### **Core Classes**
```cpp
namespace vizly {

// Base chart class
class VizlyChart {
public:
    virtual ~VizlyChart() = default;

    virtual void SetTitle(const std::string& title) = 0;
    virtual void SetAxisLabels(const std::string& x_label,
                              const std::string& y_label) = 0;
    virtual void ShowGrid(bool show = true) = 0;
    virtual void ShowLegend(bool show = true,
                           LegendConfig::Position pos = LegendConfig::TOP_RIGHT) = 0;
    virtual void Save(const std::string& filename,
                     const ExportConfig& config = ExportConfig{}) = 0;
    virtual void Export(const std::string& filename,
                       const ExportConfig& config) = 0;
};

// Line chart implementation
class LineChart : public VizlyChart {
public:
    explicit LineChart(const ChartConfig& config = ChartConfig{});

    void Plot(const std::vector<double>& x, const std::vector<double>& y,
              const Color& color = Color::FromName("blue"),
              double line_width = 2.0, const std::string& label = "",
              const std::string& line_style = "solid");

    void PlotMultiple(const std::vector<LineSeriesData>& series);

    void AddTrendLine(const std::vector<double>& x, const std::vector<double>& y,
                      const std::string& type = "linear",
                      const Color& color = Color::FromName("red"),
                      int order = 2);

    bool EnableStreaming(const StreamingConfig& config = StreamingConfig{});
    void UpdateStreamingData(const std::vector<double>& x,
                            const std::vector<double>& y,
                            size_t series_index = 0);
};

// Factory functions
std::unique_ptr<LineChart> CreateLineChart(const ChartConfig& config = ChartConfig{});
std::unique_ptr<ScatterChart> CreateScatterChart(const ChartConfig& config = ChartConfig{});
std::unique_ptr<BarChart> CreateBarChart(const ChartConfig& config = ChartConfig{});
std::unique_ptr<SurfaceChart> CreateSurfaceChart(const ChartConfig& config = ChartConfig{});
std::unique_ptr<HeatmapChart> CreateHeatmapChart(const ChartConfig& config = ChartConfig{});

} // namespace vizly
```

### **Configuration Structures**
```cpp
struct ChartConfig {
    int width = 800;
    int height = 600;
    std::string background_color = "white";
    bool enable_gpu = false;
    bool enable_vr = false;
    bool enable_streaming = false;
    std::string theme = "default";
    int dpi = 300;

    GpuConfig gpu_config;
    VrConfig vr_config;
    StreamingConfig streaming_config;
};

struct Color {
    double r, g, b, a = 1.0;

    static Color FromName(const std::string& name);
    static Color FromHex(const std::string& hex);
    std::string ToHex() const;
};
```

---

## 🔧 **Performance Optimization**

### **Best Practices**
```cpp
// 1. Use GPU acceleration for large datasets
vizly::ChartConfig config;
config.enable_gpu = vizly::IsGpuAvailable();

// 2. Pre-allocate vectors for better performance
std::vector<double> x, y;
x.reserve(expected_size);
y.reserve(expected_size);

// 3. Use move semantics for large data
auto chart = vizly::CreateLineChart(config);
chart->Plot(std::move(x), std::move(y)); // Avoid copying

// 4. Memory pools for high-frequency operations
vizly::MemoryPool pool(desired_size);
auto chart = vizly::CreateLineChart(config, &pool);

// 5. Batch operations when possible
std::vector<LineSeriesData> series;
// ... populate series
chart->PlotMultiple(series); // More efficient than individual plots
```

### **Memory Profiling**
```cpp
#include <vizly/Profiler.h>

// Enable memory profiling
vizly::MemoryProfiler profiler;
profiler.Start();

{
    auto chart = vizly::CreateLineChart(config);
    chart->Plot(large_x, large_y);
    chart->Save("output.png");
}

auto stats = profiler.GetStats();
std::cout << "Peak memory usage: " << stats.peak_memory_mb << " MB" << std::endl;
std::cout << "Total allocations: " << stats.total_allocations << std::endl;
```

---

## 🧪 **Testing & Validation**

### **Unit Testing with Google Test**
```cpp
#include <gtest/gtest.h>
#include <vizly/Vizly.h>

class VizlyTest : public ::testing::Test {
protected:
    void SetUp() override {
        ASSERT_TRUE(vizly::Initialize());
    }

    void TearDown() override {
        vizly::Shutdown();
    }

    vizly::ChartConfig config_;
};

TEST_F(VizlyTest, LineChart_BasicPlot_Success) {
    auto chart = vizly::CreateLineChart(config_);
    ASSERT_NE(chart, nullptr);

    std::vector<double> x = {1, 2, 3, 4, 5};
    std::vector<double> y = {2, 4, 6, 8, 10};

    EXPECT_NO_THROW(chart->Plot(x, y));

    // Test dimensions
    auto dims = chart->GetDimensions();
    EXPECT_EQ(dims.first, config_.width);
    EXPECT_EQ(dims.second, config_.height);
}

TEST_F(VizlyTest, GPU_Acceleration_PerformanceTest) {
    if (!vizly::IsGpuAvailable()) {
        GTEST_SKIP() << "GPU not available";
    }

    // Large dataset test
    const int size = 100000;
    std::vector<double> x(size), y(size);
    std::iota(x.begin(), x.end(), 0);
    std::transform(x.begin(), x.end(), y.begin(),
                   [](double val) { return std::sin(val / 1000.0); });

    // CPU rendering
    config_.enable_gpu = false;
    auto cpu_chart = vizly::CreateLineChart(config_);
    auto cpu_start = std::chrono::high_resolution_clock::now();
    cpu_chart->Plot(x, y);
    auto cpu_end = std::chrono::high_resolution_clock::now();

    // GPU rendering
    config_.enable_gpu = true;
    auto gpu_chart = vizly::CreateLineChart(config_);
    auto gpu_start = std::chrono::high_resolution_clock::now();
    gpu_chart->Plot(x, y);
    auto gpu_end = std::chrono::high_resolution_clock::now();

    auto cpu_duration = std::chrono::duration_cast<std::chrono::milliseconds>(cpu_end - cpu_start);
    auto gpu_duration = std::chrono::duration_cast<std::chrono::milliseconds>(gpu_end - gpu_start);

    // GPU should be faster for large datasets
    EXPECT_LT(gpu_duration.count(), cpu_duration.count());

    std::cout << "CPU: " << cpu_duration.count() << "ms, "
              << "GPU: " << gpu_duration.count() << "ms" << std::endl;
}
```

---

## 💼 **Enterprise Features**

### **Commercial Licensing**
- **Professional Support**: C++ expertise and optimization consulting
- **Enterprise Support**: 24/7 support with guaranteed response times
- **Custom Development**: Native C++ extensions and optimizations
- **Performance Consulting**: Application-specific optimization services

### **High-Performance Computing**
- **HPC Integration**: MPI, OpenMP compatibility
- **Cluster Computing**: Distributed rendering capabilities
- **Scientific Computing**: Integration with numerical libraries
- **Real-time Systems**: Low-latency, deterministic performance

### **Security & Deployment**
- **Static Linking**: Self-contained executable deployment
- **Code Signing**: Secure binary distribution
- **Memory Safety**: Comprehensive bounds checking
- **Audit Trail**: Operation logging and monitoring

---

## 📞 **Support & Resources**

### **Documentation**
- **API Reference**: Complete C++ API documentation
- **Examples**: Comprehensive example collection
- **Performance Guide**: Optimization best practices
- **Integration Guide**: CMake, vcpkg, Conan setup

### **Community & Support**
- **Email**: durai@infinidatum.net
- **Subject Line**: "C++ SDK Support Request"
- **Include**: Compiler version, OS, build configuration, issue description

### **Professional Services**
- **Performance Optimization**: Custom optimization for your use case
- **Architecture Review**: Code review and optimization recommendations
- **Training**: C++ SDK mastery training program
- **Integration**: End-to-end deployment assistance

---

## 🚀 **Getting Started Checklist**

- [ ] Install C++ compiler (GCC 9+, Clang 10+, MSVC 2019+)
- [ ] Install CMake 3.16 or later
- [ ] Install Python 3.8+ with development headers
- [ ] Install Vizly SDK via vcpkg or from source
- [ ] Compile and run basic example
- [ ] Test GPU acceleration (if available)
- [ ] Explore advanced features (VR, streaming)
- [ ] Contact for enterprise licensing if needed

### **Next Steps**
1. **Evaluate**: Test with your C++ application requirements
2. **Integrate**: Add to your build system and CI/CD pipeline
3. **Optimize**: Implement performance best practices
4. **Scale**: Deploy to production HPC environments
5. **Support**: Contact for enterprise features and consulting

---

**⚡ Unleash maximum visualization performance with native C++ power.**

**Contact durai@infinidatum.net for enterprise licensing and high-performance consulting.**

---

*© 2024 Infinidatum Corporation. All rights reserved. Commercial license required for enterprise use.*