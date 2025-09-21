"""
Tests for the TracebackAnalyzer.
"""

import pytest

from tattletail.analyzer import TracebackAnalyzer

from .fixtures.analyzer_tracebacks import MINIMAL_TRACEBACK_TEMPLATE
from .fixtures.analyzer_tracebacks import PROBABLE_CAUSE_TEST_CASES
from .fixtures.basic_tracebacks import SIMPLE_TRACEBACK
from .fixtures.complex_tracebacks import CHAINED_TRACEBACK
from .fixtures.complex_tracebacks import LONG_MESSAGE_TRACEBACK
from .fixtures.complex_tracebacks import RECURSIVE_TRACEBACK
from .fixtures.edge_case_tracebacks import EMPTY_TRACEBACK
from .fixtures.edge_case_tracebacks import MALFORMED_TRACEBACK


@pytest.fixture
def analyzer():
    """Create a TracebackAnalyzer instance for testing."""
    return TracebackAnalyzer()


def test_analyze_simple_traceback(analyzer):
    """Test analyzing a simple traceback."""
    analysis = analyzer.analyze(SIMPLE_TRACEBACK)

    # Check structure
    assert "summary" in analysis
    assert "probable_cause" in analysis
    assert "patterns" in analysis
    assert "metrics" in analysis

    # Check specific values
    assert "ValueError" in analysis["summary"]
    assert "invalid value" in analysis["probable_cause"]
    assert analysis["patterns"]["call_depth"] == 4
    assert not analysis["patterns"]["is_recursive"]

    # Check metrics
    metrics = analysis["metrics"]
    assert metrics["total_frames"] == 4
    assert metrics["user_frames"] == 4  # All frames are user frames in this test
    assert not metrics["has_chained_exceptions"]


def test_analyze_chained_traceback(analyzer):
    """Test analyzing a traceback with chained exceptions."""
    analysis = analyzer.analyze(CHAINED_TRACEBACK)

    # Check structure
    assert "RuntimeError" in analysis["summary"]
    assert analysis["patterns"]["call_depth"] == 6  # 4 + 2 frames
    assert not analysis["patterns"]["is_recursive"]

    # Check metrics for chained exceptions
    metrics = analysis["metrics"]
    assert metrics["total_frames"] == 6
    assert metrics["has_chained_exceptions"]


def test_probable_cause_identification(analyzer):
    """Test probable cause identification for common exception types."""
    for exc_type, expected_phrase in PROBABLE_CAUSE_TEST_CASES:
        minimal_traceback = MINIMAL_TRACEBACK_TEMPLATE.format(
            exception_line=f"{exc_type}: Test error"
        )

        analysis = analyzer.analyze(minimal_traceback)
        assert expected_phrase.lower() in analysis["probable_cause"].lower()


def test_pattern_detection_recursion(analyzer):
    """Test detection of recursive patterns."""
    analysis = analyzer.analyze(RECURSIVE_TRACEBACK)
    patterns = analysis["patterns"]

    assert patterns["is_recursive"]
    assert "factorial" in patterns["repeated_functions"]
    assert patterns["call_depth"] == 5


def test_metrics_calculation(analyzer):
    """Test calculation of quantitative metrics."""
    analysis = analyzer.analyze(SIMPLE_TRACEBACK)
    metrics = analysis["metrics"]

    # Check all expected metrics are present
    expected_metrics = [
        "total_frames",
        "user_frames",
        "stdlib_frames",
        "site_packages_frames",
        "unique_files",
        "has_chained_exceptions",
    ]

    for metric in expected_metrics:
        assert metric in metrics
        assert isinstance(metrics[metric], (int, bool))


def test_generate_report(analyzer):
    """Test generation of human-readable reports."""
    report = analyzer.generate_report(SIMPLE_TRACEBACK)

    # Check report structure
    assert "Tattletail Analysis Report" in report
    assert "Summary:" in report
    assert "Error Location:" in report
    assert "Detected Patterns:" in report
    assert "Call Chain" in report

    # Check content
    assert "ValueError" in report
    assert "utils.py" in report
    assert "Line: 78" in report


def test_generate_report_chained(analyzer):
    """Test report generation for chained exceptions."""
    report = analyzer.generate_report(CHAINED_TRACEBACK)

    assert "RuntimeError" in report
    assert "Something went wrong" in report
    assert "main.py" in report


def test_analyzer_history(analyzer):
    """Test that analyzer keeps track of analyzed tracebacks."""
    assert len(analyzer.history) == 0

    analyzer.analyze(SIMPLE_TRACEBACK)
    assert len(analyzer.history) == 1

    analyzer.analyze(CHAINED_TRACEBACK)
    assert len(analyzer.history) == 2

    # Check that history entries are ParsedTraceback objects
    first_entry = analyzer.history[0]
    assert hasattr(first_entry, "exception")
    assert hasattr(first_entry, "stack_frames")
    assert first_entry.exception.exception_type == "ValueError"


def test_summary_generation(analyzer):
    """Test summary generation for different scenarios."""
    # Test with long exception message
    analysis = analyzer.analyze(LONG_MESSAGE_TRACEBACK)
    summary = analysis["summary"]

    assert "ValueError" in summary
    assert "long_function_name" in summary
    assert "test.py:1" in summary
    assert "..." in summary  # Should be truncated
    assert len(summary) < 150  # Should be reasonably short


def test_empty_traceback_handling(analyzer):
    """Test handling of malformed or empty tracebacks."""
    # Test with empty string
    analysis = analyzer.analyze(EMPTY_TRACEBACK)
    assert analysis["summary"]
    assert "UnknownError" in analysis["summary"]

    # Test with just text (no proper traceback format)
    analysis = analyzer.analyze(MALFORMED_TRACEBACK)
    assert analysis["summary"]
