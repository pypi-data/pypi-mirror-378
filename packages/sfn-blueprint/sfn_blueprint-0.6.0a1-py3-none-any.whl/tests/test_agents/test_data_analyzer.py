import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from sfn_blueprint import SFNDataAnalyzerAgent

# Mock task class for testing
class Task:
    def __init__(self, data):
        self.data = data

@pytest.fixture
def mock_logger():
    """Fixture to create a mock logger."""
    return MagicMock()

# 1. Test successful data analysis with both numeric and categorical data
def test_data_analysis_success():
    agent = SFNDataAnalyzerAgent()

    # Mock task with numeric and categorical data
    task = Task(
        data=pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'categorical_col': ['A', 'B', 'A', 'B', 'C']
        })
    )

    summary = agent.execute_task(task)

    # Check that the summary includes the expected keys and values
    assert 'shape' in summary
    assert summary['shape'] == (5, 2)
    assert 'columns' in summary
    assert summary['columns'] == ['numeric_col', 'categorical_col']
    assert 'dtypes' in summary
    assert summary['dtypes'] == {'numeric_col': 'int64', 'categorical_col': 'object'}
    assert 'missing_values' in summary
    assert summary['missing_values'] == {'numeric_col': 0, 'categorical_col': 0}
    assert 'duplicates' in summary
    assert summary['duplicates'] == 0
    assert 'numeric_summary' in summary
    assert 'categorical_summary' in summary

# 2. Test data analysis with missing values
def test_data_analysis_with_missing_values():
    agent = SFNDataAnalyzerAgent()

    # Mock task with missing values
    task = Task(
        data=pd.DataFrame({
            'numeric_col': [1, 2, None, 4, 5],
            'categorical_col': ['A', 'B', None, 'B', 'C']
        })
    )

    summary = agent.execute_task(task)

    # Check that the missing values are correctly reported
    assert summary['missing_values'] == {'numeric_col': 1, 'categorical_col': 1}

# 3. Test data analysis with duplicate rows
def test_data_analysis_with_duplicates():
    agent = SFNDataAnalyzerAgent()

    # Mock task with duplicate rows
    task = Task(
        data=pd.DataFrame({
            'numeric_col': [1, 2, 2, 4, 5],
            'categorical_col': ['A', 'B', 'B', 'B', 'C']
        })
    )

    summary = agent.execute_task(task)

    # Check that the number of duplicate rows is correctly reported
    assert summary['duplicates'] == 1

# 4. Test data analysis with only numeric data
def test_data_analysis_numeric_only():
    agent = SFNDataAnalyzerAgent()

    # Mock task with only numeric data
    task = Task(
        data=pd.DataFrame({
            'numeric_col1': [1, 2, 3, 4, 5],
            'numeric_col2': [5, 4, 3, 2, 1]
        })
    )

    summary = agent.execute_task(task)

    # Check that the numeric summary is provided and the categorical summary is empty
    assert 'numeric_summary' in summary
    assert len(summary['categorical_summary']) == 0

# 5. Test data analysis with only categorical data
def test_data_analysis_categorical_only():
    agent = SFNDataAnalyzerAgent()

    # Mock task with only categorical data
    task = Task(
        data=pd.DataFrame({
            'categorical_col1': ['A', 'B', 'A', 'B', 'C'],
            'categorical_col2': ['X', 'Y', 'Y', 'X', 'Z']
        })
    )

    summary = agent.execute_task(task)

    # Check that the categorical summary is provided and the numeric summary is empty
    assert 'categorical_summary' in summary
    assert len(summary['numeric_summary']) == 0

# 6. Test error during data analysis (e.g., invalid data)
def test_data_analysis_error():
    agent = SFNDataAnalyzerAgent()

    # Mock task with invalid data that will raise an exception (e.g., unsupported data type)
    task = Task(
        data=pd.DataFrame({
            'numeric_col': [1, 2, 3],
            'invalid_col': [{'a': 1}, {'b': 2}, {'c': 3}]  # Column with dictionaries
        })
    )

    # Check that the code raises a ValueError or TypeError during analysis
    with pytest.raises(TypeError):
        agent.execute_task(task)

# 7. Test logging during data analysis
def test_logging_during_analysis(mock_logger):
    agent = SFNDataAnalyzerAgent()
    agent.logger = mock_logger

    # Mock task with valid data
    task = Task(
        data=pd.DataFrame({
            'numeric_col': [1, 2, 3, 4, 5],
            'categorical_col': ['A', 'B', 'A', 'B', 'C']
        })
    )

    # Run the task and verify logging behavior
    agent.execute_task(task)

    # Check that logger.info was called with expected messages
    mock_logger.info.assert_any_call("Starting data analysis...")
    mock_logger.info.assert_any_call("Data analysis completed successfully.")
    mock_logger.info.assert_any_call("DataFrame shape: (5, 2)")
    mock_logger.info.assert_any_call("Columns: ['numeric_col', 'categorical_col']")
