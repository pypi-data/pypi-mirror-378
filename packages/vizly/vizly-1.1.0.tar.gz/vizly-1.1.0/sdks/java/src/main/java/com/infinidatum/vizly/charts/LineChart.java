/*
 * Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
 * Commercial License - Contact durai@infinidatum.net
 */

package com.infinidatum.vizly.charts;

import com.infinidatum.vizly.core.VizlyEngine;
import com.infinidatum.vizly.exceptions.VizlyException;
import com.infinidatum.vizly.types.ChartConfig;
import com.infinidatum.vizly.types.Color;
import com.infinidatum.vizly.types.LineSeriesData;

import jep.Jep;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;

/**
 * Line chart implementation for Vizly Java SDK
 *
 * @author Infinidatum Corporation
 * @version 1.0.0
 * @since 1.0.0
 */
public class LineChart extends VizlyChart {

    private static final Logger logger = LoggerFactory.getLogger(LineChart.class);
    private int seriesCount = 0;

    /**
     * Constructor with configuration
     *
     * @param config Chart configuration
     * @throws VizlyException if chart creation fails
     */
    public LineChart(ChartConfig config) throws VizlyException {
        super(config);
        createChart();
    }

    /**
     * Constructor with default configuration
     *
     * @throws VizlyException if chart creation fails
     */
    public LineChart() throws VizlyException {
        this(new ChartConfig());
    }

    /**
     * Create the Python chart object
     */
    @Override
    protected void createChart() throws VizlyException {
        try {
            Jep jep = engine.getJep();

            // Create chart with configuration
            String chartVar = "chart_" + chartId;
            String createCommand = String.format(
                "%s = vizly.LineChart(width=%d, height=%d, background_color='%s')",
                chartVar, config.getWidth(), config.getHeight(), config.getBackgroundColor()
            );

            jep.eval(createCommand);

            // Enable GPU if requested and available
            if (config.isEnableGpu() && engine.isGpuAvailable()) {
                jep.eval(chartVar + ".set_backend('gpu')");
                logger.info("🚀 GPU acceleration enabled for LineChart");
            }

            // Enable VR if requested and available
            if (config.isEnableVr() && engine.isVrAvailable()) {
                jep.eval(chartVar + ".set_vr_mode(True)");
                logger.info("🥽 VR mode enabled for LineChart");
            }

            this.chartVariable = chartVar;
            logger.debug("📈 LineChart created: {}x{}", config.getWidth(), config.getHeight());

        } catch (Exception e) {
            throw new VizlyException("Failed to create LineChart: " + e.getMessage(), e);
        }
    }

    /**
     * Plot line data
     *
     * @param x X coordinates
     * @param y Y coordinates
     * @param color Line color
     * @param lineWidth Line width
     * @param label Series label
     * @throws VizlyException if plotting fails
     */
    public void plot(double[] x, double[] y, Color color, double lineWidth, String label)
            throws VizlyException {
        validateArrays(x, y);

        try {
            Jep jep = engine.getJep();

            // Set arrays as Python variables
            String xVar = "x_data_" + chartId + "_" + seriesCount;
            String yVar = "y_data_" + chartId + "_" + seriesCount;

            jep.set(xVar, x);
            jep.set(yVar, y);

            // Convert to numpy arrays
            jep.eval(xVar + " = np.array(" + xVar + ")");
            jep.eval(yVar + " = np.array(" + yVar + ")");

            // Plot command
            String plotCommand = String.format(
                "%s.plot(%s, %s, color='%s', linewidth=%.2f, label='%s')",
                chartVariable, xVar, yVar, color.toHex(), lineWidth, label
            );

            jep.eval(plotCommand);
            seriesCount++;

            logger.debug("📊 Plotted line series: {} points, color: {}, label: '{}'",
                        x.length, color.toHex(), label);

        } catch (Exception e) {
            throw new VizlyException("Failed to plot line data: " + e.getMessage(), e);
        }
    }

    /**
     * Plot line data with default styling
     *
     * @param x X coordinates
     * @param y Y coordinates
     * @throws VizlyException if plotting fails
     */
    public void plot(double[] x, double[] y) throws VizlyException {
        plot(x, y, Color.BLUE, 2.0, "");
    }

    /**
     * Plot line data with color
     *
     * @param x X coordinates
     * @param y Y coordinates
     * @param color Line color
     * @throws VizlyException if plotting fails
     */
    public void plot(double[] x, double[] y, Color color) throws VizlyException {
        plot(x, y, color, 2.0, "");
    }

    /**
     * Plot multiple series
     *
     * @param seriesData List of line series data
     * @throws VizlyException if plotting fails
     */
    public void plotMultiple(List<LineSeriesData> seriesData) throws VizlyException {
        for (LineSeriesData series : seriesData) {
            plot(series.getX(), series.getY(), series.getColor(),
                 series.getLineWidth(), series.getLabel());
        }
        logger.info("📊 Plotted {} line series", seriesData.size());
    }

