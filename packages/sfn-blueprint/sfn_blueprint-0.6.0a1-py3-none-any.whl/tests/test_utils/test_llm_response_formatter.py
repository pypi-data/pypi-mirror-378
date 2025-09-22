import pytest
import json
from unittest.mock import MagicMock, call
from sfn_blueprint import llm_response_formatter


@pytest.fixture
def mock_logger():
    """Fixture to provide a mock logger."""
    return MagicMock()


def test_llm_response_formatter_cortex(mock_logger):
    """Test formatting a Cortex response."""
    response = {'choices': [{'messages': 'Hello from Cortex!'}]}
    llm_provider = 'cortex'

    formatted_response = llm_response_formatter(response, llm_provider, mock_logger)
    
    # Check the sequence of logger calls
    expected_calls = [
        call('formatting llm response....'),
        call('extracting message content from llm response....'),
        call('formatted response: Hello from Cortex!')
    ]
    
    # Assert that all expected calls were made in order
    mock_logger.info.assert_has_calls(expected_calls, any_order=False)

    assert formatted_response == 'Hello from Cortex!'

def test_llm_response_formatter_anthropic(mock_logger):
    """Test formatting an Anthropic response."""
    response = MagicMock()
    response.content = [MagicMock(text="Hello from Anthropic!")]
    llm_provider = 'anthropic'

    formatted_response = llm_response_formatter(response, llm_provider, mock_logger)

    expected_calls = [
        call('formatting llm response....'),
        call('extracting message content from llm response....'),
        call('formatted response: Hello from Anthropic!')
    ]
    
    mock_logger.info.assert_has_calls(expected_calls, any_order=False)
    assert formatted_response == 'Hello from Anthropic!'


def test_llm_response_formatter_openai(mock_logger):
    """Test formatting an OpenAI response."""
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content="Hello from OpenAI!"))]
    llm_provider = 'openai'

    formatted_response = llm_response_formatter(response, llm_provider, mock_logger)

    expected_calls = [
        call('formatting llm response....'),
        call('extracting message content from llm response....'),
        call('formatted response: Hello from OpenAI!')
    ]
    
    mock_logger.info.assert_has_calls(expected_calls, any_order=False)
    assert formatted_response == 'Hello from OpenAI!'


def test_llm_response_formatter_tuple_response(mock_logger):
    """Test when response is passed as a tuple."""
    response = ({'choices': [{'messages': 'Hello from Tuple!'}]}, )
    llm_provider = 'cortex'

    formatted_response = llm_response_formatter(response, llm_provider, mock_logger)

    expected_calls = [
        call('formatting llm response....'), 
        call('llm tuple response formatting...'),
        call('extracting message content from llm response....'),
        call('formatted response: Hello from Tuple!')
    ]
    
    mock_logger.info.assert_has_calls(expected_calls, any_order=False)
    assert formatted_response == 'Hello from Tuple!'


def test_llm_response_formatter_json_string(mock_logger):
    """Test when response is a JSON string."""
    response = json.dumps({'choices': [{'messages': 'Hello from JSON string!'}]})
    llm_provider = 'cortex'

    formatted_response = llm_response_formatter(response, llm_provider, mock_logger)

    expected_calls = [
        call('formatting llm response....'), 
        call('llm json string response formatting...'),
        call('extracting message content from llm response....'),
        call('formatted response: Hello from JSON string!')
    ]
    
    mock_logger.info.assert_has_calls(expected_calls, any_order=False)
    assert formatted_response == 'Hello from JSON string!'
    
def test_llm_response_formatter_unsupported_provider(mock_logger):
    """Test unsupported llm provider case."""
    response = {'choices': [{'messages': 'Hello!'}]}
    llm_provider = 'unsupported_provider'

    # Verify that a KeyError is raised
    with pytest.raises(KeyError, match=f"Unsupported provider: {llm_provider}"):
        llm_response_formatter(response, llm_provider, mock_logger)

    # Check that the error was logged
    mock_logger.error.assert_called_once_with(
        f"Error while formatting llm response {llm_provider}: 'Unsupported provider: {llm_provider}'"
    )


def test_llm_response_formatter_invalid_json(mock_logger):
    """Test invalid JSON format in response."""
    response = '{"invalid_json": "missing_end"}'  # Simulate an invalid JSON
    llm_provider = 'cortex'

    # Verify that a JSONDecodeError is raised
    with pytest.raises(ValueError):
        llm_response_formatter(response, llm_provider, mock_logger)

    # Check that an error was logged
    mock_logger.error.assert_called_once()

    # Optionally, you can check the error message contains relevant information
    error_call = mock_logger.error.call_args[0][0]
    # Escape curly braces in f-string or use the format method
    expected_error_message = f"Invalid response format from llm provider {llm_provider}, response: {{'invalid_json': 'missing_end'}}"
    assert expected_error_message in error_call
