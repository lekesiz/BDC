"""Example API endpoints for secure file upload system."""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
import os

from .file_upload_service import FileUploadService
from .config import FileUploadConfig
from .exceptions import (
    FileUploadException,
    FileSizeExceededException,
    FileTypeNotAllowedException,
    VirusDetectedException
)

# Create blueprint
file_upload_bp = Blueprint('file_upload', __name__)

# Initialize service (in production, do this in app factory)
upload_service = FileUploadService()


@file_upload_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """
    Upload a file with security scanning.
    
    Expected form data:
    - file: The file to upload
    - category: Optional file category (image, document, video, audio)
    - metadata: Optional JSON metadata
    
    Returns:
        JSON response with file information
    """
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Get file from request
        if 'file' not in request.files:
            raise BadRequest('No file provided')
        
        file = request.files['file']
        if file.filename == '':
            raise BadRequest('No file selected')
        
        # Get optional parameters
        category = request.form.get('category')
        metadata = request.form.get('metadata', {})
        if isinstance(metadata, str):
            import json
            metadata = json.loads(metadata)
        
        # Get request info for audit
        request_info = {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
        
        # Upload file
        result = upload_service.upload_file(
            file=file,
            user_id=current_user,
            tenant_id=request.headers.get('X-Tenant-ID', 'default'),
            category=category,
            metadata=metadata,
            request_info=request_info
        )
        
        return jsonify(result), 201
        
    except FileSizeExceededException as e:
        return jsonify({'error': str(e)}), 413
    except FileTypeNotAllowedException as e:
        return jsonify({'error': str(e)}), 415
    except VirusDetectedException as e:
        return jsonify({'error': str(e)}), 422
    except FileUploadException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in file upload: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@file_upload_bp.route('/download/<file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """
    Download a file.
    
    Args:
        file_id: ID of file to download
        
    Returns:
        File download response
    """
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Get request info for audit
        request_info = {
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
        
        # Download file
        result = upload_service.download_file(
            file_id=file_id,
            user_id=current_user,
            request_info=request_info
        )
        
        # Send file
        return send_file(
            result['file_path'],
            as_attachment=True,
            download_name=result['file_info']['original_filename']
        )
        
    except FileUploadException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Unexpected error in file download: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@file_upload_bp.route('/delete/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """
    Delete a file.
    
    Args:
        file_id: ID of file to delete
        
    Returns:
        JSON response confirming deletion
    """
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Get deletion reason
        data = request.get_json() or {}
        reason = data.get('reason')
        
        # Delete file
        result = upload_service.delete_file(
            file_id=file_id,
            user_id=current_user,
            reason=reason
        )
        
        return jsonify(result), 200
        
    except FileUploadException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Unexpected error in file deletion: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@file_upload_bp.route('/update/<file_id>', methods=['PUT'])
@jwt_required()
def update_file(file_id):
    """
    Update a file (create new version).
    
    Args:
        file_id: ID of file to update
        
    Expected form data:
    - file: The new file content
    - comment: Optional version comment
    
    Returns:
        JSON response with version information
    """
    try:
        # Get current user
        current_user = get_jwt_identity()
        
        # Get file from request
        if 'file' not in request.files:
            raise BadRequest('No file provided')
        
        file = request.files['file']
        comment = request.form.get('comment')
        
        # Update file
        result = upload_service.update_file(
            file_id=file_id,
            file=file,
            user_id=current_user,
            comment=comment
        )
        
        return jsonify(result), 200
        
    except FileUploadException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in file update: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@file_upload_bp.route('/history/<file_id>', methods=['GET'])
@jwt_required()
def get_file_history(file_id):
    """
    Get complete history of a file.
    
    Args:
        file_id: ID of file
        
    Returns:
        JSON response with file history
    """
    try:
        history = upload_service.get_file_history(file_id)
        
        if not history:
            return jsonify({'error': 'File not found'}), 404
        
        return jsonify(history), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error getting file history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@file_upload_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """
    Get upload statistics for current user.
    
    Returns:
        JSON response with user statistics
    """
    try:
        # Get current user
        current_user = get_jwt_identity()
        tenant_id = request.headers.get('X-Tenant-ID', 'default')
        
        stats = upload_service.get_user_stats(current_user, tenant_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error getting user stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@file_upload_bp.route('/signed-url/<file_id>', methods=['POST'])
@jwt_required()
def create_signed_url(file_id):
    """
    Create a signed URL for temporary file access.
    
    Args:
        file_id: ID of file
        
    Expected JSON data:
    - expiration: Expiration time in seconds (default: 3600)
    
    Returns:
        JSON response with signed URL
    """
    try:
        data = request.get_json() or {}
        expiration = data.get('expiration', 3600)
        
        # Validate expiration
        if not isinstance(expiration, int) or expiration < 60 or expiration > 86400:
            raise BadRequest('Invalid expiration time (must be between 60 and 86400 seconds)')
        
        url = upload_service.create_signed_url(file_id, expiration)
        
        return jsonify({
            'signed_url': url,
            'expires_in': expiration
        }), 200
        
    except FileUploadException as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Unexpected error creating signed URL: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Error handlers
@file_upload_bp.errorhandler(413)
def request_entity_too_large(e):
    """Handle file too large errors."""
    return jsonify({'error': 'File size exceeds maximum allowed size'}), 413


@file_upload_bp.errorhandler(BadRequest)
def handle_bad_request(e):
    """Handle bad request errors."""
    return jsonify({'error': str(e)}), 400


# Example of how to register the blueprint in your Flask app:
# app.register_blueprint(file_upload_bp, url_prefix='/api/files')