"""Storage service for file uploads and downloads."""

import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
import magic

class StorageService:
    """Service for handling file storage operations."""
    
    # Allowed file extensions for different types
    ALLOWED_IMAGES = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_DOCUMENTS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv'}
    ALLOWED_VIDEOS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
    
    # Maximum file sizes (in bytes)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    def __init__(self, app=None):
        """Initialize storage service."""
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize app configuration."""
        self.app = app
        self.upload_folder = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        self.create_upload_directories()
    
    def create_upload_directories(self):
        """Create necessary upload directories."""
        directories = [
            'profile_pictures',
            'documents',
            'reports',
            'evaluations',
            'attachments'
        ]
        
        for directory in directories:
            path = os.path.join(self.upload_folder, directory)
            os.makedirs(path, exist_ok=True)
    
    def allowed_file(self, filename, file_type='document'):
        """Check if file extension is allowed."""
        if not '.' in filename:
            return False
            
        ext = filename.rsplit('.', 1)[1].lower()
        
        if file_type == 'image':
            return ext in self.ALLOWED_IMAGES
        elif file_type == 'document':
            return ext in self.ALLOWED_DOCUMENTS
        elif file_type == 'video':
            return ext in self.ALLOWED_VIDEOS
        else:
            return ext in (self.ALLOWED_IMAGES | self.ALLOWED_DOCUMENTS | self.ALLOWED_VIDEOS)
    
    def validate_file_size(self, file_size, file_type='document'):
        """Validate file size based on type."""
        if file_type == 'image':
            return file_size <= self.MAX_IMAGE_SIZE
        elif file_type == 'document':
            return file_size <= self.MAX_DOCUMENT_SIZE
        elif file_type == 'video':
            return file_size <= self.MAX_VIDEO_SIZE
        return False
    
    def generate_unique_filename(self, original_filename):
        """Generate unique filename to avoid collisions."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_string = str(uuid.uuid4())[:8]
        secure_name = secure_filename(original_filename)
        
        name, ext = os.path.splitext(secure_name)
        return f"{name}_{timestamp}_{random_string}{ext}"
    
    def save_file(self, file, directory, file_type='document'):
        """Save uploaded file to specified directory."""
        if not file:
            return None, 'No file provided'
            
        # Check if filename is present
        if file.filename == '':
            return None, 'No file selected'
            
        # Validate file type
        if not self.allowed_file(file.filename, file_type):
            return None, f'Invalid file type for {file_type}'
            
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if not self.validate_file_size(file_size, file_type):
            return None, 'File size too large'
            
        # Generate unique filename
        filename = self.generate_unique_filename(file.filename)
        
        # Save file
        file_path = os.path.join(self.upload_folder, directory, filename)
        file.save(file_path)
        
        # Generate relative URL
        relative_path = f"/static/uploads/{directory}/{filename}"
        
        return relative_path, None
    
    def save_profile_picture(self, file, user_id):
        """Save and optimize profile picture."""
        if not file:
            return None, 'No file provided'
            
        # Validate image file
        result, error = self.save_file(file, 'profile_pictures', 'image')
        if error:
            return None, error
            
        # Optimize image
        try:
            file_path = os.path.join(self.app.root_path, result.lstrip('/'))
            
            # Open and optimize image
            img = Image.open(file_path)
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1])
                img = rgb_img
            
            # Resize image if too large
            max_size = (300, 300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(file_path, 'JPEG', quality=85, optimize=True)
            
            return result, None
            
        except Exception as e:
            return None, f'Error processing image: {str(e)}'
    
    def save_document(self, file, category='general'):
        """Save document file."""
        # Create subdirectory for category
        directory = f"documents/{category}"
        full_path = os.path.join(self.upload_folder, directory)
        os.makedirs(full_path, exist_ok=True)
        
        return self.save_file(file, directory, 'document')
    
    def delete_file(self, file_path):
        """Delete file from storage."""
        try:
            # Convert relative URL to absolute path
            if file_path.startswith('/static/'):
                file_path = file_path.replace('/static/', '')
                full_path = os.path.join(self.app.root_path, 'static', file_path)
            else:
                full_path = os.path.join(self.app.root_path, file_path)
            
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
            
        except Exception as e:
            return False
    
    def get_file_info(self, file_path):
        """Get file information."""
        try:
            # Convert relative URL to absolute path
            if file_path.startswith('/static/'):
                file_path = file_path.replace('/static/', '')
                full_path = os.path.join(self.app.root_path, 'static', file_path)
            else:
                full_path = os.path.join(self.app.root_path, file_path)
            
            if not os.path.exists(full_path):
                return None
            
            # Get file stats
            stats = os.stat(full_path)
            
            # Get MIME type
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(full_path)
            
            return {
                'size': stats.st_size,
                'created_at': datetime.fromtimestamp(stats.st_ctime),
                'modified_at': datetime.fromtimestamp(stats.st_mtime),
                'mime_type': mime_type,
                'exists': True
            }
            
        except Exception as e:
            return None
    
    def move_file(self, source_path, destination_directory):
        """Move file to a different directory."""
        try:
            # Convert paths
            if source_path.startswith('/static/'):
                source_path = source_path.replace('/static/', '')
                source_full = os.path.join(self.app.root_path, 'static', source_path)
            else:
                source_full = os.path.join(self.app.root_path, source_path)
            
            if not os.path.exists(source_full):
                return None, 'Source file not found'
            
            # Create destination directory if needed
            dest_dir = os.path.join(self.upload_folder, destination_directory)
            os.makedirs(dest_dir, exist_ok=True)
            
            # Get filename
            filename = os.path.basename(source_full)
            dest_full = os.path.join(dest_dir, filename)
            
            # Move file
            os.rename(source_full, dest_full)
            
            # Return new path
            return f"/static/uploads/{destination_directory}/{filename}", None
            
        except Exception as e:
            return None, str(e)


# Global storage service instance
storage_service = StorageService()