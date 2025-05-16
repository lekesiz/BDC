import pytest
import json
from datetime import datetime, timedelta
from models import Program, ProgramBeneficiary

class TestPrograms:
    """Test program endpoints."""
    
    def test_create_program(self, client, auth_headers, test_tenant):
        """Test creating a new program."""
        data = {
            'name': 'Advanced Python Programming',
            'description': 'Learn advanced Python concepts',
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=90)).isoformat(),
            'max_participants': 30,
            'is_active': True
        }
        
        response = client.post('/api/programs',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Advanced Python Programming'
        assert data['max_participants'] == 30
    
    def test_create_program_duplicate_name(self, client, auth_headers, test_program):
        """Test creating a program with duplicate name."""
        data = {
            'name': test_program.name,
            'description': 'Another description',
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post('/api/programs',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'already exists' in data['error']
    
    def test_get_programs(self, client, auth_headers, test_program):
        """Test getting list of programs."""
        response = client.get('/api/programs',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'programs' in data
        assert 'total' in data
        assert len(data['programs']) > 0
    
    def test_get_programs_filtered(self, client, auth_headers, test_program):
        """Test filtering programs by status."""
        response = client.get('/api/programs?is_active=true',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(p['is_active'] for p in data['programs'])
    
    def test_get_program_by_id(self, client, auth_headers, test_program):
        """Test getting a specific program."""
        response = client.get(f'/api/programs/{test_program.id}',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_program.id
        assert data['name'] == test_program.name
    
    def test_update_program(self, client, auth_headers, test_program):
        """Test updating a program."""
        data = {
            'description': 'Updated description',
            'max_participants': 40
        }
        
        response = client.put(f'/api/programs/{test_program.id}',
                             json=data,
                             headers=auth_headers,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['description'] == 'Updated description'
        assert data['max_participants'] == 40
    
    def test_delete_program(self, client, auth_headers, test_program):
        """Test deleting a program."""
        response = client.delete(f'/api/programs/{test_program.id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Program deleted successfully'
    
    def test_assign_beneficiary_to_program(self, client, auth_headers, test_program, test_beneficiary):
        """Test assigning a beneficiary to a program."""
        data = {
            'beneficiary_id': test_beneficiary.id
        }
        
        response = client.post(f'/api/programs/{test_program.id}/beneficiaries',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['program_id'] == test_program.id
        assert data['beneficiary_id'] == test_beneficiary.id
    
    def test_remove_beneficiary_from_program(self, client, auth_headers, test_program, test_beneficiary, db_session):
        """Test removing a beneficiary from a program."""
        # First assign the beneficiary
        assignment = ProgramBeneficiary(
            program_id=test_program.id,
            beneficiary_id=test_beneficiary.id,
            enrolled_date=datetime.now()
        )
        db_session.add(assignment)
        db_session.commit()
        
        response = client.delete(f'/api/programs/{test_program.id}/beneficiaries/{test_beneficiary.id}',
                                headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Beneficiary removed from program'
    
    def test_get_program_beneficiaries(self, client, auth_headers, test_program, test_beneficiary, db_session):
        """Test getting beneficiaries in a program."""
        # Assign beneficiary to program
        assignment = ProgramBeneficiary(
            program_id=test_program.id,
            beneficiary_id=test_beneficiary.id,
            enrolled_date=datetime.now()
        )
        db_session.add(assignment)
        db_session.commit()
        
        response = client.get(f'/api/programs/{test_program.id}/beneficiaries',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'beneficiaries' in data
        assert len(data['beneficiaries']) > 0
        assert data['beneficiaries'][0]['id'] == test_beneficiary.id
    
    def test_get_program_schedule(self, client, auth_headers, test_program):
        """Test getting program schedule."""
        response = client.get(f'/api/programs/{test_program.id}/schedule',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'schedule' in data
        assert isinstance(data['schedule'], list)
    
    def test_create_program_schedule(self, client, auth_headers, test_program):
        """Test creating program schedule."""
        data = {
            'sessions': [
                {
                    'title': 'Introduction',
                    'date': datetime.now().isoformat(),
                    'duration': 120,
                    'location': 'Room A'
                },
                {
                    'title': 'Advanced Topics',
                    'date': (datetime.now() + timedelta(days=7)).isoformat(),
                    'duration': 180,
                    'location': 'Room B'
                }
            ]
        }
        
        response = client.post(f'/api/programs/{test_program.id}/schedule',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['sessions']) == 2
    
    def test_get_program_statistics(self, client, auth_headers, test_program):
        """Test getting program statistics."""
        response = client.get(f'/api/programs/{test_program.id}/statistics',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_beneficiaries' in data
        assert 'attendance_rate' in data
        assert 'completion_rate' in data
    
    def test_get_program_progress(self, client, auth_headers, test_program):
        """Test getting program progress."""
        response = client.get(f'/api/programs/{test_program.id}/progress',
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'overall_progress' in data
        assert 'module_progress' in data
    
    def test_clone_program(self, client, auth_headers, test_program):
        """Test cloning a program."""
        data = {
            'new_name': 'Cloned Program',
            'start_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        response = client.post(f'/api/programs/{test_program.id}/clone',
                              json=data,
                              headers=auth_headers,
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Cloned Program'
        assert data['description'] == test_program.description
    
    def test_export_program_data(self, client, auth_headers, test_program):
        """Test exporting program data."""
        response = client.get(f'/api/programs/{test_program.id}/export',
                             headers=auth_headers)
        
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        data = json.loads(response.data)
        assert 'program' in data
        assert 'beneficiaries' in data
        assert 'schedule' in data
    
    def test_program_access_control(self, client, student_headers, test_program):
        """Test that students cannot modify programs."""
        data = {
            'description': 'Student trying to update'
        }
        
        response = client.put(f'/api/programs/{test_program.id}',
                             json=data,
                             headers=student_headers,
                             content_type='application/json')
        
        assert response.status_code == 403
    
    def test_trainer_can_view_programs(self, client, trainer_headers, test_program):
        """Test that trainers can view programs."""
        response = client.get(f'/api/programs/{test_program.id}',
                             headers=trainer_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == test_program.id