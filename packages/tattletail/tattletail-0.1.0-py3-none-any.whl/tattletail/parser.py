"""
Traceback parsing functionality.

This module provides the `TracebackParser` class, which handles both string-based
traceback parsing and direct live exception parsing for optimal performance.
"""

import re
import sys
import traceback
from typing import Any

from .models import CodeContext
from .models import ExceptionInfo
from .models import ParsedTraceback
from .models import StackFrame


class TracebackParser:
    """
    Parses Python tracebacks from strings or live exceptions into structured format.

    This class handles both string-based traceback parsing (using regex) and
    direct live exception parsing (using traceback.extract_tb for better performance).

    Attributes
    ----------
    extract_locals : bool
        If True, attempts to extract local variables from the traceback.
        (Note: This feature is not fully implemented in the current version).
    extract_context : bool
        If True, extracts lines of source code around the error line.
    """

    TRACEBACK_START = re.compile(r"^Traceback \(most recent call last\):?\s*$")
    FRAME_FILE = re.compile(
        r"^\s*File \"(?P<file>.+?)\", line (?P<line>\d+)(?:, in (?P<func>.+))?$"
    )
    CODE_LINE = re.compile(r"^\s{4,}(?P<code>.+)$")
    EXCEPTION_LINE = re.compile(r"^(?P<type>\w+)(?::?\s*(?P<message>.*))?$")
    CAUSED_BY = re.compile(r"^The above exception was the direct cause")
    DURING_HANDLING = re.compile(r"^During handling of the above exception")

    def __init__(
        self, extract_locals: bool = False, extract_context: bool = False
    ) -> None:
        """
        Initialize the parser.

        Parameters
        ----------
        extract_locals : bool, optional
            If True, will attempt to extract local variables. Defaults to False.
        extract_context : bool, optional
            If True, will extract surrounding code context. Defaults to False.
        """
        self.extract_locals = extract_locals
        self.extract_context = extract_context
        self.reset()

    def reset(self):
        """Reset the parser's internal state."""
        self.current_frames: list[StackFrame] = []
        self.current_exception: ExceptionInfo | None = None
        self.raw_lines: list[str] = []
        self.chained_exceptions: list[dict[str, Any]] = []

    def parse(self, traceback_text: str) -> ParsedTraceback:
        """
        Parse a complete traceback string.

        Parameters
        ----------
        traceback_text : str
            The full traceback text to be parsed.

        Returns
        -------
        ParsedTraceback
            An object containing all the structured information from the traceback.
        """
        self.reset()
        self.raw_lines = traceback_text.strip().split("\n")

        i = 0
        while i < len(self.raw_lines):
            line = self.raw_lines[i]

            if self.TRACEBACK_START.match(line):
                i = self._parse_traceback_section(i + 1)
            elif self.CAUSED_BY.search(line) or self.DURING_HANDLING.search(line):
                # Save current exception chain as the cause
                if self.current_exception:
                    self._save_current_exception()
                # Skip the chain delimiter and any blank lines
                i += 1
                while i < len(self.raw_lines) and not self.raw_lines[i].strip():
                    i += 1
            # Check for exception line outside of a traceback section
            # (e.g., SyntaxError)
            elif self._is_exception_line(line) and not self.current_frames:
                self._parse_exception(line)
                i += 1
            else:
                i += 1

        self._finalize_exception()

        if not self.current_exception:
            # Handle cases where no exception line was found (e.g., malformed input)
            self.current_exception = ExceptionInfo(
                exception_type="UnknownError",
                exception_message="Could not parse exception from traceback.",
            )

        return ParsedTraceback(
            exception=self.current_exception,
            stack_frames=self.current_frames,
            raw_traceback=traceback_text,
        )

    def _parse_traceback_section(self, start_idx: int) -> int:
        """Parse a standard section of a traceback containing frames."""
        i = start_idx
        while i < len(self.raw_lines):
            line = self.raw_lines[i]

            frame_match = self.FRAME_FILE.match(line)
            if frame_match:
                frame = self._parse_frame(frame_match)

                # The next line might be the code line
                if i + 1 < len(self.raw_lines):
                    code_match = self.CODE_LINE.match(self.raw_lines[i + 1])
                    if code_match:
                        frame.code_line = code_match.group("code").strip()
                        i += 1

                self.current_frames.append(frame)
                i += 1
            elif self._is_exception_line(line):
                self._parse_exception(line)
                return i + 1
            else:
                i += 1
        return i

    def _parse_frame(self, match: re.Match) -> StackFrame:
        """Parse information from a stack frame line."""
        file_path = match.group("file")
        line_number = int(match.group("line"))
        function_name = match.group("func") or "<module>"

        context_lines = None
        if self.extract_context:
            context_lines = self._extract_context(file_path, line_number)

        return StackFrame(
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            code_line=None,  # Will be filled in by the caller if found
            context_lines=context_lines,
        )

    def _extract_context(
        self, file_path: str, line_number: int, context_size: int = 3
    ) -> list[CodeContext] | None:
        """Extract surrounding code context from a file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            start = max(0, line_number - context_size - 1)
            end = min(len(lines), line_number + context_size)

            return [
                CodeContext(
                    line_number=i + 1,
                    code=lines[i].rstrip(),
                    is_error_line=(i + 1 == line_number),
                )
                for i in range(start, end)
            ]
        except (IOError, OSError):
            return None  # File not accessible or does not exist

    def _is_exception_line(self, line: str) -> bool:
        """Check if a line contains exception information."""
        stripped_line = line.strip()
        if not stripped_line or self.FRAME_FILE.match(stripped_line):
            return False

        # Skip chained exception delimiters
        if self.CAUSED_BY.search(stripped_line) or self.DURING_HANDLING.search(
            stripped_line
        ):
            return False

        # Skip traceback headers
        if self.TRACEBACK_START.match(stripped_line):
            return False

        # A line is likely an exception line if it contains a colon and
        # doesn't look like a file path line.
        return ":" in stripped_line

    def _parse_exception(self, line: str):
        """Parse the exception type and message from a line."""
        match = self.EXCEPTION_LINE.match(line.strip())
        if match:
            exc_type = match.group("type")
            message = match.group("message") or ""

            self.current_exception = ExceptionInfo(
                exception_type=exc_type,
                exception_message=message.strip(),
            )
        else:
            # Fallback for lines that don't match the regex but are exception lines
            parts = line.strip().split(":", 1)
            exc_type = parts[0]
            message = parts[1].strip() if len(parts) > 1 else ""
            self.current_exception = ExceptionInfo(
                exception_type=exc_type, exception_message=message
            )

    def _save_current_exception(self):
        """Save the current exception details to handle chained exceptions."""
        if self.current_exception:
            self.chained_exceptions.append(
                {
                    "exception": self.current_exception,
                    "frames": self.current_frames.copy(),
                }
            )
        self.current_frames = []
        self.current_exception = None

    def _finalize_exception(self):
        """Process chained exceptions to link them together."""
        if not self.chained_exceptions:
            return

        # The current exception is the top-level one.
        # The first chained exception is its direct cause.
        if self.current_exception and self.chained_exceptions:
            self.current_exception.cause = self.chained_exceptions[0]["exception"]

        # Link the rest of the chain
        for i in range(len(self.chained_exceptions) - 1):
            self.chained_exceptions[i]["exception"].cause = self.chained_exceptions[
                i + 1
            ]["exception"]

        # Combine all frames
        all_frames = []
        for chained in self.chained_exceptions:
            all_frames.extend(chained["frames"])
        all_frames.extend(self.current_frames)
        self.current_frames = all_frames

    def _frame_summary_to_stack_frame(self, frame_summary) -> StackFrame:
        """
        Convert a traceback.FrameSummary to a StackFrame object.

        Parameters
        ----------
        frame_summary : traceback.FrameSummary
            The frame summary from traceback.extract_tb()

        Returns
        -------
        StackFrame
            A structured StackFrame object
        """
        context_lines = None
        if self.extract_context:
            context_lines = self._extract_context(
                frame_summary.filename, frame_summary.lineno
            )

        return StackFrame(
            file_path=frame_summary.filename,
            line_number=frame_summary.lineno,
            function_name=frame_summary.name,
            code_line=frame_summary.line,  # Already extracted by traceback module
            context_lines=context_lines,
        )

    def _parse_from_live_exception(
        self, exc_type, exc_value, exc_tb
    ) -> ParsedTraceback:
        """
        Parse a traceback directly from live exception objects using extract_tb().

        This method is more efficient and accurate than parsing formatted strings
        for live exceptions.

        Parameters
        ----------
        exc_type : type
            The exception type
        exc_value : Exception
            The exception instance
        exc_tb : traceback
            The traceback object

        Returns
        -------
        ParsedTraceback
            The structured traceback information
        """
        self.reset()

        # Build exception chain by traversing __cause__ and __context__
        exception_chain = []
        current_exc = exc_value
        current_tb = exc_tb

        while current_exc is not None:
            # Extract frames for current exception
            frames = []
            if current_tb is not None:
                extracted_frames = traceback.extract_tb(current_tb)
                frames = [
                    self._frame_summary_to_stack_frame(frame)
                    for frame in extracted_frames
                ]

            # Create exception info
            exc_info = ExceptionInfo(
                exception_type=current_exc.__class__.__name__,
                exception_message=str(current_exc),
            )

            exception_chain.append({"exception": exc_info, "frames": frames})

            # Move to the next exception in the chain
            next_exc = getattr(current_exc, "__cause__", None) or getattr(
                current_exc, "__context__", None
            )
            if next_exc is current_exc:  # Prevent infinite loops
                break
            current_exc = next_exc
            current_tb = getattr(next_exc, "__traceback__", None) if next_exc else None

        # Process the exception chain
        if exception_chain:
            # The first exception is the top-level one
            main_exception_data = exception_chain[0]
            self.current_exception = main_exception_data["exception"]
            self.current_frames = main_exception_data["frames"]

            # Link the causes
            for i in range(len(exception_chain) - 1):
                exception_chain[i]["exception"].cause = exception_chain[i + 1][
                    "exception"
                ]

            # Combine all frames from the chain
            all_frames = []
            for exc_data in exception_chain:
                all_frames.extend(exc_data["frames"])
            self.current_frames = all_frames
        else:
            # Fallback for edge cases
            self.current_exception = ExceptionInfo(
                exception_type=exc_type.__name__ if exc_type else "UnknownError",
                exception_message=(
                    str(exc_value) if exc_value else "Unknown error occurred."
                ),
            )

        # Ensure we have an exception (should always be set by now)
        if self.current_exception is None:
            self.current_exception = ExceptionInfo(
                exception_type="UnknownError",
                exception_message="No exception information available.",
            )

        return ParsedTraceback(
            exception=self.current_exception,
            stack_frames=self.current_frames,
            raw_traceback="".join(
                traceback.format_exception(exc_type, exc_value, exc_tb)
            ),
        )

    def parse_from_exception(self, exc_info: tuple | None = None) -> ParsedTraceback:
        """
        Parse a traceback directly from an exception object or `sys.exc_info()`.

        Parameters
        ----------
        exc_info : tuple, optional
            A tuple of (type, value, traceback), as returned by `sys.exc_info()`.
            If None, `sys.exc_info()` is called automatically. Defaults to None.

        Returns
        -------
        ParsedTraceback
            The structured traceback information.

        Raises
        ------
        ValueError
            If no active exception is found.
        """
        if exc_info is None:
            exc_info = sys.exc_info()

        exc_type, exc_value, exc_tb = exc_info

        if exc_type is None or exc_value is None or exc_tb is None:
            raise ValueError(
                "No active exception to parse. Please call in an `except` block."
            )

        # Use the optimized direct parsing method for live exceptions
        return self._parse_from_live_exception(exc_type, exc_value, exc_tb)
