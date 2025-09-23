"""
API Validator SDK - Intelligent API Request Validation
Version 1.0.0
"""

# Try imports: Cython -> Python fallback
try:
    from .core import Field, AdaptiveFormula
    _BACKEND = "Cython (Optimized)"
except ImportError:
    from .core_py import Field, AdaptiveFormula
    _BACKEND = "Pure Python"

from .validator import APIValidator
from .fields import (
    AUTH_FIELDS, 
    RATE_LIMIT_FIELDS, 
    SECURITY_FIELDS,
    PAYLOAD_FIELDS,
    get_standard_fields
)
from .models import (
    ValidationResult,
    RequestMetrics,
    ValidationConfig
)

__version__ = "1.0.0"
__all__ = [
    'APIValidator',
    'Field',
    'ValidationResult',
    'RequestMetrics',
    'ValidationConfig',
    'AUTH_FIELDS',
    'RATE_LIMIT_FIELDS',
    'SECURITY_FIELDS',
    'PAYLOAD_FIELDS',
    'get_standard_fields'
]

def get_backend():
    """Returns which backend is being used"""
    return _BACKEND