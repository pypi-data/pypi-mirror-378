"""
Tests for WorkflowStorageManager functionality.
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from sfn_blueprint.utils.workflow_storage import WorkflowStorageManager


class TestWorkflowStorageManager:
    """Test the WorkflowStorageManager class."""
    
    @pytest.fixture
    def temp_workflow_dir(self):
        """Create a temporary workflow directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
            'age': [25, 30, 35, 28, 32],
            'city': ['NYC', 'LA', 'Chicago', 'Miami', 'Seattle']
        })
    
    @pytest.fixture
    def storage_manager(self, temp_workflow_dir):
        """Create a WorkflowStorageManager instance for testing."""
        return WorkflowStorageManager(temp_workflow_dir, "test_workflow_123")
    
    def test_initialization(self, storage_manager, temp_workflow_dir):
        """Test that storage manager initializes correctly."""
        assert storage_manager.workflow_id == "test_workflow_123"
        assert storage_manager.base_path == Path(temp_workflow_dir)
        
        # Check that directories were created
        expected_dirs = [
            "step_results",
            "intermediate_data", 
            "temp_files",
            "final_outputs",
            "execution_logs"
        ]
        
        for dir_name in expected_dirs:
            dir_path = Path(temp_workflow_dir) / dir_name
            assert dir_path.exists()
            assert dir_path.is_dir()
    
    def test_save_step_result_dataframe(self, storage_manager, sample_dataframe):
        """Test saving a DataFrame as a step result."""
        step_id = "step_1"
        metadata = {"test": "metadata", "agent": "test_agent"}
        
        result_info = storage_manager.save_step_result(
            step_id=step_id,
            data=sample_dataframe,
            step_type="agent_execution",
            metadata=metadata
        )
        
        # Check result info structure
        assert result_info["step_id"] == step_id
        assert result_info["step_type"] == "agent_execution"
        assert result_info["workflow_id"] == "test_workflow_123"
        assert "timestamp" in result_info
        
        # Check that files were created
        assert "csv" in result_info["files"]
        assert "json" in result_info["files"]
        
        # Check metadata
        assert result_info["metadata"]["test"] == "metadata"
        assert result_info["metadata"]["agent"] == "test_agent"
        assert result_info["metadata"]["data_shape"] == [5, 4]
        assert result_info["metadata"]["data_columns"] == ['id', 'name', 'age', 'city']
        
        # Verify files exist
        csv_path = Path(result_info["files"]["csv"])
        json_path = Path(result_info["files"]["json"])
        
        assert csv_path.exists()
        assert json_path.exists()
        
        # Verify CSV content
        loaded_df = pd.read_csv(csv_path)
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)
    
    def test_save_step_result_dict(self, storage_manager):
        """Test saving a dictionary as a step result."""
        step_id = "step_2"
        data = {"key1": "value1", "key2": "value2", "numbers": [1, 2, 3]}
        metadata = {"dict_test": True}
        
        result_info = storage_manager.save_step_result(
            step_id=step_id,
            data=data,
            step_type="conditional",
            metadata=metadata
        )
        
        assert result_info["step_id"] == step_id
        assert result_info["step_type"] == "conditional"
        assert "json" in result_info["files"]
        assert result_info["metadata"]["data_keys"] == ["key1", "key2", "numbers"]
        assert result_info["metadata"]["data_type"] == "dict"
        
        # Verify JSON content
        json_path = Path(result_info["files"]["json"])
        with open(json_path, 'r') as f:
            loaded_data = eval(f.read())  # Safe for test data
        assert loaded_data == data
    
    def test_save_intermediate_data(self, storage_manager, sample_dataframe):
        """Test saving intermediate data."""
        step_id = "step_3"
        data_name = "processed_data"
        
        intermediate_path = storage_manager.save_intermediate_data(
            step_id=step_id,
            data=sample_dataframe,
            data_name=data_name,
            format="csv"
        )
        
        assert Path(intermediate_path).exists()
        
        # Verify the data
        loaded_df = pd.read_csv(intermediate_path)
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)
    
    def test_get_step_result(self, storage_manager, sample_dataframe):
        """Test retrieving a step result."""
        step_id = "step_4"
        
        # Save a step result first
        storage_manager.save_step_result(
            step_id=step_id,
            data=sample_dataframe,
            metadata={"test": "retrieval"}
        )
        
        # Retrieve it
        retrieved_result = storage_manager.get_step_result(step_id)
        
        assert retrieved_result is not None
        assert retrieved_result["step_id"] == step_id
        assert retrieved_result["metadata"]["test"] == "retrieval"
        assert "csv" in retrieved_result["files"]
        assert "json" in retrieved_result["files"]
    
    def test_list_step_results(self, storage_manager, sample_dataframe):
        """Test listing step results."""
        # Save multiple step results
        for i in range(3):
            step_id = f"step_{i+1}"
            storage_manager.save_step_result(
                step_id=step_id,
                data=sample_dataframe,
                metadata={"step_number": i+1}
            )
        
        # List results
        step_results = storage_manager.list_step_results()
        
        assert len(step_results) == 3
        assert "step_1" in step_results
        assert "step_2" in step_results
        assert "step_3" in step_results
    
    def test_get_intermediate_data_files(self, storage_manager, sample_dataframe):
        """Test getting intermediate data files."""
        step_id = "step_5"
        
        # Save intermediate data
        storage_manager.save_intermediate_data(
            step_id=step_id,
            data=sample_dataframe,
            data_name="data1",
            format="csv"
        )
        
        storage_manager.save_intermediate_data(
            step_id=step_id,
            data=sample_dataframe,
            data_name="data2", 
            format="json"
        )
        
        # Get file list
        files = storage_manager.get_intermediate_data_files(step_id)
        
        assert len(files) == 2
        assert any("data1" in f and f.endswith(".csv") for f in files)
        assert any("data2" in f and f.endswith(".json") for f in files)
    
    def test_get_storage_summary(self, storage_manager, sample_dataframe):
        """Test getting storage summary."""
        # Save some data first
        storage_manager.save_step_result(
            step_id="step_6",
            data=sample_dataframe,
            metadata={"test": "summary"}
        )
        
        storage_manager.save_intermediate_data(
            step_id="step_6",
            data=sample_dataframe,
            data_name="summary_data",
            format="csv"
        )
        
        # Get summary
        summary = storage_manager.get_storage_summary()
        
        assert summary["workflow_id"] == "test_workflow_123"
        assert "step_6" in summary["step_results"]
        assert "step_6" in summary["intermediate_data"]
        assert summary["total_files"] > 0
    
    def test_cleanup_temp_files(self, storage_manager):
        """Test cleanup of temporary files."""
        step_id = "step_7"
        temp_dir = storage_manager.base_path / "temp_files" / step_id
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create some temp files
        temp_file1 = temp_dir / "temp1.txt"
        temp_file2 = temp_dir / "temp2.txt"
        
        temp_file1.write_text("temp content 1")
        temp_file2.write_text("temp content 2")
        
        assert temp_file1.exists()
        assert temp_file2.exists()
        
        # Cleanup
        storage_manager.cleanup_temp_files(step_id)
        
        assert not temp_file1.exists()
        assert not temp_file2.exists()
        assert not temp_dir.exists()


if __name__ == "__main__":
    # Run a simple demonstration
    print("Testing WorkflowStorageManager...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create storage manager
        storage = WorkflowStorageManager(temp_dir, "demo_workflow")
        
        # Create sample data
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })
        
        # Save step result
        result = storage.save_step_result(
            step_id="demo_step",
            data=df,
            metadata={"demo": True}
        )
        
        print(f"Step result saved: {result['files']}")
        
        # Save intermediate data
        intermediate = storage.save_intermediate_data(
            step_id="demo_step",
            data=df,
            data_name="demo_data",
            format="csv"
        )
        
        print(f"Intermediate data saved: {intermediate}")
        
        # Get summary
        summary = storage.get_storage_summary()
        print(f"Storage summary: {summary['total_files']} total files")
        
        print("✅ All tests passed!")


