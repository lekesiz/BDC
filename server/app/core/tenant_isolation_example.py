"""
Example implementation of the Tenant Isolation System

This file demonstrates how to use the tenant isolation features in your models and API endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.core.tenant_isolation import (
    TenantMixin,
    TenantContextManager,
    require_tenant,
    with_tenant,
    validate_tenant_data,
    get_current_tenant
)

# Example 1: Creating a tenant-aware model
class Document(TenantMixin, db.Model):
    """Example document model with tenant isolation."""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # tenant_id is inherited from TenantMixin
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tenant_id': self.tenant_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Example 2: Creating API endpoints with tenant isolation
documents_bp = Blueprint('documents', __name__)

@documents_bp.route('/documents', methods=['GET'])
@jwt_required()
@require_tenant  # Ensures tenant context is set
def list_documents():
    """
    List all documents for the current tenant.
    Documents are automatically filtered by tenant.
    """
    # Option 1: Automatic filtering (recommended)
    documents = Document.query.all()  # Automatically filtered by tenant
    
    # Option 2: Explicit tenant filtering
    # documents = Document.for_tenant().all()
    
    return jsonify([doc.to_dict() for doc in documents])


@documents_bp.route('/documents/<int:document_id>', methods=['GET'])
@jwt_required()
@require_tenant
def get_document(document_id):
    """Get a specific document with tenant validation."""
    document = Document.query.get_or_404(document_id)
    
    # The query automatically ensures the document belongs to the current tenant
    # But you can also explicitly validate:
    document.ensure_tenant_access()
    
    return jsonify(document.to_dict())


@documents_bp.route('/documents', methods=['POST'])
@jwt_required()
@require_tenant
def create_document():
    """Create a new document for the current tenant."""
    data = request.get_json()
    
    # Method 1: Using create_for_tenant
    document = Document.create_for_tenant(
        title=data['title'],
        content=data.get('content', '')
    )
    
    # Method 2: Using validate_tenant_data
    # validated_data = validate_tenant_data(data)
    # document = Document(**validated_data)
    
    document.save()
    
    return jsonify(document.to_dict()), 201


@documents_bp.route('/documents/<int:document_id>', methods=['PUT'])
@jwt_required()
@require_tenant
def update_document(document_id):
    """Update a document with tenant validation."""
    document = Document.query.get_or_404(document_id)
    
    # Tenant access is automatically validated on query
    # But you can also explicitly check:
    document.ensure_tenant_access()
    
    data = request.get_json()
    document.title = data.get('title', document.title)
    document.content = data.get('content', document.content)
    
    document.save()  # Tenant validation happens automatically
    
    return jsonify(document.to_dict())


@documents_bp.route('/documents/<int:document_id>', methods=['DELETE'])
@jwt_required()
@require_tenant
def delete_document(document_id):
    """Delete a document with tenant validation."""
    document = Document.query.get_or_404(document_id)
    
    document.delete()  # Tenant validation happens automatically
    
    return '', 204


# Example 3: Admin endpoints that bypass tenant filtering
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/all-documents', methods=['GET'])
@jwt_required()
def list_all_documents():
    """
    Super admin endpoint to list documents across all tenants.
    """
    from app.models.user import User
    
    # Verify super admin access
    user = User.query.get(get_jwt_identity())
    if not user or user.role != 'super_admin':
        return {'error': 'Forbidden'}, 403
    
    # Query without tenant filtering
    documents = Document.query.without_tenant().all()
    
    return jsonify([doc.to_dict() for doc in documents])


@admin_bp.route('/admin/tenant/<int:tenant_id>/documents', methods=['GET'])
@jwt_required()
def list_tenant_documents(tenant_id):
    """
    Super admin endpoint to list documents for a specific tenant.
    """
    from app.models.user import User
    
    # Verify super admin access
    user = User.query.get(get_jwt_identity())
    if not user or user.role != 'super_admin':
        return {'error': 'Forbidden'}, 403
    
    # Query for specific tenant
    documents = Document.query.for_tenant(tenant_id).all()
    
    return jsonify([doc.to_dict() for doc in documents])


# Example 4: Background tasks with tenant context
@with_tenant(1)  # Execute with specific tenant context
def process_tenant_documents():
    """
    Background task that processes documents for tenant 1.
    All queries within this function are scoped to tenant 1.
    """
    documents = Document.query.filter_by(processed=False).all()
    for doc in documents:
        # Process document
        doc.processed = True
        doc.save()


# Example 5: Multi-tenant operations
def migrate_documents_between_tenants(from_tenant_id: int, to_tenant_id: int):
    """
    Example of operating across multiple tenants.
    """
    from app.models.user import User
    
    # This would typically require super admin privileges
    user = User.query.get(get_jwt_identity())
    if not user or user.role != 'super_admin':
        raise PermissionError("Only super admins can migrate between tenants")
    
    # Get documents from source tenant
    with TenantContextManager.tenant_context(from_tenant_id):
        source_documents = Document.query.all()
    
    # Copy to target tenant
    with TenantContextManager.tenant_context(to_tenant_id):
        for doc in source_documents:
            new_doc = Document.create_for_tenant(
                tenant_id=to_tenant_id,
                title=doc.title,
                content=doc.content
            )
            new_doc.save()


# Example 6: Bulk operations
@documents_bp.route('/documents/bulk', methods=['POST'])
@jwt_required()
@require_tenant
def bulk_create_documents():
    """Bulk create documents for the current tenant."""
    data = request.get_json()
    documents_data = data.get('documents', [])
    
    # Bulk create with automatic tenant assignment
    documents = Document.bulk_create_for_tenant(
        tenant_id=None,  # Uses current tenant
        instances=documents_data
    )
    
    return jsonify({
        'created': len(documents),
        'message': f'Created {len(documents)} documents'
    })


# Example 7: Switching tenants (for users with multiple tenants)
@documents_bp.route('/switch-tenant/<int:tenant_id>', methods=['POST'])
@jwt_required()
def switch_tenant(tenant_id):
    """
    Switch the current tenant context for users with access to multiple tenants.
    """
    from app.core.tenant_isolation import switch_tenant as do_switch
    
    try:
        do_switch(tenant_id)
        current_tenant = get_current_tenant()
        
        return jsonify({
            'message': 'Tenant switched successfully',
            'current_tenant': {
                'id': current_tenant.id,
                'name': current_tenant.name
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 403


# Example 8: Getting current tenant info
@documents_bp.route('/current-tenant', methods=['GET'])
@jwt_required()
@require_tenant
def get_current_tenant_info():
    """Get information about the current tenant."""
    tenant = get_current_tenant()
    
    return jsonify({
        'id': tenant.id,
        'name': tenant.name,
        'plan': tenant.plan,
        'is_active': tenant.is_active
    })


# Example 9: Custom query with tenant filtering
@documents_bp.route('/documents/search', methods=['GET'])
@jwt_required()
@require_tenant
def search_documents():
    """Search documents within the current tenant."""
    query = request.args.get('q', '')
    
    # Complex query with automatic tenant filtering
    documents = Document.query.filter(
        Document.title.contains(query) | Document.content.contains(query)
    ).order_by(Document.created_at.desc()).all()
    
    return jsonify([doc.to_dict() for doc in documents])


# Example 10: Integration with existing models
def integrate_tenant_isolation():
    """
    Example of how to integrate tenant isolation with existing models.
    """
    # For existing models, you can either:
    
    # 1. Add TenantMixin to the model inheritance
    # class ExistingModel(TenantMixin, db.Model):
    #     ...existing fields...
    
    # 2. Or manually add tenant_id and methods
    # class ExistingModel(db.Model):
    #     tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    #     
    #     def validate_tenant_access(self, tenant_id=None):
    #         if tenant_id is None:
    #             tenant_id = TenantContextManager.get_current_tenant_id()
    #         return self.tenant_id == tenant_id
    
    pass


"""
Usage in Application Initialization:

# In your app factory or initialization
from app.core.tenant_isolation import init_tenant_isolation

def create_app():
    app = Flask(__name__)
    
    # ... other initialization ...
    
    # Initialize tenant isolation
    init_tenant_isolation(app)
    
    # Register blueprints
    app.register_blueprint(documents_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
    return app
"""