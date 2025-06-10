"""Model relationship optimizations - Applied via monkey patching to avoid changing core models."""

from sqlalchemy.orm import configure_mappers
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.evaluation import Evaluation
from app.models.document import Document
from app.models.program import Program
from app.models.tenant import Tenant


def apply_relationship_optimizations():
    """Apply relationship loading optimizations to models.
    
    This function modifies the lazy loading strategy for relationships
    to prevent N+1 queries in common use cases.
    """
    
    # Beneficiary optimizations
    # Change user, trainer, tenant to eagerly load since they're almost always needed
    Beneficiary.user.property.lazy = 'joined'  # Always need user info
    Beneficiary.trainer.property.lazy = 'joined'  # Often need trainer info
    Beneficiary.tenant.property.lazy = 'joined'  # Always need tenant context
    
    # Keep these as dynamic for filtering capabilities
    # Beneficiary.appointments - keep as dynamic
    # Beneficiary.documents - keep as dynamic
    # Beneficiary.evaluations - keep as dynamic
    
    # User optimizations
    # Tenant is almost always needed for context
    if hasattr(User, 'tenant'):
        User.tenant.property.lazy = 'joined'
    
    # Roles are checked frequently for permissions
    if hasattr(User, 'roles'):
        User.roles.property.lazy = 'selectin'
    
    # Appointment optimizations
    if hasattr(Appointment, 'trainer'):
        Appointment.trainer.property.lazy = 'joined'
    if hasattr(Appointment, 'beneficiary'):
        Appointment.beneficiary.property.lazy = 'joined'
    
    # Evaluation optimizations
    if hasattr(Evaluation, 'beneficiary'):
        Evaluation.beneficiary.property.lazy = 'joined'
    if hasattr(Evaluation, 'created_by'):
        Evaluation.created_by.property.lazy = 'joined'
    
    # Document optimizations
    if hasattr(Document, 'uploaded_by'):
        Document.uploaded_by.property.lazy = 'joined'
    if hasattr(Document, 'beneficiary'):
        Document.beneficiary.property.lazy = 'joined'
    
    # Program optimizations - keep modules eager, beneficiaries lazy
    if hasattr(Program, 'modules'):
        Program.modules.property.lazy = 'selectin'
    if hasattr(Program, 'created_by'):
        Program.created_by.property.lazy = 'joined'
    
    # Tenant optimizations
    if hasattr(Tenant, 'created_by'):
        Tenant.created_by.property.lazy = 'joined'
    
    # Force mapper configuration
    configure_mappers()


# Query optimization utilities
class QueryOptimizer:
    """Utilities for optimizing database queries."""
    
    @staticmethod
    def prefetch_relationships(query, model_class, relationships):
        """Prefetch specified relationships for a query.
        
        Args:
            query: SQLAlchemy query object
            model_class: The model class being queried
            relationships: List of relationship names to prefetch
            
        Returns:
            Modified query with eager loading options
        """
        from sqlalchemy.orm import joinedload, selectinload
        
        for rel in relationships:
            if '.' in rel:
                # Handle nested relationships
                parts = rel.split('.')
                option = joinedload(getattr(model_class, parts[0]))
                for part in parts[1:]:
                    option = option.joinedload(part)
                query = query.options(option)
            else:
                # Simple relationship
                rel_property = getattr(model_class, rel).property
                if rel_property.uselist:
                    # Use selectin for collections
                    query = query.options(selectinload(getattr(model_class, rel)))
                else:
                    # Use joined for single items
                    query = query.options(joinedload(getattr(model_class, rel)))
        
        return query
    
    @staticmethod
    def batch_load(model_class, ids, relationships=None):
        """Batch load multiple records with optimized relationship loading.
        
        Args:
            model_class: The model class to query
            ids: List of IDs to load
            relationships: Optional list of relationships to eager load
            
        Returns:
            List of model instances
        """
        query = model_class.query.filter(model_class.id.in_(ids))
        
        if relationships:
            query = QueryOptimizer.prefetch_relationships(query, model_class, relationships)
        
        return query.all()
    
    @staticmethod
    def paginate_with_count(query, page=1, per_page=20):
        """Paginate query with separate count query for better performance.
        
        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Tuple of (items, total_count, total_pages)
        """
        # Get total count with a simplified query
        count_query = query.with_entities(func.count()).order_by(None)
        total_count = count_query.scalar()
        
        # Calculate pagination
        total_pages = (total_count + per_page - 1) // per_page
        offset = (page - 1) * per_page
        
        # Get paginated results
        items = query.offset(offset).limit(per_page).all()
        
        return items, total_count, total_pages