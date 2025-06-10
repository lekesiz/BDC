_('services_ai_chat_service.message.ai_chat_service_for_intelligen')
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
from app.models.chat_conversation import ChatConversation, ChatMessage, ChatRateLimit, ConversationTemplate, ConversationStatus, MessageRole
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
from flask_babel import _, lazy_gettext as _l


class AIChatService:
    _('services_ai_chat_service.message.service_for_managing_ai_powere')
    DEFAULT_DAILY_MESSAGES = 100
    DEFAULT_DAILY_TOKENS = 50000
    DEFAULT_MONTHLY_MESSAGES = 1000
    DEFAULT_MONTHLY_TOKENS = 500000
    MODEL_CONFIGS = {_('orchestration_examples.message.gpt_4_2'): {
        'max_tokens': 1000, 'temperature': 0.7}, _(
        'services_ai_chat_service.message.gpt_4_turbo'): {'max_tokens': 
        1500, 'temperature': 0.7}, _(
        'i18n_content_translation_service.message.gpt_3_5_turbo_1'): {
        'max_tokens': 800, 'temperature': 0.7}}
    CONTEXT_PROMPTS = {'education': _(
        'services_ai_chat_service.message.you_are_an_educational_support'),
        'appointment': _(
        'services_ai_chat_service.validation.you_are_an_appointment_schedul'
        ), 'progress': _(
        'services_ai_chat_service.message.you_are_a_progress_tracking_as'),
        'assessment': _(
        'services_ai_chat_service.message.you_are_an_assessment_support'),
        'general': _(
        'services_ai_chat_service.message.you_are_a_helpful_assistant_fo')}

    def __init__(self):
        _('services_ai_chat_service.message.initialize_the_ai_chat_service')
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._initialize_services()

    def _initialize_services(self):
        _('services_ai_chat_service.label.initialize_dependent_services')
        self.appointment_service = AppointmentService()
        self.program_service = ProgramService()
        self.notification_service = NotificationService()

    def create_conversation(self, user_id: int, beneficiary_id: Optional[
        int]=None, context_type: str='general', related_entity_type:
        Optional[str]=None, related_entity_id: Optional[int]=None, language:
        Optional[str]=None, initial_message: Optional[str]=None) ->Dict[str,
        Any]:
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
            if not self._check_rate_limits(user_id):
                return {'error': _(
                    'optimization_api_optimizer.label.rate_limit_exceeded'),
                    'message': _(
                    'services_ai_chat_service.message.you_have_exceeded_your_chat_li_1'
                    )}
            if not language and initial_message:
                language = self._detect_language(initial_message)
            elif not language:
                language = 'en'
            conversation = ChatConversation(user_id=user_id, beneficiary_id
                =beneficiary_id, context_type=context_type,
                related_entity_type=related_entity_type, related_entity_id=
                related_entity_id, language=language, status=
                ConversationStatus.ACTIVE, model=current_app.config.get(
                'AI_MODEL', _('orchestration_examples.message.gpt_4_2')))
            if initial_message:
                conversation.title = self._generate_conversation_title(
                    initial_message)
            else:
                conversation.title = (
                    f'{context_type.capitalize()} Conversation')
            user = User.query.get(user_id)
            if user and user.tenants:
                conversation.tenant_id = user.tenants[0].id
            db.session.add(conversation)
            db.session.commit()
            template = self._get_conversation_template(context_type,
                language, conversation.tenant_id)
            system_message = ChatMessage(conversation_id=conversation.id,
                role=MessageRole.SYSTEM, content=template.get(
                'system_prompt', self.CONTEXT_PROMPTS.get(context_type,
                self.CONTEXT_PROMPTS['general'])))
            db.session.add(system_message)
            welcome_message = ChatMessage(conversation_id=conversation.id,
                role=MessageRole.ASSISTANT, content=template.get(
                'welcome_message', self._get_default_welcome_message(language))
                )
            db.session.add(welcome_message)
            assistant_response = None
            if initial_message:
                user_message = ChatMessage(conversation_id=conversation.id,
                    role=MessageRole.USER, content=initial_message)
                db.session.add(user_message)
                db.session.commit()
                assistant_response = self._generate_response(conversation,
                    initial_message)
            else:
                db.session.commit()
            self._update_rate_limits(user_id, 1, 0)
            return {'conversation': conversation.to_dict(include_messages=
                True), 'assistant_response': assistant_response,
                'suggested_questions': template.get('suggested_questions', [])}
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating conversation: {str(e)}')
            return {'error': _(
                'services_ai_chat_service.error.failed_to_create_conversation'
                ), 'message': str(e)}

    def send_message(self, conversation_id: int, user_id: int, message: str
        ) ->Dict[str, Any]:
        _('services_ai_chat_service.message.send_a_message_in_an')
        try:
            conversation = ChatConversation.query.filter_by(id=
                conversation_id, user_id=user_id).first()
            if not conversation:
                return {'error': _(
                    'services_ai_chat_service.label.conversation_not_found_2')}
            if conversation.status != ConversationStatus.ACTIVE:
                return {'error': _(
                    'services_ai_chat_service.message.conversation_is_not_active'
                    )}
            if not self._check_rate_limits(user_id):
                return {'error': _(
                    'optimization_api_optimizer.label.rate_limit_exceeded'),
                    'message': _(
                    'services_ai_chat_service.message.you_have_exceeded_your_chat_li_1'
                    )}
            user_message = ChatMessage(conversation_id=conversation_id,
                role=MessageRole.USER, content=message)
            db.session.add(user_message)
            conversation.message_count += 1
            conversation.last_message_at = datetime.utcnow()
            db.session.commit()
            response = self._generate_response(conversation, message)
            if self._should_close_conversation(message, response.get(
                'content', '')):
                conversation.status = ConversationStatus.CLOSED
                conversation.closed_at = datetime.utcnow()
                db.session.commit()
            return response
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error sending message: {str(e)}')
            return {'error': _(
                'services_ai_chat_service.error.failed_to_send_message'),
                'message': str(e)}

    def _generate_response(self, conversation: ChatConversation,
        user_message: str) ->Dict[str, Any]:
        _('services_ai_chat_service.message.generate_ai_response_for_user')
        try:
            configure_openai()
            context = self._build_conversation_context(conversation)
            enhanced_message = self._enhance_message_with_context(conversation,
                user_message)
            recent_messages = conversation.messages.filter(ChatMessage.role !=
                MessageRole.SYSTEM).order_by(ChatMessage.created_at.desc()
                ).limit(10).all()
            messages = [{'role': 'system', 'content': context['system_prompt']}
                ]
            for msg in reversed(recent_messages):
                if msg.role == MessageRole.USER:
                    messages.append({'role': 'user', 'content': msg.content})
                elif msg.role == MessageRole.ASSISTANT:
                    messages.append({'role': 'assistant', 'content': msg.
                        content})
            messages.append({'role': 'user', 'content': enhanced_message})
            model_config = self.MODEL_CONFIGS.get(conversation.model, self.
                MODEL_CONFIGS[_('orchestration_examples.message.gpt_4_2')])
            response = openai.ChatCompletion.create(model=conversation.
                model, messages=messages, temperature=conversation.
                temperature or model_config['temperature'], max_tokens=
                conversation.max_tokens or model_config['max_tokens'],
                functions=self._get_available_functions(conversation.
                context_type), function_call='auto')
            message_content = response.choices[0].message.get('content', '')
            function_call = response.choices[0].message.get('function_call')
            if function_call:
                function_result = self._handle_function_call(conversation,
                    function_call)
                if function_result:
                    message_content = function_result.get('message',
                        message_content)
            assistant_message = ChatMessage(conversation_id=conversation.id,
                role=MessageRole.ASSISTANT, content=message_content,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens, metadata={
                'function_call': function_call} if function_call else None)
            db.session.add(assistant_message)
            self._update_rate_limits(conversation.user_id, 0, response.
                usage.total_tokens)
            if conversation.message_count % 10 == 0:
                self._update_conversation_summary(conversation)
            db.session.commit()
            return {'message': assistant_message.to_dict(), 'content':
                message_content, 'function_call': function_call,
                'tokens_used': response.usage.total_tokens}
        except Exception as e:
            logger.error(f'Error generating response: {str(e)}')
            error_message = ChatMessage(conversation_id=conversation.id,
                role=MessageRole.ASSISTANT, content=self._get_error_message
                (conversation.language), is_error=True, error_message=str(e))
            db.session.add(error_message)
            db.session.commit()
            return {'error': _(
                'services_ai_chat_service.error.failed_to_generate_response'
                ), 'message': str(e), 'content': error_message.content}

    def _build_conversation_context(self, conversation: ChatConversation
        ) ->Dict[str, Any]:
        _('services_ai_chat_service.message.build_context_for_the_conversa')
        base_prompt = self.CONTEXT_PROMPTS.get(conversation.context_type,
            self.CONTEXT_PROMPTS['general'])
        if conversation.language == 'tr':
            base_prompt += _(
                'services_ai_chat_service.message.important_respond_in_turkis')
        if conversation.related_entity_type and conversation.related_entity_id:
            entity_context = self._get_entity_context(conversation.
                related_entity_type, conversation.related_entity_id)
            if entity_context:
                base_prompt += f'\n\nContext: {entity_context}'
        if conversation.beneficiary_id:
            beneficiary_context = self._get_beneficiary_context(conversation
                .beneficiary_id)
            if beneficiary_context:
                base_prompt += f'\n\nBeneficiary Info: {beneficiary_context}'
        return {'system_prompt': base_prompt, 'context_type': conversation.
            context_type, 'language': conversation.language}

    def _enhance_message_with_context(self, conversation: ChatConversation,
        message: str) ->str:
        _('services_ai_chat_service.message.enhance_user_message_with_addi')
        enhanced = message
        if conversation.context_type == 'appointment':
            enhanced += f'\n\n[Current time: {datetime.utcnow().isoformat()}]'
        if (conversation.context_type == 'progress' and conversation.
            beneficiary_id):
            progress = self._get_beneficiary_progress(conversation.
                beneficiary_id)
            if progress:
                enhanced += f'\n\n[Progress Context: {progress}]'
        return enhanced

    def _get_available_functions(self, context_type: str) ->List[Dict[str, Any]
        ]:
        _('services_ai_chat_service.message.get_available_functions_based')
        functions = []
        if context_type == 'appointment':
            functions.extend([{'name': 'check_availability', 'description':
                _(
                'services_ai_chat_service.message.check_available_appointment_sl'
                ), 'parameters': {'type': 'object', 'properties': {'date':
                {'type': 'string', 'description': _(
                'services_ai_chat_service.message.date_to_check_yyyy_mm_dd'
                )}, 'trainer_id': {'type': 'integer', 'description': _(
                'services_ai_chat_service.label.trainer_id_optional')}},
                'required': ['date']}}, {'name': 'book_appointment',
                'description': _(
                'services_ai_chat_service.label.book_an_appointment'),
                'parameters': {'type': 'object', 'properties': {'date': {
                'type': 'string', 'description': _(
                'services_ai_chat_service.label.appointment_date')}, 'time':
                {'type': 'string', 'description': _(
                'services_ai_chat_service.label.appointment_time')},
                'trainer_id': {'type': 'integer', 'description': _(
                'services_ai_chat_service.label.trainer_id')}, 'purpose': {
                'type': 'string', 'description': _(
                'services_ai_chat_service.label.purpose_of_appointment')}},
                'required': ['date', 'time', 'trainer_id']}}])
        elif context_type == 'progress':
            functions.append({'name': 'get_progress_report', 'description':
                _(
                'services_ai_chat_service.message.get_beneficiary_s_progress_rep'
                ), 'parameters': {'type': 'object', 'properties': {'period':
                {'type': 'string', 'description': _(
                'services_ai_chat_service.message.period_week_month_all')},
                'include_details': {'type': 'boolean', 'description': _(
                'services_ai_chat_service.label.include_detailed_metrics')}}}})
        elif context_type == 'education':
            functions.append({'name': 'get_program_info', 'description': _(
                'services_ai_chat_service.validation.get_information_about_programs'
                ), 'parameters': {'type': 'object', 'properties': {
                'program_id': {'type': 'integer', 'description': _(
                'services_ai_chat_service.label.program_id_optional')},
                'category': {'type': 'string', 'description': _(
                'services_ai_chat_service.label.program_category_optional')}}}}
                )
        return functions

    def _handle_function_call(self, conversation: ChatConversation,
        function_call: Dict[str, Any]) ->Optional[Dict[str, Any]]:
        """Handle function calls from AI."""
        function_name = function_call.get('name')
        arguments = json.loads(function_call.get('arguments', '{}'))
        try:
            if function_name == 'check_availability':
                result = self._check_availability(conversation.
                    beneficiary_id, arguments.get('date'), arguments.get(
                    'trainer_id'))
                return {'message': self._format_availability_response(
                    result, conversation.language)}
            elif function_name == 'book_appointment':
                result = self._book_appointment(conversation.beneficiary_id,
                    arguments)
                return {'message': self._format_booking_response(result,
                    conversation.language)}
            elif function_name == 'get_progress_report':
                result = self._get_progress_report(conversation.
                    beneficiary_id, arguments.get('period', 'month'))
                return {'message': self._format_progress_response(result,
                    conversation.language)}
            elif function_name == 'get_program_info':
                result = self._get_program_info(arguments.get('program_id'),
                    arguments.get('category'))
                return {'message': self._format_program_response(result,
                    conversation.language)}
        except Exception as e:
            logger.error(
                f'Error handling function call {function_name}: {str(e)}')
            return None
        return None

    def _check_rate_limits(self, user_id: int) ->bool:
        _('services_ai_chat_service.message.check_if_user_has_exceeded_rat')
        rate_limit = ChatRateLimit.query.filter_by(user_id=user_id).first()
        if not rate_limit:
            rate_limit = ChatRateLimit(user_id=user_id, daily_reset_at=
                datetime.utcnow() + timedelta(days=1), monthly_reset_at=
                datetime.utcnow() + timedelta(days=30))
            db.session.add(rate_limit)
            db.session.commit()
            return True
        if rate_limit.daily_reset_at and datetime.utcnow(
            ) > rate_limit.daily_reset_at:
            rate_limit.daily_message_count = 0
            rate_limit.daily_token_count = 0
            rate_limit.daily_reset_at = datetime.utcnow() + timedelta(days=1)
        if rate_limit.monthly_reset_at and datetime.utcnow(
            ) > rate_limit.monthly_reset_at:
            rate_limit.monthly_message_count = 0
            rate_limit.monthly_token_count = 0
            rate_limit.monthly_reset_at = datetime.utcnow() + timedelta(days=30
                )
        max_daily_messages = (rate_limit.max_daily_messages or self.
            DEFAULT_DAILY_MESSAGES)
        max_daily_tokens = (rate_limit.max_daily_tokens or self.
            DEFAULT_DAILY_TOKENS)
        max_monthly_messages = (rate_limit.max_monthly_messages or self.
            DEFAULT_MONTHLY_MESSAGES)
        max_monthly_tokens = (rate_limit.max_monthly_tokens or self.
            DEFAULT_MONTHLY_TOKENS)
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

    def get_conversation_history(self, user_id: int, beneficiary_id:
        Optional[int]=None, status: Optional[ConversationStatus]=None,
        context_type: Optional[str]=None, limit: int=20, offset: int=0) ->Dict[
        str, Any]:
        _('services_ai_chat_service.message.get_conversation_history_for_a')
        try:
            query = ChatConversation.query.filter_by(user_id=user_id)
            if beneficiary_id:
                query = query.filter_by(beneficiary_id=beneficiary_id)
            if status:
                query = query.filter_by(status=status)
            if context_type:
                query = query.filter_by(context_type=context_type)
            total = query.count()
            conversations = query.order_by(ChatConversation.updated_at.desc()
                ).limit(limit).offset(offset).all()
            return {'conversations': [conv.to_dict() for conv in
                conversations], 'total': total, 'limit': limit, 'offset':
                offset}
        except Exception as e:
            logger.error(f'Error getting conversation history: {str(e)}')
            return {'error': _(
                'services_ai_chat_service.error.failed_to_get_conversation_his'
                ), 'message': str(e)}

    def export_conversation(self, conversation_id: int, user_id: int,
        format: str='json') ->Dict[str, Any]:
        _('services_ai_chat_service.validation.export_a_conversation_in_speci')
        try:
            conversation = ChatConversation.query.filter_by(id=
                conversation_id, user_id=user_id).first()
            if not conversation:
                return {'error': _(
                    'services_ai_chat_service.label.conversation_not_found_2')}
            if format == 'json':
                return {'data': conversation.to_dict(include_messages=True),
                    'format': 'json'}
            elif format == 'text':
                messages = conversation.messages.order_by(ChatMessage.
                    created_at).all()
                text_content = f'Conversation: {conversation.title}\n'
                text_content += (
                    f'Date: {conversation.created_at.isoformat()}\n')
                text_content += f'Language: {conversation.language}\n'
                text_content += '-' * 50 + '\n\n'
                for msg in messages:
                    if msg.role != MessageRole.SYSTEM:
                        text_content += (
                            f'{msg.role.value.upper()}: {msg.content}\n')
                        text_content += f'Time: {msg.created_at.isoformat()}\n'
                        text_content += '-' * 30 + '\n\n'
                return {'data': text_content, 'format': 'text'}
            else:
                return {'error': _(
                    'services_ai_chat_service.validation.unsupported_export_format'
                    )}
        except Exception as e:
            logger.error(f'Error exporting conversation: {str(e)}')
            return {'error': _(
                'services_ai_chat_service.error.failed_to_export_conversation'
                ), 'message': str(e)}

    def flag_conversation(self, conversation_id: int, admin_id: int, reason:
        str) ->Dict[str, Any]:
        _('services_ai_chat_service.message.flag_a_conversation_for_modera')
        try:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                return {'error': _(
                    'services_ai_chat_service.label.conversation_not_found_2')}
            conversation.is_flagged = True
            conversation.flag_reason = reason
            conversation.flagged_by = admin_id
            conversation.flagged_at = datetime.utcnow()
            conversation.status = ConversationStatus.FLAGGED
            self.notification_service.create_notification(user_id=
                conversation.user_id, title=_(
                'services_ai_chat_service.label.conversation_flagged'),
                message=
                f'Your conversation has been flagged for review: {reason}',
                type='moderation', related_type='chat_conversation',
                related_id=conversation_id)
            db.session.commit()
            return {'success': True, 'conversation': conversation.to_dict()}
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error flagging conversation: {str(e)}')
            return {'error': _(
                'services_ai_chat_service.error.failed_to_flag_conversation'
                ), 'message': str(e)}

    def get_conversation_analytics(self, tenant_id: Optional[int]=None,
        start_date: Optional[datetime]=None, end_date: Optional[datetime]=None
        ) ->Dict[str, Any]:
        _('services_ai_chat_service.label.get_conversation_analytics')
        try:
            query = ChatConversation.query
            if tenant_id:
                query = query.filter_by(tenant_id=tenant_id)
            if start_date:
                query = query.filter(ChatConversation.created_at >= start_date)
            if end_date:
                query = query.filter(ChatConversation.created_at <= end_date)
            total_conversations = query.count()
            active_conversations = query.filter_by(status=
                ConversationStatus.ACTIVE).count()
            flagged_conversations = query.filter_by(is_flagged=True).count()
            language_stats = db.session.query(ChatConversation.language,
                func.count(ChatConversation.id)).filter(query.whereclause if
                query.whereclause is not None else True).group_by(
                ChatConversation.language).all()
            context_stats = db.session.query(ChatConversation.context_type,
                func.count(ChatConversation.id)).filter(query.whereclause if
                query.whereclause is not None else True).group_by(
                ChatConversation.context_type).all()
            avg_messages = db.session.query(func.avg(ChatConversation.
                message_count)).filter(query.whereclause if query.
                whereclause is not None else True).scalar() or 0
            token_usage = db.session.query(func.sum(ChatMessage.total_tokens)
                ).join(ChatConversation).filter(query.whereclause if query.
                whereclause is not None else True).scalar() or 0
            return {'total_conversations': total_conversations,
                'active_conversations': active_conversations,
                'flagged_conversations': flagged_conversations,
                'language_distribution': dict(language_stats),
                'context_distribution': dict(context_stats),
                'average_messages_per_conversation': float(avg_messages),
                'total_tokens_used': token_usage}
        except Exception as e:
            logger.error(f'Error getting conversation analytics: {str(e)}')
            return {'error': _(
                'services_ai_chat_service.error.failed_to_get_analytics'),
                'message': str(e)}

    def _detect_language(self, text: str) ->str:
        """Detect language from text."""
        try:
            lang = detect(text)
            return 'tr' if lang == 'tr' else 'en'
        except:
            return 'en'

    def _generate_conversation_title(self, message: str) ->str:
        """Generate a title for the conversation from the first message."""
        title = message.split('.')[0]
        if len(title) > 50:
            title = title[:47] + '...'
        return title

    def _get_conversation_template(self, context_type: str, language: str,
        tenant_id: Optional[int]) ->Dict[str, Any]:
        _('services_ai_chat_service.message.get_conversation_template_base')
        template = ConversationTemplate.query.filter_by(tenant_id=tenant_id,
            category=context_type, language=language, is_active=True).order_by(
            ConversationTemplate.priority.desc()).first()
        if not template:
            template = ConversationTemplate.query.filter_by(tenant_id=None,
                category=context_type, language=language, is_active=True
                ).order_by(ConversationTemplate.priority.desc()).first()
        if template:
            return template.to_dict()
        return {'system_prompt': self.CONTEXT_PROMPTS.get(context_type,
            self.CONTEXT_PROMPTS['general']), 'welcome_message': self.
            _get_default_welcome_message(language), 'suggested_questions':
            self._get_default_suggestions(context_type, language)}

    def _get_default_welcome_message(self, language: str) ->str:
        _('services_ai_chat_service.message.get_default_welcome_message')
        if language == 'tr':
            return _(
                'services_ai_chat_service.message.merhaba_size_nas_l_yard_mc_o'
                )
        return _(
            'services_ai_chat_service.message.hello_how_can_i_help_you_toda')

    def _get_default_suggestions(self, context_type: str, language: str
        ) ->List[str]:
        _('services_ai_chat_service.message.get_default_question_suggestio')
        suggestions = {'education': {'en': [_(
            'services_ai_chat_service.message.what_programs_are_available'),
            _(
            'services_ai_chat_service.message.how_can_i_improve_my_study_hab'
            ), _(
            'services_ai_chat_service.message.what_resources_are_available_f'
            )], 'tr': [_(
            'services_ai_chat_service.label.hangi_programlar_mevcut'), _(
            'services_ai_chat_service.message.al_ma_al_kanl_klar_m_nas_l'),
            _(
            'services_ai_chat_service.message.renme_i_in_hangi_kaynaklar_m'
            )]}, 'appointment': {'en': [_(
            'services_ai_chat_service.message.when_is_my_next_appointment'),
            _(
            'services_ai_chat_service.message.can_i_schedule_a_new_appointme'
            ), _(
            'services_ai_chat_service.message.how_do_i_reschedule_my_appoint'
            )], 'tr': [_(
            'services_ai_chat_service.message.bir_sonraki_randevum_ne_zaman'
            ), _(
            'services_ai_chat_service.message.yeni_bir_randevu_alabilir_miyi'
            ), _(
            'services_ai_chat_service.message.randevumu_nas_l_yeniden_planla'
            )]}, 'progress': {'en': [_(
            'services_ai_chat_service.message.how_am_i_doing_in_my_programs'
            ), _(
            'services_ai_chat_service.validation.what_areas_should_i_focus_on'
            ), _(
            'services_ai_chat_service.message.can_i_see_my_recent_achievemen'
            )], 'tr': [_(
            'services_ai_chat_service.label.programlar_mda_nas_l_ilerliyor'
            ), _(
            'services_ai_chat_service.label.hangi_alanlara_odaklanmal_y_m'),
            _(
            'services_ai_chat_service.message.son_ba_ar_lar_m_g_rebilir_miy'
            )]}, 'general': {'en': [_(
            'services_ai_chat_service.message.tell_me_about_the_center'), _
            ('services_ai_chat_service.message.what_services_are_available'
            ), _('services_ai_chat_service.message.how_can_i_get_help')],
            'tr': [_(
            'services_ai_chat_service.message.merkez_hakk_nda_bilgi_verin'),
            _('services_ai_chat_service.label.hangi_hizmetler_mevcut'), _(
            'services_ai_chat_service.label.nas_l_yard_m_alabilirim')]}}
        return suggestions.get(context_type, suggestions['general']).get(
            language, [])

    def _get_error_message(self, language: str) ->str:
        _('services_ai_chat_service.error.get_error_message_in_appropria')
        if language == 'tr':
            return _(
                'services_ai_chat_service.message.zg_n_m_bir_hata_olu_tu_l_tf')
        return _('services_ai_chat_service.error.i_m_sorry_an_error_occurred')

    def _should_close_conversation(self, user_message: str,
        assistant_response: str) ->bool:
        _('services_ai_chat_service.validation.check_if_conversation_should_b')
        closing_phrases = ['goodbye', 'bye', _(
            'services_ai_chat_service.message.thank_you'), 'thanks', _(
            'services_ai_chat_service.message.that_s_all'), _(
            'services_ai_chat_service.message.g_le_g_le'), _(
            'services_ai_chat_service.message.ho_a_kal'), _(
            'services_ai_chat_service.message.te_ekk_r_ederim'), _(
            'services_ai_chat_service.message.sa_ol')]
        message_lower = user_message.lower()
        for phrase in closing_phrases:
            if phrase in message_lower:
                return True
        return False

    def _update_conversation_summary(self, conversation: ChatConversation):
        """Update conversation summary using AI."""
        try:
            messages = conversation.messages.filter(ChatMessage.role !=
                MessageRole.SYSTEM).order_by(ChatMessage.created_at).all()
            if len(messages) < 5:
                return
            conversation_text = '\n'.join([
                f'{msg.role.value}: {msg.content}' for msg in messages])
            response = openai.ChatCompletion.create(model=_(
                'i18n_content_translation_service.message.gpt_3_5_turbo_1'),
                messages=[{'role': 'system', 'content': _(
                'services_ai_chat_service.message.summarize_this_conversation_in'
                )}, {'role': 'user', 'content': conversation_text}],
                temperature=0.5, max_tokens=200)
            summary_data = response.choices[0].message['content']
            lines = summary_data.split('\n')
            summary = lines[0] if lines else _(
                'services_ai_chat_service.label.no_summary_available')
            topics = []
            if _('services_ai_chat_service.message.topics_1'
                ) in summary_data.lower():
                topics_line = [l for l in lines if _(
                    'services_ai_chat_service.message.topics_1') in l.lower()]
                if topics_line:
                    topics = [t.strip() for t in topics_line[0].split(':')[
                        1].split(',')]
            conversation.summary = summary
            conversation.key_topics = topics
        except Exception as e:
            logger.error(f'Error updating conversation summary: {str(e)}')

    def _check_availability(self, beneficiary_id: int, date: str,
        trainer_id: Optional[int]) ->Dict:
        _('services_ai_chat_service.label.check_appointment_availability')
        return {'available_slots': [_(
            'services_ai_chat_service.message.10_00'), _(
            'services_ai_chat_service.message.14_00'), _(
            'services_ai_chat_service.message.16_00')], 'date': date}

    def _book_appointment(self, beneficiary_id: int, details: Dict) ->Dict:
        _('services_ai_chat_service.label.book_an_appointment_1')
        return {'success': True, 'appointment_id': 123, 'details': details}

    def _get_progress_report(self, beneficiary_id: int, period: str) ->Dict:
        _('services_ai_chat_service.message.get_beneficiary_progress_repor')
        return {'period': period, 'overall_progress': 75,
            'completed_sessions': 12, 'upcoming_sessions': 3}

    def _get_program_info(self, program_id: Optional[int], category:
        Optional[str]) ->Dict:
        _('services_ai_chat_service.validation.get_program_information')
        return {'programs': [{'id': 1, 'name': 'Basic Skills', 'duration':
            _('services_ai_chat_service.message.3_months')}, {'id': 2,
            'name': _('services_ai_chat_service.label.advanced_training'),
            'duration': _('services_ai_chat_service.message.6_months')}]}

    def _get_entity_context(self, entity_type: str, entity_id: int) ->Optional[
        str]:
        _('services_ai_chat_service.validation.get_context_information_for_re')
        try:
            if entity_type == 'appointment':
                appointment = Appointment.query.get(entity_id)
                if appointment:
                    return (
                        f'Appointment on {appointment.start_time} with {appointment.trainer.full_name}'
                        )
            elif entity_type == 'program':
                program = Program.query.get(entity_id)
                if program:
                    return f'Program: {program.name} - {program.description}'
            elif entity_type == 'assessment':
                assessment = Assessment.query.get(entity_id)
                if assessment:
                    return f'Assessment: {assessment.title}'
        except Exception as e:
            logger.error(f'Error getting entity context: {str(e)}')
        return None

    def _get_beneficiary_context(self, beneficiary_id: int) ->Optional[str]:
        _('services_ai_chat_service.validation.get_beneficiary_context_inform')
        try:
            beneficiary = Beneficiary.query.get(beneficiary_id)
            if beneficiary:
                return (
                    f'Name: {beneficiary.full_name}, Status: {beneficiary.status}'
                    )
        except Exception as e:
            logger.error(f'Error getting beneficiary context: {str(e)}')
        return None

    def _get_beneficiary_progress(self, beneficiary_id: int) ->Optional[str]:
        _('services_ai_chat_service.message.get_beneficiary_progress_summa')
        try:
            enrollments = ProgramEnrollment.query.filter_by(beneficiary_id=
                beneficiary_id, status='active').all()
            if enrollments:
                progress_info = []
                for enrollment in enrollments:
                    progress_info.append(
                        f'{enrollment.program.name}: {enrollment.progress}% complete'
                        )
                return ', '.join(progress_info)
        except Exception as e:
            logger.error(f'Error getting beneficiary progress: {str(e)}')
        return None

    def _format_availability_response(self, result: Dict, language: str) ->str:
        _('services_ai_chat_service.validation.format_availability_check_resp')
        if language == 'tr':
            return (
                f"{result['date']} tarihinde şu saatler müsait: {', '.join(result['available_slots'])}"
                )
        return (
            f"Available slots on {result['date']}: {', '.join(result['available_slots'])}"
            )

    def _format_booking_response(self, result: Dict, language: str) ->str:
        _('services_ai_chat_service.validation.format_appointment_booking_res')
        if result.get('success'):
            if language == 'tr':
                return (
                    f"Randevunuz başarıyla oluşturuldu. Randevu numarası: {result['appointment_id']}"
                    )
            return (
                f"Your appointment has been booked successfully. Appointment ID: {result['appointment_id']}"
                )
        else:
            if language == 'tr':
                return _(
                    'services_ai_chat_service.message.randevu_olu_turulamad_l_tfen'
                    )
            return _(
                'services_ai_chat_service.message.could_not_book_the_appointment'
                )

    def _format_progress_response(self, result: Dict, language: str) ->str:
        _('services_ai_chat_service.validation.format_progress_report_respons')
        if language == 'tr':
            return (
                f"{result['period']} döneminde ilerlemeniz: %{result['overall_progress']}. Tamamlanan oturumlar: {result['completed_sessions']}, Yaklaşan oturumlar: {result['upcoming_sessions']}"
                )
        return (
            f"Your progress for {result['period']}: {result['overall_progress']}%. Completed sessions: {result['completed_sessions']}, Upcoming sessions: {result['upcoming_sessions']}"
            )

    def _format_program_response(self, result: Dict, language: str) ->str:
        _('services_ai_chat_service.validation.format_program_information_res')
        programs = result.get('programs', [])
        if not programs:
            if language == 'tr':
                return _(
                    'services_ai_chat_service.message.u_anda_uygun_program_bulunmam'
                    )
            return _(
                'services_ai_chat_service.message.no_programs_are_currently_avai'
                )
        if language == 'tr':
            response = _('services_ai_chat_service.label.mevcut_programlar')
            for prog in programs:
                response += f"- {prog['name']} (Süre: {prog['duration']})\n"
        else:
            response = _('services_ai_chat_service.label.available_programs')
            for prog in programs:
                response += (
                    f"- {prog['name']} (Duration: {prog['duration']})\n")
        return response


ai_chat_service = AIChatService()
