import pytest
from datetime import datetime, timedelta
from app import db
from app.models import Program, Tenant, User


class TestProgramModelSimple:
    """Simplified test cases for the Program model."""
    
    def test_program_creation(self, db_session):
        """Test creating a new program."""
        # Create tenant and creator
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(
            email='creator@example.com',
            first_name='Creator',
            last_name='User',  
            role='admin'
        )
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        # Create program with required fields
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Youth Development Program',
            code='YDP-001'
        )
        db.session.add(program)
        db.session.commit()
        
        assert program.id is not None
        assert program.name == 'Youth Development Program'
        assert program.code == 'YDP-001'
    
    def test_program_with_all_fields(self, db_session):
        """Test program with all optional fields."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Advanced Program',
            code='ADV-001',
            description='An advanced training program',
            duration=120,
            level='advanced',
            category='technical',
            prerequisites={'skills': ['Python', 'SQL']},
            minimum_attendance=85,
            passing_score=80,
            status='active',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=120),
            max_participants=30
        )
        db.session.add(program)
        db.session.commit()
        
        assert program.duration == 120
        assert program.level == 'advanced'
        assert program.category == 'technical'
        assert program.minimum_attendance == 85
        assert program.passing_score == 80
        assert program.status == 'active'
        assert program.max_participants == 30
    
    def test_program_defaults(self, db_session):
        """Test program default values."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Basic Program',
            code='BP-001'
        )
        db.session.add(program)
        db.session.commit()
        
        assert program.is_active is True
        assert program.created_at is not None
        assert program.updated_at is not None
    
    def test_program_relationships(self, db_session):
        """Test program relationships."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Test Program',
            code='TP-001'
        )
        db.session.add(program)
        db.session.commit()
        
        # Test relationships
        assert program.tenant == tenant
        assert program.created_by == creator
    
    def test_program_status_values(self, db_session):
        """Test different program status values."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        statuses = ['draft', 'active', 'completed', 'cancelled']
        
        for i, status in enumerate(statuses):
            program = Program(
                tenant_id=tenant.id,
                created_by_id=creator.id,
                name=f'Program {i}',
                code=f'P{i:03d}',
                status=status
            )
            db.session.add(program)
        
        db.session.commit()
        
        # Query by status
        active_programs = Program.query.filter_by(status='active').all()
        assert len(active_programs) == 1
        assert active_programs[0].status == 'active'
    
    def test_program_dates(self, db_session):
        """Test program date fields."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=90)
        
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Timed Program',
            code='TM-001',
            start_date=start_date,
            end_date=end_date
        )
        db.session.add(program)
        db.session.commit()
        
        assert program.start_date is not None
        assert program.end_date is not None
        assert program.end_date > program.start_date
    
    def test_program_scoring_fields(self, db_session):
        """Test program scoring fields."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Scored Program',
            code='SC-001',
            minimum_attendance=75,
            passing_score=65
        )
        db.session.add(program)
        db.session.commit()
        
        assert program.minimum_attendance == 75
        assert program.passing_score == 65
    
    def test_program_query_scopes(self, db_session):
        """Test querying programs with different criteria."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        # Create programs with different attributes
        programs_data = [
            ('Active Program', 'ACT-001', 'active', True),
            ('Draft Program', 'DFT-001', 'draft', True),
            ('Inactive Program', 'INA-001', 'active', False),
            ('Completed Program', 'CMP-001', 'completed', True)
        ]
        
        for name, code, status, is_active in programs_data:
            program = Program(
                tenant_id=tenant.id,
                created_by_id=creator.id,
                name=name,
                code=code,
                status=status,
                is_active=is_active
            )
            db.session.add(program)
        
        db.session.commit()
        
        # Query active programs only
        active_programs = Program.query.filter_by(
            tenant_id=tenant.id,
            is_active=True,
            status='active'
        ).all()
        assert len(active_programs) == 1
        assert active_programs[0].name == 'Active Program'
        
        # Query all active (non-deleted) programs
        all_active = Program.query.filter_by(
            tenant_id=tenant.id,
            is_active=True
        ).all()
        assert len(all_active) == 3
    
    def test_program_categories_and_levels(self, db_session):
        """Test program categories and levels."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        categories = ['technical', 'soft_skills', 'leadership', 'business']
        levels = ['beginner', 'intermediate', 'advanced', 'expert']
        
        # Create programs with different categories and levels
        for i, (category, level) in enumerate(zip(categories, levels)):
            program = Program(
                tenant_id=tenant.id,
                created_by_id=creator.id,
                name=f'{category.title()} {level.title()} Program',
                code=f'PG-{i:03d}',
                category=category,
                level=level
            )
            db.session.add(program)
        
        db.session.commit()
        
        # Query by category
        technical_programs = Program.query.filter_by(category='technical').all()
        assert len(technical_programs) == 1
        assert technical_programs[0].level == 'beginner'
        
        # Query by level
        advanced_programs = Program.query.filter_by(level='advanced').all()
        assert len(advanced_programs) == 1
        assert advanced_programs[0].category == 'leadership'
    
    def test_program_prerequisites_json(self, db_session):
        """Test program prerequisites JSON field."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='creator@example.com', first_name='C', last_name='U', role='admin')
        db.session.add_all([tenant, creator])
        db.session.commit()
        
        prerequisites = {
            'education': 'High school diploma',
            'skills': ['Basic computer skills', 'English proficiency'],
            'age_min': 18,
            'experience': 'None required'
        }
        
        program = Program(
            tenant_id=tenant.id,
            created_by_id=creator.id,
            name='Prerequisite Program',
            code='PRQ-001',
            prerequisites=prerequisites
        )
        db.session.add(program)
        db.session.commit()
        
        # Reload and verify
        program_id = program.id
        db.session.expunge_all()
        loaded_program = Program.query.get(program_id)
        
        assert loaded_program.prerequisites == prerequisites
        assert len(loaded_program.prerequisites['skills']) == 2
        assert loaded_program.prerequisites['age_min'] == 18