#!/usr/bin/env python3
"""
Vizly Enterprise API Examples
=============================

Comprehensive examples demonstrating enterprise API usage across
different scenarios and programming patterns.
"""

import sys
import os
from pathlib import Path
import asyncio
import json

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vizly.enterprise.api import VizlyEnterpriseClient, APIResponse


def example_basic_usage():
    """Basic API client usage example."""
    print("📘 Basic API Usage Example")
    print("-" * 30)

    # Initialize client with authentication
    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"  # In production, use environment variables
    )

    # Check server health
    health = client.health_check()
    if health.success:
        print(f"✅ Server is healthy: {health.data['status']}")
        print(f"   Version: {health.data['version']}")
    else:
        print(f"❌ Health check failed: {health.error}")
        return

    # Get system metrics
    metrics = client.get_metrics()
    if metrics.success:
        print(f"📊 System Metrics:")
        print(f"   CPU Usage: {metrics.data['cpu_usage']}%")
        print(f"   Memory Usage: {metrics.data['memory_usage']}%")
        print(f"   Active Sessions: {metrics.data['active_sessions']}")

    print()


def example_executive_dashboard():
    """Create executive dashboard with KPIs."""
    print("📊 Executive Dashboard Example")
    print("-" * 30)

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Define KPI data
    kpi_data = {
        "kpis": {
            "Q4 Revenue": {
                "value": 12500000,
                "target": 12000000,
                "status": "good"
            },
            "Profit Margin": {
                "value": 8.5,
                "target": 8.0,
                "status": "good"
            },
            "Customer Satisfaction": {
                "value": 87,
                "target": 90,
                "status": "warning"
            },
            "Market Share": {
                "value": 15.2,
                "target": 16.0,
                "status": "warning"
            },
            "Employee Retention": {
                "value": 92,
                "target": 95,
                "status": "critical"
            },
            "Innovation Index": {
                "value": 75,
                "target": 80,
                "status": "neutral"
            }
        }
    }

    # Create executive dashboard
    response = client.create_chart(
        "executive_dashboard",
        "Q4 2024 Executive Dashboard",
        data=kpi_data,
        security_level="confidential",
        compliance_tags=["Executive Reporting", "Board Review"]
    )

    if response.success:
        chart_info = response.data
        print(f"✅ Dashboard created successfully!")
        print(f"   Chart ID: {chart_info['id']}")
        print(f"   Title: {chart_info['title']}")
        print(f"   Security Level: {chart_info['security_level']}")
        print(f"   Compliance Tags: {', '.join(chart_info['compliance_tags'])}")
        print(f"   Audit Events: {chart_info['audit_trail_count']}")
    else:
        print(f"❌ Dashboard creation failed: {response.error}")

    print()


def example_financial_analytics():
    """Create financial analytics charts."""
    print("💰 Financial Analytics Example")
    print("-" * 30)

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Financial waterfall data
    financial_data = {
        "categories": ["Q1 Base", "Q2 Growth", "Q3 Investments", "Q4 Returns", "Year End"],
        "values": [10000000, 2500000, -1800000, 3200000, 13900000],
        "analysis_type": "waterfall"
    }

    # Create financial chart
    response = client.create_chart(
        "financial_analytics",
        "2024 Revenue Waterfall Analysis",
        data=financial_data,
        security_level="confidential",
        compliance_tags=["SOX", "Financial Reporting", "Board Review"]
    )

    if response.success:
        print(f"✅ Financial chart created!")
        print(f"   Chart ID: {response.data['id']}")
        print(f"   Security: {response.data['security_level']}")
        print(f"   SOX Compliant: {'SOX' in response.data['compliance_tags']}")
    else:
        print(f"❌ Financial chart failed: {response.error}")

    print()


