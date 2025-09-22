"""
Alias package for `venai`.
"""

try:
    import venus.agent as agent
    import venus.caching as caching
    import venus.constants as constants
    import venus.decorators as decorators
    import venus.errors as errors
    import venus.helpers as helpers
    import venus.logger as logger
    import venus.mcp_server as mcp_server
    import venus.mock_types as mock_types
    import venus.models as models
    import venus.permissions as permissions
    import venus.prompts as prompts
    import venus.schemas as schemas
    import venus.settings as settings
    import venus.types as types
    from venus import *

except ImportError:
    pass

import warnings

warnings.warn("Install `venai` instead of this package.", ImportWarning)
