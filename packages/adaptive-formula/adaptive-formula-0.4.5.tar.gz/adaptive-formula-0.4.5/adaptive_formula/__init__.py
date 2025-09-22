"""
Adaptive Formula SDK - Cognitive Programming Infrastructure
Version 0.4.4
"""

# Try imports in order: Cython → Python fallback → API
try:
    from .core import CognitiveSDK, Field
    _BACKEND = "Cython (Optimized)"
except ImportError:
    try:
        from .core_py import CognitiveSDK, Field
        _BACKEND = "Pure Python"
    except ImportError:
        from .api import CognitiveSDK, Field
        _BACKEND = "API"

__version__ = "0.4.5"
__all__ = ["CognitiveSDK", "Field", "__version__", "get_backend"]

def get_backend():
    """Returns which backend implementation is being used"""
    return _BACKEND

# Optional compatibility imports
try:
    from .models import FieldConfig, LicenseTier
    __all__.extend(["FieldConfig", "LicenseTier"])
except ImportError:
    pass