def example_compliance_monitoring():
    """Create compliance scorecard."""
    print("🔍 Compliance Monitoring Example")
    print("-" * 30)

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Compliance metrics
    compliance_data = {
        "metrics": {
            "Data Protection (GDPR)": {
                "score": 95,
                "threshold_good": 90,
                "threshold_warning": 70
            },
            "Financial Controls (SOX)": {
                "score": 88,
                "threshold_good": 90,
                "threshold_warning": 70
            },
            "Security Protocols": {
                "score": 92,
                "threshold_good": 90,
                "threshold_warning": 70
            },
            "Healthcare Data (HIPAA)": {
                "score": 76,
                "threshold_good": 90,
                "threshold_warning": 70
            },
            "Policy Compliance": {
                "score": 85,
                "threshold_good": 90,
                "threshold_warning": 70
            }
        }
    }

    # Create compliance scorecard
    response = client.create_chart(
        "compliance",
        "Enterprise Compliance Dashboard",
        data=compliance_data,
        security_level="restricted",
        compliance_tags=["GDPR", "SOX", "HIPAA", "Audit", "Legal"]
    )

    if response.success:
        print(f"✅ Compliance dashboard created!")
        print(f"   Chart ID: {response.data['id']}")
        print(f"   Security: {response.data['security_level']} (highest level)")
        print(f"   Compliance Areas: {len(response.data['compliance_tags'])}")
    else:
        print(f"❌ Compliance dashboard failed: {response.error}")

    print()


def example_risk_analysis():
    """Create risk analysis matrix."""
    print("⚠️  Risk Analysis Example")
    print("-" * 30)

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Risk assessment data
    risk_data = {
        "risks": [
            {
                "name": "Cybersecurity Breach",
                "probability": 70,
                "impact": 85,
                "category": "Technology"
            },
            {
                "name": "Market Volatility",
                "probability": 60,
                "impact": 70,
                "category": "Financial"
            },
            {
                "name": "Regulatory Changes",
                "probability": 40,
                "impact": 60,
                "category": "Compliance"
            },
            {
                "name": "Supply Chain Disruption",
                "probability": 30,
                "impact": 80,
                "category": "Operational"
            },
            {
                "name": "Key Personnel Loss",
                "probability": 25,
                "impact": 90,
                "category": "Human Resources"
            },
            {
                "name": "Technology Obsolescence",
                "probability": 50,
                "impact": 55,
                "category": "Technology"
            }
        ]
    }

    # Create risk matrix
    response = client.create_chart(
        "risk_analysis",
        "Enterprise Risk Assessment Matrix",
        data=risk_data,
        security_level="confidential",
        compliance_tags=["Risk Management", "Executive Review"]
    )

    if response.success:
        print(f"✅ Risk matrix created!")
        print(f"   Chart ID: {response.data['id']}")
        print(f"   Risk Factors Analyzed: {len(risk_data['risks'])}")
        print(f"   Security Classification: {response.data['security_level']}")
    else:
        print(f"❌ Risk analysis failed: {response.error}")

    print()


def example_batch_operations():
    """Demonstrate batch chart creation."""
    print("📦 Batch Operations Example")
    print("-" * 30)

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Define multiple charts to create
    charts_to_create = [
        {
            "type": "executive_dashboard",
            "title": "Sales Performance Dashboard",
            "data": {
                "kpis": {
                    "Monthly Sales": {"value": 850000, "target": 800000, "status": "good"},
                    "New Customers": {"value": 127, "target": 150, "status": "warning"}
                }
            },
            "security_level": "internal"
        },
        {
            "type": "financial_analytics",
            "title": "Budget Variance Report",
            "security_level": "confidential",
            "compliance_tags": ["Finance", "Budget Review"]
        },
        {
            "type": "compliance",
            "title": "Monthly Compliance Check",
            "data": {
                "metrics": {
                    "Data Security": {"score": 94, "threshold_good": 90},
                    "Process Compliance": {"score": 87, "threshold_good": 85}
                }
            },
            "security_level": "internal"
        }
    ]

    created_charts = []
    for i, chart_config in enumerate(charts_to_create, 1):
        print(f"Creating chart {i}/{len(charts_to_create)}: {chart_config['title']}")

        chart_type = chart_config.pop('type', 'executive_dashboard')
        title = chart_config.pop('title', 'Default Chart')
        response = client.create_chart(chart_type, title, **chart_config)

        if response.success:
            created_charts.append(response.data)
            print(f"   ✅ Created: {response.data['id']}")
        else:
            print(f"   ❌ Failed: {response.error}")

    print(f"\n📊 Batch Summary:")
    print(f"   Total Charts Created: {len(created_charts)}")
    print(f"   Success Rate: {len(created_charts)/len(charts_to_create)*100:.1f}%")

    # List all charts
    charts_response = client.list_charts()
    if charts_response.success:
        total_charts = len(charts_response.data.get('charts', []))
        print(f"   Total Charts in System: {total_charts}")

    print()


