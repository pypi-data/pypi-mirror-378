#!/usr/bin/env python3
"""
Vizly Enterprise Performance Monitoring Demo

Comprehensive demonstration of the enterprise performance monitoring,
metrics aggregation, and business intelligence capabilities.

This demo shows:
- Real-time performance monitoring setup
- Custom metrics definition and aggregation
- Business intelligence KPI calculations
- Dashboard generation and visualization
- Alert management and notification system
- Executive reporting and analytics

Usage:
    python performance_monitoring_demo.py
"""

import time
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add source path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vizly.enterprise.monitoring import (
    PerformanceMonitor, initialize_monitoring,
    get_performance_monitor
)
from vizly.enterprise.dashboard import (
    PerformanceDashboard, create_system_admin_dashboard,
    create_executive_dashboard
)
from vizly.enterprise.metrics_aggregator import (
    MetricsAggregator, BusinessIntelligenceEngine,
    MetricDefinition, AggregationType, TimeWindow,
    get_metrics_aggregator, get_bi_engine
)


def demo_basic_monitoring():
    """Demo basic performance monitoring setup"""
    print("🔧 Setting up Performance Monitoring")
    print("=" * 50)

    # Initialize monitoring
    config = {
        'storage_backend': 'memory',
        'collection_interval': 5.0
    }

    monitor = initialize_monitoring(config)
    print("✅ Performance monitor initialized")

    # Let monitoring run for a bit
    print("📊 Collecting metrics for 30 seconds...")
    time.sleep(30)

    # Get current dashboard data
    dashboard_data = monitor.get_dashboard_data()

    print(f"\n📈 Current System Health:")
    system_health = dashboard_data['system_health']
    print(f"   Health Score: {system_health.get('health_score', 0):.1f}/100")
    print(f"   Status: {system_health.get('status', 'unknown').title()}")

    if 'metrics' in dashboard_data:
        metrics = dashboard_data['metrics']
        if 'cpu' in metrics and metrics['cpu']:
            latest_cpu = metrics['cpu'][-1]['value']
            print(f"   CPU Usage: {latest_cpu:.1f}%")

        if 'memory' in metrics and metrics['memory']:
            latest_memory = metrics['memory'][-1]['value']
            print(f"   Memory Usage: {latest_memory:.1f}%")

    print("\n" + "=" * 50)


def demo_custom_metrics():
    """Demo custom enterprise metrics definition"""
    print("🎯 Custom Enterprise Metrics")
    print("=" * 50)

    # Get metrics aggregator
    aggregator = get_metrics_aggregator()

    # Define custom business metrics
    user_satisfaction_metric = MetricDefinition(
        name="user_satisfaction_index",
        description="Composite user satisfaction score",
        source_metrics=["api.request.duration", "api.error.rate"],
        calculation="apdex_score",
        unit="score",
        category="business",
        alert_thresholds={"critical": 0.7, "warning": 0.85},
        business_impact="critical"
    )

    system_efficiency_metric = MetricDefinition(
        name="system_efficiency_score",
        description="Overall system resource efficiency",
        source_metrics=["system.cpu.usage_percent", "system.memory.usage_percent"],
        calculation="100 - ((system.cpu.usage_percent + system.memory.usage_percent) / 2)",
        unit="percentage",
        category="efficiency",
        alert_thresholds={"warning": 70.0, "critical": 50.0},
        business_impact="high"
    )

    # Register metrics
    aggregator.define_metric(user_satisfaction_metric)
    aggregator.define_metric(system_efficiency_metric)

    print("✅ Custom metrics defined:")
    print(f"   • {user_satisfaction_metric.name}")
    print(f"   • {system_efficiency_metric.name}")

    # Add aggregation rules
    aggregator.add_aggregation_rule(
        "user_satisfaction_index",
        AggregationType.AVERAGE,
        TimeWindow.FIFTEEN_MINUTES
    )

    aggregator.add_aggregation_rule(
        "system_efficiency_score",
        AggregationType.AVERAGE,
        TimeWindow.HOUR
    )

    print("✅ Aggregation rules configured")
    print("\n" + "=" * 50)


def demo_business_intelligence():
    """Demo business intelligence and KPI calculations"""
    print("💼 Business Intelligence & KPIs")
    print("=" * 50)

    # Get BI engine
    bi_engine = get_bi_engine()

    # Calculate business KPIs
    kpis = bi_engine.calculate_business_kpis(timedelta(hours=1))

    print("📊 Current Business KPIs:")
    for kpi_name, value in kpis.items():
        print(f"   • {kpi_name}: {value:.2f}")

    # Generate executive report
    executive_report = bi_engine.generate_executive_report()

    print(f"\n📋 Executive Summary:")
    print(f"   Overall Health Score: {executive_report['overall_health_score']:.1f}")
    print(f"   Report Period: {executive_report['time_period']}")

    print(f"\n🎯 Key Performance Insights:")
    for insight in executive_report['key_insights'][:3]:
        print(f"   • {insight}")

    print(f"\n💡 Recommendations:")
    for rec in executive_report['recommendations'][:3]:
        print(f"   • {rec}")

    print("\n" + "=" * 50)


