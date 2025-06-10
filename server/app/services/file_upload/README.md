# Secure File Upload System for BDC Project

This module provides a comprehensive file upload security system with advanced features for protecting against various file-based attacks.

## Features

### 1. Advanced File Type Detection
- Uses `python-magic` for accurate MIME type detection based on file content
- Prevents file type spoofing attacks
- Validates both file extensions and actual content

### 2. Virus Scanning Integration
- Integrates with ClamAV for real-time virus scanning
- Automatically quarantines infected files
- Configurable scanning policies

### 3. Image Processing and Sanitization
- Strips potentially dangerous EXIF metadata
- Validates image integrity
- Resizes large images to prevent resource exhaustion
- Generates secure thumbnails
- Detects and blocks malicious SVG content

### 4. Secure Storage with Encryption
- Optional AES-256 encryption for stored files
- Secure filename generation to prevent path traversal
- Organized directory structure with tenant isolation

### 5. CDN/S3 Integration
- Seamless integration with AWS S3
- CDN support for fast content delivery
- Automatic failover between local and cloud storage
- Signed URLs for temporary access

### 6. File Versioning and Audit Trail
- Complete audit trail of all file operations
- Version control with configurable retention
- User activity tracking and statistics
- Compliance-ready logging

## Installation

1. Install required Python packages:
```bash
pip install python-magic pillow pillow-heif boto3 cryptography
```

2. Install ClamAV (optional but recommended):
```bash
# Ubuntu/Debian
sudo apt-get install clamav clamav-daemon

# macOS
brew install clamav

# Start ClamAV daemon
sudo systemctl start clamav-daemon
```

3. Run database migrations:
```bash
# Copy the migration functions from migrations.py to a new Alembic migration
alembic revision -m "Add file upload audit tables"
alembic upgrade head
```

## Configuration

Set the following environment variables:

```bash
# Storage paths
UPLOAD_FOLDER=/path/to/uploads
TEMP_FOLDER=/tmp/upload_temp
QUARANTINE_FOLDER=/tmp/quarantine

# S3 Configuration (optional)
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
CDN_URL=https://cdn.example.com

# ClamAV Configuration
CLAMAV_HOST=localhost
CLAMAV_PORT=3310
ENABLE_VIRUS_SCAN=True

# Security Configuration
ENABLE_ENCRYPTION=True
FILE_ENCRYPTION_KEY=your-secure-encryption-key
```

## Usage

### Basic File Upload

```python
from app.services.file_upload import FileUploadService

# Initialize service
upload_service = FileUploadService()

# Upload a file
result = upload_service.upload_file(
    file=request.files['file'],
    user_id='user123',
    tenant_id='tenant456',
    metadata={'description': 'Profile photo'}
)

# Access upload results
file_id = result['file_info']['file_id']
cdn_url = result['file_info']['cdn_url']
```

### API Integration

Register the provided blueprint in your Flask app:

```python
from app.services.file_upload.api_example import file_upload_bp

app.register_blueprint(file_upload_bp, url_prefix='/api/files')
```

Available endpoints:
- `POST /api/files/upload` - Upload a file
- `GET /api/files/download/<file_id>` - Download a file
- `DELETE /api/files/delete/<file_id>` - Delete a file
- `PUT /api/files/update/<file_id>` - Update file (new version)
- `GET /api/files/history/<file_id>` - Get file history
- `GET /api/files/stats` - Get user upload statistics
- `POST /api/files/signed-url/<file_id>` - Create temporary access URL

### Advanced Features

#### Image Processing
```python
# Process image with watermark
from app.services.file_upload import ImageProcessor

processor = ImageProcessor(config)
processor.add_watermark(
    img_path='/path/to/image.jpg',
    watermark_text='© 2024 BDC',
    output_path='/path/to/watermarked.jpg'
)
```

#### File Versioning
```python
# Update file with new version
result = upload_service.update_file(
    file_id='file123',
    file=new_file,
    user_id='user123',
    comment='Updated logo with new branding'
)
```

#### Audit Trail
```python
# Get file history
history = upload_service.get_file_history('file123')

# Get user statistics
stats = upload_service.get_user_stats('user123', 'tenant456')
```

## Security Best Practices

1. **Always enable virus scanning** in production environments
2. **Use encryption** for sensitive files
3. **Regularly update** ClamAV virus definitions
4. **Monitor audit logs** for suspicious activity
5. **Set appropriate file size limits** based on your use case
6. **Use CDN signed URLs** for temporary file access
7. **Implement rate limiting** on upload endpoints
8. **Regular cleanup** of temporary and quarantine folders

## File Type Configuration

Customize allowed file types in `config.py`:

```python
ALLOWED_FILE_TYPES = {
    'image': ['image/jpeg', 'image/png', 'image/gif'],
    'document': ['application/pdf', 'application/msword'],
    # Add more as needed
}
```

## Error Handling

The system provides specific exceptions for different error scenarios:

- `FileSizeExceededException` - File too large
- `FileTypeNotAllowedException` - Invalid file type
- `VirusDetectedException` - Malware detected
- `StorageException` - Storage operation failed
- `EncryptionException` - Encryption/decryption failed

## Maintenance

### Cleanup Tasks

Add to your scheduled tasks:

```python
# Clean temporary files older than 1 hour
upload_service.cleanup_temp_files()

# Clean audit logs older than retention period
upload_service.cleanup_old_audits()
```

### Monitoring

Monitor these metrics:
- Upload success/failure rates
- Virus detection rates
- Storage usage by user/tenant
- Average file sizes and types
- Processing times

## Testing

Run the test suite:

```bash
pytest app/services/file_upload/tests/
```

## Performance Considerations

1. **Image processing** is CPU-intensive - consider using a task queue
2. **Virus scanning** adds latency - implement async scanning for large files
3. **S3 uploads** can be slow - use multipart uploads for large files
4. **Encryption** adds overhead - balance security with performance needs

## License

This module is part of the BDC project and follows the same license terms.