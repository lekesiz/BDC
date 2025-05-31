"""Comprehensive tests for AI utility module."""

import pytest
import json
import re
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from app.utils.ai import (
    configure_openai, analyze_evaluation_responses, generate_report_content
)


class TestConfigureOpenAI:
    """Test the configure_openai function."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        return app
    
    @patch('app.utils.ai.openai')
    def test_configure_with_config_values(self, mock_openai, app):
        """Test OpenAI configuration with app config values."""
        app.config['OPENAI_API_KEY'] = 'test-api-key'
        app.config['OPENAI_ORGANIZATION'] = 'test-org'
        
        with app.app_context():
            configure_openai()
        
        assert mock_openai.api_key == 'test-api-key'
        assert mock_openai.organization == 'test-org'
    
    @patch('app.utils.ai.openai')
    @patch('app.utils.ai.os.getenv')
    def test_configure_with_env_values(self, mock_getenv, mock_openai, app):
        """Test OpenAI configuration with environment variables."""
        app.config['OPENAI_API_KEY'] = None
        app.config['OPENAI_ORGANIZATION'] = None
        mock_getenv.side_effect = lambda key, default: {
            'OPENAI_API_KEY': 'env-api-key',
            'OPENAI_ORGANIZATION': 'env-org'
        }.get(key, default)
        
        with app.app_context():
            configure_openai()
        
        assert mock_openai.api_key == 'env-api-key'
        assert mock_openai.organization == 'env-org'
    
    @patch('app.utils.ai.openai')
    def test_configure_without_organization(self, mock_openai, app):
        """Test OpenAI configuration without organization."""
        app.config['OPENAI_API_KEY'] = 'test-api-key'
        app.config['OPENAI_ORGANIZATION'] = ''
        
        with app.app_context():
            configure_openai()
        
        assert mock_openai.api_key == 'test-api-key'
        # Organization should not be set if empty
        assert not hasattr(mock_openai, 'organization') or mock_openai.organization == ''


class TestAnalyzeEvaluationResponses:
    """Test the analyze_evaluation_responses function."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.logger = Mock()
        return app
    
    @pytest.fixture
    def sample_evaluation(self):
        """Create sample evaluation data."""
        return {
            'title': 'Test Evaluation',
            'questions': [
                {
                    'text': 'What is 2+2?',
                    'answer': {
                        'text': '4',
                        'score': 100
                    }
                },
                {
                    'text': 'What is the capital of France?',
                    'answer': {
                        'text': 'Paris',
                        'score': 100
                    }
                }
            ]
        }
    
    @patch('app.utils.ai.openai')
    def test_analyze_without_api_key(self, mock_openai, app, sample_evaluation):
        """Test analysis without API key configured."""
        mock_openai.api_key = None
        
        with app.app_context():
            result = analyze_evaluation_responses(sample_evaluation)
        
        assert result['error'] == 'AI integration not configured'
        assert result['strengths'] == []
        assert result['areas_to_improve'] == []
        assert result['recommendations'] == []
    
    @patch('app.utils.ai.openai')
    def test_analyze_successful(self, mock_openai, app, sample_evaluation):
        """Test successful evaluation analysis."""
        mock_openai.api_key = 'test-key'
        
        # Mock the ChatCompletion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': json.dumps({
                'strengths': ['Perfect score on math', 'Geography knowledge'],
                'areas_to_improve': ['Could provide more detailed answers'],
                'recommendations': ['Continue practicing'],
                'summary': 'Excellent performance overall.'
            })
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = analyze_evaluation_responses(sample_evaluation)
        
        assert 'Perfect score on math' in result['strengths']
        assert 'Could provide more detailed answers' in result['areas_to_improve']
        assert 'Continue practicing' in result['recommendations']
        assert result['summary'] == 'Excellent performance overall.'
    
    @patch('app.utils.ai.openai')
    def test_analyze_with_json_wrapped_response(self, mock_openai, app, sample_evaluation):
        """Test analysis when response is wrapped in markdown code blocks."""
        mock_openai.api_key = 'test-key'
        
        # Mock response with markdown code blocks
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': '''Here's the analysis:
```json
{
    "strengths": ["Good understanding"],
    "areas_to_improve": ["Speed"],
    "recommendations": ["Practice more"],
    "summary": "Good progress."
}
```'''
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = analyze_evaluation_responses(sample_evaluation)
        
        assert 'Good understanding' in result['strengths']
        assert 'Speed' in result['areas_to_improve']
        assert 'Practice more' in result['recommendations']
        assert result['summary'] == 'Good progress.'
    
    @patch('app.utils.ai.openai')
    def test_analyze_with_malformed_json(self, mock_openai, app, sample_evaluation):
        """Test analysis with malformed JSON response."""
        mock_openai.api_key = 'test-key'
        
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': 'This is not valid JSON { broken'
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = analyze_evaluation_responses(sample_evaluation)
        
        assert result['error'] == 'Failed to parse AI response'
        assert result['strengths'] == []
        assert result['areas_to_improve'] == []
        assert result['recommendations'] == []
    
    @patch('app.utils.ai.openai')
    def test_analyze_with_api_error(self, mock_openai, app, sample_evaluation):
        """Test analysis when API call fails."""
        mock_openai.api_key = 'test-key'
        mock_openai.ChatCompletion.create.side_effect = Exception('API Error')
        
        with app.app_context():
            result = analyze_evaluation_responses(sample_evaluation)
        
        assert 'AI analysis failed' in result['error']
        assert result['strengths'] == []
        assert result['areas_to_improve'] == []
        assert result['recommendations'] == []
    
    @patch('app.utils.ai.openai')
    def test_analyze_with_missing_fields(self, mock_openai, app, sample_evaluation):
        """Test analysis when response is missing required fields."""
        mock_openai.api_key = 'test-key'
        
        # Mock response with missing fields
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': json.dumps({
                'strengths': 'Not a list',  # Wrong type
                'summary': 'Test summary'
                # Missing other fields
            })
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = analyze_evaluation_responses(sample_evaluation)
        
        # Should fix the types and add missing fields
        assert isinstance(result['strengths'], list)
        assert isinstance(result['areas_to_improve'], list)
        assert isinstance(result['recommendations'], list)
        assert result['summary'] == 'Test summary'
    
    def test_analyze_with_no_answers(self, app):
        """Test analysis with questions that have no answers."""
        evaluation = {
            'title': 'Test Evaluation',
            'questions': [
                {
                    'text': 'Unanswered question',
                    'answer': {}
                }
            ]
        }
        
        with patch('app.utils.ai.openai') as mock_openai:
            mock_openai.api_key = 'test-key'
            
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = {
                'content': json.dumps({
                    'strengths': [],
                    'areas_to_improve': ['No answers provided'],
                    'recommendations': ['Complete the evaluation'],
                    'summary': 'Evaluation incomplete.'
                })
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            with app.app_context():
                result = analyze_evaluation_responses(evaluation)
            
            assert result['areas_to_improve'] == ['No answers provided']
            assert result['recommendations'] == ['Complete the evaluation']


class TestGenerateReportContent:
    """Test the generate_report_content function."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.logger = Mock()
        return app
    
    @pytest.fixture
    def beneficiary_data(self):
        """Create sample beneficiary data."""
        return {
            'first_name': 'John',
            'last_name': 'Doe',
            'status': 'active'
        }
    
    @pytest.fixture
    def evaluation_data(self):
        """Create sample evaluation data."""
        return [
            {
                'title': 'Math Test',
                'score': 85,
                'date': '2023-05-01'
            },
            {
                'title': 'English Test',
                'score': 92,
                'date': '2023-05-02'
            }
        ]
    
    @patch('app.utils.ai.openai')
    def test_generate_without_api_key(self, mock_openai, app, beneficiary_data, evaluation_data):
        """Test report generation without API key configured."""
        mock_openai.api_key = None
        
        with app.app_context():
            result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert result['error'] == 'AI integration not configured'
        assert result['executive_summary'] == 'Not available'
        assert result['strengths'] == []
        assert result['areas_for_development'] == []
        assert result['recommendations'] == []
        assert result['conclusion'] == 'Not available'
    
    @patch('app.utils.ai.openai')
    def test_generate_successful(self, mock_openai, app, beneficiary_data, evaluation_data):
        """Test successful report generation."""
        mock_openai.api_key = 'test-key'
        
        # Mock the ChatCompletion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': json.dumps({
                'executive_summary': 'John Doe shows excellent progress.',
                'strengths': ['Strong performance in English', 'Good math skills'],
                'areas_for_development': ['Could improve calculation speed'],
                'recommendations': ['Continue current study methods', 'Practice timed exercises'],
                'conclusion': 'Overall excellent performance. Keep up the good work!'
            })
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert result['executive_summary'] == 'John Doe shows excellent progress.'
        assert 'Strong performance in English' in result['strengths']
        assert 'Could improve calculation speed' in result['areas_for_development']
        assert 'Continue current study methods' in result['recommendations']
        assert 'Overall excellent performance' in result['conclusion']
    
    @patch('app.utils.ai.openai')
    def test_generate_with_json_wrapped_response(self, mock_openai, app, beneficiary_data, evaluation_data):
        """Test report generation when response is wrapped in markdown code blocks."""
        mock_openai.api_key = 'test-key'
        
        # Mock response with markdown code blocks
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': '''Based on the evaluation results:
```json
{
    "executive_summary": "Summary here",
    "strengths": ["Strength 1"],
    "areas_for_development": ["Area 1"],
    "recommendations": ["Recommendation 1"],
    "conclusion": "Conclusion here"
}
```
That's the report.'''
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert result['executive_summary'] == 'Summary here'
        assert result['strengths'] == ['Strength 1']
        assert result['areas_for_development'] == ['Area 1']
        assert result['recommendations'] == ['Recommendation 1']
        assert result['conclusion'] == 'Conclusion here'
    
    @patch('app.utils.ai.openai')
    def test_generate_with_malformed_json(self, mock_openai, app, beneficiary_data, evaluation_data):
        """Test report generation with malformed JSON response."""
        mock_openai.api_key = 'test-key'
        
        # Mock response with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': 'Invalid JSON { not closed properly'
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert result['error'] == 'Failed to parse AI response'
        assert result['executive_summary'] == 'Not available due to processing error'
        assert result['strengths'] == []
    
    @patch('app.utils.ai.openai')
    def test_generate_with_api_error(self, mock_openai, app, beneficiary_data, evaluation_data):
        """Test report generation when API call fails."""
        mock_openai.api_key = 'test-key'
        mock_openai.ChatCompletion.create.side_effect = Exception('API Error')
        
        with app.app_context():
            result = generate_report_content(beneficiary_data, evaluation_data)
        
        assert 'AI report generation failed' in result['error']
        assert result['executive_summary'] == 'Not available due to API error'
        assert result['conclusion'] == 'Not available due to API error'
    
    @patch('app.utils.ai.openai')
    def test_generate_with_missing_fields(self, mock_openai, app, beneficiary_data, evaluation_data):
        """Test report generation when response is missing required fields."""
        mock_openai.api_key = 'test-key'
        
        # Mock response with missing fields
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = {
            'content': json.dumps({
                'executive_summary': 123,  # Wrong type
                'strengths': 'Not a list',  # Wrong type
                # Missing other fields
            })
        }
        mock_openai.ChatCompletion.create.return_value = mock_response
        
        with app.app_context():
            result = generate_report_content(beneficiary_data, evaluation_data)
        
        # Should fix the types and add missing fields
        assert isinstance(result['executive_summary'], str)
        assert isinstance(result['strengths'], list)
        assert isinstance(result['areas_for_development'], list)
        assert isinstance(result['recommendations'], list)
        assert isinstance(result['conclusion'], str)