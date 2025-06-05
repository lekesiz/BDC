"""Document API endpoints."""

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid
from datetime import datetime
from io import BytesIO
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.evaluation import Evaluation
from app.models.document import Document
from app.models.document_permission import DocumentPermission
from app.services.document_service import DocumentService
from app.services.document_version_service import DocumentVersionService
from app.services.notification_service import NotificationService
from app.utils import generate_evaluation_report, generate_beneficiary_report, analyze_evaluation_responses, generate_report_content

from app.utils.logging import logger

documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents', methods=['GET'])
@jwt_required()
def get_documents():
    """Get documents accessible by the current user."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get query parameters for pagination and filtering
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    document_type = request.args.get('type', None)
    search = request.args.get('search', None)
    
    # Base query
    query = Document.query
    
    # Filter by user role and permissions
    if user.role == 'student':
        # Students can only see their own documents
        beneficiary = Beneficiary.query.filter_by(user_id=user_id).first()
        if beneficiary:
            query = query.filter_by(beneficiary_id=beneficiary.id)
        else:
            return jsonify({'documents': [], 'total': 0, 'pages': 0}), 200
    elif user.role == 'trainer':
        # Trainers can see documents of their assigned beneficiaries
        beneficiary_ids = [b.id for b in Beneficiary.query.filter_by(trainer_id=user_id).all()]
        if beneficiary_ids:
            query = query.filter(Document.beneficiary_id.in_(beneficiary_ids))
        else:
            return jsonify({'documents': [], 'total': 0, 'pages': 0}), 200
    
    # Apply filters
    if document_type:
        query = query.filter_by(document_type=document_type)
    
    if search:
        query = query.filter(Document.title.contains(search))
    
    # Apply active filter
    query = query.filter_by(is_active=True)
    
    # Order by created date
    query = query.order_by(Document.created_at.desc())
    
    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Serialize documents
    documents = [doc.to_dict() for doc in pagination.items]
    
    return jsonify({
        'documents': documents,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@documents_bp.route('/documents/<int:id>', methods=['GET'])
@jwt_required()
def get_document(id):
    """Get a specific document by ID."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_access_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to access this document'}), 403
    
    return jsonify(document.to_dict()), 200


