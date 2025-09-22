import pytest
import pandas as pd
from sfn_blueprint.agents.code_generator import SFNFeatureCodeGeneratorAgent

class TestSFNFeatureCodeGeneratorAgent:
    @pytest.fixture
    def feature_code_generator(self):
        """Fixture to create a SFNFeatureCodeGeneratorAgent instance"""
        return SFNFeatureCodeGeneratorAgent(llm_provider='anthropic')

    @pytest.mark.parametrize("llm_provider", ['anthropic', 'openai', 'cortex'])
    def test_initialization(self, llm_provider):
        """Test agent initialization with different LLM providers"""
        agent = SFNFeatureCodeGeneratorAgent(llm_provider=llm_provider)
        assert agent is not None
        assert agent.llm_provider == llm_provider

    def test_numerical_feature_engineering(self, feature_code_generator):
        """Test generating code for numerical feature engineering"""
        task_data = {
            'suggestion': 'Calculate the moving average of the price column with a window of 3',
            'columns': ['price', 'date'],
            'dtypes': {'price': 'float64', 'date': 'datetime64'},
            'sample_records': [
                {'price': 100.0, 'date': '2023-01-01'},
                {'price': 110.0, 'date': '2023-01-02'},
                {'price': 105.0, 'date': '2023-01-03'}
            ]
        }
        
        class MockTask:
            def __init__(self, data):
                self.data = data
        
        mock_task = MockTask(task_data)
        
        # Generate feature engineering code
        generated_code = feature_code_generator.execute_task(mock_task)
        
        # Create a sample DataFrame for testing
        df = pd.DataFrame(task_data['sample_records'])
        
        # Execute the generated code
        exec(generated_code)
        
        # Assertions
        assert 'price_moving_avg' in df.columns
        assert len(df) == 3

    def test_categorical_feature_engineering(self, feature_code_generator):
        """Test generating code for categorical feature engineering"""
        task_data = {
            'suggestion': 'Perform one-hot encoding on the category column',
            'columns': ['category', 'sales'],
            'dtypes': {'category': 'object', 'sales': 'float64'},
            'sample_records': [
                {'category': 'A', 'sales': 100.0},
                {'category': 'B', 'sales': 200.0},
                {'category': 'A', 'sales': 150.0}
            ]
        }
        
        class MockTask:
            def __init__(self, data):
                self.data = data
        
        mock_task = MockTask(task_data)
        
        # Generate feature engineering code
        generated_code = feature_code_generator.execute_task(mock_task)
        
        # Create a sample DataFrame for testing
        df = pd.DataFrame(task_data['sample_records'])
        
        # Execute the generated code
        exec(generated_code)
        
        # Assertions
        assert 'category_A' in df.columns
        assert 'category_B' in df.columns
        assert len(df) == 3

    def test_date_feature_engineering(self, feature_code_generator):
        """Test generating code for date-based feature engineering"""
        task_data = {
            'suggestion': 'Extract month and year from the date column',
            'columns': ['date', 'revenue'],
            'dtypes': {'date': 'datetime64', 'revenue': 'float64'},
            'sample_records': [
                {'date': '2023-01-15', 'revenue': 1000.0},
                {'date': '2023-02-20', 'revenue': 1500.0},
                {'date': '2023-03-10', 'revenue': 1200.0}
            ]
        }
        
        class MockTask:
            def __init__(self, data):
                self.data = data
        
        mock_task = MockTask(task_data)
        
        # Generate feature engineering code
        generated_code = feature_code_generator.execute_task(mock_task)
        
        # Create a sample DataFrame for testing
        df = pd.DataFrame(task_data['sample_records'])
        df['date'] = pd.to_datetime(df['date'])
        
        # Execute the generated code
        exec(generated_code)
        
        # Assertions
        assert 'date_month' in df.columns
        assert 'date_year' in df.columns
        assert len(df) == 3

    def test_error_handling(self, feature_code_generator):
        """Test error handling for invalid input"""
        task_data = {
            'suggestion': 'Invalid feature engineering suggestion',
            'columns': [],
            'dtypes': {},
            'sample_records': []
        }
        
        class MockTask:
            def __init__(self, data):
                self.data = data
        
        mock_task = MockTask(task_data)
        
        # Expect an exception or handled error
        with pytest.raises((ValueError, Exception)):
            feature_code_generator.execute_task(mock_task)

    def test_clean_generated_code(self):
        """Test the code cleaning method"""
        sample_code_with_artifacts = '''
                ```python
                # Some comment
                print("Debug")
                df['new_feature'] = df['existing_feature'] * 2
                print(df.head())
                ```'''
        
        cleaned_code = SFNFeatureCodeGeneratorAgent.clean_generated_code(sample_code_with_artifacts)
        
        # Assertions
        assert '```' not in cleaned_code
        assert 'print(' not in cleaned_code
        assert '#' not in cleaned_code
        assert 'df[\'new_feature\'] = df[\'existing_feature\'] * 2' in cleaned_code