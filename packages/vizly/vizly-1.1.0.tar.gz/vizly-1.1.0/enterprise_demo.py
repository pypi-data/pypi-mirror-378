#!/usr/bin/env python3
"""
PlotX Enterprise Demo - Chart Enhancements
==========================================

Demonstration of enterprise chart types, themes, and export capabilities.
"""

import sys
import os
from pathlib import Path
import numpy as np
from datetime import datetime, timedelta

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from plotxy.enterprise import (
    EnterpriseChartFactory, ExecutiveDashboardChart, FinancialAnalyticsChart,
    ComplianceChart, RiskAnalysisChart, ThemeManager, BrandingConfig,
    AccessibilityConfig, EnterpriseExporter, ExportConfig
)
from plotxy.enterprise.security import SecurityLevel
from plotxy.figure import PlotXFigure


def demo_executive_dashboard():
    """Demonstrate executive dashboard chart."""
    print("📊 Creating Executive Dashboard...")

    # Create chart
    chart = EnterpriseChartFactory.create_chart('executive_dashboard')

    # Sample KPI data
    kpis = {
        'Revenue': {'value': 12500000, 'target': 12000000, 'status': 'good'},
        'Profit Margin': {'value': 8.5, 'target': 8.0, 'status': 'good'},
        'Customer Satisfaction': {'value': 87, 'target': 90, 'status': 'warning'},
        'Market Share': {'value': 15.2, 'target': 16.0, 'status': 'warning'},
        'Employee Retention': {'value': 92, 'target': 95, 'status': 'critical'},
        'Innovation Index': {'value': 75, 'target': 80, 'status': 'neutral'}
    }

    chart.create_kpi_dashboard(kpis, layout='grid')
    chart.set_security_classification(SecurityLevel.INTERNAL)
    chart.add_compliance_tag("Executive Reporting")

    print("   ✅ Executive dashboard created with 6 KPIs")
    return chart.figure, chart.metadata


def demo_financial_analytics():
    """Demonstrate financial analytics charts."""
    print("💰 Creating Financial Analytics...")

    chart = EnterpriseChartFactory.create_chart('financial_analytics')

    # Waterfall chart example
    categories = ['Q1 Revenue', 'Q2 Growth', 'Q3 Decline', 'Q4 Recovery', 'Total']
    values = [1000000, 250000, -180000, 320000, 1390000]

    chart.create_waterfall_chart(categories, values, "Revenue Waterfall Analysis")
    chart.set_security_classification(SecurityLevel.CONFIDENTIAL)
    chart.add_compliance_tag("SOX")
    chart.add_data_source("ERP System")

    print("   ✅ Financial waterfall chart created")
    return chart.figure, chart.metadata


def demo_compliance_chart():
    """Demonstrate compliance reporting charts."""
    print("🔍 Creating Compliance Charts...")

    chart = EnterpriseChartFactory.create_chart('compliance')

    # Sample compliance metrics
    compliance_metrics = {
        'Data Protection': {'score': 95, 'threshold_good': 90, 'threshold_warning': 70},
        'Financial Controls': {'score': 88, 'threshold_good': 90, 'threshold_warning': 70},
        'Security Protocols': {'score': 92, 'threshold_good': 90, 'threshold_warning': 70},
        'Audit Readiness': {'score': 76, 'threshold_good': 90, 'threshold_warning': 70},
        'Policy Compliance': {'score': 85, 'threshold_good': 90, 'threshold_warning': 70}
    }

    chart.create_compliance_scorecard(compliance_metrics)
    chart.set_security_classification(SecurityLevel.RESTRICTED)
    chart.add_compliance_tag("GDPR")
    chart.add_compliance_tag("SOX")
    chart.add_compliance_tag("HIPAA")

    print("   ✅ Compliance scorecard created")
    return chart.figure, chart.metadata


def demo_risk_analysis():
    """Demonstrate risk analysis charts."""
    print("⚠️  Creating Risk Analysis...")

    chart = EnterpriseChartFactory.create_chart('risk_analysis')

    # Sample risk data
    risks = [
        {'name': 'Cyber Security', 'probability': 70, 'impact': 85, 'category': 'Technology'},
        {'name': 'Market Volatility', 'probability': 60, 'impact': 70, 'category': 'Financial'},
        {'name': 'Regulatory Changes', 'probability': 40, 'impact': 60, 'category': 'Compliance'},
        {'name': 'Supply Chain', 'probability': 30, 'impact': 80, 'category': 'Operational'},
        {'name': 'Key Personnel', 'probability': 25, 'impact': 90, 'category': 'Human Resources'},
        {'name': 'Technology Obsolescence', 'probability': 50, 'impact': 55, 'category': 'Technology'}
    ]

    chart.create_risk_matrix(risks)
    chart.set_security_classification(SecurityLevel.CONFIDENTIAL)
    chart.add_compliance_tag("Risk Management")
    chart.add_data_source("Risk Management System")

    print("   ✅ Risk matrix created with 6 risk factors")
    return chart.figure, chart.metadata


