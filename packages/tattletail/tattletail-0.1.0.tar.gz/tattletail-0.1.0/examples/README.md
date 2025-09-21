# Tattletail Examples

This directory contains comprehensive examples demonstrating various use cases and integration patterns for the tattletail library.

## 📁 Example Files

### [01_basic_usage.py](./01_basic_usage.py)
**Core functionality demonstrations**

Learn the fundamental features of tattletail:
- ✅ Parse traceback strings from logs or error reports
- ✅ Capture and analyze live exceptions 
- ✅ Generate detailed error analysis with patterns and metrics
- ✅ Create human-readable error reports
- ✅ Extract source code context around errors

**Key Use Cases:**
- Basic error parsing and analysis
- Exception capture during development
- Context extraction for debugging
- Report generation for team communication

**Run with:** `python 01_basic_usage.py`

---

### [02_error_monitoring.py](./02_error_monitoring.py)
**Production error monitoring and alerting**

Build robust error monitoring systems:
- 🚨 Comprehensive error tracking and statistics
- 📊 Pattern-based alerting and escalation
- 📝 Structured logging integration
- 📈 Error trend analysis and reporting
- 🔔 Alert generation for critical issues

**Key Use Cases:**
- Production error monitoring
- Application health tracking
- Error trend analysis
- Integration with logging systems
- JSON export for external monitoring tools

**Generated Files:**
- `error_monitor.log` - Detailed error logs
- `structured_errors.log` - Structured logging output
- `error_export.json` - JSON data for external systems

**Run with:** `python 02_error_monitoring.py`

---

### [03_context_managers.py](./03_context_managers.py)
**Pythonic context manager integration**

Leverage Python's context managers for elegant error handling:
- 🐍 Pythonic exception handling with `with` statements
- 🧪 Testing workflows with expected exception validation
- 📊 Production monitoring with automatic logging
- 🔧 Custom callback processing for specialized workflows
- 🎯 Advanced patterns for complex integration scenarios

**Key Use Cases:**
- Clean exception handling without explicit try/except blocks
- Testing frameworks for validating expected errors
- Production monitoring with automatic analysis
- Custom error processing workflows
- Integration with existing context manager patterns

**Features Demonstrated:**
- `tattletail.capture()` - Basic exception capture with suppression
- `tattletail.expect()` - Test expected exceptions with validation
- `tattletail.monitor()` - Automatic logging and monitoring
- Custom callbacks for specialized error processing
- Context extraction and source code analysis

**Run with:** `python 03_context_managers.py`

---

## 🚀 Quick Start

1. **Install and setup (from project root):**
   ```bash
   # Install with UV (recommended)
   uv sync

   # Or ensure tattletail is available in your Python path
   export PYTHONPATH="src:$PYTHONPATH"
   ```

2. **Run all examples:**
   ```bash
   # Basic functionality
   uv run python examples/01_basic_usage.py

   # Error monitoring and alerting
   uv run python examples/02_error_monitoring.py

   # Context manager patterns
   uv run python examples/03_context_managers.py
   ```

3. **Or run individually from examples directory:**
   ```bash
   cd examples
   python 01_basic_usage.py      # Core features
   python 02_error_monitoring.py # Production monitoring
   python 03_context_managers.py # Pythonic patterns
   ```

## 📋 Example Scenarios Covered

### Development & Debugging
- **Live Exception Capture** - Catch and analyze exceptions as they occur
- **Context Extraction** - View source code around error locations
- **Pattern Analysis** - Identify problematic patterns and architectural issues
- **Testing Workflows** - Validate expected exceptions in test suites

### Production Monitoring
- **Error Aggregation** - Track and categorize application errors
- **Alert Generation** - Smart alerting based on error patterns and frequency
- **Trend Analysis** - Historical error data and statistics
- **Automatic Logging** - Seamless integration with logging frameworks

### Pythonic Integration
- **Context Managers** - Clean exception handling with `with` statements
- **Custom Callbacks** - Specialized error processing workflows
- **Expected Exception Testing** - Validate anticipated errors in tests
- **Suppression Control** - Fine-grained control over exception propagation

### Analysis Features
- **Probable Cause** - Automatic identification of likely error causes
- **Pattern Detection** - Recognition of recursion, call depth, and code location patterns
- **Metrics Calculation** - Quantitative analysis of stack frames and error characteristics

## 🛠️ Customization

Each example can be customized for your specific needs:

### Configuration Options
```python
# Customize context extraction
parser = TracebackParser(
    extract_context=True,
    context_size=5  # Lines before/after error
)

# Customize analysis parameters
analyzer = TracebackAnalyzer()
```

### Monitoring Customization
```python
# Error monitoring with custom handlers
monitor = ErrorMonitor("custom_errors.log")
monitor.capture_error(exception_string, context={'user_id': 123})

# Custom alerting conditions
def custom_alert_condition(error_record):
    return error_record['is_recursive'] or 'critical' in error_record['summary'].lower()
```

### Context Manager Customization
```python
# Custom callback processing
def custom_error_processor(ctx):
    if ctx.analysis['patterns']['is_recursive']:
        alert_ops_team(ctx.exception)
    log_to_metrics_system(ctx.analysis)

# Use with custom callback
with tattletail.capture(on_exception=custom_error_processor):
    risky_operation()

# Expected exception testing
with tattletail.expect(ValueError, "invalid input"):
    process_user_data(invalid_data)

# Production monitoring with logging
with tattletail.monitor(logger=app_logger, level="ERROR"):
    handle_user_request()
```

## 📊 Output Examples

### Error Analysis Report
```
🔍 Tattletail Analysis Report
═══════════════════════════════════════

Summary: ValueError in parse_data (utils.py:45): invalid literal for int()

📍 Error Location: utils.py:45 in parse_data()

🔍 Probable Cause: Invalid data format or type conversion

🔗 Call Chain: main() → process_file() → parse_data()

📋 Detected Patterns:
  • Call depth: 3 levels
  • No recursion detected
  • User code frames: 3/3

📊 Metrics:
  • Total frames: 3
  • Unique files: 2
  • Error frequency: First occurrence
```

### Monitoring Dashboard Data
```json
{
  "service": "my-app",
  "timestamp": "2024-01-15T10:30:00Z",
  "summary": {
    "total_errors": 25,
    "exception_types": {
      "ValueError": 8,
      "KeyError": 12,
      "TypeError": 5
    },
    "most_common": "KeyError (12 occurrences)"
  },
  "alerts": [
    {
      "message": "Recursive pattern detected",
      "count": 1,
      "timeframe": "last_10_minutes"
    }
  ]
}
```

## 🤝 Contributing

Have ideas for additional examples? Contributions are welcome!

1. **New Use Cases** - Add examples for specific industries or frameworks
2. **Integration Patterns** - Show integration with additional tools
3. **Advanced Workflows** - Demonstrate complex monitoring scenarios
4. **Performance Examples** - Show handling of high-volume error scenarios

## 🎯 Next Steps

After exploring these examples:

1. **Adapt to Your Stack** - Modify examples for your specific technology stack
2. **Integrate with Tools** - Connect with your existing monitoring and logging tools
3. **Customize Analysis** - Tune pattern detection for your domain
4. **Scale Up** - Deploy monitoring solutions to production environments
5. **Share Knowledge** - Use reports and analysis to improve team debugging skills

---

*These examples demonstrate the power of tattletail for comprehensive error analysis and monitoring. Each script is self-contained and includes detailed explanations of the concepts and patterns being demonstrated.*