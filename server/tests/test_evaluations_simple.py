"""Simple test suite for evaluations endpoints."""

import pytest
from datetime import datetime, timedelta
from app import db
from app.models import User, Tenant, Evaluation


class TestEvaluationsSimple:
    """Simple evaluation endpoint tests."""
    
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
        assert isinstance(data, (list, dict))
    
    def test_get_evaluation_by_id(self):
        """Test getting specific evaluation by ID."""
        response = self.client.get(f'/api/evaluations/{self.eval1_id}',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == self.eval1_id
        assert data['name'] == 'Python Basics Test'
    
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
        
        # Cleanup
        with self.app.app_context():
            Evaluation.query.filter_by(name='New Assessment').delete()
            db.session.commit()
    
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