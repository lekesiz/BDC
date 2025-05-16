"""Tests for AI utility functions."""

import pytest
from unittest.mock import patch, MagicMock, Mock
import json
import os
from app.utils.ai import (
    configure_openai,
    analyze_evaluation_responses,
    generate_report_content
)


class TestConfigureOpenAI:
    """Test the configure_openai function."""
    
    @patch('app.utils.ai.openai')
    def test_configure_openai_with_config(self, mock_openai, app):
        """Test configuring OpenAI with application config."""
        with app.app_context():
            app.config['OPENAI_API_KEY'] = 'test-api-key'
            app.config['OPENAI_ORGANIZATION'] = 'test-org'
            
            configure_openai()
            
            assert mock_openai.api_key == 'test-api-key'
            assert mock_openai.organization == 'test-org'
    
    @patch('app.utils.ai.openai')
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'env-api-key', 'OPENAI_ORGANIZATION': 'env-org'})
    def test_configure_openai_with_env(self, mock_openai, app):
        """Test configuring OpenAI with environment variables."""
        with app.app_context():
            app.config.pop('OPENAI_API_KEY', None)
            app.config.pop('OPENAI_ORGANIZATION', None)
            
            configure_openai()
            
            assert mock_openai.api_key == 'env-api-key'
            assert mock_openai.organization == 'env-org'
    
    @patch('app.utils.ai.openai')
    def test_configure_openai_no_org(self, mock_openai, app):
        """Test configuring OpenAI without organization."""
        with app.app_context():
            app.config['OPENAI_API_KEY'] = 'test-api-key'
            app.config.pop('OPENAI_ORGANIZATION', None)
            
            configure_openai()
            
            assert mock_openai.api_key == 'test-api-key'
            # Organization should not be set when not provided
            assert not hasattr(mock_openai, 'organization') or mock_openai.organization != 'test-org'


