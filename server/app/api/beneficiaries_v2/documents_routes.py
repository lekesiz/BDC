from flask import jsonify, current_app, request, send_file
from flask_jwt_extended import jwt_required, current_user
from werkzeug.utils import secure_filename
import os
from io import BytesIO

from app.middleware.request_context import role_required
from app.services import BeneficiaryService, DocumentService
from app.schemas import DocumentSchema
from app.extensions import db

from . import beneficiaries_bp


@beneficiaries_bp.route('/<int:beneficiary_id>/documents', methods=['GET'])
@jwt_required()
def list_documents(beneficiary_id):
    """Return documents for beneficiary."""
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        # tenant admin permission
        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        # Get documents for this beneficiary
        from app.models.document import Document
        documents = Document.query.filter_by(
            beneficiary_id=beneficiary_id,
            is_active=True
        ).order_by(Document.created_at.desc()).all()
        
        # Convert to dict format since we don't have DocumentSchema
        documents_data = []
        for doc in documents:
            documents_data.append({
                'id': doc.id,
                'title': doc.title,
                'description': doc.description,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'document_type': doc.document_type,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat(),
                'uploader': {
                    'id': doc.uploader.id,
                    'name': f"{doc.uploader.first_name} {doc.uploader.last_name}"
                } if doc.uploader else None
            })
        
        return jsonify({'documents': documents_data, 'total': len(documents_data)}), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500


@beneficiaries_bp.route('/<int:beneficiary_id>/profile-picture', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'tenant_admin', 'trainer'])
def upload_profile_picture(beneficiary_id):
    """Upload profile picture for beneficiary."""
    try:
        beneficiary = BeneficiaryService.get_beneficiary(beneficiary_id)
        if not beneficiary:
            return jsonify({'error': 'not_found', 'message': 'Beneficiary not found'}), 404

        if current_user.role == 'tenant_admin':
            tenant_id = current_user.tenants[0].id if current_user.tenants else None
            if beneficiary.tenant_id != tenant_id:
                return jsonify({'error': 'forbidden', 'message': 'Forbidden'}), 403

        if 'profile_picture' not in request.files:
            return jsonify({'error': 'no_file', 'message': 'No file provided'}), 400
        file = request.files['profile_picture']
        if file.filename == '':
            return jsonify({'error': 'no_file', 'message': 'No file selected'}), 400

        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({'error': 'invalid_type', 'message': 'Invalid file type'}), 400

        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile_pictures')
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f"beneficiary_{beneficiary_id}_{file.filename}")
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        beneficiary.user.profile_picture = f"profile_pictures/{filename}"
        db.session.commit()

        return jsonify({'message': 'Profile picture uploaded', 'path': f"profile_pictures/{filename}"}), 200
    except Exception as err:
        current_app.logger.exception(err)
        return jsonify({'error': 'server_error', 'message': 'Unexpected error'}), 500 