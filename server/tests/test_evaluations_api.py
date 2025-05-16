"""Tests for evaluations API endpoints."""

import json
from datetime import datetime
import pytest
from app.models import User, Beneficiary, TestSet, Question, TestSession
from app.extensions import db

@pytest.fixture
def setup_evaluation_api_data(session, app):
    """Setup test data for evaluation API tests."""
    with app.app_context():
        # Create test users with unique usernames
        import uuid
        suffix = str(uuid.uuid4())[:8]
        
        admin_user = User(
            username=f'admin_eval_{suffix}',
            email=f'admin_eval_{suffix}@test.com',
            first_name='Admin',
            last_name='User',
            is_active=True,
            role='admin',
            tenant_id=1
        )
        admin_user.password = 'password123'
        
        psychologist_user = User(
            username=f'psychologist_{suffix}',
            email=f'psychologist_{suffix}@test.com',
            first_name='Test',
            last_name='Psychologist',
            is_active=True,
            role='psychologist',
            tenant_id=1
        )
        psychologist_user.password = 'password123'
        
        # Create beneficiary user
        beneficiary_user = User(
            username=f'beneficiary_{suffix}',
            email=f'beneficiary_{suffix}@test.com',
            first_name='Test',
            last_name='Beneficiary',
            is_active=True,
            role='student',
            tenant_id=1
        )
        beneficiary_user.password = 'password123'
        
        session.add_all([admin_user, psychologist_user, beneficiary_user])
        session.flush()
        
        # Create beneficiary
        beneficiary = Beneficiary(
            user_id=beneficiary_user.id,
            trainer_id=psychologist_user.id,
            tenant_id=1,
            phone='1234567890'
        )
        
        # Create test sets
        test_set1 = TestSet(
            title='Psychological Assessment',
            description='Basic psychological assessment',
            instructions='Please answer all questions honestly',
            type='assessment',
            category='psychology',
            time_limit=60,
            passing_score=70.0,
            status='active',
            creator_id=admin_user.id,
            tenant_id=1
        )
        
        test_set2 = TestSet(
            title='Cognitive Test',
            description='Cognitive ability test',
            instructions='Complete all tasks',
            type='test',
            category='cognitive',
            time_limit=30,
            passing_score=80.0,
            status='active',
            creator_id=admin_user.id,
            tenant_id=1
        )
        
        session.add_all([beneficiary, test_set1, test_set2])
        session.flush()
        
        # Create questions for test_set1
        question1 = Question(
            test_set_id=test_set1.id,
            text='How are you feeling today?',
            type='multiple_choice',
            options={
                'choices': [
                    {'id': 'a', 'text': 'Very good'},
                    {'id': 'b', 'text': 'Good'},
                    {'id': 'c', 'text': 'Neutral'},
                    {'id': 'd', 'text': 'Bad'}
                ]
            },
            correct_answer={'answer': 'a'},
            points=10.0,
            order=1
        )
        
        question2 = Question(
            test_set_id=test_set1.id,
            text='Do you feel anxious often?',
            type='true_false',
            correct_answer={'answer': False},
            points=10.0,
            order=2
        )
        
        # Create test session
        test_session = TestSession(
            test_set_id=test_set1.id,
            beneficiary_id=beneficiary.id,
            start_time=datetime.utcnow(),
            status='in_progress'
        )
        
        session.add_all([question1, question2, test_session])
        session.commit()
        
        return {
            'admin': admin_user,
            'psychologist': psychologist_user,
            'beneficiary_user': beneficiary_user,
            'beneficiary': beneficiary,
            'test_set1': test_set1,
            'test_set2': test_set2,
            'question1': question1,
            'question2': question2,
            'test_session': test_session
        }


def test_list_evaluations(client, setup_evaluation_api_data, app):
    """Test listing evaluations."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['psychologist'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = client.get('/api/evaluations', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert 'evaluations' in data
        assert len(data['evaluations']) >= 2


def test_get_evaluation(client, setup_evaluation_api_data, app):
    """Test getting a single evaluation."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['psychologist'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        evaluation_id = setup_evaluation_api_data['test_set1'].id
        response = client.get(f'/api/evaluations/{evaluation_id}', headers=headers)
        
        assert response.status_code == 200
        data = response.json
        assert data['id'] == evaluation_id
        assert data['title'] == 'Psychological Assessment'


