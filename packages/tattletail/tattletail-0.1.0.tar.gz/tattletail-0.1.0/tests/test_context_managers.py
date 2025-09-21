"""
Tests for context manager functionality.

This module tests the ErrorCapture, ErrorExpector, and ErrorMonitor context managers.
"""

import unittest
from unittest.mock import Mock

import tattletail


class TestErrorCapture(unittest.TestCase):
    """Test the ErrorCapture context manager."""

    def test_capture_no_exception(self):
        """Test capturing when no exception occurs."""
        with tattletail.capture() as ctx:
            _ = 2 + 2

        self.assertIsNone(ctx.exception)
        self.assertIsNone(ctx.parsed)
        self.assertIsNone(ctx.analysis)

    def test_capture_with_exception(self):
        """Test capturing a simple exception."""
        with tattletail.capture(suppress=True) as ctx:
            raise ValueError("Test error")

        self.assertIsNotNone(ctx.exception)
        self.assertIsInstance(ctx.exception, ValueError)
        self.assertEqual(str(ctx.exception), "Test error")
        self.assertIsNotNone(ctx.parsed)
        self.assertIsNotNone(ctx.analysis)
        self.assertEqual(ctx.parsed.exception.exception_type, "ValueError")  # type: ignore
        self.assertIn("Test error", ctx.analysis["summary"])  # type: ignore

    def test_capture_with_suppress(self):
        """Test that suppress=True prevents exception from propagating."""
        exception_raised = False

        try:
            with tattletail.capture(suppress=True) as ctx:
                raise ValueError("Suppressed error")
        except ValueError:
            exception_raised = True

        self.assertFalse(exception_raised)
        self.assertIsNotNone(ctx.exception)
        self.assertIsInstance(ctx.exception, ValueError)

    def test_capture_without_suppress(self):
        """Test that suppress=False allows exception to propagate."""
        with self.assertRaises(ValueError):
            with tattletail.capture(suppress=False):
                raise ValueError("Not suppressed")

    def test_capture_with_callback(self):
        """Test the on_exception callback."""
        callback_called = False
        captured_ctx = None

        def callback(ctx):
            nonlocal callback_called, captured_ctx
            callback_called = True
            captured_ctx = ctx

        with tattletail.capture(suppress=True, on_exception=callback) as ctx:
            raise RuntimeError("Callback test")

        self.assertTrue(callback_called)
        self.assertIs(captured_ctx, ctx)
        self.assertIsInstance(ctx.exception, RuntimeError)

    def test_capture_with_context_extraction(self):
        """Test context extraction during capture."""
        with tattletail.capture(extract_context=True, suppress=True) as ctx:
            raise ValueError("Context test")

        self.assertIsNotNone(ctx.parsed)
        # Context extraction depends on file availability, so we just test it doesn't
        # crash


class TestErrorExpector(unittest.TestCase):
    """Test the ErrorExpector context manager."""

    def test_expect_matching_exception(self):
        """Test expecting an exception that occurs."""
        with tattletail.expect(ValueError) as ctx:
            raise ValueError("Expected error")

        self.assertTrue(ctx.matched)
        self.assertIsNotNone(ctx.exception)
        self.assertIsInstance(ctx.exception, ValueError)
        self.assertIsNotNone(ctx.parsed)
        self.assertIsNotNone(ctx.analysis)

    def test_expect_with_message_match(self):
        """Test expecting an exception with specific message."""
        with tattletail.expect(ValueError, "specific message") as ctx:
            raise ValueError("This contains specific message content")

        self.assertTrue(ctx.matched)
        self.assertIsNotNone(ctx.exception)

    def test_expect_with_message_no_match(self):
        """Test expecting exception with message that doesn't match."""
        with self.assertRaises(ValueError):
            with tattletail.expect(ValueError, "wrong message") as ctx:
                raise ValueError("Different message")

        self.assertFalse(ctx.matched)

    def test_expect_wrong_exception_type(self):
        """Test expecting wrong exception type."""
        with self.assertRaises(RuntimeError):
            with tattletail.expect(ValueError) as ctx:
                raise RuntimeError("Wrong type")

        self.assertFalse(ctx.matched)

    def test_expect_no_exception(self):
        """Test expecting exception when none occurs."""
        with tattletail.expect(ValueError) as ctx:
            pass  # No exception

        self.assertFalse(ctx.matched)
        self.assertIsNone(ctx.exception)

    def test_expect_multiple_types(self):
        """Test expecting multiple exception types."""
        with tattletail.expect((ValueError, RuntimeError)) as ctx:
            raise RuntimeError("One of multiple types")

        self.assertTrue(ctx.matched)
        self.assertIsInstance(ctx.exception, RuntimeError)


