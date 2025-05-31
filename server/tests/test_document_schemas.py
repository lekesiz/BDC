"""Test document schemas for coverage."""
import pytest
from datetime import datetime
from marshmallow import ValidationError
from app.schemas.document import (
    DocumentSchema, 
    DocumentCreateSchema, 
    DocumentUpdateSchema,
    DocumentFilterSchema
)


class TestDocumentSchema:
    """Test DocumentSchema."""
    
    def test_document_schema_dump(self):
        """Test document schema serialization."""
        schema = DocumentSchema()
        data = {
            'id': 1,
            'title': 'Test Document',
            'description': 'A test document',
            'file_path': '/uploads/test.pdf',
            'file_type': 'pdf',
            'file_size': 1024,
            'document_type': 'report',
            'is_active': True,
            'upload_by': 1,
            'uploader_name': 'John Doe',
            'beneficiary_id': 2,
            'evaluation_id': 3,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = schema.dump(data)
        assert result['id'] == 1
        assert result['title'] == 'Test Document'
        assert result['document_type'] == 'report'
        assert result['file_path'] == '/uploads/test.pdf'
    
    def test_document_schema_load(self):
        """Test document schema deserialization."""
        schema = DocumentSchema()
        data = {
            'title': 'New Document',
            'description': 'Description here',
            'document_type': 'certificate',
            'is_active': True,
            'beneficiary_id': 1,
            'evaluation_id': 2
        }
        
        result = schema.load(data)
        assert result['title'] == 'New Document'
        assert result['document_type'] == 'certificate'
        # dump_only fields should not be in loaded data
        assert 'file_path' not in result
        assert 'id' not in result


class TestDocumentCreateSchema:
    """Test DocumentCreateSchema."""
    
    def test_create_schema_valid(self):
        """Test valid document creation data."""
        schema = DocumentCreateSchema()
        data = {
            'title': 'New Document',
            'description': 'A new document',
            'document_type': 'general',
            'beneficiary_id': 1,
            'evaluation_id': 2
        }
        
        result = schema.load(data)
        assert result['title'] == 'New Document'
        assert result['document_type'] == 'general'
    
    def test_create_schema_required_fields(self):
        """Test required field validation."""
        schema = DocumentCreateSchema()
        
        # Missing required title
        data = {
            'description': 'Missing title',
            'document_type': 'report'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'title' in exc_info.value.messages
        assert 'required' in str(exc_info.value.messages['title'][0]).lower()
    
    def test_create_schema_invalid_type(self):
        """Test document type validation."""
        schema = DocumentCreateSchema()
        
        # Invalid document type
        data = {
            'title': 'Invalid Type Doc',
            'document_type': 'invalid_type'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'document_type' in exc_info.value.messages
    
    def test_create_schema_minimal(self):
        """Test minimal valid data."""
        schema = DocumentCreateSchema()
        
        # Only required field
        data = {
            'title': 'Minimal Document'
        }
        
        result = schema.load(data)
        assert result['title'] == 'Minimal Document'
        assert len(result) == 1


class TestDocumentUpdateSchema:
    """Test DocumentUpdateSchema."""
    
    def test_update_schema_partial(self):
        """Test partial update."""
        schema = DocumentUpdateSchema()
        
        # Update only title
        data = {
            'title': 'Updated Title'
        }
        
        result = schema.load(data)
        assert result['title'] == 'Updated Title'
        assert len(result) == 1
    
    def test_update_schema_all_fields(self):
        """Test updating all fields."""
        schema = DocumentUpdateSchema()
        
        data = {
            'title': 'Updated Document',
            'description': 'Updated description',
            'document_type': 'assessment',
            'is_active': False,
            'beneficiary_id': 5,
            'evaluation_id': 6
        }
        
        result = schema.load(data)
        assert result['title'] == 'Updated Document'
        assert result['is_active'] is False
        assert result['document_type'] == 'assessment'
    
    def test_update_schema_empty(self):
        """Test empty update."""
        schema = DocumentUpdateSchema()
        
        # Empty update should be valid
        data = {}
        result = schema.load(data)
        assert result == {}
    
    def test_update_schema_invalid_type(self):
        """Test invalid document type in update."""
        schema = DocumentUpdateSchema()
        
        data = {
            'document_type': 'not_valid'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        
        assert 'document_type' in exc_info.value.messages


class TestDocumentFilterSchema:
    """Test DocumentFilterSchema."""
    
    def test_filter_schema_all_fields(self):
        """Test filter with all fields."""
        schema = DocumentFilterSchema()
        
        data = {
            'document_type': 'report',
            'beneficiary_id': 1,
            'evaluation_id': 2,
            'upload_by': 3,
            'search': 'test document'
        }
        
        result = schema.load(data)
        assert result['document_type'] == 'report'
        assert result['search'] == 'test document'
        assert result['beneficiary_id'] == 1
    
    def test_filter_schema_date_range(self):
        """Test date range filtering."""
        schema = DocumentFilterSchema()
        
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        
        data = {
            'start_date': start.isoformat(),
            'end_date': end.isoformat()
        }
        
        result = schema.load(data)
        assert isinstance(result['start_date'], datetime)
        assert isinstance(result['end_date'], datetime)
        assert result['start_date'].year == 2024
    
    def test_filter_schema_empty(self):
        """Test empty filter."""
        schema = DocumentFilterSchema()
        
        # Empty filter should be valid
        data = {}
        result = schema.load(data)
        assert result == {}
    
    def test_filter_schema_search_only(self):
        """Test search-only filter."""
        schema = DocumentFilterSchema()
        
        data = {
            'search': 'important document'
        }
        
        result = schema.load(data)
        assert result['search'] == 'important document'
        assert len(result) == 1