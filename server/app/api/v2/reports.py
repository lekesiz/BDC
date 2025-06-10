"""
Comprehensive Reports API v2

This module provides a complete reporting API with support for:
- Template management (CRUD operations)
- Report generation in multiple formats
- Schedule management for automated reports
- Report history tracking
- Custom report builder
- Report delivery via email
- Multiple export/import formats
- Bulk operations
- Async processing for long-running tasks
- Caching and performance optimization
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import io
import json
import os
from uuid import uuid4

from flask import Blueprint, request, jsonify, send_file, Response, stream_with_context
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload
import redis
from celery import shared_task

from app.extensions import db, cache
from app.models.report import Report, ReportSchedule
from app.models.user import User
from app.models.activity import Activity
from app.services.report_service import ReportService
from app.services.reporting.report_builder_service import ReportBuilderService
from app.services.reporting.scheduler_service import SchedulerService
from app.services.reporting.export_service import ExportService
from app.utils.decorators import validate_request, require_permission, rate_limit
from app.utils.logging import logger
from app.utils.pagination import paginate
from app.core.cache_manager import CacheManager
from app.middleware.auth_middleware import check_permissions
from flask_babel import _, lazy_gettext as _l


# Initialize Blueprint
reports_bp_v2 = Blueprint('reports_v2', __name__, url_prefix='/api/v2/reports')

# Initialize services
report_service = ReportService()
report_builder_service = ReportBuilderService()
scheduler_service = SchedulerService()
export_service = ExportService()
cache_manager = CacheManager()


# Validation Schemas
class ReportTemplateSchema(Schema):
    """Schema for report template validation"""
    name = fields.String(required=True, validate=validate.Length(min=3, max=255))
    description = fields.String(allow_none=True, validate=validate.Length(max=1000))
    type = fields.String(required=True, validate=validate.OneOf([
        'beneficiary', 'program', 'trainer', 'analytics', 'performance', 'custom'
    ]))
    config = fields.Dict(allow_none=True)
    fields = fields.List(fields.String(), allow_none=True)
    filters = fields.Dict(allow_none=True)
    format = fields.String(validate=validate.OneOf(['pdf', 'xlsx', 'csv', 'json', 'html']))
    is_template = fields.Boolean(missing=True)


class ReportGenerationSchema(Schema):
    """Schema for report generation request"""
    template_id = fields.Integer(allow_none=True)
    name = fields.String(required=True)
    type = fields.String(required=True)
    format = fields.String(required=True, validate=validate.OneOf(['pdf', 'xlsx', 'csv', 'json', 'html']))
    parameters = fields.Dict(required=True)
    filters = fields.Dict(allow_none=True)
    include_charts = fields.Boolean(missing=True)
    async_generation = fields.Boolean(missing=False)


class ReportScheduleSchema(Schema):
    """Schema for report schedule validation"""
    report_id = fields.Integer(required=True)
    frequency = fields.String(required=True, validate=validate.OneOf([
        'hourly', 'daily', 'weekly', 'monthly', 'quarterly', 'yearly', 'custom'
    ]))
    cron_expression = fields.String(allow_none=True)
    schedule_config = fields.Dict(allow_none=True)
    recipients = fields.List(fields.Email(), required=True, validate=validate.Length(min=1))
    delivery_format = fields.String(validate=validate.OneOf(['pdf', 'xlsx', 'csv']))
    is_active = fields.Boolean(missing=True)
    timezone = fields.String(missing='UTC')


class BulkReportSchema(Schema):
    """Schema for bulk report generation"""
    reports = fields.List(fields.Nested(ReportGenerationSchema), required=True)
    delivery_method = fields.String(validate=validate.OneOf(['download', 'email', 'storage']))
    recipients = fields.List(fields.Email(), allow_none=True)


# Template Management Endpoints

@reports_bp_v2.route('/templates', methods=['GET'])
@jwt_required()
@require_permission('reports.view')
def list_report_templates():
    """List all report templates with pagination and filtering"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        report_type = request.args.get('type')
        
        # Build query
        query = Report.query.filter_by(is_template=True)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Report.name.ilike(f'%{search}%'),
                    Report.description.ilike(f'%{search}%')
                )
            )
        
        if report_type:
            query = query.filter_by(type=report_type)
        
        # Apply pagination
        templates = query.order_by(Report.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'templates': [template.to_dict() for template in templates.items],
            'total': templates.total,
            'pages': templates.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing report templates: {str(e)}")
        return jsonify({'error': _('Failed to list report templates')}), 500


@reports_bp_v2.route('/templates', methods=['POST'])
@jwt_required()
@require_permission('reports.create')
@validate_request(ReportTemplateSchema())
def create_report_template():
    """Create a new report template"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        # Create template
        template = Report(
            name=data['name'],
            description=data.get('description'),
            type=data['type'],
            config=data.get('config', {}),
            filters=data.get('filters', {}),
            format=data.get('format', 'pdf'),
            is_template=True,
            created_by_id=user_id,
            tenant_id=user.tenant_id,
            status='active'
        )
        
        db.session.add(template)
        db.session.commit()
        
        # Log activity
        activity = Activity(
            user_id=user_id,
            action='create_report_template',
            resource_type='report_template',
            resource_id=template.id,
            details={'template_name': template.name}
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': _('Report template created successfully'),
            'template': template.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating report template: {str(e)}")
        return jsonify({'error': _('Failed to create report template')}), 500


@reports_bp_v2.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
@require_permission('reports.update')
@validate_request(ReportTemplateSchema())
def update_report_template(template_id):
    """Update an existing report template"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        template = Report.query.filter_by(id=template_id, is_template=True).first_or_404()
        
        # Check permissions
        if not check_permissions(user_id, 'reports.update', template):
            return jsonify({'error': _('Unauthorized to update this template')}), 403
        
        # Update template
        template.name = data.get('name', template.name)
        template.description = data.get('description', template.description)
        template.config = data.get('config', template.config)
        template.filters = data.get('filters', template.filters)
        template.format = data.get('format', template.format)
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Invalidate cache
        cache_manager.delete(f"report_template:{template_id}")
        
        return jsonify({
            'message': _('Report template updated successfully'),
            'template': template.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating report template: {str(e)}")
        return jsonify({'error': _('Failed to update report template')}), 500


@reports_bp_v2.route('/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
@require_permission('reports.delete')
def delete_report_template(template_id):
    """Delete a report template"""
    try:
        user_id = get_jwt_identity()
        
        template = Report.query.filter_by(id=template_id, is_template=True).first_or_404()
        
        # Check permissions
        if not check_permissions(user_id, 'reports.delete', template):
            return jsonify({'error': _('Unauthorized to delete this template')}), 403
        
        # Check if template is used in schedules
        schedules = ReportSchedule.query.filter_by(report_id=template_id).count()
        if schedules > 0:
            return jsonify({
                'error': _('Cannot delete template with active schedules')
            }), 400
        
        db.session.delete(template)
        db.session.commit()
        
        # Invalidate cache
        cache_manager.delete(f"report_template:{template_id}")
        
        return jsonify({
            'message': _('Report template deleted successfully')
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting report template: {str(e)}")
        return jsonify({'error': _('Failed to delete report template')}), 500


# Report Generation Endpoints

@reports_bp_v2.route('/generate', methods=['POST'])
@jwt_required()
@require_permission('reports.generate')
@validate_request(ReportGenerationSchema())
def generate_report():
    """Generate a new report"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        data = request.get_json()
        
        # Check if async generation requested
        if data.get('async_generation'):
            # Create task for async generation
            task = generate_report_async.delay(user_id, data)
            
            return jsonify({
                'message': _('Report generation started'),
                'task_id': task.id,
                'status_url': f'/api/v2/reports/tasks/{task.id}/status'
            }), 202
        
        # Generate report synchronously
        report = report_service.generate_report(
            user_id=user_id,
            report_type=data['type'],
            format=data['format'],
            parameters=data['parameters'],
            filters=data.get('filters', {}),
            include_charts=data.get('include_charts', True)
        )
        
        # Return file for download
        return send_file(
            report['file_path'],
            as_attachment=True,
            download_name=report['filename'],
            mimetype=report['mimetype']
        )
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': _('Failed to generate report')}), 500


@reports_bp_v2.route('/preview', methods=['POST'])
@jwt_required()
@require_permission('reports.view')
def preview_report():
    """Generate a preview of the report without saving"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Generate preview data
        preview = report_service.generate_preview(
            report_type=data['type'],
            parameters=data.get('parameters', {}),
            filters=data.get('filters', {}),
            limit=50  # Limit preview data
        )
        
        return jsonify({
            'preview': preview,
            'row_count': preview.get('total_rows', 0),
            'estimated_size': preview.get('estimated_size', 0)
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating report preview: {str(e)}")
        return jsonify({'error': _('Failed to generate preview')}), 500


# Schedule Management Endpoints

@reports_bp_v2.route('/schedules', methods=['GET'])
@jwt_required()
@require_permission('reports.view')
def list_report_schedules():
    """List all report schedules"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = ReportSchedule.query.join(Report)
        
        # Filter by user permissions
        if not check_permissions(user_id, 'reports.view_all'):
            query = query.filter(Report.created_by_id == user_id)
        
        schedules = query.order_by(ReportSchedule.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'schedules': [schedule.to_dict() for schedule in schedules.items],
            'total': schedules.total,
            'pages': schedules.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing report schedules: {str(e)}")
        return jsonify({'error': _('Failed to list schedules')}), 500


@reports_bp_v2.route('/schedules', methods=['POST'])
@jwt_required()
@require_permission('reports.schedule')
@validate_request(ReportScheduleSchema())
def create_report_schedule():
    """Create a new report schedule"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify report exists
        report = Report.query.get_or_404(data['report_id'])
        
        # Create schedule
        schedule = scheduler_service.create_schedule(
            report_id=data['report_id'],
            frequency=data['frequency'],
            schedule_config=data.get('schedule_config', {}),
            recipients=data['recipients'],
            delivery_format=data.get('delivery_format', 'pdf'),
            timezone=data.get('timezone', 'UTC'),
            created_by_id=user_id
        )
        
        return jsonify({
            'message': _('Report schedule created successfully'),
            'schedule': schedule.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating report schedule: {str(e)}")
        return jsonify({'error': _('Failed to create schedule')}), 500


@reports_bp_v2.route('/schedules/<int:schedule_id>', methods=['PUT'])
@jwt_required()
@require_permission('reports.schedule')
@validate_request(ReportScheduleSchema())
def update_report_schedule(schedule_id):
    """Update an existing report schedule"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        schedule = ReportSchedule.query.get_or_404(schedule_id)
        
        # Update schedule
        updated_schedule = scheduler_service.update_schedule(
            schedule_id=schedule_id,
            frequency=data.get('frequency'),
            schedule_config=data.get('schedule_config'),
            recipients=data.get('recipients'),
            is_active=data.get('is_active'),
            updated_by_id=user_id
        )
        
        return jsonify({
            'message': _('Report schedule updated successfully'),
            'schedule': updated_schedule.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating report schedule: {str(e)}")
        return jsonify({'error': _('Failed to update schedule')}), 500


@reports_bp_v2.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
@require_permission('reports.schedule')
def delete_report_schedule(schedule_id):
    """Delete a report schedule"""
    try:
        user_id = get_jwt_identity()
        
        schedule = ReportSchedule.query.get_or_404(schedule_id)
        
        # Check permissions
        report = Report.query.get(schedule.report_id)
        if not check_permissions(user_id, 'reports.delete', report):
            return jsonify({'error': _('Unauthorized to delete this schedule')}), 403
        
        scheduler_service.delete_schedule(schedule_id)
        
        return jsonify({
            'message': _('Report schedule deleted successfully')
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting report schedule: {str(e)}")
        return jsonify({'error': _('Failed to delete schedule')}), 500


# Report History Endpoints

@reports_bp_v2.route('/history', methods=['GET'])
@jwt_required()
@require_permission('reports.view')
def list_report_history():
    """List report generation history"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get report history from cache or database
        cache_key = f"report_history:{user_id}:page:{page}"
        cached_data = cache_manager.get(cache_key)
        
        if cached_data:
            return jsonify(cached_data), 200
        
        history = report_service.get_report_history(
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        # Cache for 5 minutes
        cache_manager.set(cache_key, history, timeout=300)
        
        return jsonify(history), 200
        
    except Exception as e:
        logger.error(f"Error listing report history: {str(e)}")
        return jsonify({'error': _('Failed to list report history')}), 500


@reports_bp_v2.route('/history/<string:report_id>/download', methods=['GET'])
@jwt_required()
@require_permission('reports.download')
def download_historical_report(report_id):
    """Download a previously generated report"""
    try:
        user_id = get_jwt_identity()
        
        # Get report file path
        report_file = report_service.get_historical_report(report_id, user_id)
        
        if not report_file:
            return jsonify({'error': _('Report not found')}), 404
        
        return send_file(
            report_file['path'],
            as_attachment=True,
            download_name=report_file['filename'],
            mimetype=report_file['mimetype']
        )
        
    except Exception as e:
        logger.error(f"Error downloading report: {str(e)}")
        return jsonify({'error': _('Failed to download report')}), 500


@reports_bp_v2.route('/history/<string:report_id>', methods=['DELETE'])
@jwt_required()
@require_permission('reports.delete')
def delete_historical_report(report_id):
    """Delete a historical report"""
    try:
        user_id = get_jwt_identity()
        
        success = report_service.delete_historical_report(report_id, user_id)
        
        if not success:
            return jsonify({'error': _('Failed to delete report')}), 400
        
        return jsonify({
            'message': _('Report deleted successfully')
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        return jsonify({'error': _('Failed to delete report')}), 500


# Custom Report Builder

@reports_bp_v2.route('/builder/fields/<string:report_type>', methods=['GET'])
@jwt_required()
@require_permission('reports.view')
def get_available_fields(report_type):
    """Get available fields for custom report builder"""
    try:
        fields = report_builder_service.get_available_fields(report_type)
        
        return jsonify({
            'fields': fields,
            'field_count': len(fields)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting available fields: {str(e)}")
        return jsonify({'error': _('Failed to get available fields')}), 500


@reports_bp_v2.route('/builder/validate', methods=['POST'])
@jwt_required()
@require_permission('reports.view')
def validate_report_configuration():
    """Validate custom report configuration"""
    try:
        data = request.get_json()
        
        validation_result = report_builder_service.validate_configuration(
            report_type=data['type'],
            fields=data.get('fields', []),
            filters=data.get('filters', {}),
            grouping=data.get('grouping', []),
            sorting=data.get('sorting', [])
        )
        
        return jsonify(validation_result), 200
        
    except Exception as e:
        logger.error(f"Error validating configuration: {str(e)}")
        return jsonify({'error': _('Failed to validate configuration')}), 500


# Report Delivery

@reports_bp_v2.route('/deliver', methods=['POST'])
@jwt_required()
@require_permission('reports.deliver')
def deliver_report():
    """Deliver a report via email"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate recipients
        recipients = data.get('recipients', [])
        if not recipients:
            return jsonify({'error': _('No recipients specified')}), 400
        
        # Generate and deliver report
        delivery_result = report_service.deliver_report(
            report_id=data['report_id'],
            recipients=recipients,
            subject=data.get('subject', _('Your requested report')),
            message=data.get('message', ''),
            user_id=user_id
        )
        
        return jsonify({
            'message': _('Report delivered successfully'),
            'delivery_id': delivery_result['delivery_id'],
            'recipients_count': len(recipients)
        }), 200
        
    except Exception as e:
        logger.error(f"Error delivering report: {str(e)}")
        return jsonify({'error': _('Failed to deliver report')}), 500


# Report Formats

@reports_bp_v2.route('/formats', methods=['GET'])
@jwt_required()
def list_supported_formats():
    """List all supported report formats"""
    formats = [
        {
            'format': 'pdf',
            'name': _('PDF Document'),
            'description': _('Portable Document Format with charts and formatting'),
            'mime_type': 'application/pdf',
            'supports_charts': True,
            'supports_images': True
        },
        {
            'format': 'xlsx',
            'name': _('Excel Spreadsheet'),
            'description': _('Microsoft Excel format with multiple sheets'),
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'supports_charts': True,
            'supports_images': True
        },
        {
            'format': 'csv',
            'name': _('CSV File'),
            'description': _('Comma-separated values for data import/export'),
            'mime_type': 'text/csv',
            'supports_charts': False,
            'supports_images': False
        },
        {
            'format': 'json',
            'name': _('JSON Data'),
            'description': _('JavaScript Object Notation for API integration'),
            'mime_type': 'application/json',
            'supports_charts': False,
            'supports_images': False
        },
        {
            'format': 'html',
            'name': _('HTML Report'),
            'description': _('Web-based report with interactive elements'),
            'mime_type': 'text/html',
            'supports_charts': True,
            'supports_images': True
        }
    ]
    
    return jsonify({'formats': formats}), 200


# Chart Data Endpoint

@reports_bp_v2.route('/charts/<string:report_type>/data', methods=['POST'])
@jwt_required()
@require_permission('reports.view')
def get_chart_data(report_type):
    """Get chart data for report preview"""
    try:
        data = request.get_json()
        
        chart_data = report_service.generate_chart_data(
            report_type=report_type,
            chart_type=data.get('chart_type', 'bar'),
            parameters=data.get('parameters', {}),
            filters=data.get('filters', {})
        )
        
        return jsonify({
            'chart_data': chart_data,
            'chart_config': {
                'type': data.get('chart_type', 'bar'),
                'title': data.get('title', ''),
                'colors': data.get('colors', [])
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating chart data: {str(e)}")
        return jsonify({'error': _('Failed to generate chart data')}), 500


# Export/Import Endpoints

@reports_bp_v2.route('/export/<int:report_id>', methods=['GET'])
@jwt_required()
@require_permission('reports.export')
def export_report_configuration(report_id):
    """Export report configuration for sharing or backup"""
    try:
        user_id = get_jwt_identity()
        
        report = Report.query.get_or_404(report_id)
        
        # Check permissions
        if not check_permissions(user_id, 'reports.export', report):
            return jsonify({'error': _('Unauthorized to export this report')}), 403
        
        export_data = export_service.export_report_configuration(report)
        
        return Response(
            json.dumps(export_data, indent=2),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=report_{report_id}_config.json'
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting report: {str(e)}")
        return jsonify({'error': _('Failed to export report')}), 500


@reports_bp_v2.route('/import', methods=['POST'])
@jwt_required()
@require_permission('reports.import')
def import_report_configuration():
    """Import report configuration from file"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if 'file' not in request.files:
            return jsonify({'error': _('No file provided')}), 400
        
        file = request.files['file']
        
        # Parse configuration
        config_data = json.load(file.stream)
        
        # Import configuration
        imported_report = export_service.import_report_configuration(
            config_data,
            user_id,
            user.tenant_id
        )
        
        return jsonify({
            'message': _('Report configuration imported successfully'),
            'report': imported_report.to_dict()
        }), 201
        
    except json.JSONDecodeError:
        return jsonify({'error': _('Invalid JSON file')}), 400
    except Exception as e:
        logger.error(f"Error importing report: {str(e)}")
        return jsonify({'error': _('Failed to import report')}), 500


# Bulk Operations

@reports_bp_v2.route('/bulk/generate', methods=['POST'])
@jwt_required()
@require_permission('reports.bulk_generate')
@validate_request(BulkReportSchema())
def bulk_generate_reports():
    """Generate multiple reports in bulk"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Create bulk generation task
        task = bulk_generate_reports_async.delay(
            user_id=user_id,
            reports=data['reports'],
            delivery_method=data.get('delivery_method', 'download'),
            recipients=data.get('recipients', [])
        )
        
        return jsonify({
            'message': _('Bulk report generation started'),
            'task_id': task.id,
            'report_count': len(data['reports']),
            'status_url': f'/api/v2/reports/tasks/{task.id}/status'
        }), 202
        
    except Exception as e:
        logger.error(f"Error in bulk report generation: {str(e)}")
        return jsonify({'error': _('Failed to start bulk generation')}), 500


# Task Status Endpoint

@reports_bp_v2.route('/tasks/<string:task_id>/status', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Get status of async report generation task"""
    try:
        from app.extensions import celery
        
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'state': task.state,
                'status': _('Task is waiting to be processed')
            }
        elif task.state == 'PROGRESS':
            response = {
                'state': task.state,
                'current': task.info.get('current', 0),
                'total': task.info.get('total', 1),
                'status': task.info.get('status', '')
            }
        elif task.state == 'SUCCESS':
            response = {
                'state': task.state,
                'result': task.info,
                'status': _('Task completed successfully')
            }
        else:  # FAILURE
            response = {
                'state': task.state,
                'error': str(task.info),
                'status': _('Task failed')
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return jsonify({'error': _('Failed to get task status')}), 500


# Async Tasks

@shared_task(bind=True)
def generate_report_async(self, user_id, report_data):
    """Async task for report generation"""
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Initializing report generation'}
        )
        
        # Generate report
        report = report_service.generate_report(
            user_id=user_id,
            report_type=report_data['type'],
            format=report_data['format'],
            parameters=report_data['parameters'],
            filters=report_data.get('filters', {}),
            include_charts=report_data.get('include_charts', True),
            task=self
        )
        
        return {
            'status': 'completed',
            'report_id': report['id'],
            'download_url': f"/api/v2/reports/history/{report['id']}/download"
        }
        
    except Exception as e:
        logger.error(f"Error in async report generation: {str(e)}")
        raise


@shared_task(bind=True)
def bulk_generate_reports_async(self, user_id, reports, delivery_method, recipients):
    """Async task for bulk report generation"""
    try:
        total_reports = len(reports)
        generated_reports = []
        
        for idx, report_config in enumerate(reports):
            # Update progress
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': idx,
                    'total': total_reports,
                    'status': f'Generating report {idx + 1} of {total_reports}'
                }
            )
            
            # Generate report
            report = report_service.generate_report(
                user_id=user_id,
                report_type=report_config['type'],
                format=report_config['format'],
                parameters=report_config['parameters'],
                filters=report_config.get('filters', {}),
                include_charts=report_config.get('include_charts', True)
            )
            
            generated_reports.append(report)
        
        # Handle delivery
        if delivery_method == 'email' and recipients:
            for recipient in recipients:
                report_service.send_bulk_reports_email(
                    recipient=recipient,
                    reports=generated_reports,
                    user_id=user_id
                )
        
        return {
            'status': 'completed',
            'reports_generated': len(generated_reports),
            'delivery_method': delivery_method
        }
        
    except Exception as e:
        logger.error(f"Error in bulk report generation: {str(e)}")
        raise


# Streaming endpoint for large reports
@reports_bp_v2.route('/stream/<string:report_id>', methods=['GET'])
@jwt_required()
@require_permission('reports.download')
def stream_report(report_id):
    """Stream large report files"""
    try:
        user_id = get_jwt_identity()
        
        def generate():
            """Generator function for streaming file content"""
            report_file = report_service.get_historical_report(report_id, user_id)
            
            if not report_file:
                yield b''
                return
            
            with open(report_file['path'], 'rb') as f:
                while True:
                    data = f.read(4096)  # Read in 4KB chunks
                    if not data:
                        break
                    yield data
        
        report_file = report_service.get_historical_report(report_id, user_id)
        
        if not report_file:
            return jsonify({'error': _('Report not found')}), 404
        
        return Response(
            stream_with_context(generate()),
            mimetype=report_file['mimetype'],
            headers={
                'Content-Disposition': f'attachment; filename={report_file["filename"]}'
            }
        )
        
    except Exception as e:
        logger.error(f"Error streaming report: {str(e)}")
        return jsonify({'error': _('Failed to stream report')}), 500


# Health check endpoint
@reports_bp_v2.route('/health', methods=['GET'])
def health_check():
    """Check health of reports service"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Check cache connection
        cache_status = cache_manager.ping()
        
        # Check report service
        service_status = report_service.health_check()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'cache': 'connected' if cache_status else 'disconnected',
            'report_service': service_status
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503