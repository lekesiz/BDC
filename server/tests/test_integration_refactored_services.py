"""Integration tests for refactored services."""

import pytest
from datetime import datetime, timedelta, timezone
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token

from app import create_app, db
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.test import TestSet, Question, TestSession, Response
from app.models.appointment import Appointment
from app.services.appointment_service_refactored import AppointmentServiceRefactored
from app.services.evaluation_service_refactored import (
    EvaluationServiceRefactored,
    EvaluationType,
    EvaluationStatus
)


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    
    # Override config for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    """Create authentication headers."""
    with app.app_context():
        # Create test user
        user = User(
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='trainer'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }, user


@pytest.fixture
def sample_trainer(app):
    """Create a sample trainer."""
    with app.app_context():
        trainer = User(
            email='trainer@example.com',
            first_name='John',
            last_name='Trainer',
            role='trainer'
        )
        trainer.set_password('password123')
        db.session.add(trainer)
        db.session.commit()
        return trainer


@pytest.fixture
def sample_student(app):
    """Create a sample student with beneficiary."""
    with app.app_context():
        student = User(
            email='student@example.com',
            first_name='Jane',
            last_name='Student',
            role='student'
        )
        student.set_password('password123')
        db.session.add(student)
        db.session.flush()
        
        # Create beneficiary profile
        beneficiary = Beneficiary(
            user_id=student.id,
            trainer_id=None,
            date_of_birth=datetime(2000, 1, 1).date(),
            phone_number='1234567890'
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        return student, beneficiary


class TestAppointmentServiceIntegration:
    """Integration tests for AppointmentService."""
    
    def test_create_and_retrieve_appointment(self, app, sample_trainer, sample_student):
        """Test creating and retrieving an appointment."""
        with app.app_context():
            service = AppointmentServiceRefactored(db.session)
            student, beneficiary = sample_student
            
            # Assign beneficiary to trainer
            beneficiary.trainer_id = sample_trainer.id
            db.session.commit()
            
            # Create appointment
            appointment_data = {
                'title': 'Training Session',
                'description': 'Initial assessment',
                'location': 'Room 101',
                'start_time': (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                'end_time': (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
                'beneficiary_id': beneficiary.id
            }
            
            result = service.create_appointment(
                trainer_id=sample_trainer.id,
                appointment_data=appointment_data
            )
            
            # Verify creation
            assert result['title'] == 'Training Session'
            assert 'id' in result
            
            # Retrieve appointments
            appointments = service.get_appointments_for_user(
                user_id=sample_trainer.id
            )
            
            assert appointments['total'] == 1
            assert appointments['appointments'][0]['title'] == 'Training Session'
    
    def test_update_appointment(self, app, sample_trainer, sample_student):
        """Test updating an appointment."""
        with app.app_context():
            service = AppointmentServiceRefactored(db.session)
            student, beneficiary = sample_student
            
            # Create appointment first
            beneficiary.trainer_id = sample_trainer.id
            db.session.commit()
            
            appointment = Appointment(
                title='Original Title',
                start_time=datetime.now(timezone.utc) + timedelta(hours=1),
                end_time=datetime.now(timezone.utc) + timedelta(hours=2),
                trainer_id=sample_trainer.id,
                beneficiary_id=beneficiary.id,
                status='scheduled'
            )
            db.session.add(appointment)
            db.session.commit()
            
            # Update appointment
            update_data = {
                'title': 'Updated Title',
                'status': 'completed'
            }
            
            result = service.update_appointment(
                appointment_id=appointment.id,
                user_id=sample_trainer.id,
                update_data=update_data
            )
            
            assert result['title'] == 'Updated Title'
            assert result['status'] == 'completed'
    
    def test_delete_appointment(self, app, sample_trainer, sample_student):
        """Test deleting an appointment."""
        with app.app_context():
            service = AppointmentServiceRefactored(db.session)
            student, beneficiary = sample_student
            
            # Create appointment
            beneficiary.trainer_id = sample_trainer.id
            db.session.commit()
            
            appointment = Appointment(
                title='To Delete',
                start_time=datetime.now(timezone.utc) + timedelta(hours=1),
                end_time=datetime.now(timezone.utc) + timedelta(hours=2),
                trainer_id=sample_trainer.id,
                beneficiary_id=beneficiary.id,
                status='scheduled'
            )
            db.session.add(appointment)
            db.session.commit()
            appointment_id = appointment.id
            
            # Delete appointment
            result = service.delete_appointment(
                appointment_id=appointment_id,
                user_id=sample_trainer.id
            )
            
            assert result['message'] == 'Appointment deleted successfully'
            
            # Verify deletion
            deleted = db.session.query(Appointment).filter_by(id=appointment_id).first()
            assert deleted is None


class TestEvaluationServiceIntegration:
    """Integration tests for EvaluationService."""
    
    def test_create_evaluation_with_questions(self, app, sample_trainer):
        """Test creating an evaluation with questions."""
        with app.app_context():
            service = EvaluationServiceRefactored(db.session)
            
            # Create evaluation data
            evaluation_data = {
                'title': 'Math Assessment',
                'type': EvaluationType.ASSESSMENT.value,
                'tenant_id': 1,
                'description': 'Basic math skills assessment',
                'passing_score': 70,
                'questions': [
                    {
                        'text': 'What is 2 + 2?',
                        'type': 'multiple_choice',
                        'options': ['3', '4', '5', '6'],
                        'correct_answer': '4',
                        'points': 10
                    },
                    {
                        'text': 'What is 5 * 3?',
                        'type': 'multiple_choice',
                        'options': ['10', '15', '20', '25'],
                        'correct_answer': '15',
                        'points': 10
                    }
                ]
            }
            
            result = service.create_evaluation(
                creator_id=sample_trainer.id,
                data=evaluation_data
            )
            
            # Verify creation
            assert result.title == 'Math Assessment'
            assert result.id is not None
            
            # Verify questions
            questions = db.session.query(Question).filter_by(
                test_set_id=result.id
            ).all()
            
            assert len(questions) == 2
            assert questions[0].text == 'What is 2 + 2?'
            assert questions[1].text == 'What is 5 * 3?'
    
    def test_create_and_complete_test_session(self, app, sample_trainer, sample_student):
        """Test creating and completing a test session."""
        with app.app_context():
            service = EvaluationServiceRefactored(db.session)
            student, beneficiary = sample_student
            
            # Create evaluation
            evaluation = TestSet(
                title='Test Evaluation',
                type=EvaluationType.QUIZ.value,
                status=EvaluationStatus.PUBLISHED.value,
                creator_id=sample_trainer.id,
                tenant_id=1
            )
            db.session.add(evaluation)
            db.session.flush()
            
            # Add questions
            question1 = Question(
                test_set_id=evaluation.id,
                text='Question 1',
                type='multiple_choice',
                options=['A', 'B', 'C'],
                correct_answer='A',
                points=50
            )
            question2 = Question(
                test_set_id=evaluation.id,
                text='Question 2',
                type='multiple_choice',
                options=['X', 'Y', 'Z'],
                correct_answer='Y',
                points=50
            )
            db.session.add_all([question1, question2])
            db.session.commit()
            
            # Create test session
            session = service.create_test_session(
                user_id=student.id,
                evaluation_id=evaluation.id
            )
            
            assert session.status == 'in_progress'
            
            # Submit responses
            response1 = service.submit_response(
                session_id=session.id,
                question_id=question1.id,
                user_id=student.id,
                response_data={'answer': 'A'}  # Correct
            )
            
            response2 = service.submit_response(
                session_id=session.id,
                question_id=question2.id,
                user_id=student.id,
                response_data={'answer': 'X'}  # Wrong
            )
            
            # Complete session
            completed_session = service.complete_session(
                session_id=session.id,
                user_id=student.id
            )
            
            assert completed_session.status == 'completed'
            assert completed_session.score == 50  # Only first question correct
            assert completed_session.total_score == 100
    
    def test_evaluation_deletion_cascade(self, app, sample_trainer, sample_student):
        """Test that deleting an evaluation cascades properly."""
        with app.app_context():
            service = EvaluationServiceRefactored(db.session)
            student, beneficiary = sample_student
            
            # Create evaluation with questions
            evaluation_data = {
                'title': 'To Delete',
                'type': EvaluationType.EXAM.value,
                'tenant_id': 1,
                'questions': [
                    {
                        'text': 'Question to delete',
                        'type': 'text',
                        'points': 100
                    }
                ]
            }
            
            evaluation = service.create_evaluation(
                creator_id=sample_trainer.id,
                data=evaluation_data
            )
            evaluation_id = evaluation.id
            
            # Create a session
            session = TestSession(
                test_set_id=evaluation_id,
                beneficiary_id=beneficiary.id,
                status='completed'
            )
            db.session.add(session)
            db.session.commit()
            
            # Delete evaluation
            result = service.delete_evaluation(
                evaluation_id=evaluation_id,
                user_id=sample_trainer.id
            )
            
            # Verify cascade deletion
            assert db.session.query(TestSet).filter_by(id=evaluation_id).first() is None
            assert db.session.query(Question).filter_by(test_set_id=evaluation_id).first() is None
            assert db.session.query(TestSession).filter_by(test_set_id=evaluation_id).first() is None


class TestServiceInteraction:
    """Test interaction between different services."""
    
    def test_appointment_and_evaluation_workflow(self, app, sample_trainer, sample_student):
        """Test a complete workflow using both services."""
        with app.app_context():
            appointment_service = AppointmentServiceRefactored(db.session)
            evaluation_service = EvaluationServiceRefactored(db.session)
            student, beneficiary = sample_student
            
            # Assign beneficiary to trainer
            beneficiary.trainer_id = sample_trainer.id
            db.session.commit()
            
            # Step 1: Create appointment for assessment
            appointment_data = {
                'title': 'Assessment Appointment',
                'description': 'Initial skills assessment',
                'start_time': (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
                'end_time': (datetime.now(timezone.utc) + timedelta(days=1, hours=1)).isoformat(),
                'beneficiary_id': beneficiary.id
            }
            
            appointment = appointment_service.create_appointment(
                trainer_id=sample_trainer.id,
                appointment_data=appointment_data
            )
            
            # Step 2: Create evaluation for the assessment
            evaluation_data = {
                'title': 'Initial Skills Assessment',
                'type': EvaluationType.ASSESSMENT.value,
                'tenant_id': 1,
                'questions': [
                    {
                        'text': 'Basic question',
                        'type': 'text',
                        'points': 100
                    }
                ]
            }
            
            evaluation = evaluation_service.create_evaluation(
                creator_id=sample_trainer.id,
                data=evaluation_data
            )
            
            # Step 3: During appointment, create test session
            session = evaluation_service.create_test_session(
                user_id=student.id,
                evaluation_id=evaluation.id
            )
            
            # Step 4: Complete appointment
            appointment_update = {
                'status': 'completed',
                'notes': f'Assessment completed. Session ID: {session.id}'
            }
            
            updated_appointment = appointment_service.update_appointment(
                appointment_id=appointment['id'],
                user_id=sample_trainer.id,
                update_data=appointment_update
            )
            
            assert updated_appointment['status'] == 'completed'
            assert session.id is not None