/*
 * Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
 * Commercial License - Contact durai@infinidatum.net
 */

package com.infinidatum.vizly.examples;

import com.infinidatum.vizly.charts.LineChart;
import com.infinidatum.vizly.core.VizlyEngine;
import com.infinidatum.vizly.exceptions.VizlyException;
import com.infinidatum.vizly.types.*;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.List;
import java.util.Random;
import java.util.concurrent.CompletableFuture;
import java.util.stream.IntStream;

/**
 * Basic example application for Vizly Java SDK
 *
 * @author Infinidatum Corporation
 * @version 1.0.0
 * @since 1.0.0
 */
public class BasicExample {

    private static final Logger logger = LoggerFactory.getLogger(BasicExample.class);

    public static void main(String[] args) {
        logger.info("🚀 Vizly Java SDK Basic Example");
        logger.info("================================");

        try {
            // Initialize Vizly engine
            VizlyEngine engine = VizlyEngine.getInstance();
            EngineConfig engineConfig = new EngineConfig();
            engineConfig.setVerbose(true);

            engine.initialize(engineConfig);

            // Get system information
            SystemInfo sysInfo = engine.getSystemInfo();
            logger.info("📊 Vizly Version: {}", sysInfo.getVersion());
            logger.info("🖥️ Platform: {}", sysInfo.getPlatform());
            logger.info("🚀 GPU Available: {}", sysInfo.isGpuAvailable());
            logger.info("🥽 VR Available: {}", sysInfo.isVrAvailable());
            logger.info("📡 Streaming Available: {}", sysInfo.isStreamingAvailable());

            // Run examples
            createBasicLineChart();
            createMultiSeriesChart();
            demonstrateAdvancedFeatures(sysInfo);

            logger.info("✅ All examples completed successfully!");
            logger.info("💼 For enterprise licensing: durai@infinidatum.net");

        } catch (VizlyException e) {
            logger.error("❌ Vizly Error: {}", e.getMessage(), e);
        } catch (Exception e) {
            logger.error("❌ Unexpected error: {}", e.getMessage(), e);
        } finally {
            // Shutdown engine
            VizlyEngine.getInstance().shutdown();
        }
    }

    /**
     * Create a basic line chart
     */
    private static void createBasicLineChart() throws VizlyException {
        logger.info("📈 Creating Basic Line Chart...");

        ChartConfig config = new ChartConfig();
        config.setWidth(800);
        config.setHeight(600);
        config.setBackgroundColor("white");

        try (LineChart chart = new LineChart(config)) {
            // Generate sine wave data
            double[] x = IntStream.range(0, 100)
                    .mapToDouble(i -> i * Math.PI / 50.0)
                    .toArray();
            double[] y = Arrays.stream(x)
                    .map(Math::sin)
                    .toArray();

            // Plot the data
            chart.plot(x, y, Color.BLUE, 2.0, "sin(x)");
            chart.setTitle("Basic Sine Wave - Vizly Java SDK");
            chart.setAxisLabels("X (radians)", "Y");
            chart.showGrid(true);
            chart.showLegend(true);

            // Save the chart
            chart.save("java_basic_line_chart.png");
            logger.info("✅ Basic line chart saved as 'java_basic_line_chart.png'");
        }
    }

    /**
     * Create a multi-series chart
     */
    private static void createMultiSeriesChart() throws VizlyException {
        logger.info("📊 Creating Multi-Series Chart...");

        ChartConfig config = new ChartConfig();
        config.setWidth(1000);
        config.setHeight(600);
        config.setEnableGpu(VizlyEngine.getInstance().isGpuAvailable());

        try (LineChart chart = new LineChart(config)) {
            // Generate multiple series
            double[] x = IntStream.range(0, 200)
                    .mapToDouble(i -> i * Math.PI / 100.0)
                    .toArray();

            // Create series data
            LineSeriesData sinSeries = new LineSeriesData();
            sinSeries.setX(x);
            sinSeries.setY(Arrays.stream(x).map(Math::sin).toArray());
            sinSeries.setColor(Color.BLUE);
            sinSeries.setLineWidth(2.0);
            sinSeries.setLabel("sin(x)");

            LineSeriesData cosSeries = new LineSeriesData();
            cosSeries.setX(x);
            cosSeries.setY(Arrays.stream(x).map(Math::cos).toArray());
            cosSeries.setColor(Color.RED);
            cosSeries.setLineWidth(2.0);
            cosSeries.setLabel("cos(x)");

            LineSeriesData sin2Series = new LineSeriesData();
            sin2Series.setX(x);
            sin2Series.setY(Arrays.stream(x).map(v -> Math.sin(2 * v)).toArray());
            sin2Series.setColor(Color.GREEN);
            sin2Series.setLineWidth(1.5);
            sin2Series.setLabel("sin(2x)");

            // Plot multiple series
            chart.plotMultiple(Arrays.asList(sinSeries, cosSeries, sin2Series));

            // Add trend line
            chart.addTrendLine(x, sinSeries.getY(), "polynomial", Color.ORANGE);

            // Set properties
            chart.setTitle("Multi-Series Chart - Trigonometric Functions");
            chart.setAxisLabels("X (radians)", "Y");
            chart.showGrid(true);
            chart.showLegend(true);

            // Add annotations
            chart.addAnnotation(Math.PI, 0, "π", Color.BLACK);
            chart.addAnnotation(2 * Math.PI, 0, "2π", Color.BLACK);

            chart.save("java_multi_series_chart.png");
            logger.info("✅ Multi-series chart saved as 'java_multi_series_chart.png'");
        }
    }

