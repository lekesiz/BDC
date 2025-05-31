import pytest
from datetime import datetime
from app import db
from app.models import Document, User, Beneficiary, Evaluation


class TestDocumentModelSimple:
    """Simplified test cases for the Document model."""
    
    def test_document_creation(self, db_session):
        """Test creating a new document."""
        # Create uploader user
        uploader = User(
            email='uploader@example.com',
            first_name='Test',
            last_name='Uploader',
            role='staff'
        )
        db.session.add(uploader)
        db.session.commit()
        
        # Create document
        document = Document(
            title='Test Document',
            file_path='/uploads/2024/test_document.pdf',
            file_type='pdf',
            upload_by=uploader.id
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.id is not None
        assert document.title == 'Test Document'
        assert document.file_path == '/uploads/2024/test_document.pdf'
        assert document.upload_by == uploader.id
    
    def test_document_with_all_fields(self, db_session):
        """Test document with all optional fields."""
        # Create uploader and beneficiary
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([uploader, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            gender='male',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        document = Document(
            title='Complete Document',
            description='A document with all fields',
            file_path='/uploads/complete.pdf',
            file_type='pdf',
            file_size=1048576,  # 1MB
            document_type='contract',
            upload_by=uploader.id,
            beneficiary_id=beneficiary.id
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.description == 'A document with all fields'
        assert document.file_size == 1048576
        assert document.document_type == 'contract'
        assert document.beneficiary_id == beneficiary.id
    
    def test_document_defaults(self, db_session):
        """Test document default values."""
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        db.session.add(uploader)
        db.session.commit()
        
        document = Document(
            title='Default Document',
            file_path='/uploads/default.txt',
            upload_by=uploader.id
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.is_active is True
        assert document.created_at is not None
        assert document.updated_at is not None
    
    def test_document_relationships(self, db_session):
        """Test document relationships."""
        # Create users and beneficiary
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([uploader, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            gender='female',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        document = Document(
            title='Related Document',
            file_path='/uploads/related.pdf',
            upload_by=uploader.id,
            beneficiary_id=beneficiary.id
        )
        db.session.add(document)
        db.session.commit()
        
        # Test relationships
        assert document.uploader == uploader
        assert document.beneficiary == beneficiary
    
    def test_document_file_types(self, db_session):
        """Test various file types."""
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        db.session.add(uploader)
        db.session.commit()
        
        file_types = ['pdf', 'jpg', 'png', 'docx', 'xlsx', 'txt']
        
        for file_type in file_types:
            doc = Document(
                title=f'Document {file_type.upper()}',
                file_path=f'/uploads/test.{file_type}',
                file_type=file_type,
                upload_by=uploader.id
            )
            db.session.add(doc)
        
        db.session.commit()
        
        # Verify all documents were created
        docs = Document.query.all()
        assert len(docs) == len(file_types)
        
        # Query by file type
        pdf_docs = Document.query.filter_by(file_type='pdf').all()
        assert len(pdf_docs) == 1
        assert pdf_docs[0].title == 'Document PDF'
    
    def test_document_types(self, db_session):
        """Test different document types."""
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        db.session.add(uploader)
        db.session.commit()
        
        document_types = [
            'contract', 'identification', 'medical_record',
            'financial_statement', 'certificate', 'report', 'other'
        ]
        
        for doc_type in document_types:
            doc = Document(
                title=f'{doc_type.title()} Document',
                file_path=f'/uploads/{doc_type}.pdf',
                document_type=doc_type,
                upload_by=uploader.id
            )
            db.session.add(doc)
        
        db.session.commit()
        
        # Query by document type
        contracts = Document.query.filter_by(document_type='contract').all()
        assert len(contracts) == 1
        assert contracts[0].title == 'Contract Document'
    
    def test_document_with_evaluation(self, db_session):
        """Test document associated with evaluation."""
        # Create required entities
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        trainer = User(email='trainer@example.com', first_name='T', last_name='R', role='trainer')
        ben_user = User(email='ben@example.com', first_name='B', last_name='N', role='beneficiary')
        db.session.add_all([uploader, trainer, ben_user])
        db.session.commit()
        
        beneficiary = Beneficiary(
            user_id=ben_user.id,
            gender='male',
            birth_date=datetime.utcnow()
        )
        db.session.add(beneficiary)
        db.session.commit()
        
        # Create evaluation
        evaluation = Evaluation(
            beneficiary_id=beneficiary.id,
            trainer_id=trainer.id,
            score=85,
            status='completed'
        )
        db.session.add(evaluation)
        db.session.commit()
        
        # Create document linked to evaluation
        document = Document(
            title='Evaluation Report',
            file_path='/uploads/eval_report.pdf',
            upload_by=uploader.id,
            evaluation_id=evaluation.id
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.evaluation_id == evaluation.id
        assert document.evaluation == evaluation
    
    def test_document_soft_delete(self, db_session):
        """Test document soft delete."""
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        db.session.add(uploader)
        db.session.commit()
        
        document = Document(
            title='To Delete',
            file_path='/uploads/delete_me.pdf',
            upload_by=uploader.id
        )
        db.session.add(document)
        db.session.commit()
        doc_id = document.id
        
        # Soft delete
        document.is_active = False
        db.session.commit()
        
        # Verify still in database but marked as inactive
        deleted_doc = Document.query.get(doc_id)
        assert deleted_doc is not None
        assert deleted_doc.is_active is False
    
    def test_document_file_sizes(self, db_session):
        """Test document file size storage."""
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        db.session.add(uploader)
        db.session.commit()
        
        sizes = [
            (1024, 'small.txt'),  # 1KB
            (1048576, 'medium.pdf'),  # 1MB
            (10485760, 'large.zip')  # 10MB
        ]
        
        for size, filename in sizes:
            doc = Document(
                title=filename,
                file_path=f'/uploads/{filename}',
                file_size=size,
                upload_by=uploader.id
            )
            db.session.add(doc)
        
        db.session.commit()
        
        # Query and verify sizes
        small_doc = Document.query.filter_by(title='small.txt').first()
        assert small_doc.file_size == 1024
        
        large_doc = Document.query.filter_by(title='large.zip').first()
        assert large_doc.file_size == 10485760
    
    def test_document_query_by_beneficiary(self, db_session):
        """Test querying documents by beneficiary."""
        # Create users
        uploader = User(email='up@example.com', first_name='U', last_name='P', role='staff')
        ben_user1 = User(email='ben1@example.com', first_name='B1', last_name='N1', role='beneficiary')
        ben_user2 = User(email='ben2@example.com', first_name='B2', last_name='N2', role='beneficiary')
        db.session.add_all([uploader, ben_user1, ben_user2])
        db.session.commit()
        
        # Create beneficiaries
        beneficiary1 = Beneficiary(user_id=ben_user1.id, gender='male', birth_date=datetime.utcnow())
        beneficiary2 = Beneficiary(user_id=ben_user2.id, gender='female', birth_date=datetime.utcnow())
        db.session.add_all([beneficiary1, beneficiary2])
        db.session.commit()
        
        # Create documents for beneficiary1
        for i in range(3):
            doc = Document(
                title=f'Ben1 Document {i}',
                file_path=f'/uploads/ben1_doc_{i}.pdf',
                upload_by=uploader.id,
                beneficiary_id=beneficiary1.id
            )
            db.session.add(doc)
        
        # Create document for beneficiary2
        doc2 = Document(
            title='Ben2 Document',
            file_path='/uploads/ben2_doc.pdf',
            upload_by=uploader.id,
            beneficiary_id=beneficiary2.id
        )
        db.session.add(doc2)
        
        # Create document without beneficiary
        general_doc = Document(
            title='General Document',
            file_path='/uploads/general.pdf',
            upload_by=uploader.id
        )
        db.session.add(general_doc)
        db.session.commit()
        
        # Query beneficiary1 documents
        ben1_docs = Document.query.filter_by(
            beneficiary_id=beneficiary1.id,
            is_active=True
        ).all()
        assert len(ben1_docs) == 3
        
        # Query all documents
        all_docs = Document.query.all()
        assert len(all_docs) == 5