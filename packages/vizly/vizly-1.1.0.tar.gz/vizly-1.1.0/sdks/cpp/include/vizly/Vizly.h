/**
 * @file Vizly.h
 * @brief Main header file for Vizly C++ SDK
 * @version 1.0.0
 * @author Infinidatum Corporation
 * @copyright Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
 * @license Commercial License - Contact durai@infinidatum.net
 */

#pragma once

#include "VizlyTypes.h"
#include "VizlyException.h"
#include "VizlyEngine.h"
#include "VizlyChart.h"
#include "LineChart.h"
#include "ScatterChart.h"
#include "BarChart.h"
#include "SurfaceChart.h"
#include "HeatmapChart.h"

/**
 * @namespace vizly
 * @brief Main namespace for Vizly C++ SDK
 */
namespace vizly {

/**
 * @brief Get Vizly version
 * @return Version string
 */
std::string GetVersion();

/**
 * @brief Get system information
 * @return System info structure
 */
SystemInfo GetSystemInfo();

/**
 * @brief Check if GPU acceleration is available
 * @return True if GPU is available
 */
bool IsGpuAvailable();

/**
 * @brief Check if VR/AR features are available
 * @return True if VR/AR is available
 */
bool IsVrAvailable();

/**
 * @brief Check if streaming features are available
 * @return True if streaming is available
 */
bool IsStreamingAvailable();

/**
 * @brief Initialize Vizly engine
 * @param config Engine configuration
 * @return True if initialization successful
 */
bool Initialize(const EngineConfig& config = EngineConfig{});

/**
 * @brief Shutdown Vizly engine
 */
void Shutdown();

/**
 * @brief Create a line chart
 * @param config Chart configuration
 * @return Unique pointer to line chart
 */
std::unique_ptr<LineChart> CreateLineChart(const ChartConfig& config = ChartConfig{});

/**
 * @brief Create a scatter chart
 * @param config Chart configuration
 * @return Unique pointer to scatter chart
 */
std::unique_ptr<ScatterChart> CreateScatterChart(const ChartConfig& config = ChartConfig{});

/**
 * @brief Create a bar chart
 * @param config Chart configuration
 * @return Unique pointer to bar chart
 */
std::unique_ptr<BarChart> CreateBarChart(const ChartConfig& config = ChartConfig{});

/**
 * @brief Create a surface chart
 * @param config Chart configuration
 * @return Unique pointer to surface chart
 */
std::unique_ptr<SurfaceChart> CreateSurfaceChart(const ChartConfig& config = ChartConfig{});

/**
 * @brief Create a heatmap chart
 * @param config Chart configuration
 * @return Unique pointer to heatmap chart
 */
std::unique_ptr<HeatmapChart> CreateHeatmapChart(const ChartConfig& config = ChartConfig{});

} // namespace vizly