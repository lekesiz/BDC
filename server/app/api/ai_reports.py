"""AI Reports API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.ai_report_service import ai_report_service
from app.decorators import role_required
from app.models import User
from app.extensions import db

from app.utils.logging import logger

bp = Blueprint('ai_reports', __name__, url_prefix='/api/ai-reports')


@bp.route('/beneficiary/<int:beneficiary_id>', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def generate_beneficiary_report(beneficiary_id):
    """Generate AI-powered report for a beneficiary."""
    try:
        data = request.get_json()
        
        # Get report parameters
        report_type = data.get('report_type', 'comprehensive')
        time_period = data.get('time_period', 'last_month')
        include_sections = data.get('include_sections')
        
        # Validate report type
        valid_types = ['comprehensive', 'progress', 'assessment']
        if report_type not in valid_types:
            return jsonify({'error': f'Invalid report type. Must be one of: {valid_types}'}), 400
        
        # Validate time period
        valid_periods = ['last_week', 'last_month', 'last_quarter', 'last_year', 'all_time']
        if time_period not in valid_periods:
            return jsonify({'error': f'Invalid time period. Must be one of: {valid_periods}'}), 400
        
        # Generate report
        report, error = ai_report_service.generate_beneficiary_report(
            beneficiary_id=beneficiary_id,
            report_type=report_type,
            time_period=time_period,
            include_sections=include_sections
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/program/<int:program_id>', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def generate_program_report(program_id):
    """Generate AI-powered report for a program."""
    try:
        data = request.get_json()
        
        # Get report parameters
        time_period = data.get('time_period', 'last_month')
        
        # Validate time period
        valid_periods = ['last_week', 'last_month', 'last_quarter', 'last_year', 'all_time']
        if time_period not in valid_periods:
            return jsonify({'error': f'Invalid time period. Must be one of: {valid_periods}'}), 400
        
        # Generate report
        report, error = ai_report_service.generate_program_report(
            program_id=program_id,
            time_period=time_period
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/comparative', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def generate_comparative_report():
    """Generate comparative report for multiple beneficiaries."""
    try:
        data = request.get_json()
        
        # Get parameters
        beneficiary_ids = data.get('beneficiary_ids', [])
        metrics = data.get('metrics')
        
        # Validate inputs
        if not beneficiary_ids or len(beneficiary_ids) < 2:
            return jsonify({'error': 'At least 2 beneficiary IDs required'}), 400
        
        if len(beneficiary_ids) > 10:
            return jsonify({'error': 'Maximum 10 beneficiaries allowed for comparison'}), 400
        
        # Validate metrics if provided
        valid_metrics = [
            'assessment_scores',
            'attendance_rate',
            'progress_rate',
            'engagement_level',
            'completion_rate'
        ]
        
        if metrics:
            invalid_metrics = [m for m in metrics if m not in valid_metrics]
            if invalid_metrics:
                return jsonify({
                    'error': f'Invalid metrics: {invalid_metrics}. Valid metrics are: {valid_metrics}'
                }), 400
        
        # Generate report
        report, error = ai_report_service.generate_comparative_report(
            beneficiary_ids=beneficiary_ids,
            metrics=metrics
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(report), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/synthesis', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def synthesize_data():
    """Synthesize data from multiple sources for a beneficiary."""
    try:
        data = request.get_json()
        
        # Get parameters
        beneficiary_id = data.get('beneficiary_id')
        sources = data.get('sources', [])
        
        # Validate inputs
        if not beneficiary_id:
            return jsonify({'error': 'beneficiary_id is required'}), 400
        
        if not sources:
            return jsonify({'error': 'At least one source is required'}), 400
        
        # Validate sources
        valid_sources = ['assessments', 'appointments', 'documents', 'notes', 'programs']
        invalid_sources = [s for s in sources if s not in valid_sources]
        
        if invalid_sources:
            return jsonify({
                'error': f'Invalid sources: {invalid_sources}. Valid sources are: {valid_sources}'
            }), 400
        
        # Generate synthesis
        synthesis, error = ai_report_service.synthesize_multi_source_data(
            beneficiary_id=beneficiary_id,
            sources=sources
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(synthesis), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/templates', methods=['GET'])
@jwt_required()
def get_report_templates():
    """Get available report templates and configurations."""
    templates = {
        'report_types': [
            {
                'type': 'comprehensive',
                'name': 'Comprehensive Report',
                'description': 'Full analysis including all available data',
                'default_sections': ['profile', 'assessments', 'appointments', 'progress', 'documents', 'notes']
            },
            {
                'type': 'progress',
                'name': 'Progress Report',
                'description': 'Focus on performance trends and improvements',
                'default_sections': ['assessments', 'appointments', 'progress']
            },
            {
                'type': 'assessment',
                'name': 'Assessment Report',
                'description': 'Detailed analysis of test and evaluation results',
                'default_sections': ['assessments', 'progress']
            }
        ],
        'time_periods': [
            {'value': 'last_week', 'label': 'Last Week'},
            {'value': 'last_month', 'label': 'Last Month'},
            {'value': 'last_quarter', 'label': 'Last Quarter'},
            {'value': 'last_year', 'label': 'Last Year'},
            {'value': 'all_time', 'label': 'All Time'}
        ],
        'available_sections': [
            {'value': 'profile', 'label': 'Beneficiary Profile'},
            {'value': 'assessments', 'label': 'Assessment Results'},
            {'value': 'appointments', 'label': 'Attendance & Appointments'},
            {'value': 'progress', 'label': 'Progress Tracking'},
            {'value': 'documents', 'label': 'Document Activity'},
            {'value': 'notes', 'label': 'Notes & Observations'}
        ],
        'comparison_metrics': [
            {'value': 'assessment_scores', 'label': 'Assessment Scores'},
            {'value': 'attendance_rate', 'label': 'Attendance Rate'},
            {'value': 'progress_rate', 'label': 'Progress Rate'},
            {'value': 'engagement_level', 'label': 'Engagement Level'},
            {'value': 'completion_rate', 'label': 'Completion Rate'}
        ],
        'data_sources': [
            {'value': 'assessments', 'label': 'Assessments & Tests'},
            {'value': 'appointments', 'label': 'Appointments & Attendance'},
            {'value': 'documents', 'label': 'Documents & Files'},
            {'value': 'notes', 'label': 'Notes & Comments'},
            {'value': 'programs', 'label': 'Program Enrollment'}
        ]
    }
    
    return jsonify(templates), 200


@bp.route('/insights/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def get_quick_insights(beneficiary_id):
    """Get quick AI-generated insights for a beneficiary."""
    try:
        # Generate a quick progress report for the last month
        report, error = ai_report_service.generate_beneficiary_report(
            beneficiary_id=beneficiary_id,
            report_type='progress',
            time_period='last_month',
            include_sections=['assessments', 'appointments', 'progress']
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # Extract key insights
        quick_insights = {
            'beneficiary_id': beneficiary_id,
            'progress_summary': report.get('progress_summary', {}),
            'performance_metrics': report.get('performance_metrics', {}),
            'key_recommendations': report.get('recommendations', [])[:3],  # Top 3 recommendations
            'generated_at': report.get('metadata', {}).get('generated_at')
        }
        
        return jsonify(quick_insights), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/batch', methods=['POST'])
@jwt_required()
@role_required(['tenant_admin', 'super_admin'])
def generate_batch_reports():
    """Generate reports for multiple beneficiaries in batch."""
    try:
        data = request.get_json()
        
        # Get parameters
        beneficiary_ids = data.get('beneficiary_ids', [])
        report_type = data.get('report_type', 'progress')
        time_period = data.get('time_period', 'last_month')
        
        # Validate inputs
        if not beneficiary_ids:
            return jsonify({'error': 'beneficiary_ids array is required'}), 400
        
        if len(beneficiary_ids) > 20:
            return jsonify({'error': 'Maximum 20 beneficiaries allowed for batch processing'}), 400
        
        # Generate reports
        reports = []
        errors = []
        
        for ben_id in beneficiary_ids:
            report, error = ai_report_service.generate_beneficiary_report(
                beneficiary_id=ben_id,
                report_type=report_type,
                time_period=time_period
            )
            
            if error:
                errors.append({
                    'beneficiary_id': ben_id,
                    'error': error
                })
            else:
                reports.append({
                    'beneficiary_id': ben_id,
                    'report': report
                })
        
        return jsonify({
            'successful_reports': len(reports),
            'failed_reports': len(errors),
            'reports': reports,
            'errors': errors
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/export/<int:beneficiary_id>', methods=['POST'])
@jwt_required()
@role_required(['trainer', 'tenant_admin', 'super_admin'])
def export_report(beneficiary_id):
    """Export a report in different formats (PDF, DOCX, etc.)."""
    try:
        data = request.get_json()
        
        # Get parameters
        report_type = data.get('report_type', 'comprehensive')
        time_period = data.get('time_period', 'last_month')
        format_type = data.get('format', 'pdf')
        
        # Validate format
        valid_formats = ['pdf', 'docx', 'html']
        if format_type not in valid_formats:
            return jsonify({'error': f'Invalid format. Must be one of: {valid_formats}'}), 400
        
        # Generate report
        report, error = ai_report_service.generate_beneficiary_report(
            beneficiary_id=beneficiary_id,
            report_type=report_type,
            time_period=time_period
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        # For now, return the report data with export instructions
        # In production, this would generate actual PDF/DOCX files
        return jsonify({
            'message': f'Report ready for export in {format_type} format',
            'report_data': report,
            'export_format': format_type,
            'download_url': f'/api/ai-reports/download/{beneficiary_id}/{report_type}/{format_type}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500