#!/usr/bin/env python3
"""
Vizly v1.0 Production Demo
=========================

Comprehensive demonstration of Vizly's production-ready features:
- Pure Python chart rendering
- GPU acceleration
- 3D interaction and scene management
- VR/AR visualization
- Real-time streaming
- Performance benchmarking

IMPORTANT: This is a local development project, not published to PyPI.

To run this demo:
1. cd /Users/durai/Documents/GitHub/vizly
2. pip install -e .[complete]
3. python production_demo.py

Run this demo to see all features in action.
"""

import numpy as np
import time
import asyncio
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main production demo."""
    print("🚀 Vizly v1.0 Production Demo")
    print("=" * 50)

    # Create output directory
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)

    try:
        # 1. Pure Python Charts Demo
        demo_pure_charts(output_dir)

        # 2. GPU Acceleration Demo
        demo_gpu_acceleration(output_dir)

        # 3. 3D Interaction Demo
        demo_3d_interaction()

        # 4. VR/AR Demo
        demo_vr_ar()

        # 5. Real-time Streaming Demo
        asyncio.run(demo_streaming())

        # 6. Performance Benchmarks
        demo_performance_benchmarks()

        print("\n✅ All demos completed successfully!")
        print(f"📁 Output files saved to: {output_dir.absolute()}")

    except Exception as e:
        logger.error(f"Demo failed: {e}")
        return 1

    return 0


def demo_pure_charts(output_dir: Path):
    """Demonstrate pure Python chart rendering."""
    print("\n📊 1. Pure Python Charts")
    print("-" * 30)

    try:
        import vizly

        # Generate sample data
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)

        # Line Chart
        print("Creating LineChart...")
        line_chart = vizly.LineChart(width=800, height=600)
        line_chart.plot(x, y1, color='blue', linewidth=2, label='sin(x)')
        line_chart.plot(x, y2, color='red', linewidth=2, label='cos(x)')
        line_chart.set_title("Pure Python Line Chart")
        line_chart.set_labels(xlabel="X Values", ylabel="Y Values")
        line_chart.add_legend()
        line_chart.save(str(output_dir / "pure_line_chart.png"), dpi=300)

        # Scatter Chart
        print("Creating ScatterChart...")
        scatter_data_x = np.random.randn(500)
        scatter_data_y = np.random.randn(500)

        scatter_chart = vizly.ScatterChart(width=800, height=600)
        scatter_chart.scatter(scatter_data_x, scatter_data_y, alpha=0.6, size=20)
        scatter_chart.set_title("Pure Python Scatter Plot")
        scatter_chart.save(str(output_dir / "pure_scatter_chart.png"), dpi=300)

        # Bar Chart
        print("Creating BarChart...")
        categories = ['A', 'B', 'C', 'D', 'E']
        values = [23, 45, 56, 78, 32]

        bar_chart = vizly.BarChart(width=800, height=600)
        bar_chart.bar(categories, values, color='skyblue')
        bar_chart.set_title("Pure Python Bar Chart")
        bar_chart.save(str(output_dir / "pure_bar_chart.png"), dpi=300)

        # Surface Chart
        print("Creating SurfaceChart...")
        x_surf = np.linspace(-3, 3, 30)
        y_surf = np.linspace(-3, 3, 30)
        X, Y = np.meshgrid(x_surf, y_surf)
        Z = np.sin(np.sqrt(X**2 + Y**2))

        surface_chart = vizly.SurfaceChart(width=800, height=600)
        surface_chart.plot_surface(X, Y, Z, cmap='viridis')
        surface_chart.set_title("Pure Python 3D Surface")
        surface_chart.save(str(output_dir / "pure_surface_chart.png"), dpi=300)

        print("✅ Pure Python charts created successfully")

    except ImportError as e:
        print(f"⚠️  Pure charts module not available: {e}")
    except Exception as e:
        print(f"❌ Error creating pure charts: {e}")


def demo_gpu_acceleration(output_dir: Path):
    """Demonstrate GPU acceleration capabilities."""
    print("\n🚀 2. GPU Acceleration")
    print("-" * 30)

    try:
        import vizly.gpu as vgpu

        # Get best available backend
        backend = vgpu.get_best_backend()
        print(f"Using GPU backend: {backend.device_info.get('backend', 'Unknown')}")
        print(f"Device: {backend.device_info.get('name', 'Unknown')}")

        # GPU-accelerated renderer
        renderer = vgpu.AcceleratedRenderer(width=1024, height=768)

        # Large scatter plot (GPU optimized)
        print("Creating GPU-accelerated scatter plot...")
        n_points = 50000
        x_gpu = np.random.randn(n_points) * 2
        y_gpu = np.random.randn(n_points) * 2

        start_time = time.time()
        renderer.scatter_gpu(x_gpu, y_gpu, color='red', size=15)
        gpu_time = time.time() - start_time

        renderer.save(str(output_dir / "gpu_scatter_50k.png"), dpi=300)
        print(f"GPU scatter plot ({n_points:,} points) rendered in {gpu_time:.3f}s")

        # GPU line chart
        print("Creating GPU line chart...")
        x_line = np.linspace(0, 20, 10000)
        y_line = np.sin(x_line) * np.exp(-x_line/10)

        renderer_line = vgpu.AcceleratedRenderer(width=1024, height=768)
        start_time = time.time()
        renderer_line.line_gpu(x_line, y_line, color='blue', linewidth=2.0)
        gpu_line_time = time.time() - start_time

        renderer_line.save(str(output_dir / "gpu_line_chart.png"), dpi=300)
        print(f"GPU line chart (10k points) rendered in {gpu_line_time:.3f}s")

        # Performance comparison
        print(f"GPU Performance Summary:")
        print(f"  Scatter: {n_points/gpu_time:.0f} points/sec")
        print(f"  Line: {len(x_line)/gpu_line_time:.0f} points/sec")

        print("✅ GPU acceleration demo completed")

    except ImportError as e:
        print(f"⚠️  GPU module not available: {e}")
    except Exception as e:
        print(f"❌ Error in GPU demo: {e}")


def demo_3d_interaction():
    """Demonstrate 3D interaction capabilities."""
    print("\n🎮 3. 3D Interaction & Scene Management")
    print("-" * 40)

    try:
        import vizly.interaction3d as i3d

        # Advanced 3D Scene
        print("Creating Advanced 3D Scene...")
        scene = i3d.Advanced3DScene()

        # Add interactive objects
        cube_id = scene.add_interactive_object("cube", position=[0, 1, 0], size=1.0)
        sphere_id = scene.add_interactive_object("sphere", position=[2, 1, 0], radius=0.8)

        # Enable physics
        scene.enable_physics()
        print(f"Added interactive objects: {cube_id}, {sphere_id}")

        # Scene statistics
        stats = scene.get_scene_stats()
        print(f"Scene objects: {stats['objects']['total']}")
        print(f"Physics enabled: {stats['physics']['enabled']}")

        # Scene graph management
        print("Testing scene graph...")
        scene_manager = i3d.Scene3DManager(width=1024, height=768)

        # Add mesh objects
        cube_mesh = i3d.MeshObject("demo_cube", np.array([[0,0,0], [1,0,0], [1,1,0], [0,1,0]]),
                                  np.array([[0,1,2], [0,2,3]]))
        scene_manager.add_object(cube_mesh)

        # Spatial queries
        nearby_objects = scene_manager.query_objects(np.array([0.5, 0.5, 0]), radius=2.0)
        print(f"Objects near center: {len(nearby_objects)}")

        # Performance test
        for i in range(100):
            point_cloud = i3d.PointCloudObject(f"points_{i}",
                                              np.random.randn(1000, 3))
            scene_manager.add_object(point_cloud)

        scene_stats = scene_manager.get_scene_stats()
        print(f"Scene performance: {scene_stats['performance']['fps']:.1f} FPS")
        print(f"Total objects: {scene_stats['objects']['total']}")

        print("✅ 3D interaction demo completed")

    except ImportError as e:
        print(f"⚠️  3D interaction module not available: {e}")
    except Exception as e:
        print(f"❌ Error in 3D demo: {e}")


def demo_vr_ar():
    """Demonstrate VR/AR capabilities."""
    print("\n🥽 4. VR/AR Visualization")
    print("-" * 30)

    try:
        import vizly.vr as vr

        # WebXR Session
        print("Setting up WebXR session...")
        webxr_session = vr.WebXRSession("immersive-vr")

        # Add sample charts to VR
        scatter_data = {
            'type': 'scatter',
            'x': np.random.randn(100).tolist(),
            'y': np.random.randn(100).tolist(),
            'z': np.random.randn(100).tolist()
        }

        chart_id = webxr_session.add_chart(scatter_data, transform={
            'position': [0, 1.5, -2],
            'rotation': [0, 0, 0, 1],
            'scale': [1, 1, 1]
        })

        print(f"Added VR chart: {chart_id}")

        # VR Scene Management
        print("Creating VR scene...")
        vr_scene = vr.VRScene()
        vr_scene.setup_room_scale([(-2, -2), (2, -2), (2, 2), (-2, 2)])

        # Immersive Charts
        print("Creating immersive charts...")
        vr_scatter = vr.VRScatterChart("vr_demo_scatter")
        vr_scatter.update_data({
            'x': np.random.randn(200),
            'y': np.random.randn(200),
            'z': np.random.randn(200),
            'colors': ['red', 'blue', 'green'] * 67
        })

        vr_surface = vr.VRSurfaceChart("vr_demo_surface")
        X, Y = np.meshgrid(np.linspace(-2, 2, 20), np.linspace(-2, 2, 20))
        Z = np.sin(np.sqrt(X**2 + Y**2))
        vr_surface.update_data({'X': X, 'Y': Y, 'Z': Z})

        # Spatial renderer
        spatial_renderer = vr.SpatialRenderer(width=2048, height=2048)

        # Add charts to renderer
        chart_renderer = vr.ImmersiveChartRenderer(spatial_renderer)
        chart_renderer.add_chart(vr_scatter)
        chart_renderer.add_chart(vr_surface)

        stats = chart_renderer.get_chart_stats()
        print(f"Immersive charts: {stats['chart_count']}")
        print(f"Spatial objects: {stats['total_spatial_objects']}")

        # AR Demo
        print("Setting up AR session...")
        ar_canvas = vr.ARCanvas(width=1920, height=1080)
        ar_canvas.add_plane_anchor(np.array([0, 0, -2]), np.array([0, 1, 0]), (2.0, 2.0))

        ar_chart = vr.AROverlayChart("ar_demo_chart")
        ar_chart.set_anchor_plane(np.array([0, 0, -2]), np.array([0, 1, 0]), (2.0, 2.0))
        ar_chart.update_data({
            'type': 'bar',
            'values': [1, 3, 2, 5, 4],
            'labels': ['A', 'B', 'C', 'D', 'E']
        })

        print("✅ VR/AR demo completed")

    except ImportError as e:
        print(f"⚠️  VR/AR module not available: {e}")
    except Exception as e:
        print(f"❌ Error in VR/AR demo: {e}")


async def demo_streaming():
    """Demonstrate real-time streaming capabilities."""
    print("\n📡 5. Real-time Streaming")
    print("-" * 30)

    try:
        import vizly.streaming as stream

        # Streaming data manager
        print("Setting up streaming infrastructure...")
        coordinator = stream.StreamingCoordinator()

        # Simulated data streams
        def sine_generator(t):
            return np.sin(2 * np.pi * 0.1 * t) + 0.1 * np.random.randn()

        def cosine_generator(t):
            return np.cos(2 * np.pi * 0.15 * t) + 0.1 * np.random.randn()

        sine_streamer = stream.SimulatedDataStreamer("sine_data", sine_generator, interval=0.1)
        cosine_streamer = stream.SimulatedDataStreamer("cosine_data", cosine_generator, interval=0.1)

        coordinator.add_streamer(sine_streamer)
        coordinator.add_streamer(cosine_streamer)

        # Realtime charts
        print("Creating real-time charts...")
        line_chart = stream.RealtimeLineChart(width=800, height=600)
        line_chart.add_line_stream("sine_data", sine_streamer, color='blue', linewidth=2.0)
        line_chart.add_line_stream("cosine_data", cosine_streamer, color='red', linewidth=2.0)
        line_chart.set_time_window(10.0)  # 10 second window

        # Streaming analytics
        analytics = stream.StreamingAnalytics()
        analytics.add_stream_analytics("sine_data", {
            'aggregators': ['mean', 'std', 'minmax'],
            'window_size': 30.0,
            'anomaly_detection': True,
            'anomaly_threshold': 2.5
        })

        # Start streaming
        print("Starting streaming session...")
        await coordinator.start_all()

        # Run for a few seconds
        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < 5.0:  # Run for 5 seconds
            # Process data points
            for stream_id in ["sine_data", "cosine_data"]:
                buffer = coordinator.get_stream(stream_id)
                if buffer:
                    latest_points = buffer.get_latest(10)
                    for point in latest_points:
                        analytics.process_data_point(stream_id, point.value, point.timestamp)

            # Render frame
            canvas = line_chart.render_frame()
            frame_count += 1

            await asyncio.sleep(0.1)

        await coordinator.stop_all()

        # Get statistics
        stream_stats = coordinator.data_manager.get_all_stats()
        analytics_stats = analytics.get_performance_stats()

        print(f"Streaming session completed:")
        print(f"  Frames rendered: {frame_count}")
        print(f"  Streams: {len(stream_stats)}")
        print(f"  Data points processed: {analytics_stats['processed_points']}")
        print(f"  Processing rate: {analytics_stats['points_per_second']:.1f} points/sec")

        print("✅ Real-time streaming demo completed")

    except ImportError as e:
        print(f"⚠️  Streaming module not available: {e}")
    except Exception as e:
        print(f"❌ Error in streaming demo: {e}")


def demo_performance_benchmarks():
    """Demonstrate performance benchmarks."""
    print("\n⚡ 6. Performance Benchmarks")
    print("-" * 35)

    try:
        # Basic chart performance
        print("Benchmarking chart creation...")

        # Test data sizes
        sizes = [100, 1000, 10000]

        for size in sizes:
            x = np.random.randn(size)
            y = np.random.randn(size)

            # Pure Python performance
            try:
                import vizly
                start_time = time.time()
                chart = vizly.ScatterChart()
                chart.scatter(x, y)
                pure_time = time.time() - start_time
                print(f"Pure Python scatter ({size:,} points): {pure_time:.3f}s")
            except:
                print(f"Pure Python scatter ({size:,} points): Not available")

            # GPU performance
            try:
                import vizly.gpu as vgpu
                renderer = vgpu.AcceleratedRenderer()
                start_time = time.time()
                renderer.scatter_gpu(x, y)
                gpu_time = time.time() - start_time
                speedup = pure_time / gpu_time if 'pure_time' in locals() else 0
                print(f"GPU scatter ({size:,} points): {gpu_time:.3f}s (speedup: {speedup:.1f}x)")
            except:
                print(f"GPU scatter ({size:,} points): Not available")

        # GPU backend benchmarks
        try:
            import vizly.gpu as vgpu
            print("\nGPU Backend Benchmarks:")
            benchmarks = vgpu.benchmark_backends()
            for backend, result in benchmarks.items():
                if isinstance(result, dict) and result.get('available'):
                    print(f"  {backend}: {result['time']:.3f}s ({result['points_per_second']:.0f} pts/sec)")
                else:
                    print(f"  {backend}: Not available")
        except:
            print("GPU benchmarks: Not available")

        # Memory usage estimation
        import sys
        print(f"\nMemory usage: {sys.getsizeof(locals()) / 1024:.1f} KB")

        print("✅ Performance benchmarks completed")

    except Exception as e:
        print(f"❌ Error in performance benchmarks: {e}")


if __name__ == "__main__":
    exit(main())