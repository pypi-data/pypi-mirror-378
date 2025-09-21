"""
Central traceback fixtures index for backward compatibility.

This file provides imports from organized fixture files to maintain
compatibility with existing test code while enabling better organization.

Organized fixture files:
- basic_tracebacks.py: Simple single exception scenarios
- complex_tracebacks.py: Chained exceptions, recursion, unicode
- analyzer_tracebacks.py: For analysis testing
- performance_tracebacks.py: Large tracebacks for performance testing
- edge_case_tracebacks.py: Malformed and edge case scenarios
"""

# Import core fixtures for backward compatibility
from .basic_tracebacks import SIMPLE_TRACEBACK
from .complex_tracebacks import CHAINED_TRACEBACK


# Re-export for backward compatibility
__all__ = [
    "SIMPLE_TRACEBACK",
    "CHAINED_TRACEBACK",
]
