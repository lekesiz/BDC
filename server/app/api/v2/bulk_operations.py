"""Bulk operations API for efficient batch processing."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
from typing import List, Dict, Any
import csv
import io
from datetime import datetime

from app.extensions import db
from app.models import User, Beneficiary, Appointment, Document
from app.services.beneficiary_service import BeneficiaryService
from app.services.notification_service import NotificationService
from app.utils.decorators import requires_permission
from app.utils.logging import logger


bulk_bp = Blueprint('bulk_operations', __name__, url_prefix='/api/v2/bulk')


class BulkOperationSchema(Schema):
    """Schema for bulk operation requests."""
    operation = fields.Str(required=True, validate=validate.OneOf([
        'create', 'update', 'delete', 'assign', 'export'
    ]))
    entity_type = fields.Str(required=True, validate=validate.OneOf([
        'beneficiaries', 'appointments', 'documents', 'users'
    ]))
    data = fields.List(fields.Dict(), required=False)
    ids = fields.List(fields.Int(), required=False)
    filters = fields.Dict(required=False, missing={})
    fields_to_update = fields.Dict(required=False)


class BulkResultSchema(Schema):
    """Schema for bulk operation results."""
    total = fields.Int()
    successful = fields.Int()
    failed = fields.Int()
    errors = fields.List(fields.Dict())
    results = fields.List(fields.Dict())


bulk_operation_schema = BulkOperationSchema()
bulk_result_schema = BulkResultSchema()


@bulk_bp.route('/operations', methods=['POST'])
@jwt_required()
@requires_permission('bulk_operations.execute')
def execute_bulk_operation():
    """Execute a bulk operation on multiple entities."""
    try:
        data = bulk_operation_schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    operation = data['operation']
    entity_type = data['entity_type']
    
    # Route to appropriate handler
    handlers = {
        'create': handle_bulk_create,
        'update': handle_bulk_update,
        'delete': handle_bulk_delete,
        'assign': handle_bulk_assign,
        'export': handle_bulk_export
    }
    
    handler = handlers.get(operation)
    if not handler:
        return jsonify({'error': f'Unsupported operation: {operation}'}), 400
    
    try:
        result = handler(entity_type, data)
        return jsonify(bulk_result_schema.dump(result)), 200
    except Exception as e:
        logger.error(f"Bulk operation failed: {str(e)}")
        return jsonify({'error': 'Bulk operation failed', 'details': str(e)}), 500


def handle_bulk_create(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle bulk creation of entities."""
    items = data.get('data', [])
    if not items:
        raise ValueError("No data provided for bulk creation")
    
    results = {
        'total': len(items),
        'successful': 0,
        'failed': 0,
        'errors': [],
        'results': []
    }
    
    if entity_type == 'beneficiaries':
        service = get_beneficiary_service()
        for idx, item in enumerate(items):
            try:
                beneficiary = service.create_beneficiary(item)
                results['successful'] += 1
                results['results'].append({
                    'index': idx,
                    'id': beneficiary.id,
                    'status': 'created'
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'index': idx,
                    'error': str(e),
                    'data': item
                })
    
    elif entity_type == 'appointments':
        for idx, item in enumerate(items):
            try:
                appointment = Appointment(**item)
                db.session.add(appointment)
                db.session.flush()
                results['successful'] += 1
                results['results'].append({
                    'index': idx,
                    'id': appointment.id,
                    'status': 'created'
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'index': idx,
                    'error': str(e),
                    'data': item
                })
    
    # Commit all successful operations
    if results['successful'] > 0:
        db.session.commit()
    
    return results