def demo_dashboard_generation():
    """Demo dashboard generation and visualization"""
    print("📊 Dashboard Generation")
    print("=" * 50)

    # Create different dashboard types
    admin_dashboard = create_system_admin_dashboard()
    exec_dashboard = create_executive_dashboard()

    print("✅ Dashboard types created:")
    print("   • System Administrator Dashboard")
    print("   • Executive Dashboard")

    try:
        # Generate system health chart
        print("\n🎨 Generating system health visualization...")
        health_chart = admin_dashboard.generate_system_health_chart()
        health_chart.savefig("system_health_demo.png", dpi=150, bbox_inches='tight')
        print("   📈 System health chart saved: system_health_demo.png")

        # Generate resource usage chart
        print("🎨 Generating resource usage trends...")
        resource_chart = admin_dashboard.generate_resource_usage_chart()
        resource_chart.savefig("resource_usage_demo.png", dpi=150, bbox_inches='tight')
        print("   📈 Resource usage chart saved: resource_usage_demo.png")

        # Generate API performance chart
        print("🎨 Generating API performance analytics...")
        api_chart = admin_dashboard.generate_api_performance_chart()
        api_chart.savefig("api_performance_demo.png", dpi=150, bbox_inches='tight')
        print("   📈 API performance chart saved: api_performance_demo.png")

    except Exception as e:
        print(f"   ⚠️  Chart generation skipped: {e}")

    # Generate alerts overview
    alerts_overview = admin_dashboard.generate_alerts_overview()
    print(f"\n🚨 Alerts Overview:")
    print(f"   Active Alerts: {alerts_overview['active_count']}")
    print(f"   Last 24h Total: {alerts_overview['total_24h']}")

    # Executive summary
    exec_summary = exec_dashboard.generate_executive_summary()
    print(f"\n👔 Executive Summary:")
    print(f"   Overall Status: {exec_summary['overall_status']['status']}")
    print(f"   Health Score: {exec_summary['overall_status']['score']:.1f}")

    print("\n" + "=" * 50)


def demo_alert_management():
    """Demo alert management and notification system"""
    print("🚨 Alert Management System")
    print("=" * 50)

    # Get performance monitor
    monitor = get_performance_monitor()
    alert_manager = monitor.alert_manager

    # Add custom alert rules
    alert_manager.add_alert_rule(
        'demo_high_cpu', 'system.cpu.usage_percent', 75.0, 'greater', 'warning',
        'Demo: High CPU usage detected'
    )

    alert_manager.add_alert_rule(
        'demo_critical_memory', 'system.memory.usage_percent', 90.0, 'greater', 'critical',
        'Demo: Critical memory usage - immediate attention required'
    )

    print("✅ Custom alert rules added:")
    print("   • High CPU usage alert (75% threshold)")
    print("   • Critical memory usage alert (90% threshold)")

    # Add notification callback
    def demo_notification_handler(alert):
        print(f"📧 ALERT NOTIFICATION: {alert.severity.upper()} - {alert.message}")

    alert_manager.add_notification_callback(demo_notification_handler)
    print("✅ Notification handler configured")

    # Simulate checking alerts
    print("\n🔍 Checking alert conditions...")
    alert_manager.check_alerts()

    active_alerts = alert_manager.get_active_alerts()
    if active_alerts:
        print(f"⚠️  {len(active_alerts)} active alerts found")
        for alert in active_alerts:
            print(f"   • {alert.severity.upper()}: {alert.message}")
    else:
        print("✅ No active alerts")

    print("\n" + "=" * 50)


def demo_performance_api_integration():
    """Demo integration with API performance tracking"""
    print("⚡ API Performance Integration")
    print("=" * 50)

    monitor = get_performance_monitor()

    # Simulate API requests
    print("🔄 Simulating API requests...")

    import random

    for i in range(10):
        endpoint = random.choice(['/api/charts', '/api/users', '/api/auth/login'])
        duration = random.uniform(0.05, 0.5)
        status_code = random.choice([200, 200, 200, 200, 401, 500])  # Mostly 200s

        monitor.record_api_request(endpoint, duration, status_code)
        time.sleep(0.1)

    print("✅ API requests recorded")

    # Simulate chart generation
    print("🎨 Simulating chart generation...")

    for i in range(5):
        chart_type = random.choice(['scatter', 'line', 'bar', 'surface'])
        duration = random.uniform(0.2, 1.5)
        success = random.choice([True, True, True, False])  # Mostly successful

        monitor.record_chart_generation(chart_type, duration, success)
        time.sleep(0.1)

    print("✅ Chart generation metrics recorded")

    # Get updated performance data
    dashboard_data = monitor.get_dashboard_data()
    api_perf = dashboard_data['api_performance']

    print(f"\n📊 Updated API Performance:")
    print(f"   Avg Response Time: {api_perf.get('average_response_time', 0):.3f}s")
    print(f"   Request Rate: {api_perf.get('requests_per_minute', 0):.0f}/min")
    print(f"   Error Rate: {api_perf.get('error_rate', 0)*100:.2f}%")

    print("\n" + "=" * 50)


def main():
    """Run complete performance monitoring demonstration"""
    print("🚀 Vizly Enterprise Performance Monitoring Demo")
    print("=" * 60)
    print("This demo showcases the complete enterprise monitoring capabilities")
    print("=" * 60)

    try:
        # Demo 1: Basic monitoring setup
        demo_basic_monitoring()

        # Demo 2: Custom metrics definition
        demo_custom_metrics()

        # Demo 3: Business intelligence
        demo_business_intelligence()

        # Demo 4: Dashboard generation
        demo_dashboard_generation()

        # Demo 5: Alert management
        demo_alert_management()

        # Demo 6: API performance integration
        demo_performance_api_integration()

        print("✅ Demo completed successfully!")
        print("\n🎯 Next Steps:")
        print("   • Start dashboard server: python -m vizly.enterprise.dashboard_server")
        print("   • Run CLI monitoring: python plotx_enterprise.py performance monitor")
        print("   • View metrics: python plotx_enterprise.py performance metrics")
        print("   • Start dashboard: python plotx_enterprise.py performance dashboard")

    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        monitor = get_performance_monitor()
        if monitor:
            monitor.stop_monitoring()
        print("\n🧹 Cleanup completed")


if __name__ == "__main__":
    main()