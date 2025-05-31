"""Performance tests for backend services."""

import pytest
import time
from datetime import datetime, timedelta, timezone
from statistics import mean, stdev
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.appointment_service_refactored import AppointmentServiceRefactored
from app.services.evaluation_service_refactored import (
    EvaluationServiceRefactored,
    EvaluationType
)


class TestServicePerformance:
    """Performance tests for refactored services."""
    
    def test_appointment_bulk_creation_performance(self, app):
        """Test performance of bulk appointment creation."""
        with app.app_context():
            from app import db
            from app.models.user import User
            from app.models.beneficiary import Beneficiary
            
            # Create test data
            trainer = User(
                email='perf_trainer@test.com',
                first_name='Perf',
                last_name='Trainer',
                role='trainer'
            )
            trainer.set_password('password')
            db.session.add(trainer)
            
            student = User(
                email='perf_student@test.com',
                first_name='Perf',
                last_name='Student',
                role='student'
            )
            student.set_password('password')
            db.session.add(student)
            db.session.flush()
            
            beneficiary = Beneficiary(
                user_id=student.id,
                trainer_id=trainer.id,
                date_of_birth=datetime(2000, 1, 1).date()
            )
            db.session.add(beneficiary)
            db.session.commit()
            
            service = AppointmentServiceRefactored(db.session)
            
            # Measure bulk creation time
            num_appointments = 100
            start_time = time.time()
            
            for i in range(num_appointments):
                appointment_data = {
                    'title': f'Performance Test Appointment {i}',
                    'start_time': (datetime.now(timezone.utc) + timedelta(days=i, hours=1)).isoformat(),
                    'end_time': (datetime.now(timezone.utc) + timedelta(days=i, hours=2)).isoformat(),
                    'beneficiary_id': beneficiary.id
                }
                service.create_appointment(trainer.id, appointment_data)
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / num_appointments
            
            print(f"\nBulk Appointment Creation Performance:")
            print(f"Total appointments: {num_appointments}")
            print(f"Total time: {total_time:.2f} seconds")
            print(f"Average time per appointment: {avg_time * 1000:.2f} ms")
            
            # Performance assertion - should create 100 appointments in under 10 seconds
            assert total_time < 10, f"Bulk creation too slow: {total_time:.2f}s"
            assert avg_time < 0.1, f"Average creation time too high: {avg_time:.2f}s"
    
    def test_appointment_query_performance(self, app):
        """Test performance of appointment queries with filters."""
        with app.app_context():
            from app import db
            from app.models.user import User
            from app.models.beneficiary import Beneficiary
            from app.models.appointment import Appointment
            
            # Create test data
            trainer = User(
                email='query_trainer@test.com',
                first_name='Query',
                last_name='Trainer',
                role='trainer'
            )
            trainer.set_password('password')
            db.session.add(trainer)
            db.session.flush()
            
            # Create many appointments
            for i in range(500):
                appointment = Appointment(
                    title=f'Query Test {i}',
                    start_time=datetime.now(timezone.utc) + timedelta(days=i % 30),
                    end_time=datetime.now(timezone.utc) + timedelta(days=i % 30, hours=1),
                    trainer_id=trainer.id,
                    status=['scheduled', 'completed', 'cancelled'][i % 3]
                )
                db.session.add(appointment)
            
            db.session.commit()
            
            service = AppointmentServiceRefactored(db.session)
            
            # Test different query scenarios
            scenarios = [
                ("No filters", {}),
                ("Date filter", {
                    'start_date': datetime.now(timezone.utc),
                    'end_date': datetime.now(timezone.utc) + timedelta(days=7)
                }),
                ("Status filter", {'status': 'scheduled'}),
                ("Combined filters", {
                    'start_date': datetime.now(timezone.utc),
                    'end_date': datetime.now(timezone.utc) + timedelta(days=7),
                    'status': 'completed'
                })
            ]
            
            print("\nAppointment Query Performance:")
            
            for scenario_name, filters in scenarios:
                times = []
                
                for _ in range(10):  # Run each query 10 times
                    start_time = time.time()
                    result = service.get_appointments_for_user(
                        user_id=trainer.id,
                        page=1,
                        per_page=20,
                        **filters
                    )
                    end_time = time.time()
                    times.append(end_time - start_time)
                
                avg_time = mean(times)
                std_time = stdev(times) if len(times) > 1 else 0
                
                print(f"{scenario_name}: avg={avg_time*1000:.2f}ms, std={std_time*1000:.2f}ms")
                
                # Performance assertion - queries should complete in under 100ms
                assert avg_time < 0.1, f"{scenario_name} query too slow: {avg_time:.2f}s"
    
    def test_evaluation_session_performance(self, app):
        """Test performance of evaluation session operations."""
        with app.app_context():
            from app import db
            from app.models.user import User
            from app.models.beneficiary import Beneficiary
            from app.models.test import TestSet, Question
            
            # Create test data
            trainer = User(
                email='eval_trainer@test.com',
                first_name='Eval',
                last_name='Trainer',
                role='trainer'
            )
            trainer.set_password('password')
            db.session.add(trainer)
            
            student = User(
                email='eval_student@test.com',
                first_name='Eval',
                last_name='Student',
                role='student'
            )
            student.set_password('password')
            db.session.add(student)
            db.session.flush()
            
            beneficiary = Beneficiary(
                user_id=student.id,
                date_of_birth=datetime(2000, 1, 1).date()
            )
            db.session.add(beneficiary)
            
            # Create evaluation with many questions
            evaluation = TestSet(
                title='Performance Test Evaluation',
                type=EvaluationType.EXAM.value,
                status='published',
                creator_id=trainer.id,
                tenant_id=1
            )
            db.session.add(evaluation)
            db.session.flush()
            
            # Add 50 questions
            questions = []
            for i in range(50):
                question = Question(
                    test_set_id=evaluation.id,
                    text=f'Question {i+1}',
                    type='multiple_choice',
                    options=['A', 'B', 'C', 'D'],
                    correct_answer='A',
                    points=2,
                    order=i+1
                )
                db.session.add(question)
                questions.append(question)
            
            db.session.commit()
            
            service = EvaluationServiceRefactored(db.session)
            
            # Test session workflow performance
            print("\nEvaluation Session Performance:")
            
            # 1. Create session
            start_time = time.time()
            session = service.create_test_session(
                user_id=student.id,
                evaluation_id=evaluation.id
            )
            create_time = time.time() - start_time
            print(f"Session creation: {create_time*1000:.2f}ms")
            
            # 2. Submit all responses
            response_times = []
            for question in questions:
                start_time = time.time()
                service.submit_response(
                    session_id=session.id,
                    question_id=question.id,
                    user_id=student.id,
                    response_data={'answer': 'A'}
                )
                response_times.append(time.time() - start_time)
            
            avg_response_time = mean(response_times)
            print(f"Average response submission: {avg_response_time*1000:.2f}ms")
            
            # 3. Complete session
            start_time = time.time()
            completed_session = service.complete_session(
                session_id=session.id,
                user_id=student.id
            )
            complete_time = time.time() - start_time
            print(f"Session completion: {complete_time*1000:.2f}ms")
            
            # Performance assertions
            assert create_time < 0.5, f"Session creation too slow: {create_time:.2f}s"
            assert avg_response_time < 0.05, f"Response submission too slow: {avg_response_time:.2f}s"
            assert complete_time < 1.0, f"Session completion too slow: {complete_time:.2f}s"
    
    def test_concurrent_operations_performance(self, app):
        """Test performance under concurrent load."""
        with app.app_context():
            from app import db
            from app.models.user import User
            from app.models.beneficiary import Beneficiary
            
            # Create multiple trainers
            trainers = []
            for i in range(5):
                trainer = User(
                    email=f'concurrent_trainer{i}@test.com',
                    first_name=f'Trainer{i}',
                    last_name='Concurrent',
                    role='trainer'
                )
                trainer.set_password('password')
                db.session.add(trainer)
                trainers.append(trainer)
            
            db.session.flush()
            
            # Create beneficiaries
            beneficiaries = []
            for i in range(10):
                student = User(
                    email=f'concurrent_student{i}@test.com',
                    first_name=f'Student{i}',
                    last_name='Concurrent',
                    role='student'
                )
                student.set_password('password')
                db.session.add(student)
                db.session.flush()
                
                beneficiary = Beneficiary(
                    user_id=student.id,
                    trainer_id=trainers[i % 5].id,
                    date_of_birth=datetime(2000, 1, 1).date()
                )
                db.session.add(beneficiary)
                beneficiaries.append(beneficiary)
            
            db.session.commit()
            
            # Define concurrent operation
            def create_appointment(trainer_id, beneficiary_id, index):
                service = AppointmentServiceRefactored(db.session)
                start_time = time.time()
                
                try:
                    appointment_data = {
                        'title': f'Concurrent Appointment {index}',
                        'start_time': (datetime.now(timezone.utc) + timedelta(hours=index)).isoformat(),
                        'end_time': (datetime.now(timezone.utc) + timedelta(hours=index+1)).isoformat(),
                        'beneficiary_id': beneficiary_id
                    }
                    service.create_appointment(trainer_id, appointment_data)
                    return time.time() - start_time
                except Exception as e:
                    return None
            
            # Run concurrent operations
            print("\nConcurrent Operations Performance:")
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                
                for i in range(50):
                    trainer = trainers[i % len(trainers)]
                    beneficiary = beneficiaries[i % len(beneficiaries)]
                    
                    future = executor.submit(
                        create_appointment,
                        trainer.id,
                        beneficiary.id,
                        i
                    )
                    futures.append(future)
                
                # Collect results
                times = []
                errors = 0
                
                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        times.append(result)
                    else:
                        errors += 1
                
                if times:
                    avg_time = mean(times)
                    max_time = max(times)
                    min_time = min(times)
                    
                    print(f"Operations: {len(times)} successful, {errors} errors")
                    print(f"Average time: {avg_time*1000:.2f}ms")
                    print(f"Min time: {min_time*1000:.2f}ms")
                    print(f"Max time: {max_time*1000:.2f}ms")
                    
                    # Performance assertions
                    assert errors == 0, f"Concurrent operations had {errors} errors"
                    assert avg_time < 0.5, f"Average concurrent operation too slow: {avg_time:.2f}s"
                    assert max_time < 2.0, f"Slowest operation too slow: {max_time:.2f}s"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])