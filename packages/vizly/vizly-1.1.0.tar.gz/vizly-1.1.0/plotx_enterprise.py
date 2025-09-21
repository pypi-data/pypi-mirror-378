#!/usr/bin/env python3
"""
Vizly Enterprise - Command Line Interface
========================================

Enterprise visualization platform with advanced security, performance,
and collaboration features for Fortune 500 companies.

Usage:
    vizly-enterprise --help
    vizly-enterprise server start [--port=8080] [--config=enterprise.yaml]
    vizly-enterprise admin create-user <username> <role>
    vizly-enterprise admin list-users
    vizly-enterprise security audit [--days=30]
    vizly-enterprise performance benchmark [--dataset-size=1000000]
    vizly-enterprise license check
    vizly-enterprise cluster status

Examples:
    # Start enterprise server
    vizly-enterprise server start --port=8443 --config=production.yaml

    # Create new admin user
    vizly-enterprise admin create-user admin@company.com super_admin

    # Run security audit
    vizly-enterprise security audit --days=7

    # Benchmark performance
    vizly-enterprise performance benchmark --dataset-size=5000000
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from vizly.enterprise import __version__ as enterprise_version
from vizly import __version__ as core_version


def main():
    parser = argparse.ArgumentParser(
        description="Vizly Enterprise - Enterprise Visualization Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Vizly Enterprise {enterprise_version} (Core: {core_version})"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Server commands
    server_parser = subparsers.add_parser("server", help="Server management")
    server_subparsers = server_parser.add_subparsers(dest="server_action")

    start_parser = server_subparsers.add_parser("start", help="Start enterprise server")
    start_parser.add_argument("--port", type=int, default=8888, help="Server port")
    start_parser.add_argument("--config", help="Configuration file path")
    start_parser.add_argument("--ssl", action="store_true", help="Enable SSL/TLS")
    start_parser.add_argument("--no-ssl", action="store_true", help="Disable SSL/TLS")

    stop_parser = server_subparsers.add_parser("stop", help="Stop enterprise server")
    status_parser = server_subparsers.add_parser("status", help="Server status")

    # Admin commands
    admin_parser = subparsers.add_parser("admin", help="Administrative tasks")
    admin_subparsers = admin_parser.add_subparsers(dest="admin_action")

    create_user_parser = admin_subparsers.add_parser("create-user", help="Create new user")
    create_user_parser.add_argument("username", help="Username/email")
    create_user_parser.add_argument("role", choices=["viewer", "analyst", "admin", "super_admin"])

    list_users_parser = admin_subparsers.add_parser("list-users", help="List all users")

    # Security commands
    security_parser = subparsers.add_parser("security", help="Security management")
    security_subparsers = security_parser.add_subparsers(dest="security_action")

    audit_parser = security_subparsers.add_parser("audit", help="Generate security audit")
    audit_parser.add_argument("--days", type=int, default=30, help="Audit period in days")
    audit_parser.add_argument("--user", help="Specific user to audit")
    audit_parser.add_argument("--export", help="Export to file")

    # Performance commands
    perf_parser = subparsers.add_parser("performance", help="Performance management")
    perf_subparsers = perf_parser.add_subparsers(dest="perf_action")

    benchmark_parser = perf_subparsers.add_parser("benchmark", help="Run performance benchmark")
    benchmark_parser.add_argument("--dataset-size", type=int, default=1000000)
    benchmark_parser.add_argument("--chart-type", choices=["scatter", "line", "heatmap"], default="scatter")
    benchmark_parser.add_argument("--gpu", action="store_true", help="Test GPU acceleration")

    monitor_parser = perf_subparsers.add_parser("monitor", help="Start performance monitoring")
    monitor_parser.add_argument("--interval", type=float, default=1.0, help="Monitoring interval")

    dashboard_parser = perf_subparsers.add_parser("dashboard", help="Start performance dashboard")
    dashboard_parser.add_argument("--dashboard-port", type=int, default=8889, help="Dashboard port")

    metrics_parser = perf_subparsers.add_parser("metrics", help="Display current metrics")

    # License commands
    license_parser = subparsers.add_parser("license", help="License management")
    license_subparsers = license_parser.add_subparsers(dest="license_action")

    check_parser = license_subparsers.add_parser("check", help="Check license status")
    activate_parser = license_subparsers.add_parser("activate", help="Activate license")
    activate_parser.add_argument("license_key", help="License key")

    # Cluster commands
    cluster_parser = subparsers.add_parser("cluster", help="Cluster management")
    cluster_subparsers = cluster_parser.add_subparsers(dest="cluster_action")

    status_parser = cluster_subparsers.add_parser("status", help="Cluster status")
    scale_parser = cluster_subparsers.add_parser("scale", help="Scale cluster")
    scale_parser.add_argument("workers", type=int, help="Number of workers")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate handler
    if args.command == "server":
        handle_server_command(args)
    elif args.command == "admin":
        handle_admin_command(args)
    elif args.command == "security":
        handle_security_command(args)
    elif args.command == "performance":
        handle_performance_command(args)
    elif args.command == "license":
        handle_license_command(args)
    elif args.command == "cluster":
        handle_cluster_command(args)
    else:
        parser.print_help()


def handle_server_command(args):
    """Handle server management commands."""
    if args.server_action == "start":
        print(f"🚀 Starting Vizly Enterprise Server...")
        print(f"   Port: {args.port}")

        # Determine SSL setting
        ssl_enabled = args.ssl and not args.no_ssl
        print(f"   SSL: {'Enabled' if ssl_enabled else 'Disabled'}")

        if args.config:
            print(f"   Config: {args.config}")

        from vizly.enterprise.server import EnterpriseServer
        server = EnterpriseServer(port=args.port, ssl_enabled=ssl_enabled)
        server.start()

    elif args.server_action == "stop":
        print("🛑 Stopping Vizly Enterprise Server...")
        # Implementation for server stop

    elif args.server_action == "status":
        print("📊 Vizly Enterprise Server Status:")
        # Implementation for server status


def handle_admin_command(args):
    """Handle administrative commands."""
    if args.admin_action == "create-user":
        print(f"👤 Creating user: {args.username} with role: {args.role}")

        from vizly.enterprise.admin import UserManager
        user_manager = UserManager()
        success = user_manager.create_user(args.username, args.role)

        if success:
            print(f"✅ User {args.username} created successfully")
        else:
            print(f"❌ Failed to create user {args.username}")

    elif args.admin_action == "list-users":
        print("📋 Enterprise Users:")

        from vizly.enterprise.admin import UserManager
        user_manager = UserManager()
        users = user_manager.list_users()

        for user in users:
            print(f"  • {user['username']} ({user['role']}) - Last login: {user.get('last_login', 'Never')}")


def handle_security_command(args):
    """Handle security management commands."""
    if args.security_action == "audit":
        print(f"🔍 Generating security audit for last {args.days} days...")

        from vizly.enterprise.security import ComplianceAuditLogger
        from datetime import datetime, timedelta

        audit_logger = ComplianceAuditLogger()
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=args.days)

        report = audit_logger.generate_compliance_report(
            start_date, end_date, user_id=args.user
        )

        print(f"📊 Audit Report Summary:")
        print(f"   Total Events: {report['summary']['total_events']}")
        print(f"   Failed Events: {report['summary']['failed_events']}")
        print(f"   Success Rate: {report['summary']['success_rate']:.1%}")

        if args.export:
            import json
            with open(args.export, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report exported to: {args.export}")


def handle_performance_command(args):
    """Handle performance management commands."""
    if args.perf_action == "benchmark":
        print(f"⚡ Running performance benchmark...")
        print(f"   Dataset size: {args.dataset_size:,} points")
        print(f"   Chart type: {args.chart_type}")
        print(f"   GPU acceleration: {'Enabled' if args.gpu else 'Disabled'}")

        from vizly.enterprise.benchmarks import PerformanceBenchmark
        benchmark = PerformanceBenchmark()

        results = benchmark.run_benchmark(
            dataset_size=args.dataset_size,
            chart_type=args.chart_type,
            use_gpu=args.gpu
        )

        print(f"📈 Benchmark Results:")
        print(f"   Render Time: {results['render_time']:.2f}s")
        print(f"   FPS: {results['fps']:.1f}")
        print(f"   Memory Usage: {results['memory_mb']:.1f} MB")
        print(f"   Points/Second: {results['points_per_second']:,.0f}")

    elif args.perf_action == "monitor":
        print("📈 Starting enterprise performance monitoring...")

        from vizly.enterprise.monitoring import initialize_monitoring
        monitor = initialize_monitoring()

        print("✅ Performance monitoring initialized")
        print("   • Real-time metrics collection enabled")
        print("   • Alert management active")
        print("   • Dashboard available at http://localhost:8889")

        # Keep running until interrupted
        try:
            import time
            while True:
                time.sleep(10)
                dashboard_data = monitor.get_dashboard_data()
                health_score = dashboard_data['system_health'].get('health_score', 0)
                print(f"   Health Score: {health_score:.1f}/100", end='\r')
        except KeyboardInterrupt:
            print("\n🛑 Stopping performance monitoring...")
            monitor.stop_monitoring()

    elif args.perf_action == "dashboard":
        print("🎯 Starting performance dashboard server...")

        from vizly.enterprise.dashboard_server import run_dashboard_server
        print("   Dashboard available at http://localhost:8889")
        run_dashboard_server(port=getattr(args, 'dashboard_port', 8889))

    elif args.perf_action == "metrics":
        print("📊 Displaying current metrics...")

        from vizly.enterprise.monitoring import get_performance_monitor
        monitor = get_performance_monitor()
        dashboard_data = monitor.get_dashboard_data()

        print("\n🖥️  System Health:")
        system_health = dashboard_data['system_health']
        print(f"   Health Score: {system_health.get('health_score', 0):.1f}/100")
        print(f"   Status: {system_health.get('status', 'unknown').title()}")
        print(f"   CPU Usage: {system_health.get('avg_cpu_usage', 0):.1f}%")
        print(f"   Memory Usage: {system_health.get('avg_memory_usage', 0):.1f}%")

        print("\n⚡ API Performance:")
        api_perf = dashboard_data['api_performance']
        print(f"   Avg Response Time: {api_perf.get('average_response_time', 0):.3f}s")
        print(f"   Request Rate: {api_perf.get('requests_per_minute', 0):.0f}/min")
        print(f"   Error Rate: {api_perf.get('error_rate', 0)*100:.2f}%")

        print("\n🚨 Active Alerts:")
        active_alerts = dashboard_data['active_alerts']
        if active_alerts:
            for alert in active_alerts[:5]:
                print(f"   • {alert['severity'].upper()}: {alert['message']}")
        else:
            print("   No active alerts ✅")


def handle_license_command(args):
    """Handle license management commands."""
    if args.license_action == "check":
        print("📜 Checking Vizly Enterprise License...")

        from vizly.enterprise.licensing import LicenseManager
        license_mgr = LicenseManager()
        status = license_mgr.check_license()

        print(f"   Status: {status['status']}")
        print(f"   Licensed Users: {status['licensed_users']}")
        print(f"   Expires: {status['expiration_date']}")
        print(f"   Features: {', '.join(status['features'])}")

    elif args.license_action == "activate":
        print(f"🔑 Activating license: {args.license_key[:8]}...")

        from vizly.enterprise.licensing import LicenseManager
        license_mgr = LicenseManager()
        success = license_mgr.activate_license(args.license_key)

        if success:
            print("✅ License activated successfully")
        else:
            print("❌ License activation failed")


def handle_cluster_command(args):
    """Handle cluster management commands."""
    if args.cluster_action == "status":
        print("🖥️  Cluster Status:")

        from vizly.enterprise.performance import DistributedDataEngine
        from vizly.enterprise.performance import ComputeClusterConfig

        config = ComputeClusterConfig()
        engine = DistributedDataEngine(config)
        status = engine.get_cluster_status()

        print(f"   Type: {status['cluster_type']}")
        print(f"   Workers: {status['worker_count']}")
        print(f"   Active Jobs: {status['active_jobs']}")
        print(f"   Queue Size: {status['queue_size']}")

    elif args.cluster_action == "scale":
        print(f"📈 Scaling cluster to {args.workers} workers...")
        # Implementation for cluster scaling


if __name__ == "__main__":
    main()