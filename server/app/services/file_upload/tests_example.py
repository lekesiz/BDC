"""Example tests for file upload security system."""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from werkzeug.datastructures import FileStorage

from app.services.file_upload import (
    FileUploadService,
    FileScanner,
    ImageProcessor,
    StorageManager,
    FileUploadConfig
)
from app.services.file_upload.exceptions import (
    FileTypeNotAllowedException,
    VirusDetectedException,
    FileSizeExceededException
)


class TestFileScanner(unittest.TestCase):
    """Test file scanner functionality."""
    
    def setUp(self):
        self.config = FileUploadConfig()
        self.scanner = FileScanner(self.config)
        
    def test_detect_mime_type(self):
        """Test MIME type detection."""
        # Create a test JPEG file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            # JPEG magic bytes
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')
            f.flush()
            
            mime_type = self.scanner._detect_mime_type(f.name)
            self.assertEqual(mime_type, 'image/jpeg')
            
            os.unlink(f.name)
    
    def test_validate_blocked_extension(self):
        """Test that blocked extensions are rejected."""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
            f.write(b'MZ')  # PE executable header
            f.flush()
            
            with self.assertRaises(FileTypeNotAllowedException):
                self.scanner._validate_file_type(f.name, 'application/x-executable')
            
            os.unlink(f.name)
    
    @patch('socket.socket')
    def test_virus_scan_clean_file(self, mock_socket):
        """Test virus scanning for clean file."""
        # Mock ClamAV response
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b'stream: OK\0'
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        with tempfile.NamedTemporaryFile() as f:
            result = self.scanner._scan_for_virus(f.name)
            
            self.assertTrue(result['scanned'])
            self.assertTrue(result['clean'])
    
    @patch('socket.socket')
    def test_virus_scan_infected_file(self, mock_socket):
        """Test virus scanning for infected file."""
        # Mock ClamAV response for infected file
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b'stream: Eicar-Test-Signature FOUND\0'
        mock_socket.return_value.__enter__.return_value = mock_sock
        
        with tempfile.NamedTemporaryFile() as f:
            with self.assertRaises(VirusDetectedException):
                self.scanner._scan_for_virus(f.name)


class TestImageProcessor(unittest.TestCase):
    """Test image processing functionality."""
    
    def setUp(self):
        self.config = FileUploadConfig()
        self.processor = ImageProcessor(self.config)
    
    def test_process_valid_image(self):
        """Test processing a valid image."""
        # Create a simple test image
        from PIL import Image
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as input_file:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
                # Create test image
                img = Image.new('RGB', (100, 100), color='red')
                img.save(input_file.name)
                
                # Process image
                result = self.processor.process_image(
                    input_file.name,
                    output_file.name
                )
                
                self.assertIn('processed_path', result)
                self.assertIn('thumbnails', result)
                self.assertEqual(result['format'], 'PNG')
                
                # Cleanup
                os.unlink(input_file.name)
                os.unlink(output_file.name)
                for thumb_path in result['thumbnails'].values():
                    if os.path.exists(thumb_path):
                        os.unlink(thumb_path)
    
    def test_strip_exif_data(self):
        """Test EXIF data stripping."""
        from PIL import Image
        
        # Create image with EXIF data
        img = Image.new('RGB', (100, 100), color='blue')
        exif_data = img.getexif()
        exif_data[0x0112] = 3  # Orientation
        
        # Strip EXIF
        stripped_img = self.processor._strip_exif_data(img)
        
        # Verify EXIF is removed
        self.assertFalse(hasattr(stripped_img, '_getexif') or 
                        (hasattr(stripped_img, '_getexif') and stripped_img._getexif()))