def example_error_handling():
    """Demonstrate proper error handling."""
    print("🛡️  Error Handling Example")
    print("-" * 30)

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Test various error scenarios
    error_tests = [
        {
            "name": "Invalid Chart Type",
            "config": {
                "chart_type": "invalid_type",
                "title": "Test Chart"
            }
        },
        {
            "name": "Missing Required Data",
            "config": {
                "chart_type": "executive_dashboard",
                "title": ""  # Empty title
            }
        },
        {
            "name": "Invalid Security Level",
            "config": {
                "chart_type": "compliance",
                "title": "Test Compliance",
                "security_level": "invalid_level"
            }
        }
    ]

    for test in error_tests:
        print(f"Testing: {test['name']}")
        chart_type = test['config'].get('chart_type', 'executive_dashboard')
        title = test['config'].get('title', 'Test Chart')
        config_copy = test['config'].copy()
        config_copy.pop('chart_type', None)
        config_copy.pop('title', None)
        response = client.create_chart(chart_type, title, **config_copy)

        if response.success:
            print(f"   ⚠️  Unexpected success - this should have failed")
        else:
            print(f"   ✅ Correctly failed: {response.error}")
            print(f"   Status Code: {response.status_code}")

    print()


def example_advanced_features():
    """Demonstrate advanced API features."""
    print("🚀 Advanced Features Example")
    print("-" * 30)

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Create a chart with all advanced features
    advanced_chart = client.create_chart(
        "executive_dashboard",
        "Advanced Enterprise Dashboard",
        data={
            "kpis": {
                "AI/ML Model Accuracy": {"value": 94.5, "target": 95.0, "status": "warning"},
                "Data Pipeline Uptime": {"value": 99.8, "target": 99.5, "status": "good"},
                "API Response Time": {"value": 125, "target": 100, "status": "warning"},
                "Security Score": {"value": 96, "target": 95, "status": "good"}
            }
        },
        security_level="confidential",
        compliance_tags=["Tech Review", "Performance", "Security", "AI Governance"]
    )

    if advanced_chart.success:
        chart_id = advanced_chart.data['id']
        print(f"✅ Advanced chart created: {chart_id}")

        # Retrieve chart details
        chart_details = client.get_chart(chart_id)
        if chart_details.success:
            print(f"   Retrieved chart details successfully")
            print(f"   Chart Type: {chart_details.data.get('type', 'N/A')}")

        # Demonstrate listing with filters
        all_charts = client.list_charts()
        if all_charts.success:
            chart_count = len(all_charts.data.get('charts', []))
            print(f"   Total charts in system: {chart_count}")

    print()


async def example_async_operations():
    """Demonstrate asynchronous operations (conceptual)."""
    print("⚡ Async Operations Example")
    print("-" * 30)

    # Note: This is a conceptual example - actual async implementation
    # would require aiohttp or similar async HTTP client

    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    # Simulate concurrent chart creation
    chart_configs = [
        ("Sales Dashboard", "executive_dashboard"),
        ("Financial Report", "financial_analytics"),
        ("Compliance Check", "compliance"),
        ("Risk Assessment", "risk_analysis")
    ]

    print("Creating multiple charts concurrently...")

    # In a real async implementation, these would be awaited concurrently
    created_charts = []
    for title, chart_type in chart_configs:
        response = client.create_chart(
            chart_type,
            title,
            security_level="internal"
        )

        if response.success:
            created_charts.append(response.data)
            print(f"   ✅ {title}: {response.data['id']}")
        else:
            print(f"   ❌ {title}: {response.error}")

    print(f"\n📊 Created {len(created_charts)} charts")
    print()