def test_create_evaluation(client, setup_evaluation_api_data, app):
    """Test creating a new evaluation."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['admin'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        evaluation_data = {
            'title': 'New Assessment',
            'description': 'A new psychological assessment',
            'instructions': 'Complete all questions',
            'type': 'assessment',
            'category': 'mental_health',
            'time_limit': 45,
            'passing_score': 75.0,
            'questions': [
                {
                    'text': 'Rate your stress level',
                    'type': 'multiple_choice',
                    'options': {
                        'choices': [
                            {'id': '1', 'text': 'Very Low'},
                            {'id': '2', 'text': 'Low'},
                            {'id': '3', 'text': 'Medium'},
                            {'id': '4', 'text': 'High'},
                            {'id': '5', 'text': 'Very High'}
                        ]
                    },
                    'correct_answer': {'answer': '1'},
                    'points': 20.0,
                    'order': 1
                }
            ]
        }
        
        response = client.post(
            '/api/evaluations',
            data=json.dumps(evaluation_data),
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['title'] == 'New Assessment'
        assert data['time_limit'] == 45


def test_update_evaluation(client, setup_evaluation_api_data, app):
    """Test updating an evaluation."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['admin'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        evaluation_id = setup_evaluation_api_data['test_set1'].id
        update_data = {
            'title': 'Updated Assessment',
            'description': 'Updated description',
            'time_limit': 90,
            'passing_score': 65.0
        }
        
        response = client.put(
            f'/api/evaluations/{evaluation_id}',
            data=json.dumps(update_data),
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['title'] == 'Updated Assessment'
        assert data['time_limit'] == 90
        assert data['passing_score'] == 65.0


def test_delete_evaluation(client, setup_evaluation_api_data, app):
    """Test deleting an evaluation."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['admin'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        evaluation_id = setup_evaluation_api_data['test_set2'].id
        response = client.delete(
            f'/api/evaluations/{evaluation_id}',
            headers=headers
        )
        
        assert response.status_code == 204


def test_get_evaluation_questions(client, setup_evaluation_api_data, app):
    """Test getting evaluation questions."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['psychologist'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        evaluation_id = setup_evaluation_api_data['test_set1'].id
        response = client.get(
            f'/api/evaluations/{evaluation_id}/questions',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'questions' in data
        assert len(data['questions']) == 2


def test_start_evaluation_session(client, setup_evaluation_api_data, app):
    """Test starting an evaluation session."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['psychologist'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        evaluation_id = setup_evaluation_api_data['test_set2'].id
        beneficiary_id = setup_evaluation_api_data['beneficiary'].id
        
        session_data = {
            'beneficiary_id': beneficiary_id
        }
        
        response = client.post(
            f'/api/evaluations/{evaluation_id}/start',
            data=json.dumps(session_data),
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json
        assert 'session_id' in data
        assert data['status'] == 'in_progress'


def test_submit_evaluation_response(client, setup_evaluation_api_data, app):
    """Test submitting evaluation responses."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['psychologist'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        session_id = setup_evaluation_api_data['test_session'].id
        question_id = setup_evaluation_api_data['question1'].id
        
        response_data = {
            'question_id': question_id,
            'answer': 'b',
            'time_spent': 30
        }
        
        response = client.post(
            f'/api/evaluations/sessions/{session_id}/responses',
            data=json.dumps(response_data),
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json
        assert data['question_id'] == question_id
        assert data['answer'] == 'b'


def test_complete_evaluation_session(client, setup_evaluation_api_data, app):
    """Test completing an evaluation session."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['psychologist'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        session_id = setup_evaluation_api_data['test_session'].id
        
        response = client.post(
            f'/api/evaluations/sessions/{session_id}/complete',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert data['status'] == 'completed'
        assert 'score' in data
        assert 'passed' in data


def test_get_evaluation_results(client, setup_evaluation_api_data, app):
    """Test getting evaluation results."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=setup_evaluation_api_data['psychologist'].id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        session_id = setup_evaluation_api_data['test_session'].id
        
        response = client.get(
            f'/api/evaluations/sessions/{session_id}/results',
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json
        assert 'score' in data
        assert 'total_questions' in data
        assert 'correct_answers' in data
        assert 'time_spent' in data


def test_evaluation_forbidden_non_admin(client, setup_evaluation_api_data, app):
    """Test that non-admin users cannot create evaluations."""
    with app.app_context():
        from flask_jwt_extended import create_access_token
        # Use beneficiary token (not admin)
        access_token = create_access_token(identity=setup_evaluation_api_data['beneficiary_user'].id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        evaluation_data = {
            'title': 'Unauthorized Test',
            'description': 'Should not be created',
            'type': 'test'
        }
        
        response = client.post(
            '/api/evaluations',
            data=json.dumps(evaluation_data),
            headers=headers
        )
        
        assert response.status_code == 403