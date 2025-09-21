#!/usr/bin/env python3
"""
Error monitoring and logging integration examples.

This script demonstrates how to integrate tattletail with:
- Application error handlers
- Logging systems
- Error aggregation and alerting
- Production monitoring
"""

from collections import defaultdict
from datetime import datetime
import json
import logging
import sys
import time
from typing import Any
from typing import Dict


# Add src to path for examples
sys.path.insert(0, "../src")

import tattletail


class ErrorMonitor:
    """A comprehensive error monitoring system using tattletail."""

    def __init__(self, log_file: str = "error_monitor.log"):
        self.error_counts = defaultdict(int)
        self.error_history = []
        self.setup_logging(log_file)

    def setup_logging(self, log_file: str):
        """Set up structured logging for errors."""
        self.logger = logging.getLogger("error_monitor")
        self.logger.setLevel(logging.INFO)

        # File handler for detailed logs
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)

        # Console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def capture_error(
        self, exception_string: str | None = None, context: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """Capture and analyze an error with full context."""
        if exception_string is None:
            # Capture current exception
            parsed = tattletail.parse_from_exception()
            exception_string = parsed.raw_traceback
        else:
            parsed = tattletail.parse(exception_string)

        # Analyze the error
        analysis = tattletail.analyze(exception_string)
        # Create error record
        error_loc = parsed.get_error_location()
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "exception_type": parsed.exception.exception_type,
            "exception_message": parsed.exception.exception_message,
            "summary": analysis["summary"],
            "probable_cause": analysis["probable_cause"],
            "call_depth": analysis["patterns"]["call_depth"],
            "is_recursive": analysis["patterns"]["is_recursive"],
            "error_location": error_loc.to_dict() if error_loc else None,
            "call_chain": parsed.get_call_chain(),
            "context": context or {},
            "metrics": analysis["metrics"],
        }

        # Update statistics
        error_location = parsed.get_error_location()
        error_key = (
            f"{parsed.exception.exception_type}:"
            f"{error_location.function_name if error_location else 'unknown'}"
        )
        self.error_counts[error_key] += 1
        self.error_history.append(error_record)

        # Log the error
        self.logger.info(f"ERROR: {analysis['summary']}")

        return error_record

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        if not self.error_history:
            return {"message": "No errors recorded"}

        total_errors = len(self.error_history)
        exception_type_counts = defaultdict(int)
        recent_errors = []

        for error in self.error_history:
            exception_type_counts[error["exception_type"]] += 1

            # Keep last 5 errors
            if len(recent_errors) < 5:
                recent_errors.append(error)

        # Find most common errors
        most_common = sorted(
            self.error_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "total_errors": total_errors,
            "exception_types": dict(exception_type_counts),
            "most_common_errors": most_common,
            "recent_errors": recent_errors,
        }

    def should_alert(self, error_record: Dict[str, Any]) -> bool:
        """Determine if this error should trigger an alert."""
        # Alert on recurring errors
        error_key = f"{error_record['exception_type']}:{error_record['error_location']}"
        if self.error_counts[error_key] >= 3:
            return True

        # Alert on recursive patterns
        if error_record["is_recursive"]:
            return True

        return False

    def generate_alert(self, error_record: Dict[str, Any]) -> str:
        """Generate alert message for critical errors."""
        alert = f"""
🚨 ERROR ALERT 🚨
Exception: {error_record["exception_type"]}
Location: {error_record["error_location"]}
Summary: {error_record["summary"]}

Probable Cause: {error_record["probable_cause"]}
"""

        error_key = f"{error_record['exception_type']}:{error_record['error_location']}"
        if self.error_counts[error_key] > 1:
            alert += (
                f"\n⚠️  This error has occurred {self.error_counts[error_key]} times!"
            )

        return alert


def database_connection_error():
    """Simulate a database connection failure."""
    raise ConnectionError("Failed to connect to database: connection timeout")


def file_processing_error():
    """Simulate a file processing error."""

    def process_file(filename):
        with open(filename, "r") as f:
            data = json.loads(f.read())
        return data["required_field"]

    return process_file("nonexistent.json")


def validation_error():
    """Simulate data validation error."""

    def validate_user_data(user_data):
        if "email" not in user_data:
            raise ValueError("Email is required")
        if "@" not in user_data["email"]:
            raise ValueError(f"Invalid email format: {user_data['email']}")
        return True

    invalid_user = {"name": "John", "email": "invalid-email"}
    return validate_user_data(invalid_user)


