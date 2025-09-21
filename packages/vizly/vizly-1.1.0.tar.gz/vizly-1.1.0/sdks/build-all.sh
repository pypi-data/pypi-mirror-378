#!/bin/bash

# Vizly Multi-Language SDK Build Script
# Copyright (c) 2024 Infinidatum Corporation. All rights reserved.
# Commercial License - Contact durai@infinidatum.net

set -e  # Exit on any error

echo "🚀 Vizly Multi-Language SDK Build System"
echo "========================================"
echo "© 2024 Infinidatum Corporation"
echo "Commercial License - durai@infinidatum.net"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if script is run from correct directory
if [ ! -f "build-all.sh" ]; then
    print_error "Please run this script from the sdks directory"
    exit 1
fi

# Create build output directory
BUILD_DIR="build"
DIST_DIR="dist"
mkdir -p $BUILD_DIR
mkdir -p $DIST_DIR

print_status "Created build directories: $BUILD_DIR, $DIST_DIR"

# Check prerequisites
print_status "Checking prerequisites..."

# Check Python and Vizly
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

if ! python3 -c "import vizly" 2>/dev/null; then
    print_warning "Vizly not found. Installing from PyPI..."
    pip install vizly==1.0.0
    print_success "Vizly installed from PyPI"
fi

VIZLY_VERSION=$(python3 -c "import vizly; print(vizly.__version__)")
print_success "Vizly $VIZLY_VERSION available"

