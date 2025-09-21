"""
Tests for the data models.
"""

from datetime import datetime
import json

from tattletail.models import CodeContext
from tattletail.models import ExceptionInfo
from tattletail.models import ParsedTraceback
from tattletail.models import StackFrame


class TestCodeContext:
    """Test the CodeContext model."""

    def test_create_code_context(self):
        """Test creation of CodeContext."""
        context = CodeContext(
            line_number=42, code="print('Hello, World!')", is_error_line=True
        )

        assert context.line_number == 42
        assert context.code == "print('Hello, World!')"
        assert context.is_error_line is True

    def test_code_context_str_error_line(self):
        """Test string representation of error line."""
        context = CodeContext(line_number=10, code="x = y + z", is_error_line=True)

        str_repr = str(context)
        assert ">>>" in str_repr
        assert "10" in str_repr
        assert "x = y + z" in str_repr

    def test_code_context_str_normal_line(self):
        """Test string representation of normal line."""
        context = CodeContext(line_number=5, code="import sys", is_error_line=False)

        str_repr = str(context)
        assert "   " in str_repr  # Three spaces, not >>>
        assert "5" in str_repr
        assert "import sys" in str_repr


class TestStackFrame:
    """Test the StackFrame model."""

    def test_create_stack_frame(self):
        """Test creation of StackFrame."""
        frame = StackFrame(
            file_path="/home/user/project/main.py",
            line_number=42,
            function_name="main",
            code_line="result = process_data(data)",
        )

        assert frame.file_path == "/home/user/project/main.py"
        assert frame.line_number == 42
        assert frame.function_name == "main"
        assert frame.code_line == "result = process_data(data)"
        assert frame.locals_info is None
        assert frame.is_stdlib is False
        assert frame.is_site_packages is False
        assert frame.context_lines == []

    def test_stack_frame_post_init_site_packages(self):
        """Test post-init processing for site-packages detection."""
        frame = StackFrame(
            file_path="/usr/lib/python3.12/site-packages/requests/api.py",
            line_number=10,
            function_name="get",
            code_line="return request('get', url, **kwargs)",
        )

        assert frame.is_site_packages is True
        assert frame.is_stdlib is False
        assert frame.module_name == "api"

    def test_stack_frame_post_init_venv(self):
        """Test post-init processing for venv detection."""
        frame = StackFrame(
            file_path="/home/user/.venv/lib/python3.12/site-packages/flask/app.py",
            line_number=20,
            function_name="run",
            code_line="app.run()",
        )

        assert frame.is_site_packages is True
        assert frame.is_stdlib is False

    def test_stack_frame_post_init_stdlib(self):
        """Test post-init processing for stdlib detection."""
        import sys

        # Use a path that's definitely in the stdlib (not venv)
        stdlib_path = "/usr/lib/python3.12/json/decoder.py"

        frame = StackFrame(
            file_path=stdlib_path,
            line_number=30,
            function_name="decode",
            code_line="return json.loads(s)",
        )

        # This will only be True if the path actually starts with sys.prefix
        # In venv/container environments, this test verifies the logic works
        if stdlib_path.startswith(sys.prefix):
            assert frame.is_stdlib is True
            assert frame.is_site_packages is False
        else:
            # In environments where /usr/lib isn't the stdlib location,
            # it should not be marked as stdlib
            assert frame.is_stdlib is False

    def test_stack_frame_module_name_extraction(self):
        """Test module name extraction from file path."""
        frame = StackFrame(
            file_path="/home/user/myproject/utils/helpers.py",
            line_number=1,
            function_name="helper_func",
            code_line="pass",
        )

        assert frame.module_name == "helpers"

    def test_stack_frame_no_module_name_for_non_py(self):
        """Test that non-.py files don't get module names."""
        frame = StackFrame(
            file_path="/home/user/script.sh",
            line_number=1,
            function_name="main",
            code_line="echo hello",
        )

        # Should not set module_name for non-Python files
        assert frame.module_name is None

    def test_get_relative_path_with_base(self):
        """Test getting relative path with base path."""
        frame = StackFrame(
            file_path="/home/user/project/src/main.py",
            line_number=1,
            function_name="main",
            code_line="pass",
        )

        relative = frame.get_relative_path("/home/user/project")
        assert relative == "src/main.py"

    def test_get_relative_path_without_base(self):
        """Test getting relative path without base path."""
        frame = StackFrame(
            file_path="/home/user/project/main.py",
            line_number=1,
            function_name="main",
            code_line="pass",
        )

        relative = frame.get_relative_path()
        assert relative == "/home/user/project/main.py"

    def test_get_relative_path_invalid_base(self):
        """Test getting relative path with invalid base path."""
        frame = StackFrame(
            file_path="/home/user/project/main.py",
            line_number=1,
            function_name="main",
            code_line="pass",
        )

        relative = frame.get_relative_path("/different/path")
        assert relative == "/home/user/project/main.py"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        context = CodeContext(line_number=1, code="test", is_error_line=True)
        frame = StackFrame(
            file_path="/test.py",
            line_number=1,
            function_name="test",
            code_line="pass",
            locals_info={"var": "value"},
            context_lines=[context],
        )

        frame_dict = frame.to_dict()

        assert isinstance(frame_dict, dict)
        assert frame_dict["file_path"] == "/test.py"
        assert frame_dict["line_number"] == 1
        assert frame_dict["function_name"] == "test"
        assert frame_dict["locals_info"] == {"var": "value"}
        assert len(frame_dict["context_lines"]) == 1


