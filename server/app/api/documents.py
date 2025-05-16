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
from app.services.notification_service import NotificationService
from app.utils import generate_evaluation_report, generate_beneficiary_report, analyze_evaluation_responses, generate_report_content

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