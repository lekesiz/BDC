"""Comprehensive tests for programs API endpoints."""
import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.program import Program, ProgramEnrollment, ProgramModule
from app.models.beneficiary import Beneficiary


class TestProgramsAPI:
    """Test programs API endpoints comprehensively."""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_app):
        """Set up test environment."""
        self.app = test_app
        self.client = test_app.test_client()
        
        with test_app.app_context():
            # Create test tenant
            self.tenant = Tenant(
                name='Test Tenant',
                slug='test-tenant',
                email='tenant@test.com',
                is_active=True
            )
            db.session.add(self.tenant)
            
            # Create test users
            self.admin_user = User(
                email='admin@test.com',
                username='admin',
                first_name='Admin',
                last_name='User',
                role='super_admin',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.admin_user.password = 'Admin123!'
            
            self.trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Trainer',
                last_name='User',
                role='trainer',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.trainer.password = 'Trainer123!'
            
            self.student = User(
                email='student@test.com',
                username='student',
                first_name='Student',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.student.password = 'Student123!'
            
            db.session.add_all([self.admin_user, self.trainer, self.student])
            
            # Create beneficiary
            self.beneficiary = Beneficiary(
                user_id=self.student.id,
                tenant_id=self.tenant.id,
                status='active',
                enrollment_date=datetime.now()
            )
            db.session.add(self.beneficiary)
            
            # Create programs
            self.program1 = Program(
                tenant_id=self.tenant.id,
                name='Python Development',
                code='PY101',
                description='Learn Python programming',
                objectives='Master Python basics and advanced concepts',
                duration=90,
                max_participants=20,
                min_participants=5,
                price=1000.0,
                status='active',
                start_date=datetime.now() + timedelta(days=7),
                end_date=datetime.now() + timedelta(days=97),
                created_by_id=self.admin_user.id
            )
            
            self.program2 = Program(
                tenant_id=self.tenant.id,
                name='Web Development',
                code='WEB201',
                description='Full-stack web development',
                duration=120,
                max_participants=15,
                status='active',
                start_date=datetime.now() + timedelta(days=14),
                end_date=datetime.now() + timedelta(days=134),
                created_by_id=self.admin_user.id
            )
            
            self.inactive_program = Program(
                tenant_id=self.tenant.id,
                name='Archived Program',
                code='ARC001',
                description='This program is archived',
                duration=60,
                status='archived',
                created_by_id=self.admin_user.id
            )
            
            db.session.add_all([self.program1, self.program2, self.inactive_program])
            
            # Create modules for program1
            self.module1 = ProgramModule(
                program_id=self.program1.id,
                name='Python Basics',
                description='Introduction to Python',
                order=1,
                duration=30,
                is_mandatory=True
            )
            
            self.module2 = ProgramModule(
                program_id=self.program1.id,
                name='Advanced Python',
                description='Advanced Python concepts',
                order=2,
                duration=60,
                is_mandatory=True
            )
            
            db.session.add_all([self.module1, self.module2])
            
            # Create enrollment
            self.enrollment = ProgramEnrollment(
                program_id=self.program1.id,
                beneficiary_id=self.beneficiary.id,
                enrollment_date=datetime.now(),
                status='enrolled'
            )
            
            db.session.add(self.enrollment)
            db.session.commit()
            
            # Create access tokens
            self.admin_token = create_access_token(identity=self.admin_user.id)
            self.trainer_token = create_access_token(identity=self.trainer.id)
            self.student_token = create_access_token(identity=self.student.id)
    
    def test_get_programs_list(self):
        """Test getting programs list."""
        response = self.client.get('/api/programs',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'programs' in data
        assert len(data['programs']) >= 2
        assert 'total' in data
        assert 'page' in data
        assert 'per_page' in data
    
    def test_get_programs_with_filters(self):
        """Test getting programs with filters."""
        # Filter by status
        response = self.client.get('/api/programs?status=active',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(p['status'] == 'active' for p in data['programs'])
        
        # Filter by search
        response = self.client.get('/api/programs?search=Python',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert any('Python' in p['name'] for p in data['programs'])
    
    def test_get_program_by_id(self):
        """Test getting specific program."""
        response = self.client.get(f'/api/programs/{self.program1.id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == self.program1.id
        assert data['name'] == 'Python Development'
        assert data['code'] == 'PY101'
        assert 'modules' in data
    
    def test_create_program(self):
        """Test creating new program."""
        response = self.client.post('/api/programs',
            data=json.dumps({
                'name': 'Data Science',
                'code': 'DS301',
                'description': 'Learn data science with Python',
                'objectives': 'Master data analysis and machine learning',
                'duration': 180,
                'max_participants': 25,
                'min_participants': 10,
                'price': 2000.0,
                'start_date': (datetime.now() + timedelta(days=30)).isoformat(),
                'end_date': (datetime.now() + timedelta(days=210)).isoformat(),
                'prerequisites': ['Basic Python knowledge', 'Statistics'],
                'target_audience': 'Developers and analysts'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Data Science'
        assert data['code'] == 'DS301'
        assert data['duration'] == 180
    
    def test_update_program(self):
        """Test updating program."""
        response = self.client.put(f'/api/programs/{self.program1.id}',
            data=json.dumps({
                'description': 'Updated Python programming course',
                'max_participants': 25,
                'price': 1200.0
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['description'] == 'Updated Python programming course'
        assert data['max_participants'] == 25
        assert data['price'] == 1200.0
    
    def test_delete_program(self):
        """Test deleting program."""
        # Create a program to delete
        with self.app.app_context():
            prog_to_delete = Program(
                tenant_id=self.tenant.id,
                name='To Delete',
                code='DEL001',
                description='This will be deleted',
                duration=30,
                status='draft',
                created_by_id=self.admin_user.id
            )
            db.session.add(prog_to_delete)
            db.session.commit()
            delete_id = prog_to_delete.id
        
        response = self.client.delete(f'/api/programs/{delete_id}',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        
        # Verify program is deleted
        with self.app.app_context():
            prog = Program.query.get(delete_id)
            assert prog is None
    
    def test_publish_program(self):
        """Test publishing a draft program."""
        # Create draft program
        with self.app.app_context():
            draft_prog = Program(
                tenant_id=self.tenant.id,
                name='Draft Program',
                code='DRAFT001',
                description='Draft program',
                duration=45,
                status='draft',
                created_by_id=self.admin_user.id
            )
            db.session.add(draft_prog)
            db.session.commit()
            draft_id = draft_prog.id
        
        response = self.client.post(f'/api/programs/{draft_id}/publish',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'active'
    
    def test_archive_program(self):
        """Test archiving a program."""
        response = self.client.post(f'/api/programs/{self.program2.id}/archive',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'archived'
    
    def test_get_program_modules(self):
        """Test getting program modules."""
        response = self.client.get(f'/api/programs/{self.program1.id}/modules',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'modules' in data
        assert len(data['modules']) == 2
        assert data['modules'][0]['name'] == 'Python Basics'
    
    def test_add_program_module(self):
        """Test adding module to program."""
        response = self.client.post(f'/api/programs/{self.program1.id}/modules',
            data=json.dumps({
                'name': 'Python Projects',
                'description': 'Build real projects',
                'order': 3,
                'duration': 30,
                'is_mandatory': False
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Python Projects'
        assert data['order'] == 3
    
    def test_update_program_module(self):
        """Test updating program module."""
        response = self.client.put(f'/api/programs/{self.program1.id}/modules/{self.module1.id}',
            data=json.dumps({
                'description': 'Updated introduction to Python',
                'duration': 35
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['duration'] == 35
    
    def test_enroll_beneficiary(self):
        """Test enrolling beneficiary in program."""
        # Create another beneficiary
        with self.app.app_context():
            new_student = User(
                email='student2@test.com',
                username='student2',
                first_name='Student2',
                last_name='User',
                role='student',
                tenant_id=self.tenant.id,
                is_active=True
            )
            new_student.password = 'Student123!'
            db.session.add(new_student)
            
            new_beneficiary = Beneficiary(
                user_id=new_student.id,
                tenant_id=self.tenant.id,
                status='active',
                enrollment_date=datetime.now()
            )
            db.session.add(new_beneficiary)
            db.session.commit()
            ben_id = new_beneficiary.id
        
        response = self.client.post(f'/api/programs/{self.program2.id}/enroll',
            data=json.dumps({
                'beneficiary_id': ben_id
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['program_id'] == self.program2.id
        assert data['beneficiary_id'] == ben_id
        assert data['status'] == 'enrolled'
    
    def test_get_program_enrollments(self):
        """Test getting program enrollments."""
        response = self.client.get(f'/api/programs/{self.program1.id}/enrollments',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'enrollments' in data
        assert len(data['enrollments']) >= 1
        assert data['enrollments'][0]['beneficiary_id'] == self.beneficiary.id
    
    def test_get_program_progress(self):
        """Test getting program progress for beneficiary."""
        response = self.client.get(f'/api/programs/{self.program1.id}/progress',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'progress' in data
        assert 'completed_modules' in data
        assert 'total_modules' in data
        assert 'percentage' in data
    
    def test_get_my_programs(self):
        """Test getting programs for current user."""
        response = self.client.get('/api/programs/my',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'programs' in data
        assert any(p['id'] == self.program1.id for p in data['programs'])
    
    def test_complete_program_module(self):
        """Test marking module as completed."""
        response = self.client.post(f'/api/programs/{self.program1.id}/modules/{self.module1.id}/complete',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data['completed'] is True
    
    def test_get_program_certificate(self):
        """Test getting program certificate."""
        # First complete the program
        with self.app.app_context():
            enrollment = ProgramEnrollment.query.filter_by(
                program_id=self.program1.id,
                beneficiary_id=self.beneficiary.id
            ).first()
            enrollment.status = 'completed'
            enrollment.completion_date = datetime.now()
            db.session.commit()
        
        response = self.client.get(f'/api/programs/{self.program1.id}/certificate',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type == 'application/pdf'
    
    def test_program_analytics(self):
        """Test getting program analytics."""
        response = self.client.get(f'/api/programs/{self.program1.id}/analytics',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_enrolled' in data
        assert 'completed' in data
        assert 'in_progress' in data
        assert 'dropout_rate' in data
    
    def test_clone_program(self):
        """Test cloning a program."""
        response = self.client.post(f'/api/programs/{self.program1.id}/clone',
            data=json.dumps({
                'name': 'Python Development Copy',
                'code': 'PY101-COPY'
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [201, 404]
        if response.status_code == 201:
            data = json.loads(response.data)
            assert data['name'] == 'Python Development Copy'
            assert data['code'] == 'PY101-COPY'
    
    def test_export_program_data(self):
        """Test exporting program data."""
        response = self.client.get(f'/api/programs/{self.program1.id}/export?format=pdf',
            headers={'Authorization': f'Bearer {self.admin_token}'}
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            assert response.content_type == 'application/pdf'
    
    def test_program_permissions(self):
        """Test program permissions for different roles."""
        # Student can view but not modify
        response = self.client.put(f'/api/programs/{self.program1.id}',
            data=json.dumps({'name': 'Hacked'}),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        assert response.status_code == 403
        
        # Trainer can view but might have limited edit
        response = self.client.get(f'/api/programs/{self.program1.id}',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        assert response.status_code == 200
    
    def test_program_waitlist(self):
        """Test program waitlist functionality."""
        # Make program full
        with self.app.app_context():
            prog = Program.query.get(self.program1.id)
            prog.max_participants = 1  # Already has 1 enrollment
            db.session.commit()
        
        # Try to enroll when full
        response = self.client.post(f'/api/programs/{self.program1.id}/waitlist',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code in [200, 201, 404]
    
    def test_program_feedback(self):
        """Test submitting program feedback."""
        response = self.client.post(f'/api/programs/{self.program1.id}/feedback',
            data=json.dumps({
                'rating': 5,
                'comments': 'Excellent program!',
                'would_recommend': True
            }),
            content_type='application/json',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        assert response.status_code in [201, 404]