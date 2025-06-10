"""Human-in-the-loop workflow management."""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field
import uuid


logger = logging.getLogger(__name__)


class ReviewStatus(str, Enum):
    """Status of human review requests."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ReviewPriority(str, Enum):
    """Priority levels for review requests."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ReviewRequest(BaseModel):
    """Human review request."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str
    task_type: str
    status: ReviewStatus = ReviewStatus.PENDING
    priority: ReviewPriority = ReviewPriority.MEDIUM
    input_data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    reviewer: Optional[str] = None
    reason: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReviewAssignment(BaseModel):
    """Assignment of review to a specific reviewer."""
    review_id: str
    reviewer_id: str
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReviewerProfile(BaseModel):
    """Profile of a human reviewer."""
    id: str
    name: str
    email: str
    specializations: List[str] = Field(default_factory=list)
    availability: bool = True
    max_concurrent_reviews: int = 5
    current_reviews: List[str] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)


class HumanInLoopManager:
    """Manages human-in-the-loop workflows."""
    
    def __init__(self, redis_client):
        """Initialize the human-in-the-loop manager."""
        self.redis_client = redis_client
        self.reviews_key = "hitl:reviews"
        self.reviewers_key = "hitl:reviewers"
        self.assignments_key = "hitl:assignments"
        self.notifications_key = "hitl:notifications"
        
        # Configuration
        self.default_timeout = timedelta(hours=24)
        self.reminder_intervals = [timedelta(hours=4), timedelta(hours=12)]
    
    def create_review(self,
                     task_name: str,
                     task_type: str,
                     input_data: Dict[str, Any],
                     priority: ReviewPriority = ReviewPriority.MEDIUM,
                     timeout: Optional[timedelta] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new review request."""
        # Create review request
        review = ReviewRequest(
            task_name=task_name,
            task_type=task_type,
            priority=priority,
            input_data=input_data,
            expires_at=datetime.utcnow() + (timeout or self.default_timeout),
            metadata=metadata or {}
        )
        
        # Store in Redis
        self.redis_client.hset(
            self.reviews_key,
            review.id,
            json.dumps(review.dict(), default=str)
        )
        
        # Add to priority queue
        self._add_to_queue(review)
        
        # Auto-assign if possible
        self._auto_assign_review(review.id)
        
        # Send notifications
        self._notify_new_review(review)
        
        logger.info(f"Created review request: {review.id} for task: {task_name}")
        return review.id
    
    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get a review request by ID."""
        review_data = self.redis_client.hget(self.reviews_key, review_id)
        if not review_data:
            return None
        
        return json.loads(review_data)
    
    def list_pending_reviews(self, 
                           reviewer_id: Optional[str] = None,
                           priority: Optional[ReviewPriority] = None,
                           task_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List pending review requests with optional filters."""
        all_reviews = self.redis_client.hgetall(self.reviews_key)
        pending_reviews = []
        
        for review_id, review_data in all_reviews.items():
            review = json.loads(review_data)
            
            # Check status
            if review["status"] != ReviewStatus.PENDING:
                continue
            
            # Check expiration
            expires_at = datetime.fromisoformat(review["expires_at"])
            if expires_at < datetime.utcnow():
                self._expire_review(review_id)
                continue
            
            # Apply filters
            if priority and review["priority"] != priority:
                continue
            
            if task_type and review["task_type"] != task_type:
                continue
            
            if reviewer_id:
                # Check if assigned to specific reviewer
                assignment = self._get_assignment(review_id)
                if not assignment or assignment["reviewer_id"] != reviewer_id:
                    continue
            
            pending_reviews.append(review)
        
        # Sort by priority and creation time
        priority_order = {
            ReviewPriority.URGENT: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.MEDIUM: 2,
            ReviewPriority.LOW: 3
        }
        
        pending_reviews.sort(
            key=lambda r: (
                priority_order.get(r["priority"], 999),
                r["created_at"]
            )
        )
        
        return pending_reviews
    
    def assign_review(self,
                     review_id: str,
                     reviewer_id: str,
                     deadline: Optional[datetime] = None) -> bool:
        """Assign a review to a specific reviewer."""
        # Get review
        review = self.get_review(review_id)
        if not review or review["status"] != ReviewStatus.PENDING:
            return False
        
        # Get reviewer
        reviewer = self._get_reviewer(reviewer_id)
        if not reviewer or not reviewer["availability"]:
            return False
        
        # Check capacity
        if len(reviewer["current_reviews"]) >= reviewer["max_concurrent_reviews"]:
            return False
        
        # Create assignment
        assignment = ReviewAssignment(
            review_id=review_id,
            reviewer_id=reviewer_id,
            deadline=deadline or datetime.utcnow() + timedelta(hours=24)
        )
        
        # Update review status
        review["status"] = ReviewStatus.IN_PROGRESS
        review["reviewer"] = reviewer_id
        review["assigned_at"] = datetime.utcnow().isoformat()
        
        # Update reviewer
        reviewer["current_reviews"].append(review_id)
        
        # Store updates
        self.redis_client.hset(
            self.reviews_key,
            review_id,
            json.dumps(review, default=str)
        )
        
        self.redis_client.hset(
            self.assignments_key,
            review_id,
            json.dumps(assignment.dict(), default=str)
        )
        
        self.redis_client.hset(
            self.reviewers_key,
            reviewer_id,
            json.dumps(reviewer, default=str)
        )
        
        # Send notification
        self._notify_assignment(review_id, reviewer_id)
        
        logger.info(f"Assigned review {review_id} to reviewer {reviewer_id}")
        return True
    
    def complete_review(self,
                       review_id: str,
                       reviewer_id: str,
                       result: Dict[str, Any],
                       feedback: Optional[str] = None) -> bool:
        """Complete a review with results."""
        # Get review
        review = self.get_review(review_id)
        if not review or review["status"] != ReviewStatus.IN_PROGRESS:
            return False
        
        # Verify reviewer
        if review.get("reviewer") != reviewer_id:
            return False
        
        # Update review
        review["status"] = ReviewStatus.COMPLETED
        review["result"] = result
        review["feedback"] = feedback
        review["completed_at"] = datetime.utcnow().isoformat()
        
        # Update reviewer
        reviewer = self._get_reviewer(reviewer_id)
        if reviewer and review_id in reviewer["current_reviews"]:
            reviewer["current_reviews"].remove(review_id)
            
            # Update performance metrics
            completion_time = (
                datetime.fromisoformat(review["completed_at"]) - 
                datetime.fromisoformat(review["assigned_at"])
            ).total_seconds() / 3600  # hours
            
            if "avg_completion_time" not in reviewer["performance_metrics"]:
                reviewer["performance_metrics"]["avg_completion_time"] = completion_time
            else:
                # Running average
                current_avg = reviewer["performance_metrics"]["avg_completion_time"]
                reviewer["performance_metrics"]["avg_completion_time"] = (current_avg + completion_time) / 2
            
            reviewer["performance_metrics"]["total_completed"] = (
                reviewer["performance_metrics"].get("total_completed", 0) + 1
            )
            
            # Store reviewer updates
            self.redis_client.hset(
                self.reviewers_key,
                reviewer_id,
                json.dumps(reviewer, default=str)
            )
        
        # Store review update
        self.redis_client.hset(
            self.reviews_key,
            review_id,
            json.dumps(review, default=str)
        )
        
        # Clean up assignment
        self.redis_client.hdel(self.assignments_key, review_id)
        
        # Send notification
        self._notify_completion(review_id)
        
        logger.info(f"Completed review {review_id} by reviewer {reviewer_id}")
        return True
    
    def reject_review(self,
                     review_id: str,
                     reviewer_id: str,
                     reason: str) -> bool:
        """Reject a review request."""
        # Get review
        review = self.get_review(review_id)
        if not review or review["status"] != ReviewStatus.IN_PROGRESS:
            return False
        
        # Verify reviewer
        if review.get("reviewer") != reviewer_id:
            return False
        
        # Update review
        review["status"] = ReviewStatus.REJECTED
        review["reason"] = reason
        review["completed_at"] = datetime.utcnow().isoformat()
        
        # Update reviewer
        reviewer = self._get_reviewer(reviewer_id)
        if reviewer and review_id in reviewer["current_reviews"]:
            reviewer["current_reviews"].remove(review_id)
            self.redis_client.hset(
                self.reviewers_key,
                reviewer_id,
                json.dumps(reviewer, default=str)
            )
        
        # Store review update
        self.redis_client.hset(
            self.reviews_key,
            review_id,
            json.dumps(review, default=str)
        )
        
        # Clean up assignment
        self.redis_client.hdel(self.assignments_key, review_id)
        
        # Send notification
        self._notify_rejection(review_id, reason)
        
        logger.info(f"Rejected review {review_id} by reviewer {reviewer_id}: {reason}")
        return True
    
    def cancel_review(self, review_id: str) -> bool:
        """Cancel a review request."""
        review = self.get_review(review_id)
        if not review:
            return False
        
        # Update review status
        review["status"] = ReviewStatus.CANCELLED
        review["completed_at"] = datetime.utcnow().isoformat()
        
        # Clean up reviewer assignment
        if review.get("reviewer"):
            reviewer = self._get_reviewer(review["reviewer"])
            if reviewer and review_id in reviewer["current_reviews"]:
                reviewer["current_reviews"].remove(review_id)
                self.redis_client.hset(
                    self.reviewers_key,
                    review["reviewer"],
                    json.dumps(reviewer, default=str)
                )
        
        # Store update
        self.redis_client.hset(
            self.reviews_key,
            review_id,
            json.dumps(review, default=str)
        )
        
        # Clean up assignment
        self.redis_client.hdel(self.assignments_key, review_id)
        
        logger.info(f"Cancelled review {review_id}")
        return True
    
    def register_reviewer(self, profile: ReviewerProfile) -> str:
        """Register a new reviewer."""
        self.redis_client.hset(
            self.reviewers_key,
            profile.id,
            json.dumps(profile.dict(), default=str)
        )
        
        logger.info(f"Registered reviewer: {profile.id} ({profile.name})")
        return profile.id
    
    def update_reviewer_availability(self, reviewer_id: str, available: bool) -> bool:
        """Update reviewer availability."""
        reviewer = self._get_reviewer(reviewer_id)
        if not reviewer:
            return False
        
        reviewer["availability"] = available
        self.redis_client.hset(
            self.reviewers_key,
            reviewer_id,
            json.dumps(reviewer, default=str)
        )
        
        return True
    
    def get_reviewer_workload(self, reviewer_id: str) -> Dict[str, Any]:
        """Get current workload for a reviewer."""
        reviewer = self._get_reviewer(reviewer_id)
        if not reviewer:
            return {}
        
        current_reviews = []
        for review_id in reviewer["current_reviews"]:
            review = self.get_review(review_id)
            if review:
                current_reviews.append(review)
        
        return {
            "reviewer_id": reviewer_id,
            "name": reviewer["name"],
            "availability": reviewer["availability"],
            "current_reviews_count": len(current_reviews),
            "max_concurrent_reviews": reviewer["max_concurrent_reviews"],
            "capacity_utilization": len(current_reviews) / reviewer["max_concurrent_reviews"],
            "current_reviews": current_reviews,
            "performance_metrics": reviewer["performance_metrics"]
        }
    
    def _get_reviewer(self, reviewer_id: str) -> Optional[Dict[str, Any]]:
        """Get reviewer by ID."""
        reviewer_data = self.redis_client.hget(self.reviewers_key, reviewer_id)
        if not reviewer_data:
            return None
        return json.loads(reviewer_data)
    
    def _get_assignment(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get assignment for a review."""
        assignment_data = self.redis_client.hget(self.assignments_key, review_id)
        if not assignment_data:
            return None
        return json.loads(assignment_data)
    
    def _add_to_queue(self, review: ReviewRequest):
        """Add review to priority queue."""
        priority_score = {
            ReviewPriority.URGENT: 1000,
            ReviewPriority.HIGH: 100,
            ReviewPriority.MEDIUM: 10,
            ReviewPriority.LOW: 1
        }.get(review.priority, 1)
        
        # Use timestamp as secondary sort criteria
        timestamp_score = int(review.created_at.timestamp())
        final_score = priority_score * 1000000 + timestamp_score
        
        self.redis_client.zadd(
            "hitl:queue",
            {review.id: final_score}
        )
    
    def _auto_assign_review(self, review_id: str) -> bool:
        """Automatically assign review to best available reviewer."""
        review = self.get_review(review_id)
        if not review:
            return False
        
        # Get all available reviewers
        all_reviewers = self.redis_client.hgetall(self.reviewers_key)
        available_reviewers = []
        
        for reviewer_id, reviewer_data in all_reviewers.items():
            reviewer = json.loads(reviewer_data)
            
            # Check availability and capacity
            if (reviewer["availability"] and 
                len(reviewer["current_reviews"]) < reviewer["max_concurrent_reviews"]):
                
                # Check specialization match
                if (not reviewer["specializations"] or 
                    review["task_type"] in reviewer["specializations"]):
                    available_reviewers.append((reviewer_id, reviewer))
        
        if not available_reviewers:
            return False
        
        # Sort by workload and performance
        def reviewer_score(reviewer_tuple):
            reviewer_id, reviewer = reviewer_tuple
            workload_score = len(reviewer["current_reviews"]) / reviewer["max_concurrent_reviews"]
            performance_score = reviewer["performance_metrics"].get("avg_completion_time", 24) / 24
            return workload_score + performance_score
        
        available_reviewers.sort(key=reviewer_score)
        best_reviewer_id = available_reviewers[0][0]
        
        return self.assign_review(review_id, best_reviewer_id)
    
    def _expire_review(self, review_id: str):
        """Mark a review as expired."""
        review = self.get_review(review_id)
        if review:
            review["status"] = ReviewStatus.EXPIRED
            self.redis_client.hset(
                self.reviews_key,
                review_id,
                json.dumps(review, default=str)
            )
    
    def _notify_new_review(self, review: ReviewRequest):
        """Send notification for new review."""
        notification = {
            "type": "new_review",
            "review_id": review.id,
            "task_name": review.task_name,
            "priority": review.priority,
            "created_at": review.created_at.isoformat()
        }
        
        self.redis_client.lpush(
            self.notifications_key,
            json.dumps(notification, default=str)
        )
    
    def _notify_assignment(self, review_id: str, reviewer_id: str):
        """Send notification for review assignment."""
        notification = {
            "type": "review_assigned",
            "review_id": review_id,
            "reviewer_id": reviewer_id,
            "assigned_at": datetime.utcnow().isoformat()
        }
        
        self.redis_client.lpush(
            self.notifications_key,
            json.dumps(notification, default=str)
        )
    
    def _notify_completion(self, review_id: str):
        """Send notification for review completion."""
        notification = {
            "type": "review_completed",
            "review_id": review_id,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        self.redis_client.lpush(
            self.notifications_key,
            json.dumps(notification, default=str)
        )
    
    def _notify_rejection(self, review_id: str, reason: str):
        """Send notification for review rejection."""
        notification = {
            "type": "review_rejected",
            "review_id": review_id,
            "reason": reason,
            "rejected_at": datetime.utcnow().isoformat()
        }
        
        self.redis_client.lpush(
            self.notifications_key,
            json.dumps(notification, default=str)
        )