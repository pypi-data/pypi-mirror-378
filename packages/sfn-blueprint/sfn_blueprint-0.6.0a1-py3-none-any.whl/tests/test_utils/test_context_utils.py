"""
Test cases for context utilities module.
"""

import pytest
import json
from unittest.mock import Mock, patch
import logging

# Import the context utilities
from sfn_blueprint.utils.context_utils import (
    ContextInfo, ContextRecommendations, ContextAnalyzer,
    extract_context_info, get_context_recommendations,
    validate_context, log_context_usage
)


class TestContextInfo:
    """Test the ContextInfo dataclass."""
    
    def test_context_info_creation(self):
        """Test creating a ContextInfo instance."""
        context = ContextInfo(
            domain="healthcare",
            business_context={"compliance": "HIPAA"},
            workflow_goal="Test goal",
            data_sensitivity="high",
            compliance_requirements=["HIPAA"],
            optimization_hints=["performance"],
            risk_factors=["privacy"],
            data_files=["test.csv"],
            constraints={"privacy": "high"},
            stakeholders=["doctors"],
            workflow_complexity="complex",
            risk_level="high",
            current_step={"step_id": "step_1"},
            execution_progress={"completed": 0}
        )
        
        assert context.domain == "healthcare"
        assert context.workflow_goal == "Test goal"
        assert context.data_sensitivity == "high"
        assert "HIPAA" in context.compliance_requirements


class TestContextRecommendations:
    """Test the ContextRecommendations dataclass."""
    
    def test_context_recommendations_creation(self):
        """Test creating a ContextRecommendations instance."""
        recommendations = ContextRecommendations(
            data_processing=["Process data securely"],
            quality_checks=["Validate data integrity"],
            optimization_strategies=["Use parallel processing"],
            risk_mitigation=["Apply encryption"],
            compliance_measures=["Follow HIPAA guidelines"],
            performance_tuning=["Optimize memory usage"]
        )
        
        assert len(recommendations.data_processing) == 1
        assert len(recommendations.compliance_measures) == 1
        assert "Process data securely" in recommendations.data_processing


