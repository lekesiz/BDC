"""
Backup and Recovery API Endpoints
Provides backup management, restore operations, and recovery point management.
"""

from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.backup_service import backup_service, BackupSchedule
from app.core.auth import requires_permission
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)

backup_bp = Blueprint('backup', __name__, url_prefix='/api/v2/backup')

@backup_bp.route('/create', methods=['POST'])
@jwt_required()
@requires_permission('backup.create')
def create_backup():
    """
    Create a new backup
    """
    try:
        data = request.get_json() or {}
        
        # Validate backup type
        backup_type = data.get('backup_type', 'full')
        if backup_type not in ['full', 'incremental', 'differential']:
            return jsonify({'error': 'Invalid backup type'}), 400
        
        # Create backup
        metadata = backup_service.create_backup(
            backup_type=backup_type,
            description=data.get('description'),
            include_files=data.get('include_files', True),
            notify=data.get('notify', True)
        )
        
        return jsonify({
            'success': True,
            'backup': {
                'backup_id': metadata.backup_id,
                'type': metadata.backup_type,
                'status': metadata.status,
                'size_mb': round(metadata.size_bytes / 1024 / 1024, 2),
                'duration_seconds': metadata.duration_seconds,
                'timestamp': metadata.timestamp.isoformat(),
                'storage_location': metadata.storage_location,
                'checksum': metadata.checksum
            }
        })
        
    except Exception as e:
        logger.error(f"Backup creation failed: {str(e)}")
        return jsonify({
            'error': 'Backup creation failed',
            'message': str(e)
        }), 500

@backup_bp.route('/restore', methods=['POST'])
@jwt_required()
@requires_permission('backup.restore')
def restore_backup():
    """
    Restore from backup
    """
    try:
        data = request.get_json()
        
        if not data or 'backup_id' not in data:
            return jsonify({'error': 'Backup ID is required'}), 400
        
        # Parse restore point if provided
        restore_point = None
        if data.get('restore_point'):
            restore_point = datetime.fromisoformat(data['restore_point'])
        
        # Perform restore
        result = backup_service.restore_backup(
            backup_id=data['backup_id'],
            restore_point=restore_point,
            restore_database=data.get('restore_database', True),
            restore_files=data.get('restore_files', True),
            target_database=data.get('target_database')
        )
        
        return jsonify({
            'success': True,
            'restore_result': result
        })
        
    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        return jsonify({
            'error': 'Restore failed',
            'message': str(e)
        }), 500

@backup_bp.route('/history', methods=['GET'])
@jwt_required()
@requires_permission('backup.view')
def get_backup_history():
    """
    Get backup history with optional filters
    """
    try:
        # Parse filters
        start_date = request.args.get('start_date')
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        
        end_date = request.args.get('end_date')
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        backup_type = request.args.get('type')
        status = request.args.get('status')
        
        # Get backup history
        backups = backup_service.get_backup_history(
            start_date=start_date,
            end_date=end_date,
            backup_type=backup_type,
            status=status
        )
        
        return jsonify({
            'backups': [
                {
                    'backup_id': b.backup_id,
                    'type': b.backup_type,
                    'timestamp': b.timestamp.isoformat(),
                    'size_mb': round(b.size_bytes / 1024 / 1024, 2),
                    'duration_seconds': b.duration_seconds,
                    'status': b.status,
                    'storage_location': b.storage_location,
                    'retention_days': b.retention_days,
                    'checksum': b.checksum,
                    'error_message': b.error_message
                }
                for b in backups
            ],
            'total': len(backups)
        })
        
    except Exception as e:
        logger.error(f"Failed to get backup history: {str(e)}")
        return jsonify({
            'error': 'Failed to get backup history',
            'message': str(e)
        }), 500

@backup_bp.route('/recovery-points', methods=['GET'])
@jwt_required()
@requires_permission('backup.view')
def get_recovery_points():
    """
    Get available recovery points
    """
    try:
        recovery_points = backup_service.get_recovery_points()
        
        return jsonify({
            'recovery_points': recovery_points,
            'total': len(recovery_points)
        })
        
    except Exception as e:
        logger.error(f"Failed to get recovery points: {str(e)}")
        return jsonify({
            'error': 'Failed to get recovery points',
            'message': str(e)
        }), 500

