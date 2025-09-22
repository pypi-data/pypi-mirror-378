#!/usr/bin/env python3
"""
Demonstration of WorkflowStorageManager for agents.

This script shows how agents can use the new workflow storage functionality
to save their intermediate results in workflow-specific directories.
"""

import pandas as pd
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the parent directory to the path so we can import sfn_blueprint
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfn_blueprint import WorkflowStorageManager


def demonstrate_cleaning_agent_storage():
    """Demonstrate how a cleaning agent would use workflow storage."""
    print("🧹 CLEANING AGENT WORKFLOW STORAGE DEMO")
    print("=" * 50)
    
    # Create temporary workflow directory
    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_id = "healthcare_workflow_123"
        storage_manager = WorkflowStorageManager(temp_dir, workflow_id)
        
        print(f"📁 Created workflow storage at: {temp_dir}")
        print(f"🆔 Workflow ID: {workflow_id}")
        
        # Simulate cleaning agent processing
        print("\n📊 Processing patient data...")
        
        # Create sample patient data (like what cleaning agent would process)
        patient_data = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'name': ['John Smith', 'Mary Johnson', 'Bob Wilson', 'Alice Brown', 'Charlie Davis'],
            'age': [45, 32, 58, 29, 41],
            'diagnosis': ['Hypertension', 'Diabetes', 'Heart Disease', 'Asthma', 'Hypertension'],
            'admission_date': ['2024-01-15', '2024-01-20', '2024-02-05', '2024-02-10', '2024-02-15'],
            'discharge_date': ['2024-01-18', '2024-01-23', '2024-02-08', '2024-02-13', '2024-02-18'],
            'readmission_risk': ['High', 'Medium', 'High', 'Low', 'Medium']
        })
        
        print(f"   📈 Original data shape: {patient_data.shape}")
        
        # Simulate cleaning operations
        print("   🧹 Cleaning data...")
        
        # Remove duplicates
        cleaned_data = patient_data.drop_duplicates()
        
        # Handle missing values
        cleaned_data = cleaned_data.fillna('Unknown')
        
        # Standardize dates
        cleaned_data['admission_date'] = pd.to_datetime(cleaned_data['admission_date'])
        cleaned_data['discharge_date'] = pd.to_datetime(cleaned_data['discharge_date'])
        
        # Calculate length of stay
        cleaned_data['length_of_stay'] = (
            cleaned_data['discharge_date'] - cleaned_data['admission_date']
        ).dt.days
        
        print(f"   ✅ Cleaned data shape: {cleaned_data.shape}")
        
        # Save cleaning result to workflow storage
        print("\n💾 Saving cleaning result to workflow storage...")
        
        cleaning_report = {
            "data_summary": {
                "original_shape": patient_data.shape.tolist(),
                "cleaned_shape": cleaned_data.shape.tolist(),
                "rows_removed": len(patient_data) - len(cleaned_data),
                "columns_added": ["length_of_stay"]
            },
            "cleaning_operations": [
                "removed_duplicates",
                "filled_missing_values", 
                "standardized_dates",
                "calculated_length_of_stay"
            ],
            "execution_time": 2.5,
            "data_quality_score": 0.95
        }
        
        # Save as step result
        step_result = storage_manager.save_step_result(
            step_id="cleaning_step_1",
            data=cleaned_data,
            step_type="agent_execution",
            metadata={
                "agent_type": "cleaning_agent",
                "cleaning_report": cleaning_report,
                "input_file": "patients.csv",
                "output_description": "Cleaned patient data with length of stay calculation"
            }
        )
        
        print(f"   📁 Step result saved: {list(step_result['files'].keys())}")
        
        # Save as intermediate data for easy access
        intermediate_path = storage_manager.save_intermediate_data(
            step_id="cleaning_step_1",
            data=cleaned_data,
            data_name="cleaned_patients",
            format="csv"
        )
        
        print(f"   📊 Intermediate data saved: {Path(intermediate_path).name}")
        
        # Demonstrate retrieval
        print("\n🔍 Retrieving step result...")
        retrieved_result = storage_manager.get_step_result("cleaning_step_1")
        
        if retrieved_result:
            print(f"   ✅ Retrieved result for: {retrieved_result['step_id']}")
            print(f"   📊 Data shape: {retrieved_result['metadata']['data_shape']}")
            print(f"   🧹 Operations: {len(retrieved_result['metadata']['cleaning_operations'])}")
        
        # Show storage summary
        print("\n📋 Storage Summary:")
        summary = storage_manager.get_storage_summary()
        print(f"   📁 Total files: {summary['total_files']}")
        print(f"   🔧 Steps with results: {list(summary['step_results'].keys())}")
        print(f"   📊 Intermediate data: {list(summary['intermediate_data'].keys())}")
        
        print("\n✅ Cleaning agent workflow storage demo completed!")


