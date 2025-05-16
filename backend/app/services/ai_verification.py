from datetime import datetime
from flask import current_app
from sqlalchemy import and_
from app.models import User, AIAnalysis, HumanVerification
from app.extensions import db
from app.utils.notifications import send_notification

class AIVerificationService:
    """Service for managing human verification of AI-generated content"""
    
    VERIFICATION_LEVELS = {
        'LOW': 0.7,      # AI confidence above 70% - auto-approve
        'MEDIUM': 0.5,   # AI confidence 50-70% - optional review
        'HIGH': 0.0      # AI confidence below 50% - mandatory review
    }
    
    @staticmethod
    def create_verification_request(
        content_type,
        content_id,
        ai_output,
        confidence_score,
        reviewer_id=None,
        priority='normal'
    ):
        """Create a human verification request for AI-generated content"""
        
        # Determine verification level
        verification_level = AIVerificationService._determine_verification_level(confidence_score)
        
        # Auto-approve if confidence is high enough
        if verification_level == 'LOW':
            return AIVerificationService._auto_approve(content_type, content_id, ai_output)
        
        # Create verification request
        verification = HumanVerification(
            content_type=content_type,
            content_id=content_id,
            ai_output=ai_output,
            confidence_score=confidence_score,
            verification_level=verification_level,
            priority=priority,
            status='pending',
            reviewer_id=reviewer_id
        )
        
        db.session.add(verification)
        db.session.commit()
        
        # Notify reviewers
        AIVerificationService._notify_reviewers(verification)
        
        return verification
    
    @staticmethod
    def verify_content(verification_id, reviewer_id, decision, feedback=None, modifications=None):
        """Process human verification decision"""
        
        verification = HumanVerification.query.get(verification_id)
        if not verification:
            return None, "Verification request not found"
        
        if verification.status != 'pending':
            return None, "Verification already processed"
        
        # Update verification record
        verification.reviewer_id = reviewer_id
        verification.status = decision  # 'approved', 'rejected', 'modified'
        verification.review_feedback = feedback
        verification.modified_output = modifications or verification.ai_output
        verification.reviewed_at = datetime.utcnow()
        
        # Update AI analysis record
        ai_analysis = AIAnalysis.query.filter_by(
            content_type=verification.content_type,
            content_id=verification.content_id
        ).first()
        
        if ai_analysis:
            ai_analysis.human_verified = True
            ai_analysis.verification_status = decision
            if modifications:
                ai_analysis.final_output = modifications
            
        db.session.commit()
        
        # Notify content owner
        AIVerificationService._notify_content_owner(verification)
        
        return verification, None
    
    @staticmethod
    def get_pending_verifications(reviewer_id=None, content_type=None):
        """Get pending verification requests"""
        
        query = HumanVerification.query.filter_by(status='pending')
        
        if reviewer_id:
            query = query.filter(
                or_(
                    HumanVerification.reviewer_id == reviewer_id,
                    HumanVerification.reviewer_id.is_(None)
                )
            )
        
        if content_type:
            query = query.filter_by(content_type=content_type)
        
        return query.order_by(
            HumanVerification.priority.desc(),
            HumanVerification.created_at
        ).all()
    
    @staticmethod
    def get_verification_stats(start_date=None, end_date=None):
        """Get verification statistics"""
        
        query = HumanVerification.query
        
        if start_date:
            query = query.filter(HumanVerification.created_at >= start_date)
        if end_date:
            query = query.filter(HumanVerification.created_at <= end_date)
        
        stats = {
            'total': query.count(),
            'pending': query.filter_by(status='pending').count(),
            'approved': query.filter_by(status='approved').count(),
            'rejected': query.filter_by(status='rejected').count(),
            'modified': query.filter_by(status='modified').count(),
            'avg_confidence': db.session.query(
                func.avg(HumanVerification.confidence_score)
            ).scalar() or 0,
            'avg_review_time': AIVerificationService._calculate_avg_review_time(query)
        }
        
        return stats
    
    @staticmethod
    def _determine_verification_level(confidence_score):
        """Determine verification level based on confidence score"""
        
        if confidence_score >= AIVerificationService.VERIFICATION_LEVELS['LOW']:
            return 'LOW'
        elif confidence_score >= AIVerificationService.VERIFICATION_LEVELS['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    @staticmethod
    def _auto_approve(content_type, content_id, ai_output):
        """Auto-approve high-confidence AI output"""
        
        verification = HumanVerification(
            content_type=content_type,
            content_id=content_id,
            ai_output=ai_output,
            confidence_score=1.0,
            verification_level='LOW',
            status='approved',
            auto_approved=True,
            reviewed_at=datetime.utcnow()
        )
        
        db.session.add(verification)
        db.session.commit()
        
        return verification
    
    @staticmethod
    def _notify_reviewers(verification):
        """Notify qualified reviewers about pending verification"""
        
        # Get qualified reviewers based on content type
        reviewers = User.query.filter_by(
            role='trainer',
            is_active=True
        ).all()
        
        for reviewer in reviewers:
            send_notification(
                user_id=reviewer.id,
                type='verification_request',
                title='AI İçerik Doğrulama Talebi',
                message=f'{verification.content_type} için doğrulama bekliyor',
                data={
                    'verification_id': verification.id,
                    'priority': verification.priority
                }
            )
    
    @staticmethod
    def _notify_content_owner(verification):
        """Notify content owner about verification result"""
        
        # Get content owner based on content type and ID
        # This would need to be implemented based on your content models
        
        message = {
            'approved': 'AI içeriğiniz onaylandı',
            'rejected': 'AI içeriğiniz reddedildi',
            'modified': 'AI içeriğiniz düzenlenerek onaylandı'
        }
        
        # Send notification (implementation depends on your notification system)
        pass
    
    @staticmethod
    def _calculate_avg_review_time(query):
        """Calculate average review time for verified content"""
        
        completed = query.filter(
            HumanVerification.reviewed_at.isnot(None)
        ).all()
        
        if not completed:
            return 0
        
        total_time = sum(
            (v.reviewed_at - v.created_at).total_seconds()
            for v in completed
        )
        
        return total_time / len(completed)


class AIContentModerator:
    """Service for moderating AI-generated content"""
    
    CONTENT_POLICIES = {
        'profanity': True,
        'personal_info': True,
        'medical_advice': True,
        'legal_advice': True,
        'harmful_content': True
    }
    
    @staticmethod
    def moderate_content(content, content_type='text'):
        """Moderate AI-generated content for policy violations"""
        
        violations = []
        confidence = 1.0
        
        # Check for profanity
        if AIContentModerator.CONTENT_POLICIES['profanity']:
            if AIContentModerator._contains_profanity(content):
                violations.append('profanity')
                confidence *= 0.8
        
        # Check for personal information
        if AIContentModerator.CONTENT_POLICIES['personal_info']:
            if AIContentModerator._contains_personal_info(content):
                violations.append('personal_info')
                confidence *= 0.7
        
        # Check for medical/legal advice
        if content_type in ['assessment_feedback', 'recommendations']:
            if AIContentModerator._contains_professional_advice(content):
                violations.append('professional_advice')
                confidence *= 0.6
        
        return {
            'violations': violations,
            'confidence': confidence,
            'requires_review': len(violations) > 0 or confidence < 0.8,
            'auto_approve': len(violations) == 0 and confidence >= 0.9
        }
    
    @staticmethod
    def _contains_profanity(content):
        """Check for profanity in content"""
        # Implement profanity detection
        # This could use a profanity detection library or custom word list
        return False
    
    @staticmethod
    def _contains_personal_info(content):
        """Check for personal information in content"""
        import re
        
        # Check for common patterns
        patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{16}\b',              # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    @staticmethod
    def _contains_professional_advice(content):
        """Check for medical or legal advice"""
        
        medical_keywords = [
            'diagnosis', 'prescribe', 'medication', 'treatment',
            'medical advice', 'consult doctor'
        ]
        
        legal_keywords = [
            'legal advice', 'attorney', 'lawyer', 'lawsuit',
            'court', 'litigation'
        ]
        
        content_lower = content.lower()
        
        for keyword in medical_keywords + legal_keywords:
            if keyword in content_lower:
                return True
        
        return False