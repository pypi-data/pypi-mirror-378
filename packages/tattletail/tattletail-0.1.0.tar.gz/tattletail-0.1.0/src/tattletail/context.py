"""
Context manager functionality for Tattletail.

This module provides context managers for elegant exception capture and analysis.
"""

from types import TracebackType
from typing import Any
from typing import Callable
from typing import Optional
from typing import Type
from typing import Union

from .analyzer import TracebackAnalyzer
from .models import ParsedTraceback
from .parser import TracebackParser


class ErrorCapture:
    """
    Context manager for automatic exception capture and analysis.

    Examples
    --------
    >>> with tattletail.capture() as ctx:
    ...     risky_operation()
    >>> if ctx.exception:
    ...     print(ctx.analysis["summary"])
    """

    def __init__(
        self,
        extract_context: bool = False,
        suppress: bool = False,
        on_exception: Optional[Callable] = None,
    ):
        """
        Initialize the error capture context manager.

        Parameters
        ----------
        extract_context : bool, optional
            Whether to extract source code context around errors
        suppress : bool, optional
            Whether to suppress the exception (don't re-raise)
        on_exception : callable, optional
            Function to call when an exception occurs
        """
        self.extract_context = extract_context
        self.suppress = suppress
        self.on_exception = on_exception

        # Results
        self.exception: Optional[BaseException] = None
        self.parsed: Optional[ParsedTraceback] = None
        self.analysis: Optional[dict[str, Any]] = None

        # Internal
        self._parser = TracebackParser(extract_context=extract_context)
        self._analyzer = TracebackAnalyzer()

    def __enter__(self) -> "ErrorCapture":
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """Exit the context manager and process any exception."""
        if exc_type is not None and exc_value is not None and traceback is not None:
            # Capture the exception
            self.exception = exc_value

            # Parse and analyze
            self.parsed = self._parser.parse_from_exception(
                (exc_type, exc_value, traceback)
            )
            self.analysis = self._analyzer.analyze_parsed(self.parsed)

            # Call user callback if provided
            if self.on_exception:
                self.on_exception(self)

        # Return True to suppress exception, False to re-raise
        return self.suppress


class ErrorExpector:
    """
    Context manager for testing expected exceptions.

    Examples
    --------
    >>> with tattletail.expect(ValueError) as ctx:
    ...     int("invalid")
    >>> assert ctx.matched
    >>> assert "invalid literal" in ctx.analysis["summary"]
    """

    def __init__(
        self,
        expected_type: Union[Type[BaseException], tuple[Type[BaseException], ...]],
        expected_message: Optional[str] = None,
        extract_context: bool = False,
    ):
        """
        Initialize the error expectation context manager.

        Parameters
        ----------
        expected_type : type or tuple of types
            Expected exception type(s)
        expected_message : str, optional
            Expected substring in exception message
        extract_context : bool, optional
            Whether to extract source code context
        """
        self.expected_type = expected_type
        self.expected_message = expected_message
        self.extract_context = extract_context

        # Results
        self.exception: Optional[BaseException] = None
        self.parsed: Optional[ParsedTraceback] = None
        self.analysis: Optional[dict[str, Any]] = None
        self.matched: bool = False

        # Internal
        self._parser = TracebackParser(extract_context=extract_context)
        self._analyzer = TracebackAnalyzer()

    def __enter__(self) -> "ErrorExpector":
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """Exit and check if the expected exception occurred."""
        if exc_type is not None and exc_value is not None and traceback is not None:
            # Check if exception type matches
            type_matches = isinstance(exc_value, self.expected_type)

            # Check if message matches (if specified)
            message_matches = True
            if self.expected_message is not None:
                message_matches = self.expected_message in str(exc_value)

            if type_matches and message_matches:
                # Expected exception occurred
                self.exception = exc_value
                self.parsed = self._parser.parse_from_exception(
                    (exc_type, exc_value, traceback)
                )
                self.analysis = self._analyzer.analyze_parsed(self.parsed)
                self.matched = True
                return True  # Suppress the exception
            else:
                # Unexpected exception
                self.matched = False
                return False  # Let it propagate
        else:
            # No exception occurred
            self.matched = False
            # Could raise an assertion error here if desired
            return False


