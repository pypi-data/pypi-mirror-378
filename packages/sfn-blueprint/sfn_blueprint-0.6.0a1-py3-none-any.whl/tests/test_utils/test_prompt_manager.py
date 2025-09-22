import pytest
import os
import json
from unittest.mock import patch, mock_open
from sfn_blueprint import SFNPromptManager


@pytest.fixture
def valid_prompts_config():
    """Fixture to provide a valid prompts configuration"""
    return {
        "feature_suggester": {
            "openai": {
                "main": {
                    "system_prompt": "You are a helpful assistant.",
                    "user_prompt_template": "Suggest features for {project_name}."
                },
                "validation": {
                    "system_prompt": "Validate the feature suggestions.",
                    "user_prompt_template": "Please validate the features for {project_name}."
                }
            }
        }
    }


def test_initialization_with_valid_config(monkeypatch, valid_prompts_config):
    """Test initialization of SFNPromptManager with valid config"""
    config_json = json.dumps(valid_prompts_config)
    mock_open_file = mock_open(read_data=config_json)

    with patch("builtins.open", mock_open_file):
        with patch("os.path.exists", return_value=True):
            prompt_manager = SFNPromptManager(prompts_config_path="fake_path.json")
            assert prompt_manager.prompts_config == valid_prompts_config


def test_initialization_with_invalid_json():
    """Test initialization failure due to invalid JSON format"""
    invalid_json = "{invalid_json"
    mock_open_file = mock_open(read_data=invalid_json)

    with patch("builtins.open", mock_open_file):
        with patch("os.path.exists", return_value=True):
            with pytest.raises(RuntimeError, match="Invalid JSON in config file:"):
                SFNPromptManager(prompts_config_path="fake_path.json")

def test_initialization_with_missing_config():
    """Test initialization failure due to missing config file"""
    with patch("os.path.exists", return_value=False):
        with pytest.raises(RuntimeError, match="Prompts config file not found at:"):
            SFNPromptManager(prompts_config_path="non_existing_path.json")

def test_get_prompt_with_valid_params(monkeypatch, valid_prompts_config):
    """Test getting the prompt with valid agent type and LLM provider"""
    config_json = json.dumps(valid_prompts_config)
    mock_open_file = mock_open(read_data=config_json)

    with patch("builtins.open", mock_open_file):
        with patch("os.path.exists", return_value=True):
            prompt_manager = SFNPromptManager(prompts_config_path="fake_path.json")
            
            # Test for main prompt
            system_prompt, user_prompt = prompt_manager.get_prompt(
                agent_type="feature_suggester",
                llm_provider="openai",
                prompt_type="main",
                project_name="TestProject"
            )
            assert system_prompt == "You are a helpful assistant."
            assert user_prompt == "Suggest features for TestProject."


def test_get_prompt_with_invalid_agent_type(monkeypatch, valid_prompts_config):
    """Test getting the prompt with invalid agent type"""
    config_json = json.dumps(valid_prompts_config)
    mock_open_file = mock_open(read_data=config_json)

    with patch("builtins.open", mock_open_file):
        with patch("os.path.exists", return_value=True):
            prompt_manager = SFNPromptManager(prompts_config_path="fake_path.json")
            
            with pytest.raises(ValueError, match="Unknown agent type"):
                prompt_manager.get_prompt(
                    agent_type="invalid_agent",
                    llm_provider="openai",
                    prompt_type="main"
                )


def test_get_prompt_with_invalid_llm_provider(monkeypatch, valid_prompts_config):
    """Test getting the prompt with invalid LLM provider"""
    config_json = json.dumps(valid_prompts_config)
    mock_open_file = mock_open(read_data=config_json)

    with patch("builtins.open", mock_open_file):
        with patch("os.path.exists", return_value=True):
            prompt_manager = SFNPromptManager(prompts_config_path="fake_path.json")
            
            with pytest.raises(ValueError, match="Unknown LLM provider"):
                prompt_manager.get_prompt(
                    agent_type="feature_suggester",
                    llm_provider="invalid_provider",
                    prompt_type="main"
                )


def test_get_prompt_with_invalid_prompt_type(monkeypatch, valid_prompts_config):
    """Test getting the prompt with invalid prompt type"""
    config_json = json.dumps(valid_prompts_config)
    mock_open_file = mock_open(read_data=config_json)

    with patch("builtins.open", mock_open_file):
        with patch("os.path.exists", return_value=True):
            prompt_manager = SFNPromptManager(prompts_config_path="fake_path.json")
            
            with pytest.raises(ValueError, match="Unknown prompt type"):
                prompt_manager.get_prompt(
                    agent_type="feature_suggester",
                    llm_provider="openai",
                    prompt_type="invalid_prompt_type"
                )


def test_get_validation_prompt_format(monkeypatch, valid_prompts_config):
    """Test that validation prompts return a dictionary format"""
    config_json = json.dumps(valid_prompts_config)
    mock_open_file = mock_open(read_data=config_json)

    with patch("builtins.open", mock_open_file):
        with patch("os.path.exists", return_value=True):
            prompt_manager = SFNPromptManager(prompts_config_path="fake_path.json")
            
            prompts_dict = prompt_manager.get_prompt(
                agent_type="feature_suggester",
                llm_provider="openai",
                prompt_type="validation",
                project_name="TestProject"
            )
            assert isinstance(prompts_dict, dict)
            assert prompts_dict["system_prompt"] == "Validate the feature suggestions."
            assert prompts_dict["user_prompt"] == "Please validate the features for TestProject."
