#!/usr/bin/env python3
"""
Context Manager Examples for Tattletail.

This script demonstrates the powerful context manager functionality
that makes error handling and analysis more Pythonic and elegant.
"""

import logging
import sys


# Add src to path for examples
sys.path.insert(0, "../src")

import tattletail


def demonstrate_basic_capture():
    """Show basic exception capture without handling."""
    print("=== Basic Exception Capture ===")

    # Capture and analyze automatically
    with tattletail.capture(suppress=True) as ctx:

        def calculate_average(numbers):
            return sum(numbers) / len(numbers)

        # This will cause a ZeroDivisionError
        calculate_average([])

    if ctx.exception:
        print(f"Caught: {ctx.parsed.exception.exception_type}")  # type: ignore
        print(f"Message: {ctx.parsed.exception.exception_message}")  # type: ignore
        print(f"Location: {ctx.parsed.get_error_location().function_name}")  # type: ignore
        print(f"Probable cause: {ctx.analysis['probable_cause']}")  # type: ignore
    print()


def demonstrate_testing_workflow():
    """Show how context managers make testing easier."""
    print("=== Testing Workflow ===")

    # Test that specific errors occur
    with tattletail.expect(ValueError, "invalid literal") as ctx:
        int("not_a_number")

    if ctx.matched:
        print("✅ Expected ValueError with 'invalid literal' message occurred")
        print(f"   Exception: {ctx.exception}")
        print(f"   Analysis: {ctx.analysis['summary']}")  # type: ignore
    else:
        print("❌ Expected exception did not occur")

    # Test multiple exception types
    with tattletail.expect((ValueError, TypeError)) as ctx:
        len(None)  # type: ignore  # This will raise TypeError

    if ctx.matched:
        print("✅ One of the expected exception types occurred")
        print(f"   Got: {type(ctx.exception).__name__}")
    print()


def demonstrate_production_monitoring():
    """Show production monitoring with logging."""
    print("=== Production Monitoring ===")

    # Setup logger
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger = logging.getLogger(__name__)

    # Monitor with automatic logging
    with tattletail.monitor(logger=logger, level="ERROR"):
        try:
            # Simulate a production operation
            user_data = {"name": "John", "age": "not_a_number"}
            int(user_data["age"])
        except ValueError:
            pass  # Context manager will log it

    print(
        "Check the log output above - the error was automatically logged "
        "with rich context!"
    )
    print()


def demonstrate_callback_functionality():
    """Show custom callback functionality."""
    print("=== Custom Callback Functionality ===")

    error_reports = []

    def error_callback(ctx):
        """Process errors with custom callback."""
        error_reports.append(
            {
                "type": ctx.parsed.exception.exception_type,
                "file": ctx.parsed.get_error_location().file_path,
                "line": ctx.parsed.get_error_location().line_number,
                "complexity": ctx.analysis["patterns"]["call_depth"],
                "probable_cause": ctx.analysis["probable_cause"],
            }
        )
        print(f"🚨 Error captured by callback: {ctx.parsed.exception.exception_type}")

    # Use callback for custom error processing
    with tattletail.capture(suppress=True, on_exception=error_callback):

        def level_3():
            raise RuntimeError("Deep nested error")

        def level_2():
            level_3()

        def level_1():
            level_2()

        level_1()

    print(f"Error reports collected: {len(error_reports)}")
    if error_reports:
        report = error_reports[0]
        print(f"  Type: {report['type']}")
        print(f"  Complexity: {report['complexity']} call stack levels")
        print(f"  Cause: {report['probable_cause']}")
    print()


def demonstrate_context_extraction():
    """Show context extraction in context managers."""
    print("=== Context Extraction ===")

    # Create a temporary function for demonstration
    def problematic_function():
        x = 10
        y = 0
        result = x / y  # This will fail
        return result

    with tattletail.capture(extract_context=True, suppress=True) as ctx:
        problematic_function()

    if ctx.exception and ctx.parsed and ctx.parsed.stack_frames:
        print("Source code context around error:")
        for frame in ctx.parsed.stack_frames:
            if frame.context_lines and "problematic_function" in frame.function_name:
                print(
                    f"\nIn {frame.function_name} "
                    f"({frame.file_path}:{frame.line_number}):"
                )
                for line_ctx in frame.context_lines:
                    marker = ">>> " if line_ctx.is_error_line else "    "
                    print(f"{marker}{line_ctx.line_number:3d}: {line_ctx.code}")
    print()


def demonstrate_advanced_patterns():
    """Show advanced context manager patterns."""
    print("=== Advanced Patterns ===")

    # Chained operations with monitoring
    operations_log = []

    def log_operation(operation_name):
        def callback(ctx):
            operations_log.append(
                {
                    "operation": operation_name,
                    "error": ctx.parsed.exception.exception_type,
                    "message": ctx.parsed.exception.exception_message,
                }
            )

        return callback

    def validate_data(x):
        return int(x) if x.isdigit() else None

    # Multiple operations with individual monitoring
    with tattletail.capture(
        suppress=True, on_exception=log_operation("data_validation")
    ):
        validate_data("invalid")

    with tattletail.capture(suppress=True, on_exception=log_operation("calculation")):
        _ = 10 / 0  # Intentional division by zero for demonstration

    with tattletail.capture(suppress=True, on_exception=log_operation("data_access")):
        data = {"key": "value"}
        data["missing_key"]

    print(f"Operations completed with {len(operations_log)} errors logged:")
    for log_entry in operations_log:
        print(f"  • {log_entry['operation']}: {log_entry['error']}")
    print()


def demonstrate_integration_with_existing_code():
    """Show how to integrate with existing error handling."""
    print("=== Integration with Existing Code ===")

    def existing_function_with_error_handling():
        """Simulate existing code that already has error handling."""
        try:
            # Some risky operation
            data = [1, 2, "three", 4]
            return [x * 2 for x in data]
        except TypeError as e:
            # Existing error handling
            print(f"Existing handler caught: {e}")
            raise  # Re-raise for context manager to catch

    # Wrap existing code with Tattletail for enhanced analysis
    with tattletail.capture(suppress=True) as ctx:
        try:
            existing_function_with_error_handling()
        except TypeError:
            pass  # Let context manager handle the analysis

    if ctx.exception and ctx.analysis and ctx.parsed:
        print("Enhanced analysis of existing error:")
        print(f"  Complexity: {ctx.analysis['patterns']['call_depth']} levels")
        error_location = ctx.parsed.get_error_location()
        if error_location:
            print(f"  Error location: {error_location.function_name}")
        print(f"  Insight: {ctx.analysis['probable_cause']}")
    print()


def main():
    """Run all context manager examples."""
    print("Tattletail Context Manager Examples")
    print("=" * 40)
    print()

    demonstrate_basic_capture()
    demonstrate_testing_workflow()
    demonstrate_production_monitoring()
    demonstrate_callback_functionality()
    demonstrate_context_extraction()
    demonstrate_advanced_patterns()
    demonstrate_integration_with_existing_code()

    print("🎉 All context manager examples completed!")
    print("\nKey Benefits:")
    print("• Pythonic exception handling with 'with' statements")
    print("• Automatic analysis without manual try/except blocks")
    print("• Flexible options for testing, monitoring, and custom processing")
    print("• Clean integration with existing error handling patterns")


if __name__ == "__main__":
    main()
