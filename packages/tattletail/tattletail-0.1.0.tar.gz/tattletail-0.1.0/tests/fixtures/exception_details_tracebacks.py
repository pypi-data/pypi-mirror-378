"""
Exception details traceback fixtures for testing exception analysis functionality.
"""

# Basic ZeroDivisionError
ZERO_DIVISION_ERROR = """Traceback (most recent call last):
  File "test.py", line 10, in main
    result = 10 / 0
ZeroDivisionError: division by zero
"""

# IndexError with hierarchy testing
INDEX_ERROR = """Traceback (most recent call last):
  File "test.py", line 5, in func
    values[10]
IndexError: list index out of range
"""

# Custom exception for hierarchy testing
CUSTOM_ERROR = """Traceback (most recent call last):
  File "test.py", line 5, in func
    raise CustomError("something went wrong")
CustomError: something went wrong
"""

# ValueError for module testing
VALUE_ERROR_MODULE = """Traceback (most recent call last):
  File "test.py", line 5, in func
    raise ValueError("bad value")
ValueError: bad value
"""

# Chained exceptions with cause
CHAINED_EXCEPTION_CAUSE = """Traceback (most recent call last):
  File "test.py", line 3, in func1
    func2()
  File "test.py", line 6, in func2
    1 / 0
ZeroDivisionError: division by zero

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "test.py", line 10, in main
    func1()
  File "test.py", line 4, in func1
    raise ValueError("calculation failed") from e
ValueError: calculation failed
"""

# KeyError for hierarchy testing
KEY_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise KeyError("test error")
KeyError: test error
"""

# TypeError for hierarchy testing
TYPE_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise TypeError("test error")
TypeError: test error
"""

# NameError for hierarchy testing
NAME_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise NameError("test error")
NameError: test error
"""

# AttributeError for hierarchy testing
ATTRIBUTE_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise AttributeError("test error")
AttributeError: test error
"""

# ImportError for hierarchy testing
IMPORT_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise ImportError("test error")
ImportError: test error
"""

# ModuleNotFoundError for hierarchy testing
MODULE_NOT_FOUND_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise ModuleNotFoundError("test error")
ModuleNotFoundError: test error
"""

# FileNotFoundError for hierarchy testing
FILE_NOT_FOUND_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise FileNotFoundError("test error")
FileNotFoundError: test error
"""

# PermissionError for hierarchy testing
PERMISSION_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise PermissionError("test error")
PermissionError: test error
"""

# RecursionError for hierarchy testing
RECURSION_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise RecursionError("test error")
RecursionError: test error
"""

# MemoryError for hierarchy testing
MEMORY_ERROR = """Traceback (most recent call last):
  File "test.py", line 1, in func
    raise MemoryError("test error")
MemoryError: test error
"""
