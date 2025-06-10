"""
Comprehensive Tenant Isolation System for BDC Project

This module provides a complete tenant isolation framework including:
- TenantMixin for all models
- Automatic tenant filtering in all queries
- Tenant context management
- Request-level tenant validation
"""

import functools
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Type, Any, List, Dict, Union, Callable
from flask import g, current_app, request, abort
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import event, inspect, and_, or_
from sqlalchemy.orm import Query, Session, scoped_session
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql import visitors
from werkzeug.local import LocalProxy

from app.extensions import db
from app.exceptions import TenantAccessError, TenantContextError


# Thread-local storage for tenant context
_tenant_context = threading.local()


class TenantContextManager:
    """
    Manages tenant context throughout the application lifecycle.
    Provides thread-safe tenant isolation.
    """
    
    @staticmethod
    def get_current_tenant_id() -> Optional[int]:
        """
        Get the current tenant ID from the context.
        
        Priority order:
        1. Explicitly set tenant ID in context
        2. Tenant ID from request context (g)
        3. Tenant ID from JWT token
        4. Tenant ID from authenticated user
        
        Returns:
            Optional[int]: Current tenant ID or None
        """
        # Check thread-local storage first
        if hasattr(_tenant_context, 'tenant_id'):
            return _tenant_context.tenant_id
        
        # Check Flask request context
        if hasattr(g, 'tenant_id') and g.tenant_id is not None:
            return g.tenant_id
        
        # Try to get from JWT claims
        try:
            jwt_claims = get_jwt()
            if jwt_claims and 'tenant_id' in jwt_claims:
                tenant_id = jwt_claims['tenant_id']
                TenantContextManager.set_tenant_id(tenant_id)
                return tenant_id
        except:
            pass
        
        # Try to get from current user
        try:
            user_id = get_jwt_identity()
            if user_id:
                from app.models.user import User
                user = User.query.get(user_id)
                if user:
                    # Get primary tenant if user has multiple
                    if hasattr(user, 'tenants') and user.tenants:
                        tenant_id = user.tenants[0].id
                    elif hasattr(user, 'tenant_id'):
                        tenant_id = user.tenant_id
                    else:
                        return None
                    
                    TenantContextManager.set_tenant_id(tenant_id)
                    return tenant_id
        except:
            pass
        
        return None
    
    @staticmethod
    def set_tenant_id(tenant_id: Optional[int]):
        """
        Set the tenant ID in both thread-local and request context.
        
        Args:
            tenant_id: The tenant ID to set
        """
        _tenant_context.tenant_id = tenant_id
        if hasattr(g, '_'):
            g.tenant_id = tenant_id
    
    @staticmethod
    def clear_tenant_context():
        """Clear all tenant context."""
        if hasattr(_tenant_context, 'tenant_id'):
            delattr(_tenant_context, 'tenant_id')
        if hasattr(g, 'tenant_id'):
            delattr(g, 'tenant_id')
    
    @staticmethod
    @contextmanager
    def tenant_context(tenant_id: int):
        """
        Context manager for temporarily setting tenant context.
        
        Usage:
            with TenantContextManager.tenant_context(tenant_id):
                # All queries within this block will be scoped to tenant_id
                documents = Document.query.all()
        """
        previous_tenant_id = TenantContextManager.get_current_tenant_id()
        TenantContextManager.set_tenant_id(tenant_id)
        try:
            yield
        finally:
            if previous_tenant_id is not None:
                TenantContextManager.set_tenant_id(previous_tenant_id)
            else:
                TenantContextManager.clear_tenant_context()
    
    @staticmethod
    def validate_tenant_id(tenant_id: int) -> bool:
        """
        Validate that a tenant ID exists and is active.
        
        Args:
            tenant_id: The tenant ID to validate
            
        Returns:
            bool: True if tenant is valid and active
        """
        from app.models.tenant import Tenant
        tenant = Tenant.query.get(tenant_id)
        return tenant is not None and tenant.is_active
    
    @staticmethod
    def get_user_tenant_ids(user_id: int) -> List[int]:
        """
        Get all tenant IDs accessible by a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List[int]: List of accessible tenant IDs
        """
        from app.models.user import User
        user = User.query.get(user_id)
        if not user:
            return []
        
        # Super admin has access to all tenants
        if user.role == 'super_admin':
            from app.models.tenant import Tenant
            return [t.id for t in Tenant.query.filter_by(is_active=True).all()]
        
        # Regular users have access to their assigned tenants
        if hasattr(user, 'tenants'):
            return [t.id for t in user.tenants if t.is_active]
        elif hasattr(user, 'tenant_id') and user.tenant_id:
            return [user.tenant_id]
        
        return []


