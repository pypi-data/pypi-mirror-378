"""
Advanced traceback analysis.

This module provides the `TracebackAnalyzer` class, which offers high-level
insights, statistics, and patterns based on a parsed traceback.
"""

from pathlib import Path
from typing import Any

from .models import ParsedTraceback
from .parser import TracebackParser


class TracebackAnalyzer:
    """
    Provides advanced analysis of `ParsedTraceback` objects.

    This analyzer computes metrics, identifies common patterns, and
    provides insights for debugging.

    Attributes
    ----------
    parser : TracebackParser
        The parser instance to use for converting raw text to `ParsedTraceback`.
    history : list[ParsedTraceback]
        A history of all tracebacks analyzed by this instance.
    """

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.parser = TracebackParser(extract_context=True)
        self.history: list[ParsedTraceback] = []

    def analyze(self, traceback_text: str) -> dict[str, Any]:
        """
        Analyze a traceback and return a dictionary of insights.

        Parameters
        ----------
        traceback_text : str
            The raw traceback string to analyze.

        Returns
        -------
        dict[str, any]
            A dictionary containing the analysis results, including summary,
            probable cause, patterns, and metrics.
        """
        parsed = self.parser.parse(traceback_text)
        return self.analyze_parsed(parsed)

    def analyze_parsed(self, parsed: ParsedTraceback) -> dict[str, Any]:
        """
        Analyze a pre-parsed traceback and return insights.

        Parameters
        ----------
        parsed : ParsedTraceback
            The already parsed traceback object to analyze.

        Returns
        -------
        dict[str, any]
            A dictionary containing the analysis results, including summary,
            probable cause, patterns, and metrics.
        """
        self.history.append(parsed)

        return {
            "summary": self._generate_summary(parsed),
            "exception": self._extract_exception_details(parsed),
            "probable_cause": self._identify_probable_cause(parsed),
            "patterns": self._identify_patterns(parsed),
            "metrics": self._calculate_metrics(parsed),
        }

    def _generate_summary(self, parsed: ParsedTraceback) -> str:
        """Generate a concise one-line summary of the error."""
        error_frame = parsed.get_error_location()
        exc_type = parsed.exception.exception_type
        exc_msg = parsed.exception.exception_message

        summary = f"{exc_type}"
        if error_frame:
            summary += f" in {error_frame.function_name}"
            summary += (
                f" ({Path(error_frame.file_path).name}:{error_frame.line_number})"
            )

        if exc_msg:
            summary += f": {exc_msg[:100]}"
            if len(exc_msg) > 100:
                summary += "..."

        return summary

    def _extract_exception_details(self, parsed: ParsedTraceback) -> dict[str, Any]:
        """Extract detailed exception information."""
        exception = parsed.exception
        error_frame = parsed.get_error_location()

        # Get exception class hierarchy
        hierarchy = self._get_exception_hierarchy(exception.exception_type)

        return {
            "class": exception.exception_type,
            "name": exception.exception_type,  # Same as class for Python exceptions
            "message": exception.exception_message,
            "module": exception.exception_module,
            "full_name": exception.get_full_type(),
            "hierarchy": hierarchy,
            "line_number": error_frame.line_number if error_frame else None,
            "file_path": error_frame.file_path if error_frame else None,
            "function_name": error_frame.function_name if error_frame else None,
            "has_cause": exception.cause is not None,
            "has_context": exception.context is not None,
        }

    def _get_exception_hierarchy(self, exception_type: str) -> list[str]:
        """Get the inheritance hierarchy for a known exception type."""
        # Built-in exception hierarchy mapping
        hierarchy_map = {
            "Exception": ["BaseException", "Exception"],
            "ArithmeticError": ["BaseException", "Exception", "ArithmeticError"],
            "LookupError": ["BaseException", "Exception", "LookupError"],
            "ValueError": ["BaseException", "Exception", "ValueError"],
            "TypeError": ["BaseException", "Exception", "TypeError"],
            "NameError": ["BaseException", "Exception", "NameError"],
            "AttributeError": ["BaseException", "Exception", "AttributeError"],
            "KeyError": ["BaseException", "Exception", "LookupError", "KeyError"],
            "IndexError": ["BaseException", "Exception", "LookupError", "IndexError"],
            "ZeroDivisionError": [
                "BaseException",
                "Exception",
                "ArithmeticError",
                "ZeroDivisionError",
            ],
            "OverflowError": [
                "BaseException",
                "Exception",
                "ArithmeticError",
                "OverflowError",
            ],
            "FloatingPointError": [
                "BaseException",
                "Exception",
                "ArithmeticError",
                "FloatingPointError",
            ],
            "ImportError": ["BaseException", "Exception", "ImportError"],
            "ModuleNotFoundError": [
                "BaseException",
                "Exception",
                "ImportError",
                "ModuleNotFoundError",
            ],
            "FileNotFoundError": [
                "BaseException",
                "Exception",
                "OSError",
                "FileNotFoundError",
            ],
            "PermissionError": [
                "BaseException",
                "Exception",
                "OSError",
                "PermissionError",
            ],
            "ConnectionError": [
                "BaseException",
                "Exception",
                "OSError",
                "ConnectionError",
            ],
            "RecursionError": [
                "BaseException",
                "Exception",
                "RuntimeError",
                "RecursionError",
            ],
            "MemoryError": ["BaseException", "MemoryError"],
            "SystemExit": ["BaseException", "SystemExit"],
            "KeyboardInterrupt": ["BaseException", "KeyboardInterrupt"],
        }

        return hierarchy_map.get(
            exception_type, ["BaseException", "Exception", exception_type]
        )

    def _identify_probable_cause(self, parsed: ParsedTraceback) -> str:
        """Identify the probable cause based on exception type."""
        exc_type = parsed.exception.exception_type

        causes = {
            "NameError": "A variable or function name is not defined or misspelled.",
            "TypeError": (
                "An operation was applied to an object of an inappropriate type."
            ),
            "ValueError": (
                "A function received an argument with the right type but "
                "an invalid value."
            ),
            "KeyError": "A dictionary key was accessed that does not exist.",
            "IndexError": "A sequence subscript is out of range.",
            "AttributeError": "An attribute reference or assignment failed.",
            "ImportError": (
                "The `import` statement failed to find the module definition."
            ),
            "ModuleNotFoundError": "A module could not be located.",
            "FileNotFoundError": "A file or directory was requested but not found.",
            "ZeroDivisionError": (
                "The second argument of a division or modulo operation was zero."
            ),
            "RecursionError": "The maximum recursion depth was exceeded.",
            "MemoryError": "An operation ran out of memory.",
            "ConnectionError": "A network connection failed.",
            "PermissionError": (
                "An operation was attempted without adequate access rights."
            ),
        }
        return causes.get(exc_type, "Could not automatically determine the cause.")

    def _identify_patterns(self, parsed: ParsedTraceback) -> dict[str, Any]:
        """Identify common patterns in the traceback."""
        functions = [f.function_name for f in parsed.stack_frames]
        function_counts = {func: functions.count(func) for func in set(functions)}
        repeated_functions = [
            func for func, count in function_counts.items() if count > 3
        ]

        error_frame = parsed.get_error_location()

        return {
            "is_recursive": bool(repeated_functions),
            "repeated_functions": repeated_functions,
            "call_depth": len(parsed.stack_frames),
            "error_in_stdlib": error_frame.is_stdlib if error_frame else False,
            "error_in_site_packages": error_frame.is_site_packages
            if error_frame
            else False,
        }

    def _calculate_metrics(self, parsed: ParsedTraceback) -> dict[str, Any]:
        """Calculate quantitative metrics from the traceback."""
        return {
            "total_frames": len(parsed.stack_frames),
            "user_frames": len(parsed.get_user_frames()),
            "stdlib_frames": sum(1 for f in parsed.stack_frames if f.is_stdlib),
            "site_packages_frames": sum(
                1 for f in parsed.stack_frames if f.is_site_packages
            ),
            "unique_files": len(set(f.file_path for f in parsed.stack_frames)),
            "has_chained_exceptions": parsed.exception.cause is not None,
        }

    def generate_report(self, traceback_text: str) -> str:
        """
        Generate a full, human-readable analysis report from a traceback string.

        Parameters
        ----------
        traceback_text : str
            The raw traceback string.

        Returns
        -------
        str
            A formatted report containing a summary and analysis.
        """
        analysis = self.analyze(traceback_text)
        parsed = self.history[-1]
        error_frame = parsed.get_error_location()

        report = [
            "=" * 70,
            "Tattletail Analysis Report",
            "=" * 70,
            "",
            "Summary:",
            "--------",
            f"  - Exception: {analysis['summary']}",
            f"  - Probable Cause: {analysis['probable_cause']}",
            "",
        ]

        if error_frame:
            code_line = (
                error_frame.code_line.strip() if error_frame.code_line else "N/A"
            )
            report.extend(
                [
                    "Error Location:",
                    "--------------- ",
                    f"  - File: {error_frame.file_path}",
                    f"  - Line: {error_frame.line_number}",
                    f"  - Function: {error_frame.function_name}",
                    f"  - Code: {code_line}",
                    "",
                ]
            )

        patterns = analysis["patterns"]
        is_recursive = "Yes" if patterns["is_recursive"] else "No"
        in_stdlib = "Yes" if patterns["error_in_stdlib"] else "No"
        in_site = "Yes" if patterns["error_in_site_packages"] else "No"
        report.extend(
            [
                "Detected Patterns:",
                "------------------",
                f"  - Call Stack Depth: {patterns['call_depth']}",
                f"  - Possible Recursion: {is_recursive}",
                f"  - Error in Standard Library: {in_stdlib}",
                f"  - Error in Third-Party Package: {in_site}",
                "",
            ]
        )

        report.append("Call Chain (most recent last): ")
        report.append("------------------------------")
        for frame in parsed.stack_frames:
            line = (
                f"  -> {frame.function_name} in "
                f"{Path(frame.file_path).name}:{frame.line_number}"
            )
            report.append(line)

        report.append("\n" + "=" * 70)
        return "\n".join(report)