class ErrorMonitor:
    """
    Context manager for production error monitoring with automatic logging.

    Examples
    --------
    >>> import logging
    >>> logger = logging.getLogger(__name__)
    >>> with tattletail.monitor(logger=logger) as ctx:
    ...     process_request()
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        level: str = "ERROR",
        extract_context: bool = False,
        suppress: bool = False,
        include_analysis: bool = True,
    ):
        """
        Initialize the error monitoring context manager.

        Parameters
        ----------
        logger : logging.Logger, optional
            Logger instance to use for error reporting
        level : str, optional
            Logging level for error messages
        extract_context : bool, optional
            Whether to extract source code context
        suppress : bool, optional
            Whether to suppress exceptions after logging
        include_analysis : bool, optional
            Whether to include analysis in log messages
        """
        self.logger = logger
        self.level = level.upper()
        self.extract_context = extract_context
        self.suppress = suppress
        self.include_analysis = include_analysis

        # Results
        self.exception: Optional[BaseException] = None
        self.parsed: Optional[ParsedTraceback] = None
        self.analysis: Optional[dict[str, Any]] = None

        # Internal
        self._parser = TracebackParser(extract_context=extract_context)
        self._analyzer = TracebackAnalyzer()

    def __enter__(self) -> "ErrorMonitor":
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        """Exit and log any exception that occurred."""
        if exc_type is not None and exc_value is not None and traceback is not None:
            # Capture the exception
            self.exception = exc_value
            self.parsed = self._parser.parse_from_exception(
                (exc_type, exc_value, traceback)
            )

            if self.include_analysis:
                self.analysis = self._analyzer.analyze_parsed(self.parsed)

            # Log the error if logger is provided
            if self.logger:
                self._log_error()

        return self.suppress

    def _log_error(self) -> None:
        """Log the captured error with structured information."""
        if not self.logger or not self.parsed:
            return

        # Basic error information
        error_location = self.parsed.get_error_location()
        if error_location:
            log_msg = (
                f"Exception captured: {self.parsed.exception.exception_type} "
                f"in {error_location.function_name} "
                f"({error_location.file_path}:{error_location.line_number})"
            )
            extra_data = {
                "exception_type": self.parsed.exception.exception_type,
                "exception_message": self.parsed.exception.exception_message,
                "file_path": error_location.file_path,
                "line_number": error_location.line_number,
                "function_name": error_location.function_name,
                "call_chain": self.parsed.get_call_chain(),
                "frame_count": len(self.parsed.stack_frames),
            }
        else:
            log_msg = f"Exception captured: {self.parsed.exception.exception_type}"
            extra_data = {
                "exception_type": self.parsed.exception.exception_type,
                "exception_message": self.parsed.exception.exception_message,
                "call_chain": self.parsed.get_call_chain(),
                "frame_count": len(self.parsed.stack_frames),
            }

        # Add analysis if available
        if self.analysis:
            extra_data.update(
                {
                    "probable_cause": self.analysis["probable_cause"],
                    "call_depth": self.analysis["patterns"]["call_depth"],
                    "is_recursive": self.analysis["patterns"]["is_recursive"],
                    "error_in_stdlib": self.analysis["patterns"]["error_in_stdlib"],
                }
            )
            log_msg += f" | Cause: {self.analysis['probable_cause']}"

        # Log with appropriate level
        log_method = getattr(self.logger, self.level.lower(), self.logger.error)
        log_method(log_msg, extra=extra_data)


# Convenience functions for easier imports
def capture(
    extract_context: bool = False,
    suppress: bool = False,
    on_exception: Optional[Callable] = None,
) -> ErrorCapture:
    """
    Create an ErrorCapture context manager.

    Parameters
    ----------
    extract_context : bool, optional
        Whether to extract source code context around errors
    suppress : bool, optional
        Whether to suppress the exception (don't re-raise)
    on_exception : callable, optional
        Function to call when an exception occurs

    Returns
    -------
    ErrorCapture
        Context manager for capturing exceptions

    Examples
    --------
    >>> with capture() as ctx:
    ...     risky_operation()
    >>> if ctx.exception:
    ...     print(ctx.analysis["summary"])
    """
    return ErrorCapture(
        extract_context=extract_context, suppress=suppress, on_exception=on_exception
    )


def expect(
    expected_type: Union[Type[BaseException], tuple[Type[BaseException], ...]],
    expected_message: Optional[str] = None,
    extract_context: bool = False,
) -> ErrorExpector:
    """
    Create an ErrorExpector context manager for testing.

    Parameters
    ----------
    expected_type : type or tuple of types
        Expected exception type(s)
    expected_message : str, optional
        Expected substring in exception message
    extract_context : bool, optional
        Whether to extract source code context

    Returns
    -------
    ErrorExpector
        Context manager for testing expected exceptions

    Examples
    --------
    >>> with expect(ValueError, "invalid") as ctx:
    ...     int("invalid")
    >>> assert ctx.matched
    """
    return ErrorExpector(
        expected_type=expected_type,
        expected_message=expected_message,
        extract_context=extract_context,
    )


def monitor(
    logger: Optional[Any] = None,
    level: str = "ERROR",
    extract_context: bool = False,
    suppress: bool = False,
    include_analysis: bool = True,
) -> ErrorMonitor:
    """
    Create an ErrorMonitor context manager for production monitoring.

    Parameters
    ----------
    logger : logging.Logger, optional
        Logger instance to use for error reporting
    level : str, optional
        Logging level for error messages
    extract_context : bool, optional
        Whether to extract source code context
    suppress : bool, optional
        Whether to suppress exceptions after logging
    include_analysis : bool, optional
        Whether to include analysis in log messages

    Returns
    -------
    ErrorMonitor
        Context manager for monitoring exceptions

    Examples
    --------
    >>> import logging
    >>> logger = logging.getLogger(__name__)
    >>> with monitor(logger=logger) as ctx:
    ...     process_request()
    """
    return ErrorMonitor(
        logger=logger,
        level=level,
        extract_context=extract_context,
        suppress=suppress,
        include_analysis=include_analysis,
    )
