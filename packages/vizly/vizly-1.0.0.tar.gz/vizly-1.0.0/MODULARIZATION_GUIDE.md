# Vizly Modularization Guide

This document explains how Vizly has been modularized to prevent conflicts with external PyPI libraries, particularly the `plotxy` package.

## 🔐 Isolation Strategy

### Problem
The original codebase was named "plotxy" which conflicts with an existing PyPI package of the same name. If users install both packages, it can lead to:
- Import conflicts
- Unexpected behavior
- Breaking changes when the external plotxy package updates

### Solution
Vizly implements a comprehensive isolation strategy:

1. **Complete Rebranding**: All references changed from plotxy/PlotX to vizly/Vizly
2. **Import Protection**: Built-in warnings for accidental plotxy imports
3. **Dependency Isolation**: Clear separation of dependencies
4. **Virtual Environment Recommendations**: Best practices for development

## 🛡️ Isolation Features

### Automatic Import Protection
```python
import vizly  # Automatically enables import protection

# This will trigger a warning:
import plotxy  # ⚠️ Warning: May conflict with Vizly
```

### Manual Control
```python
from vizly.vizly_isolation_config import (
    enable_vizly_isolation,
    disable_vizly_isolation,
    check_vizly_isolation
)

# Enable protection
enable_vizly_isolation()

# Check status
check_vizly_isolation()

# Disable if needed (for testing)
disable_vizly_isolation()
```

### Environment Variable Control
```bash
# Disable isolation completely
export VIZLY_DISABLE_ISOLATION=1
python -c "import vizly"  # No warnings

# Re-enable (default)
export VIZLY_DISABLE_ISOLATION=0
python -c "import vizly"  # Warnings enabled
```

## 📋 Best Practices

### For Users
1. **Always use `vizly` imports**:
   ```python
   import vizly                    # ✅ Correct
   from vizly import LineChart     # ✅ Correct

   import plotxy                   # ❌ Avoid - may conflict
   ```

2. **Use virtual environments**:
   ```bash
   python -m venv vizly-env
   source vizly-env/bin/activate
   pip install vizly
   ```

3. **Pin versions in requirements.txt**:
   ```txt
   vizly==1.0.7
   # plotxy  # Explicitly avoid
   ```

### For Developers
1. **Check isolation status**:
   ```python
   from vizly.vizly_isolation_config import check_vizly_isolation
   check_vizly_isolation()
   ```

2. **Test with different environments**:
   ```bash
   # Test with isolation enabled
   python test_script.py

   # Test with isolation disabled
   VIZLY_DISABLE_ISOLATION=1 python test_script.py
   ```

## 🔧 Technical Implementation

### Files Changed
- **Package Structure**: `src/plotxy/` → `src/vizly/`
- **Class Names**: `PlotXFigure` → `VizlyFigure`, `PlotXTheme` → `VizlyTheme`
- **Configuration**: `setup.py`, `pyproject.toml` updated
- **Examples**: All example files use `vizly` imports
- **Documentation**: Updated to reflect new naming

### New Files Added
- `src/vizly/vizly_isolation_config.py` - Isolation management
- `requirements.txt` - Clear dependency specification
- `requirements-dev.txt` - Development dependencies
- `MODULARIZATION_GUIDE.md` - This guide

## 🚀 Migration from plotxy

If you have existing code using plotxy, here's how to migrate:

### 1. Update Imports
```python
# Old
import plotxy
from plotxy.charts import LineChart
from plotxy.figure import PlotXFigure

# New
import vizly
from vizly.charts import LineChart
from vizly.figure import VizlyFigure
```

### 2. Update Class Names
```python
# Old
fig = PlotXFigure()
theme = PlotXTheme()

# New
fig = VizlyFigure()
theme = VizlyTheme()
```

### 3. Update Dependencies
```bash
# Remove old package
pip uninstall plotxy

# Install new package
pip install vizly
```

## 🔍 Conflict Detection

Vizly automatically detects potential conflicts and provides recommendations:

```python
🔒 Vizly Isolation Report
========================================
Vizly Version: 1.0.7
Isolation Enabled: True
✅ No conflicts detected

📋 Recommendations:
   - Always use 'import vizly' instead of 'import plotxy'
   - Update legacy code to use vizly imports
   - Pin vizly version in requirements.txt
```

## 🆘 Troubleshooting

### Import Warnings
If you see plotxy import warnings:
1. Update your imports to use `vizly`
2. Check for transitive dependencies importing plotxy
3. Consider using virtual environments

### Disable Warnings Temporarily
```python
from vizly.vizly_isolation_config import disable_vizly_isolation
disable_vizly_isolation()
# Your code here
```

### Check Installation
```bash
pip list | grep -E "(vizly|plotxy)"
python -c "import vizly; vizly.demo()"
```

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Run `python -c "from vizly.vizly_isolation_config import check_vizly_isolation; check_vizly_isolation()"`
3. Create an issue with the isolation report output

## 🔮 Future-Proofing

This modularization ensures:
- ✅ No conflicts with external plotxy packages
- ✅ Stable API regardless of external library changes
- ✅ Clear dependency management
- ✅ Easy migration path for existing users
- ✅ Professional library structure

The isolation system is designed to be non-intrusive but protective, warning users about potential conflicts while allowing flexibility for advanced use cases.