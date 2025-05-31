import pytest
from datetime import datetime, timedelta
from app import db
from app.models import Evaluation, User, Beneficiary, Tenant


class TestEvaluationModelSimple:
    """Simplified test cases for the Evaluation model."""
    
    def test_evaluation_creation(self, db_session):
        """Test creating a new evaluation."""
        # Create required entities
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        creator = User(email='creator@example.com', first_name='C', last_name='R', role='staff')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            gender='male',
            birth_date=datetime.utcnow() - timedelta(days=365*25)
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create evaluation
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            creator_id=creator.id,
            score=85.5,
            status='completed'
        )
        db.session.add(evaluation)
        db.session.commit()
        
        assert evaluation.id is not None
        assert evaluation.score == 85.5
        assert evaluation.status == 'completed'
    
    def test_evaluation_with_feedback(self, db_session):
        """Test evaluation with detailed feedback."""
        # Create required entities
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            gender='female',
            birth_date=datetime.utcnow() - timedelta(days=365*23)
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create evaluation with feedback
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            score=92,
            feedback='Excellent performance in all areas.',
            strengths='Strong communication skills, quick learner',
            weaknesses='Needs more practice with advanced topics',
            recommendations='Continue with advanced level training',
            status='completed'
        )
        db.session.add(evaluation)
        db.session.commit()
        
        assert evaluation.feedback is not None
        assert 'Excellent' in evaluation.feedback
        assert evaluation.strengths is not None
        assert evaluation.weaknesses is not None
        assert evaluation.recommendations is not None
    
    def test_evaluation_defaults(self, db_session):
        """Test evaluation default values."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id
        )
        db.session.add(evaluation)
        db.session.commit()
        
        assert evaluation.status == 'pending'
        assert evaluation.created_at is not None
        assert evaluation.updated_at is not None
    
    def test_evaluation_relationships(self, db_session):
        """Test evaluation relationships."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        creator = User(email='creator@example.com', first_name='C', last_name='R', role='staff')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            creator_id=creator.id
        )
        db.session.add(evaluation)
        db.session.commit()
        
        # Test relationships
        assert evaluation.beneficiary == beneficiary
        assert evaluation.trainer == trainer
        assert evaluation.tenant == tenant
        assert evaluation.creator == creator
    
    def test_evaluation_status_transitions(self, db_session):
        """Test evaluation status transitions."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            status='pending'
        )
        db.session.add(evaluation)
        db.session.commit()
        
        # Test status transitions
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        for status in valid_statuses:
            evaluation.status = status
            db.session.commit()
            assert evaluation.status == status
    
    def test_evaluation_metadata_json(self, db_session):
        """Test evaluation metadata JSON field."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        metadata = {
            'evaluation_type': 'skills_assessment',
            'duration_minutes': 60,
            'location': 'Training Center',
            'categories': {
                'technical': 85,
                'communication': 90,
                'teamwork': 88
            }
        }
        
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            evaluation_metadata=metadata,
            score=87.67  # average of categories
        )
        db.session.add(evaluation)
        db.session.commit()
        
        # Reload and verify
        eval_id = evaluation.id
        db.session.expunge_all()
        loaded_eval = Evaluation.query.get(eval_id)
        
        assert loaded_eval.evaluation_metadata == metadata
        assert loaded_eval.evaluation_metadata['categories']['technical'] == 85
        assert loaded_eval.evaluation_metadata['duration_minutes'] == 60
    
    def test_evaluation_responses_json(self, db_session):
        """Test evaluation responses JSON field."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        responses = {
            'questions': [
                {'id': 1, 'question': 'Rate your understanding', 'answer': 4, 'max_score': 5},
                {'id': 2, 'question': 'Practical skills', 'answer': 5, 'max_score': 5},
                {'id': 3, 'question': 'Team collaboration', 'answer': 4, 'max_score': 5}
            ],
            'total_score': 13,
            'max_total_score': 15
        }
        
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            responses=responses,
            score=86.67  # 13/15 * 100
        )
        db.session.add(evaluation)
        db.session.commit()
        
        assert evaluation.responses is not None
        assert len(evaluation.responses['questions']) == 3
        assert evaluation.responses['total_score'] == 13
    
    def test_evaluation_completion_dates(self, db_session):
        """Test evaluation completion and review dates."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create evaluation
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            status='pending'
        )
        db.session.add(evaluation)
        db.session.commit()
        
        # Complete evaluation
        evaluation.status = 'completed'
        evaluation.completed_at = datetime.utcnow()
        db.session.commit()
        
        assert evaluation.completed_at is not None
        
        # Review evaluation
        evaluation.reviewed_at = datetime.utcnow()
        db.session.commit()
        
        assert evaluation.reviewed_at is not None
        assert evaluation.reviewed_at >= evaluation.completed_at
    
    def test_evaluation_query_by_beneficiary(self, db_session):
        """Test querying evaluations by beneficiary."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user1 = User(email='ben1@example.com', first_name='B1', last_name='N1', role='beneficiary')
        ben_user2 = User(email='ben2@example.com', first_name='B2', last_name='N2', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user1, ben_user2])
        db.session.commit()
        
        beneficiary1 = Beneficiary(user_id=ben_user1.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        beneficiary2 = Beneficiary(user_id=ben_user2.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add_all([beneficiary1, beneficiary2])
        db.session.commit()
        
        # Create evaluations for beneficiary1
        for i in range(3):
            evaluation = Evaluation(
                beneficiary_id=beneficiary1.id,
                trainer_id=trainer.id,
                tenant_id=tenant.id,
                score=80 + i * 5,
                status='completed'
            )
            db.session.add(evaluation)
        
        # Create evaluation for beneficiary2
        evaluation2 = Evaluation(
            beneficiary_id=beneficiary2.id,
            trainer_id=trainer.id,
            tenant_id=tenant.id,
            score=75,
            status='completed'
        )
        db.session.add(evaluation2)
        db.session.commit()
        
        # Query beneficiary1 evaluations
        b1_evaluations = Evaluation.query.filter_by(
            beneficiary_id=beneficiary1.id
        ).all()
        assert len(b1_evaluations) == 3
        
        # Query by status
        completed_evals = Evaluation.query.filter_by(
            tenant_id=tenant.id,
            status='completed'
        ).all()
        assert len(completed_evals) == 4
    
    def test_evaluation_score_range(self, db_session):
        """Test evaluation scores with different ranges."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([tenant, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        scores = [0, 50.5, 75.25, 100]
        
        for score in scores:
            evaluation = Evaluation(
                beneficiary_id=beneficiary.id,
                trainer_id=trainer.id,
                tenant_id=tenant.id,
                score=score
            )
            db.session.add(evaluation)
        
        db.session.commit()
        
        # Query evaluations with score >= 75
        high_scores = Evaluation.query.filter(
            Evaluation.tenant_id == tenant.id,
            Evaluation.score >= 75
        ).all()
        assert len(high_scores) == 2