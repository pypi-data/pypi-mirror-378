"""
Advanced tests for the TracebackParser, including context extraction and edge cases.
"""

from pathlib import Path
import tempfile

import pytest

from tattletail.parser import TracebackParser

from .fixtures.basic_tracebacks import CONNECTION_ERROR_MULTI_COLONS
from .fixtures.basic_tracebacks import CONTEXT_DISABLED
from .fixtures.basic_tracebacks import CONTEXT_EXTRACTION_TEMPLATE
from .fixtures.basic_tracebacks import CONTEXT_NONEXISTENT_FILE
from .fixtures.basic_tracebacks import EXCEPTION_ONLY
from .fixtures.basic_tracebacks import FRAME_NO_FUNCTION
from .fixtures.basic_tracebacks import LONG_PATH_TEMPLATE
from .fixtures.basic_tracebacks import SPECIAL_CHARACTERS
from .fixtures.basic_tracebacks import VALUE_ERROR_NO_MESSAGE
from .fixtures.complex_tracebacks import COMPLEX_CHAINED_EXCEPTIONS
from .fixtures.complex_tracebacks import UNICODE_TRACEBACK
from .fixtures.edge_case_tracebacks import EMPTY_TRACEBACK
from .fixtures.edge_case_tracebacks import EXCEPTION_LINES_TEST_CASES
from .fixtures.edge_case_tracebacks import MALFORMED_TRACEBACK
from .fixtures.edge_case_tracebacks import NON_EXCEPTION_LINES_TEST_CASES
from .fixtures.edge_case_tracebacks import RESET_TEST_EXCEPTION