# Function to build C# SDK
build_csharp() {
    print_status "Building C# SDK..."

    if ! command -v dotnet &> /dev/null; then
        print_warning ".NET SDK not found - skipping C# build"
        return 1
    fi

    cd csharp

    print_status "Restoring NuGet packages..."
    dotnet restore

    print_status "Building C# SDK..."
    dotnet build --configuration Release

    print_status "Running C# tests..."
    if [ -d "tests" ]; then
        dotnet test --configuration Release --no-build
    fi

    print_status "Packing NuGet package..."
    dotnet pack --configuration Release --output ../build/

    cd ..

    # Copy artifacts
    cp csharp/bin/Release/net6.0/*.dll $DIST_DIR/ 2>/dev/null || true
    cp build/*.nupkg $DIST_DIR/ 2>/dev/null || true

    print_success "C# SDK build completed"
    return 0
}

# Function to build C++ SDK
build_cpp() {
    print_status "Building C++ SDK..."

    if ! command -v cmake &> /dev/null; then
        print_warning "CMake not found - skipping C++ build"
        return 1
    fi

    cd cpp
    mkdir -p build
    cd build

    print_status "Configuring CMake..."
    cmake .. -DCMAKE_BUILD_TYPE=Release -DBUILD_EXAMPLES=ON -DBUILD_TESTS=ON

    print_status "Building C++ SDK..."
    cmake --build . --config Release

    print_status "Running C++ tests..."
    if [ -f "tests/test_vizly" ]; then
        ./tests/test_vizly
    fi

    print_status "Creating C++ package..."
    cmake --build . --target package

    cd ../..

    # Copy artifacts
    cp cpp/build/lib*.* $DIST_DIR/ 2>/dev/null || true
    cp cpp/build/*.tar.gz $DIST_DIR/ 2>/dev/null || true
    cp cpp/build/*.deb $DIST_DIR/ 2>/dev/null || true

    print_success "C++ SDK build completed"
    return 0
}

# Function to build Java SDK
build_java() {
    print_status "Building Java SDK..."

    if ! command -v mvn &> /dev/null && ! command -v gradle &> /dev/null; then
        print_warning "Maven/Gradle not found - skipping Java build"
        return 1
    fi

    cd java

    if [ -f "pom.xml" ]; then
        print_status "Using Maven build..."

        print_status "Compiling Java SDK..."
        mvn clean compile

        print_status "Running Java tests..."
        mvn test

        print_status "Packaging JAR..."
        mvn package

        # Copy artifacts
        cp target/*.jar ../$DIST_DIR/ 2>/dev/null || true

    elif [ -f "build.gradle" ]; then
        print_status "Using Gradle build..."

        ./gradlew clean build

        # Copy artifacts
        cp build/libs/*.jar ../$DIST_DIR/ 2>/dev/null || true
    fi

    cd ..

    print_success "Java SDK build completed"
    return 0
}

# Function to run examples
run_examples() {
    print_status "Running SDK examples..."

    # C# example
    if [ -f "csharp/examples/bin/Release/net6.0/examples.dll" ]; then
        print_status "Running C# example..."
        cd csharp/examples
        dotnet run --configuration Release || print_warning "C# example failed"
        cd ../..
    fi

    # C++ example
    if [ -f "cpp/build/examples/basic_example" ]; then
        print_status "Running C++ example..."
        cd cpp/build/examples
        ./basic_example || print_warning "C++ example failed"
        cd ../../..
    fi

    # Java example
    if [ -f "java/target/vizly-sdk-1.0.0.jar" ]; then
        print_status "Running Java example..."
        cd java
        mvn exec:java || print_warning "Java example failed"
        cd ..
    fi
}

# Function to create distribution package
create_distribution() {
    print_status "Creating distribution package..."

    # Create distribution info
    cat > $DIST_DIR/README.txt << EOF
Vizly Multi-Language SDKs - Distribution Package
===============================================

Version: 1.0.0
Date: $(date)
License: Commercial License - Contact durai@infinidatum.net

This package contains the compiled SDKs for:
- C# (.NET 6.0+)
- C++ (C++17)
- Java (Java 11+)

For installation and usage instructions, see:
https://pypi.org/project/vizly/

Enterprise support: durai@infinidatum.net

© 2024 Infinidatum Corporation. All rights reserved.
EOF

    # Create archive
    cd $DIST_DIR
    tar -czf vizly-sdks-1.0.0.tar.gz *
    cd ..

    print_success "Distribution package created: $DIST_DIR/vizly-sdks-1.0.0.tar.gz"
}

# Function to show build summary
show_summary() {
    print_status "Build Summary"
    echo "=============="

    echo ""
    echo "📦 Built Packages:"
    ls -la $DIST_DIR/

    echo ""
    echo "📊 Package Sizes:"
    du -h $DIST_DIR/*

    echo ""
    echo "🎯 Installation Instructions:"
    echo ""
    echo "C# (.NET):"
    echo "  dotnet add package Vizly.SDK"
    echo ""
    echo "C++:"
    echo "  # Extract and use CMake find_package(Vizly)"
    echo ""
    echo "Java:"
    echo "  # Add to Maven pom.xml:"
    echo "  # <dependency>"
    echo "  #   <groupId>com.infinidatum</groupId>"
    echo "  #   <artifactId>vizly-sdk</artifactId>"
    echo "  #   <version>1.0.0</version>"
    echo "  # </dependency>"
    echo ""
    echo "💼 Enterprise Features:"
    echo "  Contact durai@infinidatum.net for:"
    echo "  - GPU acceleration licensing"
    echo "  - VR/AR visualization capabilities"
    echo "  - Real-time streaming features"
    echo "  - Custom development services"
}

# Main build process
print_status "Starting multi-language SDK build process..."

# Build individual SDKs
CSHARP_SUCCESS=0
CPP_SUCCESS=0
JAVA_SUCCESS=0

if build_csharp; then
    CSHARP_SUCCESS=1
fi

if build_cpp; then
    CPP_SUCCESS=1
fi

if build_java; then
    JAVA_SUCCESS=1
fi

# Check if at least one SDK built successfully
TOTAL_SUCCESS=$((CSHARP_SUCCESS + CPP_SUCCESS + JAVA_SUCCESS))

if [ $TOTAL_SUCCESS -eq 0 ]; then
    print_error "All SDK builds failed. Please check dependencies."
    exit 1
fi

print_success "$TOTAL_SUCCESS out of 3 SDKs built successfully"

# Run examples if requested
if [ "$1" = "--with-examples" ]; then
    run_examples
fi

# Create distribution package
create_distribution

# Show summary
show_summary

print_success "🎉 Vizly Multi-Language SDK build completed!"
print_status "Ready for commercial distribution and enterprise deployment"

echo ""
echo "Next steps:"
echo "1. Test the SDKs in your target environments"
echo "2. Contact durai@infinidatum.net for enterprise licensing"
echo "3. Deploy to your package repositories"
echo ""
echo "Thank you for using Vizly! 🚀"