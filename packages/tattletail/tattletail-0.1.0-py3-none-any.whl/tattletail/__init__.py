"""
Modern Traceback Parsing and Analysis for Python.

Tattletail is a Python library that provides tools to parse, analyze, and
generate insightful reports from Python tracebacks. It is designed to be
lightweight, have zero third-party dependencies, and offer a modern,
type-hinted API with elegant context manager support.

Main Functions:
---------------
- `parse()`: Parses a raw traceback string into a structured `ParsedTraceback` object.
- `parse_from_exception()`: Parses live exceptions with optimized performance.
- `analyze()`: Provides high-level analysis of a traceback string, including
  probable causes and pattern detection.
- `generate_report()`: Creates a detailed, human-readable report from a traceback.

Context Managers:
-----------------
- `capture()`: Automatically capture and analyze exceptions in a 'with' block.
- `expect()`: Test that specific exceptions occur (great for unit tests).
- `monitor()`: Production monitoring with automatic logging integration.

Examples
--------
# Basic usage
parsed = tattletail.parse(traceback_string)
analysis = tattletail.analyze(traceback_string)

# Context manager for elegant exception handling
with tattletail.capture() as ctx:
    risky_operation()
if ctx.exception:
    print(ctx.analysis['probable_cause'])

# Testing expected exceptions
with tattletail.expect(ValueError) as ctx:
    int("invalid")
assert ctx.matched

# Production monitoring
with tattletail.monitor(logger=my_logger):
    process_user_request()

"""

__version__ = "0.1.0"  # TODO: This will be managed by bump2version


from typing import Any

from .analyzer import TracebackAnalyzer
from .context import ErrorCapture as ErrorCapture
from .context import ErrorExpector as ErrorExpector
from .context import ErrorMonitor as ErrorMonitor

# Context manager functionality
from .context import capture as capture
from .context import expect as expect
from .context import monitor as monitor
from .models import ParsedTraceback
from .parser import TracebackParser


def parse(traceback_text: str, extract_context: bool = False) -> ParsedTraceback:
    """
    Parse a raw traceback string into a structured `ParsedTraceback` object.

    This is the main entry point for parsing a traceback from a string.

    Parameters
    ----------
    traceback_text : str
        The raw traceback string to parse.
    extract_context : bool, optional
        If True, extracts lines of source code around the error line.
        Defaults to False.

    Returns
    -------
    ParsedTraceback
        A structured object representing the parsed traceback.
    """
    parser = TracebackParser(extract_context=extract_context)
    return parser.parse(traceback_text)


def parse_from_exception(
    exc_info: tuple | None = None, extract_context: bool = False
) -> ParsedTraceback:
    """
    Parse a traceback directly from an exception or `sys.exc_info()`.

    Should be called from within an `except` block.

    Parameters
    ----------
    exc_info : tuple, optional
        A tuple of (type, value, traceback) from `sys.exc_info()`. If None,
        `sys.exc_info()` is called automatically. Defaults to None.
    extract_context : bool, optional
        If True, extracts lines of source code around the error line.
        Defaults to False.

    Returns
    -------
    ParsedTraceback
        A structured object representing the parsed traceback.
    """
    parser = TracebackParser(extract_context=extract_context)
    return parser.parse_from_exception(exc_info)


def analyze(traceback_text: str) -> dict[str, Any]:
    """
    Perform a high-level analysis of a traceback string.

    Returns a dictionary with insights like severity, probable cause, and
    debugging suggestions.

    Parameters
    ----------
    traceback_text : str
        The raw traceback string to analyze.

    Returns
    -------
    dict[str, any]
        A dictionary containing the analysis results.
    """
    analyzer = TracebackAnalyzer()
    return analyzer.analyze(traceback_text)


def generate_report(traceback_text: str) -> str:
    """
    Generate a detailed, human-readable report from a traceback string.

    Parameters
    ----------
    traceback_text : str
        The raw traceback string.

    Returns
    -------
    str
        A formatted report string.
    """
    analyzer = TracebackAnalyzer()
    return analyzer.generate_report(traceback_text)
