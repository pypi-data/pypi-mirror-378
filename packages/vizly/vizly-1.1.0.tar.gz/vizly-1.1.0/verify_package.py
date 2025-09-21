#!/usr/bin/env python3
"""
Vizly Package Verification Script
================================

Comprehensive verification that Vizly is ready for PyPI upload.
"""

import subprocess
import sys
import importlib
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description}: PASSED")
            return True
        else:
            print(f"❌ {description}: FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False

def verify_package():
    """Verify the Vizly package is ready for PyPI."""
    print("🚀 Vizly PyPI Readiness Verification")
    print("=" * 50)

    checks = []

    # 1. Check build files exist
    dist_path = Path("dist")
    wheel_file = dist_path / "vizly-1.0.0-py3-none-any.whl"
    tarball_file = dist_path / "vizly-1.0.0.tar.gz"

    if wheel_file.exists() and tarball_file.exists():
        print("✅ Distribution files exist")
        print(f"   - Wheel: {wheel_file} ({wheel_file.stat().st_size / 1024:.1f} KB)")
        print(f"   - Tarball: {tarball_file} ({tarball_file.stat().st_size / (1024*1024):.1f} MB)")
        checks.append(True)
    else:
        print("❌ Distribution files missing")
        checks.append(False)

    # 2. Twine check
    checks.append(run_command("twine check dist/vizly-1.0.0*", "Twine package validation"))

    # 3. Import test
    print("🔍 Testing package import...")
    try:
        import vizly
        print(f"✅ Package import: PASSED (v{vizly.__version__})")
        checks.append(True)
    except Exception as e:
        print(f"❌ Package import: FAILED - {e}")
        checks.append(False)

    # 4. Core functionality test
    print("🔍 Testing core functionality...")
    try:
        import vizly
        import numpy as np

        # Test LineChart
        x = np.linspace(0, 5, 10)
        y = np.sin(x)
        chart = vizly.LineChart()
        chart.plot(x, y, color='blue')

        # Test ScatterChart
        scatter = vizly.ScatterChart()
        scatter.scatter(np.random.randn(20), np.random.randn(20))

        # Test BarChart
        bar = vizly.BarChart()
        bar.bar(['A', 'B', 'C'], [1, 2, 3], color='skyblue')

        print("✅ Core functionality: PASSED")
        checks.append(True)
    except Exception as e:
        print(f"❌ Core functionality: FAILED - {e}")
        checks.append(False)

    # 5. Advanced modules test
    print("🔍 Testing advanced modules...")
    advanced_checks = []

    try:
        import vizly.gpu as vgpu
        backend = vgpu.get_best_backend()
        print(f"✅ GPU module: {backend.device_info.get('backend', 'Unknown')}")
        advanced_checks.append(True)
    except Exception as e:
        print(f"⚠️ GPU module: {e}")
        advanced_checks.append(False)

    try:
        import vizly.vr as vr
        session = vr.WebXRSession()
        print("✅ VR/AR module")
        advanced_checks.append(True)
    except Exception as e:
        print(f"⚠️ VR/AR module: {e}")
        advanced_checks.append(False)

    try:
        import vizly.interaction3d as i3d
        manager = i3d.Scene3DManager()
        print("✅ 3D interaction module")
        advanced_checks.append(True)
    except Exception as e:
        print(f"⚠️ 3D module: {e}")
        advanced_checks.append(False)

    # Summary
    print("\n📊 Verification Summary")
    print("-" * 30)

    core_passed = sum(checks)
    advanced_passed = sum(advanced_checks)

    print(f"Core checks: {core_passed}/{len(checks)} passed")
    print(f"Advanced modules: {advanced_passed}/{len(advanced_checks)} passed")

    if core_passed == len(checks):
        print("\n🎉 PACKAGE READY FOR PYPI!")
        print("✅ All core functionality verified")
        print("📦 Distribution files validated")
        print("🚀 Ready to upload with: twine upload dist/vizly-1.0.0*")

        if advanced_passed >= 2:
            print("✨ Advanced features working well")

        print("\n📞 Commercial License Contact: durai@infinidatum.net")
        return True
    else:
        print("\n❌ PACKAGE NOT READY")
        print("Fix the failing checks before uploading")
        return False

if __name__ == "__main__":
    success = verify_package()
    sys.exit(0 if success else 1)