class TestAnalyzeEvaluationResponses:
    """Test the analyze_evaluation_responses function."""
    
    @patch('app.utils.ai.openai')
    def test_analyze_evaluation_no_api_key(self, mock_openai, app):
        """Test analyze_evaluation_responses without API key."""
        with app.app_context():
            mock_openai.api_key = None
            app.config.pop('OPENAI_API_KEY', None)
            
            evaluation = {'title': 'Test Evaluation', 'questions': []}
            result = analyze_evaluation_responses(evaluation)
            
            assert result['error'] == 'AI integration not configured'
            assert result['strengths'] == []
            assert result['areas_to_improve'] == []
            assert result['recommendations'] == []
    
    @patch('app.utils.ai.openai')
    def test_analyze_evaluation_success(self, mock_openai, app):
        """Test successful evaluation analysis."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': json.dumps({
                    'strengths': ['Good understanding', 'Clear answers'],
                    'areas_to_improve': ['Time management', 'Detail depth'],
                    'recommendations': ['Practice more', 'Review materials'],
                    'summary': 'Overall good performance with room for improvement.'
                })
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            evaluation = {
                'title': 'Test Evaluation',
                'questions': [
                    {
                        'text': 'What is Python?',
                        'answer': {
                            'text': 'A programming language',
                            'score': 8
                        }
                    }
                ]
            }
            
            result = analyze_evaluation_responses(evaluation)
            
            assert result['strengths'] == ['Good understanding', 'Clear answers']
            assert result['areas_to_improve'] == ['Time management', 'Detail depth']
            assert result['recommendations'] == ['Practice more', 'Review materials']
            assert result['summary'] == 'Overall good performance with room for improvement.'
    
    @patch('app.utils.ai.openai')
    def test_analyze_evaluation_json_with_backticks(self, mock_openai, app):
        """Test parsing JSON wrapped in markdown code blocks."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response with JSON in code blocks
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': '```json\n' + json.dumps({
                    'strengths': ['Good'],
                    'areas_to_improve': ['Needs work'],
                    'recommendations': ['Try harder'],
                    'summary': 'Summary here.'
                }) + '\n```'
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            evaluation = {'title': 'Test', 'questions': []}
            result = analyze_evaluation_responses(evaluation)
            
            assert result['strengths'] == ['Good']
            assert result['areas_to_improve'] == ['Needs work']
            assert result['recommendations'] == ['Try harder']
            assert result['summary'] == 'Summary here.'
    
    @patch('app.utils.ai.openai')
    def test_analyze_evaluation_invalid_json(self, mock_openai, app):
        """Test handling invalid JSON response."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response with invalid JSON
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': 'This is not valid JSON'
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            evaluation = {'title': 'Test', 'questions': []}
            result = analyze_evaluation_responses(evaluation)
            
            assert result['error'] == 'Failed to parse AI response'
            assert result['strengths'] == []
            assert result['areas_to_improve'] == []
            assert result['recommendations'] == []
            assert 'processing error' in result['summary']
    
    @patch('app.utils.ai.openai')
    def test_analyze_evaluation_api_exception(self, mock_openai, app):
        """Test handling OpenAI API exceptions."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            mock_openai.ChatCompletion.create.side_effect = Exception('API Error')
            
            evaluation = {'title': 'Test', 'questions': []}
            result = analyze_evaluation_responses(evaluation)
            
            assert 'AI analysis failed' in result['error']
            assert result['strengths'] == []
            assert result['areas_to_improve'] == []
            assert result['recommendations'] == []
            assert 'API error' in result['summary']
    
    @patch('app.utils.ai.openai')
    def test_analyze_evaluation_missing_fields(self, mock_openai, app):
        """Test handling response with missing required fields."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response with partial data
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': json.dumps({
                    'strengths': 'Not a list',  # Wrong type
                    # Missing other fields
                })
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            evaluation = {'title': 'Test', 'questions': []}
            result = analyze_evaluation_responses(evaluation)
            
            # Should ensure lists are returned even if wrong type
            assert isinstance(result['strengths'], list)
            assert isinstance(result['areas_to_improve'], list)
            assert isinstance(result['recommendations'], list)
            assert result['summary'] == 'Analysis summary not available.'


class TestGenerateReportContent:
    """Test the generate_report_content function."""
    
    @patch('app.utils.ai.openai')
    def test_generate_report_no_api_key(self, mock_openai, app):
        """Test generate_report_content without API key."""
        with app.app_context():
            mock_openai.api_key = None
            app.config.pop('OPENAI_API_KEY', None)
            
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
    def test_generate_report_success(self, mock_openai, app):
        """Test successful report generation."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': json.dumps({
                    'executive_summary': 'Strong performance overall',
                    'strengths': ['Excellent communication', 'Problem-solving skills'],
                    'areas_for_development': ['Time management', 'Technical depth'],
                    'recommendations': ['Focus on deadlines', 'Study advanced topics'],
                    'conclusion': 'Great progress, continue the momentum.'
                })
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            beneficiary_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'status': 'Active'
            }
            evaluation_data = [
                {
                    'title': 'Math Test',
                    'score': 85,
                    'completed': True
                }
            ]
            
            result = generate_report_content(beneficiary_data, evaluation_data)
            
            assert result['executive_summary'] == 'Strong performance overall'
            assert result['strengths'] == ['Excellent communication', 'Problem-solving skills']
            assert result['areas_for_development'] == ['Time management', 'Technical depth']
            assert result['recommendations'] == ['Focus on deadlines', 'Study advanced topics']
            assert result['conclusion'] == 'Great progress, continue the momentum.'
    
    @patch('app.utils.ai.openai')
    def test_generate_report_json_with_backticks(self, mock_openai, app):
        """Test parsing JSON wrapped in markdown code blocks."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response with JSON in code blocks
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': '```json\n' + json.dumps({
                    'executive_summary': 'Summary',
                    'strengths': ['Good'],
                    'areas_for_development': ['Needs work'],
                    'recommendations': ['Try harder'],
                    'conclusion': 'Conclusion'
                }) + '\n```'
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            beneficiary_data = {'first_name': 'Jane', 'last_name': 'Smith'}
            evaluation_data = []
            result = generate_report_content(beneficiary_data, evaluation_data)
            
            assert result['executive_summary'] == 'Summary'
            assert result['strengths'] == ['Good']
            assert result['areas_for_development'] == ['Needs work']
            assert result['recommendations'] == ['Try harder']
            assert result['conclusion'] == 'Conclusion'
    
    @patch('app.utils.ai.openai')
    def test_generate_report_invalid_json(self, mock_openai, app):
        """Test handling invalid JSON response."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response with invalid JSON
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': 'This is not valid JSON'
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            beneficiary_data = {'first_name': 'Test', 'last_name': 'User'}
            evaluation_data = []
            result = generate_report_content(beneficiary_data, evaluation_data)
            
            assert result['error'] == 'Failed to parse AI response'
            assert 'processing error' in result['executive_summary']
            assert result['strengths'] == []
            assert result['areas_for_development'] == []
            assert result['recommendations'] == []
            assert 'processing error' in result['conclusion']
    
    @patch('app.utils.ai.openai')
    def test_generate_report_api_exception(self, mock_openai, app):
        """Test handling OpenAI API exceptions."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            mock_openai.ChatCompletion.create.side_effect = Exception('API Error')
            
            beneficiary_data = {'first_name': 'Error', 'last_name': 'Test'}
            evaluation_data = []
            result = generate_report_content(beneficiary_data, evaluation_data)
            
            assert 'AI report generation failed' in result['error']
            assert 'API error' in result['executive_summary']
            assert result['strengths'] == []
            assert result['areas_for_development'] == []
            assert result['recommendations'] == []
            assert 'API error' in result['conclusion']
    
    @patch('app.utils.ai.openai')
    def test_generate_report_missing_fields(self, mock_openai, app):
        """Test handling response with missing required fields."""
        with app.app_context():
            mock_openai.api_key = 'test-api-key'
            
            # Mock the OpenAI response with partial data
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message = {
                'content': json.dumps({
                    'executive_summary': None,  # Wrong type
                    'strengths': 'Not a list',  # Wrong type
                    # Missing other fields
                })
            }
            mock_openai.ChatCompletion.create.return_value = mock_response
            
            beneficiary_data = {'first_name': 'Partial', 'last_name': 'Data'}
            evaluation_data = []
            result = generate_report_content(beneficiary_data, evaluation_data)
            
            # Should ensure correct types are returned
            assert isinstance(result['executive_summary'], str)
            assert isinstance(result['strengths'], list)
            assert isinstance(result['areas_for_development'], list)
            assert isinstance(result['recommendations'], list)
            assert isinstance(result['conclusion'], str)