class TestExceptionInfo:
    """Test the ExceptionInfo model."""

    def test_create_exception_info(self):
        """Test creation of ExceptionInfo."""
        exc = ExceptionInfo(
            exception_type="ValueError",
            exception_message="Invalid value provided",
            exception_module="builtins",
        )

        assert exc.exception_type == "ValueError"
        assert exc.exception_message == "Invalid value provided"
        assert exc.exception_module == "builtins"
        assert exc.cause is None
        assert exc.context is None

    def test_get_full_type_with_module(self):
        """Test get_full_type with module."""
        exc = ExceptionInfo(
            exception_type="ValueError",
            exception_message="test",
            exception_module="builtins",
        )

        assert exc.get_full_type() == "builtins.ValueError"

    def test_get_full_type_without_module(self):
        """Test get_full_type without module."""
        exc = ExceptionInfo(exception_type="CustomError", exception_message="test")

        assert exc.get_full_type() == "CustomError"

    def test_to_dict_simple(self):
        """Test conversion to dictionary without chaining."""
        exc = ExceptionInfo(
            exception_type="RuntimeError",
            exception_message="Something went wrong",
            exception_module="builtins",
        )

        exc_dict = exc.to_dict()

        assert exc_dict["type"] == "RuntimeError"
        assert exc_dict["message"] == "Something went wrong"
        assert exc_dict["full_type"] == "builtins.RuntimeError"
        assert "cause" not in exc_dict
        assert "context" not in exc_dict

    def test_to_dict_with_cause(self):
        """Test conversion to dictionary with cause."""
        cause = ExceptionInfo("ValueError", "Original error")
        exc = ExceptionInfo(
            exception_type="RuntimeError",
            exception_message="Wrapper error",
            cause=cause,
        )

        exc_dict = exc.to_dict()

        assert "cause" in exc_dict
        assert exc_dict["cause"]["type"] == "ValueError"
        assert exc_dict["cause"]["message"] == "Original error"

    def test_to_dict_with_context(self):
        """Test conversion to dictionary with context."""
        context = ExceptionInfo("KeyError", "Missing key")
        exc = ExceptionInfo(
            exception_type="AttributeError",
            exception_message="Attribute missing",
            context=context,
        )

        exc_dict = exc.to_dict()

        assert "context" in exc_dict
        assert exc_dict["context"]["type"] == "KeyError"
        assert exc_dict["context"]["message"] == "Missing key"