def recursive_function_error():
    """Simulate a recursive function causing stack overflow."""

    def factorial(n):
        if n < 0:
            return factorial(n - 1)  # Infinite recursion
        return 1 if n <= 1 else n * factorial(n - 1)

    return factorial(-5)


def simulate_application_errors():
    """Simulate various application errors for monitoring."""
    return [
        ("Database Connection", database_connection_error),
        ("File Processing", file_processing_error),
        ("Data Validation", validation_error),
        ("Recursive Function", recursive_function_error),
    ]


def demonstrate_error_monitoring():
    """Demonstrate comprehensive error monitoring."""
    print("=== Error Monitoring System ===")

    monitor = ErrorMonitor("examples/error_monitor.log")

    # Simulate various application errors
    error_scenarios = simulate_application_errors()

    for scenario_name, error_func in error_scenarios:
        print(f"\nSimulating: {scenario_name}")

        try:
            error_func()
        except Exception:
            # Capture error with context
            context = {
                "scenario": scenario_name,
                "user_id": "user123",
                "session_id": "session456",
                "environment": "production",
            }

            error_record = monitor.capture_error(context=context)

            # Check if alert should be triggered
            if monitor.should_alert(error_record):
                alert = monitor.generate_alert(error_record)
                print("ALERT TRIGGERED:")
                print(alert)

        # Add some delay between errors
        time.sleep(0.1)

    # Show error statistics
    print("\n=== Error Statistics ===")
    stats = monitor.get_error_statistics()
    print(f"Total Errors: {stats['total_errors']}")
    print(f"Exception Types: {stats['exception_types']}")

    print("\nMost Common Errors:")
    for error_key, count in stats["most_common_errors"]:
        print(f"  {error_key}: {count} occurrences")


def demonstrate_logging_integration():
    """Show integration with Python's logging system."""
    print("\n=== Logging Integration ===")

    # Setup custom log handler that uses tattletail
    class TattletailLogHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.monitor = ErrorMonitor("examples/structured_errors.log")

        def emit(self, record):
            if record.exc_info:
                # Extract exception information
                exc_type, exc_value, exc_traceback = record.exc_info
                tb_string = "".join(
                    __import__("traceback").format_exception(
                        exc_type, exc_value, exc_traceback
                    )
                )

                # Analyze with tattletail
                context = {
                    "logger_name": record.name,
                    "level": record.levelname,
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                self.monitor.capture_error(tb_string, context)

    # Setup application logger with tattletail handler
    app_logger = logging.getLogger("myapp")
    app_logger.setLevel(logging.ERROR)
    app_logger.addHandler(TattletailLogHandler())

    # Simulate application with logging
    try:

        def risky_operation():
            data = [1, 2, 3]
            return data[10]  # IndexError

        risky_operation()
    except Exception:
        app_logger.exception("Error in risky_operation")

    print("Error logged and analyzed through logging integration")


def demonstrate_json_export():
    """Show exporting error data for external systems."""
    print("\n=== JSON Export for External Systems ===")

    monitor = ErrorMonitor()

    # Simulate some errors
    try:
        {"key": "value"}["missing"]
    except Exception:
        monitor.capture_error(
            context={
                "service": "api",
                "endpoint": "/users/profile",
                "request_id": "req-789",
            }
        )

    # Export to JSON for external monitoring systems
    export_data = {
        "service": "tattletail-demo",
        "timestamp": datetime.now().isoformat(),
        "errors": monitor.error_history,
        "statistics": monitor.get_error_statistics(),
    }

    # Save to file (could be sent to monitoring service)
    with open("examples/error_export.json", "w") as f:
        json.dump(export_data, f, indent=2)

    print("Error data exported to error_export.json")
    print("This can be ingested by monitoring systems like:")
    print("• Datadog • New Relic • Grafana • Custom dashboards")


def main():
    """Run all error monitoring examples."""
    print("Tattletail Error Monitoring Examples")
    print("=" * 40)

    demonstrate_error_monitoring()
    demonstrate_logging_integration()
    demonstrate_json_export()

    print("\n" + "=" * 40)
    print("Error monitoring examples completed!")
    print("Check the generated log files:")
    print("• examples/error_monitor.log")
    print("• examples/structured_errors.log")
    print("• examples/error_export.json")


if __name__ == "__main__":
    main()
