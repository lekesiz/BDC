"""Optimized beneficiary service with relationship loading strategies."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Query
from app.models.beneficiary import Beneficiary
from app.models.user import User
from app.models.optimized_relationships import OptimizedRelationships, optimize_query
from app.extensions import db
import logging

logger = logging.getLogger(__name__)


class OptimizedBeneficiaryService:
    """Service for optimized beneficiary queries."""
    
    @staticmethod
    def get_beneficiary_list(
        page: int = 1,
        per_page: int = 20,
        trainer_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of beneficiaries with optimized loading."""
        # Start with base query
        query = Beneficiary.query
        
        # Apply optimized relationship loading for list view
        query = optimize_query(query, OptimizedRelationships.BENEFICIARY_FOR_LIST)
        
        # Apply filters
        if trainer_id:
            query = query.filter_by(trainer_id=trainer_id)
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        if status:
            query = query.filter_by(status=status)
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.join(Beneficiary.user).filter(
                db.or_(
                    Beneficiary.user.has(User.first_name.ilike(search_term)),
                    Beneficiary.user.has(User.last_name.ilike(search_term)),
                    Beneficiary.user.has(User.email.ilike(search_term)),
                    Beneficiary.phone.ilike(search_term)
                )
            )
        
        # Order by creation date
        query = query.order_by(Beneficiary.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Convert to dict
        beneficiaries_data = []
        for b in pagination.items:
            data = {
                'id': b.id,
                'user': {
                    'id': b.user.id,
                    'first_name': b.user.first_name,
                    'last_name': b.user.last_name,
                    'email': b.user.email
                } if b.user else None,
                'trainer': {
                    'id': b.trainer.id,
                    'first_name': b.trainer.first_name,
                    'last_name': b.trainer.last_name
                } if b.trainer else None,
                'status': b.status,
                'is_active': b.is_active,
                'phone': b.phone,
                'created_at': b.created_at.isoformat() if b.created_at else None
            }
            beneficiaries_data.append(data)
        
        return {
            'beneficiaries': beneficiaries_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_prev': pagination.has_prev,
                'has_next': pagination.has_next
            }
        }
    
    @staticmethod
    def get_beneficiary_details(beneficiary_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed beneficiary information with optimized loading."""
        # Use optimized query for details view
        beneficiary = Beneficiary.query.options(
            *OptimizedRelationships.BENEFICIARY_WITH_DETAILS
        ).filter_by(id=beneficiary_id).first()
        
        if not beneficiary:
            return None
        
        # Build detailed response
        data = {
            'id': beneficiary.id,
            'user': {
                'id': beneficiary.user.id,
                'first_name': beneficiary.user.first_name,
                'last_name': beneficiary.user.last_name,
                'email': beneficiary.user.email,
                'phone': beneficiary.user.phone if hasattr(beneficiary.user, 'phone') else None,
                'is_active': beneficiary.user.is_active
            } if beneficiary.user else None,
            'trainer': {
                'id': beneficiary.trainer.id,
                'first_name': beneficiary.trainer.first_name,
                'last_name': beneficiary.trainer.last_name,
                'email': beneficiary.trainer.email
            } if beneficiary.trainer else None,
            'tenant': {
                'id': beneficiary.tenant.id,
                'name': beneficiary.tenant.name
            } if beneficiary.tenant else None,
            'personal_info': {
                'gender': beneficiary.gender,
                'birth_date': beneficiary.birth_date.isoformat() if beneficiary.birth_date else None,
                'phone': beneficiary.phone,
                'address': beneficiary.address,
                'city': beneficiary.city,
                'postal_code': beneficiary.postal_code,
                'country': beneficiary.country,
                'nationality': beneficiary.nationality,
                'native_language': beneficiary.native_language
            },
            'professional_info': {
                'profession': beneficiary.profession,
                'company': beneficiary.company,
                'company_size': beneficiary.company_size,
                'years_of_experience': beneficiary.years_of_experience,
                'education_level': beneficiary.education_level
            },
            'additional_info': {
                'category': beneficiary.category,
                'bio': beneficiary.bio,
                'goals': beneficiary.goals,
                'notes': beneficiary.notes,
                'referral_source': beneficiary.referral_source,
                'custom_fields': beneficiary.custom_fields
            },
            'emergency_contact': {
                'name': beneficiary.emergency_contact_name,
                'relationship': beneficiary.emergency_contact_relationship,
                'phone': beneficiary.emergency_contact_phone,
                'email': beneficiary.emergency_contact_email,
                'address': beneficiary.emergency_contact_address
            },
            'status_info': {
                'status': beneficiary.status,
                'is_active': beneficiary.is_active,
                'created_at': beneficiary.created_at.isoformat() if beneficiary.created_at else None,
                'updated_at': beneficiary.updated_at.isoformat() if beneficiary.updated_at else None
            },
            'statistics': {
                'evaluation_count': beneficiary.evaluation_count,
                'completed_evaluation_count': beneficiary.completed_evaluation_count,
                'session_count': beneficiary.session_count,
                'document_count': len(beneficiary.documents.all()) if beneficiary.documents else 0
            }
        }
        
        # Add recent documents if loaded
        if beneficiary.documents:
            data['recent_documents'] = [
                {
                    'id': doc.id,
                    'title': doc.title if hasattr(doc, 'title') else 'Document',
                    'document_type': doc.document_type if hasattr(doc, 'document_type') else None,
                    'created_at': doc.created_at.isoformat() if doc.created_at else None
                }
                for doc in list(beneficiary.documents)[:5]  # Last 5 documents
            ]
        
        return data
    
    @staticmethod
    def get_beneficiary_progress(beneficiary_id: int) -> Optional[Dict[str, Any]]:
        """Get beneficiary with progress information using optimized loading."""
        # Use optimized query for progress view
        beneficiary = Beneficiary.query.options(
            *OptimizedRelationships.BENEFICIARY_WITH_PROGRESS
        ).filter_by(id=beneficiary_id).first()
        
        if not beneficiary:
            return None
        
        # Build progress response
        data = {
            'id': beneficiary.id,
            'name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}" if beneficiary.user else 'Unknown',
            'status': beneficiary.status,
            'appointments': [],
            'evaluations': [],
            'ai_analytics': None
        }
        
        # Add appointments if loaded
        if beneficiary.appointments:
            data['appointments'] = [
                {
                    'id': apt.id,
                    'title': apt.title if hasattr(apt, 'title') else 'Appointment',
                    'start_time': apt.start_time.isoformat() if apt.start_time else None,
                    'status': apt.status
                }
                for apt in beneficiary.appointments
            ]
        
        # Add evaluations if loaded
        if beneficiary.evaluations:
            data['evaluations'] = [
                {
                    'id': eval.id,
                    'type': eval.type if hasattr(eval, 'type') else 'evaluation',
                    'status': eval.status if hasattr(eval, 'status') else None,
                    'created_at': eval.created_at.isoformat() if eval.created_at else None
                }
                for eval in beneficiary.evaluations
            ]
        
        # Add AI analytics if available
        if hasattr(beneficiary, 'ai_analytics') and beneficiary.ai_analytics:
            analytics = beneficiary.ai_analytics[0] if isinstance(beneficiary.ai_analytics, list) else beneficiary.ai_analytics
            data['ai_analytics'] = {
                'strengths': analytics.strengths if hasattr(analytics, 'strengths') else [],
                'areas_for_improvement': analytics.areas_for_improvement if hasattr(analytics, 'areas_for_improvement') else [],
                'recommended_next_steps': analytics.recommended_next_steps if hasattr(analytics, 'recommended_next_steps') else []
            }
        
        return data
    
    @staticmethod
    def get_beneficiaries_for_trainer(trainer_id: int) -> List[Dict[str, Any]]:
        """Get all beneficiaries for a specific trainer with optimized loading."""
        from app.models.optimized_relationships import get_beneficiaries_for_trainer
        
        beneficiaries = get_beneficiaries_for_trainer(trainer_id, db.session)
        
        # Convert to dict
        return [
            {
                'id': b.id,
                'user': {
                    'id': b.user.id,
                    'first_name': b.user.first_name,
                    'last_name': b.user.last_name,
                    'email': b.user.email
                } if b.user else None,
                'status': b.status,
                'is_active': b.is_active,
                'phone': b.phone,
                'last_activity': b.updated_at.isoformat() if b.updated_at else None,
                'progress': getattr(b, 'progress', 0),
                'evaluation_count': b.evaluation_count,
                'next_appointment': None  # Would need to query separately if needed
            }
            for b in beneficiaries
        ]
    
    @staticmethod
    def batch_load_beneficiaries(beneficiary_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Batch load multiple beneficiaries with optimized loading."""
        from app.models.model_optimizations import QueryOptimizer
        
        # Use batch loading utility
        beneficiaries = QueryOptimizer.batch_load(
            Beneficiary,
            beneficiary_ids,
            relationships=['user', 'trainer', 'tenant']
        )
        
        # Convert to dict indexed by ID
        result = {}
        for b in beneficiaries:
            result[b.id] = {
                'id': b.id,
                'name': f"{b.user.first_name} {b.user.last_name}" if b.user else 'Unknown',
                'email': b.user.email if b.user else None,
                'trainer_name': f"{b.trainer.first_name} {b.trainer.last_name}" if b.trainer else None,
                'tenant_name': b.tenant.name if b.tenant else None,
                'status': b.status,
                'is_active': b.is_active
            }
        
        return result