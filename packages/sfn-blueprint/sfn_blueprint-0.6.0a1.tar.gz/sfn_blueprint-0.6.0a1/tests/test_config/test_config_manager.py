import pytest
import json
import yaml
from unittest.mock import patch, mock_open, MagicMock, call
from sfn_blueprint import SFNConfigManager

# 1. Test successful loading of JSON config
@patch("sfn_blueprint.config.config_manager.setup_logger")
@patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1", "key2": "value2"}')
def test_load_json_config(mock_file, mock_setup_logger):
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)

    config_manager = SFNConfigManager(config_path="config/settings.json")

    # Check that the config is loaded correctly
    assert config_manager.config == {"key1": "value1", "key2": "value2"}
    mock_logger.info.assert_called_once_with("Loading configuration from JSON file.")

# 2. Test unsupported file format error
@patch("sfn_blueprint.config.config_manager.setup_logger")
@patch("builtins.open", new_callable=mock_open, read_data="some content")
def test_load_unsupported_file_format(mock_file, mock_setup_logger):
    """Test loading an unsupported file format raises ValueError."""
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)
    with pytest.raises(ValueError, match="Unsupported configuration file format"):
        SFNConfigManager(config_path="config/settings.txt")

# 3. Test FileNotFoundError during config load
@patch("sfn_blueprint.config.config_manager.setup_logger")
@patch("builtins.open", side_effect=FileNotFoundError)
def test_file_not_found_error(mock_file, mock_setup_logger):
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)

    with pytest.raises(FileNotFoundError):
        SFNConfigManager(config_path="config/missing_file.json")

    mock_logger.error.assert_called_once_with("Configuration file not found: config/missing_file.json")

# 4. Test JSONDecodeError during config load
@patch("sfn_blueprint.config.config_manager.setup_logger")
def test_json_decode_error(mock_setup_logger):
    """Test handling of invalid JSON content."""
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)
    
    mock_file = mock_open(read_data='{"invalid_json":')
    with patch("builtins.open", mock_file):
        with pytest.raises(json.JSONDecodeError):
            SFNConfigManager(config_path="config/invalid.json")

# 5. Test key retrieval from config
@patch("sfn_blueprint.config.config_manager.setup_logger")
@patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1", "key2": "value2"}')
def test_get_key_from_config(mock_file, mock_setup_logger):
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)

    config_manager = SFNConfigManager(config_path="config/settings.json")
    value = config_manager.get("key1")

    # Check that the value is retrieved correctly
    assert value == "value1"

# 6. Test key retrieval with default value
@patch("sfn_blueprint.config.config_manager.setup_logger")
@patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1"}')
def test_get_key_with_default(mock_file, mock_setup_logger):
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)

    config_manager = SFNConfigManager(config_path="config/settings.json")
    value = config_manager.get("missing_key", default="default_value")

    # Check that the default value is returned when the key is missing
    print('...................value:',value)
    assert value == "default_value"
    mock_logger.warning.assert_called_once_with("Key 'missing_key' not found, returning default: default_value")

# 7. Test loading YAML config
@patch("sfn_blueprint.config.config_manager.setup_logger")
@patch("builtins.open", new_callable=mock_open, read_data="key1: value1\nkey2: value2\n")
@patch("yaml.safe_load")
def test_load_yaml_config(mock_safe_load, mock_file, mock_setup_logger):
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)

    # Set up the mock to return a dictionary when safe_load is called
    mock_safe_load.return_value = {"key1": "value1", "key2": "value2"}

    config_manager = SFNConfigManager(config_path="config/settings.yaml")

    # Check that the config is loaded correctly for YAML files
    assert config_manager.config == {"key1": "value1", "key2": "value2"}
    mock_logger.info.assert_called_once_with("Loading configuration from YAML file.")

# 8. Test unexpected error during config load
@patch("sfn_blueprint.config.config_manager.setup_logger")
@patch("builtins.open", side_effect=Exception("Unexpected error"))
def test_unexpected_error(mock_file, mock_setup_logger):
    mock_logger = MagicMock()
    mock_setup_logger.return_value = (mock_logger, None)

    with pytest.raises(Exception, match="Unexpected error"):
        SFNConfigManager(config_path="config/settings.json")
    
    mock_logger.error.assert_called_once_with("Unexpected error while loading config: Unexpected error")