"""AI Chat Service for intelligent conversational assistance."""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from flask import current_app
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
import openai
from langdetect import detect
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.extensions import db, cache
from app.models.chat_conversation import (
    ChatConversation, ChatMessage, ChatRateLimit, 
    ConversationTemplate, ConversationStatus, MessageRole
)
from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.program import Program, ProgramEnrollment
from app.models.assessment import Assessment
from app.models.evaluation import Evaluation
from app.services.appointment_service import AppointmentService
from app.services.program_service import ProgramService
from app.services.notification_service import NotificationService
from app.utils.logger import logger
from app.utils.ai import configure_openai


class AIChatService:
    """Service for managing AI-powered chat conversations."""
    
    # Default rate limits
    DEFAULT_DAILY_MESSAGES = 100
    DEFAULT_DAILY_TOKENS = 50000
    DEFAULT_MONTHLY_MESSAGES = 1000
    DEFAULT_MONTHLY_TOKENS = 500000
    
    # Model configurations
    MODEL_CONFIGS = {
        'gpt-4': {'max_tokens': 1000, 'temperature': 0.7},
        'gpt-4-turbo': {'max_tokens': 1500, 'temperature': 0.7},
        'gpt-3.5-turbo': {'max_tokens': 800, 'temperature': 0.7}
    }
    
    # Context types and their system prompts
    CONTEXT_PROMPTS = {
        'education': """You are an educational support assistant helping beneficiaries with their learning journey. 
                       Provide clear, encouraging, and helpful responses about educational topics, study strategies, 
                       and program-related questions.""",
        
        'appointment': """You are an appointment scheduling assistant. Help users with booking, rescheduling, 
                         and managing their appointments. Provide clear information about availability and 
                         appointment procedures.""",
        
        'progress': """You are a progress tracking assistant. Help beneficiaries understand their progress, 
                      achievements, and areas for improvement. Be encouraging and constructive in your feedback.""",
        
        'assessment': """You are an assessment support assistant. Help users understand assessment requirements, 
                        preparation strategies, and provide guidance on improving their performance.""",
        
        'general': """You are a helpful assistant for the Beneficiary Development Center. Provide accurate, 
                     friendly, and supportive responses to help beneficiaries with their queries."""
    }
    
    def __init__(self):
        """Initialize the AI Chat Service."""
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize dependent services."""
        self.appointment_service = AppointmentService()
        self.program_service = ProgramService()
        self.notification_service = NotificationService()
    
    def create_conversation(
        self,
        user_id: int,
        beneficiary_id: Optional[int] = None,
        context_type: str = 'general',
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
        language: Optional[str] = None,
        initial_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new chat conversation.
        
        Args:
            user_id: ID of the user
            beneficiary_id: ID of the beneficiary (if applicable)
            context_type: Type of conversation context
            related_entity_type: Type of related entity
            related_entity_id: ID of related entity
            language: Conversation language ('en' or 'tr')
            initial_message: Optional initial message from user
            
        Returns:
            Dictionary with conversation details and initial response
        """
        try:
            # Check rate limits
            if not self._check_rate_limits(user_id):
                return {
                    'error': 'Rate limit exceeded',
                    'message': 'You have exceeded your chat limits. Please try again later.'
                }
            
            # Auto-detect language if not provided
            if not language and initial_message:
                language = self._detect_language(initial_message)
            elif not language:
                language = 'en'
            
            # Create conversation
            conversation = ChatConversation(
                user_id=user_id,
                beneficiary_id=beneficiary_id,
                context_type=context_type,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                language=language,
                status=ConversationStatus.ACTIVE,
                model=current_app.config.get('AI_MODEL', 'gpt-4')
            )
            
            # Generate title from initial message or context
            if initial_message:
                conversation.title = self._generate_conversation_title(initial_message)
            else:
                conversation.title = f"{context_type.capitalize()} Conversation"
            
            # Get user's tenant
            user = User.query.get(user_id)
            if user and user.tenants:
                conversation.tenant_id = user.tenants[0].id
            
            db.session.add(conversation)
            db.session.commit()
            
            # Get appropriate template
            template = self._get_conversation_template(
                context_type, language, conversation.tenant_id
            )
            
            # Add system message
            system_message = ChatMessage(
                conversation_id=conversation.id,
                role=MessageRole.SYSTEM,
                content=template.get('system_prompt', self.CONTEXT_PROMPTS.get(context_type, self.CONTEXT_PROMPTS['general']))
            )
            db.session.add(system_message)
            
            # Add welcome message
            welcome_message = ChatMessage(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=template.get('welcome_message', self._get_default_welcome_message(language))
            )
            db.session.add(welcome_message)
            
            # Process initial message if provided
            assistant_response = None
            if initial_message:
                user_message = ChatMessage(
                    conversation_id=conversation.id,
                    role=MessageRole.USER,
                    content=initial_message
                )
                db.session.add(user_message)
                db.session.commit()
                
                # Generate response
                assistant_response = self._generate_response(
                    conversation, initial_message
                )
            else:
                db.session.commit()
            
            # Update rate limits
            self._update_rate_limits(user_id, 1, 0)
            
            return {
                'conversation': conversation.to_dict(include_messages=True),
                'assistant_response': assistant_response,
                'suggested_questions': template.get('suggested_questions', [])
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating conversation: {str(e)}")
            return {
                'error': 'Failed to create conversation',
                'message': str(e)
            }
    
    def send_message(
        self,
        conversation_id: int,
        user_id: int,
        message: str
    ) -> Dict[str, Any]:
        """
        Send a message in an existing conversation.
        
        Args:
            conversation_id: ID of the conversation
            user_id: ID of the user sending the message
            message: Message content
            
        Returns:
            Dictionary with assistant response
        """
        try:
            # Get conversation
            conversation = ChatConversation.query.filter_by(
                id=conversation_id,
                user_id=user_id
            ).first()
            
            if not conversation:
                return {
                    'error': 'Conversation not found'
                }
            
            if conversation.status != ConversationStatus.ACTIVE:
                return {
                    'error': 'Conversation is not active'
                }
            
            # Check rate limits
            if not self._check_rate_limits(user_id):
                return {
                    'error': 'Rate limit exceeded',
                    'message': 'You have exceeded your chat limits. Please try again later.'
                }
            
            # Add user message
            user_message = ChatMessage(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content=message
            )
            db.session.add(user_message)
            
            # Update conversation
            conversation.message_count += 1
            conversation.last_message_at = datetime.utcnow()
            
            db.session.commit()
            
            # Generate response
            response = self._generate_response(conversation, message)
            
            # Check for conversation closure intent
            if self._should_close_conversation(message, response.get('content', '')):
                conversation.status = ConversationStatus.CLOSED
                conversation.closed_at = datetime.utcnow()
                db.session.commit()
            
            return response
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error sending message: {str(e)}")
            return {
                'error': 'Failed to send message',
                'message': str(e)
            }
    
    def _generate_response(
        self,
        conversation: ChatConversation,
        user_message: str
    ) -> Dict[str, Any]:
        """Generate AI response for user message."""
        try:
            # Configure OpenAI
            configure_openai()
            
            # Get conversation context
            context = self._build_conversation_context(conversation)
            
            # Add context-specific information
            enhanced_message = self._enhance_message_with_context(
                conversation, user_message
            )
            
            # Get recent messages for context
            recent_messages = conversation.messages.filter(
                ChatMessage.role != MessageRole.SYSTEM
            ).order_by(ChatMessage.created_at.desc()).limit(10).all()
            
            # Build messages for API
            messages = [
                {"role": "system", "content": context['system_prompt']}
            ]
            
            # Add conversation history (in chronological order)
            for msg in reversed(recent_messages):
                if msg.role == MessageRole.USER:
                    messages.append({"role": "user", "content": msg.content})
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append({"role": "assistant", "content": msg.content})
            
            # Add enhanced current message
            messages.append({"role": "user", "content": enhanced_message})
            
            # Get model config
            model_config = self.MODEL_CONFIGS.get(
                conversation.model, 
                self.MODEL_CONFIGS['gpt-4']
            )
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=conversation.model,
                messages=messages,
                temperature=conversation.temperature or model_config['temperature'],
                max_tokens=conversation.max_tokens or model_config['max_tokens'],
                functions=self._get_available_functions(conversation.context_type),
                function_call="auto"
            )
            
            # Extract response
            message_content = response.choices[0].message.get('content', '')
            function_call = response.choices[0].message.get('function_call')
            
            # Handle function calls
            if function_call:
                function_result = self._handle_function_call(
                    conversation, function_call
                )
                if function_result:
                    message_content = function_result.get('message', message_content)
            
            # Create assistant message
            assistant_message = ChatMessage(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=message_content,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                metadata={'function_call': function_call} if function_call else None
            )
            db.session.add(assistant_message)
            
            # Update rate limits
            self._update_rate_limits(
                conversation.user_id,
                0,
                response.usage.total_tokens
            )
            
            # Update conversation summary periodically
            if conversation.message_count % 10 == 0:
                self._update_conversation_summary(conversation)
            
            db.session.commit()
            
            return {
                'message': assistant_message.to_dict(),
                'content': message_content,
                'function_call': function_call,
                'tokens_used': response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            
            # Create error message
            error_message = ChatMessage(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=self._get_error_message(conversation.language),
                is_error=True,
                error_message=str(e)
            )
            db.session.add(error_message)
            db.session.commit()
            
            return {
                'error': 'Failed to generate response',
                'message': str(e),
                'content': error_message.content
            }
    
    def _build_conversation_context(
        self,
        conversation: ChatConversation
    ) -> Dict[str, Any]:
        """Build context for the conversation."""
        base_prompt = self.CONTEXT_PROMPTS.get(
            conversation.context_type,
            self.CONTEXT_PROMPTS['general']
        )
        
        # Add language instruction
        if conversation.language == 'tr':
            base_prompt += "\n\nIMPORTANT: Respond in Turkish language."
        
        # Add entity-specific context
        if conversation.related_entity_type and conversation.related_entity_id:
            entity_context = self._get_entity_context(
                conversation.related_entity_type,
                conversation.related_entity_id
            )
            if entity_context:
                base_prompt += f"\n\nContext: {entity_context}"
        
        # Add beneficiary context
        if conversation.beneficiary_id:
            beneficiary_context = self._get_beneficiary_context(
                conversation.beneficiary_id
            )
            if beneficiary_context:
                base_prompt += f"\n\nBeneficiary Info: {beneficiary_context}"
        
        return {
            'system_prompt': base_prompt,
            'context_type': conversation.context_type,
            'language': conversation.language
        }
    
    def _enhance_message_with_context(
        self,
        conversation: ChatConversation,
        message: str
    ) -> str:
        """Enhance user message with additional context."""
        enhanced = message
        
        # Add timestamp context for appointment queries
        if conversation.context_type == 'appointment':
            enhanced += f"\n\n[Current time: {datetime.utcnow().isoformat()}]"
        
        # Add progress context
        if conversation.context_type == 'progress' and conversation.beneficiary_id:
            progress = self._get_beneficiary_progress(conversation.beneficiary_id)
            if progress:
                enhanced += f"\n\n[Progress Context: {progress}]"
        
        return enhanced
    
    def _get_available_functions(self, context_type: str) -> List[Dict[str, Any]]:
        """Get available functions based on context type."""
        functions = []
        
        if context_type == 'appointment':
            functions.extend([
                {
                    "name": "check_availability",
                    "description": "Check available appointment slots",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Date to check (YYYY-MM-DD)"},
                            "trainer_id": {"type": "integer", "description": "Trainer ID (optional)"}
                        },
                        "required": ["date"]
                    }
                },
                {
                    "name": "book_appointment",
                    "description": "Book an appointment",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Appointment date"},
                            "time": {"type": "string", "description": "Appointment time"},
                            "trainer_id": {"type": "integer", "description": "Trainer ID"},
                            "purpose": {"type": "string", "description": "Purpose of appointment"}
                        },
                        "required": ["date", "time", "trainer_id"]
                    }
                }
            ])
        
        elif context_type == 'progress':
            functions.append({
                "name": "get_progress_report",
                "description": "Get beneficiary's progress report",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "period": {"type": "string", "description": "Period (week, month, all)"},
                        "include_details": {"type": "boolean", "description": "Include detailed metrics"}
                    }
                }
            })
        
        elif context_type == 'education':
            functions.append({
                "name": "get_program_info",
                "description": "Get information about programs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "program_id": {"type": "integer", "description": "Program ID (optional)"},
                        "category": {"type": "string", "description": "Program category (optional)"}
                    }
                }
            })
        
        return functions
    
    def _handle_function_call(
        self,
        conversation: ChatConversation,
        function_call: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Handle function calls from AI."""
        function_name = function_call.get('name')
        arguments = json.loads(function_call.get('arguments', '{}'))
        
        try:
            if function_name == 'check_availability':
                result = self._check_availability(
                    conversation.beneficiary_id,
                    arguments.get('date'),
                    arguments.get('trainer_id')
                )
                return {
                    'message': self._format_availability_response(result, conversation.language)
                }
            
            elif function_name == 'book_appointment':
                result = self._book_appointment(
                    conversation.beneficiary_id,
                    arguments
                )
                return {
                    'message': self._format_booking_response(result, conversation.language)
                }
            
            elif function_name == 'get_progress_report':
                result = self._get_progress_report(
                    conversation.beneficiary_id,
                    arguments.get('period', 'month')
                )
                return {
                    'message': self._format_progress_response(result, conversation.language)
                }
            
            elif function_name == 'get_program_info':
                result = self._get_program_info(
                    arguments.get('program_id'),
                    arguments.get('category')
                )
                return {
                    'message': self._format_program_response(result, conversation.language)
                }
            
        except Exception as e:
            logger.error(f"Error handling function call {function_name}: {str(e)}")
            return None
        
        return None
    
    def _check_rate_limits(self, user_id: int) -> bool:
        """Check if user has exceeded rate limits."""
        rate_limit = ChatRateLimit.query.filter_by(user_id=user_id).first()
        
        if not rate_limit:
            # Create new rate limit record
            rate_limit = ChatRateLimit(
                user_id=user_id,
                daily_reset_at=datetime.utcnow() + timedelta(days=1),
                monthly_reset_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(rate_limit)
            db.session.commit()
            return True
        
        # Check daily limits
        if rate_limit.daily_reset_at and datetime.utcnow() > rate_limit.daily_reset_at:
            rate_limit.daily_message_count = 0
            rate_limit.daily_token_count = 0
            rate_limit.daily_reset_at = datetime.utcnow() + timedelta(days=1)
        
        # Check monthly limits
        if rate_limit.monthly_reset_at and datetime.utcnow() > rate_limit.monthly_reset_at:
            rate_limit.monthly_message_count = 0
            rate_limit.monthly_token_count = 0
            rate_limit.monthly_reset_at = datetime.utcnow() + timedelta(days=30)
        
        # Get limits
        max_daily_messages = rate_limit.max_daily_messages or self.DEFAULT_DAILY_MESSAGES
        max_daily_tokens = rate_limit.max_daily_tokens or self.DEFAULT_DAILY_TOKENS
        max_monthly_messages = rate_limit.max_monthly_messages or self.DEFAULT_MONTHLY_MESSAGES
        max_monthly_tokens = rate_limit.max_monthly_tokens or self.DEFAULT_MONTHLY_TOKENS
        
        # Check if limits exceeded
        if rate_limit.daily_message_count >= max_daily_messages:
            return False
        if rate_limit.daily_token_count >= max_daily_tokens:
            return False
        if rate_limit.monthly_message_count >= max_monthly_messages:
            return False
        if rate_limit.monthly_token_count >= max_monthly_tokens:
            return False
        
        return True
    
    def _update_rate_limits(self, user_id: int, messages: int, tokens: int):
        """Update rate limit counters."""
        rate_limit = ChatRateLimit.query.filter_by(user_id=user_id).first()
        
        if rate_limit:
            rate_limit.daily_message_count += messages
            rate_limit.daily_token_count += tokens
            rate_limit.monthly_message_count += messages
            rate_limit.monthly_token_count += tokens
            db.session.commit()
    
    def get_conversation_history(
        self,
        user_id: int,
        beneficiary_id: Optional[int] = None,
        status: Optional[ConversationStatus] = None,
        context_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get conversation history for a user."""
        try:
            query = ChatConversation.query.filter_by(user_id=user_id)
            
            if beneficiary_id:
                query = query.filter_by(beneficiary_id=beneficiary_id)
            if status:
                query = query.filter_by(status=status)
            if context_type:
                query = query.filter_by(context_type=context_type)
            
            total = query.count()
            conversations = query.order_by(
                ChatConversation.updated_at.desc()
            ).limit(limit).offset(offset).all()
            
            return {
                'conversations': [conv.to_dict() for conv in conversations],
                'total': total,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return {
                'error': 'Failed to get conversation history',
                'message': str(e)
            }
    
    def export_conversation(
        self,
        conversation_id: int,
        user_id: int,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """Export a conversation in specified format."""
        try:
            conversation = ChatConversation.query.filter_by(
                id=conversation_id,
                user_id=user_id
            ).first()
            
            if not conversation:
                return {'error': 'Conversation not found'}
            
            if format == 'json':
                return {
                    'data': conversation.to_dict(include_messages=True),
                    'format': 'json'
                }
            
            elif format == 'text':
                messages = conversation.messages.order_by(
                    ChatMessage.created_at
                ).all()
                
                text_content = f"Conversation: {conversation.title}\n"
                text_content += f"Date: {conversation.created_at.isoformat()}\n"
                text_content += f"Language: {conversation.language}\n"
                text_content += "-" * 50 + "\n\n"
                
                for msg in messages:
                    if msg.role != MessageRole.SYSTEM:
                        text_content += f"{msg.role.value.upper()}: {msg.content}\n"
                        text_content += f"Time: {msg.created_at.isoformat()}\n"
                        text_content += "-" * 30 + "\n\n"
                
                return {
                    'data': text_content,
                    'format': 'text'
                }
            
            else:
                return {'error': 'Unsupported export format'}
                
        except Exception as e:
            logger.error(f"Error exporting conversation: {str(e)}")
            return {
                'error': 'Failed to export conversation',
                'message': str(e)
            }
    
    def flag_conversation(
        self,
        conversation_id: int,
        admin_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Flag a conversation for moderation."""
        try:
            conversation = ChatConversation.query.get(conversation_id)
            
            if not conversation:
                return {'error': 'Conversation not found'}
            
            conversation.is_flagged = True
            conversation.flag_reason = reason
            conversation.flagged_by = admin_id
            conversation.flagged_at = datetime.utcnow()
            conversation.status = ConversationStatus.FLAGGED
            
            # Send notification to user
            self.notification_service.create_notification(
                user_id=conversation.user_id,
                title="Conversation Flagged",
                message=f"Your conversation has been flagged for review: {reason}",
                type="moderation",
                related_type="chat_conversation",
                related_id=conversation_id
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'conversation': conversation.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error flagging conversation: {str(e)}")
            return {
                'error': 'Failed to flag conversation',
                'message': str(e)
            }
    
    def get_conversation_analytics(
        self,
        tenant_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get conversation analytics."""
        try:
            query = ChatConversation.query
            
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            if start_date:
                query = query.filter(ChatConversation.created_at >= start_date)
            if end_date:
                query = query.filter(ChatConversation.created_at <= end_date)
            
            # Basic stats
            total_conversations = query.count()
            active_conversations = query.filter_by(status=ConversationStatus.ACTIVE).count()
            flagged_conversations = query.filter_by(is_flagged=True).count()
            
            # Language distribution
            language_stats = db.session.query(
                ChatConversation.language,
                func.count(ChatConversation.id)
            ).filter(
                query.whereclause if query.whereclause is not None else True
            ).group_by(ChatConversation.language).all()
            
            # Context type distribution
            context_stats = db.session.query(
                ChatConversation.context_type,
                func.count(ChatConversation.id)
            ).filter(
                query.whereclause if query.whereclause is not None else True
            ).group_by(ChatConversation.context_type).all()
            
            # Average messages per conversation
            avg_messages = db.session.query(
                func.avg(ChatConversation.message_count)
            ).filter(
                query.whereclause if query.whereclause is not None else True
            ).scalar() or 0
            
            # Token usage
            token_usage = db.session.query(
                func.sum(ChatMessage.total_tokens)
            ).join(ChatConversation).filter(
                query.whereclause if query.whereclause is not None else True
            ).scalar() or 0
            
            return {
                'total_conversations': total_conversations,
                'active_conversations': active_conversations,
                'flagged_conversations': flagged_conversations,
                'language_distribution': dict(language_stats),
                'context_distribution': dict(context_stats),
                'average_messages_per_conversation': float(avg_messages),
                'total_tokens_used': token_usage
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation analytics: {str(e)}")
            return {
                'error': 'Failed to get analytics',
                'message': str(e)
            }
    
    def _detect_language(self, text: str) -> str:
        """Detect language from text."""
        try:
            lang = detect(text)
            return 'tr' if lang == 'tr' else 'en'
        except:
            return 'en'
    
    def _generate_conversation_title(self, message: str) -> str:
        """Generate a title for the conversation from the first message."""
        # Truncate to first sentence or 50 chars
        title = message.split('.')[0]
        if len(title) > 50:
            title = title[:47] + '...'
        return title
    
    def _get_conversation_template(
        self,
        context_type: str,
        language: str,
        tenant_id: Optional[int]
    ) -> Dict[str, Any]:
        """Get conversation template based on context and language."""
        # Try to get tenant-specific template
        template = ConversationTemplate.query.filter_by(
            tenant_id=tenant_id,
            category=context_type,
            language=language,
            is_active=True
        ).order_by(ConversationTemplate.priority.desc()).first()
        
        # Fallback to global template
        if not template:
            template = ConversationTemplate.query.filter_by(
                tenant_id=None,
                category=context_type,
                language=language,
                is_active=True
            ).order_by(ConversationTemplate.priority.desc()).first()
        
        if template:
            return template.to_dict()
        
        # Default templates
        return {
            'system_prompt': self.CONTEXT_PROMPTS.get(context_type, self.CONTEXT_PROMPTS['general']),
            'welcome_message': self._get_default_welcome_message(language),
            'suggested_questions': self._get_default_suggestions(context_type, language)
        }
    
    def _get_default_welcome_message(self, language: str) -> str:
        """Get default welcome message."""
        if language == 'tr':
            return "Merhaba! Size nasıl yardımcı olabilirim?"
        return "Hello! How can I help you today?"
    
    def _get_default_suggestions(self, context_type: str, language: str) -> List[str]:
        """Get default question suggestions."""
        suggestions = {
            'education': {
                'en': [
                    "What programs are available?",
                    "How can I improve my study habits?",
                    "What resources are available for learning?"
                ],
                'tr': [
                    "Hangi programlar mevcut?",
                    "Çalışma alışkanlıklarımı nasıl geliştirebilirim?",
                    "Öğrenme için hangi kaynaklar mevcut?"
                ]
            },
            'appointment': {
                'en': [
                    "When is my next appointment?",
                    "Can I schedule a new appointment?",
                    "How do I reschedule my appointment?"
                ],
                'tr': [
                    "Bir sonraki randevum ne zaman?",
                    "Yeni bir randevu alabilir miyim?",
                    "Randevumu nasıl yeniden planlayabilirim?"
                ]
            },
            'progress': {
                'en': [
                    "How am I doing in my programs?",
                    "What areas should I focus on?",
                    "Can I see my recent achievements?"
                ],
                'tr': [
                    "Programlarımda nasıl ilerliyorum?",
                    "Hangi alanlara odaklanmalıyım?",
                    "Son başarılarımı görebilir miyim?"
                ]
            },
            'general': {
                'en': [
                    "Tell me about the center",
                    "What services are available?",
                    "How can I get help?"
                ],
                'tr': [
                    "Merkez hakkında bilgi verin",
                    "Hangi hizmetler mevcut?",
                    "Nasıl yardım alabilirim?"
                ]
            }
        }
        
        return suggestions.get(context_type, suggestions['general']).get(language, [])
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in appropriate language."""
        if language == 'tr':
            return "Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin."
        return "I'm sorry, an error occurred. Please try again later."
    
    def _should_close_conversation(self, user_message: str, assistant_response: str) -> bool:
        """Check if conversation should be closed."""
        closing_phrases = [
            'goodbye', 'bye', 'thank you', 'thanks', 'that\'s all',
            'güle güle', 'hoşça kal', 'teşekkür ederim', 'sağ ol'
        ]
        
        message_lower = user_message.lower()
        for phrase in closing_phrases:
            if phrase in message_lower:
                return True
        
        return False
    
    def _update_conversation_summary(self, conversation: ChatConversation):
        """Update conversation summary using AI."""
        try:
            messages = conversation.messages.filter(
                ChatMessage.role != MessageRole.SYSTEM
            ).order_by(ChatMessage.created_at).all()
            
            if len(messages) < 5:
                return
            
            # Build conversation text
            conversation_text = "\n".join([
                f"{msg.role.value}: {msg.content}"
                for msg in messages
            ])
            
            # Generate summary
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize this conversation in 2-3 sentences. Also identify key topics discussed."
                    },
                    {
                        "role": "user",
                        "content": conversation_text
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            summary_data = response.choices[0].message['content']
            
            # Parse summary and topics
            lines = summary_data.split('\n')
            summary = lines[0] if lines else "No summary available"
            
            # Extract topics (simple approach)
            topics = []
            if 'topics:' in summary_data.lower():
                topics_line = [l for l in lines if 'topics:' in l.lower()]
                if topics_line:
                    topics = [t.strip() for t in topics_line[0].split(':')[1].split(',')]
            
            conversation.summary = summary
            conversation.key_topics = topics
            
        except Exception as e:
            logger.error(f"Error updating conversation summary: {str(e)}")
    
    # Helper methods for function calls
    def _check_availability(self, beneficiary_id: int, date: str, trainer_id: Optional[int]) -> Dict:
        """Check appointment availability."""
        # Implementation would call appointment service
        return {
            'available_slots': ['10:00', '14:00', '16:00'],
            'date': date
        }
    
    def _book_appointment(self, beneficiary_id: int, details: Dict) -> Dict:
        """Book an appointment."""
        # Implementation would call appointment service
        return {
            'success': True,
            'appointment_id': 123,
            'details': details
        }
    
    def _get_progress_report(self, beneficiary_id: int, period: str) -> Dict:
        """Get beneficiary progress report."""
        # Implementation would call program service
        return {
            'period': period,
            'overall_progress': 75,
            'completed_sessions': 12,
            'upcoming_sessions': 3
        }
    
    def _get_program_info(self, program_id: Optional[int], category: Optional[str]) -> Dict:
        """Get program information."""
        # Implementation would call program service
        return {
            'programs': [
                {'id': 1, 'name': 'Basic Skills', 'duration': '3 months'},
                {'id': 2, 'name': 'Advanced Training', 'duration': '6 months'}
            ]
        }
    
    def _get_entity_context(self, entity_type: str, entity_id: int) -> Optional[str]:
        """Get context information for related entity."""
        try:
            if entity_type == 'appointment':
                appointment = Appointment.query.get(entity_id)
                if appointment:
                    return f"Appointment on {appointment.start_time} with {appointment.trainer.full_name}"
            
            elif entity_type == 'program':
                program = Program.query.get(entity_id)
                if program:
                    return f"Program: {program.name} - {program.description}"
            
            elif entity_type == 'assessment':
                assessment = Assessment.query.get(entity_id)
                if assessment:
                    return f"Assessment: {assessment.title}"
            
        except Exception as e:
            logger.error(f"Error getting entity context: {str(e)}")
        
        return None
    
    def _get_beneficiary_context(self, beneficiary_id: int) -> Optional[str]:
        """Get beneficiary context information."""
        try:
            beneficiary = Beneficiary.query.get(beneficiary_id)
            if beneficiary:
                return f"Name: {beneficiary.full_name}, Status: {beneficiary.status}"
        except Exception as e:
            logger.error(f"Error getting beneficiary context: {str(e)}")
        
        return None
    
    def _get_beneficiary_progress(self, beneficiary_id: int) -> Optional[str]:
        """Get beneficiary progress summary."""
        try:
            # Get active enrollments
            enrollments = ProgramEnrollment.query.filter_by(
                beneficiary_id=beneficiary_id,
                status='active'
            ).all()
            
            if enrollments:
                progress_info = []
                for enrollment in enrollments:
                    progress_info.append(
                        f"{enrollment.program.name}: {enrollment.progress}% complete"
                    )
                return ", ".join(progress_info)
                
        except Exception as e:
            logger.error(f"Error getting beneficiary progress: {str(e)}")
        
        return None
    
    def _format_availability_response(self, result: Dict, language: str) -> str:
        """Format availability check response."""
        if language == 'tr':
            return f"{result['date']} tarihinde şu saatler müsait: {', '.join(result['available_slots'])}"
        return f"Available slots on {result['date']}: {', '.join(result['available_slots'])}"
    
    def _format_booking_response(self, result: Dict, language: str) -> str:
        """Format appointment booking response."""
        if result.get('success'):
            if language == 'tr':
                return f"Randevunuz başarıyla oluşturuldu. Randevu numarası: {result['appointment_id']}"
            return f"Your appointment has been booked successfully. Appointment ID: {result['appointment_id']}"
        else:
            if language == 'tr':
                return "Randevu oluşturulamadı. Lütfen daha sonra tekrar deneyin."
            return "Could not book the appointment. Please try again later."
    
    def _format_progress_response(self, result: Dict, language: str) -> str:
        """Format progress report response."""
        if language == 'tr':
            return (f"{result['period']} döneminde ilerlemeniz: %{result['overall_progress']}. "
                   f"Tamamlanan oturumlar: {result['completed_sessions']}, "
                   f"Yaklaşan oturumlar: {result['upcoming_sessions']}")
        return (f"Your progress for {result['period']}: {result['overall_progress']}%. "
               f"Completed sessions: {result['completed_sessions']}, "
               f"Upcoming sessions: {result['upcoming_sessions']}")
    
    def _format_program_response(self, result: Dict, language: str) -> str:
        """Format program information response."""
        programs = result.get('programs', [])
        if not programs:
            if language == 'tr':
                return "Şu anda uygun program bulunmamaktadır."
            return "No programs are currently available."
        
        if language == 'tr':
            response = "Mevcut programlar:\n"
            for prog in programs:
                response += f"- {prog['name']} (Süre: {prog['duration']})\n"
        else:
            response = "Available programs:\n"
            for prog in programs:
                response += f"- {prog['name']} (Duration: {prog['duration']})\n"
        
        return response


# Create singleton instance
ai_chat_service = AIChatService()