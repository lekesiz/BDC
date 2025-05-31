import os
import io
import pytest
from botocore.stub import Stubber
from unittest.mock import patch, MagicMock

from app import create_app
from app.services.storage_service import storage_service, s3_client, S3_BUCKET, USE_S3

pytestmark = pytest.mark.skipif(not USE_S3, reason="S3 backend not enabled")


@pytest.fixture()
def s3_stub():
    with Stubber(s3_client) as stubber:
        # Default response for uploading files
        stubber.add_response(
            'upload_fileobj', 
            {},  # Empty response for successful upload
            {
                'Bucket': S3_BUCKET,
                'Key': 'test.txt',
                'ExtraArgs': {'ACL': 'private'}
            }
        )
        
        # Allow additional responses to be added
        yield stubber


@pytest.fixture()
def app_ctx(monkeypatch, s3_stub):
    os.environ['STORAGE_BACKEND'] = 's3'
    os.environ['AWS_ACCESS_KEY_ID'] = 'test_key'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret'
    os.environ['S3_BUCKET'] = 'test-bucket'
    
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    ctx.pop()
    os.environ.pop('STORAGE_BACKEND')
    os.environ.pop('AWS_ACCESS_KEY_ID')
    os.environ.pop('AWS_SECRET_ACCESS_KEY')
    os.environ.pop('S3_BUCKET')


def test_save_file_s3(app_ctx, s3_stub):
    """Test saving a file to S3."""
    fake_file = io.BytesIO(b'hello world')
    fake_file.filename = 'test.txt'
    
    path, err = storage_service.save_file(fake_file, 'documents', 'document')
    
    assert err is None
    assert path.startswith(f's3://{S3_BUCKET}/')
    assert 'test.txt' in path
    s3_stub.assert_no_pending_responses()


def test_save_file_s3_with_invalid_extension(app_ctx):
    """Test saving a file with invalid extension to S3."""
    fake_file = io.BytesIO(b'hello world')
    fake_file.filename = 'test.invalid'
    
    path, err = storage_service.save_file(fake_file, 'documents', 'document')
    
    assert path is None
    assert 'Invalid file type' in err


def test_save_file_s3_with_oversized_file(app_ctx):
    """Test saving an oversized file to S3."""
    # Create a file larger than MAX_DOCUMENT_SIZE
    fake_file = io.BytesIO(b'x' * (storage_service.MAX_DOCUMENT_SIZE + 1))
    fake_file.filename = 'large.pdf'
    
    path, err = storage_service.save_file(fake_file, 'documents', 'document')
    
    assert path is None
    assert 'File size too large' in err


@patch('app.services.storage_service.s3_client')
def test_s3_upload_error(mock_s3_client, app_ctx):
    """Test handling of S3 upload errors."""
    # Configure mock to raise an exception
    mock_s3_client.upload_fileobj.side_effect = Exception("S3 upload failed")
    
    fake_file = io.BytesIO(b'hello world')
    fake_file.filename = 'test.txt'
    
    # Test exception handling
    with pytest.raises(Exception) as excinfo:
        storage_service.save_file(fake_file, 'documents', 'document')
    
    assert "S3 upload failed" in str(excinfo.value)


def test_save_profile_picture_s3(app_ctx, s3_stub):
    """Test saving a profile picture to S3."""
    s3_stub.add_response(
        'upload_fileobj', 
        {},  # Empty response for successful upload
        {
            'Bucket': S3_BUCKET,
            'Key': pytest.param(lambda x: x.endswith('.jpg') or x.endswith('.png'), None),
            'ExtraArgs': {'ACL': 'private'}
        }
    )
    
    # Mock image optimization since we're testing S3 upload
    with patch('app.services.storage_service.Image', MagicMock()):
        fake_image = io.BytesIO(b'fake image data')
        fake_image.filename = 'profile.jpg'
        
        path, err = storage_service.save_profile_picture(fake_image, 1)
        
        assert err is None
        assert path.startswith(f's3://{S3_BUCKET}/')
        s3_stub.assert_no_pending_responses()


def test_save_document_s3(app_ctx, s3_stub):
    """Test saving a document to S3."""
    s3_stub.add_response(
        'upload_fileobj', 
        {},  # Empty response for successful upload
        {
            'Bucket': S3_BUCKET,
            'Key': pytest.param(lambda x: x.endswith('.pdf'), None),
            'ExtraArgs': {'ACL': 'private'}
        }
    )
    
    fake_doc = io.BytesIO(b'fake pdf data')
    fake_doc.filename = 'document.pdf'
    
    path, err = storage_service.save_document(fake_doc, 'reports')
    
    assert err is None
    assert path.startswith(f's3://{S3_BUCKET}/')
    s3_stub.assert_no_pending_responses()