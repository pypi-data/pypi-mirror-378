import pytest
import pandas as pd
import sqlite3
from io import BytesIO
from sfn_blueprint import SFNDataPostProcessor


@pytest.fixture
def sample_data():
    """Sample DataFrame for testing purposes."""
    return pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [6, 7, 8, 9, 10],
        'C': ['x', 'y', 'z', 'a', 'b']
    })


@pytest.fixture
def post_processor(sample_data):
    """Returns an instance of SFNDataPostProcessor."""
    return SFNDataPostProcessor(sample_data)


def test_view_data(post_processor, sample_data):
    """Test the view_data method."""
    result = post_processor.view_data(num_rows=3)
    assert len(result) == 3
    pd.testing.assert_frame_equal(result, sample_data.head(3))


def test_download_data_csv(post_processor):
    """Test downloading data as CSV."""
    csv_data = post_processor.download_data(file_format='csv')
    expected_csv = post_processor.data.to_csv(index=False).encode('utf-8')
    assert csv_data == expected_csv


def test_download_data_excel(post_processor):
    """Test downloading data as Excel."""
    # Instead of checking the exact content, we can validate the output type.
    excel_data = post_processor.download_data(file_format='excel', file_name='test_data')
    assert isinstance(excel_data, BytesIO)  # Check if the returned object is BytesIO


def test_download_data_unsupported_format(post_processor):
    """Test that unsupported formats raise an error."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        post_processor.download_data(file_format='txt')


def test_summarize_data(post_processor, sample_data):
    """Test the summarize_data method."""
    summary = post_processor.summarize_data()
    pd.testing.assert_frame_equal(summary, sample_data.describe())


def test_reset_data(post_processor, sample_data):
    """Test the reset_data method."""
    modified_data = sample_data.copy()
    modified_data['A'] = modified_data['A'] * 2
    post_processor.reset_data(original_data=sample_data)
    pd.testing.assert_frame_equal(post_processor.data, sample_data)


def test_export_to_database(post_processor, sample_data):
    """Test exporting data to a SQLite database."""
    connection = sqlite3.connect(":memory:")
    table_name = "test_table"
    
    result = post_processor.export_to_database(connection, table_name)
    assert result == f"Data exported to {table_name} table in the database."

    # Check if data was written to the database
    query_result = pd.read_sql(f"SELECT * FROM {table_name}", connection)
    pd.testing.assert_frame_equal(query_result, sample_data)
    connection.close()
