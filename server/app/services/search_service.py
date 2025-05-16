"""Search and filter service."""

from sqlalchemy import or_, and_, func
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.document import Document
from app.models.test import Test
from app.models.program import Program
from app.models.report import Report

class SearchService:
    """Service for global search and filtering."""
    
    @staticmethod
    def global_search(query_string, user, limit=10):
        """Perform global search across multiple models."""
        results = {
            'users': [],
            'beneficiaries': [],
            'documents': [],
            'tests': [],
            'programs': [],
            'reports': []
        }
        
        if not query_string:
            return results
            
        # Clean query string
        query_string = query_string.strip().lower()
        
        # Search users (if admin)
        if user.role in ['super_admin', 'tenant_admin']:
            user_query = User.query.filter(
                or_(
                    func.lower(User.first_name).contains(query_string),
                    func.lower(User.last_name).contains(query_string),
                    func.lower(User.email).contains(query_string)
                )
            )
            
            if user.role == 'tenant_admin':
                user_query = user_query.filter_by(tenant_id=user.tenant_id)
                
            results['users'] = [u.to_dict() for u in user_query.limit(limit).all()]
        
        # Search beneficiaries
        beneficiary_query = Beneficiary.query.filter(
            or_(
                func.lower(Beneficiary.first_name).contains(query_string),
                func.lower(Beneficiary.last_name).contains(query_string),
                func.lower(Beneficiary.email).contains(query_string)
            )
        )
        
        if user.role == 'trainer':
            beneficiary_query = beneficiary_query.filter_by(trainer_id=user.id)
        elif user.role == 'tenant_admin':
            beneficiary_query = beneficiary_query.filter_by(tenant_id=user.tenant_id)
            
        results['beneficiaries'] = [b.to_dict() for b in beneficiary_query.limit(limit).all()]
        
        # Search documents
        document_query = Document.query.filter(
            or_(
                func.lower(Document.name).contains(query_string),
                func.lower(Document.description).contains(query_string)
            )
        )
        
        # Apply document permissions
        if user.role not in ['super_admin', 'tenant_admin']:
            # Complex permission logic would go here
            pass
            
        results['documents'] = [d.to_dict() for d in document_query.limit(limit).all()]
        
        # Search tests
        test_query = Test.query.filter(
            or_(
                func.lower(Test.title).contains(query_string),
                func.lower(Test.description).contains(query_string)
            )
        )
        
        results['tests'] = [t.to_dict() for t in test_query.limit(limit).all()]
        
        # Search programs
        program_query = Program.query.filter(
            or_(
                func.lower(Program.name).contains(query_string),
                func.lower(Program.description).contains(query_string),
                func.lower(Program.code).contains(query_string)
            )
        )
        
        if user.role == 'tenant_admin':
            program_query = program_query.filter_by(tenant_id=user.tenant_id)
            
        results['programs'] = [p.to_dict() for p in program_query.limit(limit).all()]
        
        # Search reports
        report_query = Report.query.filter(
            or_(
                func.lower(Report.name).contains(query_string),
                func.lower(Report.description).contains(query_string)
            )
        )
        
        if user.role not in ['super_admin', 'tenant_admin']:
            report_query = report_query.filter_by(created_by_id=user.id)
        elif user.role == 'tenant_admin':
            report_query = report_query.filter_by(tenant_id=user.tenant_id)
            
        results['reports'] = [r.to_dict() for r in report_query.limit(limit).all()]
        
        return results
    
    @staticmethod
    def apply_filters(query, model, filters):
        """Apply filters to a query."""
        for field, value in filters.items():
            if value is None:
                continue
                
            # Handle different filter types
            if isinstance(value, dict):
                # Range filters
                if 'min' in value and value['min'] is not None:
                    query = query.filter(getattr(model, field) >= value['min'])
                if 'max' in value and value['max'] is not None:
                    query = query.filter(getattr(model, field) <= value['max'])
                    
            elif isinstance(value, list):
                # In filters
                if value:
                    query = query.filter(getattr(model, field).in_(value))
                    
            elif isinstance(value, str):
                # String contains filter
                if value:
                    query = query.filter(
                        func.lower(getattr(model, field)).contains(value.lower())
                    )
            else:
                # Exact match
                query = query.filter(getattr(model, field) == value)
                
        return query
    
    @staticmethod
    def apply_sorting(query, model, sort_by, sort_order='asc'):
        """Apply sorting to a query."""
        if not sort_by or not hasattr(model, sort_by):
            return query
            
        column = getattr(model, sort_by)
        
        if sort_order == 'desc':
            return query.order_by(column.desc())
        else:
            return query.order_by(column)
    
    @staticmethod
    def paginate_query(query, page=1, per_page=10):
        """Paginate a query."""
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }