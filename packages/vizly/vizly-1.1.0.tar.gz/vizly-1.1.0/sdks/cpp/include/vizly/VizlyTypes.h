/**
 * @file VizlyTypes.h
 * @brief Type definitions for Vizly C++ SDK
 * @version 1.0.0
 * @author Infinidatum Corporation
 * @copyright Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
 * @license Commercial License - Contact durai@infinidatum.net
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>
#include <functional>

namespace vizly {

/**
 * @brief Chart configuration structure
 */
struct ChartConfig {
    int width = 800;                    ///< Chart width in pixels
    int height = 600;                   ///< Chart height in pixels
    std::string background_color = "white"; ///< Background color
    bool enable_gpu = false;            ///< Enable GPU acceleration
    bool enable_vr = false;             ///< Enable VR/AR features
    bool enable_streaming = false;      ///< Enable real-time streaming
    std::string theme = "default";      ///< Chart theme
    int dpi = 300;                      ///< DPI for exports
};

/**
 * @brief Engine configuration structure
 */
struct EngineConfig {
    std::string python_home = "";       ///< Python home directory
    std::string python_path = "";       ///< Python path
    bool verbose = false;               ///< Verbose logging
    std::string log_level = "INFO";     ///< Log level
};

/**
 * @brief System information structure
 */
struct SystemInfo {
    std::string version;                ///< Vizly version
    bool gpu_available;                 ///< GPU available
    bool vr_available;                  ///< VR/AR available
    bool streaming_available;           ///< Streaming available
    std::string platform;               ///< Platform name
    std::string python_version;         ///< Python version
};

/**
 * @brief Color structure
 */
struct Color {
    double r, g, b, a = 1.0;           ///< RGBA values (0.0-1.0)

    Color() : r(0), g(0), b(0), a(1.0) {}
    Color(double r, double g, double b, double a = 1.0) : r(r), g(g), b(b), a(a) {}

    /**
     * @brief Create color from hex string
     * @param hex Hex color string (e.g., "#FF0000")
     * @return Color object
     */
    static Color FromHex(const std::string& hex);

    /**
     * @brief Create color from name
     * @param name Color name (e.g., "red", "blue")
     * @return Color object
     */
    static Color FromName(const std::string& name);

    /**
     * @brief Convert to hex string
     * @return Hex color string
     */
    std::string ToHex() const;
};

/**
 * @brief Point structure for 2D coordinates
 */
struct Point2D {
    double x, y;
    Point2D() : x(0), y(0) {}
    Point2D(double x, double y) : x(x), y(y) {}
};

/**
 * @brief Point structure for 3D coordinates
 */
struct Point3D {
    double x, y, z;
    Point3D() : x(0), y(0), z(0) {}
    Point3D(double x, double y, double z) : x(x), y(y), z(z) {}
};

/**
 * @brief Data series for line charts
 */
struct LineSeriesData {
    std::vector<double> x;              ///< X coordinates
    std::vector<double> y;              ///< Y coordinates
    Color color = Color::FromName("blue"); ///< Line color
    double line_width = 2.0;            ///< Line width
    std::string label = "";             ///< Series label
    std::string line_style = "solid";   ///< Line style
};

/**
 * @brief Data series for scatter charts
 */
struct ScatterSeriesData {
    std::vector<double> x;              ///< X coordinates
    std::vector<double> y;              ///< Y coordinates
    Color color = Color::FromName("blue"); ///< Point color
    double point_size = 5.0;            ///< Point size
    std::string label = "";             ///< Series label
    std::string marker_style = "circle"; ///< Marker style
};

/**
 * @brief Data for bar charts
 */
struct BarData {
    std::vector<std::string> categories; ///< Category labels
    std::vector<double> values;         ///< Bar values
    std::vector<Color> colors;          ///< Bar colors (optional)
    std::string label = "";             ///< Data label
};

/**
 * @brief Surface data for 3D charts
 */
struct SurfaceData {
    std::vector<std::vector<double>> x; ///< X mesh grid
    std::vector<std::vector<double>> y; ///< Y mesh grid
    std::vector<std::vector<double>> z; ///< Z values
    std::string colormap = "viridis";   ///< Color map
};

/**
 * @brief Legend configuration
 */
struct LegendConfig {
    enum Position { TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT, CENTER };
    Position position = TOP_RIGHT;      ///< Legend position
    bool show_frame = true;             ///< Show legend frame
    Color background_color = Color(1, 1, 1, 0.8); ///< Background color
};

/**
 * @brief Grid configuration
 */
struct GridConfig {
    bool show_major = true;             ///< Show major grid
    bool show_minor = false;            ///< Show minor grid
    Color major_color = Color(0.8, 0.8, 0.8, 0.5); ///< Major grid color
    Color minor_color = Color(0.9, 0.9, 0.9, 0.3); ///< Minor grid color
    double major_width = 1.0;           ///< Major grid line width
    double minor_width = 0.5;           ///< Minor grid line width
};

/**
 * @brief Axis configuration
 */
struct AxisConfig {
    std::string label = "";             ///< Axis label
    bool show_ticks = true;             ///< Show tick marks
    bool show_labels = true;            ///< Show tick labels
    double min_value = 0.0;             ///< Minimum value (auto if 0)
    double max_value = 0.0;             ///< Maximum value (auto if 0)
    bool log_scale = false;             ///< Use logarithmic scale
};

/**
 * @brief Export configuration
 */
struct ExportConfig {
    enum Format { PNG, SVG, PDF, JPEG };
    Format format = PNG;                ///< Export format
    int dpi = 300;                      ///< DPI for raster formats
    bool transparent = false;           ///< Transparent background
    int quality = 95;                   ///< JPEG quality (1-100)
};

/**
 * @brief VR/AR configuration
 */
struct VrConfig {
    bool enable_hand_tracking = true;   ///< Enable hand tracking
    bool enable_spatial_anchoring = true; ///< Enable spatial anchoring
    double tracking_confidence = 0.8;   ///< Tracking confidence threshold
    std::vector<std::string> gestures = {"pinch", "grab", "point"}; ///< Enabled gestures
};

/**
 * @brief GPU configuration
 */
struct GpuConfig {
    enum Backend { AUTO, CUDA, OPENCL, CPU };
    Backend backend = AUTO;             ///< GPU backend
    int device_id = 0;                  ///< Device ID
    bool enable_profiling = false;      ///< Enable performance profiling
    size_t memory_limit = 0;            ///< Memory limit in MB (0 = auto)
};

/**
 * @brief Streaming configuration
 */
struct StreamingConfig {
    int buffer_size = 1000;             ///< Data buffer size
    double update_interval = 0.016;     ///< Update interval in seconds (60 FPS)
    bool enable_compression = true;     ///< Enable data compression
    std::string protocol = "websocket"; ///< Streaming protocol
};

/**
 * @brief Error callback type
 */
using ErrorCallback = std::function<void(const std::string& message)>;

/**
 * @brief Progress callback type
 */
using ProgressCallback = std::function<void(double progress)>;

} // namespace vizly