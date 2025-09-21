/**
 * @file LineChart.h
 * @brief Line chart class for Vizly C++ SDK
 * @version 1.0.0
 * @author Infinidatum Corporation
 * @copyright Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
 * @license Commercial License - Contact durai@infinidatum.net
 */

#pragma once

#include "VizlyChart.h"
#include "VizlyTypes.h"

namespace vizly {

/**
 * @brief Line chart implementation
 */
class LineChart : public VizlyChart {
public:
    /**
     * @brief Constructor
     * @param config Chart configuration
     */
    explicit LineChart(const ChartConfig& config = ChartConfig{});

    /**
     * @brief Destructor
     */
    virtual ~LineChart() = default;

    /**
     * @brief Plot line data
     * @param x X coordinates
     * @param y Y coordinates
     * @param color Line color
     * @param line_width Line width
     * @param label Series label
     * @param line_style Line style ("solid", "dashed", "dotted")
     */
    void Plot(const std::vector<double>& x,
              const std::vector<double>& y,
              const Color& color = Color::FromName("blue"),
              double line_width = 2.0,
              const std::string& label = "",
              const std::string& line_style = "solid");

    /**
     * @brief Plot multiple series
     * @param series Vector of line series data
     */
    void PlotMultiple(const std::vector<LineSeriesData>& series);

    /**
     * @brief Add trend line
     * @param x X coordinates
     * @param y Y coordinates
     * @param type Trend line type ("linear", "polynomial", "exponential")
     * @param color Trend line color
     * @param order Polynomial order (for polynomial trends)
     */
    void AddTrendLine(const std::vector<double>& x,
                      const std::vector<double>& y,
                      const std::string& type = "linear",
                      const Color& color = Color::FromName("red"),
                      int order = 2);

    /**
     * @brief Add error bars
     * @param x X coordinates
     * @param y Y coordinates
     * @param y_error Error values
     * @param color Error bar color
     */
    void AddErrorBars(const std::vector<double>& x,
                      const std::vector<double>& y,
                      const std::vector<double>& y_error,
                      const Color& color = Color::FromName("gray"));

    /**
     * @brief Add fill between curves
     * @param x X coordinates
     * @param y1 First Y curve
     * @param y2 Second Y curve
     * @param color Fill color
     * @param alpha Transparency (0.0-1.0)
     */
    void FillBetween(const std::vector<double>& x,
                     const std::vector<double>& y1,
                     const std::vector<double>& y2,
                     const Color& color = Color::FromName("blue"),
                     double alpha = 0.3);

    /**
     * @brief Add vertical line
     * @param x X position
     * @param color Line color
     * @param line_width Line width
     * @param label Line label
     */
    void AddVerticalLine(double x,
                        const Color& color = Color::FromName("black"),
                        double line_width = 1.0,
                        const std::string& label = "");

    /**
     * @brief Add horizontal line
     * @param y Y position
     * @param color Line color
     * @param line_width Line width
     * @param label Line label
     */
    void AddHorizontalLine(double y,
                          const Color& color = Color::FromName("black"),
                          double line_width = 1.0,
                          const std::string& label = "");

    /**
     * @brief Set X axis scale
     * @param scale Scale type ("linear", "log")
     */
    void SetXScale(const std::string& scale);

    /**
     * @brief Set Y axis scale
     * @param scale Scale type ("linear", "log")
     */
    void SetYScale(const std::string& scale);

    /**
     * @brief Set axis limits
     * @param x_min Minimum X value
     * @param x_max Maximum X value
     * @param y_min Minimum Y value
     * @param y_max Maximum Y value
     */
    void SetLimits(double x_min, double x_max, double y_min, double y_max);

    /**
     * @brief Enable real-time streaming
     * @param config Streaming configuration
     * @return True if streaming enabled successfully
     */
    bool EnableStreaming(const StreamingConfig& config = StreamingConfig{});

    /**
     * @brief Update streaming data
     * @param x New X data points
     * @param y New Y data points
     * @param series_index Series index to update (default: 0)
     */
    void UpdateStreamingData(const std::vector<double>& x,
                            const std::vector<double>& y,
                            size_t series_index = 0);

    /**
     * @brief Add annotation
     * @param x X position
     * @param y Y position
     * @param text Annotation text
     * @param color Text color
     */
    void AddAnnotation(double x, double y,
                      const std::string& text,
                      const Color& color = Color::FromName("black"));

private:
    std::vector<LineSeriesData> series_data_;
    bool streaming_enabled_ = false;
    StreamingConfig streaming_config_;
};

} // namespace vizly