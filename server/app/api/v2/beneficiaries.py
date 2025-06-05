"""Beneficiary API routes using dependency injection."""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import io

from app.core.container import get_beneficiary_service
from app.core.cache_manager import cache_manager, invalidate_beneficiary_cache
from app.schemas.beneficiary import BeneficiarySchema, NoteSchema
from app.schemas.document import DocumentSchema
from app.schemas.appointment import AppointmentSchema
from app.utils.decorators import validate_request, requires_permission

from app.utils.logging import logger


beneficiaries_bp_v2 = Blueprint('beneficiaries_v2', __name__, url_prefix='/api/v2/beneficiaries')
beneficiary_schema = BeneficiarySchema()
beneficiaries_schema = BeneficiarySchema(many=True)
note_schema = NoteSchema()
notes_schema = NoteSchema(many=True)
document_schema = DocumentSchema()
documents_schema = DocumentSchema(many=True)
appointment_schema = AppointmentSchema()
appointments_schema = AppointmentSchema(many=True)


@beneficiaries_bp_v2.route('', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.view')
@cache_manager.cache_response(ttl=300, key_prefix='beneficiaries_list')
def list_beneficiaries():
    """List beneficiaries with search and pagination."""
    # Get query parameters
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    # Build filters
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('city'):
        filters['city'] = request.args.get('city')
    if request.args.get('program_id'):
        filters['program_id'] = int(request.args.get('program_id'))
    
    service = get_beneficiary_service()
    result = service.search_beneficiaries(query, filters, page, per_page)
    
    return jsonify({
        'beneficiaries': beneficiaries_schema.dump(result['items']),
        'pagination': {
            'total': result['total'],
            'page': result['page'],
            'per_page': result['per_page'],
            'pages': result['pages']
        }
    }), 200


@beneficiaries_bp_v2.route('', methods=['POST'])
@jwt_required()
@requires_permission('beneficiaries.create')
@validate_request(beneficiary_schema)
def create_beneficiary():
    """Create a new beneficiary."""
    data = request.get_json()
    service = get_beneficiary_service()
    
    try:
        beneficiary = service.create_beneficiary(data)
        
        # Clear list cache as we have a new beneficiary
        cache_manager.clear_pattern('beneficiaries_list:*')
        
        return jsonify({
            'message': 'Beneficiary created successfully',
            'beneficiary': beneficiary_schema.dump(beneficiary)
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@beneficiaries_bp_v2.route('/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.view')
@cache_manager.cache_response(ttl=600, key_prefix='beneficiary_detail')
def get_beneficiary(beneficiary_id):
    """Get beneficiary details."""
    service = get_beneficiary_service()
    beneficiary = service.get_beneficiary(beneficiary_id)
    
    if not beneficiary:
        return jsonify({'error': 'Beneficiary not found'}), 404
    
    return jsonify({
        'beneficiary': beneficiary_schema.dump(beneficiary)
    }), 200


@beneficiaries_bp_v2.route('/<int:beneficiary_id>', methods=['PUT'])
@jwt_required()
@requires_permission('beneficiaries.edit')
@validate_request(beneficiary_schema)
def update_beneficiary(beneficiary_id):
    """Update beneficiary information."""
    data = request.get_json()
    service = get_beneficiary_service()
    
    beneficiary = service.update_beneficiary(beneficiary_id, data)
    if not beneficiary:
        return jsonify({'error': 'Beneficiary not found'}), 404
    
    # Invalidate cache for this beneficiary
    invalidate_beneficiary_cache(beneficiary_id)
    cache_manager.clear_pattern('beneficiaries_list:*')
    
    return jsonify({
        'message': 'Beneficiary updated successfully',
        'beneficiary': beneficiary_schema.dump(beneficiary)
    }), 200


@beneficiaries_bp_v2.route('/<int:beneficiary_id>', methods=['DELETE'])
@jwt_required()
@requires_permission('beneficiaries.delete')
def delete_beneficiary(beneficiary_id):
    """Delete a beneficiary."""
    service = get_beneficiary_service()
    
    if service.delete_beneficiary(beneficiary_id):
        # Invalidate cache for this beneficiary
        invalidate_beneficiary_cache(beneficiary_id)
        cache_manager.clear_pattern('beneficiaries_list:*')
        
        return jsonify({'message': 'Beneficiary deleted successfully'}), 200
    
    return jsonify({'error': 'Beneficiary not found'}), 404


@beneficiaries_bp_v2.route('/statistics', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.view')
@cache_manager.cache_response(ttl=900, key_prefix='beneficiary_stats')  # 15 min cache
def get_statistics():
    """Get beneficiary statistics."""
    service = get_beneficiary_service()
    stats = service.get_beneficiary_statistics()
    
    return jsonify(stats), 200


# Note management endpoints
@beneficiaries_bp_v2.route('/<int:beneficiary_id>/notes', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.view')
def get_notes(beneficiary_id):
    """Get beneficiary notes."""
    include_private = request.args.get('include_private', 'false').lower() == 'true'
    
    service = get_beneficiary_service()
    notes = service.get_notes(beneficiary_id, include_private)
    
    return jsonify({
        'notes': notes_schema.dump(notes)
    }), 200


@beneficiaries_bp_v2.route('/<int:beneficiary_id>/notes', methods=['POST'])
@jwt_required()
@requires_permission('beneficiaries.edit')
def add_note(beneficiary_id):
    """Add a note to beneficiary."""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    service = get_beneficiary_service()
    note = service.add_note(
        beneficiary_id=beneficiary_id,
        note_content=data.get('content'),
        note_type=data.get('note_type', 'general'),
        is_private=data.get('is_private', False),
        created_by_id=user_id
    )
    
    return jsonify({
        'message': 'Note added successfully',
        'note': note_schema.dump(note)
    }), 201


@beneficiaries_bp_v2.route('/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
@requires_permission('beneficiaries.edit')
def update_note(note_id):
    """Update a note."""
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    service = get_beneficiary_service()
    note = service.update_note(note_id, content)
    
    if not note:
        return jsonify({'error': 'Note not found'}), 404
    
    return jsonify({
        'message': 'Note updated successfully',
        'note': note_schema.dump(note)
    }), 200


@beneficiaries_bp_v2.route('/notes/<int:note_id>', methods=['DELETE'])
@jwt_required()
@requires_permission('beneficiaries.edit')
def delete_note(note_id):
    """Delete a note."""
    service = get_beneficiary_service()
    
    if service.delete_note(note_id):
        return jsonify({'message': 'Note deleted successfully'}), 200
    
    return jsonify({'error': 'Note not found'}), 404


# Document management endpoints
@beneficiaries_bp_v2.route('/<int:beneficiary_id>/documents', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.view')
def get_documents(beneficiary_id):
    """Get beneficiary documents."""
    document_type = request.args.get('type')
    
    service = get_beneficiary_service()
    documents = service.get_documents(beneficiary_id, document_type)
    
    return jsonify({
        'documents': documents_schema.dump(documents)
    }), 200


@beneficiaries_bp_v2.route('/<int:beneficiary_id>/documents', methods=['POST'])
@jwt_required()
@requires_permission('beneficiaries.edit')
def upload_document(beneficiary_id):
    """Upload a document for beneficiary."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    user_id = get_jwt_identity()
    
    service = get_beneficiary_service()
    document = service.upload_document(beneficiary_id, {
        'file': file,
        'title': request.form.get('title', file.filename),
        'document_type': request.form.get('document_type', 'other'),
        'uploaded_by_id': user_id
    })
    
    return jsonify({
        'message': 'Document uploaded successfully',
        'document': document_schema.dump(document)
    }), 201


@beneficiaries_bp_v2.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.view')
def download_document(document_id):
    """Download a document."""
    service = get_beneficiary_service()
    result = service.download_document(document_id)
    
    if not result:
        return jsonify({'error': 'Document not found'}), 404
    
    return send_file(
        io.BytesIO(result['content']),
        mimetype=result['mime_type'],
        as_attachment=True,
        download_name=result['filename']
    )


@beneficiaries_bp_v2.route('/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
@requires_permission('beneficiaries.edit')
def delete_document(document_id):
    """Delete a document."""
    service = get_beneficiary_service()
    
    if service.delete_document(document_id):
        return jsonify({'message': 'Document deleted successfully'}), 200
    
    return jsonify({'error': 'Document not found'}), 404


# Appointment management endpoints
@beneficiaries_bp_v2.route('/<int:beneficiary_id>/appointments', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.view')
def get_appointments(beneficiary_id):
    """Get beneficiary appointments."""
    include_past = request.args.get('include_past', 'false').lower() == 'true'
    
    service = get_beneficiary_service()
    appointments = service.get_appointments(beneficiary_id, include_past)
    
    return jsonify({
        'appointments': appointments_schema.dump(appointments)
    }), 200


@beneficiaries_bp_v2.route('/<int:beneficiary_id>/appointments', methods=['POST'])
@jwt_required()
@requires_permission('appointments.create')
@validate_request(appointment_schema)
def schedule_appointment(beneficiary_id):
    """Schedule an appointment."""
    data = request.get_json()
    user_id = get_jwt_identity()
    
    data['created_by_id'] = user_id
    
    service = get_beneficiary_service()
    appointment = service.schedule_appointment(beneficiary_id, data)
    
    return jsonify({
        'message': 'Appointment scheduled successfully',
        'appointment': appointment_schema.dump(appointment)
    }), 201


@beneficiaries_bp_v2.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@requires_permission('appointments.edit')
def update_appointment(appointment_id):
    """Update an appointment."""
    data = request.get_json()
    
    service = get_beneficiary_service()
    appointment = service.update_appointment(appointment_id, data)
    
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404
    
    return jsonify({
        'message': 'Appointment updated successfully',
        'appointment': appointment_schema.dump(appointment)
    }), 200


@beneficiaries_bp_v2.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@jwt_required()
@requires_permission('appointments.edit')
def cancel_appointment(appointment_id):
    """Cancel an appointment."""
    data = request.get_json()
    reason = data.get('reason')
    
    service = get_beneficiary_service()
    
    if service.cancel_appointment(appointment_id, reason):
        return jsonify({'message': 'Appointment cancelled successfully'}), 200
    
    return jsonify({'error': 'Appointment not found'}), 404


# Export endpoints
@beneficiaries_bp_v2.route('/<int:beneficiary_id>/export', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.export')
def export_beneficiary(beneficiary_id):
    """Export beneficiary data."""
    format = request.args.get('format', 'pdf')
    
    service = get_beneficiary_service()
    
    try:
        data = service.export_beneficiary_data(beneficiary_id, format)
        
        if format == 'pdf':
            return send_file(
                io.BytesIO(data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'beneficiary_{beneficiary_id}.pdf'
            )
        elif format == 'csv':
            return send_file(
                io.BytesIO(data),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'beneficiary_{beneficiary_id}.csv'
            )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@beneficiaries_bp_v2.route('/export', methods=['GET'])
@jwt_required()
@requires_permission('beneficiaries.export')
def export_beneficiaries():
    """Export list of beneficiaries."""
    format = request.args.get('format', 'csv')
    
    # Build filters
    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('city'):
        filters['city'] = request.args.get('city')
    
    service = get_beneficiary_service()
    
    try:
        data = service.export_beneficiaries_list(filters, format)
        
        return send_file(
            io.BytesIO(data),
            mimetype='text/csv',
            as_attachment=True,
            download_name='beneficiaries.csv'
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400