@backup_bp.route('/schedules', methods=['GET'])
@jwt_required()
@requires_permission('backup.view')
def get_backup_schedules():
    """
    Get backup schedules
    """
    try:
        schedules = backup_service.backup_schedules
        
        return jsonify({
            'schedules': [
                {
                    'name': s.name,
                    'backup_type': s.backup_type,
                    'frequency': s.frequency,
                    'time': s.time,
                    'retention_days': s.retention_days,
                    'enabled': s.enabled,
                    'last_run': s.last_run.isoformat() if s.last_run else None,
                    'next_run': s.next_run.isoformat() if s.next_run else None
                }
                for s in schedules
            ],
            'total': len(schedules)
        })
        
    except Exception as e:
        logger.error(f"Failed to get backup schedules: {str(e)}")
        return jsonify({
            'error': 'Failed to get backup schedules',
            'message': str(e)
        }), 500

@backup_bp.route('/schedules', methods=['POST'])
@jwt_required()
@requires_permission('backup.schedule')
def create_backup_schedule():
    """
    Create a new backup schedule
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'backup_type', 'frequency', 'time', 'retention_days']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create schedule
        schedule = BackupSchedule(
            name=data['name'],
            backup_type=data['backup_type'],
            frequency=data['frequency'],
            time=data['time'],
            retention_days=data['retention_days'],
            enabled=data.get('enabled', True)
        )
        
        backup_service.schedule_backup(schedule)
        
        return jsonify({
            'success': True,
            'schedule': {
                'name': schedule.name,
                'backup_type': schedule.backup_type,
                'frequency': schedule.frequency,
                'time': schedule.time,
                'retention_days': schedule.retention_days,
                'enabled': schedule.enabled
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to create backup schedule: {str(e)}")
        return jsonify({
            'error': 'Failed to create backup schedule',
            'message': str(e)
        }), 500

@backup_bp.route('/schedules/<schedule_name>', methods=['PUT'])
@jwt_required()
@requires_permission('backup.schedule')
def update_backup_schedule(schedule_name):
    """
    Update a backup schedule
    """
    try:
        data = request.get_json()
        
        # Find schedule
        schedule = None
        for s in backup_service.backup_schedules:
            if s.name == schedule_name:
                schedule = s
                break
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        # Update schedule
        if 'enabled' in data:
            schedule.enabled = data['enabled']
        if 'frequency' in data:
            schedule.frequency = data['frequency']
        if 'time' in data:
            schedule.time = data['time']
        if 'retention_days' in data:
            schedule.retention_days = data['retention_days']
        
        return jsonify({
            'success': True,
            'schedule': {
                'name': schedule.name,
                'backup_type': schedule.backup_type,
                'frequency': schedule.frequency,
                'time': schedule.time,
                'retention_days': schedule.retention_days,
                'enabled': schedule.enabled
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to update backup schedule: {str(e)}")
        return jsonify({
            'error': 'Failed to update backup schedule',
            'message': str(e)
        }), 500

@backup_bp.route('/schedules/<schedule_name>', methods=['DELETE'])
@jwt_required()
@requires_permission('backup.schedule')
def delete_backup_schedule(schedule_name):
    """
    Delete a backup schedule
    """
    try:
        # Find and remove schedule
        schedule_found = False
        for i, s in enumerate(backup_service.backup_schedules):
            if s.name == schedule_name:
                backup_service.backup_schedules.pop(i)
                schedule_found = True
                break
        
        if not schedule_found:
            return jsonify({'error': 'Schedule not found'}), 404
        
        return jsonify({
            'success': True,
            'message': f'Schedule {schedule_name} deleted'
        })
        
    except Exception as e:
        logger.error(f"Failed to delete backup schedule: {str(e)}")
        return jsonify({
            'error': 'Failed to delete backup schedule',
            'message': str(e)
        }), 500

@backup_bp.route('/download/<backup_id>', methods=['GET'])
@jwt_required()
@requires_permission('backup.download')
def download_backup(backup_id):
    """
    Download a backup file
    """
    try:
        # Find backup
        metadata = None
        for b in backup_service.backup_history:
            if b.backup_id == backup_id:
                metadata = b
                break
        
        if not metadata:
            return jsonify({'error': 'Backup not found'}), 404
        
        # Check if backup is local
        if metadata.storage_location.startswith('s3://'):
            return jsonify({'error': 'Direct download not available for S3 backups'}), 400
        
        # Send file
        if os.path.exists(metadata.storage_location):
            return send_file(
                metadata.storage_location,
                as_attachment=True,
                download_name=f"{backup_id}.tar.gz",
                mimetype='application/gzip'
            )
        else:
            return jsonify({'error': 'Backup file not found'}), 404
            
    except Exception as e:
        logger.error(f"Failed to download backup: {str(e)}")
        return jsonify({
            'error': 'Failed to download backup',
            'message': str(e)
        }), 500

@backup_bp.route('/verify/<backup_id>', methods=['POST'])
@jwt_required()
@requires_permission('backup.verify')
def verify_backup(backup_id):
    """
    Verify backup integrity
    """
    try:
        # Find backup
        metadata = None
        for b in backup_service.backup_history:
            if b.backup_id == backup_id:
                metadata = b
                break
        
        if not metadata:
            return jsonify({'error': 'Backup not found'}), 404
        
        # Download if needed
        local_backup = backup_service._download_backup(metadata)
        
        # Verify
        backup_service._verify_backup(local_backup, metadata)
        
        return jsonify({
            'success': True,
            'backup_id': backup_id,
            'verified': True,
            'checksum': metadata.checksum
        })
        
    except Exception as e:
        logger.error(f"Backup verification failed: {str(e)}")
        return jsonify({
            'error': 'Backup verification failed',
            'message': str(e)
        }), 500

@backup_bp.route('/status', methods=['GET'])
@jwt_required()
@requires_permission('backup.view')
def get_backup_status():
    """
    Get backup service status
    """
    try:
        # Calculate statistics
        total_backups = len(backup_service.backup_history)
        successful_backups = len([b for b in backup_service.backup_history if b.status == 'completed'])
        failed_backups = len([b for b in backup_service.backup_history if b.status == 'failed'])
        
        # Get storage usage
        total_size = sum(b.size_bytes for b in backup_service.backup_history if b.status == 'completed')
        
        # Get last backup
        last_backup = None
        if backup_service.backup_history:
            last_backup = max(backup_service.backup_history, key=lambda x: x.timestamp)
        
        # Get next scheduled backup
        next_backup = None
        for schedule in backup_service.backup_schedules:
            if schedule.enabled and schedule.next_run:
                if not next_backup or schedule.next_run < next_backup:
                    next_backup = schedule.next_run
        
        return jsonify({
            'status': {
                'scheduler_running': backup_service._running,
                'total_backups': total_backups,
                'successful_backups': successful_backups,
                'failed_backups': failed_backups,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'storage_type': backup_service.config['BACKUP_STORAGE'],
                'retention_days': backup_service.config['BACKUP_RETENTION_DAYS'],
                'compression': backup_service.config['BACKUP_COMPRESSION'],
                'encryption': backup_service.config['BACKUP_ENCRYPTION']
            },
            'last_backup': {
                'backup_id': last_backup.backup_id,
                'timestamp': last_backup.timestamp.isoformat(),
                'status': last_backup.status
            } if last_backup else None,
            'next_scheduled_backup': next_backup.isoformat() if next_backup else None
        })
        
    except Exception as e:
        logger.error(f"Failed to get backup status: {str(e)}")
        return jsonify({
            'error': 'Failed to get backup status',
            'message': str(e)
        }), 500

# Error handlers
@backup_bp.errorhandler(403)
def forbidden(error):
    return jsonify({
        'error': 'Insufficient permissions',
        'message': 'You do not have permission to perform backup operations'
    }), 403

@backup_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'An error occurred during backup operation'
    }), 500