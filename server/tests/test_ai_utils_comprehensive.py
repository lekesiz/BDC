"""Comprehensive tests for AI utility module."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from app.utils.ai import (
    configure_openai,
    analyze_evaluation_responses,
    generate_report_content
)


class TestConfigureOpenAI:
    """Test configure_openai function."""
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_configure_openai_with_config(self, mock_app, mock_openai):
        """Test OpenAI configuration with app config."""
        mock_app.config.get.side_effect = lambda key, default: {
            'OPENAI_API_KEY': 'sk-test-key-123',
            'OPENAI_ORGANIZATION': 'org-test-123'
        }.get(key, default)
        
        configure_openai()
        
        assert mock_openai.api_key == 'sk-test-key-123'
        assert mock_openai.organization == 'org-test-123'
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-env-key', 'OPENAI_ORGANIZATION': 'org-env'})
    def test_configure_openai_with_env(self, mock_app, mock_openai):
        """Test OpenAI configuration with environment variables."""
        mock_app.config.get.return_value = None
        
        configure_openai()
        
        assert mock_openai.api_key == 'sk-env-key'
        assert mock_openai.organization == 'org-env'
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_configure_openai_no_org(self, mock_app, mock_openai):
        """Test OpenAI configuration without organization."""
        mock_app.config.get.side_effect = lambda key, default: {
            'OPENAI_API_KEY': 'sk-test-key'
        }.get(key, default)
        
        configure_openai()
        
        assert mock_openai.api_key == 'sk-test-key'
        # Organization should not be set if not provided
        assert not hasattr(mock_openai, 'organization') or mock_openai.organization == ''


class TestAnalyzeEvaluationResponses:
    """Test analyze_evaluation_responses function."""
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_analyze_evaluation_no_api_key(self, mock_app, mock_openai):
        """Test analysis when API key is not configured."""
        mock_app.config.get.return_value = None
        mock_openai.api_key = None
        
        evaluation = {
            'title': 'Test Evaluation',
            'questions': [
                {'text': 'What is Python?', 'answer': {'text': 'A programming language'}}
            ]
        }
        
        result = analyze_evaluation_responses(evaluation)
        
        assert result['error'] == 'AI integration not configured'
        assert result['strengths'] == []
        assert result['areas_to_improve'] == []
        assert result['recommendations'] == []
        mock_app.logger.error.assert_called_once()
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_analyze_evaluation_success(self, mock_app, mock_openai):
        """Test successful evaluation analysis."""
        mock_app.config.get.return_value = 'sk-test-key'
        mock_openai.api_key = 'sk-test-key'
        
        # Mock OpenAI response
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message={'content': '''
            {
                "strengths": ["Good understanding of basics", "Clear communication"],
                "areas_to_improve": ["Need more practice with advanced concepts"],
                "recommendations": ["Study advanced Python topics", "Practice more coding exercises"],
                "summary": "Overall good performance with room for improvement"
            }
            '''})
        ]
        mock_openai.ChatCompletion.create.return_value = mock_completion
        
        evaluation = {
            'title': 'Python Assessment',
            'questions': [
                {'text': 'What is Python?', 'answer': {'text': 'A programming language', 'score': 10}},
                {'text': 'What is a variable?', 'answer': {'text': 'A container for data'}}
            ]
        }
        
        result = analyze_evaluation_responses(evaluation)
        
        assert 'strengths' in result
        assert len(result['strengths']) == 2
        assert 'areas_to_improve' in result
        assert 'recommendations' in result
        assert 'summary' in result
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_analyze_evaluation_api_error(self, mock_app, mock_openai):
        """Test evaluation analysis with API error."""
        mock_app.config.get.return_value = 'sk-test-key'
        mock_openai.api_key = 'sk-test-key'
        mock_openai.ChatCompletion.create.side_effect = Exception('API Error')
        
        evaluation = {'questions': []}
        
        result = analyze_evaluation_responses(evaluation)
        
        assert 'error' in result
        assert 'AI analysis failed' in result['error']
        mock_app.logger.error.assert_called()
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_analyze_evaluation_json_parse_error(self, mock_app, mock_openai):
        """Test evaluation analysis with JSON parsing error."""
        mock_app.config.get.return_value = 'sk-test-key'
        mock_openai.api_key = 'sk-test-key'
        
        # Mock OpenAI response with invalid JSON
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message={'content': 'Invalid JSON response'})
        ]
        mock_openai.ChatCompletion.create.return_value = mock_completion
        
        evaluation = {'questions': []}
        
        result = analyze_evaluation_responses(evaluation)
        
        # Should handle JSON parse error gracefully
        assert result['error'] == 'Failed to parse AI response'
        assert isinstance(result['strengths'], list)
        assert isinstance(result['areas_to_improve'], list)
        assert isinstance(result['recommendations'], list)
        assert result['summary'] == 'Analysis summary not available due to processing error.'


class TestGenerateReportContent:
    """Test generate_report_content function."""
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_generate_report_no_api_key(self, mock_app, mock_openai):
        """Test report generation without API key."""
        mock_app.config.get.return_value = None
        mock_openai.api_key = None
        
        beneficiary_data = {'first_name': 'John', 'last_name': 'Doe'}
        evaluation_data = []
        
        result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert result['error'] == 'AI integration not configured'
        assert result['executive_summary'] == 'Not available'
        assert result['strengths'] == []
        assert result['areas_for_development'] == []
        assert result['recommendations'] == []
        assert result['conclusion'] == 'Not available'
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_generate_report_success(self, mock_app, mock_openai):
        """Test successful report generation."""
        mock_app.config.get.return_value = 'sk-test-key'
        mock_openai.api_key = 'sk-test-key'
        
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message={'content': '''
            {
                "executive_summary": "John Doe has shown excellent progress",
                "strengths": ["Strong analytical skills", "Good communication"],
                "areas_for_development": ["Time management", "Advanced techniques"],
                "recommendations": ["Focus on advanced topics", "Practice time management"],
                "conclusion": "Continue with current learning path"
            }
            '''})
        ]
        mock_openai.ChatCompletion.create.return_value = mock_completion
        
        beneficiary_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'status': 'active'
        }
        evaluation_data = [
            {'score': 85, 'title': 'Python Assessment'},
            {'score': 90, 'title': 'Data Analysis'}
        ]
        
        result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert result['executive_summary'] == 'John Doe has shown excellent progress'
        assert 'strengths' in result
        assert len(result['strengths']) == 2
        assert 'areas_for_development' in result
        assert 'recommendations' in result
        assert 'conclusion' in result
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_generate_report_with_json_wrapper(self, mock_app, mock_openai):
        """Test report generation with markdown JSON wrapper."""
        mock_app.config.get.return_value = 'sk-test-key'
        mock_openai.api_key = 'sk-test-key'
        
        mock_completion = Mock()
        mock_completion.choices = [
            Mock(message={'content': '''Here is the report:
            ```json
            {
                "executive_summary": "Summary",
                "strengths": ["Strength 1"],
                "areas_for_development": ["Area 1"],
                "recommendations": ["Recommendation 1"],
                "conclusion": "Conclusion"
            }
            ```
            '''})
        ]
        mock_openai.ChatCompletion.create.return_value = mock_completion
        
        beneficiary_data = {'first_name': 'Jane', 'last_name': 'Smith'}
        evaluation_data = []
        
        result = generate_report_content(beneficiary_data, evaluation_data)
        
        # Should successfully parse JSON from markdown wrapper
        assert result['executive_summary'] == 'Summary'
        assert result['strengths'] == ['Strength 1']
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.current_app')
    def test_generate_report_api_error(self, mock_app, mock_openai):
        """Test report generation with API error."""
        mock_app.config.get.return_value = 'sk-test-key'
        mock_openai.api_key = 'sk-test-key'
        mock_openai.ChatCompletion.create.side_effect = Exception('API Error')
        
        beneficiary_data = {'first_name': 'Test', 'last_name': 'User'}
        evaluation_data = []
        
        result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert 'error' in result
        assert 'AI report generation failed' in result['error']
        assert result['executive_summary'] == 'Not available due to API error'
        mock_app.logger.error.assert_called()