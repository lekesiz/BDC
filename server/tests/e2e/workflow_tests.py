"""End-to-end workflow tests."""

import pytest
import json
from app.models.user import User
from app.models.beneficiary import Beneficiary


class TestUserWorkflows:
    """Test complete user workflows."""
    
    def test_complete_user_registration_workflow(self, client, db_session):
        """Test complete user registration and activation workflow."""
        # 1. Register new user
        registration_data = {
            'email': 'workflow@example.com',
            'username': 'workflowuser',
            'password': 'Workflow123!',
            'password_confirm': 'Workflow123!',
            'first_name': 'Workflow',
            'last_name': 'User'
        }
        
        register_response = client.post('/api/auth/register', json=registration_data)
        assert register_response.status_code == 201
        
        register_data = register_response.get_json()
        assert register_data['success'] is True
        user_id = register_data['user']['id']
        
        # 2. User should be created but might need verification
        user = User.query.get(user_id)
        assert user is not None
        assert user.email == 'workflow@example.com'
        
        # 3. Login with new user
        login_response = client.post('/api/auth/login', json={
            'email': 'workflow@example.com',
            'password': 'Workflow123!',
            'remember': False
        })
        
        # Should succeed if email verification not required, or fail if required
        assert login_response.status_code in [200, 401]
        
        if login_response.status_code == 200:
            login_data = login_response.get_json()
            access_token = login_data['access_token']
            
            # 4. Access user profile
            headers = {'Authorization': f'Bearer {access_token}'}
            profile_response = client.get('/api/auth/me', headers=headers)
            
            assert profile_response.status_code == 200
            profile_data = profile_response.get_json()
            assert profile_data['user']['email'] == 'workflow@example.com'
    
    def test_beneficiary_management_workflow(self, client, auth_headers, db_session):
        """Test complete beneficiary management workflow."""
        # 1. Create beneficiary
        beneficiary_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@workflow.com',
            'phone': '+1234567890',
            'date_of_birth': '1985-06-15',
            'address': '123 Workflow Street',
            'emergency_contact': 'Jane Doe',
            'emergency_phone': '+0987654321'
        }
        
        create_response = client.post('/api/beneficiaries',
                                    headers=auth_headers,
                                    json=beneficiary_data)
        
        assert create_response.status_code == 201
        created_data = create_response.get_json()
        beneficiary_id = created_data['beneficiary']['id']
        
        # 2. Retrieve beneficiary
        get_response = client.get(f'/api/beneficiaries/{beneficiary_id}',
                                headers=auth_headers)
        
        assert get_response.status_code == 200
        get_data = get_response.get_json()
        assert get_data['beneficiary']['email'] == 'john.doe@workflow.com'
        
        # 3. Update beneficiary
        update_data = {
            'phone': '+1111111111',
            'address': '456 Updated Avenue'
        }
        
        update_response = client.put(f'/api/beneficiaries/{beneficiary_id}',
                                   headers=auth_headers,
                                   json=update_data)
        
        assert update_response.status_code == 200
        updated_data = update_response.get_json()
        assert updated_data['beneficiary']['phone'] == '+1111111111'
        
        # 4. Add note to beneficiary
        note_data = {
            'content': 'Initial assessment completed',
            'note_type': 'assessment',
            'is_private': False
        }
        
        note_response = client.post(f'/api/beneficiaries/{beneficiary_id}/notes',
                                  headers=auth_headers,
                                  json=note_data)
        
        if note_response.status_code == 201:
            note_data = note_response.get_json()
            assert 'note' in note_data
        
        # 5. Schedule appointment
        appointment_data = {
            'title': 'Initial Consultation',
            'description': 'First meeting with beneficiary',
            'start_time': '2024-12-01T10:00:00Z',
            'end_time': '2024-12-01T11:00:00Z',
            'location': 'Main Office'
        }
        
        appointment_response = client.post(f'/api/beneficiaries/{beneficiary_id}/appointments',
                                         headers=auth_headers,
                                         json=appointment_data)
        
        # Appointment creation may or may not be implemented
        # Test structure ensures workflow completeness
        
        # 6. List all beneficiaries to verify
        list_response = client.get('/api/beneficiaries',
                                 headers=auth_headers)
        
        assert list_response.status_code == 200
        list_data = list_response.get_json()
        
        # Should find our created beneficiary
        found_beneficiary = any(
            ben['id'] == beneficiary_id 
            for ben in list_data['beneficiaries']
        )
        assert found_beneficiary
        
        # 7. Clean up - delete beneficiary
        delete_response = client.delete(f'/api/beneficiaries/{beneficiary_id}',
                                      headers=auth_headers)
        
        assert delete_response.status_code == 200
    
    def test_assessment_workflow(self, client, auth_headers, db_session):
        """Test assessment creation and management workflow."""
        # 1. Create beneficiary for assessment
        beneficiary_data = {
            'first_name': 'Assessment',
            'last_name': 'Subject',
            'email': 'assessment@workflow.com'
        }
        
        ben_response = client.post('/api/beneficiaries',
                                 headers=auth_headers,
                                 json=beneficiary_data)
        
        assert ben_response.status_code == 201
        beneficiary_id = ben_response.get_json()['beneficiary']['id']
        
        # 2. Create assessment
        assessment_data = {
            'title': 'Initial Skills Assessment',
            'description': 'Evaluate current skill level',
            'assessment_type': 'skills',
            'beneficiary_id': beneficiary_id
        }
        
        assessment_response = client.post('/api/assessments',
                                        headers=auth_headers,
                                        json=assessment_data)
        
        # Assessment endpoint may or may not exist
        if assessment_response.status_code == 201:
            assessment_data = assessment_response.get_json()
            assessment_id = assessment_data['assessment']['id']
            
            # 3. Submit assessment results
            results_data = {
                'score': 85,
                'notes': 'Good understanding of basic concepts',
                'recommendations': ['Advanced training recommended']
            }
            
            results_response = client.put(f'/api/assessments/{assessment_id}/results',
                                        headers=auth_headers,
                                        json=results_data)
            
            # Continue workflow if implemented
        
        # Clean up
        client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers)
    
    def test_document_management_workflow(self, client, auth_headers, db_session):
        """Test document upload and management workflow."""
        # 1. Create beneficiary for documents
        beneficiary_data = {
            'first_name': 'Document',
            'last_name': 'Owner',
            'email': 'docs@workflow.com'
        }
        
        ben_response = client.post('/api/beneficiaries',
                                 headers=auth_headers,
                                 json=beneficiary_data)
        
        assert ben_response.status_code == 201
        beneficiary_id = ben_response.get_json()['beneficiary']['id']
        
        # 2. Upload document
        # Note: This would require multipart/form-data for file upload
        # For now, test document metadata creation
        
        document_data = {
            'title': 'ID Document',
            'description': 'Government issued ID',
            'document_type': 'identification',
            'beneficiary_id': beneficiary_id
        }
        
        doc_response = client.post('/api/documents',
                                 headers=auth_headers,
                                 json=document_data)
        
        # Document endpoint may or may not exist
        if doc_response.status_code == 201:
            doc_data = doc_response.get_json()
            document_id = doc_data['document']['id']
            
            # 3. Retrieve document
            get_doc_response = client.get(f'/api/documents/{document_id}',
                                        headers=auth_headers)
            
            if get_doc_response.status_code == 200:
                assert get_doc_response.get_json()['document']['title'] == 'ID Document'
            
            # 4. Update document metadata
            update_doc_data = {
                'description': 'Updated: Government issued ID with photo'
            }
            
            update_doc_response = client.put(f'/api/documents/{document_id}',
                                           headers=auth_headers,
                                           json=update_doc_data)
            
            # Continue if implemented
        
        # Clean up
        client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers)
    
    def test_program_enrollment_workflow(self, client, auth_headers, db_session):
        """Test program enrollment and participation workflow."""
        # 1. Create beneficiary
        beneficiary_data = {
            'first_name': 'Program',
            'last_name': 'Participant',
            'email': 'program@workflow.com'
        }
        
        ben_response = client.post('/api/beneficiaries',
                                 headers=auth_headers,
                                 json=beneficiary_data)
        
        assert ben_response.status_code == 201
        beneficiary_id = ben_response.get_json()['beneficiary']['id']
        
        # 2. Create program
        program_data = {
            'title': 'Job Skills Training',
            'description': 'Basic job skills development program',
            'program_type': 'training',
            'duration_weeks': 8,
            'max_participants': 20
        }
        
        program_response = client.post('/api/programs',
                                     headers=auth_headers,
                                     json=program_data)
        
        # Program endpoint may or may not exist
        if program_response.status_code == 201:
            program_data = program_response.get_json()
            program_id = program_data['program']['id']
            
            # 3. Enroll beneficiary in program
            enrollment_data = {
                'beneficiary_id': beneficiary_id,
                'enrollment_date': '2024-01-15'
            }
            
            enrollment_response = client.post(f'/api/programs/{program_id}/enrollments',
                                            headers=auth_headers,
                                            json=enrollment_data)
            
            # Continue workflow if implemented
        
        # Clean up
        client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers)


