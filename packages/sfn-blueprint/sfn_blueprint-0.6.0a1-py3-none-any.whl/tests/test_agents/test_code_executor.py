import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from sfn_blueprint import SFNCodeExecutorAgent

# Mock task class for testing
class Task:
    def __init__(self, code, data):
        self.code = code
        self.data = data

@pytest.fixture
def mock_logger():
    """Fixture to create a mock logger."""
    return MagicMock()

# 1. Test successful code execution
def test_code_execution_success():
    agent = SFNCodeExecutorAgent()

    # Mock task with simple code that modifies the DataFrame
    task = Task(
        code="df['new_col'] = df['col1'] * 2",
        data=pd.DataFrame({'col1': [1, 2, 3]})
    )

    result_df = agent.execute_task(task)
    
    # Check if the DataFrame was modified correctly
    assert 'new_col' in result_df.columns
    assert all(result_df['new_col'] == [2, 4, 6])

# 2. Test code execution with an exception
def test_code_execution_error():
    agent = SFNCodeExecutorAgent()

    # Mock task with code that will raise an error
    task = Task(
        code="df['new_col'] = non_existent_variable",  # undefined variable
        data=pd.DataFrame({'col1': [1, 2, 3]})
    )

    # Check that the code raises an error during execution
    with pytest.raises(NameError):
        agent.execute_task(task)

# 3. Test missing 'df' in local environment after execution
def test_missing_df_key_error():
    agent = SFNCodeExecutorAgent()

    # Mock task with code that deletes 'df' from local_env
    task = Task(
        code="del df",  # This deletes the 'df' variable
        data=pd.DataFrame({'col1': [1, 2, 3]})
    )

    # Check that a KeyError is raised when 'df' is missing
    with pytest.raises(KeyError, match="'df' key DataFrame not  found in the local environment after code execution"):
        agent.execute_task(task)

# 4. Test logging during task execution
def test_logging_during_execution(mock_logger):
    agent = SFNCodeExecutorAgent()
    agent.logger = mock_logger

    # Mock task with valid code
    task = Task(
        code="df['new_col'] = df['col1'] * 2",
        data=pd.DataFrame({'col1': [1, 2, 3]})
    )

    # Run the task and verify logging behavior
    agent.execute_task(task)

    # Check that logger.info was called with expected messages
    mock_logger.info.assert_any_call(f"Executing task with provided code: {task.code[:100]}...")
    mock_logger.info.assert_any_call("Executing code...")
    mock_logger.info.assert_any_call("Code execution successful")
    mock_logger.info.assert_any_call("Returning modified DataFrame")