class TestContextAnalyzer:
    """Test the ContextAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = ContextAnalyzer()
        self.sample_task_data = {
            'enriched_context': {
                'domain_knowledge': {
                    'domain': 'healthcare',
                    'business_context': {
                        'compliance': 'HIPAA',
                        'data_sensitivity': 'high',
                        'industry': 'medical'
                    },
                    'data_files': ['patients.csv', 'medical_records.csv'],
                    'constraints': {'privacy': 'high', 'security': 'critical'},
                    'stakeholders': ['doctors', 'nurses', 'administrators']
                },
                'workflow_context': {
                    'goal': 'Analyze patient data for treatment optimization',
                    'complexity': 'complex',
                    'risk_level': 'high',
                    'optimization_requirements': ['performance', 'accuracy']
                },
                'execution_context': {
                    'current_step': {
                        'step_id': 'step_1',
                        'agent_name': 'cleaning_agent'
                    },
                    'execution_progress': {
                        'completed_steps': [],
                        'current_step_number': 1
                    }
                }
            }
        }
    
    def test_extract_context_info_success(self):
        """Test successful context extraction."""
        context_info = self.analyzer.extract_context_info(self.sample_task_data)
        
        assert context_info is not None
        assert context_info.domain == 'healthcare'
        assert context_info.workflow_goal == 'Analyze patient data for treatment optimization'
        assert context_info.data_sensitivity == 'high'
        assert 'HIPAA' in context_info.compliance_requirements
        assert context_info.workflow_complexity == 'complex'
        assert context_info.risk_level == 'high'
    
    def test_extract_context_info_no_enriched_context(self):
        """Test context extraction when no enriched_context is present."""
        task_data = {'some_other_data': 'value'}
        context_info = self.analyzer.extract_context_info(task_data)
        
        assert context_info is None
    
    def test_extract_context_info_missing_fields(self):
        """Test context extraction with missing optional fields."""
        minimal_task_data = {
            'enriched_context': {
                'domain_knowledge': {
                    'domain': 'retail'
                },
                'workflow_context': {
                    'goal': 'Basic goal'
                },
                'execution_context': {}
            }
        }
        
        context_info = self.analyzer.extract_context_info(minimal_task_data)
        
        assert context_info is not None
        assert context_info.domain == 'retail'
        assert context_info.workflow_goal == 'Basic goal'
        assert context_info.data_sensitivity == 'medium'  # default value
        assert context_info.workflow_complexity == 'moderate'  # default value
    
    @patch('sfn_blueprint.utils.context_utils.SFNAIHandler')
    @patch('sfn_blueprint.utils.context_utils.SFNPromptManager')
    def test_get_context_aware_recommendations_ai_powered(self, mock_prompt_manager, mock_ai_handler):
        """Test AI-powered recommendations generation."""
        # Mock the AI handler response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "data_processing": ["Apply healthcare-specific data cleaning"],
            "quality_checks": ["Validate HIPAA compliance"],
            "optimization_strategies": ["Use parallel processing"],
            "risk_mitigation": ["Implement audit trails"],
            "compliance_measures": ["Follow HIPAA guidelines"],
            "performance_tuning": ["Optimize memory usage"]
        })
        
        mock_ai_handler_instance = Mock()
        mock_ai_handler_instance.route_to.return_value = mock_response
        mock_ai_handler.return_value = mock_ai_handler_instance
        
        # Mock the prompt manager
        mock_prompt_manager_instance = Mock()
        mock_prompt_manager_instance.prompts_config = {
            'context_analyzer': {
                'openai': {
                    'main': {
                        'system_prompt': 'Test system prompt',
                        'user_prompt_template': 'Test user prompt'
                    }
                }
            }
        }
        mock_prompt_manager.return_value = mock_prompt_manager_instance
        
        context_info = self.analyzer.extract_context_info(self.sample_task_data)
        recommendations = self.analyzer.get_context_aware_recommendations(context_info, 'cleaning_agent')
        
        # Check that AI was called
        mock_ai_handler_instance.route_to.assert_called_once()
        
        # Check recommendations were generated
        assert len(recommendations.data_processing) > 0
        assert len(recommendations.compliance_measures) > 0
        assert "Apply healthcare-specific data cleaning" in recommendations.data_processing
        assert "Follow HIPAA guidelines" in recommendations.compliance_measures
    
    @patch('sfn_blueprint.utils.context_utils.SFNAIHandler')
    @patch('sfn_blueprint.utils.context_utils.SFNPromptManager')
    def test_get_context_aware_recommendations_finance(self, mock_prompt_manager, mock_ai_handler):
        """Test finance-specific recommendations with AI."""
        # Mock the AI handler response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "data_processing": ["Apply financial data security measures"],
            "quality_checks": ["Validate PCI DSS compliance"],
            "optimization_strategies": ["Use financial-grade encryption"],
            "risk_mitigation": ["Implement fraud detection"],
            "compliance_measures": ["Follow PCI DSS guidelines"],
            "performance_tuning": ["Optimize for real-time processing"]
        })
        
        mock_ai_handler_instance = Mock()
        mock_ai_handler_instance.route_to.return_value = mock_response
        mock_ai_handler.return_value = mock_ai_handler_instance
        
        # Mock the prompt manager
        mock_prompt_manager_instance = Mock()
        mock_prompt_manager_instance.prompts_config = {
            'context_analyzer': {
                'openai': {
                    'main': {
                        'system_prompt': 'Test system prompt',
                        'user_prompt_template': 'Test user prompt'
                    }
                }
            }
        }
        mock_prompt_manager.return_value = mock_prompt_manager_instance
        
        finance_task_data = {
            'enriched_context': {
                'domain_knowledge': {
                    'domain': 'finance',
                    'business_context': {
                        'compliance': 'PCI DSS',
                        'data_sensitivity': 'high'
                    },
                    'data_files': [],
                    'constraints': {},
                    'stakeholders': []
                },
                'workflow_context': {
                    'goal': 'Financial analysis',
                    'complexity': 'moderate',
                    'risk_level': 'medium'
                },
                'execution_context': {
                    'current_step': {},
                    'execution_progress': {}
                }
            }
        }
        
        context_info = self.analyzer.extract_context_info(finance_task_data)
        recommendations = self.analyzer.get_context_aware_recommendations(context_info, 'model_selection_agent')
        
        # Check that AI was called
        mock_ai_handler_instance.route_to.assert_called_once()
        
        # Check finance-specific recommendations
        assert len(recommendations.compliance_measures) > 0
        assert "Follow PCI DSS guidelines" in recommendations.compliance_measures
    
    def test_error_when_no_supported_providers(self):
        """Test that error is thrown when no supported LLM providers are available."""
        with patch('sfn_blueprint.utils.context_utils.SFN_SUPPORTED_LLM_PROVIDERS', ['openai', 'anthropic']):
            # Mock the prompt manager with no supported providers
            with patch('sfn_blueprint.utils.context_utils.SFNPromptManager') as mock_prompt_manager:
                mock_prompt_manager_instance = Mock()
                mock_prompt_manager_instance.prompts_config = {
                    'context_analyzer': {
                        'unsupported_provider': {
                            'main': {
                                'system_prompt': 'Test system prompt',
                                'user_prompt_template': 'Test user prompt'
                            }
                        }
                    }
                }
                mock_prompt_manager.return_value = mock_prompt_manager_instance
                
                context_info = self.analyzer.extract_context_info(self.sample_task_data)
                
                # Check that error is thrown instead of fallback
                with pytest.raises(ValueError) as exc_info:
                    self.analyzer.get_context_aware_recommendations(context_info, 'cleaning_agent')
                
                assert "No supported LLM providers found" in str(exc_info.value)
    
    @patch('sfn_blueprint.utils.context_utils.SFNAIHandler')
    @patch('sfn_blueprint.utils.context_utils.SFNPromptManager')
    def test_get_context_aware_recommendations_retail(self, mock_prompt_manager, mock_ai_handler):
        """Test retail-specific recommendations with AI."""
        # Mock the AI handler response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "data_processing": ["Apply customer-focused data processing"],
            "quality_checks": ["Validate customer data integrity"],
            "optimization_strategies": ["Focus on customer experience optimization"],
            "risk_mitigation": ["Implement customer privacy protection"],
            "compliance_measures": ["Follow retail industry standards"],
            "performance_tuning": ["Optimize for real-time processing"]
        })
        
        mock_ai_handler_instance = Mock()
        mock_ai_handler_instance.route_to.return_value = mock_response
        mock_ai_handler.return_value = mock_ai_handler_instance
        
        # Mock the prompt manager
        mock_prompt_manager_instance = Mock()
        mock_prompt_manager_instance.prompts_config = {
            'context_analyzer': {
                'openai': {
                    'main': {
                        'system_prompt': 'Test system prompt',
                        'user_prompt_template': 'Test user prompt'
                    }
                }
            }
        }
        mock_prompt_manager.return_value = mock_prompt_manager_instance
        
        retail_task_data = {
            'enriched_context': {
                'domain_knowledge': {
                    'domain': 'retail',
                    'business_context': {},
                    'data_files': [],
                    'constraints': {},
                    'stakeholders': []
                },
                'workflow_context': {
                    'goal': 'Customer analysis',
                    'complexity': 'simple',
                    'risk_level': 'low'
                },
                'execution_context': {
                    'current_step': {},
                    'execution_progress': {}
                }
            }
        }
        
        context_info = self.analyzer.extract_context_info(retail_task_data)
        recommendations = self.analyzer.get_context_aware_recommendations(context_info, 'split_execution_agent')
        
        # Check that AI was called
        mock_ai_handler_instance.route_to.assert_called_once()
        
        # Check retail-specific recommendations
        assert len(recommendations.optimization_strategies) > 0
        assert "Focus on customer experience optimization" in recommendations.optimization_strategies
    
    def test_config_based_llm_provider_selection(self):
        """Test that LLM provider selection uses config instead of hardcoded values."""
        with patch('sfn_blueprint.utils.context_utils.SFN_SUPPORTED_LLM_PROVIDERS', ['openai', 'anthropic']):
                # Mock the AI handler response
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = json.dumps({
                    "data_processing": ["Test recommendation"],
                    "quality_checks": [],
                    "optimization_strategies": [],
                    "risk_mitigation": [],
                    "compliance_measures": [],
                    "performance_tuning": []
                })
                
                with patch('sfn_blueprint.utils.context_utils.SFNAIHandler') as mock_ai_handler:
                    mock_ai_handler_instance = Mock()
                    mock_ai_handler_instance.route_to.return_value = mock_response
                    mock_ai_handler.return_value = mock_ai_handler_instance
                    
                    # Mock the prompt manager with only anthropic available
                    with patch('sfn_blueprint.utils.context_utils.SFNPromptManager') as mock_prompt_manager:
                        mock_prompt_manager_instance = Mock()
                        mock_prompt_manager_instance.prompts_config = {
                            'context_analyzer': {
                                'anthropic': {
                                    'main': {
                                        'system_prompt': 'Test system prompt',
                                        'user_prompt_template': 'Test user prompt'
                                    }
                                }
                            }
                        }
                        mock_prompt_manager.return_value = mock_prompt_manager_instance
                        
                        context_info = self.analyzer.extract_context_info(self.sample_task_data)
                        recommendations = self.analyzer.get_context_aware_recommendations(context_info, 'cleaning_agent')
                        
                        # Check that AI was called with anthropic provider (not hardcoded openai)
                        mock_ai_handler_instance.route_to.assert_called_once()
                        call_args = mock_ai_handler_instance.route_to.call_args
                        assert call_args[1]['llm_provider'] == 'anthropic'
                        
                        # Check recommendations were generated
                        assert len(recommendations.data_processing) > 0
    
    def test_generic_configuration_no_hardcoded_values(self):
        """Test that configuration is generic with no hardcoded values."""
        with patch('sfn_blueprint.utils.context_utils.SFN_SUPPORTED_LLM_PROVIDERS', ['openai', 'anthropic']):
                # Mock the AI handler response
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = json.dumps({
                    "data_processing": ["Test recommendation"],
                    "quality_checks": [],
                    "optimization_strategies": [],
                    "risk_mitigation": [],
                    "compliance_measures": [],
                    "performance_tuning": []
                })
                
                with patch('sfn_blueprint.utils.context_utils.SFNAIHandler') as mock_ai_handler:
                    mock_ai_handler_instance = Mock()
                    mock_ai_handler_instance.route_to.return_value = mock_response
                    mock_ai_handler.return_value = mock_ai_handler_instance
                    
                    # Mock the prompt manager
                    with patch('sfn_blueprint.utils.context_utils.SFNPromptManager') as mock_prompt_manager:
                        mock_prompt_manager_instance = Mock()
                        mock_prompt_manager_instance.prompts_config = {
                            'context_analyzer': {
                                'openai': {
                                    'main': {
                                        'system_prompt': 'Test system prompt',
                                        'user_prompt_template': 'Test user prompt'
                                    }
                                }
                            }
                        }
                        mock_prompt_manager.return_value = mock_prompt_manager_instance
                        
                        context_info = self.analyzer.extract_context_info(self.sample_task_data)
                        recommendations = self.analyzer.get_context_aware_recommendations(context_info, 'cleaning_agent')
                        
                        # Check that AI was called
                        mock_ai_handler_instance.route_to.assert_called_once()
                        call_args = mock_ai_handler_instance.route_to.call_args
                        
                        # Verify configuration is generic (only messages, no hardcoded temperature/max_tokens)
                        configuration = call_args[1]['configuration']
                        assert 'messages' in configuration
                        assert 'temperature' not in configuration  # Should not be hardcoded
                        assert 'max_tokens' not in configuration  # Should not be hardcoded
                        
                        # Verify model is None (let handler decide)
                        assert call_args[1]['model'] is None
                        
                        # Check recommendations were generated
                        assert len(recommendations.data_processing) > 0
    
    def test_fallback_when_no_supported_providers(self):
        """Test that fallback recommendations are used when no supported LLM providers are available."""
        with patch('sfn_blueprint.utils.context_utils.SFN_SUPPORTED_LLM_PROVIDERS', ['openai', 'anthropic']):
            # Mock the prompt manager with no supported providers
            with patch('sfn_blueprint.utils.context_utils.SFNPromptManager') as mock_prompt_manager:
                mock_prompt_manager_instance = Mock()
                mock_prompt_manager_instance.prompts_config = {
                    'context_analyzer': {
                        'unsupported_provider': {
                            'main': {
                                'system_prompt': 'Test system prompt',
                                'user_prompt_template': 'Test user prompt'
                            }
                        }
                    }
                }
                mock_prompt_manager.return_value = mock_prompt_manager_instance
                
                context_info = self.analyzer.extract_context_info(self.sample_task_data)
                
                # Check that error is thrown instead of fallback
                with pytest.raises(ValueError) as exc_info:
                    self.analyzer.get_context_aware_recommendations(context_info, 'cleaning_agent')
                
                assert "No supported LLM providers found" in str(exc_info.value)
    
    def test_validate_required_context_success(self):
        """Test successful context validation."""
        context_info = self.analyzer.extract_context_info(self.sample_task_data)
        required_fields = ['domain', 'workflow_goal', 'data_sensitivity']
        
        validation_result = self.analyzer.validate_required_context(context_info, required_fields)
        
        assert validation_result['is_valid'] is True
        assert validation_result['quality_score'] == 1.0
        assert len(validation_result['missing_fields']) == 0
        assert len(validation_result['empty_fields']) == 0
    
    def test_validate_required_context_missing_fields(self):
        """Test context validation with missing fields."""
        context_info = self.analyzer.extract_context_info(self.sample_task_data)
        required_fields = ['domain', 'workflow_goal', 'nonexistent_field']
        
        validation_result = self.analyzer.validate_required_context(context_info, required_fields)
        
        assert validation_result['is_valid'] is False
        assert validation_result['quality_score'] < 1.0
        assert 'nonexistent_field' in validation_result['missing_fields']
    
    def test_validate_required_context_empty_fields(self):
        """Test context validation with empty fields."""
        empty_task_data = {
            'enriched_context': {
                'domain_knowledge': {
                    'domain': '',  # empty
                    'business_context': {},
                    'data_files': [],
                    'constraints': {},
                    'stakeholders': []
                },
                'workflow_context': {
                    'goal': 'Test goal',
                    'complexity': 'moderate',
                    'risk_level': 'medium'
                },
                'execution_context': {
                    'current_step': {},
                    'execution_progress': {}
                }
            }
        }
        
        context_info = self.analyzer.extract_context_info(empty_task_data)
        required_fields = ['domain', 'workflow_goal']
        
        validation_result = self.analyzer.validate_required_context(context_info, required_fields)
        
        assert validation_result['is_valid'] is False
        assert validation_result['quality_score'] < 1.0
        assert 'domain' in validation_result['empty_fields']
    
    def test_is_empty_value(self):
        """Test the _is_empty_value helper method."""
        assert self.analyzer._is_empty_value(None) is True
        assert self.analyzer._is_empty_value("") is True
        assert self.analyzer._is_empty_value("   ") is True
        assert self.analyzer._is_empty_value([]) is True
        assert self.analyzer._is_empty_value({}) is True
        assert self.analyzer._is_empty_value("valid") is False
        assert self.analyzer._is_empty_value(["item"]) is False
        assert self.analyzer._is_empty_value({"key": "value"}) is False


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    def test_extract_context_info_function(self):
        """Test the extract_context_info convenience function."""
        sample_data = {
            'enriched_context': {
                'domain_knowledge': {
                    'domain': 'test',
                    'business_context': {},
                    'data_files': [],
                    'constraints': {},
                    'stakeholders': []
                },
                'workflow_context': {
                    'goal': 'Test goal',
                    'complexity': 'simple',
                    'risk_level': 'low'
                },
                'execution_context': {
                    'current_step': {},
                    'execution_progress': {}
                }
            }
        }
        
        context_info = extract_context_info(sample_data)
        assert context_info is not None
        assert context_info.domain == 'test'
    
    def test_get_context_recommendations_function(self):
        """Test the get_context_recommendations convenience function."""
        context_info = ContextInfo(
            domain="healthcare",
            business_context={},
            workflow_goal="Test",
            data_sensitivity="medium",
            compliance_requirements=[],
            optimization_hints=[],
            risk_factors=[],
            data_files=[],
            constraints={},
            stakeholders=[],
            workflow_complexity="moderate",
            risk_level="medium",
            current_step={},
            execution_progress={}
        )
        
        # Mock the SFNPromptManager to avoid file not found errors
        with patch('sfn_blueprint.utils.context_utils.SFNPromptManager') as mock_prompt_manager:
            mock_prompt_manager_instance = Mock()
            mock_prompt_manager_instance.prompts_config = {
                'context_analyzer': {
                    'openai': {
                        'main': {
                            'system_prompt': 'Test system prompt',
                            'user_prompt_template': 'Test user prompt'
                        }
                    }
                }
            }
            mock_prompt_manager.return_value = mock_prompt_manager_instance
            
            # Mock the SFNAIHandler to avoid actual LLM calls
            with patch('sfn_blueprint.utils.context_utils.SFNAIHandler') as mock_ai_handler:
                mock_ai_handler_instance = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message.content = '{"data_processing": ["Test"], "quality_checks": [], "optimization_strategies": [], "risk_mitigation": [], "compliance_measures": [], "performance_tuning": []}'
                mock_ai_handler_instance.route_to.return_value = mock_response
                mock_ai_handler.return_value = mock_ai_handler_instance
                
                recommendations = get_context_recommendations(context_info, 'cleaning_agent')
                assert isinstance(recommendations, ContextRecommendations)
    
    def test_validate_context_function(self):
        """Test the validate_context convenience function."""
        context_info = ContextInfo(
            domain="test",
            business_context={},
            workflow_goal="Test goal",
            data_sensitivity="medium",
            compliance_requirements=[],
            optimization_hints=[],
            risk_factors=[],
            data_files=[],
            constraints={},
            stakeholders=[],
            workflow_complexity="moderate",
            risk_level="medium",
            current_step={},
            execution_progress={}
        )
        
        validation_result = validate_context(context_info, ['domain', 'workflow_goal'])
        assert validation_result['is_valid'] is True
        assert validation_result['quality_score'] == 1.0


if __name__ == "__main__":
    pytest.main([__file__])
