"""Tests for evaluation endpoints."""

import json
from unittest.mock import patch


def test_get_evaluations(client, auth_headers):
    """Test getting list of evaluations."""
    # Mock evaluation service
    with patch('app.api.evaluations.evaluation_service.get_evaluations') as mock_get:
        # Configure the mock to return a list of evaluations
        mock_get.return_value = [
            {
                'id': 1, 
                'title': 'Evaluation One',
                'beneficiary_id': 1, 
                'status': 'completed',
                'score': 85,
                'date_created': '2025-05-01T14:30:00Z'
            },
            {
                'id': 2, 
                'title': 'Evaluation Two',
                'beneficiary_id': 2, 
                'status': 'in_progress',
                'score': None,
                'date_created': '2025-05-10T09:15:00Z'
            },
        ]
        
        # Send request
        response = client.get(
            '/api/evaluations',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['title'] == 'Evaluation One'


def test_get_evaluation(client, auth_headers):
    """Test getting a specific evaluation."""
    # Mock evaluation service
    with patch('app.api.evaluations.evaluation_service.get_evaluation_by_id') as mock_get:
        # Configure the mock to return an evaluation
        mock_get.return_value = {
            'id': 1, 
            'title': 'Evaluation One',
            'beneficiary_id': 1, 
            'status': 'completed',
            'score': 85,
            'date_created': '2025-05-01T14:30:00Z',
            'questions': [
                {'id': 1, 'text': 'Question 1', 'answer': 'Answer 1'},
                {'id': 2, 'text': 'Question 2', 'answer': 'Answer 2'}
            ]
        }
        
        # Send request
        response = client.get(
            '/api/evaluations/1',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert response.json['title'] == 'Evaluation One'
        assert len(response.json['questions']) == 2


def test_create_evaluation(client, auth_headers):
    """Test creating a new evaluation."""
    # Mock evaluation service
    with patch('app.api.evaluations.evaluation_service.create_evaluation') as mock_create:
        # Configure the mock to return a new evaluation
        mock_create.return_value = {
            'id': 3, 
            'title': 'New Evaluation',
            'beneficiary_id': 1, 
            'status': 'not_started',
            'score': None,
            'date_created': '2025-05-15T11:00:00Z'
        }
        
        # Send request
        response = client.post(
            '/api/evaluations',
            data=json.dumps({
                'title': 'New Evaluation',
                'beneficiary_id': 1,
                'template_id': 2
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 201
        assert response.json['title'] == 'New Evaluation'
        assert response.json['status'] == 'not_started'


def test_update_evaluation(client, auth_headers):
    """Test updating an evaluation."""
    # Mock evaluation service
    with patch('app.api.evaluations.evaluation_service.update_evaluation') as mock_update:
        # Configure the mock to return an updated evaluation
        mock_update.return_value = {
            'id': 1, 
            'title': 'Updated Evaluation',
            'beneficiary_id': 1, 
            'status': 'completed',
            'score': 92,
            'date_created': '2025-05-01T14:30:00Z',
            'date_completed': '2025-05-15T16:45:00Z'
        }
        
        # Send request
        response = client.put(
            '/api/evaluations/1',
            data=json.dumps({
                'title': 'Updated Evaluation',
                'status': 'completed',
                'score': 92
            }),
            content_type='application/json',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert response.json['title'] == 'Updated Evaluation'
        assert response.json['score'] == 92


def test_delete_evaluation(client, auth_headers):
    """Test deleting an evaluation."""
    # Mock evaluation service
    with patch('app.api.evaluations.evaluation_service.delete_evaluation') as mock_delete:
        # Configure the mock to return success
        mock_delete.return_value = True
        
        # Send request
        response = client.delete(
            '/api/evaluations/1',
            headers=auth_headers
        )
        
        # Assert response
        assert response.status_code == 200
        assert 'message' in response.json