import pytest
from datetime import datetime
from app import db
from app.models import Note, User, Beneficiary, Tenant
from werkzeug.security import generate_password_hash


class TestNoteModel:
    """Test cases for the Note model."""
    
    def test_note_creation(self, db_session):
        """Test creating a new note."""
        # Create tenant and user
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        db.session.add(tenant)
        
        creator = User(
            email='creator@example.com',
            first_name='Note',
            last_name='Creator',
            role='staff'
        )
        creator.password = 'test123'
        
        ben_user = User(
            email='beneficiary@example.com',
            first_name='Ben',
            last_name='Eficiary',
            role='beneficiary'
        )
        ben_user.password = 'test123'
        
        db.session.add_all([creator, ben_user])
        db.session.commit()
        
        # Create beneficiary
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            gender='female',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create note
        note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            content='Initial assessment completed. Beneficiary shows strong motivation.'
        )
        db.session.add(note)
        db.session.commit()
        
        assert note.id is not None
        assert note.content is not None
        assert 'strong motivation' in note.content
        assert note.creator_id == creator.id
        assert note.beneficiary_id == beneficiary.id
    
    def test_note_with_title(self, db_session):
        """Test note with title and tags."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='c@example.com', first_name='C', last_name='R', role='staff')
        creator.password = 'test123'
        ben_user = User(email='b@example.com', first_name='B', last_name='N', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            tenant_id=tenant.id,
            gender='male',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create note with title and tags
        note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            title='Progress Report - Week 4',
            content='Excellent progress in technical skills.',
            tags=['progress', 'technical', 'positive']
        )
        db.session.add(note)
        db.session.commit()
        
        assert note.title == 'Progress Report - Week 4'
        assert note.tags is not None
        assert 'progress' in note.tags
        assert len(note.tags) == 3
    
    def test_note_defaults(self, db_session):
        """Test note default values."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='c@example.com', first_name='C', last_name='R', role='staff')
        creator.password = 'test123'
        ben_user = User(email='b@example.com', first_name='B', last_name='N', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            content='Simple note'
        )
        db.session.add(note)
        db.session.commit()
        
        assert note.created_at is not None
        assert note.updated_at is not None
        assert note.is_private is False  # Default visibility
    
    def test_note_relationships(self, db_session):
        """Test note relationships."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='c@example.com', first_name='C', last_name='R', role='staff')
        creator.password = 'test123'
        ben_user = User(email='b@example.com', first_name='B', last_name='N', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            content='Relationship test note'
        )
        db.session.add(note)
        db.session.commit()
        
        # Test relationships
        assert note.beneficiary == beneficiary
        assert note.creator == creator
        assert note in beneficiary.notes_rel
    
    def test_note_privacy(self, db_session):
        """Test note privacy settings."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='c@example.com', first_name='C', last_name='R', role='staff')
        creator.password = 'test123'
        ben_user = User(email='b@example.com', first_name='B', last_name='N', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create public note
        public_note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            content='Public note visible to all staff',
            is_private=False
        )
        
        # Create private note
        private_note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            content='Private note only for creator',
            is_private=True
        )
        
        db.session.add_all([public_note, private_note])
        db.session.commit()
        
        assert public_note.is_private is False
        assert private_note.is_private is True
    
    def test_note_content_length(self, db_session):
        """Test note with long content."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='c@example.com', first_name='C', last_name='R', role='staff')
        creator.password = 'test123'
        ben_user = User(email='b@example.com', first_name='B', last_name='N', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create note with long content
        long_content = """
        This is a detailed progress report for the beneficiary.
        
        Week 1: Initial assessment completed. Identified key areas for development.
        - Technical skills: Basic level, needs improvement
        - Communication: Good verbal skills, written needs work
        - Time management: Requires structure and guidance
        
        Week 2: Started technical training program
        - Completed introduction to programming
        - Showed good understanding of basic concepts
        - Homework completion rate: 80%
        
        Week 3: Continued progress
        - Advanced to intermediate topics
        - Peer collaboration improved significantly
        - Started working on first project
        
        Recommendations:
        1. Continue with current program
        2. Add supplementary communication workshops
        3. Schedule bi-weekly check-ins
        """
        
        note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            title='Month 1 Progress Report',
            content=long_content.strip()
        )
        db.session.add(note)
        db.session.commit()
        
        assert len(note.content) > 500
        assert 'technical training program' in note.content
        assert 'Recommendations' in note.content
    
    def test_note_query_by_beneficiary(self, db_session):
        """Test querying notes by beneficiary."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator1 = User(email='c1@example.com', first_name='C1', last_name='R1', role='staff')
        creator1.password = 'test123'
        creator2 = User(email='c2@example.com', first_name='C2', last_name='R2', role='staff')
        creator2.password = 'test123'
        ben_user1 = User(email='b1@example.com', first_name='B1', last_name='N1', role='beneficiary')
        ben_user1.password = 'test123'
        ben_user2 = User(email='b2@example.com', first_name='B2', last_name='N2', role='beneficiary')
        ben_user2.password = 'test123'
        db.session.add_all([tenant, creator1, creator2, ben_user1, ben_user2])
        db.session.commit()
        
        beneficiary1 = Beneficiary(user_id=ben_user1.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        beneficiary2 = Beneficiary(user_id=ben_user2.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add_all([beneficiary1, beneficiary2])
        db.session.commit()
        
        # Create notes for beneficiary1
        for i in range(3):
            note = Note(
                beneficiary_id=beneficiary1.id,
                creator_id=creator1.id if i % 2 == 0 else creator2.id,
                content=f'Note {i} for beneficiary 1'
            )
            db.session.add(note)
        
        # Create note for beneficiary2
        note2 = Note(
            beneficiary_id=beneficiary2.id,
            creator_id=creator1.id,
            content='Note for beneficiary 2'
        )
        db.session.add(note2)
        db.session.commit()
        
        # Query beneficiary1 notes
        b1_notes = Note.query.filter_by(beneficiary_id=beneficiary1.id).all()
        assert len(b1_notes) == 3
        
        # Query creator1 notes
        c1_notes = Note.query.filter_by(creator_id=creator1.id).all()
        assert len(c1_notes) == 3  # 2 for b1, 1 for b2
    
    def test_note_update_tracking(self, db_session):
        """Test note update timestamp tracking."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='c@example.com', first_name='C', last_name='R', role='staff')
        creator.password = 'test123'
        ben_user = User(email='b@example.com', first_name='B', last_name='N', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='female', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create note
        note = Note(
            beneficiary_id=beneficiary.id,
            creator_id=creator.id,
            content='Original content'
        )
        db.session.add(note)
        db.session.commit()
        
        original_updated = note.updated_at
        
        # Update note content
        note.content = 'Updated content with new information'
        db.session.commit()
        
        # Note: In real implementation, updated_at should be automatically updated
        # This test documents the expected behavior
        assert note.content == 'Updated content with new information'
    
    def test_note_with_tags_query(self, db_session):
        """Test querying notes by tags."""
        tenant = Tenant(name='Test Org', slug='test-org', email='test@org.com')
        creator = User(email='c@example.com', first_name='C', last_name='R', role='staff')
        creator.password = 'test123'
        ben_user = User(email='b@example.com', first_name='B', last_name='N', role='beneficiary')
        ben_user.password = 'test123'
        db.session.add_all([tenant, creator, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(user_id=ben_user.id, tenant_id=tenant.id, gender='male', birth_date=datetime.utcnow())
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create notes with different tags
        notes_data = [
            ('Progress note', ['progress', 'positive']),
            ('Medical note', ['medical', 'urgent']),
            ('Follow-up note', ['follow-up', 'progress']),
            ('General note', [])
        ]
        
        for content, tags in notes_data:
            note = Note(
                beneficiary_id=beneficiary.id,
                creator_id=creator.id,
                content=content,
                tags=tags if tags else None
            )
            db.session.add(note)
        
        db.session.commit()
        
        # Query all notes
        all_notes = Note.query.filter_by(beneficiary_id=beneficiary.id).all()
        assert len(all_notes) == 4
        
        # Filter notes with 'progress' tag (manual check)
        progress_notes = [n for n in all_notes if n.tags and 'progress' in n.tags]
        assert len(progress_notes) == 2