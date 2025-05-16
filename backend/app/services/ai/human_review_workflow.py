"""
Human review workflow for AI-generated content
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.user import User
from app.models.notification import Notification
from app.models.base import Base
from app.core.database import engine
from app.core.cache import cache_service
from app.services.notification_service import notification_service
from app.services.monitoring.error_tracking import error_tracker
from app.services.ai.report_synthesis import report_synthesis_service
from app.services.ai.content_recommendations import content_recommendation_service
import logging

logger = logging.getLogger(__name__)

# Create review workflow models
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

class ReviewStatus(enum.Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"
    REVISED = "revised"

class ReviewType(enum.Enum):
    REPORT = "report"
    RECOMMENDATION = "recommendation"
    ASSESSMENT_ANALYSIS = "assessment_analysis"
    CONTENT_SUGGESTION = "content_suggestion"

class ReviewWorkflow(Base):
    __tablename__ = 'review_workflows'
    
    id = Column(Integer, primary_key=True)
    review_type = Column(Enum(ReviewType), nullable=False)
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    
    # AI-generated content
    ai_content = Column(JSON, nullable=False)
    ai_metadata = Column(JSON)
    confidence_score = Column(Integer)  # 0-100
    
    # Review data
    reviewer_id = Column(Integer, ForeignKey('users.id'))
    review_started_at = Column(DateTime)
    review_completed_at = Column(DateTime)
    review_notes = Column(Text)
    modifications = Column(JSON)
    
    # Final content
    final_content = Column(JSON)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    beneficiary_id = Column(Integer, ForeignKey('beneficiaries.id'))
    created_by = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    creator = relationship("User", foreign_keys=[created_by])

# Create table if it doesn't exist
Base.metadata.create_all(bind=engine)

class HumanReviewWorkflowService:
    """Service for managing human review of AI-generated content"""
    
    def create_review_workflow(self, review_type: ReviewType,
                             ai_content: Dict[str, Any],
                             created_by: int,
                             beneficiary_id: Optional[int] = None,
                             confidence_score: Optional[int] = None,
                             metadata: Optional[Dict] = None,
                             db: Session = None) -> ReviewWorkflow:
        """Create a new review workflow for AI-generated content"""
        try:
            workflow = ReviewWorkflow(
                review_type=review_type,
                ai_content=ai_content,
                ai_metadata=metadata or {},
                confidence_score=confidence_score,
                created_by=created_by,
                beneficiary_id=beneficiary_id,
                status=ReviewStatus.PENDING
            )
            
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
            
            # Auto-approve if confidence is very high
            if confidence_score and confidence_score >= 95:
                self.auto_approve_workflow(workflow.id, db)
            else:
                # Notify reviewers
                self._notify_reviewers(workflow, db)
            
            return workflow
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error creating review workflow: {str(e)}")
            db.rollback()
            raise
            
    def start_review(self, workflow_id: int, reviewer_id: int,
                    db: Session) -> ReviewWorkflow:
        """Start reviewing a workflow"""
        try:
            workflow = db.query(ReviewWorkflow).filter_by(id=workflow_id).first()
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
                
            if workflow.status not in [ReviewStatus.PENDING, ReviewStatus.REVISED]:
                raise ValueError(f"Workflow {workflow_id} is not available for review")
                
            workflow.status = ReviewStatus.IN_REVIEW
            workflow.reviewer_id = reviewer_id
            workflow.review_started_at = datetime.utcnow()
            
            db.commit()
            db.refresh(workflow)
            
            return workflow
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error starting review: {str(e)}")
            db.rollback()
            raise
            
    def complete_review(self, workflow_id: int, reviewer_id: int,
                       action: str, review_notes: Optional[str] = None,
                       modifications: Optional[Dict] = None,
                       db: Session = None) -> ReviewWorkflow:
        """Complete the review process"""
        try:
            workflow = db.query(ReviewWorkflow).filter_by(
                id=workflow_id,
                reviewer_id=reviewer_id
            ).first()
            
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found or not assigned to reviewer")
                
            if workflow.status != ReviewStatus.IN_REVIEW:
                raise ValueError(f"Workflow {workflow_id} is not in review")
                
            workflow.review_completed_at = datetime.utcnow()
            workflow.review_notes = review_notes
            
            if action == 'approve':
                workflow.status = ReviewStatus.APPROVED
                workflow.final_content = modifications or workflow.ai_content
                workflow.modifications = modifications
                
                # Notify creator of approval
                self._notify_approval(workflow, db)
                
            elif action == 'reject':
                workflow.status = ReviewStatus.REJECTED
                
                # Notify creator of rejection
                self._notify_rejection(workflow, db)
                
            elif action == 'request_revision':
                workflow.status = ReviewStatus.REVISION_REQUESTED
                workflow.modifications = modifications
                
                # Notify for revision
                self._notify_revision_request(workflow, db)
                
            else:
                raise ValueError(f"Invalid action: {action}")
                
            db.commit()
            db.refresh(workflow)
            
            return workflow
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error completing review: {str(e)}")
            db.rollback()
            raise
            
    def revise_content(self, workflow_id: int, revised_content: Dict[str, Any],
                      db: Session) -> ReviewWorkflow:
        """Submit revised content for re-review"""
        try:
            workflow = db.query(ReviewWorkflow).filter_by(id=workflow_id).first()
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
                
            if workflow.status != ReviewStatus.REVISION_REQUESTED:
                raise ValueError(f"Workflow {workflow_id} is not pending revision")
                
            workflow.ai_content = revised_content
            workflow.status = ReviewStatus.REVISED
            workflow.review_notes = None
            workflow.modifications = None
            
            db.commit()
            db.refresh(workflow)
            
            # Notify reviewer of revision
            self._notify_revision_submitted(workflow, db)
            
            return workflow
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error revising content: {str(e)}")
            db.rollback()
            raise
            
    def auto_approve_workflow(self, workflow_id: int, db: Session) -> ReviewWorkflow:
        """Auto-approve high-confidence workflows"""
        try:
            workflow = db.query(ReviewWorkflow).filter_by(id=workflow_id).first()
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")
                
            workflow.status = ReviewStatus.APPROVED
            workflow.final_content = workflow.ai_content
            workflow.review_notes = "Auto-approved due to high confidence score"
            workflow.review_completed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(workflow)
            
            # Notify creator of auto-approval
            notification_service.create_notification(
                user_id=workflow.created_by,
                notification_type='review_complete',
                title='Content Auto-Approved',
                message=f'Your {workflow.review_type.value} has been auto-approved',
                data={'workflow_id': workflow.id},
                db=db
            )
            
            return workflow
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error auto-approving workflow: {str(e)}")
            db.rollback()
            raise
            
    def get_pending_reviews(self, reviewer_id: Optional[int] = None,
                          review_type: Optional[ReviewType] = None,
                          db: Session = None) -> List[ReviewWorkflow]:
        """Get pending review workflows"""
        try:
            query = db.query(ReviewWorkflow).filter(
                ReviewWorkflow.status.in_([
                    ReviewStatus.PENDING,
                    ReviewStatus.REVISED
                ])
            )
            
            if reviewer_id:
                query = query.filter(
                    or_(
                        ReviewWorkflow.reviewer_id == reviewer_id,
                        ReviewWorkflow.reviewer_id.is_(None)
                    )
                )
                
            if review_type:
                query = query.filter(ReviewWorkflow.review_type == review_type)
                
            return query.order_by(ReviewWorkflow.created_at.desc()).all()
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error getting pending reviews: {str(e)}")
            return []
            
    def get_review_statistics(self, time_period: str = 'last_month',
                            db: Session = None) -> Dict[str, Any]:
        """Get review workflow statistics"""
        try:
            # Calculate date filter
            date_filter = self._get_date_filter(time_period)
            
            query = db.query(ReviewWorkflow)
            if date_filter:
                query = query.filter(ReviewWorkflow.created_at >= date_filter)
                
            workflows = query.all()
            
            total_count = len(workflows)
            status_counts = {}
            type_counts = {}
            avg_review_time = 0
            auto_approved = 0
            
            review_times = []
            
            for workflow in workflows:
                # Count by status
                status = workflow.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count by type
                review_type = workflow.review_type.value
                type_counts[review_type] = type_counts.get(review_type, 0) + 1
                
                # Calculate review times
                if workflow.review_started_at and workflow.review_completed_at:
                    review_time = (workflow.review_completed_at - workflow.review_started_at).total_seconds() / 60
                    review_times.append(review_time)
                    
                # Count auto-approvals
                if (workflow.status == ReviewStatus.APPROVED and 
                    workflow.confidence_score and 
                    workflow.confidence_score >= 95):
                    auto_approved += 1
                    
            if review_times:
                avg_review_time = sum(review_times) / len(review_times)
                
            approval_rate = (status_counts.get('approved', 0) / total_count * 100) if total_count > 0 else 0
            
            return {
                'total_workflows': total_count,
                'status_breakdown': status_counts,
                'type_breakdown': type_counts,
                'approval_rate': approval_rate,
                'average_review_time_minutes': avg_review_time,
                'auto_approved_count': auto_approved,
                'pending_reviews': status_counts.get('pending', 0) + status_counts.get('revised', 0),
                'time_period': time_period,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error getting review statistics: {str(e)}")
            return {}
            
    def _notify_reviewers(self, workflow: ReviewWorkflow, db: Session):
        """Notify available reviewers of new content to review"""
        # Get trainers and admins as potential reviewers
        reviewers = db.query(User).filter(
            User.role.in_(['trainer', 'admin', 'super_admin']),
            User.is_active == True
        ).all()
        
        for reviewer in reviewers:
            notification_service.create_notification(
                user_id=reviewer.id,
                notification_type='review_request',
                title='New Content for Review',
                message=f'New {workflow.review_type.value} requires review',
                data={
                    'workflow_id': workflow.id,
                    'review_type': workflow.review_type.value,
                    'confidence_score': workflow.confidence_score
                },
                db=db
            )
            
    def _notify_approval(self, workflow: ReviewWorkflow, db: Session):
        """Notify creator of content approval"""
        notification_service.create_notification(
            user_id=workflow.created_by,
            notification_type='review_complete',
            title='Content Approved',
            message=f'Your {workflow.review_type.value} has been approved',
            data={
                'workflow_id': workflow.id,
                'reviewer_id': workflow.reviewer_id
            },
            db=db
        )
        
    def _notify_rejection(self, workflow: ReviewWorkflow, db: Session):
        """Notify creator of content rejection"""
        notification_service.create_notification(
            user_id=workflow.created_by,
            notification_type='review_complete',
            title='Content Rejected',
            message=f'Your {workflow.review_type.value} has been rejected',
            data={
                'workflow_id': workflow.id,
                'reviewer_id': workflow.reviewer_id,
                'review_notes': workflow.review_notes
            },
            db=db
        )
        
    def _notify_revision_request(self, workflow: ReviewWorkflow, db: Session):
        """Notify creator of revision request"""
        notification_service.create_notification(
            user_id=workflow.created_by,
            notification_type='revision_request',
            title='Revision Requested',
            message=f'Your {workflow.review_type.value} requires revision',
            data={
                'workflow_id': workflow.id,
                'reviewer_id': workflow.reviewer_id,
                'review_notes': workflow.review_notes,
                'modifications': workflow.modifications
            },
            db=db
        )
        
    def _notify_revision_submitted(self, workflow: ReviewWorkflow, db: Session):
        """Notify reviewer of revision submission"""
        if workflow.reviewer_id:
            notification_service.create_notification(
                user_id=workflow.reviewer_id,
                notification_type='revision_submitted',
                title='Revision Submitted',
                message=f'Revised {workflow.review_type.value} ready for review',
                data={
                    'workflow_id': workflow.id,
                    'creator_id': workflow.created_by
                },
                db=db
            )
            
    def _get_date_filter(self, time_period: str) -> Optional[datetime]:
        """Get date filter based on time period"""
        if time_period == 'all_time':
            return None
            
        now = datetime.utcnow()
        
        if time_period == 'last_week':
            return now - timedelta(days=7)
        elif time_period == 'last_month':
            return now - timedelta(days=30)
        elif time_period == 'last_quarter':
            return now - timedelta(days=90)
        elif time_period == 'last_year':
            return now - timedelta(days=365)
        else:
            return None
            
    def integrate_with_ai_services(self, service_type: str,
                                 content_data: Dict[str, Any],
                                 created_by: int,
                                 beneficiary_id: Optional[int] = None,
                                 db: Session = None) -> ReviewWorkflow:
        """Integration point for AI services to submit content for review"""
        try:
            # Map service types to review types
            review_type_map = {
                'report': ReviewType.REPORT,
                'recommendation': ReviewType.RECOMMENDATION,
                'assessment_analysis': ReviewType.ASSESSMENT_ANALYSIS,
                'content_suggestion': ReviewType.CONTENT_SUGGESTION
            }
            
            review_type = review_type_map.get(service_type)
            if not review_type:
                raise ValueError(f"Unknown service type: {service_type}")
                
            # Extract confidence score if available
            confidence_score = content_data.get('confidence_score', 75)
            
            # Create the review workflow
            workflow = self.create_review_workflow(
                review_type=review_type,
                ai_content=content_data,
                created_by=created_by,
                beneficiary_id=beneficiary_id,
                confidence_score=confidence_score,
                metadata={
                    'service_type': service_type,
                    'generated_at': datetime.utcnow().isoformat()
                },
                db=db
            )
            
            return workflow
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error integrating with AI services: {str(e)}")
            raise

# Initialize the service
human_review_service = HumanReviewWorkflowService()