"""
Edge case and malformed traceback fixtures for robust testing.
"""

# Empty traceback
EMPTY_TRACEBACK = ""

# Malformed traceback with random text
MALFORMED_TRACEBACK = """This is not a traceback
Just some random text
With: colons but no structure"""

# Exception lines for parser internal testing
EXCEPTION_LINES_TEST_CASES = [
    # Should be exception lines
    "ValueError: Invalid value",
    "RuntimeError: Something went wrong",
    "CustomError: Custom message",
]

NON_EXCEPTION_LINES_TEST_CASES = [
    # Should NOT be exception lines
    '  File "test.py", line 1, in <module>',
    "Traceback (most recent call last):",
    "The above exception was the direct cause",
    "During handling of the above exception",
    "",
    "    some_code()",
]

# Simple exception for reset functionality testing
RESET_TEST_EXCEPTION = "ValueError: test"
