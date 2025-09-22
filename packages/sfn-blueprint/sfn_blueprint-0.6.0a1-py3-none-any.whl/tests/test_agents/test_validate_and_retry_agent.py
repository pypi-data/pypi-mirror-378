import pytest
from unittest.mock import MagicMock
from sfn_blueprint import SFNValidateAndRetryAgent

DEFAULT_LLM_PROVIDER = 'openai'

# Mock dependencies
@pytest.fixture
def mock_logger():
    logger = MagicMock()
    return logger

@pytest.fixture
def mock_prompt_manager():
    prompt_manager = MagicMock()
    prompt_manager.get_prompt.return_value = ("system_prompt", "user_prompt")
    return prompt_manager

@pytest.fixture
def mock_ai_handler():
    ai_handler = MagicMock()
    ai_handler.route_to.return_value = ("TRUE\nValidation successful", {"tokens": 100})
    return ai_handler

@pytest.fixture
def mock_task():
    task = MagicMock()
    task.execute_task.return_value = {"result": "some result"}
    return task

@pytest.fixture
def mock_validation_task():
    validation_task = MagicMock()
    return validation_task

@pytest.fixture
def mock_suggestion_agent():
    suggestion_agent = MagicMock()
    suggestion_agent.execute_task.return_value = {"result": "valid result"}
    suggestion_agent.get_validation_params.return_value = {
        "system_prompt": "system validation prompt", 
        "user_prompt": "user validation prompt"
    }
    return suggestion_agent

# Create the ValidateAndRetryAgent instance with mocks
@pytest.fixture
def validation_agent(mock_prompt_manager, mock_ai_handler, mock_logger):
    agent = SFNValidateAndRetryAgent(llm_provider=DEFAULT_LLM_PROVIDER, for_agent='category_identifier')
    agent.prompt_manager = mock_prompt_manager
    agent.ai_handler = mock_ai_handler
    agent.logger = mock_logger
    return agent

# Test for successful completion without retries
def test_complete_success(validation_agent, mock_suggestion_agent, mock_task, mock_validation_task):
    validation_agent.validate = MagicMock(return_value=(True, "Validation successful"))  # Mock validation to return True
    response, message, is_valid = validation_agent.complete(
        agent_to_validate=mock_suggestion_agent, 
        task=mock_task, 
        validation_task=mock_validation_task, 
        method_name='execute_task',
        get_validation_params='get_validation_params'
    )
    
    assert response == {"result": "valid result"}  # Verify that the correct response is returned
    assert message == "Validation successful"
    assert is_valid is True
    validation_agent.validate.assert_called_once()  # Ensure validation was called only once

# Test for retries on validation failure and then success
def test_complete_with_retries(validation_agent, mock_suggestion_agent, mock_task, mock_validation_task):
    validation_agent.validate = MagicMock(side_effect=[(False, "Failed validation"), (False, "Failed validation"), (True, "Validation successful")])  # Fail first 2 attempts, then succeed
    
    response, message, is_valid = validation_agent.complete(
        agent_to_validate=mock_suggestion_agent, 
        task=mock_task, 
        validation_task=mock_validation_task, 
        method_name='execute_task',
        get_validation_params='get_validation_params',
        max_retries=3
    )
    
    assert response == {"result": "valid result"}
    assert message == "Validation successful"
    assert is_valid is True
    assert validation_agent.validate.call_count == 3  # Ensure validation was called 3 times (with retries)

# Test for retries but max retry limit exceeded
def test_complete_retry_limit_exceeded(validation_agent, mock_suggestion_agent, mock_task, mock_validation_task):
    validation_agent.validate = MagicMock(return_value=(False, "Failed validation"))  # Always fail validation
    
    response, message, is_valid = validation_agent.complete(
        agent_to_validate=mock_suggestion_agent, 
        task=mock_task, 
        validation_task=mock_validation_task, 
        method_name='execute_task',
        get_validation_params='get_validation_params',
        max_retries=3
    )

    assert response == {"result": "valid result"}
    assert message == "Validation failed:Failed validation"
    assert is_valid is False
    assert validation_agent.validate.call_count == 3  # Ensure it stopped after max retries

# Test validation handling when empty response is returned
def test_complete_empty_response(validation_agent, mock_suggestion_agent, mock_task, mock_validation_task):
    mock_suggestion_agent.execute_task.return_value = {}  # Return an empty response
    validation_agent.validate = MagicMock(return_value=(True, "Validation successful"))  # Force validation to succeed

    response, message, is_valid = validation_agent.complete(
        agent_to_validate=mock_suggestion_agent, 
        task=mock_task, 
        validation_task=mock_validation_task, 
        method_name='execute_task',
        get_validation_params='get_validation_params'
    )
    
    assert response == {}  # Check that the empty response is returned
    assert message == "Validation successful"
    assert is_valid is True
    validation_agent.validate.assert_called_once()  # Validation should still be called

# Test for validation delay between retries
def test_complete_with_retry_delay(validation_agent, mock_suggestion_agent, mock_task, mock_validation_task, mocker):
    mock_sleep = mocker.patch('time.sleep', return_value=None)  # Mock sleep to avoid actual delays
    validation_agent.validate = MagicMock(side_effect=[(False, "Failed validation"), (True, "Validation successful")])  # Fail first attempt, succeed on second
    
    response, message, is_valid = validation_agent.complete(
        agent_to_validate=mock_suggestion_agent, 
        task=mock_task, 
        validation_task=mock_validation_task, 
        method_name='execute_task',
        get_validation_params='get_validation_params',
        max_retries=3,
        retry_delay=3.0
    )
    
    assert response == {"result": "valid result"}
    assert message == "Validation successful"
    assert is_valid is True
    mock_sleep.assert_called_once_with(3.0)  # Ensure sleep was called with the specified retry delay

# Test for parsing validation result (TRUE case)
def test_parse_validation_result_true(validation_agent):
    llm_response = "TRUE\nValidation successful"
    is_valid, message = validation_agent._parse_validation_result(llm_response)
    
    assert is_valid is True  # Ensure "TRUE" is interpreted as a valid result
    assert message == "Validation successful"

# Test for parsing validation result (FALSE case)
def test_parse_validation_result_false(validation_agent):
    llm_response = "FALSE\nValidation failed"
    is_valid, message = validation_agent._parse_validation_result(llm_response)
    
    assert is_valid is False  # Ensure "FALSE" is interpreted as an invalid result
    assert message == "Validation failed"

# Test for parsing validation result when exception occurs
def test_parse_validation_result_exception(validation_agent):
    llm_response = "Invalid response format"
    is_valid, message = validation_agent._parse_validation_result(llm_response)
    
    assert is_valid is False
    assert "Error parsing validation result" in message