class TenantMixin:
    """
    Mixin class that provides tenant isolation capabilities to any model.
    
    Features:
    - Automatic tenant filtering on queries
    - Tenant validation on create/update/delete
    - Utility methods for tenant operations
    """
    
    # Define tenant_id column - models can override this
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    
    @classmethod
    def query_class(cls):
        """Return a custom query class with tenant filtering."""
        return TenantQuery(cls, session=db.session)
    
    @classmethod
    def for_tenant(cls, tenant_id: Optional[int] = None):
        """
        Get query filtered by tenant.
        
        Args:
            tenant_id: Specific tenant ID or None for current tenant
            
        Returns:
            Query object filtered by tenant
        """
        if tenant_id is None:
            tenant_id = TenantContextManager.get_current_tenant_id()
        
        if tenant_id is None:
            raise TenantContextError("No tenant context available")
        
        return cls.query.filter_by(tenant_id=tenant_id)
    
    @classmethod
    def create_for_tenant(cls, tenant_id: Optional[int] = None, **kwargs):
        """
        Create a new instance for a specific tenant.
        
        Args:
            tenant_id: Tenant ID or None for current tenant
            **kwargs: Model attributes
            
        Returns:
            New model instance
        """
        if tenant_id is None:
            tenant_id = TenantContextManager.get_current_tenant_id()
        
        if tenant_id is None:
            raise TenantContextError("No tenant context for creation")
        
        # Validate tenant exists and is active
        if not TenantContextManager.validate_tenant_id(tenant_id):
            raise TenantAccessError(f"Invalid or inactive tenant: {tenant_id}")
        
        kwargs['tenant_id'] = tenant_id
        return cls(**kwargs)
    
    def validate_tenant_access(self, tenant_id: Optional[int] = None) -> bool:
        """
        Validate that this instance belongs to the specified tenant.
        
        Args:
            tenant_id: Tenant ID to check or None for current tenant
            
        Returns:
            bool: True if access is allowed
        """
        if tenant_id is None:
            tenant_id = TenantContextManager.get_current_tenant_id()
        
        if tenant_id is None:
            # No tenant context - check if user is super admin
            try:
                user_id = get_jwt_identity()
                if user_id:
                    from app.models.user import User
                    user = User.query.get(user_id)
                    if user and user.role == 'super_admin':
                        return True
            except:
                pass
            return False
        
        return self.tenant_id == tenant_id
    
    def ensure_tenant_access(self, tenant_id: Optional[int] = None):
        """
        Ensure that this instance belongs to the specified tenant.
        Raises exception if access is denied.
        
        Args:
            tenant_id: Tenant ID to check or None for current tenant
            
        Raises:
            TenantAccessError: If access is denied
        """
        if not self.validate_tenant_access(tenant_id):
            raise TenantAccessError(
                f"Access denied to {self.__class__.__name__} "
                f"(id={self.id}) for tenant {tenant_id}"
            )
    
    def save(self, validate_tenant: bool = True):
        """
        Save the instance with tenant validation.
        
        Args:
            validate_tenant: Whether to validate tenant access
            
        Raises:
            TenantAccessError: If tenant validation fails
        """
        if validate_tenant:
            self.ensure_tenant_access()
        
        # Set tenant_id if not already set
        if not self.tenant_id:
            tenant_id = TenantContextManager.get_current_tenant_id()
            if not tenant_id:
                raise TenantContextError("No tenant context for save operation")
            self.tenant_id = tenant_id
        
        db.session.add(self)
        db.session.commit()
    
    def delete(self, validate_tenant: bool = True):
        """
        Delete the instance with tenant validation.
        
        Args:
            validate_tenant: Whether to validate tenant access
            
        Raises:
            TenantAccessError: If tenant validation fails
        """
        if validate_tenant:
            self.ensure_tenant_access()
        
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def bulk_create_for_tenant(cls, tenant_id: Optional[int], instances: List[Dict]):
        """
        Bulk create instances for a tenant.
        
        Args:
            tenant_id: Tenant ID or None for current tenant
            instances: List of instance dictionaries
            
        Returns:
            List of created instances
        """
        if tenant_id is None:
            tenant_id = TenantContextManager.get_current_tenant_id()
        
        if tenant_id is None:
            raise TenantContextError("No tenant context for bulk creation")
        
        created = []
        for instance_data in instances:
            instance_data['tenant_id'] = tenant_id
            created.append(cls(**instance_data))
        
        db.session.bulk_save_objects(created)
        db.session.commit()
        return created


