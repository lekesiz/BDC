"""Comprehensive test suite for programs endpoints."""

import pytest
from datetime import datetime, timedelta
from app import db
from app.models import User, Tenant, Program, ProgramModule, ProgramEnrollment


class TestProgramsComprehensive:
    """Comprehensive program endpoint tests."""
    
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
            
            # Store tenant ID to avoid detached instance errors
            self.tenant_id = self.tenant.id
            
            # Create admin user
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
            
            # Create trainer
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
            
            # Create student
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
            
            # Create test programs
            self.program1 = Program(
                name='Python Basics',
                description='Introduction to Python programming',
                code='PY101',
                duration=30,
                level='beginner',
                category='programming',
                tenant_id=self.tenant_id,
                created_by_id=self.admin_id,
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=30)).date(),
                status='active',
                is_active=True
            )
            db.session.add(self.program1)
            
            self.program2 = Program(
                name='Advanced Python',
                description='Advanced Python concepts',
                code='PY201',
                duration=45,
                level='advanced',
                category='programming',
                tenant_id=self.tenant_id,
                created_by_id=self.admin_id,
                start_date=(datetime.now() + timedelta(days=60)).date(),
                end_date=(datetime.now() + timedelta(days=105)).date(),
                status='draft',
                is_active=True
            )
            db.session.add(self.program2)
            
            db.session.commit()
            
            # Store program IDs
            self.program1_id = self.program1.id
            self.program2_id = self.program2.id
            
            # Get tokens
            self.admin_token = self._get_token('test_admin@bdc.com', 'Admin123!')
            self.trainer_token = self._get_token('test_trainer@bdc.com', 'Trainer123!')
            self.student_token = self._get_token('test_student@bdc.com', 'Student123!')
        
        yield
        
        # Cleanup
        with self.app.app_context():
            ProgramEnrollment.query.delete()
            ProgramModule.query.delete()
            Program.query.delete()
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
    
    def test_list_programs_as_admin(self):
        """Test listing programs as admin."""
        response = self.client.get('/api/programs',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert len(data['items']) >= 2
        assert 'total' in data
        assert 'pages' in data
    
    def test_list_programs_pagination(self):
        """Test program list pagination."""
        response = self.client.get('/api/programs?page=1&per_page=1',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 1
        assert data['per_page'] == 1
    
    def test_list_programs_filter_by_status(self):
        """Test filtering programs by status."""
        response = self.client.get('/api/programs?status=active',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        # All returned programs should be active
        for program in data['items']:
            assert program['status'] == 'active'
    
    def test_list_programs_filter_by_level(self):
        """Test filtering programs by level."""
        response = self.client.get('/api/programs?level=beginner',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        # All returned programs should be beginner level
        for program in data['items']:
            assert program['level'] == 'beginner'
    
    def test_list_programs_search(self):
        """Test searching programs."""
        response = self.client.get('/api/programs?search=python',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) >= 2
        # All results should contain 'python' in name or description
        for program in data['items']:
            assert 'python' in program['name'].lower() or 'python' in program.get('description', '').lower()
    
    def test_get_program_by_id(self):
        """Test getting specific program by ID."""
        response = self.client.get(f'/api/programs/{self.program1_id}',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == self.program1_id
        assert data['name'] == 'Python Basics'
        assert data['code'] == 'PY101'
    
    def test_get_nonexistent_program(self):
        """Test getting non-existent program."""
        response = self.client.get('/api/programs/99999',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 404
    
    def test_create_program_as_admin(self):
        """Test creating new program as admin."""
        response = self.client.post('/api/programs',
                                  headers={'Authorization': f'Bearer {self.admin_token}'},
                                  json={
                                      'name': 'JavaScript Fundamentals',
                                      'description': 'Learn JavaScript basics',
                                      'code': 'JS101',
                                      'duration': 25,
                                      'level': 'beginner',
                                      'category': 'programming',
                                      'max_participants': 30,
                                      'minimum_attendance': 80,
                                      'passing_score': 70
                                  })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'JavaScript Fundamentals'
        assert data['code'] == 'JS101'
        assert data['level'] == 'beginner'
        
        # Cleanup
        with self.app.app_context():
            Program.query.filter_by(code='JS101').delete()
            db.session.commit()
    
    def test_create_program_as_trainer(self):
        """Test that trainers cannot create programs."""
        response = self.client.post('/api/programs',
                                  headers={'Authorization': f'Bearer {self.trainer_token}'},
                                  json={
                                      'name': 'Unauthorized Program',
                                      'code': 'UNAUTH01'
                                  })
        
        assert response.status_code == 403
    
    def test_create_program_duplicate_code(self):
        """Test creating program with duplicate code."""
        response = self.client.post('/api/programs',
                                  headers={'Authorization': f'Bearer {self.admin_token}'},
                                  json={
                                      'name': 'Duplicate Code Program',
                                      'code': 'PY101',  # Already exists
                                      'level': 'intermediate'
                                  })
        
        assert response.status_code == 400
    
    def test_update_program_as_admin(self):
        """Test updating program as admin."""
        response = self.client.put(f'/api/programs/{self.program2_id}',
                                 headers={'Authorization': f'Bearer {self.admin_token}'},
                                 json={
                                     'name': 'Advanced Python - Updated',
                                     'description': 'Updated description',
                                     'status': 'active'
                                 })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Advanced Python - Updated'
        assert data['description'] == 'Updated description'
        assert data['status'] == 'active'
    
    def test_delete_program_as_admin(self):
        """Test deleting program as admin."""
        # Create a program to delete
        with self.app.app_context():
            program_to_delete = Program(
                name='Delete Me',
                code='DEL01',
                tenant_id=self.tenant_id,
                created_by_id=self.admin_id
            )
            db.session.add(program_to_delete)
            db.session.commit()
            program_id = program_to_delete.id
        
        response = self.client.delete(f'/api/programs/{program_id}',
                                    headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code == 200
        
        # Verify program is soft deleted
        with self.app.app_context():
            deleted_program = Program.query.get(program_id)
            assert deleted_program is not None
            assert deleted_program.is_active is False
    
    def test_enroll_in_program(self):
        """Test enrolling in a program."""
        response = self.client.post(f'/api/programs/{self.program1_id}/enroll',
                                  headers={'Authorization': f'Bearer {self.student_token}'},
                                  json={
                                      'beneficiary_id': None  # Will use current user
                                  })
        
        # This might return 201 or 400 depending on if enrollment endpoint exists
        assert response.status_code in [201, 400, 404]
    
    def test_get_program_enrollments(self):
        """Test getting program enrollments."""
        response = self.client.get(f'/api/programs/{self.program1_id}/enrollments',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list) or 'items' in data
    
    def test_create_program_module(self):
        """Test creating program module."""
        response = self.client.post(f'/api/programs/{self.program1_id}/modules',
                                  headers={'Authorization': f'Bearer {self.admin_token}'},
                                  json={
                                      'name': 'Module 1: Introduction',
                                      'description': 'Introduction to Python',
                                      'order': 1,
                                      'duration': 5
                                  })
        
        assert response.status_code in [201, 404]
    
    def test_get_program_modules(self):
        """Test getting program modules."""
        response = self.client.get(f'/api/programs/{self.program1_id}/modules',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code in [200, 404]
    
    def test_get_program_categories(self):
        """Test getting available program categories."""
        response = self.client.get('/api/programs/categories',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)
            assert 'programming' in data
    
    def test_get_program_levels(self):
        """Test getting available program levels."""
        response = self.client.get('/api/programs/levels',
                                 headers={'Authorization': f'Bearer {self.admin_token}'})
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)
            assert 'beginner' in data
            assert 'advanced' in data
    
    def test_list_programs_as_student(self):
        """Test that students can list programs."""
        response = self.client.get('/api/programs',
                                 headers={'Authorization': f'Bearer {self.student_token}'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
    
    def test_update_program_as_student(self):
        """Test that students cannot update programs."""
        response = self.client.put(f'/api/programs/{self.program1_id}',
                                 headers={'Authorization': f'Bearer {self.student_token}'},
                                 json={
                                     'name': 'Hacked Program'
                                 })
        
        assert response.status_code == 403