def demonstrate_mapping_agent_storage():
    """Demonstrate how a mapping agent would use workflow storage."""
    print("\n🗺️  MAPPING AGENT WORKFLOW STORAGE DEMO")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_id = "healthcare_workflow_123"
        storage_manager = WorkflowStorageManager(temp_dir, workflow_id)
        
        print(f"📁 Using workflow storage at: {temp_dir}")
        
        # Simulate mapping agent processing
        print("\n📊 Mapping patient data to domain schema...")
        
        # Create mapped data (like what mapping agent would produce)
        mapped_data = pd.DataFrame({
            'patient_id': ['P001', 'P002', 'P003', 'P004', 'P005'],
            'full_name': ['John Smith', 'Mary Johnson', 'Bob Wilson', 'Alice Brown', 'Charlie Davis'],
            'age_years': [45, 32, 58, 29, 41],
            'primary_diagnosis': ['Hypertension', 'Diabetes', 'Heart Disease', 'Asthma', 'Hypertension'],
            'admission_timestamp': ['2024-01-15 10:00:00', '2024-01-20 14:30:00', '2024-02-05 09:15:00', '2024-02-10 16:45:00', '2024-02-15 11:20:00'],
            'discharge_timestamp': ['2024-01-18 15:00:00', '2024-01-23 12:30:00', '2024-02-08 17:15:00', '2024-02-13 14:45:00', '2024-02-18 13:20:00'],
            'readmission_risk_level': ['HIGH', 'MEDIUM', 'HIGH', 'LOW', 'MEDIUM'],
            'length_of_stay_days': [3, 3, 3, 3, 3]
        })
        
        print(f"   📈 Mapped data shape: {mapped_data.shape}")
        
        # Save mapping result
        print("\n💾 Saving mapping result to workflow storage...")
        
        mapping_report = {
            "mapping_summary": {
                "original_columns": ['patient_id', 'name', 'age', 'diagnosis', 'admission_date', 'discharge_date', 'readmission_risk'],
                "mapped_columns": ['patient_id', 'full_name', 'age_years', 'primary_diagnosis', 'admission_timestamp', 'discharge_timestamp', 'readmission_risk_level', 'length_of_stay_days'],
                "columns_mapped": 7,
                "columns_added": 1,
                "data_type_conversions": 3
            },
            "mapping_rules": [
                "name -> full_name (standardized)",
                "age -> age_years (clarified unit)",
                "diagnosis -> primary_diagnosis (domain terminology)",
                "admission_date -> admission_timestamp (ISO format)",
                "discharge_date -> discharge_timestamp (ISO format)",
                "readmission_risk -> readmission_risk_level (standardized values)",
                "length_of_stay -> length_of_stay_days (calculated field)"
            ],
            "execution_time": 1.8,
            "mapping_confidence": 0.98
        }
        
        step_result = storage_manager.save_step_result(
            step_id="mapping_step_1",
            data=mapped_data,
            step_type="agent_execution",
            metadata={
                "agent_type": "mapping_agent",
                "mapping_report": mapping_report,
                "input_step": "cleaning_step_1",
                "output_description": "Mapped patient data conforming to healthcare domain schema"
            }
        )
        
        print(f"   📁 Step result saved: {list(step_result['files'].keys())}")
        
        # Save as intermediate data
        intermediate_path = storage_manager.save_intermediate_data(
            step_id="mapping_step_1",
            data=mapped_data,
            data_name="mapped_patients",
            format="csv"
        )
        
        print(f"   📊 Intermediate data saved: {Path(intermediate_path).name}")
        
        print("\n✅ Mapping agent workflow storage demo completed!")


def demonstrate_storage_retrieval():
    """Demonstrate how to retrieve and analyze stored workflow data."""
    print("\n🔍 WORKFLOW STORAGE RETRIEVAL DEMO")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        workflow_id = "healthcare_workflow_123"
        storage_manager = WorkflowStorageManager(temp_dir, workflow_id)
        
        # Create some sample data first
        sample_data = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [100, 200, 300]
        })
        
        # Save multiple step results
        for i in range(3):
            step_id = f"demo_step_{i+1}"
            storage_manager.save_step_result(
                step_id=step_id,
                data=sample_data,
                metadata={"step_number": i+1, "demo": True}
            )
        
        print(f"📁 Created {len(storage_manager.list_step_results())} demo steps")
        
        # Show all step results
        print("\n📋 Available step results:")
        for step_id in storage_manager.list_step_results():
            result = storage_manager.get_step_result(step_id)
            if result:
                print(f"   🔧 {step_id}: {result['metadata']['step_number']} files")
        
        # Show storage summary
        print("\n📊 Storage Summary:")
        summary = storage_manager.get_storage_summary()
        print(f"   📁 Total files: {summary['total_files']}")
        print(f"   🔧 Steps: {list(summary['step_results'].keys())}")
        
        print("\n✅ Storage retrieval demo completed!")


def main():
    """Run all demonstrations."""
    print("🚀 WORKFLOW STORAGE MANAGER DEMONSTRATION")
    print("=" * 60)
    print("This demo shows how agents can use the new WorkflowStorageManager")
    print("to save their intermediate results in workflow-specific directories.")
    print("=" * 60)
    
    try:
        # Run demonstrations
        demonstrate_cleaning_agent_storage()
        demonstrate_mapping_agent_storage()
        demonstrate_storage_retrieval()
        
        print("\n🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("\n💡 Key Benefits:")
        print("   ✅ Agents can save intermediate results to workflow storage")
        print("   ✅ Results are organized by step and easily retrievable")
        print("   ✅ Multiple formats supported (CSV, JSON, Excel, Parquet)")
        print("   ✅ Rich metadata tracking for debugging and lineage")
        print("   ✅ Future-ready for warehouse integration (PostgreSQL, Snowflake)")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


