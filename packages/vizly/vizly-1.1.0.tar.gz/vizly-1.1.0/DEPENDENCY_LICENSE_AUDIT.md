# Vizly External Dependencies License Audit

**Audit Date:** December 2024
**Status:** ✅ ALL DEPENDENCIES ARE OPEN SOURCE
**Risk Level:** 🟢 LOW RISK - No commercial licenses found

## Executive Summary

All external dependencies used by Vizly are distributed under permissive open source licenses. No commercial, proprietary, or restrictive licenses were found. The project is safe for both commercial and non-commercial use.

## Core Dependencies Analysis

### Required Dependencies (install_requires)

| Library | Version | License | Status | Risk |
|---------|---------|---------|---------|------|
| **numpy** | ≥1.19.0 | BSD-3-Clause | ✅ Open Source | 🟢 None |
| **matplotlib** | ≥3.7.0 | BSD-compatible (PSF-based) | ✅ Open Source | 🟢 None |
| **tornado** | ≥6.0.0 | Apache 2.0 | ✅ Open Source | 🟢 None |
| **jupyter** | ≥1.0.0 | BSD-3-Clause | ✅ Open Source | 🟢 None |
| **ipywidgets** | ≥7.0.0 | BSD-3-Clause | ✅ Open Source | 🟢 None |

### Optional Dependencies (extras_require)

#### Development Tools
| Library | Version | License | Status | Risk |
|---------|---------|---------|---------|------|
| **pytest** | ≥6.0.0 | MIT | ✅ Open Source | 🟢 None |
| **pytest-cov** | ≥2.10.0 | MIT | ✅ Open Source | 🟢 None |
| **black** | ≥21.0.0 | MIT | ✅ Open Source | 🟢 None |
| **flake8** | ≥3.8.0 | MIT | ✅ Open Source | 🟢 None |
| **mypy** | ≥0.800 | MIT | ✅ Open Source | 🟢 None |

#### Code Dependencies (Found in Source)
| Library | License | Status | Usage | Risk |
|---------|---------|---------|--------|------|
| **scipy** | BSD-3-Clause | ✅ Open Source | Scientific computing | 🟢 None |
| **plotly** | MIT | ✅ Open Source | Alternative plotting (optional) | 🟢 None |
| **cryptography** | Apache-2.0 OR BSD-3-Clause | ✅ Open Source | Security features | 🟢 None |
| **PyJWT** | MIT | ✅ Open Source | Authentication tokens | 🟢 None |
| **requests** | Apache-2.0 | ✅ Open Source | HTTP client | 🟢 None |

## License Compatibility Matrix

All licenses are compatible with each other and with MIT licensing:

| License Type | Compatible with MIT | Commercial Use | Distribution | Modification |
|--------------|-------------------|----------------|--------------|--------------|
| **MIT** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **BSD-3-Clause** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Apache-2.0** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

## Detailed License Information

### 1. NumPy (BSD-3-Clause)
- **Type:** Permissive open source
- **Rights:** Commercial use, modification, distribution, private use
- **Obligations:** Include license and copyright notice

### 2. Matplotlib (BSD-compatible)
- **Type:** Permissive open source (Python Software Foundation based)
- **Rights:** Commercial use, modification, distribution, private use
- **Obligations:** Include license and copyright notice
- **Note:** Specifically designed for broad compatibility

### 3. SciPy (BSD-3-Clause)
- **Type:** Permissive open source
- **Rights:** Commercial use, modification, distribution, private use
- **Obligations:** Include license and copyright notice

### 4. Tornado (Apache-2.0)
- **Type:** Permissive open source
- **Rights:** Commercial use, modification, distribution, private use, patent grant
- **Obligations:** Include license, copyright notice, and changes

### 5. Jupyter Ecosystem (BSD-3-Clause)
- **Type:** Permissive open source
- **Rights:** Commercial use, modification, distribution, private use
- **Obligations:** Include license and copyright notice

### 6. Plotly (MIT)
- **Type:** Highly permissive open source
- **Rights:** Commercial use, modification, distribution, private use
- **Obligations:** Include license and copyright notice only

### 7. Cryptography (Apache-2.0 OR BSD-3-Clause)
- **Type:** Dual license - user can choose either
- **Rights:** Commercial use, modification, distribution, private use
- **Obligations:** Include chosen license and copyright notice

### 8. PyJWT (MIT)
- **Type:** Highly permissive open source
- **Rights:** Commercial use, modification, distribution, private use
- **Obligations:** Include license and copyright notice only

## Risk Assessment

### 🟢 **NO COMMERCIAL LICENSE RISKS IDENTIFIED**

1. **No Copyleft Licenses:** No GPL, LGPL, or other viral licenses found
2. **No Proprietary Licenses:** No commercial or closed-source dependencies
3. **No Export Restrictions:** No ITAR or export-controlled libraries
4. **No Patent Issues:** All licenses include appropriate patent grants where needed

### Compliance Requirements

**Minimal obligations across all dependencies:**
1. Include original license notices in distributions
2. Include copyright notices
3. For Apache-licensed components: Include NOTICE file if changes made

## Recommendations

### ✅ **APPROVED FOR ALL USE CASES**

The dependency stack is **fully compliant** for:
- ✅ Commercial use
- ✅ Private/internal use
- ✅ Open source redistribution
- ✅ Proprietary software integration
- ✅ SaaS/cloud deployments
- ✅ Enterprise deployments

### 🔧 **MAINTENANCE RECOMMENDATIONS**

1. **Monitor License Changes:** Set up automated license scanning in CI/CD
2. **Document Compliance:** Include all license notices in releases
3. **Regular Audits:** Re-audit dependencies quarterly
4. **Version Pinning:** Consider pinning major versions to avoid license changes

## License Notice Template

For distribution, include this notice:

```
This software includes the following open source components:

- NumPy (BSD-3-Clause License)
- Matplotlib (BSD-compatible License)
- SciPy (BSD-3-Clause License)
- Tornado (Apache-2.0 License)
- Jupyter (BSD-3-Clause License)
- Plotly (MIT License)
- Cryptography (Apache-2.0 OR BSD-3-Clause License)
- PyJWT (MIT License)

Full license texts are available in the LICENSES/ directory.
```

---

**Audit Conclusion:** ✅ Vizly's dependency stack is **100% open source** with no commercial licensing restrictions.