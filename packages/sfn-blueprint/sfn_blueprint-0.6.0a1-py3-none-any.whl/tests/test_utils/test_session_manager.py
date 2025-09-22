import pytest
from unittest.mock import MagicMock, patch
from sfn_blueprint import SFNSessionManager

@pytest.fixture
def session_manager():
    """Fixture to get the singleton instance of SFNSessionManager."""
    # Resetting the singleton instance before each test to avoid reuse
    SFNSessionManager._instance = None
    return SFNSessionManager()

@pytest.fixture
def mock_logger():
    """Fixture to create a mock logger."""
    return MagicMock()

def test_singleton_behavior():
    """Test that SFNSessionManager follows singleton pattern."""
    instance1 = SFNSessionManager()
    instance2 = SFNSessionManager()
    assert instance1 is instance2, "SFNSessionManager is not following singleton behavior."

def test_get_method(session_manager):
    """Test the get method for retrieving session data."""
    session_manager.set("test_key", "test_value")
    assert session_manager.get("test_key") == "test_value", "Failed to retrieve the correct value."
    assert session_manager.get("non_existent_key", "default_value") == "default_value", "Failed to return default value for non-existent key."

def test_set_method(session_manager, mock_logger):
    """Test the set method for updating session data and logging."""
    # Replace the existing logger in the session manager
    session_manager.logger = mock_logger
    # Perform the operation
    session_manager.set("new_key", "new_value")
    # Verify the value was set
    assert session_manager.get("new_key") == "new_value"
    # Verify the log message
    mock_logger.info.assert_called_with("Setting key: new_key, value: new_value")

    

def test_clear_method(session_manager, mock_logger):
    """Test the clear method to ensure session data is cleared and logged."""
    # Replace the existing logger in the session manager
    session_manager.logger = mock_logger
    session_manager.set("key1", "value1")
    session_manager.clear()
    assert session_manager.get("key1") is None, "Session data was not cleared properly."
    mock_logger.info.assert_called_once_with("Session data cleared.")


def test_clear_method(session_manager, mock_logger):
    """Test the clear method to ensure session data is cleared and logged."""
    # Replace the existing logger in the session manager
    session_manager.logger = mock_logger
    # Set some data
    session_manager.set("key1", "value1")
    # Reset mock to clear the set() log message
    mock_logger.reset_mock()
    # Clear the session
    session_manager.clear()
    # Verify data is cleared
    assert session_manager.get("key1") is None, "Session data was not cleared properly."
    # Now only the clear() log message will be checked
    mock_logger.info.assert_called_once_with("Session data cleared.")

    # OR instead reset_mock recognize all logs
    # Set some data (this will trigger first log message)
    # session_manager.set("key1", "value1")
    # # Clear the session (this will trigger second log message)
    # session_manager.clear()
    # # Verify data is cleared
    # assert session_manager.get("key1") is None, "Session data was not cleared properly."
    # # Verify both log messages were called in correct order
    # mock_logger.info.assert_has_calls([
    #     mock.call("Setting key: key1, value: value1"),
    #     mock.call("Session data cleared.")
    # ])

def test_logger_on_set(session_manager, mock_logger):
    """Test that logger is called when setting a key-value pair."""
    session_manager.logger = mock_logger
    session_manager.set("sample_key", "sample_value")
    mock_logger.info.assert_called_once_with("Setting key: sample_key, value: sample_value")

def test_logger_on_clear(session_manager, mock_logger):
    """Test that logger is called when clearing session data."""
    session_manager.logger = mock_logger
    session_manager.clear()
    mock_logger.info.assert_called_once_with("Session data cleared.")