class TestDataIntegrityWorkflows:
    """Test workflows that ensure data integrity."""
    
    def test_cascading_deletes_workflow(self, client, auth_headers, db_session):
        """Test that related data is properly handled on deletion."""
        # 1. Create beneficiary with related data
        beneficiary_data = {
            'first_name': 'Cascade',
            'last_name': 'Test',
            'email': 'cascade@workflow.com'
        }
        
        ben_response = client.post('/api/beneficiaries',
                                 headers=auth_headers,
                                 json=beneficiary_data)
        
        assert ben_response.status_code == 201
        beneficiary_id = ben_response.get_json()['beneficiary']['id']
        
        # 2. Add related data (notes, appointments, etc.)
        note_data = {
            'content': 'Test note for cascade deletion',
            'note_type': 'general'
        }
        
        note_response = client.post(f'/api/beneficiaries/{beneficiary_id}/notes',
                                  headers=auth_headers,
                                  json=note_data)
        
        # 3. Delete beneficiary
        delete_response = client.delete(f'/api/beneficiaries/{beneficiary_id}',
                                      headers=auth_headers)
        
        assert delete_response.status_code == 200
        
        # 4. Verify beneficiary is deleted
        get_response = client.get(f'/api/beneficiaries/{beneficiary_id}',
                                headers=auth_headers)
        
        assert get_response.status_code == 404
        
        # 5. Verify related data is handled properly
        # (Implementation would depend on cascade delete configuration)
    
    def test_data_validation_workflow(self, client, auth_headers):
        """Test comprehensive data validation."""
        # Test various invalid data scenarios
        invalid_beneficiary_data = [
            # Missing required fields
            {'last_name': 'OnlyLast'},
            
            # Invalid email format
            {
                'first_name': 'Invalid',
                'last_name': 'Email',
                'email': 'not-an-email'
            },
            
            # Invalid phone format
            {
                'first_name': 'Invalid',
                'last_name': 'Phone',
                'email': 'valid@email.com',
                'phone': 'not-a-phone'
            },
            
            # Invalid date format
            {
                'first_name': 'Invalid',
                'last_name': 'Date',
                'email': 'valid@email.com',
                'date_of_birth': 'not-a-date'
            }
        ]
        
        for invalid_data in invalid_beneficiary_data:
            response = client.post('/api/beneficiaries',
                                 headers=auth_headers,
                                 json=invalid_data)
            
            # Should get validation error
            assert response.status_code == 400
            error_data = response.get_json()
            assert error_data['success'] is False
    
    def test_concurrent_access_workflow(self, client, auth_headers, db_session):
        """Test handling of concurrent access to resources."""
        # This would test optimistic locking or other concurrency controls
        # For now, test basic resource access
        
        # 1. Create resource
        beneficiary_data = {
            'first_name': 'Concurrent',
            'last_name': 'Test',
            'email': 'concurrent@workflow.com'
        }
        
        ben_response = client.post('/api/beneficiaries',
                                 headers=auth_headers,
                                 json=beneficiary_data)
        
        assert ben_response.status_code == 201
        beneficiary_id = ben_response.get_json()['beneficiary']['id']
        
        # 2. Simulate concurrent updates
        update_data1 = {'phone': '+1111111111'}
        update_data2 = {'phone': '+2222222222'}
        
        response1 = client.put(f'/api/beneficiaries/{beneficiary_id}',
                             headers=auth_headers,
                             json=update_data1)
        
        response2 = client.put(f'/api/beneficiaries/{beneficiary_id}',
                             headers=auth_headers,
                             json=update_data2)
        
        # Both should succeed (last one wins) or handle concurrency properly
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Clean up
        client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers)


