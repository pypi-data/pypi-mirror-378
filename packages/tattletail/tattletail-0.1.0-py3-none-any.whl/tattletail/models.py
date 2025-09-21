"""
Data models for structured traceback information.

This module defines the data classes that represent the components of a parsed
Python traceback, including stack frames, exception details, and the overall
parsed traceback structure.
"""

from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sys
from typing import Any


@dataclass
class CodeContext:
    """
    Represents a single line of code in a source file.

    Attributes
    ----------
    line_number : int
        The line number in the source file.
    code : str
        The source code of the line.
    is_error_line : bool
        True if this is the line where the error occurred.
    """

    line_number: int
    code: str
    is_error_line: bool

    def __str__(self) -> str:
        """
        Return a string representation of the code context line.

        Returns
        -------
        str
            A formatted string with a marker for the error line.
        """
        marker = ">>>" if self.is_error_line else "   "
        return f"{marker} {self.line_number:4d}: {self.code}"


@dataclass
class StackFrame:
    """
    Represents a single frame in the call stack.

    Attributes
    ----------
    file_path : str
        The absolute path to the file of the frame.
    line_number : int
        The line number in the file where the exception occurred.
    function_name : str
        The name of the function or module for the frame.
    code_line : str | None
        The line of code that was executed.
    locals_info : dict[str, any] | None, optional
        A dictionary of local variables in the frame, by default None.
    module_name : str | None, optional
        The name of the module, by default None.
    is_stdlib : bool
        True if the frame is part of the Python standard library.
    is_site_packages : bool
        True if the frame is part of an installed third-party package.
    context_lines : list[CodeContext]
        A list of code context lines around the error line.
    """

    file_path: str
    line_number: int
    function_name: str
    code_line: str | None
    locals_info: dict[str, Any] | None = None
    module_name: str | None = None
    is_stdlib: bool = False
    is_site_packages: bool = False
    context_lines: list[CodeContext] | None = None

    def __post_init__(self):
        """Perform post-initialization processing."""
        if self.context_lines is None:
            self.context_lines = []

        if "site-packages" in self.file_path or ".venv" in self.file_path:
            self.is_site_packages = True
        elif self.file_path.startswith(sys.prefix):
            self.is_stdlib = True

        if self.file_path and not self.module_name:
            path = Path(self.file_path)
            if path.suffix == ".py":
                self.module_name = path.stem

    def get_relative_path(self, base_path: str | None = None) -> str:
        """
        Return the relative path of the file.

        If a `base_path` is provided, the file path is made relative to it.

        Parameters
        ----------
        base_path : str, optional
            The base path to make the file path relative to, by default None.

        Returns
        -------
        str
            The relative file path, or the full path if it cannot be made
            relative.
        """
        if base_path:
            try:
                return str(Path(self.file_path).relative_to(base_path))
            except ValueError:
                pass
        return self.file_path

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the stack frame to a dictionary.

        Returns
        -------
        dict[str, any]
            A dictionary representation of the stack frame.
        """
        return asdict(self)


@dataclass
class ExceptionInfo:
    """
    Contains information about an exception.

    Attributes
    ----------
    exception_type : str
        The type of the exception (e.g., 'ValueError').
    exception_message : str
        The message of the exception.
    exception_module : str | None, optional
        The module where the exception is defined, by default None.
    cause : 'ExceptionInfo | None', optional
        The direct cause of this exception (chained exception), by default None.
    context : 'ExceptionInfo | None', optional
        The context of this exception, by default None.
    """

    exception_type: str
    exception_message: str
    exception_module: str | None = None
    cause: "ExceptionInfo | None" = None
    context: "ExceptionInfo | None" = None

    def get_full_type(self) -> str:
        """
        Return the full type of the exception, including the module.

        Returns
        -------
        str
            The full exception type (e.g., 'builtins.ValueError').
        """
        if self.exception_module:
            return f"{self.exception_module}.{self.exception_type}"
        return self.exception_type

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the exception info to a dictionary.

        Returns
        -------
        dict[str, any]
            A dictionary representation of the exception info.
        """
        result = {
            "type": self.exception_type,
            "message": self.exception_message,
            "full_type": self.get_full_type(),
        }
        if self.cause:
            result["cause"] = self.cause.to_dict()  # type: ignore
        if self.context:
            result["context"] = self.context.to_dict()  # type: ignore
        return result


@dataclass
class ParsedTraceback:
    """
    Represents a fully parsed and structured traceback.

    Attributes
    ----------
    exception : ExceptionInfo
        The details of the exception that was raised.
    stack_frames : list[StackFrame]
        A list of stack frames from the traceback, ordered from oldest to newest.
    raw_traceback : str
        The original, unparsed traceback string.
    timestamp : datetime
        The timestamp when the traceback was parsed.
    python_version : str
        The Python version used when the traceback was generated.
    """

    exception: ExceptionInfo
    stack_frames: list[StackFrame]
    raw_traceback: str
    timestamp: datetime | None = None
    python_version: str | None = None

    def __post_init__(self):
        """Add metadata after initialization."""
        if not self.timestamp:
            self.timestamp = datetime.now()
        if not self.python_version:
            self.python_version = (
                f"{sys.version_info.major}.{sys.version_info.minor}."
                f"{sys.version_info.micro}"
            )

    def get_error_location(self) -> StackFrame | None:
        """
        Return the frame where the error occurred (the last frame).

        Returns
        -------
        StackFrame | None
            The last stack frame in the call stack, or None if it's empty.
        """
        return self.stack_frames[-1] if self.stack_frames else None

    def get_user_frames(self) -> list[StackFrame]:
        """
        Return only the frames from the user's code.

        Filters out frames from the standard library and site-packages.

        Returns
        -------
        list[StackFrame]
            A list of stack frames belonging to the user's application code.
        """
        return [
            f for f in self.stack_frames if not f.is_stdlib and not f.is_site_packages
        ]

    def get_call_chain(self) -> list[str]:
        """
        Return the call chain as a list of formatted strings.

        Returns
        -------
        list[str]
            A list of strings, each representing a function call in the stack.
        """
        return [
            f"{frame.function_name} ({frame.file_path}:{frame.line_number})"
            for frame in self.stack_frames
        ]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the parsed traceback to a dictionary.

        Returns
        -------
        dict[str, any]
            A dictionary representation of the parsed traceback.
        """
        error_location = self.get_error_location()
        return {
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "python_version": self.python_version,
            "exception": self.exception.to_dict(),
            "stack_frames": [frame.to_dict() for frame in self.stack_frames],
            "error_location": error_location.to_dict() if error_location else None,
            "call_chain": self.get_call_chain(),
        }

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the parsed traceback to a JSON formatted string.

        Parameters
        ----------
        indent : int, optional
            The number of spaces to use for indentation, by default 2.

        Returns
        -------
        str
            A JSON string representing the parsed traceback.
        """
        import json

        return json.dumps(self.to_dict(), indent=indent, default=str)