class TestErrorMonitor(unittest.TestCase):
    """Test the ErrorMonitor context manager."""

    def test_monitor_no_exception(self):
        """Test monitoring when no exception occurs."""
        logger = Mock()

        with tattletail.monitor(logger=logger) as ctx:
            _ = 1 + 1

        self.assertIsNone(ctx.exception)
        self.assertIsNone(ctx.parsed)
        self.assertIsNone(ctx.analysis)
        logger.error.assert_not_called()

    def test_monitor_with_exception(self):
        """Test monitoring with an exception."""
        logger = Mock()

        with self.assertRaises(ValueError):
            with tattletail.monitor(logger=logger) as ctx:
                raise ValueError("Monitor test")

        self.assertIsNotNone(ctx.exception)
        self.assertIsNotNone(ctx.parsed)
        self.assertIsNotNone(ctx.analysis)
        logger.error.assert_called_once()

    def test_monitor_with_suppress(self):
        """Test monitoring with exception suppression."""
        logger = Mock()

        with tattletail.monitor(logger=logger, suppress=True) as ctx:
            raise ValueError("Suppressed monitor test")

        self.assertIsNotNone(ctx.exception)
        logger.error.assert_called_once()

    def test_monitor_without_analysis(self):
        """Test monitoring without analysis."""
        logger = Mock()

        with tattletail.monitor(
            logger=logger, include_analysis=False, suppress=True
        ) as ctx:
            raise ValueError("No analysis test")

        self.assertIsNotNone(ctx.exception)
        self.assertIsNotNone(ctx.parsed)
        self.assertIsNone(ctx.analysis)
        logger.error.assert_called_once()

    def test_monitor_different_log_level(self):
        """Test monitoring with different log level."""
        logger = Mock()

        with tattletail.monitor(logger=logger, level="WARNING", suppress=True):
            raise ValueError("Warning level test")

        logger.warning.assert_called_once()
        logger.error.assert_not_called()

    def test_monitor_without_logger(self):
        """Test monitoring without a logger."""
        with tattletail.monitor(suppress=True) as ctx:
            raise ValueError("No logger test")

        self.assertIsNotNone(ctx.exception)
        # Should not crash even without logger


class TestContextManagerIntegration(unittest.TestCase):
    """Test integration scenarios with context managers."""

    def test_nested_captures(self):
        """Test nested context managers."""
        with tattletail.capture(suppress=True) as outer_ctx:
            with tattletail.capture(suppress=True) as inner_ctx:
                raise ValueError("Nested error")

        # Inner context manager should capture the exception
        # Outer context manager won't see it because inner suppressed it
        self.assertIsNone(
            outer_ctx.exception
        )  # Didn't reach outer due to inner suppression
        self.assertIsNotNone(inner_ctx.exception)
        self.assertIsInstance(inner_ctx.exception, ValueError)

    def test_capture_chained_exceptions(self):
        """Test capturing chained exceptions."""
        with tattletail.capture(suppress=True) as ctx:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise RuntimeError("Wrapper error") from e

        self.assertIsNotNone(ctx.exception)
        self.assertIsInstance(ctx.exception, RuntimeError)
        self.assertIsNotNone(ctx.parsed.exception.cause)
        self.assertEqual(ctx.parsed.exception.cause.exception_type, "ValueError")

    def test_complex_analysis_workflow(self):
        """Test complex workflow with analysis."""
        results = []

        def capture_callback(ctx):
            results.append(
                {
                    "type": ctx.parsed.exception.exception_type,
                    "message": ctx.parsed.exception.exception_message,
                    "cause": ctx.analysis["probable_cause"],
                    "depth": ctx.analysis["patterns"]["call_depth"],
                }
            )

        with tattletail.capture(suppress=True, on_exception=capture_callback):

            def level3():
                raise ValueError("Deep error")

            def level2():
                level3()

            def level1():
                level2()

            level1()

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "ValueError")
        self.assertGreater(results[0]["depth"], 3)  # Should have multiple frames


if __name__ == "__main__":
    unittest.main()