def demo_themes():
    """Demonstrate enterprise themes."""
    print("🎨 Demonstrating Enterprise Themes...")

    # Create theme manager
    theme_manager = ThemeManager()

    # Create custom branding
    custom_branding = BrandingConfig(
        primary_color="#1f4e79",
        secondary_color="#28a745",
        company_name="Acme Corporation",
        font_family="Arial",
        watermark_text="© Acme Corp - Confidential"
    )

    # Demo different themes
    themes_to_demo = ['enterprise', 'presentation', 'print', 'dark']
    demo_charts = []

    for theme_name in themes_to_demo:
        print(f"   📋 Applying {theme_name} theme...")

        # Apply theme
        theme_manager.apply_theme(theme_name, custom_branding)

        # Create a simple chart to show theme
        figure = PlotXFigure(width=8, height=6)
        ax = figure.axes

        # Sample data
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        y3 = np.sin(x + np.pi/4)

        ax.plot(x, y1, label='Sales', linewidth=2)
        ax.plot(x, y2, label='Profit', linewidth=2)
        ax.plot(x, y3, label='Market Share', linewidth=2)

        ax.set_title(f'{theme_name.title()} Theme Demo - Financial Trends')
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Performance Index')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Apply branding
        if hasattr(theme_manager.current_theme, 'apply_corporate_branding'):
            theme_manager.current_theme.apply_corporate_branding(figure.figure)

        # Create metadata
        from plotxy.enterprise.charts import ChartMetadata
        metadata = ChartMetadata(
            chart_id=f"theme_demo_{theme_name}",
            title=f"{theme_name.title()} Theme Demo",
            created_by="demo_system"
        )

        demo_charts.append((figure, metadata, theme_name))

    print(f"   ✅ Created {len(demo_charts)} themed charts")
    return demo_charts


def demo_exports(charts_with_metadata):
    """Demonstrate enterprise export capabilities."""
    print("📤 Demonstrating Export Capabilities...")

    # Create exporter with branding
    branding = BrandingConfig(
        primary_color="#1f4e79",
        company_name="Demo Corporation",
        watermark_text="© Demo Corp - Internal Use Only"
    )
    exporter = EnterpriseExporter(branding)

    # Export configurations to test
    export_configs = [
        ExportConfig(format="pdf", include_metadata=True, branded=True),
        ExportConfig(format="png", dpi=300, watermark=True),
        ExportConfig(format="html", include_metadata=True),
        ExportConfig(format="json")
    ]

    exported_files = []

    for i, (figure, metadata) in enumerate(charts_with_metadata[:2]):  # Export first 2 charts
        for config in export_configs:
            try:
                output_path = exporter.export_chart(figure, metadata, config)
                exported_files.append(output_path)
                print(f"   📄 Exported {config.format.upper()}: {Path(output_path).name}")
            except Exception as e:
                print(f"   ❌ Failed to export {config.format}: {e}")

    # Create executive report
    try:
        from plotxy.enterprise.exports import ReportSection
        sections = [
            ReportSection(
                title="Executive Summary",
                content_type="text",
                content="This report presents key performance indicators and financial analysis for Q4 2024."
            )
        ]

        # Add chart sections
        for figure, metadata in charts_with_metadata[:2]:
            sections.append(ReportSection(
                title=metadata.title,
                content_type="chart",
                content=figure,
                description=f"Generated on {metadata.created_at.strftime('%Y-%m-%d')}"
            ))

        report_path = exporter.create_executive_report(sections, "Q4 Enterprise Report", "html")
        print(f"   📊 Created executive report: {Path(report_path).name}")
        exported_files.append(report_path)

    except Exception as e:
        print(f"   ❌ Failed to create executive report: {e}")

    print(f"   ✅ Successfully exported {len(exported_files)} files")
    return exported_files


def main():
    """Run enterprise chart demo."""
    print("🚀 PlotX Enterprise Chart Enhancements Demo")
    print("=" * 50)

    charts_with_metadata = []

    try:
        # Demo enterprise chart types
        charts_with_metadata.extend([
            demo_executive_dashboard(),
            demo_financial_analytics(),
            demo_compliance_chart(),
            demo_risk_analysis()
        ])

        # Demo themes
        themed_charts = demo_themes()
        print(f"📊 Created {len(themed_charts)} themed demonstration charts")

        # Demo exports
        exported_files = demo_exports(charts_with_metadata)

        # Summary
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print(f"✅ Created {len(charts_with_metadata)} enterprise charts")
        print(f"✅ Demonstrated 4 theme variations")
        print(f"✅ Exported {len(exported_files)} files")

        print(f"\n📁 Output directory: {Path(exported_files[0]).parent if exported_files else 'No exports'}")

        # Show enterprise features
        print("\n🔐 Enterprise Features Demonstrated:")
        print("• Executive KPI dashboards with status indicators")
        print("• Financial waterfall and variance analysis")
        print("• Compliance scorecards with traffic lights")
        print("• Risk probability vs impact matrices")
        print("• Professional themes with corporate branding")
        print("• Accessibility features (colorblind-friendly palettes)")
        print("• Security classification and audit trails")
        print("• Multi-format exports (PDF, PNG, HTML, JSON)")
        print("• Branded reports with metadata")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())