class TestContextExtraction:
    """Test context extraction functionality."""

    def test_context_extraction_with_file(self):
        """Test context extraction from an actual file."""
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            content = """def hello():
    print("Hello")
    x = 1
    y = 2  # This is line 4
    z = x + y
    return z

def main():
    result = hello()
    print(result)
"""
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            # Create a traceback that references the temp file
            traceback_text = CONTEXT_EXTRACTION_TEMPLATE.format(temp_path=temp_path)

            parser = TracebackParser(extract_context=True)
            parsed = parser.parse(traceback_text)

            assert len(parsed.stack_frames) == 1
            frame = parsed.stack_frames[0]

            # Should have context lines
            assert frame.context_lines is not None
            assert len(frame.context_lines) > 0

            # Find the error line in context
            error_line = None
            for ctx in frame.context_lines:
                if ctx.is_error_line:
                    error_line = ctx
                    break

            assert error_line is not None
            assert error_line.line_number == 4
            assert "y = 2" in error_line.code

        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_context_extraction_nonexistent_file(self):
        """Test context extraction with non-existent file."""
        parser = TracebackParser(extract_context=True)
        parsed = parser.parse(CONTEXT_NONEXISTENT_FILE)

        frame = parsed.stack_frames[0]
        # Should handle missing file gracefully
        assert frame.context_lines is None or len(frame.context_lines) == 0

    def test_context_extraction_disabled(self):
        """Test that context extraction can be disabled."""
        parser = TracebackParser(extract_context=False)
        parsed = parser.parse(CONTEXT_DISABLED)

        frame = parsed.stack_frames[0]
        assert frame.context_lines == []

    def test_context_size_parameter(self):
        """Test custom context size."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            content = "\n".join([f"line_{i}" for i in range(1, 21)])  # 20 lines
            f.write(content)
            f.flush()
            temp_path = f.name

        try:
            parser = TracebackParser(extract_context=True)
            # Manually test the _extract_context method with custom size
            context = parser._extract_context(temp_path, 10, context_size=2)

            assert context is not None
            # Should have 2 lines before + error line + 2 lines after = 5 total
            assert len(context) == 5

            # Check that line 10 is marked as error line
            error_line = next(ctx for ctx in context if ctx.is_error_line)
            assert error_line.line_number == 10

        finally:
            Path(temp_path).unlink()


class TestParseFromException:
    """Test parsing from exception objects."""

    def test_parse_from_exception_with_exc_info(self):
        """Test parsing from exception info tuple."""
        parser = TracebackParser()

        try:
            raise ValueError("Test exception for parsing")
        except Exception:
            import sys

            exc_info = sys.exc_info()
            parsed = parser.parse_from_exception(exc_info)

            assert parsed.exception.exception_type == "ValueError"
            assert "Test exception for parsing" in parsed.exception.exception_message
            assert len(parsed.stack_frames) > 0

    def test_parse_from_exception_auto_exc_info(self):
        """Test parsing from exception with automatic exc_info()."""
        parser = TracebackParser()

        try:
            raise RuntimeError("Auto exc_info test")
        except Exception:
            parsed = parser.parse_from_exception()

            assert parsed.exception.exception_type == "RuntimeError"
            assert "Auto exc_info test" in parsed.exception.exception_message

    def test_parse_from_exception_no_active_exception(self):
        """Test parsing when no exception is active."""
        parser = TracebackParser()

        with pytest.raises(ValueError, match="No active exception"):
            parser.parse_from_exception()

    def test_parse_from_exception_none_exc_info(self):
        """Test parsing with None exc_info."""
        parser = TracebackParser()

        with pytest.raises(ValueError, match="No active exception"):
            parser.parse_from_exception((None, None, None))


class TestEdgeCases:
    """Test edge cases and malformed tracebacks."""

    def test_empty_traceback(self):
        """Test parsing empty traceback."""
        parser = TracebackParser()
        parsed = parser.parse(EMPTY_TRACEBACK)

        assert parsed.exception.exception_type == "UnknownError"
        assert "Could not parse" in parsed.exception.exception_message
        assert len(parsed.stack_frames) == 0

    def test_malformed_traceback(self):
        """Test parsing malformed traceback."""
        parser = TracebackParser()
        parsed = parser.parse(MALFORMED_TRACEBACK)

        # Should still return a result, even if not perfect
        assert parsed.exception is not None

    def test_traceback_without_frames(self):
        """Test traceback with just exception line."""
        parser = TracebackParser()
        parsed = parser.parse(EXCEPTION_ONLY)

        assert parsed.exception.exception_type == "ValueError"
        assert parsed.exception.exception_message == "Something went wrong"
        assert len(parsed.stack_frames) == 0

    def test_exception_without_message(self):
        """Test exception line without message."""
        parser = TracebackParser()
        parsed = parser.parse(VALUE_ERROR_NO_MESSAGE)

        assert parsed.exception.exception_type == "ValueError"
        assert parsed.exception.exception_message == ""

    def test_frame_without_function_name(self):
        """Test frame line without function name."""
        parser = TracebackParser()
        parsed = parser.parse(FRAME_NO_FUNCTION)

        frame = parsed.stack_frames[0]
        assert frame.function_name == "<module>"  # Default value

    def test_complex_chained_exceptions(self):
        """Test complex chained exception scenario."""
        parser = TracebackParser()
        parsed = parser.parse(COMPLEX_CHAINED_EXCEPTIONS)

        # Should parse the final exception
        assert parsed.exception.exception_type == "FinalError"
        assert parsed.exception.exception_message == "Final error"

        # Should have cause chain - the parser processes them in order,
        # so first exception becomes the cause
        assert parsed.exception.cause is not None
        assert parsed.exception.cause.exception_type == "ValueError"

    def test_unicode_in_traceback(self):
        """Test traceback with unicode characters."""
        parser = TracebackParser()
        parsed = parser.parse(UNICODE_TRACEBACK)

        assert parsed.exception.exception_type == "ValueError"
        assert "こんにちは" in parsed.exception.exception_message
        assert parsed.stack_frames[0].function_name == "测试函数"
        assert "tëst.py" in parsed.stack_frames[0].file_path

    def test_very_long_paths(self):
        """Test with very long file paths."""
        long_path = "/very/long/path/" + "directory/" * 20 + "file.py"
        traceback_text = LONG_PATH_TEMPLATE.format(long_path=long_path)

        parser = TracebackParser()
        parsed = parser.parse(traceback_text)

        assert parsed.stack_frames[0].file_path == long_path

    def test_special_characters_in_code(self):
        """Test with special characters in code lines."""
        parser = TracebackParser()
        parsed = parser.parse(SPECIAL_CHARACTERS)

        frame = parsed.stack_frames[0]
        assert frame.code_line is not None
        assert "HelloWorld" in frame.code_line

    def test_multiple_colons_in_exception_message(self):
        """Test exception message with multiple colons."""
        parser = TracebackParser()
        parsed = parser.parse(CONNECTION_ERROR_MULTI_COLONS)

        assert parsed.exception.exception_type == "ConnectionError"
        expected_msg = "Failed to connect to server: connection timeout: 30s"
        assert parsed.exception.exception_message == expected_msg


class TestParserInternals:
    """Test internal parser methods."""

    def test_is_exception_line_various_cases(self):
        """Test _is_exception_line method with various inputs."""
        parser = TracebackParser()

        # Should be exception lines
        for line in EXCEPTION_LINES_TEST_CASES:
            assert parser._is_exception_line(line)

        # Should NOT be exception lines
        for line in NON_EXCEPTION_LINES_TEST_CASES:
            assert not parser._is_exception_line(line)

    def test_reset_functionality(self):
        """Test parser reset functionality."""
        parser = TracebackParser()

        # Parse something first
        parser.parse(RESET_TEST_EXCEPTION)

        # Verify state is populated
        assert parser.current_exception is not None

        # Reset and verify state is cleared
        parser.reset()
        assert parser.current_exception is None
        assert len(parser.current_frames) == 0
        assert len(parser.raw_lines) == 0
        assert len(parser.chained_exceptions) == 0
