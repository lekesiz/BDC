"""
Fixtures for integration tests.
"""
import pytest
from datetime import datetime, timedelta
from app.models import (
    User, Tenant, Beneficiary, Appointment, 
    Evaluation, Report, Notification,
    TestSet, TestSession, Response, UserRole
)
from app.extensions import db


@pytest.fixture
def setup_integration_data(app):
    """Set up comprehensive data for integration tests."""
    with app.app_context():
        # Create tenants
        tenant1 = Tenant(name='Integration Test Clinic', slug='integration-test-clinic', email='test@clinic.com', is_active=True)
        tenant2 = Tenant(name='Secondary Test Clinic', slug='secondary-test-clinic', email='test2@clinic.com', is_active=True)
        db.session.add_all([tenant1, tenant2])
        db.session.commit()
        
        # Create users of different types
        admin = User(
            username='admin_test',
            email='admin@test.com',
            first_name='Admin',
            last_name='Test',
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            tenant_id=tenant1.id
        )
        admin.password = 'adminpass123'
        
        manager = User(
            username='manager_test',
            email='manager@test.com',
            first_name='Manager',
            last_name='Test',
            role=UserRole.TENANT_ADMIN,
            is_active=True,
            tenant_id=tenant1.id
        )
        manager.password = 'managerpass123'
        
        specialist = User(
            username='specialist_test',
            email='specialist@test.com',
            first_name='Specialist',
            last_name='Test',
            role=UserRole.TRAINER,
            is_active=True,
            tenant_id=tenant1.id
        )
        specialist.password = 'specialistpass123'
        
        therapist = User(
            username='therapist_test',
            email='therapist@test.com',
            first_name='Therapist',
            last_name='Test',
            role=UserRole.TRAINER,
            is_active=True,
            tenant_id=tenant1.id
        )
        therapist.password = 'therapistpass123'
        
        receptionist = User(
            username='receptionist_test',
            email='receptionist@test.com',
            first_name='Receptionist',
            last_name='Test',
            role=UserRole.STUDENT,
            is_active=True,
            tenant_id=tenant1.id
        )
        receptionist.password = 'receptionpass123'
        
        db.session.add_all([admin, manager, specialist, therapist, receptionist])
        db.session.commit()
        
        # Create beneficiary users first
        beneficiary_user1 = User(
            username='john_doe',
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe',
            role=UserRole.STUDENT,
            is_active=True,
            tenant_id=tenant1.id
        )
        beneficiary_user1.password = 'benpass123'
        db.session.add(beneficiary_user1)
        db.session.commit()
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(
            user_id=beneficiary_user1.id,
            trainer_id=therapist.id,
            tenant_id=tenant1.id,
            gender='male',
            birth_date=datetime(2010, 1, 15),
            phone='555-0001',
            address='123 Main St',
            city='New York',
            status='active'
        )
        
        beneficiary_user2 = User(
            username='jane_smith',
            email='jane.smith@example.com',
            first_name='Jane',
            last_name='Smith',
            role=UserRole.STUDENT,
            is_active=True,
            tenant_id=tenant1.id
        )
        beneficiary_user2.password = 'benpass123'
        db.session.add(beneficiary_user2)
        db.session.commit()
        
        beneficiary2 = Beneficiary(
            user_id=beneficiary_user2.id,
            trainer_id=therapist.id,
            tenant_id=tenant1.id,
            gender='female',
            birth_date=datetime(2012, 6, 20),
            phone='555-0002',
            address='456 Oak Ave',
            city='New York',
            status='active'
        )
        
        beneficiary_user3 = User(
            username='mike_johnson',
            email='mike.johnson@example.com',
            first_name='Mike',
            last_name='Johnson',
            role=UserRole.STUDENT,
            is_active=True,
            tenant_id=tenant1.id
        )
        beneficiary_user3.password = 'benpass123'
        db.session.add(beneficiary_user3)
        db.session.commit()
        
        beneficiary3 = Beneficiary(
            user_id=beneficiary_user3.id,
            trainer_id=specialist.id,
            tenant_id=tenant1.id,
            gender='male',
            birth_date=datetime(2008, 3, 10),
            phone='555-0003',
            address='789 Pine Rd',
            city='New York',
            status='active'
        )
        
        db.session.add_all([beneficiary1, beneficiary2, beneficiary3])
        db.session.commit()
        
        # Create appointments
        today = datetime.now()
        appointments = []
        
        # Past appointments
        for i in range(3):
            start = today - timedelta(days=i+1)
            appointment = Appointment(
                title=f'Past appointment {i+1}',
                start_time=start.replace(hour=14, minute=0),
                end_time=start.replace(hour=15, minute=0),
                beneficiary_id=beneficiary1.id,
                trainer_id=therapist.id,
                status='completed',
                description=f'Past therapy appointment {i+1}',
                notes=f'Past appointment {i+1}'
            )
            appointments.append(appointment)
        
        # Today's appointments
        appointment_today = Appointment(
            title='Today\'s therapy session',
            start_time=today.replace(hour=14, minute=0),
            end_time=today.replace(hour=15, minute=0),
            beneficiary_id=beneficiary2.id,
            trainer_id=therapist.id,
            status='scheduled',
            description='Today\'s therapy appointment',
            notes='Today\'s appointment'
        )
        appointments.append(appointment_today)
        
        # Future appointments
        for i in range(5):
            start = today + timedelta(days=i+1)
            appointment = Appointment(
                title=f'Future appointment {i+1}',
                start_time=start.replace(hour=10+i, minute=0),
                end_time=start.replace(hour=11+i, minute=0),
                beneficiary_id=beneficiary3.id if i % 2 == 0 else beneficiary1.id,
                trainer_id=specialist.id if i % 2 == 0 else therapist.id,
                status='scheduled',
                description=f'Future {"evaluation" if i % 3 == 0 else "therapy"} appointment {i+1}',
                notes=f'Future appointment {i+1}'
            )
            appointments.append(appointment)
        
        db.session.add_all(appointments)
        db.session.commit()
        
        # Create test templates
        template1 = TestSet(
            title='Cognitive Assessment',
            description='Standard cognitive assessment template',
            type='assessment',
            category='cognitive',
            tenant_id=tenant1.id,
            creator_id=specialist.id,
            time_limit=30,
            passing_score=70.0,
            status='active'
        )
        
        template2 = TestSet(
            title='Behavioral Checklist',
            description='Daily behavior tracking template',
            type='questionnaire',
            category='behavioral',
            tenant_id=tenant1.id,
            creator_id=therapist.id,
            time_limit=15,
            passing_score=60.0,
            status='active'
        )
        
        db.session.add_all([template1, template2])
        db.session.commit()
        
        # Create test sessions
        sessions = []
        for i in range(3):
            session = TestSession(
                test_set_id=template1.id if i == 0 else template2.id,
                beneficiary_id=beneficiary1.id if i == 0 else beneficiary2.id,
                start_time=today - timedelta(days=i*7),
                end_time=today - timedelta(days=i*7) + timedelta(hours=1),
                status='completed',
                score=80 + i*5,
                max_score=100,
                passed=True
            )
            sessions.append(session)
        
        db.session.add_all([s for s in sessions if s is not None])
        db.session.commit()
        
        # Create evaluations with corrected fields
        evaluations = []
        for i, session in enumerate(sessions):
            if session and session.id:  # Make sure session exists
                evaluation = Evaluation(
                    beneficiary_id=beneficiary1.id if i == 0 else beneficiary2.id,
                    trainer_id=specialist.id if i == 0 else therapist.id,
                    test_id=template1.id if i == 0 else template2.id,
                    score=75 + i*5,
                    feedback=f'Good progress in session {i+1}',
                    strengths='Shows improvement in focus and attention',
                    weaknesses='Still struggles with complex tasks',
                    recommendations='Continue with current therapy approach',
                    responses={
                        'memory_score': 7 + i,
                        'can_focus': True,
                        'interaction_notes': f'Good progress in session {i+1}'
                    },
                    evaluation_metadata={
                        'test_session_id': session.id,
                        'evaluation_type': 'cognitive' if i == 0 else 'behavioral'
                    },
                    status='completed',
                    created_at=session.start_time,
                    completed_at=session.end_time,
                    tenant_id=tenant1.id
                )
                evaluations.append(evaluation)
        
        db.session.add_all(evaluations)
        db.session.commit()
        
        # Create reports with corrected fields
        reports = []
        for i in range(2):
            report = Report(
                name=f'Monthly Progress Report {i+1}',
                type='beneficiary',
                description='Monthly progress report for beneficiary',
                created_by_id=specialist.id,
                tenant_id=tenant1.id,
                status='completed',
                parameters={
                    'beneficiary_id': beneficiary1.id if i == 0 else beneficiary2.id,
                    'period_start': (today - timedelta(days=30)).isoformat(),
                    'period_end': today.isoformat(),
                    'summary': {
                        'overall_progress': 'Good',
                        'key_achievements': ['Improved focus', 'Better social interaction'],
                        'recommendations': ['Continue current therapy', 'Increase group activities']
                    },
                    'sections': [
                        {
                            'title': 'Cognitive Development',
                            'content': 'Significant improvements observed in memory and attention tasks.'
                        },
                        {
                            'title': 'Social Skills',
                            'content': 'Better interaction with peers during group sessions.'
                        }
                    ]
                },
                last_generated=today - timedelta(days=i*15)
            )
            reports.append(report)
        
        db.session.add_all(reports)
        db.session.commit()
        
        # Create notifications with corrected field
        notifications = []
        
        # System notifications
        for user in [admin, manager, specialist, therapist]:
            notification = Notification(
                user_id=user.id,
                title='System Update',
                message='New features have been added to the system',
                type='system',
                priority='low',
                read=False,  # Changed from is_read to read
                created_at=today - timedelta(days=1),
                tenant_id=tenant1.id
            )
            notifications.append(notification)
        
        # Appointment reminders
        for appointment in appointments[-3:]:  # Last 3 future appointments
            notification = Notification(
                user_id=appointment.trainer_id,
                title='Appointment Reminder',
                message=f'You have an appointment on {appointment.start_time.date()}',
                type='appointment',
                priority='medium',
                read=False,  # Changed from is_read to read
                data={
                    'appointment_id': appointment.id,
                    'beneficiary_name': f'{appointment.beneficiary.user.first_name} {appointment.beneficiary.user.last_name}'
                },
                related_id=appointment.id,
                related_type='appointment',
                created_at=today,
                tenant_id=tenant1.id
            )
            notifications.append(notification)
        
        # Report notifications
        for report in reports:
            notification = Notification(
                user_id=report.created_by_id,
                title='Report Generated',
                message=f'Report "{report.name}" has been generated',
                type='report',
                priority='high',
                read=True,  # Changed from is_read to read
                data={
                    'report_id': report.id,
                    'beneficiary_id': report.parameters.get('beneficiary_id')
                },
                related_id=report.id,
                related_type='report',
                created_at=report.last_generated,
                tenant_id=tenant1.id
            )
            notifications.append(notification)
        
        db.session.add_all(notifications)
        db.session.commit()
        
        yield {
            'tenants': [tenant1, tenant2],
            'users': {
                'admin': admin,
                'manager': manager,
                'specialist': specialist,
                'therapist': therapist,
                'receptionist': receptionist
            },
            'beneficiaries': [beneficiary1, beneficiary2, beneficiary3],
            'appointments': appointments,
            'templates': [template1, template2],
            'sessions': sessions,
            'evaluations': evaluations,
            'reports': reports,
            'notifications': notifications
        }
        
        # Cleanup
        db.session.query(Notification).delete()
        db.session.query(Report).delete()
        db.session.query(Response).delete()
        db.session.query(Evaluation).delete()
        db.session.query(TestSession).delete()
        db.session.query(TestSet).delete()
        db.session.query(Appointment).delete()
        db.session.query(Beneficiary).delete()
        db.session.query(User).delete()
        db.session.query(Tenant).delete()
        db.session.commit()