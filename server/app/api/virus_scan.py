"""Virus scanning API endpoints."""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from app.services.virus_scanner_service import VirusScannerService
from app.models.virus_scan_log import VirusScanLog
from app.models.user import User
from app.extensions import db
from app.middleware.i18n_middleware import i18n_response
import logging

logger = logging.getLogger(__name__)

virus_scan_bp = Blueprint('virus_scan', __name__, url_prefix='/api/virus-scan')


@virus_scan_bp.route('/scan-file', methods=['POST'])
@jwt_required()
@i18n_response
def scan_file():
    """Scan an uploaded file for viruses."""
    try:
        user_id = get_jwt_identity()
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'error': 'no_file',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'empty_filename',
                'message': 'No file selected'
            }), 400
        
        # Save file temporarily
        temp_dir = tempfile.mkdtemp()
        filename = secure_filename(file.filename)
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)
        
        try:
            # Scan file
            scanner = VirusScannerService()
            result = scanner.scan_file(temp_path, user_id)
            
            # Clean up if file is clean
            if result['status'] == 'clean':
                os.remove(temp_path)
                os.rmdir(temp_dir)
            
            return jsonify({
                'success': True,
                'scan_result': result
            }), 200
            
        except Exception as e:
            # Clean up on error
            try:
                os.remove(temp_path)
                os.rmdir(temp_dir)
            except:
                pass
            raise
            
    except Exception as e:
        logger.error(f"File scan error: {str(e)}")
        return jsonify({
            'error': 'scan_failed',
            'message': str(e)
        }), 500


@virus_scan_bp.route('/scan-url', methods=['POST'])
@jwt_required()
@i18n_response
def scan_url():
    """Scan a file from URL for viruses."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        url = data.get('url')
        if not url:
            return jsonify({
                'error': 'invalid_request',
                'message': 'URL is required'
            }), 400
        
        # Download file to temp location
        import requests
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Download with size limit
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > 50 * 1024 * 1024:  # 50MB
                return jsonify({
                    'error': 'file_too_large',
                    'message': 'File exceeds maximum size limit'
                }), 400
            
            # Save to temp file
            filename = secure_filename(url.split('/')[-1] or 'download')
            temp_path = os.path.join(temp_dir, filename)
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Scan file
            scanner = VirusScannerService()
            result = scanner.scan_file(temp_path, user_id)
            
            # Clean up if file is clean
            if result['status'] == 'clean':
                os.remove(temp_path)
                os.rmdir(temp_dir)
            
            return jsonify({
                'success': True,
                'scan_result': result
            }), 200
            
        except requests.RequestException as e:
            return jsonify({
                'error': 'download_failed',
                'message': f'Failed to download file: {str(e)}'
            }), 400
        finally:
            # Clean up on error
            try:
                if os.path.exists(temp_dir):
                    import shutil
                    shutil.rmtree(temp_dir)
            except:
                pass
            
    except Exception as e:
        logger.error(f"URL scan error: {str(e)}")
        return jsonify({
            'error': 'scan_failed',
            'message': str(e)
        }), 500


@virus_scan_bp.route('/history', methods=['GET'])
@jwt_required()
@i18n_response
def get_scan_history():
    """Get virus scan history for current user."""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        
        scans = VirusScanLog.get_user_scan_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'scans': [scan.to_dict() for scan in scans]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scan history: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@virus_scan_bp.route('/statistics', methods=['GET'])
@jwt_required()
@i18n_response
def get_scan_statistics():
    """Get virus scan statistics (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is admin
        if not user or user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({
                'error': 'unauthorized',
                'message': 'Admin access required'
            }), 403
        
        days = request.args.get('days', 30, type=int)
        
        scanner = VirusScannerService()
        stats = scanner.get_scan_statistics(days)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting scan statistics: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@virus_scan_bp.route('/recent-threats', methods=['GET'])
@jwt_required()
@i18n_response
def get_recent_threats():
    """Get recent virus detections (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is admin
        if not user or user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({
                'error': 'unauthorized',
                'message': 'Admin access required'
            }), 403
        
        limit = request.args.get('limit', 10, type=int)
        
        infections = VirusScanLog.get_recent_infections(limit)
        
        return jsonify({
            'success': True,
            'infections': [infection.to_dict() for infection in infections]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting recent threats: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@virus_scan_bp.route('/quarantine', methods=['GET'])
@jwt_required()
@i18n_response
def list_quarantine():
    """List quarantined files (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is admin
        if not user or user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({
                'error': 'unauthorized',
                'message': 'Admin access required'
            }), 403
        
        quarantine_path = current_app.config.get('QUARANTINE_PATH', '/tmp/quarantine')
        
        if not os.path.exists(quarantine_path):
            return jsonify({
                'success': True,
                'files': []
            }), 200
        
        quarantined_files = []
        
        for filename in os.listdir(quarantine_path):
            if filename.endswith('.info'):
                continue
                
            file_path = os.path.join(quarantine_path, filename)
            info_path = f"{file_path}.info"
            
            file_info = {
                'filename': filename,
                'size': os.path.getsize(file_path),
                'quarantine_date': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
            }
            
            # Read info file if exists
            if os.path.exists(info_path):
                import json
                with open(info_path, 'r') as f:
                    info = json.load(f)
                    file_info.update(info)
            
            quarantined_files.append(file_info)
        
        return jsonify({
            'success': True,
            'files': quarantined_files
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing quarantine: {str(e)}")
        return jsonify({
            'error': 'fetch_failed',
            'message': str(e)
        }), 500


@virus_scan_bp.route('/quarantine/<filename>', methods=['DELETE'])
@jwt_required()
@i18n_response
def delete_quarantined_file(filename):
    """Delete a quarantined file (admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        # Check if user is admin
        if not user or user.role != 'super_admin':
            return jsonify({
                'error': 'unauthorized',
                'message': 'Super admin access required'
            }), 403
        
        quarantine_path = current_app.config.get('QUARANTINE_PATH', '/tmp/quarantine')
        file_path = os.path.join(quarantine_path, secure_filename(filename))
        info_path = f"{file_path}.info"
        
        if not os.path.exists(file_path):
            return jsonify({
                'error': 'not_found',
                'message': 'Quarantined file not found'
            }), 404
        
        # Delete file and info
        os.remove(file_path)
        if os.path.exists(info_path):
            os.remove(info_path)
        
        # Log deletion
        logger.warning(f"Quarantined file deleted by {user.email}: {filename}")
        
        return jsonify({
            'success': True,
            'message': 'Quarantined file deleted'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting quarantined file: {str(e)}")
        return jsonify({
            'error': 'delete_failed',
            'message': str(e)
        }), 500