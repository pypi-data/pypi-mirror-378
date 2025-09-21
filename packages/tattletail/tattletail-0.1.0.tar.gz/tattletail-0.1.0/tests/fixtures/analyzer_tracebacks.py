"""
Traceback fixtures specifically for analyzer testing.
"""

# Template for minimal traceback with different exception types
MINIMAL_TRACEBACK_TEMPLATE = """Traceback (most recent call last):
  File "test.py", line 1, in <module>
    raise Exception()
{exception_line}"""

# Exception types for probable cause testing
PROBABLE_CAUSE_TEST_CASES = [
    ("NameError", "variable or function name"),
    ("TypeError", "inappropriate type"),
    ("ValueError", "right type but an invalid value"),
    ("KeyError", "dictionary key"),
    ("IndexError", "subscript is out of range"),
    ("AttributeError", "attribute reference"),
    ("ImportError", "import"),
    ("FileNotFoundError", "file or directory"),
    ("ZeroDivisionError", "division or modulo"),
]