class TestParsedTraceback:
    """Test the ParsedTraceback model."""

    def test_create_parsed_traceback(self):
        """Test creation of ParsedTraceback."""
        exc = ExceptionInfo("ValueError", "Test error")
        frame = StackFrame("/test.py", 1, "main", "pass")

        tb = ParsedTraceback(
            exception=exc,
            stack_frames=[frame],
            raw_traceback="Traceback...",
        )

        assert tb.exception == exc
        assert len(tb.stack_frames) == 1
        assert tb.raw_traceback == "Traceback..."
        assert tb.timestamp is not None
        assert tb.python_version is not None

    def test_post_init_timestamp(self):
        """Test that timestamp is set in post_init."""
        exc = ExceptionInfo("ValueError", "Test")
        tb = ParsedTraceback(exc, [], "test")

        assert isinstance(tb.timestamp, datetime)

    def test_post_init_python_version(self):
        """Test that Python version is set in post_init."""
        exc = ExceptionInfo("ValueError", "Test")
        tb = ParsedTraceback(exc, [], "test")

        assert isinstance(tb.python_version, str)
        assert "." in tb.python_version  # Should be like "3.12.2"

    def test_get_error_location(self):
        """Test getting error location (last frame)."""
        frames = [
            StackFrame("/test1.py", 1, "func1", "pass"),
            StackFrame("/test2.py", 2, "func2", "pass"),
            StackFrame("/test3.py", 3, "func3", "pass"),
        ]

        exc = ExceptionInfo("ValueError", "Test")
        tb = ParsedTraceback(exc, frames, "test")

        error_location = tb.get_error_location()
        assert error_location is not None
        assert error_location.file_path == "/test3.py"
        assert error_location.line_number == 3

    def test_get_error_location_empty(self):
        """Test getting error location with no frames."""
        exc = ExceptionInfo("ValueError", "Test")
        tb = ParsedTraceback(exc, [], "test")

        error_location = tb.get_error_location()
        assert error_location is None

    def test_get_user_frames(self):
        """Test filtering user frames."""
        import sys

        frames = [
            StackFrame("/home/user/app.py", 1, "main", "pass"),  # User
            StackFrame(
                f"{sys.prefix}/lib/python3.12/json/decoder.py", 2, "decode", "pass"
            ),  # Stdlib
            StackFrame(
                "/usr/lib/python3.12/site-packages/requests/api.py", 3, "get", "pass"
            ),  # Site-packages
            StackFrame("/home/user/utils.py", 4, "helper", "pass"),  # User
        ]

        exc = ExceptionInfo("ValueError", "Test")
        tb = ParsedTraceback(exc, frames, "test")

        user_frames = tb.get_user_frames()
        assert len(user_frames) == 2
        assert user_frames[0].file_path == "/home/user/app.py"
        assert user_frames[1].file_path == "/home/user/utils.py"

    def test_get_call_chain(self):
        """Test getting call chain."""
        frames = [
            StackFrame("/app.py", 10, "main", "pass"),
            StackFrame("/utils.py", 20, "helper", "pass"),
            StackFrame("/core.py", 30, "process", "pass"),
        ]

        exc = ExceptionInfo("ValueError", "Test")
        tb = ParsedTraceback(exc, frames, "test")

        call_chain = tb.get_call_chain()
        assert len(call_chain) == 3
        assert call_chain[0] == "main (/app.py:10)"
        assert call_chain[1] == "helper (/utils.py:20)"
        assert call_chain[2] == "process (/core.py:30)"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        frames = [StackFrame("/test.py", 1, "main", "pass")]
        exc = ExceptionInfo("ValueError", "Test error")
        tb = ParsedTraceback(exc, frames, "Traceback...")

        tb_dict = tb.to_dict()

        assert "timestamp" in tb_dict
        assert "python_version" in tb_dict
        assert "exception" in tb_dict
        assert "stack_frames" in tb_dict
        assert "error_location" in tb_dict
        assert "call_chain" in tb_dict

        assert tb_dict["exception"]["type"] == "ValueError"
        assert len(tb_dict["stack_frames"]) == 1
        assert len(tb_dict["call_chain"]) == 1

    def test_to_json(self):
        """Test conversion to JSON."""
        frame = StackFrame("/test.py", 1, "main", "pass")
        exc = ExceptionInfo("ValueError", "Test error")
        tb = ParsedTraceback(exc, [frame], "Traceback...")

        json_str = tb.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert "exception" in parsed
        assert "stack_frames" in parsed

        # Test custom indentation
        json_str_indent4 = tb.to_json(indent=4)
        assert json_str_indent4 != json_str  # Should be different formatting

    def test_to_json_with_custom_indent(self):
        """Test JSON conversion with custom indentation."""
        frame = StackFrame("/test.py", 1, "main", "pass")
        exc = ExceptionInfo("ValueError", "Test")
        tb = ParsedTraceback(exc, [frame], "test")

        json_str = tb.to_json(indent=4)
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