class TenantQuery(Query):
    """
    Custom query class that automatically applies tenant filtering.
    """
    
    def __init__(self, entities, session=None):
        super().__init__(entities, session)
        self._tenant_filter_applied = False
        self._disable_tenant_filter = False
    
    def _apply_tenant_filter(self):
        """Apply tenant filter if not already applied."""
        if self._tenant_filter_applied or self._disable_tenant_filter:
            return self
        
        tenant_id = TenantContextManager.get_current_tenant_id()
        if tenant_id is None:
            return self
        
        # Apply filter to each entity that has tenant_id
        for entity in self.column_descriptions:
            if entity.get('type') and hasattr(entity['type'], 'tenant_id'):
                self = self.filter(entity['type'].tenant_id == tenant_id)
                self._tenant_filter_applied = True
        
        return self
    
    def without_tenant(self):
        """
        Disable tenant filtering for this query.
        Use with caution - typically only for super admin operations.
        
        Returns:
            Query without tenant filtering
        """
        self._disable_tenant_filter = True
        return self
    
    def for_tenant(self, tenant_id: int):
        """
        Filter query for a specific tenant.
        
        Args:
            tenant_id: The tenant ID to filter by
            
        Returns:
            Filtered query
        """
        self._disable_tenant_filter = True
        for entity in self.column_descriptions:
            if entity.get('type') and hasattr(entity['type'], 'tenant_id'):
                self = self.filter(entity['type'].tenant_id == tenant_id)
        return self
    
    def all(self):
        """Override to apply tenant filter before executing."""
        return self._apply_tenant_filter().all()
    
    def first(self):
        """Override to apply tenant filter before executing."""
        return self._apply_tenant_filter().first()
    
    def one(self):
        """Override to apply tenant filter before executing."""
        return self._apply_tenant_filter().one()
    
    def one_or_none(self):
        """Override to apply tenant filter before executing."""
        return self._apply_tenant_filter().one_or_none()
    
    def count(self):
        """Override to apply tenant filter before executing."""
        return self._apply_tenant_filter().count()
    
    def exists(self):
        """Override to apply tenant filter before executing."""
        return self._apply_tenant_filter().exists()
    
    def __iter__(self):
        """Override to apply tenant filter before iterating."""
        return self._apply_tenant_filter().__iter__()


# SQLAlchemy Event Listeners for Automatic Tenant Handling
@event.listens_for(Session, "before_bulk_insert")
def receive_before_bulk_insert(mapper, connection, state):
    """Automatically set tenant_id on bulk inserts."""
    tenant_id = TenantContextManager.get_current_tenant_id()
    if tenant_id and hasattr(mapper.class_, 'tenant_id'):
        for instance in state:
            if not instance.get('tenant_id'):
                instance['tenant_id'] = tenant_id


@event.listens_for(db.Model, "before_insert", propagate=True)
def receive_before_insert(mapper, connection, target):
    """Automatically set tenant_id before insert."""
    if hasattr(target, 'tenant_id') and not target.tenant_id:
        tenant_id = TenantContextManager.get_current_tenant_id()
        if tenant_id:
            target.tenant_id = tenant_id
        elif not hasattr(target, '_skip_tenant_check'):
            raise TenantContextError(
                f"No tenant context for inserting {target.__class__.__name__}"
            )


