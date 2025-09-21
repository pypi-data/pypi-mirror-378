#!/usr/bin/env python3
"""
Basic usage examples of the tattletail library.

This script demonstrates the core functionality:
- Parsing tracebacks from strings
- Capturing live exceptions
- Analyzing tracebacks for insights
- Generating readable reports
"""

import sys
import traceback


# Add src to path for examples
sys.path.insert(0, "../src")

import tattletail


def example_division_error():
    """Create a division by zero error for demonstration."""

    def calculate_average(numbers):
        total = sum(numbers)
        count = len(numbers)
        return total / count  # This will fail with empty list

    def process_data(data_sets):
        results = []
        for data in data_sets:
            avg = calculate_average(data)
            results.append(avg)
        return results

    # This will cause a ZeroDivisionError
    data_sets = [[1, 2, 3], [], [4, 5, 6]]  # Empty list in middle
    return process_data(data_sets)


def example_type_error():
    """Create a type error for demonstration."""

    def concatenate_strings(items):
        result = ""
        for item in items:
            result += item  # This will fail when item is not a string
        return result

    mixed_data = ["Hello", " ", "World", 42, "!"]
    return concatenate_strings(mixed_data)


def demonstrate_basic_parsing():
    """Show basic traceback parsing from a string."""
    print("=== Basic Traceback Parsing ===")

    # Sample traceback string (could come from logs, etc.)
    traceback_string = """Traceback (most recent call last):
  File "example.py", line 15, in main
    result = divide_numbers(10, 0)
  File "example.py", line 8, in divide_numbers
    return a / b
ZeroDivisionError: division by zero"""

    # Parse the traceback
    parsed = tattletail.parse(traceback_string)

    print(f"Exception Type: {parsed.exception.exception_type}")
    print(f"Exception Message: {parsed.exception.exception_message}")
    print(f"Number of Stack Frames: {len(parsed.stack_frames)}")
    print(f"Error Location: {parsed.get_error_location()}")

    print("\nStack Frames:")
    for i, frame in enumerate(parsed.stack_frames):
        print(
            f"  {i + 1}. {frame.function_name} in {frame.file_path}:{frame.line_number}"
        )

    print()


def demonstrate_live_exception_capture():
    """Show capturing and parsing live exceptions."""
    print("=== Live Exception Capture ===")

    try:
        example_division_error()
    except Exception:
        # Capture the current exception
        parsed = tattletail.parse_from_exception()

        print(f"Caught: {parsed.exception.exception_type}")
        print(f"Message: {parsed.exception.exception_message}")
        print(f"Call depth: {len(parsed.stack_frames)} frames")

        # Show the call chain
        call_chain = parsed.get_call_chain()
        print(f"Call chain: {' -> '.join(call_chain)}")
        print()


def demonstrate_analysis():
    """Show traceback analysis capabilities."""
    print("=== Traceback Analysis ===")

    try:
        example_type_error()
    except Exception:
        # Get the traceback as string
        tb_string = traceback.format_exc()

        # Analyze the traceback
        analysis = tattletail.analyze(tb_string)

        print(f"Summary: {analysis['summary']}")
        print(f"Probable Cause: {analysis['probable_cause']}")

        print("\nPatterns Detected:")
        patterns = analysis["patterns"]
        print(f"  • Call depth: {patterns['call_depth']}")
        print(f"  • Recursive: {patterns['is_recursive']}")

        if patterns["repeated_functions"]:
            print(
                f"  • Repeated functions: {', '.join(patterns['repeated_functions'])}"
            )

        print("\nMetrics:")
        metrics = analysis["metrics"]
        print(f"  • Total frames: {metrics['total_frames']}")
        print(f"  • User frames: {metrics['user_frames']}")
        print(f"  • Unique files: {metrics['unique_files']}")
        print()


def demonstrate_report_generation():
    """Show human-readable report generation."""
    print("=== Report Generation ===")

    try:
        # Create a more complex error scenario
        def outer_function():
            def middle_function():
                def inner_function():
                    data = {"key": "value"}
                    return data["missing_key"]  # KeyError

                return inner_function()

            return middle_function()

        outer_function()

    except Exception:
        tb_string = traceback.format_exc()

        # Generate a comprehensive report
        report = tattletail.generate_report(tb_string)
        print(report)


def demonstrate_context_extraction():
    """Show context extraction when files are available."""
    print("=== Context Extraction ===")

    # Create a temporary file to demonstrate context extraction
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("""def example_function():
    # This is line 2
    x = 10
    y = 0  # This is the problematic line
    result = x / y  # Division by zero
    return result

example_function()
""")
        temp_file = f.name

    try:
        # Execute the temporary file to generate a real traceback
        exec(compile(open(temp_file).read(), temp_file, "exec"))
    except Exception:
        # Parse with context extraction enabled
        parsed = tattletail.parse_from_exception(extract_context=True)

        print(f"Exception: {parsed.exception.exception_type}")
        print("Context around error:")

        for frame in parsed.stack_frames:
            if frame.context_lines and temp_file in frame.file_path:
                print(f"\nFile: {frame.file_path}:{frame.line_number}")
                for ctx in frame.context_lines:
                    marker = ">>>" if ctx.is_error_line else "   "
                    print(f"{marker} {ctx.line_number:3d}: {ctx.code}")

    finally:
        # Clean up
        os.unlink(temp_file)

    print()


def main():
    """Run all examples."""
    print("Tattletail Library - Usage Examples")
    print("=" * 40)
    print()

    demonstrate_basic_parsing()
    demonstrate_live_exception_capture()
    demonstrate_analysis()
    demonstrate_report_generation()
    demonstrate_context_extraction()

    print("All examples completed!")


if __name__ == "__main__":
    main()
