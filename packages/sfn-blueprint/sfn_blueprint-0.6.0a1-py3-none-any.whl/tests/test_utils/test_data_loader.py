# Updated test cases with correct logger mocking and call assertions

import pytest
import os
from unittest import mock
import pandas as pd
from sfn_blueprint import SFNDataLoader 
from unittest.mock import MagicMock

@pytest.fixture
def data_loader():
    """Fixture to create an instance of SFNDataLoader for tests."""
    return SFNDataLoader()

@pytest.fixture
def mock_logger():
    """Fixture to create a mock logger."""
    return MagicMock()

def test_file_not_found(data_loader, mock_logger):
    """Test that FileNotFoundError is raised when the file does not exist."""
    task = mock.Mock()
    task.path = "non_existent_file.csv"
    
    with pytest.raises(FileNotFoundError, match="File not found: non_existent_file.csv"):
        data_loader.execute_task(task)
    
    mock_logger.error.assert_not_called()

def test_unsupported_file_format(data_loader, mock_logger, tmpdir):
    """Test that ValueError is raised for unsupported file formats."""
    # Create a dummy file with an unsupported extension
    data_loader.logger = mock_logger
    unsupported_file = tmpdir.join("data.txt")
    unsupported_file.write("dummy content")

    task = mock.Mock()
    task.path = str(unsupported_file)

    with pytest.raises(ValueError, match="Unsupported file format. Please provide a CSV, Excel, JSON, or Parquet file."):
        data_loader.execute_task(task)

    mock_logger.error.assert_called_once_with("Unsupported file format: txt")

    
def test_load_csv(data_loader, mock_logger, tmpdir):
    """Test that CSV files are loaded correctly."""
    data_loader.logger = mock_logger
    # Create a dummy CSV file
    csv_file = tmpdir.join("data.csv")
    csv_file.write("col1,col2\n1,2\n3,4")

    task = mock.Mock()
    task.path = str(csv_file)

    # Mock dask read_csv to avoid actual file I/O
    with mock.patch("dask.dataframe.read_csv") as mock_read_csv:
        mock_dask_df = mock.Mock()
        mock_read_csv.return_value = mock_dask_df
        mock_dask_df.compute.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})

        result = data_loader.execute_task(task)

    assert isinstance(result, pd.DataFrame)
    assert result.equals(pd.DataFrame({"col1": [1, 3], "col2": [2, 4]}))

    # Ensure the logger was called with the correct messages
    mock_logger.info.assert_any_call("Received file with extension: csv")
    mock_logger.info.assert_any_call("Loading file using CSV loader")
    mock_logger.info.assert_any_call("Loading CSV file")


def test_load_json(data_loader, mock_logger, tmpdir):
    """Test that JSON files are loaded correctly."""
    data_loader.logger = mock_logger
    
    json_file = tmpdir.join("data.json")
    json_file.write('{"col1": [1, 3], "col2": [2, 4]}')
    task = mock.Mock()
    task.path = str(json_file)
    
    with mock.patch("pandas.read_json") as mock_read_json:
        mock_read_json.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
        result = data_loader.execute_task(task)
    
    expected_calls = [
        mock.call("Received file with extension: json"),
        mock.call("Loading file using JSON loader"),
        mock.call("Loading JSON file")
    ]
    assert mock_logger.info.call_args_list == expected_calls

def test_load_excel(data_loader, mock_logger, tmpdir):
    """Test that Excel files are loaded correctly."""
    data_loader.logger = mock_logger
    
    excel_file = tmpdir.join("data.xlsx")
    excel_file.write("dummy excel content")
    task = mock.Mock()
    task.path = str(excel_file)
    
    with mock.patch("pandas.read_excel") as mock_read_excel:
        mock_read_excel.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
        result = data_loader.execute_task(task)
    
    expected_calls = [
        mock.call("Received file with extension: xlsx"),
        mock.call("Loading file using XLSX loader"),
        mock.call("Loading Excel file")
    ]
    assert mock_logger.info.call_args_list == expected_calls

def test_load_parquet(data_loader, mock_logger, tmpdir):
    """Test that Parquet files are loaded correctly."""
    data_loader.logger = mock_logger
    
    parquet_file = tmpdir.join("data.parquet")
    parquet_file.write("dummy parquet content")
    task = mock.Mock()
    task.path = str(parquet_file)
    
    with mock.patch("dask.dataframe.read_parquet") as mock_read_parquet:
        mock_dask_df = mock.Mock()
        mock_read_parquet.return_value = mock_dask_df
        mock_dask_df.compute.return_value = pd.DataFrame({"col1": [1, 3], "col2": [2, 4]})
        result = data_loader.execute_task(task)
    
    expected_calls = [
        mock.call("Received file with extension: parquet"),
        mock.call("Loading file using PARQUET loader"),
        mock.call("Loading Parquet file")
    ]
    assert mock_logger.info.call_args_list == expected_calls