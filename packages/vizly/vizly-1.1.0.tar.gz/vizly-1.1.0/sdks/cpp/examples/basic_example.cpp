/**
 * @file basic_example.cpp
 * @brief Basic example for Vizly C++ SDK
 * @version 1.0.0
 * @author Infinidatum Corporation
 * @copyright Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
 * @license Commercial License - Contact durai@infinidatum.net
 */

#include <iostream>
#include <vector>
#include <cmath>
#include <vizly/Vizly.h>

int main() {
    std::cout << "🚀 Vizly C++ SDK Basic Example" << std::endl;
    std::cout << "================================" << std::endl;

    try {
        // Initialize Vizly engine
        vizly::EngineConfig engine_config;
        engine_config.verbose = true;

        if (!vizly::Initialize(engine_config)) {
            std::cerr << "❌ Failed to initialize Vizly engine" << std::endl;
            return 1;
        }

        // Get system information
        auto sys_info = vizly::GetSystemInfo();
        std::cout << "📊 Vizly Version: " << sys_info.version << std::endl;
        std::cout << "🖥️ Platform: " << sys_info.platform << std::endl;
        std::cout << "🚀 GPU Available: " << (sys_info.gpu_available ? "Yes" : "No") << std::endl;
        std::cout << "🥽 VR Available: " << (sys_info.vr_available ? "Yes" : "No") << std::endl;

        // Create line chart configuration
        vizly::ChartConfig config;
        config.width = 800;
        config.height = 600;
        config.background_color = "white";
        config.enable_gpu = vizly::IsGpuAvailable();

        // Create line chart
        auto chart = vizly::CreateLineChart(config);
        if (!chart) {
            std::cerr << "❌ Failed to create line chart" << std::endl;
            return 1;
        }

        std::cout << "📈 Creating sine wave data..." << std::endl;

        // Generate sine wave data
        std::vector<double> x, y;
        const int num_points = 100;
        const double pi = 3.14159265359;

        for (int i = 0; i < num_points; ++i) {
            double x_val = i * 2.0 * pi / num_points;
            x.push_back(x_val);
            y.push_back(std::sin(x_val));
        }

        // Plot the data
        chart->Plot(x, y, vizly::Color::FromName("blue"), 2.0, "sin(x)");

        // Set chart properties
        chart->SetTitle("Basic Sine Wave - Vizly C++ SDK");
        chart->SetAxisLabels("X (radians)", "Y");
        chart->ShowGrid(true);
        chart->ShowLegend(true);

        // Save the chart
        std::cout << "💾 Saving chart..." << std::endl;
        chart->Save("basic_sine_wave.png");

        std::cout << "✅ Chart saved as 'basic_sine_wave.png'" << std::endl;

        // Create multi-series example
        std::cout << "📊 Creating multi-series chart..." << std::endl;

        auto multi_chart = vizly::CreateLineChart(config);

        // Generate multiple series
        std::vector<double> cos_y, sin_2x;
        for (int i = 0; i < num_points; ++i) {
            double x_val = x[i];
            cos_y.push_back(std::cos(x_val));
            sin_2x.push_back(std::sin(2.0 * x_val));
        }

        // Plot multiple series
        multi_chart->Plot(x, y, vizly::Color::FromName("blue"), 2.0, "sin(x)");
        multi_chart->Plot(x, cos_y, vizly::Color::FromName("red"), 2.0, "cos(x)");
        multi_chart->Plot(x, sin_2x, vizly::Color::FromName("green"), 1.5, "sin(2x)");

        // Add trend line
        multi_chart->AddTrendLine(x, y, "polynomial", vizly::Color::FromName("orange"));

        // Set properties
        multi_chart->SetTitle("Multi-Series Chart - Trigonometric Functions");
        multi_chart->SetAxisLabels("X (radians)", "Y");
        multi_chart->ShowGrid(true);
        multi_chart->ShowLegend(true, vizly::LegendConfig::TOP_RIGHT);

        // Save multi-series chart
        multi_chart->Save("multi_series_chart.png");
        std::cout << "✅ Multi-series chart saved as 'multi_series_chart.png'" << std::endl;

        // Demonstrate advanced features
        if (sys_info.gpu_available) {
            std::cout << "🚀 Creating GPU-accelerated chart..." << std::endl;

            vizly::ChartConfig gpu_config = config;
            gpu_config.enable_gpu = true;
            gpu_config.width = 1200;
            gpu_config.height = 800;

            auto gpu_chart = vizly::CreateLineChart(gpu_config);

            // Large dataset for GPU demonstration
            std::vector<double> large_x, large_y;
            const int large_points = 10000;

            for (int i = 0; i < large_points; ++i) {
                double x_val = i * 10.0 / large_points;
                large_x.push_back(x_val);
                large_y.push_back(std::sin(x_val) + 0.1 * (rand() / double(RAND_MAX) - 0.5));
            }

            gpu_chart->Plot(large_x, large_y, vizly::Color::FromName("purple"), 1.0, "Noisy Signal");
            gpu_chart->SetTitle("GPU-Accelerated Rendering - 10K Points");
            gpu_chart->SetAxisLabels("Time", "Signal");
            gpu_chart->ShowGrid(true);

            gpu_chart->Save("gpu_accelerated_chart.png");
            std::cout << "✅ GPU-accelerated chart saved" << std::endl;
        }

        // Export as different formats
        std::cout << "📤 Exporting in different formats..." << std::endl;

        vizly::ExportConfig export_config;

        // Export as SVG
        export_config.format = vizly::ExportConfig::SVG;
        chart->Export("basic_chart.svg", export_config);

        // Export as high-DPI PNG
        export_config.format = vizly::ExportConfig::PNG;
        export_config.dpi = 600;
        chart->Export("basic_chart_hd.png", export_config);

        std::cout << "✅ Exported charts in multiple formats" << std::endl;

        // Performance benchmark
        std::cout << "⏱️ Running performance benchmark..." << std::endl;

        auto start = std::chrono::high_resolution_clock::now();

        auto bench_chart = vizly::CreateLineChart(config);
        bench_chart->Plot(large_x, large_y, vizly::Color::FromName("blue"));
        bench_chart->Save("benchmark_chart.png");

        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

        std::cout << "📊 Benchmark Results:" << std::endl;
        std::cout << "• Dataset size: " << large_x.size() << " points" << std::endl;
        std::cout << "• Rendering time: " << duration.count() << " ms" << std::endl;
        std::cout << "• Points per second: " << (large_x.size() * 1000 / duration.count()) << std::endl;

        std::cout << "\n🎉 All examples completed successfully!" << std::endl;
        std::cout << "💼 For enterprise licensing: durai@infinidatum.net" << std::endl;

    } catch (const vizly::VizlyException& e) {
        std::cerr << "❌ Vizly Error: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }

    // Shutdown Vizly engine
    vizly::Shutdown();

    return 0;
}