def handle_bulk_update(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle bulk update of entities."""
    ids = data.get('ids', [])
    fields_to_update = data.get('fields_to_update', {})
    filters = data.get('filters', {})
    
    if not fields_to_update:
        raise ValueError("No fields to update specified")
    
    results = {
        'total': 0,
        'successful': 0,
        'failed': 0,
        'errors': [],
        'results': []
    }
    
    # Build query based on entity type
    if entity_type == 'beneficiaries':
        query = Beneficiary.query
        if ids:
            query = query.filter(Beneficiary.id.in_(ids))
        for key, value in filters.items():
            if hasattr(Beneficiary, key):
                query = query.filter(getattr(Beneficiary, key) == value)
        
        entities = query.all()
        results['total'] = len(entities)
        
        for entity in entities:
            try:
                for field, value in fields_to_update.items():
                    if hasattr(entity, field):
                        setattr(entity, field, value)
                entity.updated_at = datetime.utcnow()
                results['successful'] += 1
                results['results'].append({
                    'id': entity.id,
                    'status': 'updated'
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'id': entity.id,
                    'error': str(e)
                })
    
    # Commit all updates
    if results['successful'] > 0:
        db.session.commit()
    
    return results


def handle_bulk_delete(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle bulk deletion of entities."""
    ids = data.get('ids', [])
    filters = data.get('filters', {})
    
    if not ids and not filters:
        raise ValueError("No IDs or filters specified for deletion")
    
    results = {
        'total': 0,
        'successful': 0,
        'failed': 0,
        'errors': [],
        'results': []
    }
    
    if entity_type == 'beneficiaries':
        query = Beneficiary.query
        if ids:
            query = query.filter(Beneficiary.id.in_(ids))
        for key, value in filters.items():
            if hasattr(Beneficiary, key):
                query = query.filter(getattr(Beneficiary, key) == value)
        
        entities = query.all()
        results['total'] = len(entities)
        
        for entity in entities:
            try:
                # Check if entity can be deleted (e.g., no active appointments)
                if entity.appointments.filter_by(status='scheduled').count() > 0:
                    raise ValueError("Cannot delete beneficiary with scheduled appointments")
                
                db.session.delete(entity)
                results['successful'] += 1
                results['results'].append({
                    'id': entity.id,
                    'status': 'deleted'
                })
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'id': entity.id,
                    'error': str(e)
                })
    
    # Commit deletions
    if results['successful'] > 0:
        db.session.commit()
    
    return results


