"""Tests for structured JSON logging."""

import json
import logging

from fuel_price_mcp.logging import JSONFormatter, setup_logging


class TestJSONFormatter:
    def test_basic_format(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello %s",
            args=("world",),
            exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["level"] == "INFO"
        assert data["logger"] == "test"
        assert data["message"] == "hello world"
        assert "timestamp" in data
        assert "exception" not in data

    def test_format_with_exception(self):
        formatter = JSONFormatter()
        try:
            msg = "fail"
            raise ValueError(msg)
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="error occurred",
            args=(),
            exc_info=exc_info,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert "exception" in data
        assert "ValueError" in data["exception"]


class TestSetupLogging:
    def test_configures_handler_and_level(self):
        setup_logging("DEBUG")
        logger = logging.getLogger("fuel_price_mcp")
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0].formatter, JSONFormatter)

    def test_invalid_level_falls_back_to_info(self):
        setup_logging("GARBAGE")
        logger = logging.getLogger("fuel_price_mcp")
        assert logger.level == logging.INFO