    /**
     * Demonstrate advanced features
     */
    private static void demonstrateAdvancedFeatures(SystemInfo sysInfo) throws VizlyException {
        logger.info("🚀 Demonstrating Advanced Features...");

        // GPU acceleration demo
        if (sysInfo.isGpuAvailable()) {
            logger.info("🚀 Creating GPU-accelerated chart...");

            ChartConfig gpuConfig = new ChartConfig();
            gpuConfig.setWidth(1200);
            gpuConfig.setHeight(800);
            gpuConfig.setEnableGpu(true);

            try (LineChart gpuChart = new LineChart(gpuConfig)) {
                // Large dataset for GPU demonstration
                Random random = new Random(42);
                double[] largeX = IntStream.range(0, 10000)
                        .mapToDouble(i -> i / 1000.0)
                        .toArray();
                double[] largeY = Arrays.stream(largeX)
                        .map(x -> Math.sin(x) + 0.1 * random.nextGaussian())
                        .toArray();

                gpuChart.plot(largeX, largeY, Color.PURPLE, 1.0, "Noisy Signal");
                gpuChart.setTitle("GPU-Accelerated Rendering - 10K Points");
                gpuChart.setAxisLabels("Time", "Signal");
                gpuChart.showGrid(true);

                gpuChart.save("java_gpu_accelerated_chart.png");
                logger.info("✅ GPU-accelerated chart saved");
            }
        }

        // Asynchronous operations demo
        logger.info("⚡ Demonstrating async operations...");

        ChartConfig asyncConfig = new ChartConfig();
        asyncConfig.setWidth(600);
        asyncConfig.setHeight(400);

        try (LineChart asyncChart = new LineChart(asyncConfig)) {
            double[] x = IntStream.range(0, 50)
                    .mapToDouble(i -> i / 10.0)
                    .toArray();
            double[] y = Arrays.stream(x)
                    .map(v -> Math.exp(-v) * Math.cos(v))
                    .toArray();

            asyncChart.plot(x, y, Color.RED, 2.5, "Damped Oscillation");
            asyncChart.setTitle("Async Operations Example");

            // Save asynchronously
            CompletableFuture<Void> saveTask = asyncChart.saveAsync("java_async_chart.png");
            saveTask.join(); // Wait for completion

            logger.info("✅ Async chart saved");
        }

        // Performance benchmark
        logger.info("⏱️ Running performance benchmark...");

        long startTime = System.currentTimeMillis();

        ChartConfig benchConfig = new ChartConfig();
        try (LineChart benchChart = new LineChart(benchConfig)) {
            double[] benchX = IntStream.range(0, 5000)
                    .mapToDouble(i -> i / 1000.0)
                    .toArray();
            double[] benchY = Arrays.stream(benchX)
                    .map(Math::sin)
                    .toArray();

            benchChart.plot(benchX, benchY, Color.BLUE);
            benchChart.save("java_benchmark_chart.png");
        }

        long endTime = System.currentTimeMillis();
        long duration = endTime - startTime;

        logger.info("📊 Benchmark Results:");
        logger.info("• Dataset size: 5,000 points");
        logger.info("• Rendering time: {} ms", duration);
        logger.info("• Points per second: {}", (5000 * 1000 / duration));

        // Feature availability summary
        logger.info("\n🎯 Feature Availability Summary:");
        logger.info("• Version: {}", sysInfo.getVersion());
        logger.info("• GPU Acceleration: {}", sysInfo.isGpuAvailable() ? "✅ Available" : "📋 Enterprise Edition");
        logger.info("• VR/AR Visualization: {}", sysInfo.isVrAvailable() ? "✅ Available" : "📋 Enterprise Edition");
        logger.info("• Real-time Streaming: {}", sysInfo.isStreamingAvailable() ? "✅ Available" : "📋 Enterprise Edition");

        if (!sysInfo.isGpuAvailable() || !sysInfo.isVrAvailable() || !sysInfo.isStreamingAvailable()) {
            logger.info("\n💼 Enterprise Features:");
            logger.info("Contact durai@infinidatum.net for:");
            logger.info("• GPU acceleration licensing");
            logger.info("• VR/AR visualization capabilities");
            logger.info("• Real-time streaming features");
            logger.info("• Custom development services");
        }
    }
}