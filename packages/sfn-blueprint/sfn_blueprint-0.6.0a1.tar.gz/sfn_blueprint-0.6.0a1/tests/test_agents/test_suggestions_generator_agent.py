import json
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from sfn_blueprint import SFNSuggestionsGeneratorAgent
from sfn_blueprint import Task
from sfn_blueprint import SFNAIHandler
from sfn_blueprint import MODEL_CONFIG
from sfn_blueprint import SFNPromptManager

DEFAULT_LLM_PROVIDER = 'openai'

# Fixture to create an instance of the SFNSuggestionsGeneratorAgent
@pytest.fixture
def suggestions_agent():
    return SFNSuggestionsGeneratorAgent(llm_provider=DEFAULT_LLM_PROVIDER)

# Fixture for a mock task
@pytest.fixture
def mock_task():
    return Task(description="", data={'df': MagicMock(columns=['col1', 'col2'], head=lambda x: MagicMock(to_dict=lambda orient: {}), describe=lambda: {})},
                task_type='test_type', category='test_category')

# Mock the ai_handler route_to method to simulate LLM API responses
@pytest.fixture
def mock_route_to():
    with patch.object(SFNAIHandler, 'route_to', return_value=({"choices": [{"message": {"content": "suggestion1\nsuggestion2\n"}}]}, {'cost': 0.1})) as mock_method:
        yield mock_method

# Mock logging setup
@pytest.fixture
def mock_logger():
    """Fixture to create a mock logger."""
    return MagicMock()

# Test for logger setup in constructor
def test_logger_setup(mock_logger):
        suggestions_generator_agent = SFNSuggestionsGeneratorAgent(llm_provider=DEFAULT_LLM_PROVIDER)
        suggestions_generator_agent.logger = mock_logger
        mock_logger.assert_called_once_with(logger_name="SFNSuggestionsGeneratorAgent")

# Test error handling for invalid task data
def test_execute_task_invalid_data(suggestions_agent):
    invalid_task = Task(description='', data={'wrong_key': 'value'}, task_type='test_type', category='test_category')
    with pytest.raises(ValueError, match="Task data must be a dictionary containing 'df' key"):
        suggestions_agent.execute_task(invalid_task)

# Test empty DataFrame handling in execute_task
def test_execute_task_empty_dataframe(suggestions_agent):
    empty_df = pd.DataFrame()
    task = Task(description='', data={"df": empty_df}, task_type="test_type", category="test_category")
    with patch.object(SFNSuggestionsGeneratorAgent, '_generate_suggestions', return_value=[]):
        result = suggestions_agent.execute_task(task)
        assert result == []

# Test empty response from LLM
def test_generate_suggestions_empty_response(suggestions_agent):
    columns = ['col1', 'col2']
    sample_records = [{"col1": "val1", "col2": "val2"}]
    describe_dict = {"col1": {"mean": 1.0, "std": 0.1}, "col2": {"mean": 2.0, "std": 0.2}}
    
    with patch.object(SFNAIHandler, 'route_to', return_value=({"choices": [{"message": {"content": ""}}]}, {'cost': 0.1})):
        suggestions = suggestions_agent._generate_suggestions(columns, sample_records, describe_dict, 'feature_suggestion', 'generic')
        assert suggestions == []

# Test for task execution success with default LLM provider (OpenAI)
def test_execute_task_default_llm(suggestions_agent, mock_task, mock_route_to):
    result = suggestions_agent.execute_task(mock_task)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == 'suggestion1'
    assert result[1] == 'suggestion2'
    mock_route_to.assert_called_once_with(DEFAULT_LLM_PROVIDER, Any, MODEL_CONFIG['suggestions_generator'][DEFAULT_LLM_PROVIDER]['model'])

# Test for task execution with specific LLM provider (Anthropic)
def test_execute_task_anthropic_llm(suggestions_agent, mock_task, mock_route_to):
    result = suggestions_agent.execute_task(mock_task)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == 'suggestion1'
    assert result[1] == 'suggestion2'
    mock_route_to.assert_called_once_with('anthropic', Any, MODEL_CONFIG['suggestions_generator']['anthropic']['model'])

# Test for task execution with Cortex LLM provider
def test_execute_task_cortex_llm(suggestions_agent, mock_task, mock_route_to):
    result = suggestions_agent.execute_task(mock_task)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == 'suggestion1'
    assert result[1] == 'suggestion2'
    mock_route_to.assert_called_once_with('cortex', Any, MODEL_CONFIG['suggestions_generator']['cortex']['model'])

