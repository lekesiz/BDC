"""Tests for assessment templates API endpoints."""

import pytest
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models.user import User
from app.models.assessment import AssessmentTemplate, AssessmentSection, AssessmentQuestion


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def trainer_headers(app):
    """Create authentication headers for a trainer user."""
    with app.app_context():
        user = User(
            email='trainer@test.com',
            username='trainer',
            password='password123',
            first_name='Trainer',
            last_name='User',
            role='trainer',
            tenant_id=1
        )
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def student_headers(app):
    """Create authentication headers for a student user."""
    with app.app_context():
        user = User(
            email='student@test.com',
            username='student',
            password='password123',
            first_name='Student',
            last_name='User',
            role='student',
            tenant_id=1
        )
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return {'Authorization': f'Bearer {access_token}'}


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
    
    def test_get_template_by_id(self, client, trainer_headers, app):
        """Test retrieving a specific template."""
        with app.app_context():
            # Create a template first
            template = AssessmentTemplate(
                title='Test Template',
                description='Test description',
                created_by=1,
                tenant_id=1,
                max_score=50
            )
            db.session.add(template)
            db.session.commit()
            template_id = template.id
        
        response = client.get(f'/api/assessment/templates/{template_id}', headers=trainer_headers)
        assert response.status_code == 200
        assert response.json['title'] == 'Test Template'
    
    def test_update_template(self, client, trainer_headers, app):
        """Test updating an assessment template."""
        with app.app_context():
            # Create a template first
            template = AssessmentTemplate(
                title='Old Title',
                description='Old description',
                created_by=1,
                tenant_id=1
            )
            db.session.add(template)
            db.session.commit()
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
    
    def test_delete_template(self, client, trainer_headers, app):
        """Test deleting an assessment template."""
        with app.app_context():
            template = AssessmentTemplate(
                title='To Delete',
                description='Will be deleted',
                created_by=1,
                tenant_id=1
            )
            db.session.add(template)
            db.session.commit()
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
    
    def test_duplicate_template(self, client, trainer_headers, app):
        """Test duplicating an assessment template."""
        with app.app_context():
            # Create a template with sections and questions
            template = AssessmentTemplate(
                title='Original Template',
                description='To be duplicated',
                created_by=1,
                tenant_id=1
            )
            db.session.add(template)
            db.session.flush()
            
            section = AssessmentSection(
                template_id=template.id,
                title='Section 1',
                order=1
            )
            db.session.add(section)
            db.session.flush()
            
            question = AssessmentQuestion(
                section_id=section.id,
                text='Question 1',
                type='text',
                max_score=10,
                order=1
            )
            db.session.add(question)
            db.session.commit()
            template_id = template.id
        
        response = client.post(
            f'/api/assessment/templates/{template_id}/duplicate',
            headers=trainer_headers
        )
        assert response.status_code == 201
        assert 'Copy' in response.json['title']
        assert response.json['title'] != 'Original Template'
    
    def test_filter_templates_by_category(self, client, trainer_headers, app):
        """Test filtering templates by category."""
        with app.app_context():
            # Create templates with different categories
            template1 = AssessmentTemplate(
                title='Technical Assessment',
                category='technical',
                created_by=1,
                tenant_id=1
            )
            template2 = AssessmentTemplate(
                title='Soft Skills Assessment',
                category='soft_skills',
                created_by=1,
                tenant_id=1
            )
            db.session.add_all([template1, template2])
            db.session.commit()
        
        response = client.get(
            '/api/assessment/templates?category=technical',
            headers=trainer_headers
        )
        assert response.status_code == 200
        assert response.json['total'] == 1
        assert response.json['templates'][0]['category'] == 'technical'
    
    def test_search_templates(self, client, trainer_headers, app):
        """Test searching templates by title or description."""
        with app.app_context():
            template = AssessmentTemplate(
                title='Python Programming Assessment',
                description='Test Python knowledge',
                created_by=1,
                tenant_id=1
            )
            db.session.add(template)
            db.session.commit()
        
        response = client.get(
            '/api/assessment/templates?search=python',
            headers=trainer_headers
        )
        assert response.status_code == 200
        assert response.json['total'] >= 1
        assert 'Python' in response.json['templates'][0]['title']
    
    def test_pagination(self, client, trainer_headers, app):
        """Test template pagination."""
        with app.app_context():
            # Create multiple templates
            for i in range(15):
                template = AssessmentTemplate(
                    title=f'Template {i}',
                    created_by=1,
                    tenant_id=1
                )
                db.session.add(template)
            db.session.commit()
        
        # Test first page
        response = client.get(
            '/api/assessment/templates?page=1&per_page=10',
            headers=trainer_headers
        )
        assert response.status_code == 200
        assert len(response.json['templates']) == 10
        assert response.json['total'] == 15
        
        # Test second page
        response = client.get(
            '/api/assessment/templates?page=2&per_page=10',
            headers=trainer_headers
        )
        assert response.status_code == 200
        assert len(response.json['templates']) == 5