    /**
     * Add trend line
     *
     * @param x X coordinates
     * @param y Y coordinates
     * @param type Trend type ("linear", "polynomial", "exponential")
     * @param color Trend line color
     * @throws VizlyException if adding trend line fails
     */
    public void addTrendLine(double[] x, double[] y, String type, Color color)
            throws VizlyException {
        validateArrays(x, y);

        try {
            Jep jep = engine.getJep();

            String xVar = "trend_x_" + chartId;
            String yVar = "trend_y_" + chartId;

            jep.set(xVar, x);
            jep.set(yVar, y);
            jep.eval(xVar + " = np.array(" + xVar + ")");
            jep.eval(yVar + " = np.array(" + yVar + ")");

            String trendCommand = String.format(
                "%s.add_trendline(%s, %s, '%s', color='%s')",
                chartVariable, xVar, yVar, type, color.toHex()
            );

            jep.eval(trendCommand);
            logger.debug("📈 Added {} trend line", type);

        } catch (Exception e) {
            throw new VizlyException("Failed to add trend line: " + e.getMessage(), e);
        }
    }

    /**
     * Add vertical line
     *
     * @param x X position
     * @param color Line color
     * @param lineWidth Line width
     * @param label Line label
     * @throws VizlyException if adding line fails
     */
    public void addVerticalLine(double x, Color color, double lineWidth, String label)
            throws VizlyException {
        try {
            Jep jep = engine.getJep();

            String command = String.format(
                "%s.axvline(%.6f, color='%s', linewidth=%.2f, label='%s')",
                chartVariable, x, color.toHex(), lineWidth, label
            );

            jep.eval(command);
            logger.debug("📏 Added vertical line at x={}", x);

        } catch (Exception e) {
            throw new VizlyException("Failed to add vertical line: " + e.getMessage(), e);
        }
    }

    /**
     * Add horizontal line
     *
     * @param y Y position
     * @param color Line color
     * @param lineWidth Line width
     * @param label Line label
     * @throws VizlyException if adding line fails
     */
    public void addHorizontalLine(double y, Color color, double lineWidth, String label)
            throws VizlyException {
        try {
            Jep jep = engine.getJep();

            String command = String.format(
                "%s.axhline(%.6f, color='%s', linewidth=%.2f, label='%s')",
                chartVariable, y, color.toHex(), lineWidth, label
            );

            jep.eval(command);
            logger.debug("📏 Added horizontal line at y={}", y);

        } catch (Exception e) {
            throw new VizlyException("Failed to add horizontal line: " + e.getMessage(), e);
        }
    }

    /**
     * Set axis limits
     *
     * @param xMin Minimum X value
     * @param xMax Maximum X value
     * @param yMin Minimum Y value
     * @param yMax Maximum Y value
     * @throws VizlyException if setting limits fails
     */
    public void setLimits(double xMin, double xMax, double yMin, double yMax)
            throws VizlyException {
        try {
            Jep jep = engine.getJep();

            String command = String.format(
                "%s.set_xlim(%.6f, %.6f); %s.set_ylim(%.6f, %.6f)",
                chartVariable, xMin, xMax, chartVariable, yMin, yMax
            );

            jep.eval(command);
            logger.debug("🎯 Set limits: X=[{}, {}], Y=[{}, {}]", xMin, xMax, yMin, yMax);

        } catch (Exception e) {
            throw new VizlyException("Failed to set axis limits: " + e.getMessage(), e);
        }
    }

    /**
     * Set logarithmic scale
     *
     * @param xLog Use log scale for X axis
     * @param yLog Use log scale for Y axis
     * @throws VizlyException if setting scale fails
     */
    public void setLogScale(boolean xLog, boolean yLog) throws VizlyException {
        try {
            Jep jep = engine.getJep();

            if (xLog) {
                jep.eval(chartVariable + ".set_xscale('log')");
            }
            if (yLog) {
                jep.eval(chartVariable + ".set_yscale('log')");
            }

            logger.debug("📊 Set log scale: X={}, Y={}", xLog, yLog);

        } catch (Exception e) {
            throw new VizlyException("Failed to set log scale: " + e.getMessage(), e);
        }
    }

    /**
     * Add annotation
     *
     * @param x X position
     * @param y Y position
     * @param text Annotation text
     * @param color Text color
     * @throws VizlyException if adding annotation fails
     */
    public void addAnnotation(double x, double y, String text, Color color)
            throws VizlyException {
        try {
            Jep jep = engine.getJep();

            String command = String.format(
                "%s.annotate('%s', xy=(%.6f, %.6f), color='%s')",
                chartVariable, text.replace("'", "\\'"), x, y, color.toHex()
            );

            jep.eval(command);
            logger.debug("📝 Added annotation at ({}, {}): '{}'", x, y, text);

        } catch (Exception e) {
            throw new VizlyException("Failed to add annotation: " + e.getMessage(), e);
        }
    }

    /**
     * Save chart asynchronously
     *
     * @param filename Output filename
     * @return CompletableFuture for async operation
     */
    public CompletableFuture<Void> saveAsync(String filename) {
        return CompletableFuture.runAsync(() -> {
            try {
                save(filename);
            } catch (VizlyException e) {
                throw new RuntimeException(e);
            }
        });
    }

    /**
     * Get series count
     *
     * @return Number of plotted series
     */
    public int getSeriesCount() {
        return seriesCount;
    }

    /**
     * Validate input arrays
     */
    private void validateArrays(double[] x, double[] y) throws VizlyException {
        if (x == null || y == null) {
            throw new VizlyException("Input arrays cannot be null");
        }
        if (x.length != y.length) {
            throw new VizlyException("X and Y arrays must have the same length");
        }
        if (x.length == 0) {
            throw new VizlyException("Input arrays cannot be empty");
        }
    }
}