"""
Complex traceback fixtures including chained exceptions and recursion.
"""

# Core chained traceback with exception cause
CHAINED_TRACEBACK = """Traceback (most recent call last):
  File "/home/user/project/main.py", line 10, in <module>
    main()
  File "/home/user/project/main.py", line 7, in main
    level1()
  File "/home/user/project/funcs.py", line 5, in level1
    level2()
  File "/home/user/project/funcs.py", line 9, in level2
    raise ValueError("level2 error")
ValueError: level2 error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/user/project/main.py", line 10, in <module>
    main()
  File "/home/user/project/main.py", line 7, in main
    level1()
RuntimeError: Something went wrong
"""

# Complex chained exception scenario
COMPLEX_CHAINED_EXCEPTIONS = """Traceback (most recent call last):
  File "test1.py", line 1, in func1
    func2()
  File "test2.py", line 2, in func2
    raise ValueError("Original error")
ValueError: Original error

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "test3.py", line 3, in func3
    func1()
  File "test1.py", line 1, in func1
    func2()
RuntimeError: Handling error

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "main.py", line 4, in main
    func3()
  File "test3.py", line 3, in func3
    func1()
FinalError: Final error"""

# Recursive traceback pattern
RECURSIVE_TRACEBACK = """Traceback (most recent call last):
  File "test.py", line 1, in factorial
    return factorial(n-1)
  File "test.py", line 1, in factorial
    return factorial(n-1)
  File "test.py", line 1, in factorial
    return factorial(n-1)
  File "test.py", line 1, in factorial
    return factorial(n-1)
  File "test.py", line 1, in factorial
    return factorial(n-1)
RecursionError: maximum recursion depth exceeded"""

# Unicode characters in traceback
UNICODE_TRACEBACK = """Traceback (most recent call last):
  File "tëst.py", line 1, in 测试函数
    raise Exception()
ValueError: Unicode message: こんにちは"""

# Unicode traceback for main interface testing
UNICODE_MAIN_INTERFACE = """Traceback (most recent call last):
  File "test_файл.py", line 1, in 测试函数
    raise Exception()
UnicodeError: Тест unicode сообщение"""

# Long exception message for summary testing
LONG_MESSAGE_TRACEBACK = (
    """Traceback (most recent call last):
  File "test.py", line 1, in long_function_name
    raise Exception()
ValueError: This is a very long error message that should be truncated when it """
    """exceeds the maximum length limit for summaries to keep them concise and """
    """readable and should definitely be longer than any reasonable summary limit"""
)
