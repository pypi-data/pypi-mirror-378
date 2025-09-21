"""
Tests for the main module interface functions.
"""

import sys

import tattletail
from tattletail import analyze
from tattletail import generate_report
from tattletail import parse
from tattletail import parse_from_exception

from .fixtures.basic_tracebacks import SIMPLE_TRACEBACK
from .fixtures.complex_tracebacks import UNICODE_MAIN_INTERFACE
from .fixtures.edge_case_tracebacks import MALFORMED_TRACEBACK
from .fixtures.performance_tracebacks import generate_large_traceback


class TestMainInterfaceFunctions:
    """Test the main module interface functions."""

    def test_parse_function(self):
        """Test the main parse function."""
        parsed = parse(SIMPLE_TRACEBACK)

        assert parsed.exception.exception_type == "ValueError"
        assert len(parsed.stack_frames) == 4
        assert parsed.raw_traceback == SIMPLE_TRACEBACK

    def test_parse_function_with_context(self):
        """Test the parse function with context extraction."""
        parsed = parse(SIMPLE_TRACEBACK, extract_context=True)

        assert parsed.exception.exception_type == "ValueError"
        # Context extraction should be enabled, though may not have content
        # due to missing files
        for frame in parsed.stack_frames:
            assert frame.context_lines is not None

    def test_parse_from_exception_function(self):
        """Test the parse_from_exception function."""
        try:
            raise ValueError("Test exception for interface")
        except Exception:
            parsed = parse_from_exception()

            assert parsed.exception.exception_type == "ValueError"
            assert "Test exception for interface" in parsed.exception.exception_message

    def test_parse_from_exception_with_exc_info(self):
        """Test parse_from_exception with explicit exc_info."""
        try:
            raise RuntimeError("Explicit exc_info test")
        except Exception:
            exc_info = sys.exc_info()
            parsed = parse_from_exception(exc_info)

            assert parsed.exception.exception_type == "RuntimeError"
            assert "Explicit exc_info test" in parsed.exception.exception_message

    def test_parse_from_exception_with_context(self):
        """Test parse_from_exception with context extraction."""
        try:
            raise TypeError("Context extraction test")
        except Exception:
            parsed = parse_from_exception(extract_context=True)

            assert parsed.exception.exception_type == "TypeError"

    def test_analyze_function(self):
        """Test the analyze function."""
        analysis = analyze(SIMPLE_TRACEBACK)

        assert isinstance(analysis, dict)
        assert "summary" in analysis
        assert "probable_cause" in analysis
        assert "patterns" in analysis
        assert "metrics" in analysis

        assert "ValueError" in analysis["summary"]

    def test_generate_report_function(self):
        """Test the generate_report function."""
        report = generate_report(SIMPLE_TRACEBACK)

        assert isinstance(report, str)
        assert "Tattletail Analysis Report" in report
        assert "ValueError" in report
        assert "Summary:" in report

    def test_module_version(self):
        """Test that module version is accessible."""
        assert hasattr(tattletail, "__version__")
        assert isinstance(tattletail.__version__, str)
        assert tattletail.__version__ == "0.1.0"

    def test_module_exports(self):
        """Test that expected functions are exported."""
        expected_functions = [
            "parse",
            "parse_from_exception",
            "analyze",
            "generate_report",
        ]

        for func_name in expected_functions:
            assert hasattr(tattletail, func_name)
            assert callable(getattr(tattletail, func_name))

    def test_module_docstring(self):
        """Test that module has proper docstring."""
        assert tattletail.__doc__ is not None
        assert "Traceback Parsing and Analysis" in tattletail.__doc__
        assert "parse()" in tattletail.__doc__
        assert "analyze()" in tattletail.__doc__


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple functions."""

    def test_parse_and_analyze_workflow(self):
        """Test typical workflow of parsing then analyzing."""
        # First parse
        parsed = parse(SIMPLE_TRACEBACK)

        # Then analyze the same traceback
        analysis = analyze(SIMPLE_TRACEBACK)

        # Both should agree on the exception type
        assert parsed.exception.exception_type == "ValueError"
        assert "ValueError" in analysis["summary"]

    def test_parse_analyze_report_workflow(self):
        """Test full workflow: parse -> analyze -> report."""
        # Parse
        parsed = parse(SIMPLE_TRACEBACK)

        # Analyze
        analysis = analyze(SIMPLE_TRACEBACK)

        # Generate report
        report = generate_report(SIMPLE_TRACEBACK)

        # All should be consistent
        exc_type = parsed.exception.exception_type
        assert exc_type in analysis["summary"]
        assert exc_type in report

    def test_exception_to_analysis_workflow(self):
        """Test workflow from live exception to analysis."""
        try:
            # Create a test exception scenario
            def inner_func():
                raise ValueError("Test workflow exception")

            def outer_func():
                inner_func()

            outer_func()

        except Exception:
            # Parse the current exception
            parsed = parse_from_exception()

            # Convert to string and analyze
            tb_string = parsed.raw_traceback
            analysis = analyze(tb_string)

            # Should be consistent
            assert parsed.exception.exception_type == "ValueError"
            assert "ValueError" in analysis["summary"]
            assert "Test workflow exception" in parsed.exception.exception_message

    def test_error_handling_consistency(self):
        """Test that all functions handle errors consistently."""
        # All functions should handle this gracefully
        parsed = parse(MALFORMED_TRACEBACK)
        analysis = analyze(MALFORMED_TRACEBACK)
        report = generate_report(MALFORMED_TRACEBACK)

        # Should not raise exceptions
        assert parsed is not None
        assert analysis is not None
        assert report is not None

    def test_unicode_handling_across_functions(self):
        """Test unicode handling across all functions."""
        parsed = parse(UNICODE_MAIN_INTERFACE)
        analysis = analyze(UNICODE_MAIN_INTERFACE)
        report = generate_report(UNICODE_MAIN_INTERFACE)

        # All should handle unicode properly
        assert "UnicodeError" in parsed.exception.exception_type
        assert len(parsed.stack_frames) > 0
        assert "测试函数" in parsed.stack_frames[0].function_name
        assert "UnicodeError" in analysis["summary"]
        assert "UnicodeError" in report

    def test_performance_with_large_traceback(self):
        """Test performance with a large traceback."""
        large_traceback = generate_large_traceback()

        # Should handle large tracebacks efficiently
        parsed = parse(large_traceback)
        analysis = analyze(large_traceback)

        assert len(parsed.stack_frames) == 100
        assert analysis["patterns"]["call_depth"] == 100
        assert parsed.exception.exception_type == "RuntimeError"
