#!/usr/bin/env python3
"""Seed demo data for BDC application."""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the server directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.beneficiary import Beneficiary
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.models.document import Document
from app.models.appointment import Appointment

def create_demo_data():
    """Create comprehensive demo data for the BDC application."""
    
    app = create_app()
    with app.app_context():
        print("🌱 Creating demo data...")
        
        # Get default tenant
        tenant = Tenant.query.filter_by(slug='default').first()
        if not tenant:
            print("Error: Default tenant not found")
            return
        
        # Create additional users
        users_data = [
            {
                'email': 'trainer@bdc.com',
                'username': 'trainer',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'trainer',
                'password': 'trainer123'
            },
            {
                'email': 'student@bdc.com', 
                'username': 'student',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'role': 'student',
                'password': 'student123'
            },
            {
                'email': 'coordinator@bdc.com',
                'username': 'coordinator', 
                'first_name': 'Emma',
                'last_name': 'Davis',
                'role': 'program_coordinator',
                'password': 'coordinator123'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=True,
                    tenant_id=tenant.id
                )
                user.password = user_data['password']
                db.session.add(user)
                created_users.append(user)
                print(f"✅ Created user: {user_data['email']}")
            else:
                created_users.append(existing_user)
                print(f"📝 User already exists: {user_data['email']}")
        
        db.session.commit()
        
        # Create demo programs
        programs_data = [
            {
                'name': 'Digital Literacy Training',
                'description': 'Comprehensive program to teach basic computer skills and internet literacy to community members.',
                'status': 'active',
                'start_date': datetime.now() - timedelta(days=30),
                'end_date': datetime.now() + timedelta(days=60),
                'max_participants': 25,
                'objectives': ['Basic computer operation', 'Internet navigation', 'Email communication', 'Online safety']
            },
            {
                'name': 'Entrepreneurship Bootcamp',
                'description': 'Intensive program designed to help participants develop business skills and start their own ventures.',
                'status': 'active', 
                'start_date': datetime.now() - timedelta(days=15),
                'end_date': datetime.now() + timedelta(days=75),
                'max_participants': 20,
                'objectives': ['Business planning', 'Financial management', 'Marketing basics', 'Legal requirements']
            },
            {
                'name': 'Health & Wellness Workshop',
                'description': 'Educational program focusing on personal health, nutrition, and wellness practices.',
                'status': 'completed',
                'start_date': datetime.now() - timedelta(days=90),
                'end_date': datetime.now() - timedelta(days=30),
                'max_participants': 30,
                'objectives': ['Nutrition education', 'Exercise planning', 'Mental health awareness', 'Preventive care']
            },
            {
                'name': 'Vocational Skills Development',
                'description': 'Hands-on training program for practical vocational skills in various trades.',
                'status': 'planned',
                'start_date': datetime.now() + timedelta(days=30),
                'end_date': datetime.now() + timedelta(days=120),
                'max_participants': 15,
                'objectives': ['Technical skills', 'Safety procedures', 'Quality standards', 'Professional development']
            }
        ]
        
        created_programs = []
        for program_data in programs_data:
            program = Program(
                name=program_data['name'],
                description=program_data['description'],
                status=program_data['status'],
                start_date=program_data['start_date'],
                end_date=program_data['end_date'],
                max_participants=program_data['max_participants'],
                tenant_id=tenant.id,
                created_by_id=created_users[0].id  # trainer
            )
            db.session.add(program)
            created_programs.append(program)
            print(f"✅ Created program: {program_data['name']}")
        
        db.session.commit()
        
        # Create demo beneficiaries (as users first, then beneficiary records)
        beneficiaries_data = [
            {
                'email': 'maria.rodriguez@email.com',
                'username': 'maria.rodriguez',
                'first_name': 'Maria',
                'last_name': 'Rodriguez',
                'phone': '+1234567890',
                'address': '123 Main St, City, State 12345',
                'birth_date': datetime(1985, 3, 15),
                'gender': 'female',
                'education_level': 'high_school'
            },
            {
                'email': 'john.smith@email.com',
                'username': 'john.smith',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '+1234567891',
                'address': '456 Oak Ave, City, State 12346',
                'birth_date': datetime(1978, 7, 22),
                'gender': 'male',
                'education_level': 'some_college'
            },
            {
                'email': 'fatima.alzahra@email.com',
                'username': 'fatima.alzahra',
                'first_name': 'Fatima',
                'last_name': 'Al-Zahra',
                'phone': '+1234567892',
                'address': '789 Pine St, City, State 12347',
                'birth_date': datetime(1990, 11, 8),
                'gender': 'female',
                'education_level': 'college'
            },
            {
                'email': 'carlos.garcia@email.com',
                'username': 'carlos.garcia',
                'first_name': 'Carlos',
                'last_name': 'Garcia',
                'phone': '+1234567893',
                'address': '321 Elm Dr, City, State 12348',
                'birth_date': datetime(1982, 5, 12),
                'gender': 'male',
                'education_level': 'vocational'
            }
        ]
        
        created_beneficiaries = []
        for ben_data in beneficiaries_data:
            # Create user first
            existing_user = User.query.filter_by(email=ben_data['email']).first()
            if not existing_user:
                user = User(
                    email=ben_data['email'],
                    username=ben_data['username'],
                    first_name=ben_data['first_name'],
                    last_name=ben_data['last_name'],
                    role='beneficiary',
                    is_active=True,
                    tenant_id=tenant.id
                )
                user.password = 'beneficiary123'
                db.session.add(user)
                db.session.flush()  # To get the ID
                
                # Create beneficiary record
                beneficiary = Beneficiary(
                    user_id=user.id,
                    tenant_id=tenant.id,
                    phone=ben_data['phone'],
                    address=ben_data['address'],
                    birth_date=ben_data['birth_date'],
                    gender=ben_data['gender'],
                    education_level=ben_data['education_level'],
                    status='active',
                    is_active=True
                )
                db.session.add(beneficiary)
                created_beneficiaries.append(beneficiary)
                print(f"✅ Created beneficiary: {ben_data['first_name']} {ben_data['last_name']}")
            else:
                # Find existing beneficiary by user email with explicit join
                existing_beneficiary = Beneficiary.query.join(User, Beneficiary.user_id == User.id).filter(User.email == ben_data['email']).first()
                if existing_beneficiary:
                    created_beneficiaries.append(existing_beneficiary)
                print(f"📝 Beneficiary user already exists: {ben_data['email']}")
        
        db.session.commit()
        
        # Create program enrollments (random assignments)
        print("🔗 Creating program enrollments...")
        from app.models.program import ProgramEnrollment
        
        enrollments_created = 0
        for beneficiary in created_beneficiaries:
            # Enroll each beneficiary in 1-3 random active programs
            active_programs = [p for p in created_programs if p.status == 'active']
            num_enrollments = random.randint(1, min(3, len(active_programs)))
            enrolled_programs = random.sample(active_programs, num_enrollments)
            
            for program in enrolled_programs:
                # Check if enrollment already exists
                existing = ProgramEnrollment.query.filter_by(
                    program_id=program.id,
                    beneficiary_id=beneficiary.id
                ).first()
                
                if not existing:
                    enrollment = ProgramEnrollment(
                        program_id=program.id,
                        beneficiary_id=beneficiary.id,
                        enrollment_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                        status='active',
                        progress=random.uniform(10.0, 90.0),
                        attendance_rate=random.uniform(70.0, 100.0),
                        overall_score=random.uniform(60.0, 95.0)
                    )
                    db.session.add(enrollment)
                    enrollments_created += 1
        
        db.session.commit()
        print(f"✅ Created {enrollments_created} program enrollments")
        
        # Create tests first (required for evaluations)
        print("📝 Creating tests...")
        from app.models.test import Test
        
        tests_data = [
            {
                'title': 'Digital Skills Assessment',
                'description': 'Comprehensive assessment of basic digital literacy skills',
                'type': 'skill_test',
                'category': 'digital_literacy',
                'duration': 60,
                'passing_score': 70.0,
                'total_points': 100.0
            },
            {
                'title': 'Business Knowledge Evaluation',
                'description': 'Assessment of entrepreneurship and business fundamentals',
                'type': 'assessment',
                'category': 'business',
                'duration': 45,
                'passing_score': 75.0,
                'total_points': 100.0
            },
            {
                'title': 'Communication Skills Test',
                'description': 'Evaluation of verbal and written communication abilities',
                'type': 'skill_test',
                'category': 'communication',
                'duration': 30,
                'passing_score': 65.0,
                'total_points': 100.0
            }
        ]
        
        created_tests = []
        for test_data in tests_data:
            test = Test(
                title=test_data['title'],
                description=test_data['description'],
                type=test_data['type'],
                category=test_data['category'],
                tenant_id=tenant.id,
                created_by=created_users[0].id,  # trainer
                duration=test_data['duration'],
                passing_score=test_data['passing_score'],
                total_points=test_data['total_points'],
                status='published'
            )
            db.session.add(test)
            created_tests.append(test)
        
        db.session.commit()
        print(f"✅ Created {len(created_tests)} tests")
        
        # Create evaluations
        print("📋 Creating evaluations...")
        evaluations_created = 0
        
        for beneficiary in created_beneficiaries:
            # Create 2-3 evaluations per beneficiary
            num_evaluations = random.randint(2, 3)
            for i in range(num_evaluations):
                test = random.choice(created_tests)
                
                # Random completion status
                is_completed = random.choice([True, False])
                completion_date = datetime.now() - timedelta(days=random.randint(0, 30)) if is_completed else None
                
                evaluation = Evaluation(
                    beneficiary_id=beneficiary.id,
                    test_id=test.id,
                    trainer_id=created_users[0].id,  # trainer
                    tenant_id=tenant.id,
                    creator_id=created_users[0].id,  # trainer
                    score=random.uniform(65.0, 95.0) if is_completed else None,
                    feedback=f"Good progress shown in {test.category} skills. Recommendation for continued development." if is_completed else None,
                    strengths="Demonstrates good understanding of key concepts, strong problem-solving approach." if is_completed else None,
                    weaknesses="Could improve in time management and attention to detail." if is_completed else None,
                    recommendations="Continue practice with advanced exercises and seek mentoring." if is_completed else None,
                    status='completed' if is_completed else random.choice(['in_progress', 'in_progress']),
                    completed_at=completion_date
                )
                db.session.add(evaluation)
                evaluations_created += 1
        
        db.session.commit()
        print(f"✅ Created {evaluations_created} evaluations")
        
        # Create appointments
        print("📅 Creating appointments...")
        appointments_created = 0
        
        for beneficiary in created_beneficiaries:
            # Create 2-3 appointments per beneficiary (past and future)
            num_appointments = random.randint(2, 3)
            for i in range(num_appointments):
                # Mix of past and future appointments
                is_future = random.choice([True, False])
                if is_future:
                    start_time = datetime.now() + timedelta(days=random.randint(1, 30))
                    status = 'scheduled'
                else:
                    start_time = datetime.now() - timedelta(days=random.randint(1, 30))
                    status = random.choice(['completed', 'cancelled'])
                
                appointment_titles = [
                    f"Consultation - {beneficiary.first_name}",
                    f"Progress Meeting - {beneficiary.first_name}",
                    f"Skill Assessment - {beneficiary.first_name}",
                    f"Career Guidance - {beneficiary.first_name}"
                ]
                
                appointment = Appointment(
                    beneficiary_id=beneficiary.id,
                    trainer_id=created_users[0].id,  # trainer
                    title=random.choice(appointment_titles),
                    description=f"Individual session focused on personal development and skill building for {beneficiary.first_name}.",
                    start_time=start_time,
                    end_time=start_time + timedelta(hours=1),
                    location=random.choice(['Online', 'Office A', 'Training Room 1', 'Conference Room']),
                    status=status,
                    notes="Session notes and follow-up actions will be documented here." if status == 'completed' else None
                )
                db.session.add(appointment)
                appointments_created += 1
        
        db.session.commit()
        print(f"✅ Created {appointments_created} appointments")
        
        # Create documents
        print("📄 Creating documents...")
        documents_created = 0
        document_types = ['certificate', 'assessment', 'report', 'application', 'identification']
        
        for beneficiary in created_beneficiaries:
            # Create 1-3 documents per beneficiary
            num_documents = random.randint(1, 3)
            for i in range(num_documents):
                doc_type = random.choice(document_types)
                document = Document(
                    beneficiary_id=beneficiary.id,
                    upload_by=created_users[0].id,  # trainer
                    title=f"{doc_type.title()} - {beneficiary.first_name} {beneficiary.last_name}",
                    description=f"Important {doc_type} document for {beneficiary.first_name}",
                    file_path=f"/uploads/documents/{doc_type}_{beneficiary.id}_{i+1}.pdf",
                    file_type="application/pdf",
                    file_size=random.randint(50000, 500000),  # 50KB to 500KB
                    document_type=doc_type,
                    is_active=True
                )
                db.session.add(document)
                documents_created += 1
        
        db.session.commit()
        print(f"✅ Created {documents_created} documents")
        
        print("✅ Basic demo data created successfully!")
        
        print("\n🎉 Demo data creation completed successfully!")
        
        # Print summary
        print("\n📊 Demo Data Summary:")
        print(f"👥 Users: {User.query.count()}")
        print(f"🎯 Programs: {Program.query.count()}")
        print(f"🤝 Beneficiaries: {Beneficiary.query.count()}")
        print(f"📝 Tests: {Test.query.count()}")
        print(f"📋 Evaluations: {Evaluation.query.count()}")
        print(f"📅 Appointments: {Appointment.query.count()}")
        print(f"📄 Documents: {Document.query.count()}")
        print(f"🔗 Program Enrollments: {ProgramEnrollment.query.count()}")
        
        print("\n👤 Test User Credentials:")
        print("• Admin: admin@bdc.com / admin123")
        print("• Trainer: trainer@bdc.com / trainer123")
        print("• Student: student@bdc.com / student123")
        print("• Coordinator: coordinator@bdc.com / coordinator123")

if __name__ == '__main__':
    create_demo_data()