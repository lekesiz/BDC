"""SMS repository implementation."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, or_, func

from app.extensions import db
from app.models.sms_message import SMSMessage, SMSTemplate, SMSCampaign, SMSStatus
from app.repositories.interfaces.sms_repository_interface import ISMSRepository


class SMSRepository(ISMSRepository):
    """SMS repository for database operations."""
    
    def create(self, **kwargs) -> Optional[SMSMessage]:
        """Create a new SMS message record."""
        try:
            sms_message = SMSMessage(**kwargs)
            db.session.add(sms_message)
            db.session.commit()
            return sms_message
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get(self, message_id: int) -> Optional[SMSMessage]:
        """Get an SMS message by ID."""
        return SMSMessage.query.get(message_id)
    
    def update(self, message_id: int, **kwargs) -> bool:
        """Update an SMS message."""
        try:
            sms_message = self.get(message_id)
            if not sms_message:
                return False
            
            for key, value in kwargs.items():
                if hasattr(sms_message, key):
                    setattr(sms_message, key, value)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self, message_id: int) -> bool:
        """Delete an SMS message."""
        try:
            sms_message = self.get(message_id)
            if not sms_message:
                return False
            
            db.session.delete(sms_message)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_by_status(self, status: str, limit: int = 100) -> List[SMSMessage]:
        """Get SMS messages by status."""
        return SMSMessage.query.filter_by(status=status).limit(limit).all()
    
    def get_scheduled_messages(self, before_time: datetime) -> List[SMSMessage]:
        """Get scheduled messages that need to be sent."""
        return SMSMessage.query.filter(
            and_(
                SMSMessage.status == SMSStatus.PENDING.value,
                SMSMessage.scheduled_for.isnot(None),
                SMSMessage.scheduled_for <= before_time
            )
        ).all()
    
    def get_user_messages(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        status: Optional[str] = None
    ) -> List[SMSMessage]:
        """Get SMS messages for a specific user."""
        query = SMSMessage.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(SMSMessage.created_at.desc())\
                   .limit(limit)\
                   .offset(offset)\
                   .all()
    
    def get_by_phone(
        self,
        phone_number: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[SMSMessage]:
        """Get SMS messages by phone number."""
        return SMSMessage.query.filter_by(recipient_phone=phone_number)\
                              .order_by(SMSMessage.created_at.desc())\
                              .limit(limit)\
                              .offset(offset)\
                              .all()
    
    def get_by_campaign(self, campaign_id: int) -> List[SMSMessage]:
        """Get SMS messages for a specific campaign."""
        return SMSMessage.query.filter(
            SMSMessage.metadata.contains({'campaign_id': campaign_id})
        ).all()
    
    def count_by_status(self, status: str, start_date: Optional[datetime] = None) -> int:
        """Count SMS messages by status."""
        query = SMSMessage.query.filter_by(status=status)
        
        if start_date:
            query = query.filter(SMSMessage.created_at >= start_date)
        
        return query.count()
    
    def get_cost_summary(
        self,
        tenant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get cost summary for SMS messages."""
        query = db.session.query(
            func.sum(SMSMessage.cost_amount).label('total_cost'),
            func.count(SMSMessage.id).label('total_messages'),
            func.avg(SMSMessage.cost_amount).label('avg_cost')
        )
        
        if tenant_id:
            query = query.filter(SMSMessage.tenant_id == tenant_id)
        if start_date:
            query = query.filter(SMSMessage.created_at >= start_date)
        if end_date:
            query = query.filter(SMSMessage.created_at <= end_date)
        
        result = query.first()
        
        return {
            'total_cost': float(result.total_cost or 0),
            'total_messages': result.total_messages or 0,
            'average_cost': float(result.avg_cost or 0),
            'currency': 'USD'
        }


class SMSTemplateRepository:
    """Repository for SMS template operations."""
    
    def create(self, **kwargs) -> Optional[SMSTemplate]:
        """Create a new SMS template."""
        try:
            template = SMSTemplate(**kwargs)
            db.session.add(template)
            db.session.commit()
            return template
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get(self, template_id: int) -> Optional[SMSTemplate]:
        """Get an SMS template by ID."""
        return SMSTemplate.query.get(template_id)
    
    def get_by_template_id(self, template_id: str) -> Optional[SMSTemplate]:
        """Get an SMS template by template ID."""
        return SMSTemplate.query.filter_by(template_id=template_id).first()
    
    def get_active_templates(self, tenant_id: Optional[int] = None) -> List[SMSTemplate]:
        """Get active SMS templates."""
        query = SMSTemplate.query.filter_by(is_active=True)
        
        if tenant_id:
            query = query.filter(
                or_(
                    SMSTemplate.tenant_id == tenant_id,
                    SMSTemplate.tenant_id.is_(None)
                )
            )
        
        return query.all()
    
    def update(self, template_id: int, **kwargs) -> bool:
        """Update an SMS template."""
        try:
            template = self.get(template_id)
            if not template:
                return False
            
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self, template_id: int) -> bool:
        """Delete an SMS template."""
        try:
            template = self.get(template_id)
            if not template:
                return False
            
            db.session.delete(template)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e


class SMSCampaignRepository:
    """Repository for SMS campaign operations."""
    
    def create(self, **kwargs) -> Optional[SMSCampaign]:
        """Create a new SMS campaign."""
        try:
            campaign = SMSCampaign(**kwargs)
            db.session.add(campaign)
            db.session.commit()
            return campaign
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get(self, campaign_id: int) -> Optional[SMSCampaign]:
        """Get an SMS campaign by ID."""
        return SMSCampaign.query.get(campaign_id)
    
    def get_scheduled_campaigns(self, before_time: datetime) -> List[SMSCampaign]:
        """Get scheduled campaigns that need to be executed."""
        return SMSCampaign.query.filter(
            and_(
                SMSCampaign.status == 'scheduled',
                SMSCampaign.scheduled_for.isnot(None),
                SMSCampaign.scheduled_for <= before_time
            )
        ).all()
    
    def get_tenant_campaigns(
        self,
        tenant_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[SMSCampaign]:
        """Get campaigns for a specific tenant."""
        return SMSCampaign.query.filter_by(tenant_id=tenant_id)\
                                .order_by(SMSCampaign.created_at.desc())\
                                .limit(limit)\
                                .offset(offset)\
                                .all()
    
    def update(self, campaign_id: int, **kwargs) -> bool:
        """Update an SMS campaign."""
        try:
            campaign = self.get(campaign_id)
            if not campaign:
                return False
            
            for key, value in kwargs.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e
    
    def delete(self, campaign_id: int) -> bool:
        """Delete an SMS campaign."""
        try:
            campaign = self.get(campaign_id)
            if not campaign:
                return False
            
            db.session.delete(campaign)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e