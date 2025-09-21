# Tattletail

[![PyPI version](https://badge.fury.io/py/tattletail.svg)](https://badge.fury.io/py/tattletail)
[![Python Support](https://img.shields.io/pypi/pyversions/tattletail.svg)](https://pypi.org/project/tattletail/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![CI](https://github.com/ericmiguel/tattletail/actions/workflows/ci.yaml/badge.svg)](https://github.com/ericmiguel/tattletail/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/ericmiguel/tattletail/branch/main/graph/badge.svg)](https://codecov.io/gh/ericmiguel/tattletail)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)

Python tracebacks like structured, analyzable data with rich insights.

## 📌 What is Tattletail?

Don't get me wrong, I love Python's native traceback capabilities, but Tattletail transforms this traceback:

```python
Traceback (most recent call last):
  File "/app/main.py", line 45, in process_data
    result = clean_values(data['values'])
  File "/app/utils.py", line 78, in clean_values
    return [int(v) for v in values]
ValueError: invalid literal for int() with base 10: 'abc'
```

Into this structured analysis:

```python
{
    "summary": "ValueError in clean_values (utils.py:78): invalid literal for int()",
    "exception": {
        "class": "ValueError",
        "name": "ValueError",
        "message": "invalid literal for int() with base 10: 'abc'",
        "module": None,
        "full_name": "ValueError",
        "hierarchy": ["BaseException", "Exception", "ValueError"],
        "line_number": 78,
        "file_path": "/app/utils.py",
        "function_name": "clean_values",
        "has_cause": False,
        "has_context": False
    },
    "probable_cause": "A function received an argument with the right type but an invalid value.",
    "patterns": {
        "call_depth": 2,
        "is_recursive": False,
        "error_in_stdlib": False
    },
    "metrics": {
        "total_frames": 2,
        "user_frames": 2,
        "unique_files": 2
    }
}
```

Tattletail is suitable and friendly for debugging, error monitoring, historical log analysis, and building intelligent development tools.

## 🚀 **Quick Start**

### Installation

```bash
uv add tattletail  # or pip install tattletail
```

### Basic Example

```python
import tattletail

# Parse a traceback string
traceback_text = """
Traceback (most recent call last):
  File "example.py", line 10, in main
    result = divide(10, 0)
ZeroDivisionError: division by zero
"""

# Get structured analysis
analysis = tattletail.analyze(traceback_text)
print(analysis['summary'])
# "ZeroDivisionError in main (example.py:10): division by zero"

# Generate a detailed report
report = tattletail.generate_report(traceback_text)
print(report)
```

### Capture Live Exceptions

```python
import tattletail

try:
    # Your risky code here
    result = some_function()
except Exception:
    # Analyze the current exception
    parsed = tattletail.parse_from_exception()
    print(f"Error in {parsed.get_error_location()}")
    print(f"Call chain: {' -> '.join(parsed.get_call_chain())}")
```

## ✨ **Key Features**

### **🧩 Structured Parsing**

-   **Rich Data Models**: Convert tracebacks into structured `ParsedTraceback` objects
-   **Context Extraction**: Automatically pull source code around error locations
-   **Chained Exception Support**: Handle complex `__cause__` and `__context__` chains
-   **Unicode Friendly**: Works with international characters in paths and messages

### **🧠 Smart Analysis**

-   **Exception Details**: Extract class, hierarchy, location, and metadata information
-   **Pattern Detection**: Identify recursion, call depth, and code location patterns
-   **Probable Cause**: Automatic identification of likely error causes
-   **Metrics Calculation**: Quantitative analysis of stack frames and error characteristics
-   **Summary Generation**: Concise, human-readable error descriptions

### **💻 Developer Experience**

-   **Simple API**: Single-function entry points for common tasks
-   **Context Aware**: Shows relevant source code when files are available
-   **Report Generation**: Beautiful, formatted reports for debugging
-   **Error Monitoring**: Perfect for production error tracking

## 🧞 Why use Tattletail?

Python's built-in `traceback` module is awesome for basic needs, but Tattletail goes a little bit beyond. Yes, I also know Sentry, Rollbar, Bugsnag, Better Exceptions, Pretty Errors, Structlog and so on. Each one of them are truly great tools. I'm just a guy who faced some situations where none of them fulfilled my needs. Sentry is too powerful for small organizations or projects (somewhat complex to self-host or paid), Structlog asks for some refactoring on already living projects, Better Exceptions is focused on live exceptions, etc.

**Tattletail's unique strength**: It can extract info from old logs and historical data - something no other tool can do for some reason I don't know. Need to analyze that traceback buried in last week's log files? Tattletail handles it. Want to build custom error analysis tools? Tattletail provides the foundation.

```python
# What you CAN'T do with other tools:
error_from_log = """Traceback (most recent call last):
  File "app.py", line 42, in process_data
    result = parse_json(data)
ValueError: Invalid JSON format"""

analysis = tattletail.analyze(error_from_log)  # This works!
# Sentry/Rollbar: ❌ Can't parse strings from logs
# Better Exceptions: ❌ Only works with live exceptions
```

Parse tracebacks from ANYWHERE. Ingest everything you have of some existing application.

```python
error_sources = [
    application_logs,           # ✅ Log file entries
    error_monitoring_systems,   # ✅ Sentry, Rollbar exports
    bug_reports,                # ✅ User-submitted errors
    database_error_records,     # ✅ Stored error strings
    CI/CD_failure_logs,         # ✅ Test failure outputs
    email_error_notifications   # ✅ Automated alerts
]

for error_text in error_sources:
    parsed = tattletail.parse(error_text)  # Works with ALL of these!
```

It's deadly simple with zero third-party dependencies. I'm not aiming to compete with anyone. I just wrote Tattletail for personal use and... it's done. Why shouldn't I publish it if it maybe can be of use to someone?

## 🎯 **Common Use Cases**

### **Interactive Debugging**

```python
import tattletail

# Quick analysis during development
try:
    complex_operation()
except Exception:
    parsed = tattletail.parse_from_exception(extract_context=True)

    # See the error location with source code context
    for frame in parsed.stack_frames:
        if frame.context_lines:
            print(f"Error in {frame.file_path}:{frame.line_number}")
            for ctx in frame.context_lines:
                marker = ">>>" if ctx.is_error_line else "   "
                print(f"{marker} {ctx.line_number:3d}: {ctx.code}")
```

### **Production Monitoring**

```python
import tattletail
import logging

def log_error(exception_text, user_context=None):
    analysis = tattletail.analyze(exception_text)

    logger.info(f"Error: {analysis['summary']}")
    logger.info(f"Cause: {analysis['probable_cause']}")

    if analysis['patterns']['is_recursive']:
        logger.warning("Recursive pattern detected!")

    if analysis['patterns']['call_depth'] > 10:
        logger.warning(f"Deep call stack: {analysis['patterns']['call_depth']} frames")
```

### **Tool Integration**

```python
import tattletail

# Build debugging tools with rich traceback data
def analyze_test_failure(traceback_text):
    parsed = tattletail.parse(traceback_text)
    analysis = tattletail.analyze(traceback_text)

    return {
        'test_file': parsed.get_error_location().file_path,
        'error_line': parsed.get_error_location().line_number,
        'error_type': parsed.exception.exception_type,
        'complexity': analysis['patterns']['call_depth'],
        'user_code_ratio': analysis['metrics']['user_frames'] / analysis['metrics']['total_frames']
    }
```

## 🔬 **Advanced Features**

### **Context Extraction**

Automatically show source code around errors when files are available:

```python
# Enable context extraction
parsed = tattletail.parse(traceback_text, extract_context=True)

# Access source code context
error_frame = parsed.get_error_location()
if error_frame.context_lines:
    for line in error_frame.context_lines:
        print(f"{line.line_number}: {line.code}")
```

### **Pattern Analysis**

Detect common patterns in your tracebacks:

```python
analysis = tattletail.analyze(traceback_text)
patterns = analysis['patterns']

if patterns['is_recursive']:
    print(f"Recursion detected! Functions: {patterns['repeated_functions']}")

if patterns['error_in_stdlib']:
    print("Error originated in Python standard library")

print(f"Call stack depth: {patterns['call_depth']} frames")
```

### **Exception Details**

Access focused exception information with comprehensive details:

```python
analysis = tattletail.analyze(traceback_text)
exception = analysis['exception']

print(f"Exception type: {exception['class']}")
print(f"Error message: {exception['message']}")
print(f"Inheritance chain: {' -> '.join(exception['hierarchy'])}")
print(f"Error location: {exception['file_path']}:{exception['line_number']}")
print(f"In function: {exception['function_name']}")
print(f"Has chained exceptions: {exception['has_cause'] or exception['has_context']}")
```

### **Detailed Metrics**

Get quantitative insights about your errors:

```python
metrics = analysis['metrics']
print(f"Total frames: {metrics['total_frames']}")
print(f"User code frames: {metrics['user_frames']}")
print(f"Third-party frames: {metrics['site_packages_frames']}")
print(f"Files involved: {metrics['unique_files']}")
print(f"Has chained exceptions: {metrics['has_chained_exceptions']}")
```

## 📚 **Examples**

Check out the [`examples/`](./examples) directory for detailed usage patterns:

-   **[Basic Usage](./examples/01_basic_usage.py)**: Core functionality and common patterns
-   **[Error Monitoring](./examples/02_error_monitoring.py)**: Production monitoring and alerting
-   **[Context manager](./examples/03_context_managers.py)**: Pythonic context managers to help you write readable code

## 🙌 **Contributing**

I would love contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b my-feature`
3. **Write tests** for your changes
4. **Run the test suite**: `make test`
5. **Submit a pull request**

### **Development Setup**

```bash
# Clone the repository
git clone https://github.com/yourusername/tattletail.git
cd tattletail

# Install dependencies
uv sync

# Run tests
make test

# Run linting
make lint
```
---

**Happy debugging! 🚀**