@documents_bp.route('/documents/<int:id>', methods=['PUT'])
@jwt_required()
def update_document(id):
    """Update a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_modify_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to modify this document'}), 403
    
    # Get update data
    data = request.get_json()
    
    # Update allowed fields
    if 'title' in data:
        document.title = data['title']
    if 'description' in data:
        document.description = data['description']
    if 'tags' in data:
        document.tags = data['tags']
    if 'category' in data:
        document.category = data['category']
    
    document.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Document updated successfully',
            'document': document.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating document: {str(e)}")
        return jsonify({'error': 'server_error', 'message': 'Failed to update document'}), 500


@documents_bp.route('/documents/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_document(id):
    """Delete a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_delete_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to delete this document'}), 403
    
    # Soft delete
    document.is_active = False
    document.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Delete physical file if exists
        if document.file_path and os.path.exists(document.file_path):
            try:
                os.remove(document.file_path)
            except Exception as e:
                current_app.logger.error(f"Error deleting file: {str(e)}")
        
        return jsonify({'message': 'Document deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting document: {str(e)}")
        return jsonify({'error': 'server_error', 'message': 'Failed to delete document'}), 500


@documents_bp.route('/documents/<int:id>/download', methods=['GET'])
@jwt_required()
def download_document(id):
    """Download a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_access_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to download this document'}), 403
    
    # Check if file exists
    if not document.file_path or not os.path.exists(document.file_path):
        return jsonify({'error': 'not_found', 'message': 'Document file not found'}), 404
    
    # Record download
    document.download_count = (document.download_count or 0) + 1
    document.last_accessed_at = datetime.utcnow()
    db.session.commit()
    
    # Send file
    return send_file(
        document.file_path,
        mimetype=document.mime_type or 'application/octet-stream',
        as_attachment=True,
        download_name=document.filename or f"document_{id}"
    )


@documents_bp.route('/documents/<int:id>/share', methods=['POST'])
@jwt_required()
def share_document(id):
    """Share a document with other users."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_share_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to share this document'}), 403
    
    # Get share data
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    permission_type = data.get('permission_type', 'view')  # view, edit, delete
    
    if not user_ids:
        return jsonify({'error': 'validation_error', 'message': 'No users specified to share with'}), 400
    
    if permission_type not in ['view', 'edit', 'delete']:
        return jsonify({'error': 'validation_error', 'message': 'Invalid permission type'}), 400
    
    # Create permissions
    shared_with = []
    for uid in user_ids:
        # Check if user exists
        target_user = User.query.get(uid)
        if not target_user:
            continue
        
        # Check if permission already exists
        existing = DocumentPermission.query.filter_by(
            document_id=document.id,
            user_id=uid
        ).first()
        
        if existing:
            # Update existing permission
            existing.permission_type = permission_type
            existing.updated_at = datetime.utcnow()
        else:
            # Create new permission
            permission = DocumentPermission(
                document_id=document.id,
                user_id=uid,
                permission_type=permission_type,
                granted_by_id=user_id
            )
            db.session.add(permission)
        
        shared_with.append({
            'user_id': uid,
            'name': f"{target_user.first_name} {target_user.last_name}",
            'email': target_user.email,
            'permission': permission_type
        })
        
        # Send notification
        NotificationService.create_notification(
            user_id=uid,
            title='Document Shared',
            message=f'{user.first_name} {user.last_name} has shared "{document.title}" with you',
            type='document',
            related_id=document.id,
            related_type='document',
            sender_id=user_id
        )
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Document shared successfully',
            'shared_with': shared_with
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sharing document: {str(e)}")
        return jsonify({'error': 'server_error', 'message': 'Failed to share document'}), 500


@documents_bp.route('/documents/evaluation-report/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def get_evaluation_report(evaluation_id):
    """Generate and download a PDF report for a specific evaluation."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the evaluation
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    
    # Get the beneficiary
    beneficiary = Beneficiary.query.get_or_404(evaluation.beneficiary_id)
    
    # Check permissions (only trainers assigned to this beneficiary or admins can access)
    if user.role not in ['super_admin', 'tenant_admin'] and \
       (user.role != 'trainer' or beneficiary.trainer_id != user_id):
        return jsonify({"error": "Not authorized to access this evaluation"}), 403
    
    # Generate the PDF
    pdf_content = generate_evaluation_report(evaluation, user, beneficiary)
    
    # Create a file-like buffer for the PDF
    buffer = BytesIO(pdf_content)
    buffer.seek(0)
    
    # Create filename
    filename = f"evaluation_report_{evaluation_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Send the file
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@documents_bp.route('/documents/beneficiary-report/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
def get_beneficiary_report(beneficiary_id):
    """Generate and download a comprehensive PDF report for a beneficiary."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the beneficiary
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    
    # Check permissions (only trainers assigned to this beneficiary or admins can access)
    if user.role not in ['super_admin', 'tenant_admin'] and \
       (user.role != 'trainer' or beneficiary.trainer_id != user_id):
        return jsonify({"error": "Not authorized to access this beneficiary"}), 403
    
    # Get all evaluations for this beneficiary
    evaluations = Evaluation.query.filter_by(beneficiary_id=beneficiary_id).all()
    
    # Generate the PDF
    pdf_content = generate_beneficiary_report(beneficiary, evaluations, user)
    
    # Create a file-like buffer for the PDF
    buffer = BytesIO(pdf_content)
    buffer.seek(0)
    
    # Create filename
    filename = f"beneficiary_report_{beneficiary_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Send the file
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@documents_bp.route('/documents/analyze-evaluation/<int:evaluation_id>', methods=['GET'])
@jwt_required()
def analyze_evaluation(evaluation_id):
    """Analyze an evaluation using AI and return the insights."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the evaluation
    evaluation = Evaluation.query.get_or_404(evaluation_id)
    
    # Get the beneficiary
    beneficiary = Beneficiary.query.get_or_404(evaluation.beneficiary_id)
    
    # Check permissions (only trainers assigned to this beneficiary or admins can access)
    if user.role not in ['super_admin', 'tenant_admin'] and \
       (user.role != 'trainer' or beneficiary.trainer_id != user_id):
        return jsonify({"error": "Not authorized to access this evaluation"}), 403
    
    # Convert the evaluation to a dictionary
    evaluation_dict = {
        'id': evaluation.id,
        'title': evaluation.title,
        'beneficiary_id': evaluation.beneficiary_id,
        'status': evaluation.status,
        'score': evaluation.score,
        'questions': [
            {
                'id': q.id,
                'text': q.text,
                'answer': {
                    'id': a.id,
                    'text': a.text,
                    'score': a.score
                } if hasattr(q, 'answer') and q.answer else None
            } for q in evaluation.questions
        ] if hasattr(evaluation, 'questions') else []
    }
    
    # Analyze the evaluation
    analysis = analyze_evaluation_responses(evaluation_dict)
    
    return jsonify(analysis), 200


@documents_bp.route('/documents/generate-report/<int:beneficiary_id>', methods=['GET'])
@jwt_required()
def generate_beneficiary_ai_report(beneficiary_id):
    """Generate a report for a beneficiary using AI and return the content."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the beneficiary
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    
    # Check permissions (only trainers assigned to this beneficiary or admins can access)
    if user.role not in ['super_admin', 'tenant_admin'] and \
       (user.role != 'trainer' or beneficiary.trainer_id != user_id):
        return jsonify({"error": "Not authorized to access this beneficiary"}), 403
    
    # Get all evaluations for this beneficiary
    evaluations = Evaluation.query.filter_by(beneficiary_id=beneficiary_id).all()
    
    # Convert beneficiary and evaluations to dictionaries
    beneficiary_dict = {
        'id': beneficiary.id,
        'first_name': beneficiary.first_name,
        'last_name': beneficiary.last_name,
        'email': beneficiary.email,
        'status': beneficiary.status
    }
    
    evaluation_dicts = [
        {
            'id': eval.id,
            'title': eval.title,
            'status': eval.status,
            'score': eval.score,
            'date_created': eval.date_created.isoformat()
        } for eval in evaluations
    ]
    
    # Generate the report content
    report_content = generate_report_content(beneficiary_dict, evaluation_dicts)
    
    return jsonify(report_content), 200


@documents_bp.route('/documents/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """Upload a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Get additional metadata
    document_type = request.form.get('type', 'general')
    beneficiary_id = request.form.get('beneficiary_id')
    evaluation_id = request.form.get('evaluation_id')
    title = request.form.get('title', 'Untitled Document')
    description = request.form.get('description', '')
    
    # Check file type
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx', 'xls', 'xlsx'})
    if not file.filename.lower().endswith(tuple('.' + ext for ext in allowed_extensions)):
        return jsonify({"error": f"Only {', '.join(allowed_extensions)} files are allowed"}), 400
    
    # Save file
    filename = secure_filename(file.filename)
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Create folder path based on document type
    folder_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documents', document_type)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
    
    file_path = os.path.join(folder_path, unique_filename)
    
    # Save file
    file.save(file_path)
    
    # Create document record in database
    # Note: This assumes you have a Document model; if not, you'd need to create one
    from app.models.document import Document
    
    document = Document(
        title=title,
        description=description,
        file_path=f"/uploads/documents/{document_type}/{unique_filename}",
        file_type=os.path.splitext(filename)[1][1:],  # Get extension without the dot
        file_size=os.path.getsize(file_path),
        upload_by=user_id,
        document_type=document_type
    )
    
    if beneficiary_id:
        document.beneficiary_id = beneficiary_id
    
    if evaluation_id:
        document.evaluation_id = evaluation_id
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify({
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "file_path": document.file_path
    }), 201


@documents_bp.route('/documents/<int:document_id>/permissions', methods=['GET'])
@jwt_required()
def get_document_permissions(document_id):
    """Get all permissions for a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(document_id)
    
    # Check permissions
    if document.upload_by != user_id and not user.role in ['super_admin', 'tenant_admin']:
        # Check if the user has permission to view this document's permissions
        if not DocumentService.check_permission(document_id, user_id, 'share'):
            return jsonify({"error": "Not authorized to view document permissions"}), 403
    
    # Get permissions
    permissions = DocumentService.get_document_permissions(document_id)
    
    return jsonify({
        "document_id": document_id,
        "permissions": permissions
    }), 200


@documents_bp.route('/documents/<int:document_id>/permissions', methods=['POST'])
@jwt_required()
def grant_document_permission(document_id):
    """Grant permission to a user or role for a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(document_id)
    
    # Check permissions
    if document.upload_by != user_id and not user.role in ['super_admin', 'tenant_admin']:
        # Check if the user has permission to share this document
        if not DocumentService.check_permission(document_id, user_id, 'share'):
            return jsonify({"error": "Not authorized to share this document"}), 403
    
    # Validate request data
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    # Get permission data
    target_user_id = request.json.get('user_id')
    target_role = request.json.get('role')
    
    if not target_user_id and not target_role:
        return jsonify({"error": "Either user_id or role must be provided"}), 400
    
    # Get permissions
    permissions = request.json.get('permissions', {})
    
    # Get expiry
    expires_in = request.json.get('expires_in')
    
    # Grant permission
    permission = DocumentService.grant_permission(
        document_id=document_id,
        user_id=target_user_id,
        role=target_role,
        permissions=permissions,
        expires_in=expires_in
    )
    
    if not permission:
        return jsonify({"error": "Failed to grant permission"}), 500
    
    return jsonify({
        "message": "Permission granted successfully",
        "permission": permission.to_dict()
    }), 201


@documents_bp.route('/documents/<int:document_id>/permissions', methods=['DELETE'])
@jwt_required()
def revoke_document_permission(document_id):
    """Revoke permission from a user or role for a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(document_id)
    
    # Check permissions
    if document.upload_by != user_id and not user.role in ['super_admin', 'tenant_admin']:
        return jsonify({"error": "Not authorized to revoke document permissions"}), 403
    
    # Validate request data
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400
    
    # Get permission data
    target_user_id = request.json.get('user_id')
    target_role = request.json.get('role')
    
    if not target_user_id and not target_role:
        return jsonify({"error": "Either user_id or role must be provided"}), 400
    
    # Revoke permission
    success = DocumentService.revoke_permission(
        document_id=document_id,
        user_id=target_user_id,
        role=target_role
    )
    
    if not success:
        return jsonify({"error": "Failed to revoke permission"}), 500
    
    return jsonify({
        "message": "Permission revoked successfully"
    }), 200


@documents_bp.route('/user/documents', methods=['GET'])
@jwt_required()
def get_user_documents():
    """Get all documents a user has access to."""
    user_id = get_jwt_identity()
    
    # Get documents
    documents = DocumentService.get_user_document_permissions(user_id)
    
    return jsonify({
        "documents": documents,
        "count": len(documents)
    }), 200


@documents_bp.route('/documents/<int:document_id>/check-permission', methods=['GET'])
@jwt_required()
def check_document_permission(document_id):
    """Check if a user has permission to access a document."""
    user_id = get_jwt_identity()
    
    # Get permission type from query parameter
    permission_type = request.args.get('type', 'read')
    
    # Check permission
    has_permission = DocumentService.check_permission(
        document_id=document_id,
        user_id=user_id,
        permission_type=permission_type
    )
    
    return jsonify({
        "has_permission": has_permission,
        "permission_type": permission_type
    }), 200


# Document Versioning Endpoints
@documents_bp.route('/documents/<int:id>/versions', methods=['GET'])
@jwt_required()
def get_document_versions(id):
    """Get all versions of a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_access_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to view this document'}), 403
    
    # Get include_archived parameter
    include_archived = request.args.get('include_archived', 'false').lower() == 'true'
    
    # Get versions
    versions = DocumentVersionService.get_versions(id, include_archived=include_archived)
    
    return jsonify({
        'document_id': id,
        'current_version': document.current_version,
        'version_control_enabled': document.version_control_enabled,
        'versions': [v.to_dict() for v in versions],
        'total': len(versions)
    }), 200


@documents_bp.route('/documents/<int:id>/versions', methods=['POST'])
@jwt_required()
def create_document_version(id):
    """Create a new version of a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_modify_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to modify this document'}), 403
    
    # Check if file is provided
    if 'file' not in request.files:
        return jsonify({'error': 'validation_error', 'message': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'validation_error', 'message': 'No file selected'}), 400
    
    # Get change notes
    change_notes = request.form.get('change_notes', '')
    
    try:
        # Create new version
        version = DocumentVersionService.create_version(
            document_id=id,
            file=file,
            user_id=user_id,
            change_notes=change_notes
        )
        
        return jsonify({
            'message': 'New version created successfully',
            'version': version.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'validation_error', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating document version: {str(e)}")
        return jsonify({'error': 'server_error', 'message': 'Failed to create document version'}), 500


@documents_bp.route('/documents/<int:id>/versions/<int:version_id>', methods=['GET'])
@jwt_required()
def get_document_version(id, version_id):
    """Get a specific version of a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_access_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to view this document'}), 403
    
    # Get version
    version = DocumentVersionService.get_version(version_id)
    
    if not version or version.document_id != id:
        return jsonify({'error': 'not_found', 'message': 'Version not found'}), 404
    
    return jsonify(version.to_dict()), 200


@documents_bp.route('/documents/<int:id>/versions/<int:version_id>/download', methods=['GET'])
@jwt_required()
def download_document_version(id, version_id):
    """Download a specific version of a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_access_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to download this document'}), 403
    
    # Get version
    version = DocumentVersionService.get_version(version_id)
    
    if not version or version.document_id != id:
        return jsonify({'error': 'not_found', 'message': 'Version not found'}), 404
    
    # Check if file exists
    if not os.path.exists(version.file_path):
        return jsonify({'error': 'not_found', 'message': 'Version file not found'}), 404
    
    # Send file
    return send_file(
        version.file_path,
        mimetype=version.mime_type or 'application/octet-stream',
        as_attachment=True,
        download_name=f"{version.filename}_v{version.version_number}"
    )


@documents_bp.route('/documents/<int:id>/versions/<int:version_id>/restore', methods=['POST'])
@jwt_required()
def restore_document_version(id, version_id):
    """Restore a previous version of a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_modify_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to modify this document'}), 403
    
    try:
        # Restore version
        new_version = DocumentVersionService.restore_version(
            document_id=id,
            version_id=version_id,
            user_id=user_id
        )
        
        return jsonify({
            'message': 'Version restored successfully',
            'version': new_version.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'validation_error', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error restoring document version: {str(e)}")
        return jsonify({'error': 'server_error', 'message': 'Failed to restore document version'}), 500


@documents_bp.route('/documents/<int:id>/versions/compare', methods=['POST'])
@jwt_required()
def compare_document_versions(id):
    """Compare two versions of a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions
    if not DocumentService.can_access_document(user, document):
        return jsonify({'error': 'forbidden', 'message': 'You do not have permission to view this document'}), 403
    
    # Get version IDs from request
    data = request.get_json()
    version1_id = data.get('version1_id')
    version2_id = data.get('version2_id')
    
    if not version1_id or not version2_id:
        return jsonify({'error': 'validation_error', 'message': 'Both version IDs are required'}), 400
    
    try:
        # Compare versions
        comparison = DocumentVersionService.compare_versions(
            document_id=id,
            version1_id=version1_id,
            version2_id=version2_id,
            user_id=user_id
        )
        
        return jsonify({
            'message': 'Versions compared successfully',
            'comparison': comparison.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'validation_error', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error comparing document versions: {str(e)}")
        return jsonify({'error': 'server_error', 'message': 'Failed to compare document versions'}), 500


@documents_bp.route('/documents/<int:id>/enable-versioning', methods=['POST'])
@jwt_required()
def enable_document_versioning(id):
    """Enable version control for a document."""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    # Get the document
    document = Document.query.get_or_404(id)
    
    # Check permissions (only owner or admin can enable versioning)
    if document.upload_by != user_id and user.role != 'super_admin':
        return jsonify({'error': 'forbidden', 'message': 'Only document owner or admin can enable versioning'}), 403
    
    # Get max versions from request
    data = request.get_json() or {}
    max_versions = data.get('max_versions', 10)
    
    try:
        # Enable versioning
        version = DocumentVersionService.enable_versioning(
            document_id=id,
            max_versions=max_versions
        )
        
        return jsonify({
            'message': 'Versioning enabled successfully',
            'version': version.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'validation_error', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error enabling document versioning: {str(e)}")
        return jsonify({'error': 'server_error', 'message': 'Failed to enable document versioning'}), 500