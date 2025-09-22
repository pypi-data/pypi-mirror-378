import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from sfn_blueprint import SFNAIHandler
from sfn_blueprint.utils.llm_handler.llm_clients import sfn_openai_client, sfn_anthropic_client, sfn_cortex_client, get_snowflake_session
from sfn_llm_client.llm_api_client.openai_client import OpenAIClient
# Mock environment variables for the tests
@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-openai-api-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-anthropic-api-key")
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "fake-account")
    monkeypatch.setenv("SNOWFLAKE_USER", "fake-user")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "fake-password")

# Test unsupported provider case
def test_route_to_unsupported_provider(mock_env_vars):
    handler = SFNAIHandler()
    response = handler.route_to(
        llm_provider="unsupported_provider",
        configuration={"messages": [{"role": "user", "content": "test"}]},
        model="some-model"
    )
    assert response is None

# Test exception handling in route_to method
def test_route_to_with_exception(mock_env_vars):
    with patch.object(OpenAIClient, 'chat_completion', side_effect=Exception("API call failed")) as mock_chat_completion:
        ai_handler = SFNAIHandler()

        with pytest.raises(Exception, match="API call failed"):
            ai_handler.route_to(
                llm_provider="openai",
                configuration={"messages": [{"role": "user", "content": "test"}]},
                model="gpt-3.5-turbo"
            )

        mock_chat_completion.assert_called_once()

# Test OpenAI client creation
def test_sfn_openai_client(mock_env_vars):
    with patch("sfn_blueprint.utils.llm_handler.llm_clients.OpenAIClient") as MockOpenAIClient:
        mock_client = MockOpenAIClient.return_value  # MockOpenAIClient() will return this
        client = sfn_openai_client("gpt-3.5-turbo")
        assert client is mock_client  # Use 'is' instead of '=='
        MockOpenAIClient.assert_called_once()

# Test Anthropic client creation
def test_sfn_anthropic_client(mock_env_vars):
    with patch("sfn_blueprint.utils.llm_handler.llm_clients.AnthropicClient") as MockAnthropicClient:
        mock_client = MockAnthropicClient.return_value  # MockAnthropicClient() will return this
        client = sfn_anthropic_client("claude-3-5-sonnet-20240620")
        assert client is mock_client  # Use 'is' instead of '=='
        MockAnthropicClient.assert_called_once()

# Test Cortex client creation
def test_sfn_cortex_client():
    with patch("sfn_blueprint.utils.llm_handler.llm_clients.CortexClient") as MockCortexClient:
        mock_client = MockCortexClient.return_value  # MockOpenAIClient() will return this
        client = sfn_cortex_client("snowflake-arctic")
        assert client is mock_client  # Use 'is' instead of '=='
        MockCortexClient.assert_called_once()

# Test the route_to method in SFNAIHandler for OpenAI
def test_route_to_openai(mock_env_vars):
    with patch("sfn_blueprint.utils.llm_handler.llm_clients.OpenAIClient.chat_completion") as mock_chat_completion:
        handler = SFNAIHandler()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_chat_completion.return_value = (mock_response, {"prompt_tokens": 10, "completion_tokens": 10})

        # Call the route_to method
        response, token_summary = handler.route_to(
            llm_provider="openai",
            configuration={"messages": [{"role": "user", "content": "test"}]},
            model="gpt-3.5-turbo"
        )

        # Assert the response and token_summary
        assert response == "Test response"
        assert token_summary == {"prompt_tokens": 10, "completion_tokens": 10}

# Test the route_to method in SFNAIHandler for Anthropic
def test_route_to_anthropic(mock_env_vars):
    with patch("sfn_blueprint.utils.llm_handler.llm_clients.AnthropicClient.chat_completion") as mock_chat_completion:
        ai_handler = SFNAIHandler()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_token_summary = {"prompt_tokens": 10, "completion_tokens": 10}
        
        # Set the return value of the mocked chat_completion method
        mock_chat_completion.return_value = (mock_response, mock_token_summary)

        response, token_summary = ai_handler.route_to(
            llm_provider="anthropic",
            configuration={"messages": [{"role": "user", "content": "test"}]},
            model="claude-3-5-sonnet-20240620"
        )
        print('response:',response)
        print('token_summary:',token_summary)
        # Ensure the mock returns the expected response
        assert response == "Test response"
        assert token_summary == mock_token_summary

# Test the route_to method in SFNAIHandler for Cortex
def test_route_to_cortex():
    with patch("sfn_blueprint.utils.llm_handler.llm_clients.CortexClient.chat_completion") as mock_chat_completion, \
         patch("sfn_blueprint.utils.llm_handler.llm_clients.get_snowflake_session") as mock_get_session:
        handler = SFNAIHandler()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(messages="Test response")]
        mock_chat_completion.return_value = (mock_response, {"prompt_tokens": 10, "completion_tokens": 10})
        mock_get_session.return_value = MagicMock()

        # Call the route_to method
        response, token_summary = handler.route_to(
            llm_provider="cortex",
            configuration={"messages": [{"role": "user", "content": "test"}]},
            model="snowflake-arctic"
        )
        print('response:',response)
        print('token_summary:',token_summary)
        # Assert the response and token_summary
        assert response == "Test response"
        assert token_summary == {"prompt_tokens": 10, "completion_tokens": 10}

# Test Snowflake session creation
def test_get_snowflake_session_with_password():
    with patch("sfn_blueprint.utils.llm_handler.llm_clients.Session.builder.configs") as mock_builder:
        mock_session = mock_builder.return_value.create.return_value
        session = get_snowflake_session()
        assert session == mock_session
        mock_builder.assert_called_once()
