import pytest
import logging
import os
from sfn_blueprint import setup_logger


@pytest.fixture
def cleanup_log_file():
    """Fixture to clean up any test-created log files after the test."""
    log_file = 'test_log_file.log'
    yield log_file
    if os.path.exists(log_file):
        os.remove(log_file)


def test_setup_logger_stream_handler():
    """Test that the logger is correctly set up with a StreamHandler (console logging)."""
    logger_name = "test_logger"
    logger, stream_handler = setup_logger(logger_name)

    # Assert that the logger name is correct
    assert logger.name == logger_name

    # Check if logger has a StreamHandler
    assert isinstance(stream_handler, logging.StreamHandler)

    # Ensure the StreamHandler has the correct formatter
    assert stream_handler.formatter._fmt == '%(asctime)s - %(levelname)s - %(message)s'

    # Verify logging level is set to INFO
    assert logger.level == logging.INFO

    # Log a message and check if the handler handles it (no assertion for console output, but it's verified via log level)
    logger.info("Test message for console logging")


def test_setup_logger_file_handler(cleanup_log_file):
    """Test that the logger is correctly set up with a FileHandler (file logging)."""
    logger_name = "test_logger_with_file"
    log_file = cleanup_log_file

    logger, stream_handler = setup_logger(logger_name, log_file)

    # Check if the logger has a FileHandler
    file_handler = None
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            file_handler = handler
            break

    assert file_handler is not None, "Logger should have a FileHandler."

    # Ensure the FileHandler has the correct formatter
    assert file_handler.formatter._fmt == '%(asctime)s - %(levelname)s - %(message)s'

    # Log a message to ensure it is written to the file
    test_message = "Test message for file logging"
    logger.info(test_message)

    # Read the log file and ensure the message is logged
    with open(log_file, 'r') as f:
        log_contents = f.read()

    assert test_message in log_contents, "The log message should be written to the file."


def test_setup_logger_multiple_handlers(cleanup_log_file):
    """Test logger with both StreamHandler and FileHandler."""
    logger_name = "test_logger_with_multiple_handlers"
    log_file = cleanup_log_file

    logger, stream_handler = setup_logger(logger_name, log_file)

    # Assert the logger has both StreamHandler and FileHandler
    handlers = [type(handler) for handler in logger.handlers]
    assert logging.StreamHandler in handlers
    assert logging.FileHandler in handlers

    # Log a message and ensure it is both in console (StreamHandler) and the log file (FileHandler)
    test_message = "Test message for multiple handlers"
    logger.info(test_message)

    # Check the log file
    with open(log_file, 'r') as f:
        log_contents = f.read()

    assert test_message in log_contents, "The log message should be written to the file."

    # Verify the log message also works for the stream (This would typically be verified by observing the console output.)


def test_setup_logger_no_duplicate_handlers():
    """Test that multiple setup_logger calls don't add duplicate handlers."""
    logger_name = "test_logger_no_duplicates"
    logger, _ = setup_logger(logger_name)

    # Call setup_logger again with the same logger name
    logger, _ = setup_logger(logger_name)

    # Ensure that no duplicate handlers are added (There should only be one StreamHandler)
    stream_handler_count = sum(1 for handler in logger.handlers if isinstance(handler, logging.StreamHandler))
    assert stream_handler_count == 1, "There should be only one StreamHandler."
