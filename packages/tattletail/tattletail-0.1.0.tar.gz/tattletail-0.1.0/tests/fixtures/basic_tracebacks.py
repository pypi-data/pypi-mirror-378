"""
Basic traceback fixtures for testing common scenarios.
"""

# Core simple traceback with multiple frames
SIMPLE_TRACEBACK = """Traceback (most recent call last):
  File "/home/user/project/main.py", line 45, in main
    result = process_data(data)
  File "/home/user/project/processor.py", line 23, in process_data
    cleaned = clean_values(data['values'])
  File "/home/user/project/utils.py", line 78, in clean_values
    return [int(v) for v in values]
  File "/home/user/project/utils.py", line 78, in <listcomp>
    return [int(v) for v in values]
ValueError: invalid literal for int() with base 10: 'abc'
"""

# Simple ValueError traceback
BASIC_VALUE_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    raise Exception()
ValueError: Test error"""

# Simple ValueError without full traceback (just exception line)
EXCEPTION_ONLY = "ValueError: Something went wrong"

# ValueError with empty message
VALUE_ERROR_NO_MESSAGE = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    raise Exception()
ValueError:"""

# Frame without function name
FRAME_NO_FUNCTION = """Traceback (most recent call last):
  File "test.py", line 1
    some_code()
ValueError: Test error"""

# ConnectionError with multiple colons
CONNECTION_ERROR_MULTI_COLONS = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    some_code()
ConnectionError: Failed to connect to server: connection timeout: 30s"""

# Simple traceback for context extraction (nonexistent file)
CONTEXT_NONEXISTENT_FILE = """Traceback (most recent call last):
  File "/nonexistent/file.py", line 10, in test_func
    some_code()
ValueError: Test error"""

# Simple traceback for context disabled
CONTEXT_DISABLED = """Traceback (most recent call last):
  File "/some/file.py", line 10, in test_func
    some_code()
ValueError: Test error"""

# Simple traceback with code characters
SPECIAL_CHARACTERS = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    print("HelloWorld")
ValueError: Test error"""

# Template for dynamic long path (requires formatting)
LONG_PATH_TEMPLATE = """Traceback (most recent call last):
  File "{long_path}", line 1, in test_function
    some_code()
ValueError: Test error"""

# Template for dynamic file path in context extraction (requires formatting)
CONTEXT_EXTRACTION_TEMPLATE = """Traceback (most recent call last):
  File "{temp_path}", line 4, in hello
    y = 2  # This is line 4
ValueError: Test error"""
