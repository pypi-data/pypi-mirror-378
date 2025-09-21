cmake_minimum_required(VERSION 3.16)
project(VizlySDK VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Project info
set(PROJECT_DESCRIPTION "Vizly Commercial Visualization SDK for C++")
set(PROJECT_AUTHOR "Infinidatum Corporation")
set(PROJECT_URL "https://pypi.org/project/vizly/")

# Compiler options
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# Source files
set(VIZLY_SOURCES
    src/VizlyChart.cpp
    src/LineChart.cpp
    src/ScatterChart.cpp
    src/BarChart.cpp
    src/SurfaceChart.cpp
    src/HeatmapChart.cpp
    src/VizlyEngine.cpp
    src/VizlyException.cpp
)

# Header files
set(VIZLY_HEADERS
    include/vizly/VizlyChart.h
    include/vizly/LineChart.h
    include/vizly/ScatterChart.h
    include/vizly/BarChart.h
    include/vizly/SurfaceChart.h
    include/vizly/HeatmapChart.h
    include/vizly/VizlyEngine.h
    include/vizly/VizlyException.h
    include/vizly/VizlyTypes.h
    include/vizly/Vizly.h
)

# Create static library
add_library(vizly_static STATIC ${VIZLY_SOURCES} ${VIZLY_HEADERS})
target_link_libraries(vizly_static PRIVATE pybind11::embed)
target_include_directories(vizly_static PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Create shared library
add_library(vizly_shared SHARED ${VIZLY_SOURCES} ${VIZLY_HEADERS})
target_link_libraries(vizly_shared PRIVATE pybind11::embed)
target_include_directories(vizly_shared PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# Set library properties
set_target_properties(vizly_static PROPERTIES
    OUTPUT_NAME vizly
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
)

set_target_properties(vizly_shared PROPERTIES
    OUTPUT_NAME vizly
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
)

# Examples
option(BUILD_EXAMPLES "Build example programs" ON)
if(BUILD_EXAMPLES)
    add_subdirectory(examples)
endif()

# Tests
option(BUILD_TESTS "Build test programs" ON)
if(BUILD_TESTS)
    add_subdirectory(tests)
endif()

# Installation
include(GNUInstallDirs)

install(TARGETS vizly_static vizly_shared
    EXPORT VizlyTargets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)

install(DIRECTORY include/vizly
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Export configuration
install(EXPORT VizlyTargets
    FILE VizlyTargets.cmake
    NAMESPACE Vizly::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Vizly
)

# Create config file
include(CMakePackageConfigHelpers)
configure_package_config_file(
    "cmake/VizlyConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/VizlyConfig.cmake"
    INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Vizly
)

write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/VizlyConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/VizlyConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/VizlyConfigVersion.cmake"
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Vizly
)

# Package configuration
set(CPACK_PACKAGE_NAME "VizlySDK")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY ${PROJECT_DESCRIPTION})
set(CPACK_PACKAGE_VENDOR ${PROJECT_AUTHOR})
set(CPACK_PACKAGE_CONTACT "durai@infinidatum.net")
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/LICENSE")
set(CPACK_RESOURCE_FILE_README "${CMAKE_CURRENT_SOURCE_DIR}/README.md")

include(CPack)