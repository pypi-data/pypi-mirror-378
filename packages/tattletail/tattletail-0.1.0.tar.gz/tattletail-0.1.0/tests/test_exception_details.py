"""Tests for the new exception details extraction functionality."""

from tattletail.analyzer import TracebackAnalyzer
from tattletail.parser import TracebackParser
from tests.fixtures import exception_details_tracebacks as fixtures  # type: ignore


class TestExceptionDetails:
    """Test extraction of detailed exception information."""

    def test_exception_details_basic(self):
        """Test basic exception details extraction."""
        analyzer = TracebackAnalyzer()
        analysis = analyzer.analyze(fixtures.ZERO_DIVISION_ERROR)

        exception_details = analysis["exception"]

        assert exception_details["class"] == "ZeroDivisionError"
        assert exception_details["name"] == "ZeroDivisionError"
        assert exception_details["message"] == "division by zero"
        assert exception_details["module"] is None
        assert exception_details["full_name"] == "ZeroDivisionError"
        assert exception_details["line_number"] == 10
        assert exception_details["file_path"] == "test.py"
        assert exception_details["function_name"] == "main"
        assert exception_details["has_cause"] is False
        assert exception_details["has_context"] is False

    def test_exception_hierarchy_builtin(self):
        """Test exception hierarchy for built-in exceptions."""
        analyzer = TracebackAnalyzer()
        analysis = analyzer.analyze(fixtures.INDEX_ERROR)

        exception_details = analysis["exception"]
        hierarchy = exception_details["hierarchy"]

        expected_hierarchy = ["BaseException", "Exception", "LookupError", "IndexError"]
        assert hierarchy == expected_hierarchy

    def test_exception_hierarchy_unknown(self):
        """Test exception hierarchy for unknown exceptions."""
        analyzer = TracebackAnalyzer()
        analysis = analyzer.analyze(fixtures.CUSTOM_ERROR)

        exception_details = analysis["exception"]
        hierarchy = exception_details["hierarchy"]

        expected_hierarchy = ["BaseException", "Exception", "CustomError"]
        assert hierarchy == expected_hierarchy

    def test_exception_details_with_module(self):
        """Test exception details when exception has module information."""
        # Create a parsed traceback with module info
        parser = TracebackParser()
        parsed = parser.parse(fixtures.VALUE_ERROR_MODULE)

        # Manually set module info for testing
        parsed.exception.exception_module = "builtins"

        analyzer = TracebackAnalyzer()
        analysis = analyzer.analyze_parsed(parsed)

        exception_details = analysis["exception"]
        assert exception_details["module"] == "builtins"
        assert exception_details["full_name"] == "builtins.ValueError"

    def test_exception_details_chained(self):
        """Test exception details with chained exceptions."""
        analyzer = TracebackAnalyzer()
        analysis = analyzer.analyze(fixtures.CHAINED_EXCEPTION_CAUSE)

        exception_details = analysis["exception"]

        assert exception_details["class"] == "ValueError"
        assert exception_details["message"] == "calculation failed"
        assert exception_details["has_cause"] is True
        assert exception_details["has_context"] is False

    def test_exception_details_various_types(self):
        """Test exception details for various exception types."""
        test_cases = [
            (
                fixtures.KEY_ERROR,
                "KeyError",
                ["BaseException", "Exception", "LookupError", "KeyError"],
            ),
            (
                fixtures.TYPE_ERROR,
                "TypeError",
                ["BaseException", "Exception", "TypeError"],
            ),
            (
                fixtures.NAME_ERROR,
                "NameError",
                ["BaseException", "Exception", "NameError"],
            ),
            (
                fixtures.ATTRIBUTE_ERROR,
                "AttributeError",
                ["BaseException", "Exception", "AttributeError"],
            ),
            (
                fixtures.IMPORT_ERROR,
                "ImportError",
                ["BaseException", "Exception", "ImportError"],
            ),
            (
                fixtures.MODULE_NOT_FOUND_ERROR,
                "ModuleNotFoundError",
                ["BaseException", "Exception", "ImportError", "ModuleNotFoundError"],
            ),
            (
                fixtures.FILE_NOT_FOUND_ERROR,
                "FileNotFoundError",
                ["BaseException", "Exception", "OSError", "FileNotFoundError"],
            ),
            (
                fixtures.PERMISSION_ERROR,
                "PermissionError",
                ["BaseException", "Exception", "OSError", "PermissionError"],
            ),
            (
                fixtures.RECURSION_ERROR,
                "RecursionError",
                ["BaseException", "Exception", "RuntimeError", "RecursionError"],
            ),
            (fixtures.MEMORY_ERROR, "MemoryError", ["BaseException", "MemoryError"]),
        ]

        for traceback_text, exception_type, expected_hierarchy in test_cases:
            analyzer = TracebackAnalyzer()
            analysis = analyzer.analyze(traceback_text)

            exception_details = analysis["exception"]
            assert exception_details["class"] == exception_type
            assert exception_details["hierarchy"] == expected_hierarchy

    def test_exception_details_no_error_frame(self):
        """Test exception details when there's no error frame."""
        # Create a minimal parsed traceback without frames
        from tattletail.models import ExceptionInfo
        from tattletail.models import ParsedTraceback

        exception = ExceptionInfo(
            exception_type="RuntimeError", exception_message="test error"
        )
        parsed = ParsedTraceback(
            exception=exception,
            stack_frames=[],
            raw_traceback="RuntimeError: test error",
        )

        analyzer = TracebackAnalyzer()
        analysis = analyzer.analyze_parsed(parsed)

        exception_details = analysis["exception"]
        assert exception_details["class"] == "RuntimeError"
        assert exception_details["message"] == "test error"
        assert exception_details["line_number"] is None
        assert exception_details["file_path"] is None
        assert exception_details["function_name"] is None

    def test_exception_backwards_compatibility(self):
        """Test that analysis still contains all original keys."""
        analyzer = TracebackAnalyzer()
        analysis = analyzer.analyze(fixtures.ZERO_DIVISION_ERROR)

        # Verify all original keys are still present
        assert "summary" in analysis
        assert "probable_cause" in analysis
        assert "patterns" in analysis
        assert "metrics" in analysis
        # And the new key
        assert "exception" in analysis
