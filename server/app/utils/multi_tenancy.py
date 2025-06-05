"""Multi-tenancy utilities for row-level security."""

from functools import wraps
from flask import g, current_app
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import and_
from typing import Optional, Type, Any
from app.models.user import User
from app.extensions import db


class TenantContext:
    """Manages tenant context for the current request."""
    
    @staticmethod
    def get_current_tenant_id() -> Optional[int]:
        """Get current tenant ID from request context."""
        # First check if explicitly set in g
        if hasattr(g, 'tenant_id') and g.tenant_id:
            return g.tenant_id
        
        # Try to get from current user
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(user_id)
            if user and user.tenant_id:
                g.tenant_id = user.tenant_id
                return user.tenant_id
        
        return None
    
    @staticmethod
    def set_tenant_id(tenant_id: int):
        """Explicitly set tenant ID for the request."""
        g.tenant_id = tenant_id
    
    @staticmethod
    def clear_tenant_id():
        """Clear tenant ID from request context."""
        if hasattr(g, 'tenant_id'):
            delattr(g, 'tenant_id')


class TenantFilterMixin:
    """Mixin for models that need tenant filtering."""
    
    @classmethod
    def query_with_tenant(cls, tenant_id: Optional[int] = None):
        """Get query filtered by tenant."""
        if tenant_id is None:
            tenant_id = TenantContext.get_current_tenant_id()
        
        if tenant_id and hasattr(cls, 'tenant_id'):
            return cls.query.filter_by(tenant_id=tenant_id)
        return cls.query
    
    @classmethod
    def get_by_id_with_tenant(cls, id: int, tenant_id: Optional[int] = None):
        """Get record by ID with tenant check."""
        if tenant_id is None:
            tenant_id = TenantContext.get_current_tenant_id()
        
        query = cls.query.filter_by(id=id)
        if tenant_id and hasattr(cls, 'tenant_id'):
            query = query.filter_by(tenant_id=tenant_id)
        
        return query.first()
    
    def belongs_to_tenant(self, tenant_id: Optional[int] = None) -> bool:
        """Check if record belongs to tenant."""
        if not hasattr(self, 'tenant_id'):
            return True  # Model doesn't support multi-tenancy
        
        if tenant_id is None:
            tenant_id = TenantContext.get_current_tenant_id()
        
        if not tenant_id:
            return True  # No tenant context
        
        return self.tenant_id == tenant_id


def require_tenant(f):
    """Decorator to ensure tenant context is set."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = TenantContext.get_current_tenant_id()
        if not tenant_id:
            return {'error': 'No tenant context'}, 403
        return f(*args, **kwargs)
    return decorated_function


def with_tenant_filter(model_class: Type[db.Model]):
    """Decorator to automatically apply tenant filtering to queries."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Store original query method
            original_query = model_class.query
            
            # Replace with tenant-filtered query
            tenant_id = TenantContext.get_current_tenant_id()
            if tenant_id and hasattr(model_class, 'tenant_id'):
                model_class.query = model_class.query.filter_by(tenant_id=tenant_id)
            
            try:
                result = f(*args, **kwargs)
            finally:
                # Restore original query
                model_class.query = original_query
            
            return result
        return decorated_function
    return decorator


class TenantScopedQuery:
    """Custom query class that automatically applies tenant filtering."""
    
    def __init__(self, entities, session=None):
        self._query = db.Query(entities, session=session)
        self._tenant_filtered = False
    
    def _apply_tenant_filter(self):
        """Apply tenant filter if not already applied."""
        if not self._tenant_filtered:
            tenant_id = TenantContext.get_current_tenant_id()
            if tenant_id:
                # Check if any entity has tenant_id
                for entity in self._query.column_descriptions:
                    if hasattr(entity['type'], 'tenant_id'):
                        self._query = self._query.filter(
                            entity['type'].tenant_id == tenant_id
                        )
                self._tenant_filtered = True
        return self._query
    
    def __getattr__(self, name):
        """Proxy all methods to underlying query with tenant filter."""
        self._apply_tenant_filter()
        return getattr(self._query, name)


def add_tenant_id(instance: db.Model, tenant_id: Optional[int] = None):
    """Add tenant ID to instance before saving."""
    if hasattr(instance, 'tenant_id') and not instance.tenant_id:
        if tenant_id is None:
            tenant_id = TenantContext.get_current_tenant_id()
        if tenant_id:
            instance.tenant_id = tenant_id


def validate_tenant_access(instance: db.Model, tenant_id: Optional[int] = None) -> bool:
    """Validate that instance belongs to current tenant."""
    if not hasattr(instance, 'tenant_id'):
        return True  # No tenant field, allow access
    
    if tenant_id is None:
        tenant_id = TenantContext.get_current_tenant_id()
    
    if not tenant_id:
        # No tenant context - check user role
        user_id = get_jwt_identity()
        if user_id:
            user = User.query.get(user_id)
            if user and user.role == 'super_admin':
                return True  # Super admin can access all
        return False
    
    return instance.tenant_id == tenant_id


# SQLAlchemy event listeners for automatic tenant filtering
from sqlalchemy import event
from sqlalchemy.orm import Query

@event.listens_for(Query, "before_compile", propagate=True)
def apply_tenant_filter_on_query(query, delete_context):
    """Automatically apply tenant filter to all queries."""
    # Skip if explicitly disabled
    if hasattr(query, '_disable_tenant_filter'):
        return
    
    tenant_id = TenantContext.get_current_tenant_id()
    if not tenant_id:
        return
    
    # Apply filter to each entity that has tenant_id
    for entity in query.column_descriptions:
        if hasattr(entity.get('type'), 'tenant_id'):
            query = query.filter(entity['type'].tenant_id == tenant_id)


# Model base class with multi-tenancy support
class TenantModel(db.Model):
    """Base model class with multi-tenancy support."""
    __abstract__ = True
    
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    
    @classmethod
    def create(cls, **kwargs):
        """Create new instance with automatic tenant assignment."""
        instance = cls(**kwargs)
        add_tenant_id(instance)
        return instance
    
    def save(self):
        """Save instance with tenant validation."""
        add_tenant_id(self)
        if not validate_tenant_access(self):
            raise PermissionError("Cannot save to different tenant")
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """Delete instance with tenant validation."""
        if not validate_tenant_access(self):
            raise PermissionError("Cannot delete from different tenant")
        db.session.delete(self)
        db.session.commit()


# Usage example:
"""
# In models
from app.utils.multi_tenancy import TenantModel

class Document(TenantModel):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    # tenant_id is inherited from TenantModel

# In views
from app.utils.multi_tenancy import require_tenant, TenantContext

@app.route('/api/documents')
@jwt_required()
@require_tenant
def list_documents():
    # Documents will be automatically filtered by tenant
    documents = Document.query.all()
    return jsonify([d.to_dict() for d in documents])

# For super admin to access all tenants
@app.route('/api/admin/all-documents')
@jwt_required()
def list_all_documents():
    user = get_current_user()
    if user.role != 'super_admin':
        abort(403)
    
    # Temporarily clear tenant context
    TenantContext.clear_tenant_id()
    documents = Document.query.all()
    return jsonify([d.to_dict() for d in documents])
"""