def handle_bulk_assign(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle bulk assignment operations (e.g., assign trainers to beneficiaries)."""
    ids = data.get('ids', [])
    assign_data = data.get('fields_to_update', {})
    
    results = {
        'total': len(ids),
        'successful': 0,
        'failed': 0,
        'errors': [],
        'results': []
    }
    
    if entity_type == 'beneficiaries' and 'trainer_id' in assign_data:
        trainer_id = assign_data['trainer_id']
        trainer = User.query.filter_by(id=trainer_id, role='trainer').first()
        
        if not trainer:
            raise ValueError("Invalid trainer ID")
        
        for beneficiary_id in ids:
            try:
                beneficiary = Beneficiary.query.get(beneficiary_id)
                if not beneficiary:
                    raise ValueError(f"Beneficiary {beneficiary_id} not found")
                
                # Assign trainer
                beneficiary.assigned_trainer_id = trainer_id
                beneficiary.updated_at = datetime.utcnow()
                
                results['successful'] += 1
                results['results'].append({
                    'beneficiary_id': beneficiary_id,
                    'trainer_id': trainer_id,
                    'status': 'assigned'
                })
                
                # Send notification
                notification_service = get_notification_service()
                notification_service.send_notification(
                    user_id=trainer_id,
                    type='beneficiary_assigned',
                    title='New Beneficiary Assigned',
                    message=f'{beneficiary.first_name} {beneficiary.last_name} has been assigned to you.',
                    data={'beneficiary_id': beneficiary_id}
                )
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'beneficiary_id': beneficiary_id,
                    'error': str(e)
                })
    
    # Commit assignments
    if results['successful'] > 0:
        db.session.commit()
    
    return results


def handle_bulk_export(entity_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle bulk export of entities."""
    ids = data.get('ids', [])
    filters = data.get('filters', {})
    export_format = data.get('format', 'csv')
    
    if entity_type == 'beneficiaries':
        query = Beneficiary.query
        if ids:
            query = query.filter(Beneficiary.id.in_(ids))
        for key, value in filters.items():
            if hasattr(Beneficiary, key):
                query = query.filter(getattr(Beneficiary, key) == value)
        
        beneficiaries = query.all()
        
        if export_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            headers = [
                'ID', 'First Name', 'Last Name', 'Email', 'Phone',
                'Status', 'City', 'Created At', 'Updated At'
            ]
            writer.writerow(headers)
            
            # Write data
            for b in beneficiaries:
                writer.writerow([
                    b.id, b.first_name, b.last_name, b.email, b.phone,
                    b.status, b.city, b.created_at, b.updated_at
                ])
            
            output.seek(0)
            return {
                'export_data': output.getvalue(),
                'format': 'csv',
                'filename': f'beneficiaries_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
    
    return {'error': 'Export not implemented for this entity type'}


@bulk_bp.route('/import/<entity_type>', methods=['POST'])
@jwt_required()
@requires_permission('bulk_operations.import')
def bulk_import(entity_type: str):
    """Import entities from uploaded file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files are supported'}), 400
    
    results = {
        'total': 0,
        'successful': 0,
        'failed': 0,
        'errors': [],
        'results': []
    }
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF-8"))
        csv_reader = csv.DictReader(stream)
        
        items = list(csv_reader)
        results['total'] = len(items)
        
        if entity_type == 'beneficiaries':
            service = get_beneficiary_service()
            for idx, row in enumerate(items):
                try:
                    # Map CSV columns to model fields
                    beneficiary_data = {
                        'first_name': row.get('First Name', ''),
                        'last_name': row.get('Last Name', ''),
                        'email': row.get('Email', ''),
                        'phone': row.get('Phone', ''),
                        'status': row.get('Status', 'active'),
                        'city': row.get('City', ''),
                        'address': row.get('Address', ''),
                        'country': row.get('Country', ''),
                    }
                    
                    beneficiary = service.create_beneficiary(beneficiary_data)
                    results['successful'] += 1
                    results['results'].append({
                        'row': idx + 1,
                        'id': beneficiary.id,
                        'status': 'imported'
                    })
                    
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'row': idx + 1,
                        'error': str(e),
                        'data': row
                    })
        
        # Commit successful imports
        if results['successful'] > 0:
            db.session.commit()
        
        return jsonify(bulk_result_schema.dump(results)), 200
        
    except Exception as e:
        logger.error(f"Bulk import failed: {str(e)}")
        return jsonify({'error': 'Import failed', 'details': str(e)}), 500


@bulk_bp.route('/templates/<entity_type>', methods=['GET'])
@jwt_required()
def get_import_template(entity_type: str):
    """Get CSV template for bulk import."""
    templates = {
        'beneficiaries': [
            'First Name', 'Last Name', 'Email', 'Phone',
            'Status', 'Address', 'City', 'Country'
        ],
        'appointments': [
            'Beneficiary Email', 'Trainer Email', 'Date', 'Time',
            'Duration', 'Type', 'Location', 'Notes'
        ]
    }
    
    if entity_type not in templates:
        return jsonify({'error': 'Template not available for this entity type'}), 404
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(templates[entity_type])
    
    # Add example row
    if entity_type == 'beneficiaries':
        writer.writerow([
            'John', 'Doe', 'john@example.com', '+1234567890',
            'active', '123 Main St', 'New York', 'USA'
        ])
    
    output.seek(0)
    
    return output.getvalue(), 200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': f'attachment; filename={entity_type}_import_template.csv'
    }


@bulk_bp.route('/validate', methods=['POST'])
@jwt_required()
@requires_permission('bulk_operations.execute')
def validate_bulk_operation():
    """Validate bulk operation before execution."""
    try:
        data = bulk_operation_schema.load(request.get_json())
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    validation_results = {
        'valid': True,
        'warnings': [],
        'errors': []
    }
    
    # Validate based on operation type
    if data['operation'] == 'delete':
        ids = data.get('ids', [])
        if len(ids) > 100:
            validation_results['warnings'].append(
                f'Large deletion operation ({len(ids)} items). This cannot be undone.'
            )
    
    elif data['operation'] == 'create':
        items = data.get('data', [])
        if len(items) > 1000:
            validation_results['errors'].append(
                'Cannot create more than 1000 items in a single operation'
            )
            validation_results['valid'] = False
    
    # Check permissions for specific operations
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if data['operation'] == 'delete' and user.role not in ['super_admin', 'admin']:
        validation_results['errors'].append(
            'Only administrators can perform bulk delete operations'
        )
        validation_results['valid'] = False
    
    return jsonify(validation_results), 200