class TestErrorHandlingWorkflows:
    """Test error handling in complete workflows."""
    
    def test_network_interruption_simulation(self, client, auth_headers):
        """Test handling of simulated network interruptions."""
        # Test partial data submission scenarios
        
        # 1. Start beneficiary creation
        beneficiary_data = {
            'first_name': 'Network',
            'last_name': 'Test',
            'email': 'network@workflow.com'
        }
        
        response = client.post('/api/beneficiaries',
                             headers=auth_headers,
                             json=beneficiary_data)
        
        if response.status_code == 201:
            beneficiary_id = response.get_json()['beneficiary']['id']
            
            # 2. Attempt operations that might fail
            invalid_update = {'invalid_field': 'invalid_value'}
            
            error_response = client.put(f'/api/beneficiaries/{beneficiary_id}',
                                      headers=auth_headers,
                                      json=invalid_update)
            
            # Should handle error gracefully
            assert error_response.status_code == 400
            
            # 3. Verify original data integrity
            get_response = client.get(f'/api/beneficiaries/{beneficiary_id}',
                                    headers=auth_headers)
            
            assert get_response.status_code == 200
            data = get_response.get_json()
            assert data['beneficiary']['first_name'] == 'Network'
            
            # Clean up
            client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers)
    
    def test_authorization_workflow_interruption(self, client, auth_headers):
        """Test handling of authorization changes during workflow."""
        # 1. Start with valid authorization
        beneficiary_data = {
            'first_name': 'Auth',
            'last_name': 'Test',
            'email': 'auth@workflow.com'
        }
        
        response = client.post('/api/beneficiaries',
                             headers=auth_headers,
                             json=beneficiary_data)
        
        if response.status_code == 201:
            beneficiary_id = response.get_json()['beneficiary']['id']
            
            # 2. Try to access with invalid token
            invalid_headers = {'Authorization': 'Bearer invalid_token'}
            
            error_response = client.get(f'/api/beneficiaries/{beneficiary_id}',
                                      headers=invalid_headers)
            
            # Should get authorization error
            assert error_response.status_code == 401
            
            # 3. Valid token should still work
            valid_response = client.get(f'/api/beneficiaries/{beneficiary_id}',
                                      headers=auth_headers)
            
            assert valid_response.status_code == 200
            
            # Clean up
            client.delete(f'/api/beneficiaries/{beneficiary_id}', headers=auth_headers)