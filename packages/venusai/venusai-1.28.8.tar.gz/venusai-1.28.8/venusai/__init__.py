"""
Alias package for `venai`.
"""
try:
    from venus import *
except ImportError:
    pass

import warnings

warnings.warn(
    "Install `venai` instead of this package.",
    ImportWarning
)