class TestStorageManager(unittest.TestCase):
    """Test storage manager functionality."""
    
    def setUp(self):
        self.config = FileUploadConfig()
        self.config.ENABLE_ENCRYPTION = False  # Disable for testing
        self.storage = StorageManager(self.config)
    
    def test_generate_secure_filename(self):
        """Test secure filename generation."""
        filename = self.storage._generate_secure_filename('/path/to/test.jpg')
        
        # Should be UUID + extension
        self.assertTrue(filename.endswith('.jpg'))
        self.assertEqual(len(filename), 36)  # 32 char UUID + 4 char extension
    
    def test_create_storage_path(self):
        """Test storage path creation."""
        path = self.storage._create_storage_path(
            'image',
            'user123',
            'test.jpg'
        )
        
        self.assertIn('image', path)
        self.assertIn('user123', path)
        self.assertIn('test.jpg', path)
    
    @patch('boto3.client')
    def test_s3_upload(self, mock_boto):
        """Test S3 upload functionality."""
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_boto.return_value = mock_s3
        
        self.storage.s3_client = mock_s3
        self.config.S3_BUCKET = 'test-bucket'
        
        with tempfile.NamedTemporaryFile() as f:
            url = self.storage._upload_to_s3(f.name, 'image', 'user123')
            
            self.assertIsNotNone(url)
            mock_s3.upload_file.assert_called_once()


class TestFileUploadService(unittest.TestCase):
    """Test main file upload service."""
    
    def setUp(self):
        self.config = FileUploadConfig()
        self.config.ENABLE_VIRUS_SCAN = False  # Disable for testing
        self.config.ENABLE_ENCRYPTION = False
        self.service = FileUploadService(self.config)
    
    @patch('app.services.file_upload.audit_logger.db')
    def test_upload_valid_file(self, mock_db):
        """Test uploading a valid file."""
        # Create mock file
        file_data = b'Test file content'
        file = FileStorage(
            stream=BytesIO(file_data),
            filename='test.txt',
            content_type='text/plain'
        )
        
        # Mock database session
        mock_db.session = MagicMock()
        
        # Upload file
        result = self.service.upload_file(
            file=file,
            user_id='user123',
            tenant_id='tenant456'
        )
        
        self.assertTrue(result['success'])
        self.assertIn('file_info', result)
        self.assertEqual(result['file_info']['original_filename'], 'test.txt')
    
    def test_upload_oversized_file(self):
        """Test uploading an oversized file."""
        # Create large mock file
        self.config.MAX_FILE_SIZE = 1024  # 1 KB limit
        
        file_data = b'X' * 2048  # 2 KB file
        file = FileStorage(
            stream=BytesIO(file_data),
            filename='large.txt',
            content_type='text/plain'
        )
        
        with self.assertRaises(FileSizeExceededException):
            self.service.upload_file(
                file=file,
                user_id='user123',
                tenant_id='tenant456'
            )
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        dangerous_names = [
            '../../../etc/passwd',
            'file<script>.txt',
            'file name with spaces.doc',
            'file@#$%^&*.txt'
        ]
        
        for name in dangerous_names:
            sanitized = self.service._sanitize_filename(name)
            
            # Should not contain path traversal
            self.assertNotIn('..', sanitized)
            # Should not contain special characters
            self.assertNotIn('<', sanitized)
            self.assertNotIn('>', sanitized)
            # Spaces should be replaced
            self.assertNotIn(' ', sanitized)


class TestFileUploadIntegration(unittest.TestCase):
    """Integration tests for file upload system."""
    
    def setUp(self):
        self.config = FileUploadConfig()
        self.config.ENABLE_VIRUS_SCAN = False
        self.config.ENABLE_ENCRYPTION = True
        self.config.ENCRYPTION_KEY = 'test-encryption-key'
        self.service = FileUploadService(self.config)
    
    @patch('app.services.file_upload.audit_logger.db')
    def test_complete_upload_workflow(self, mock_db):
        """Test complete upload workflow with encryption."""
        # Mock database
        mock_db.session = MagicMock()
        
        # Create test image
        from PIL import Image
        img = Image.new('RGB', (200, 200), color='green')
        
        # Save to BytesIO
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Create file storage
        file = FileStorage(
            stream=img_bytes,
            filename='test_image.png',
            content_type='image/png'
        )
        
        # Upload file
        result = self.service.upload_file(
            file=file,
            user_id='user123',
            tenant_id='tenant456',
            metadata={'purpose': 'profile_photo'}
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['file_info']['file_category'], 'image')
        self.assertTrue(result['file_info']['encrypted'])
        self.assertIn('thumbnails', result['file_info'])


if __name__ == '__main__':
    unittest.main()