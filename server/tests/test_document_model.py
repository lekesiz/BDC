"""Tests for Document model."""

import pytest
from datetime import datetime
from app.models.document import Document
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.evaluation import Evaluation
from app.extensions import db


class TestDocumentModel:
    """Test the Document model."""

    @pytest.fixture
    def setup_data(self, db_session):
        """Set up test data."""
        import uuid
        
        # Create user
        user = User(
            email=f"doc_uploader_{uuid.uuid4().hex[:8]}@example.com",
            first_name="Doc",
            last_name="Uploader",
            role="staff"
        )
        user.password = "password123"
        db.session.add(user)
        
        # Create beneficiary
        beneficiary = Beneficiary(
            first_name="Ben",
            last_name="Eficiary",
            email=f"beneficiary_{uuid.uuid4().hex[:8]}@example.com",
            phone="+1234567890",
            address="123 Test St"
        )
        db.session.add(beneficiary)
        
        # Create evaluation
        evaluation = Evaluation(
            title="Test Evaluation",
            type="assessment",
            status="completed"
        )
        db.session.add(evaluation)
        
        db.session.commit()
        
        return {
            "user": user,
            "beneficiary": beneficiary,
            "evaluation": evaluation
        }

    def test_document_creation(self, db_session, setup_data):
        """Test creating a document."""
        document = Document(
            title="Test Document",
            description="This is a test document",
            file_path="/uploads/test_document.pdf",
            file_type="pdf",
            file_size=1024576,
            document_type="report",
            is_active=True,
            upload_by=setup_data["user"].id,
            beneficiary_id=setup_data["beneficiary"].id,
            evaluation_id=setup_data["evaluation"].id
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.id is not None
        assert document.title == "Test Document"
        assert document.description == "This is a test document"
        assert document.file_path == "/uploads/test_document.pdf"
        assert document.file_type == "pdf"
        assert document.file_size == 1024576
        assert document.document_type == "report"
        assert document.is_active is True
        assert document.upload_by == setup_data["user"].id
        assert document.beneficiary_id == setup_data["beneficiary"].id
        assert document.evaluation_id == setup_data["evaluation"].id
        assert isinstance(document.created_at, datetime)
        assert isinstance(document.updated_at, datetime)

    def test_document_defaults(self, db_session, setup_data):
        """Test document with default values."""
        document = Document(
            title="Minimal Document",
            file_path="/uploads/minimal.txt",
            file_type="txt",
            file_size=1024,
            upload_by=setup_data["user"].id
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.description is None
        assert document.document_type == "general"
        assert document.is_active is True
        assert document.beneficiary_id is None
        assert document.evaluation_id is None

    def test_document_to_dict(self, db_session, setup_data):
        """Test converting document to dictionary."""
        document = Document(
            title="Dict Test Document",
            description="Testing to_dict method",
            file_path="/uploads/dict_test.pdf",
            file_type="pdf",
            file_size=2048576,
            document_type="certificate",
            is_active=True,
            upload_by=setup_data["user"].id,
            beneficiary_id=setup_data["beneficiary"].id,
            evaluation_id=setup_data["evaluation"].id
        )
        db.session.add(document)
        db.session.commit()
        
        doc_dict = document.to_dict()
        
        assert doc_dict['id'] == document.id
        assert doc_dict['title'] == "Dict Test Document"
        assert doc_dict['description'] == "Testing to_dict method"
        assert doc_dict['file_path'] == "/uploads/dict_test.pdf"
        assert doc_dict['file_type'] == "pdf"
        assert doc_dict['file_size'] == 2048576
        assert doc_dict['document_type'] == "certificate"
        assert doc_dict['is_active'] is True
        assert doc_dict['upload_by'] == setup_data["user"].id
        assert doc_dict['uploader_name'] == "Doc Uploader"
        assert doc_dict['beneficiary_id'] == setup_data["beneficiary"].id
        assert doc_dict['evaluation_id'] == setup_data["evaluation"].id
        assert doc_dict['created_at'] == document.created_at.isoformat()
        assert doc_dict['updated_at'] == document.updated_at.isoformat()

    def test_document_to_dict_without_uploader(self, db_session):
        """Test converting document to dictionary when uploader is deleted."""
        import uuid
        
        # Create user
        user = User(
            email=f"temp_user_{uuid.uuid4().hex[:8]}@example.com",
            first_name="Temp",
            last_name="User",
            role="staff"
        )
        user.password = "password123"
        db.session.add(user)
        db.session.commit()
        
        user_id = user.id
        
        # Create document
        document = Document(
            title="Orphaned Document",
            file_path="/uploads/orphaned.pdf",
            file_type="pdf",
            file_size=1024,
            upload_by=user_id
        )
        db.session.add(document)
        db.session.commit()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        # Detach and reattach to simulate fresh load
        db.session.expunge(document)
        document = db.session.query(Document).filter_by(id=document.id).first()
        
        doc_dict = document.to_dict()
        assert doc_dict['uploader_name'] is None

    def test_document_repr(self, db_session, setup_data):
        """Test document string representation."""
        document = Document(
            title="Repr Test Document",
            file_path="/uploads/repr_test.pdf",
            file_type="pdf",
            file_size=1024,
            upload_by=setup_data["user"].id
        )
        db.session.add(document)
        db.session.commit()
        
        assert repr(document) == '<Document Repr Test Document>'

    def test_document_relationships(self, db_session, setup_data):
        """Test document relationships."""
        document = Document(
            title="Related Document",
            file_path="/uploads/related.pdf",
            file_type="pdf",
            file_size=1024,
            upload_by=setup_data["user"].id,
            beneficiary_id=setup_data["beneficiary"].id,
            evaluation_id=setup_data["evaluation"].id
        )
        db.session.add(document)
        db.session.commit()
        
        # Test forward relationships
        assert document.uploader == setup_data["user"]
        assert document.beneficiary == setup_data["beneficiary"]
        assert document.evaluation == setup_data["evaluation"]
        
        # Test backward relationships
        assert document in setup_data["user"].uploaded_documents
        assert document in setup_data["beneficiary"].documents
        assert document in setup_data["evaluation"].documents

    def test_document_inactive(self, db_session, setup_data):
        """Test inactive document."""
        document = Document(
            title="Inactive Document",
            file_path="/uploads/inactive.pdf",
            file_type="pdf",
            file_size=1024,
            upload_by=setup_data["user"].id,
            is_active=False
        )
        db.session.add(document)
        db.session.commit()
        
        assert document.is_active is False

    def test_document_update(self, db_session, setup_data):
        """Test updating document."""
        document = Document(
            title="Original Title",
            file_path="/uploads/original.pdf",
            file_type="pdf",
            file_size=1024,
            upload_by=setup_data["user"].id
        )
        db.session.add(document)
        db.session.commit()
        
        original_created = document.created_at
        
        # Update document
        document.title = "Updated Title"
        document.description = "Added description"
        document.document_type = "updated_type"
        document.is_active = False
        db.session.commit()
        
        assert document.title == "Updated Title"
        assert document.description == "Added description"
        assert document.document_type == "updated_type"
        assert document.is_active is False
        assert document.created_at == original_created