def example_integration_patterns():
    """Show common integration patterns."""
    print("🔗 Integration Patterns Example")
    print("-" * 30)

    # Pattern 1: Configuration-driven chart creation
    def create_from_config(config_file: str):
        """Create charts from configuration file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            client = VizlyEnterpriseClient(**config['client_settings'])

            for chart_config in config['charts']:
                chart_type = chart_config.pop('type', 'executive_dashboard')
        title = chart_config.pop('title', 'Default Chart')
        response = client.create_chart(chart_type, title, **chart_config)
                if response.success:
                    print(f"   ✅ {chart_config['title']}")
                else:
                    print(f"   ❌ {chart_config['title']}: {response.error}")

        except FileNotFoundError:
            print("   ⚠️  Config file not found - skipping")

    # Pattern 2: Environment-based configuration
    def create_from_environment():
        """Create client from environment variables."""
        import os

        client = VizlyEnterpriseClient(
            base_url=os.getenv('PLOTX_API_URL', 'http://localhost:8888'),
            username=os.getenv('PLOTX_USERNAME'),
            password=os.getenv('PLOTX_PASSWORD'),
            api_key=os.getenv('PLOTX_API_KEY')
        )

        # Health check to verify connection
        health = client.health_check()
        print(f"   Environment config: {'✅ Connected' if health.success else '❌ Failed'}")

    # Pattern 3: Retry logic for resilience
    def create_with_retry(chart_config, max_retries=3):
        """Create chart with retry logic."""
        for attempt in range(max_retries):
            config_copy = chart_config.copy()
            chart_type = config_copy.pop('chart_type', 'executive_dashboard')
            title = config_copy.pop('title', 'Default Chart')
            response = client.create_chart(chart_type, title, **config_copy)

            if response.success:
                return response

            print(f"   Attempt {attempt + 1} failed: {response.error}")
            if attempt < max_retries - 1:
                print(f"   Retrying in {2 ** attempt} seconds...")
                import time
                time.sleep(2 ** attempt)

        return response

    print("1. Configuration-driven creation:")
    create_from_config("chart_config.json")

    print("\n2. Environment-based configuration:")
    create_from_environment()

    print("\n3. Resilient creation with retry:")
    client = VizlyEnterpriseClient(
        base_url="http://localhost:8888",
        username="admin@company.com",
        password="password123"
    )

    test_config = {
        "chart_type": "executive_dashboard",
        "title": "Resilient Test Chart",
        "security_level": "internal"
    }

    # Modify create_with_retry to handle the new signature
    def create_chart_wrapper(config):
        chart_type = config.pop('chart_type', 'executive_dashboard')
        title = config.pop('title', 'Test Chart')
        return client.create_chart(chart_type, title, **config)

    response = create_with_retry(test_config)
    if response.success:
        print(f"   ✅ Resilient creation succeeded")
    else:
        print(f"   ❌ All retry attempts failed")

    print()


def main():
    """Run all API examples."""
    print("🚀 Vizly Enterprise API Examples")
    print("=" * 50)

    try:
        # Basic examples
        example_basic_usage()
        example_executive_dashboard()
        example_financial_analytics()
        example_compliance_monitoring()
        example_risk_analysis()

        # Advanced examples
        example_batch_operations()
        example_error_handling()
        example_advanced_features()

        # Integration patterns
        example_integration_patterns()

        # Async example (conceptual)
        asyncio.run(example_async_operations())

        print("🎉 All examples completed successfully!")
        print("\n📚 Next Steps:")
        print("• Review the generated charts in the Vizly Enterprise web interface")
        print("• Explore the OpenAPI documentation for full API reference")
        print("• Integrate Vizly Enterprise into your applications")
        print("• Contact enterprise support for advanced features")

    except Exception as e:
        print(f"❌ Examples failed: {e}")
        print("\nTroubleshooting:")
        print("• Ensure Vizly Enterprise server is running")
        print("• Check your authentication credentials")
        print("• Verify network connectivity")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())