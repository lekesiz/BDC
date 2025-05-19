import pytest
import json
from datetime import datetime, timedelta
from app.models import Test, Question, TestSession, Response

class TestAssessments:
    """Test assessment/test engine endpoints."""
    
    def test_create_test(self, client, auth_headers, test_tenant):
        """Test creating a new test."""
        data = {
            'name': 'Python Basics Test',
            'description': 'Test your Python knowledge',
            'duration_minutes': 60,
            'passing_score': 70,
            'is_active': True,
            'instructions': 'Answer all questions within the time limit'
        }
        
        response = client.post('/api/tests',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Python Basics Test'
        assert data['duration_minutes'] == 60
        assert data['passing_score'] == 70
    
    def test_get_tests(self, client, auth_headers, test_test):
        """Test getting list of tests."""
        response = client.get('/api/tests',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tests' in data
        assert len(data['tests']) > 0
    
    def test_get_test_by_id(self, client, auth_headers, test_test):
        """Test getting a specific test."""
        response = client.get(f'/api/tests/{test_test.id}',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_test.id
        assert data['name'] == test_test.name
    
    def test_create_question(self, client, auth_headers, test_test):
        """Test creating a test question."""
        data = {
            'question_text': 'What is Python?',
            'question_type': 'multiple_choice',
            'points': 10,
            'correct_answer': 'A programming language',
            'answer_options': [
                'A programming language',
                'A snake',
                'A software',
                'A framework'
            ]
        }
        
        response = client.post(f'/api/tests/{test_test.id}/questions',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['question_text'] == 'What is Python?'
        assert data['points'] == 10
    
    def test_get_test_questions(self, client, auth_headers, test_test, test_question):
        """Test getting test questions."""
        response = client.get(f'/api/tests/{test_test.id}/questions',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'questions' in data
        assert len(data['questions']) > 0
    
    def test_update_question(self, client, auth_headers, test_test, test_question):
        """Test updating a question."""
        data = {
            'points': 15,
            'question_text': 'Updated: What is Python?'
        }
        
        response = client.put(f'/api/tests/{test_test.id}/questions/{test_question.id}',
                             json=data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['points'] == 15
        assert 'Updated' in data['question_text']
    
    def test_delete_question(self, client, auth_headers, test_test, test_question):
        """Test deleting a question."""
        response = client.delete(f'/api/tests/{test_test.id}/questions/{test_question.id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Question deleted successfully'
    
    def test_start_test_session(self, client, student_headers, test_test, test_student):
        """Test starting a test session."""
        response = client.post(f'/api/tests/{test_test.id}/start',
                              headers=student_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'session_id' in data
        assert 'start_time' in data
        assert 'end_time' in data
    
    def test_submit_answer(self, client, student_headers, test_test, test_question, test_student, db_session):
        """Test submitting an answer."""
        # Start a test session first
        session = TestSession(
            test_id=test_test.id,
            user_id=test_student.id,
            started_at=datetime.now()
        )
        db_session.add(session)
        db_session.commit()
        
        data = {
            'answer': '4'
        }
        
        response = client.post(f'/api/tests/sessions/{session.id}/questions/{test_question.id}/answer',
                              json=data,
                              headers=student_headers,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['answer'] == '4'
        assert data['is_correct'] == True
    
    def test_complete_test_session(self, client, student_headers, test_test, test_student, db_session):
        """Test completing a test session."""
        # Create a test session
        session = TestSession(
            test_id=test_test.id,
            user_id=test_student.id,
            started_at=datetime.now()
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.post(f'/api/tests/sessions/{session.id}/complete',
                              headers=student_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'score' in data
        assert 'passed' in data
        assert 'completed_at' in data
    
    def test_get_test_results(self, client, student_headers, test_test, test_student, db_session):
        """Test getting test results."""
        # Create a completed test session
        session = TestSession(
            test_id=test_test.id,
            user_id=test_student.id,
            started_at=datetime.now(),
            completed_at=datetime.now(),
            score=85.0,
            passed=True
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.get(f'/api/tests/sessions/{session.id}/results',
                             headers=student_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['score'] == 85.0
        assert data['passed'] == True
    
    def test_get_user_test_history(self, client, student_headers, test_student):
        """Test getting user's test history."""
        response = client.get('/api/tests/my-tests',
                             headers=student_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tests' in data
        assert isinstance(data['tests'], list)
    
    def test_assign_test_to_beneficiary(self, client, auth_headers, test_test, test_beneficiary):
        """Test assigning a test to a beneficiary."""
        data = {
            'beneficiary_id': test_beneficiary.id,
            'due_date': (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        response = client.post(f'/api/tests/{test_test.id}/assign',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['test_id'] == test_test.id
        assert data['beneficiary_id'] == test_beneficiary.id
    
    def test_test_analytics(self, client, auth_headers, test_test):
        """Test getting test analytics."""
        response = client.get(f'/api/tests/{test_test.id}/analytics',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_attempts' in data
        assert 'average_score' in data
        assert 'pass_rate' in data
        assert 'question_analytics' in data
    
    def test_clone_test(self, client, auth_headers, test_test):
        """Test cloning a test."""
        data = {
            'new_name': 'Cloned Test'
        }
        
        response = client.post(f'/api/tests/{test_test.id}/clone',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Cloned Test'
        assert data['duration_minutes'] == test_test.duration_minutes
    
    def test_test_access_control(self, client, student_headers, test_test):
        """Test that students cannot modify tests."""
        data = {
            'name': 'Student trying to update'
        }
        
        response = client.put(f'/api/tests/{test_test.id}',
                             json=data,
                             headers=student_headers,
                             content_type='application/json')
        
        assert response.status_code == 403
    
    def test_export_test_results(self, client, auth_headers, test_test):
        """Test exporting test results."""
        response = client.get(f'/api/tests/{test_test.id}/export-results',
                             headers=auth_headers)
        
        assert response.status_code == 200
        assert response.content_type == 'text/csv'
    
    def test_bulk_import_questions(self, client, auth_headers, test_test):
        """Test bulk importing questions."""
        csv_data = """question_text,question_type,points,correct_answer,answer_options
"What is 3+3?",multiple_choice,10,"6","3|4|5|6"
"Python is compiled",true_false,5,"false","true|false"
"Explain OOP",essay,20,"",""
"""
        
        response = client.post(f'/api/tests/{test_test.id}/import-questions',
                              data={'file': (csv_data, 'questions.csv')},
                              headers=auth_headers,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['imported'] == 3