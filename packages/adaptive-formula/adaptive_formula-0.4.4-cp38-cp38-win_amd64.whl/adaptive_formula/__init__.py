"""
Adaptive Formula SDK - Cognitive Programming Infrastructure
Version 0.4.4
"""

import warnings

# Try to import optimized Cython version first
_USING_CYTHON = False

try:
    # Try Cython-compiled version
    from .core import CognitiveSDK, Field, AdaptiveFormula
    _USING_CYTHON = True
except ImportError:
    try:
        # Fallback to pure Python version
        from .core_py import CognitiveSDK, Field, AdaptiveFormula
        _USING_CYTHON = False
    except ImportError:
        # If that fails too, try api.py (your existing structure)
        try:
            from .api import CognitiveSDK, Field
            _USING_CYTHON = False
        except ImportError:
            raise ImportError(
                "Could not import adaptive_formula core. "
                "Please reinstall the package: pip install --upgrade adaptive-formula"
            )

# Version info
__version__ = "0.4.4"

# Public API
__all__ = ["CognitiveSDK", "Field", "__version__"]

# Optional: Function to check which backend is being used
def get_backend():
    """Returns the backend being used (Cython or Pure Python)"""
    return "Cython (Optimized)" if _USING_CYTHON else "Pure Python"

# Compatibility imports (if needed)
try:
    from .models import FieldConfig, LicenseTier
    __all__.extend(["FieldConfig", "LicenseTier"])
except ImportError:
    pass