@event.listens_for(db.Model, "before_update", propagate=True)
def receive_before_update(mapper, connection, target):
    """Validate tenant access before update."""
    if hasattr(target, 'tenant_id') and hasattr(target, 'validate_tenant_access'):
        if not hasattr(target, '_skip_tenant_check') and not target.validate_tenant_access():
            raise TenantAccessError(
                f"Cannot update {target.__class__.__name__} "
                f"(id={target.id}) - tenant access denied"
            )


# Decorators for Tenant Isolation
def require_tenant(f: Callable) -> Callable:
    """
    Decorator to ensure tenant context is set for the request.
    
    Usage:
        @require_tenant
        def my_view():
            # Tenant context is guaranteed to be set
            pass
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = TenantContextManager.get_current_tenant_id()
        if not tenant_id:
            abort(403, description="No tenant context available")
        
        # Validate tenant is active
        if not TenantContextManager.validate_tenant_id(tenant_id):
            abort(403, description="Invalid or inactive tenant")
        
        return f(*args, **kwargs)
    return decorated_function


def with_tenant(tenant_id: int):
    """
    Decorator to execute a function with a specific tenant context.
    
    Args:
        tenant_id: The tenant ID to use
        
    Usage:
        @with_tenant(1)
        def process_tenant_data():
            # All queries will be scoped to tenant 1
            pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            with TenantContextManager.tenant_context(tenant_id):
                return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_tenant_data(data: Dict[str, Any], tenant_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Validate and inject tenant_id into data dictionary.
    
    Args:
        data: Data dictionary
        tenant_id: Tenant ID or None for current tenant
        
    Returns:
        Updated data dictionary with tenant_id
        
    Raises:
        TenantContextError: If no tenant context available
    """
    if tenant_id is None:
        tenant_id = TenantContextManager.get_current_tenant_id()
    
    if tenant_id is None:
        raise TenantContextError("No tenant context for data validation")
    
    data['tenant_id'] = tenant_id
    return data


# Request hooks for automatic tenant context management
def init_tenant_isolation(app):
    """
    Initialize tenant isolation for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def set_tenant_context():
        """Set tenant context from request."""
        # Clear any existing context
        TenantContextManager.clear_tenant_context()
        
        # Try to set from request headers
        tenant_header = request.headers.get('X-Tenant-ID')
        if tenant_header:
            try:
                tenant_id = int(tenant_header)
                # Validate user has access to this tenant
                user_id = get_jwt_identity()
                if user_id:
                    tenant_ids = TenantContextManager.get_user_tenant_ids(user_id)
                    if tenant_id in tenant_ids:
                        TenantContextManager.set_tenant_id(tenant_id)
            except:
                pass
    
    @app.teardown_request
    def clear_tenant_context(exception=None):
        """Clear tenant context after request."""
        TenantContextManager.clear_tenant_context()


# Utility functions
def get_current_tenant():
    """
    Get the current tenant object.
    
    Returns:
        Tenant object or None
    """
    tenant_id = TenantContextManager.get_current_tenant_id()
    if tenant_id:
        from app.models.tenant import Tenant
        return Tenant.query.get(tenant_id)
    return None


def switch_tenant(tenant_id: int):
    """
    Switch to a different tenant context.
    
    Args:
        tenant_id: The tenant ID to switch to
        
    Raises:
        TenantAccessError: If user doesn't have access to the tenant
    """
    user_id = get_jwt_identity()
    if not user_id:
        raise TenantAccessError("No authenticated user")
    
    tenant_ids = TenantContextManager.get_user_tenant_ids(user_id)
    if tenant_id not in tenant_ids:
        raise TenantAccessError(f"User does not have access to tenant {tenant_id}")
    
    TenantContextManager.set_tenant_id(tenant_id)


# Export main components
__all__ = [
    'TenantContextManager',
    'TenantMixin',
    'TenantQuery',
    'require_tenant',
    'with_tenant',
    'validate_tenant_data',
    'init_tenant_isolation',
    'get_current_tenant',
    'switch_tenant',
]