# Test for unsupported LLM provider
def test_route_to_unsupported_llm(suggestions_agent, mock_task):
    with pytest.raises(Exception):
        SFNSuggestionsGeneratorAgent(llm_provider='unsupported_llm')
        suggestions_agent.execute_task(mock_task)

# Test for edge case: Null values in the DataFrame
def test_execute_task_with_null_values(suggestions_agent):
    df = pd.DataFrame({
        "col1": [1, None, 3],
        "col2": [None, 5, 6]
    })
    task = Task(description='', data={"df": df}, task_type="test_type", category="test_category")
    with patch.object(SFNSuggestionsGeneratorAgent, '_generate_suggestions', return_value=[]):
        result = suggestions_agent.execute_task(task)
        assert result == []

# Test for large dataset performance (mock LLM response)
def test_execute_task_large_dataset(suggestions_agent):
    large_df = pd.DataFrame({
        "col1": range(10000),
        "col2": range(10000, 20000)
    })
    task = Task(description='', data={"df": large_df}, task_type="test_type", category="test_category")
    
    with patch.object(SFNSuggestionsGeneratorAgent, '_generate_suggestions', return_value=["suggestion"] * 100):
        result = suggestions_agent.execute_task(task)
        assert len(result) == 100

def test_agent_initialization():
    agent = SFNSuggestionsGeneratorAgent(llm_provider=DEFAULT_LLM_PROVIDER)
    assert agent.llm_provider == DEFAULT_LLM_PROVIDER
    assert isinstance(agent.prompt_manager, SFNPromptManager)
    assert isinstance(agent.ai_handler, SFNAIHandler)
    assert agent.logger is not None

def test_execute_task_valid_input():
    # Create a mock Task with a dataframe
    task_data = {"df": pd.DataFrame({"column1": [1, 2, 3], "column2": [4, 5, 6]})}
    task = Task(description='', data=task_data, task_type="feature_suggestion", category="test_category")
    agent = SFNSuggestionsGeneratorAgent(llm_provider=DEFAULT_LLM_PROVIDER)

    suggestions = agent.execute_task(task)
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0  # Check that suggestions are generated

def test_execute_task_invalid_input():
    task_data = {}  # Invalid data, missing 'df'
    task = Task(description='', data=task_data, task_type="feature_suggestion", category="test_category")
    agent = SFNSuggestionsGeneratorAgent(llm_provider=DEFAULT_LLM_PROVIDER)

    with pytest.raises(ValueError):
        agent.execute_task(task)

# Test the suggestion generation process for valid suggestions
def test_generate_suggestions(suggestions_agent):
    columns = ['col1', 'col2']
    sample_records = [{"col1": "val1", "col2": "val2"}]
    describe_dict = {"col1": {"mean": 1.0, "std": 0.1}, "col2": {"mean": 2.0, "std": 0.2}}
    task_type = 'feature_suggestion'
    category = 'generic'
    llm_provider=DEFAULT_LLM_PROVIDER

    with patch.object(SFNAIHandler, 'route_to', return_value=({"choices": [{"message": {"content": "suggestion1\nsuggestion2\n"}}]}, {'cost': 0.1})):
        suggestions = suggestions_agent._generate_suggestions(columns, sample_records, describe_dict, task_type, category, llm_provider)
        assert len(suggestions) == 2
        assert suggestions[0] == 'suggestion1'
        assert suggestions[1] == 'suggestion2'
        
def test_parse_suggestions(suggestions_agent):
    suggestions_text = "1. Suggestion 1\n2. Suggestion 2\n"
    
    parsed_suggestions = suggestions_agent._parse_suggestions(suggestions_text)
    assert isinstance(parsed_suggestions, list)
    assert len(parsed_suggestions) == 2  # Check that there are two parsed suggestions
    assert parsed_suggestions == ["Suggestion 1", "Suggestion 2"]
    
    # Test malformed suggestions
def test_parse_suggestions_malformed_text(suggestions_agent):
    malformed_suggestions = "1. suggestion1 2) suggestion2\ninvalid_line suggestion3"
    parsed_suggestions = suggestions_agent._parse_suggestions(malformed_suggestions)
    assert parsed_suggestions == ['suggestion1', 'suggestion2', 'invalid_line suggestion3']
