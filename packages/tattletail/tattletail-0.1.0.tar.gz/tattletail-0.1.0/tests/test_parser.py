"""
Tests for the TracebackParser.
"""

from tattletail.parser import TracebackParser

from .fixtures.basic_tracebacks import SIMPLE_TRACEBACK
from .fixtures.complex_tracebacks import CHAINED_TRACEBACK


def test_parse_simple_traceback():
    """Test parsing a simple traceback."""
    parser = TracebackParser()
    parsed = parser.parse(SIMPLE_TRACEBACK)

    assert parsed.exception.exception_type == "ValueError"
    assert (
        parsed.exception.exception_message
        == "invalid literal for int() with base 10: 'abc'"
    )
    assert len(parsed.stack_frames) == 4

    last_frame = parsed.get_error_location()
    assert last_frame is not None
    assert last_frame.file_path == "/home/user/project/utils.py"
    assert last_frame.line_number == 78
    assert last_frame.function_name == "<listcomp>"


def test_parse_chained_traceback():
    """Test parsing a traceback with chained exceptions."""
    parser = TracebackParser()
    parsed = parser.parse(CHAINED_TRACEBACK)

    assert parsed.exception.exception_type == "RuntimeError"
    assert parsed.exception.exception_message == "Something went wrong"
    assert parsed.exception.cause is not None
    assert parsed.exception.cause.exception_type == "ValueError"
    assert parsed.exception.cause.exception_message == "level2 error"
    assert len(parsed.stack_frames) == 6

    last_frame = parsed.get_error_location()
    assert last_frame is not None
    assert last_frame.file_path == "/home/user/project/main.py"
    assert last_frame.line_number == 7
    assert last_frame.function_name == "main"
