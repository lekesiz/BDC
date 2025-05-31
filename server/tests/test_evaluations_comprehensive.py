"""Comprehensive test suite for evaluations endpoints."""

import pytest
from datetime import datetime, timedelta
from app import db
from app.models import User, Tenant, Evaluation, Question, Test


class TestEvaluationsComprehensive:
    """Comprehensive evaluation endpoint tests."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_app, client):
        """Setup for each test."""
        self.app = test_app
        self.client = client
        
        with self.app.app_context():
            # Create test tenant
            self.tenant = Tenant(
                name='Test Tenant',
                slug='test-tenant',
                email='test@tenant.com',
                is_active=True
            )
            db.session.add(self.tenant)
            db.session.commit()
            
            # Store tenant ID
            self.tenant_id = self.tenant.id
            
            # Create users
            self.admin_user = User(
                email='test_admin@bdc.com',
                username='test_admin',
                first_name='Test',
                last_name='Admin',
                role='super_admin',
                is_active=True,
                tenant_id=self.tenant_id
            )
            self.admin_user.password = 'Admin123!'
            db.session.add(self.admin_user)
            
            self.trainer_user = User(
                email='test_trainer@bdc.com',
                username='test_trainer',
                first_name='Test',
                last_name='Trainer',
                role='trainer',
                is_active=True,
                tenant_id=self.tenant_id
            )
            self.trainer_user.password = 'Trainer123!'
            db.session.add(self.trainer_user)
            
            self.student_user = User(
                email='test_student@bdc.com',
                username='test_student',
                first_name='Test',
                last_name='Student',
                role='student',
                is_active=True,
                tenant_id=self.tenant_id
            )
            self.student_user.password = 'Student123!'
            db.session.add(self.student_user)
            
            db.session.commit()
            
            # Store user IDs
            self.admin_id = self.admin_user.id
            self.trainer_id = self.trainer_user.id
            self.student_id = self.student_user.id
            
            # Create test evaluations
            self.evaluation1 = Evaluation(
                name='Python Basics Test',
                description='Test your Python knowledge',
                type='test',
                status='published',
                tenant_id=self.tenant_id,
                created_by=self.trainer_id,
                duration_minutes=60,
                passing_score=70,
                max_attempts=3,
                is_active=True
            )
            db.session.add(self.evaluation1)
            
            self.evaluation2 = Evaluation(
                name='JavaScript Quiz',
                description='Quick JS quiz',
                type='quiz',
                status='draft',
                tenant_id=self.tenant_id,
                created_by=self.trainer_id,
                duration_minutes=30,
                passing_score=80,
                max_attempts=2,
                is_active=True
            )
            db.session.add(self.evaluation2)
            
            db.session.commit()
            
            # Store evaluation IDs
            self.eval1_id = self.evaluation1.id
            self.eval2_id = self.evaluation2.id
            
            # Get tokens
            self.admin_token = self._get_token('test_admin@bdc.com', 'Admin123!')
            self.trainer_token = self._get_token('test_trainer@bdc.com', 'Trainer123!')
            self.student_token = self._get_token('test_student@bdc.com', 'Student123!')
        
        yield
        
        # Cleanup
        with self.app.app_context():
            Question.query.delete()
            Evaluation.query.delete()
            User.query.filter(User.email.like('test_%')).delete()
            Tenant.query.filter_by(slug='test-tenant').delete()
            db.session.commit()
    
    def _get_token(self, email, password):
        """Helper to get auth token."""
        response = self.client.post('/api/auth/login', json={
            'email': email,
            'password': password,
            'remember': False
        })
        return response.get_json()['access_token']
    
    def test_list_evaluations_as_admin(self):
        """Test listing evaluations as admin."""
        response = self.client.get('/api/evaluations',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data or isinstance(data, list)
        if 'items' in data:
            assert len(data['items']) >= 2
        else:
            assert len(data) >= 2
    
    def test_list_evaluations_pagination(self):
        """Test evaluation list pagination."""
        response = self.client.get('/api/evaluations?page=1&limit=1',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        if 'items' in data:
            assert len(data['items']) <= 1
    
    def test_list_evaluations_filter_by_type(self):
        """Test filtering evaluations by type."""
        response = self.client.get('/api/evaluations?type=test',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        items = data.get('items', data) if isinstance(data, dict) else data
        # All returned evaluations should be tests
        for evaluation in items:
            assert evaluation['type'] == 'test'
    
    def test_list_evaluations_filter_by_status(self):
        """Test filtering evaluations by status."""
        response = self.client.get('/api/evaluations?status=published',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        items = data.get('items', data) if isinstance(data, dict) else data
        # All returned evaluations should be published
        for evaluation in items:
            assert evaluation['status'] == 'published'
    
    def test_get_evaluation_by_id(self):
        """Test getting specific evaluation by ID."""
        response = self.client.get(f'/api/evaluations/{self.eval1_id}',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == self.eval1_id
        assert data['name'] == 'Python Basics Test'
        assert data['type'] == 'test'
    
    def test_get_nonexistent_evaluation(self):
        """Test getting non-existent evaluation."""
        response = self.client.get('/api/evaluations/99999',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 404
    
    def test_create_evaluation_as_trainer(self):
        """Test creating new evaluation as trainer."""
        response = self.client.post('/api/evaluations',
                                  headers={'Authorization': f'Bearer {self.trainer_token}'},
                                  json={
                                      'name': 'New Assessment',
                                      'description': 'A new assessment',
                                      'type': 'assessment',
                                      'duration_minutes': 45,
                                      'passing_score': 75,
                                      'max_attempts': 1
                                  })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Assessment'
        assert data['type'] == 'assessment'
        assert data['created_by'] == self.trainer_id
        
        # Cleanup
        with self.app.app_context():
            Evaluation.query.filter_by(name='New Assessment').delete()
            db.session.commit()
    
    def test_create_evaluation_as_student(self):
        """Test that students cannot create evaluations."""
        response = self.client.post('/api/evaluations',
                                  headers={'Authorization': f'Bearer {self.student_token}'},
                                  json={
                                      'name': 'Unauthorized Evaluation',
                                      'type': 'test'
                                  })
        
        assert response.status_code == 403
    
    def test_update_evaluation_as_trainer(self):
        """Test updating evaluation as trainer (owner)."""
        response = self.client.patch(f'/api/evaluations/{self.eval2_id}',
                                   headers={'Authorization': f'Bearer {self.trainer_token}'},
                                   json={
                                       'name': 'JavaScript Quiz - Updated',
                                       'status': 'published'
                                   })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'JavaScript Quiz - Updated'
        assert data['status'] == 'published'
    
    def test_update_evaluation_as_other_trainer(self):
        """Test that trainers cannot update other trainers' evaluations."""
        # Create another trainer
        with self.app.app_context():
            other_trainer = User(
                email='other_trainer@bdc.com',
                username='other_trainer',
                first_name='Other',
                last_name='Trainer',
                role='trainer',
                tenant_id=self.tenant_id
            )
            other_trainer.password = 'OtherTrainer123!'
            db.session.add(other_trainer)
            db.session.commit()
        
        other_token = self._get_token('other_trainer@bdc.com', 'OtherTrainer123!')
        
        response = self.client.patch(f'/api/evaluations/{self.eval1_id}',
                                   headers={'Authorization': f'Bearer {other_token}'},
                                   json={
                                       'name': 'Hacked Evaluation'
                                   })
        
        assert response.status_code == 403
        
        # Cleanup
        with self.app.app_context():
            User.query.filter_by(email='other_trainer@bdc.com').delete()
            db.session.commit()
    
    def test_delete_evaluation_as_admin(self):
        """Test deleting evaluation as admin."""
        # Create an evaluation to delete
        with self.app.app_context():
            eval_to_delete = Evaluation(
                name='Delete Me',
                type='test',
                tenant_id=self.tenant_id,
                created_by=self.trainer_id
            )
            db.session.add(eval_to_delete)
            db.session.commit()
            eval_id = eval_to_delete.id
        
        response = self.client.delete(f'/api/evaluations/{eval_id}',
                                    headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        
        # Verify evaluation is soft deleted
        with self.app.app_context():
            deleted_eval = Evaluation.query.get(eval_id)
            assert deleted_eval is not None
            assert deleted_eval.is_active is False
    
    def test_create_evaluation_question(self):
        """Test creating evaluation question."""
        response = self.client.post(f'/api/evaluations/{self.eval1_id}/questions',
                                  headers={'Authorization': f'Bearer {self.trainer_token}'},
                                  json={
                                      'text': 'What is Python?',
                                      'type': 'multiple_choice',
                                      'points': 10,
                                      'options': [
                                          'A snake',
                                          'A programming language',
                                          'A food',
                                          'A movie'
                                      ],
                                      'correct_answer': 'A programming language'
                                  })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['text'] == 'What is Python?'
        assert data['type'] == 'multiple_choice'
        assert data['points'] == 10
    
    def test_get_evaluation_questions(self):
        """Test getting evaluation questions."""
        # First create a question
        with self.app.app_context():
            question = Question(
                test_set_id=self.eval1_id,
                text='Test question?',
                type='true_false',
                points=5,
                correct_answer='true'
            )
            db.session.add(question)
            db.session.commit()
        
        response = self.client.get(f'/api/evaluations/{self.eval1_id}/questions',
                                 headers={'Authorization': f'Bearer {self.trainer_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) >= 1
        assert any(q['text'] == 'Test question?' for q in data)
    
    def test_update_evaluation_question(self):
        """Test updating evaluation question."""
        # First create a question
        with self.app.app_context():
            question = Question(
                test_set_id=self.eval1_id,
                text='Original question?',
                type='short_answer',
                points=15
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        response = self.client.patch(f'/api/evaluations/questions/{question_id}',
                                   headers={'Authorization': f'Bearer {self.trainer_token}'},
                                   json={
                                       'text': 'Updated question?',
                                       'points': 20
                                   })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['text'] == 'Updated question?'
        assert data['points'] == 20
    
    def test_delete_evaluation_question(self):
        """Test deleting evaluation question."""
        # First create a question
        with self.app.app_context():
            question = Question(
                test_set_id=self.eval1_id,
                text='Delete me?',
                type='true_false',
                points=5
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        response = self.client.delete(f'/api/evaluations/questions/{question_id}',
                                    headers={'Authorization': f'Bearer {self.trainer_token}'})
        
        assert response.status_code == 200
        
        # Verify question is deleted
        with self.app.app_context():
            deleted_question = Question.query.get(question_id)
            assert deleted_question is None
    
    def test_list_evaluations_as_student(self):
        """Test that students can list published evaluations."""
        response = self.client.get('/api/evaluations',
                                 headers={'Authorization': f'Bearer {self.student_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        items = data.get('items', data) if isinstance(data, dict) else data
        # Students should only see published evaluations
        for evaluation in items:
            assert evaluation['status'] == 'published'