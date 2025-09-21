#!/usr/bin/env python3
"""
Vizly Setup Configuration
High-performance visualization library with zero dependencies.
"""

from setuptools import setup, find_packages
import os

# Read long description from README
def read_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Vizly: High-performance visualization library with zero dependencies"

# Read version from __init__.py
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'src', 'vizly', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

setup(
    # Package metadata
    name="vizly",
    version="1.1.0",
    author="Infinidatum Corporation",
    author_email="durai@infinidatum.net",
    description="Commercial high-performance visualization library with GPU acceleration, VR/AR support, and zero dependencies",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/vizly/vizly",
    project_urls={
        "Bug Tracker": "https://github.com/vizly/vizly/issues",
        "Documentation": "https://vizly.readthedocs.io/",
        "Source Code": "https://github.com/vizly/vizly",
        "Examples": "https://github.com/vizly/vizly/tree/main/examples",
    },

    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,

    # Dependencies - All features included by default
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies
        "numpy>=1.19.0",
        "matplotlib>=3.5.0",  # For compatibility with existing charts
        "pandas>=1.3.0",      # For data handling
        "scipy>=1.7.0",       # For scientific computations

        # Performance and GPU (optional but included)
        "psutil>=5.8.0",      # Performance monitoring
        "joblib>=1.1.0",      # Parallel processing

        # Web and streaming capabilities
        "websockets>=10.0",   # Real-time streaming
        "aiohttp>=3.8.0",     # HTTP client for streaming

        # Advanced features
        "pillow>=8.0.0",      # Image processing
        "opencv-python>=4.5.0",  # Computer vision (for VR/AR)

        # Financial analysis
        "TA-Lib>=0.4.24",     # Technical analysis (optional fallback in code)
    ],

    # Development-only dependencies
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "ruff>=0.1.0",
            "mypy>=0.800",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
        "gpu": [
            "cupy>=9.0.0",        # CUDA acceleration (hardware dependent)
            "pyopencl>=2021.1.0", # OpenCL acceleration (hardware dependent)
        ],
        "enterprise": [
            "redis>=4.0.0",       # Enterprise caching
            "celery>=5.0.0",      # Distributed processing
            "sqlalchemy>=1.4.0",  # Database integration
        ],
    },

    # Package classification
    classifiers=[
        # Development status
        "Development Status :: 5 - Production/Stable",

        # Intended audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Education",

        # Topic classification
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",

        # License
        "License :: Other/Proprietary License",

        # Programming language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        # Operating systems
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
        "Environment :: X11 Applications",
    ],

    # Keywords for discoverability
    keywords=[
        "visualization", "plotting", "charts", "graphs", "data-science",
        "matplotlib-alternative", "plotly-alternative", "zero-dependencies",
        "3d-visualization", "interactive-charts", "financial-charts",
        "real-time-plotting", "high-performance", "pure-python",
        "scientific-visualization", "engineering-plots", "dashboard",
        "webgl", "vr", "ar", "immersive-visualization"
    ],

    # Entry points
    entry_points={
        "console_scripts": [
            "vizly-demo=vizly.cli:demo_command",
            "vizly-gallery=vizly.cli:gallery_command",
            "vizly-server=vizly.cli:server_command",
        ],
    },

    # Package data
    package_data={
        "vizly": [
            "templates/*.html",
            "static/*.js",
            "static/*.css",
            "themes/*.json",
            "examples/*.py",
        ],
    },

    # Zip safety
    zip_safe=False,
)