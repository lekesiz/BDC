"""Tests for assessment templates API endpoints."""

import pytest
from app.models.assessment import AssessmentTemplate, AssessmentSection, AssessmentQuestion


class TestAssessmentTemplatesAPI:
    """Test assessment templates API endpoints."""
    
    def test_get_empty_templates(self, client, trainer_headers):
        """Test getting templates when none exist."""
        response = client.get('/api/assessment/templates', headers=trainer_headers)
        assert response.status_code == 200
        assert response.json['templates'] == []
        assert response.json['total'] == 0
    
    def test_create_assessment_template(self, client, trainer_headers):
        """Test creating a new assessment template."""
        data = {
            'title': 'Leadership Assessment',
            'description': 'Evaluate leadership skills',
            'category': 'soft_skills',
            'duration_minutes': 60,
            'max_score': 100,
            'is_active': True,
            'sections': [
                {
                    'title': 'Communication Skills',
                    'description': 'Assess communication abilities',
                    'order': 1,
                    'questions': [
                        {
                            'text': 'How do you handle team conflicts?',
                            'type': 'text',
                            'max_score': 10,
                            'order': 1,
                            'required': True
                        },
                        {
                            'text': 'Rate your public speaking skills',
                            'type': 'rating',
                            'max_score': 5,
                            'order': 2,
                            'options': ['1', '2', '3', '4', '5']
                        }
                    ]
                },
                {
                    'title': 'Problem Solving',
                    'description': 'Evaluate problem-solving abilities',
                    'order': 2,
                    'questions': [
                        {
                            'text': 'Describe a challenging problem you solved',
                            'type': 'text',
                            'max_score': 15,
                            'order': 1
                        }
                    ]
                }
            ]
        }
        
        response = client.post('/api/assessment/templates', json=data, headers=trainer_headers)
        assert response.status_code == 201
        assert response.json['title'] == 'Leadership Assessment'
        assert len(response.json['sections']) == 2
        assert len(response.json['sections'][0]['questions']) == 2
    
    def test_create_template_without_auth(self, client):
        """Test creating template without authentication."""
        data = {'title': 'Test Template'}
        response = client.post('/api/assessment/templates', json=data)
        assert response.status_code == 401
    
    def test_student_cannot_create_template(self, client, student_headers):
        """Test that students cannot create templates."""
        data = {'title': 'Unauthorized Template'}
        response = client.post('/api/assessment/templates', json=data, headers=student_headers)
        assert response.status_code == 403
    
    def test_get_template_by_id(self, client, trainer_headers, test_trainer, db_session):
        """Test retrieving a specific template."""
        # Create a template first
        template = AssessmentTemplate(
            title='Test Template',
            description='Test description',
            created_by=test_trainer.id,
            tenant_id=test_trainer.tenant_id,
            max_score=50
        )
        db_session.add(template)
        db_session.commit()
        template_id = template.id
        
        response = client.get(f'/api/assessment/templates/{template_id}', headers=trainer_headers)
        assert response.status_code == 200
        assert response.json['title'] == 'Test Template'
    
    def test_update_template(self, client, trainer_headers, test_trainer, db_session):
        """Test updating an assessment template."""
        # Create a template first
        template = AssessmentTemplate(
            title='Old Title',
            description='Old description',
            created_by=test_trainer.id,
            tenant_id=test_trainer.tenant_id
        )
        db_session.add(template)
        db_session.commit()
        template_id = template.id
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'duration_minutes': 90,
            'is_active': False
        }
        
        response = client.put(
            f'/api/assessment/templates/{template_id}',
            json=update_data,
            headers=trainer_headers
        )
        assert response.status_code == 200
        assert response.json['title'] == 'Updated Title'
        assert response.json['is_active'] is False
    
    def test_delete_template(self, client, trainer_headers, test_trainer, db_session):
        """Test deleting an assessment template."""
        template = AssessmentTemplate(
            title='To Delete',
            description='Will be deleted',
            created_by=test_trainer.id,
            tenant_id=test_trainer.tenant_id
        )
        db_session.add(template)
        db_session.commit()
        template_id = template.id
        
        response = client.delete(
            f'/api/assessment/templates/{template_id}',
            headers=trainer_headers
        )
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(
            f'/api/assessment/templates/{template_id}',
            headers=trainer_headers
        )
        assert response.status_code == 404
    
    def test_duplicate_template(self, client, trainer_headers, test_trainer, db_session):
        """Test duplicating an assessment template."""
        # Create a template with sections and questions
        template = AssessmentTemplate(
            title='Original Template',
            description='To be duplicated',
            created_by=test_trainer.id,
            tenant_id=test_trainer.tenant_id
        )
        db_session.add(template)
        db_session.flush()
        
        section = AssessmentSection(
            template_id=template.id,
            title='Section 1',
            order=1
        )
        db_session.add(section)
        db_session.flush()
        
        question = AssessmentQuestion(
            section_id=section.id,
            text='Question 1',
            type='text',
            max_score=10,
            order=1
        )
        db_session.add(question)
        db_session.commit()
        template_id = template.id
        
        response = client.post(
            f'/api/assessment/templates/{template_id}/duplicate',
            headers=trainer_headers
        )
        assert response.status_code == 201
        assert 'Copy' in response.json['title']
        assert response.json['title'] != 'Original Template'
    
    def test_filter_templates_by_category(self, client, trainer_headers, test_trainer, db_session):
        """Test filtering templates by category."""
        # Create templates with different categories
        template1 = AssessmentTemplate(
            title='Technical Assessment',
            category='technical',
            created_by=test_trainer.id,
            tenant_id=test_trainer.tenant_id
        )
        template2 = AssessmentTemplate(
            title='Soft Skills Assessment',
            category='soft_skills',
            created_by=test_trainer.id,
            tenant_id=test_trainer.tenant_id
        )
        db_session.add_all([template1, template2])
        db_session.commit()
        
        response = client.get(
            '/api/assessment/templates?category=technical',
            headers=trainer_headers
        )
        assert response.status_code == 200
        assert response.json['total'] == 1
        assert response.json['templates'][0]['category'] == 'technical'