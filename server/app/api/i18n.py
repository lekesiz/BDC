"""Internationalization API endpoints."""

import json
import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from sqlalchemy import and_, or_
from datetime import datetime

from app.extensions import db
from app.models.i18n import (
    Language, MultilingualContent, TranslationProject, 
    TranslationWorkflow, UserLanguagePreference
)
from app.models.user import User
from app.services.i18n import (
    LanguageDetectionService, TranslationService, 
    LocaleService, ContentTranslationService
)
from app.services.i18n.content_translation_service import TranslationRequest
from app.utils.decorators import require_role

logger = logging.getLogger(__name__)

# Create blueprint
i18n_bp = Blueprint('i18n', __name__, url_prefix='/api/i18n')

# Initialize services
language_detection_service = LanguageDetectionService()
translation_service = TranslationService()
locale_service = LocaleService()
content_translation_service = ContentTranslationService()


# Schemas for request validation
class LanguageSchema(Schema):
    """Schema for language data."""
    code = fields.Str(required=True, validate=lambda x: len(x) <= 10)
    name = fields.Str(required=True, validate=lambda x: len(x) <= 100)
    native_name = fields.Str(required=True, validate=lambda x: len(x) <= 100)
    direction = fields.Str(missing='ltr', validate=lambda x: x in ['ltr', 'rtl'])
    region = fields.Str(missing=None, validate=lambda x: x is None or len(x) <= 10)
    is_active = fields.Bool(missing=True)
    flag_icon = fields.Str(missing=None)
    sort_order = fields.Int(missing=0)


class TranslationRequestSchema(Schema):
    """Schema for translation requests."""
    content = fields.Str(required=True)
    source_language = fields.Str(required=True)
    target_language = fields.Str(required=True)
    content_type = fields.Str(missing='text', validate=lambda x: x in ['text', 'html', 'markdown'])
    context = fields.Str(missing=None)
    priority = fields.Str(missing='normal', validate=lambda x: x in ['low', 'normal', 'high', 'urgent'])


class MultilingualContentSchema(Schema):
    """Schema for multilingual content."""
    entity_type = fields.Str(required=True)
    entity_id = fields.Str(required=True)
    field_name = fields.Str(required=True)
    language_code = fields.Str(required=True)
    content = fields.Str(required=True)
    content_type = fields.Str(missing='text')
    is_original = fields.Bool(missing=False)
    translation_method = fields.Str(missing=None)


class UserLanguagePreferenceSchema(Schema):
    """Schema for user language preferences."""
    primary_language = fields.Str(required=True)
    secondary_languages = fields.List(fields.Str(), missing=[])
    enable_auto_detection = fields.Bool(missing=True)
    detect_from_browser = fields.Bool(missing=True)
    detect_from_content = fields.Bool(missing=False)
    detect_from_location = fields.Bool(missing=False)
    fallback_language = fields.Str(missing='en')
    show_original_content = fields.Bool(missing=False)
    auto_translate_content = fields.Bool(missing=True)


# Language Management Endpoints

@i18n_bp.route('/languages', methods=['GET'])
def get_languages():
    """Get all supported languages."""
    try:
        languages = Language.query.filter_by(is_active=True).order_by(Language.sort_order, Language.name).all()
        
        return jsonify({
            'success': True,
            'data': [lang.to_dict() for lang in languages]
        })
        
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return jsonify({'success': False, 'error': 'Failed to get languages'}), 500


@i18n_bp.route('/languages', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def create_language():
    """Create a new language."""
    try:
        schema = LanguageSchema()
        data = schema.load(request.get_json())
        
        # Check if language code already exists
        existing = Language.query.filter_by(code=data['code']).first()
        if existing:
            return jsonify({
                'success': False, 
                'error': 'Language code already exists'
            }), 400
        
        language = Language(**data)
        db.session.add(language)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': language.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except Exception as e:
        logger.error(f"Error creating language: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create language'}), 500


@i18n_bp.route('/languages/<language_code>', methods=['PUT'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def update_language(language_code):
    """Update a language."""
    try:
        language = Language.query.filter_by(code=language_code).first()
        if not language:
            return jsonify({'success': False, 'error': 'Language not found'}), 404
        
        schema = LanguageSchema()
        data = schema.load(request.get_json())
        
        for key, value in data.items():
            setattr(language, key, value)
        
        language.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': language.to_dict()
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except Exception as e:
        logger.error(f"Error updating language: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to update language'}), 500


# Language Detection Endpoints

@i18n_bp.route('/detect-language', methods=['POST'])
def detect_language():
    """Detect language from various sources."""
    try:
        data = request.get_json()
        
        result = language_detection_service.detect_best_language(
            user_preference=data.get('user_preference'),
            accept_language=data.get('accept_language'),
            content=data.get('content'),
            country_code=data.get('country_code')
        )
        
        language_info = language_detection_service.get_language_info(result)
        
        return jsonify({
            'success': True,
            'data': {
                'detected_language': result,
                'language_info': language_info
            }
        })
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        return jsonify({'success': False, 'error': 'Failed to detect language'}), 500


@i18n_bp.route('/language-info/<language_code>', methods=['GET'])
def get_language_info(language_code):
    """Get comprehensive language information."""
    try:
        language_info = language_detection_service.get_language_info(language_code)
        locale_info = locale_service.get_locale_info(language_code)
        calendar_data = locale_service.get_calendar_data(language_code)
        
        return jsonify({
            'success': True,
            'data': {
                'language': language_info,
                'locale': locale_info,
                'calendar': calendar_data
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting language info: {e}")
        return jsonify({'success': False, 'error': 'Failed to get language info'}), 500


# Translation Endpoints

@i18n_bp.route('/translate', methods=['POST'])
@jwt_required()
def translate_text():
    """Translate text using translation service."""
    try:
        schema = TranslationRequestSchema()
        data = schema.load(request.get_json())
        
        user_id = get_jwt_identity()
        
        # Create translation request
        request_obj = TranslationRequest(
            content=data['content'],
            source_language=data['source_language'],
            target_language=data['target_language'],
            content_type=data['content_type'],
            context=data.get('context'),
            priority=data['priority']
        )
        
        # Translate content
        result = content_translation_service.translate_content(request_obj, user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'translated_content': result.translated_content,
                'source_language': result.source_language,
                'target_language': result.target_language,
                'confidence': result.confidence,
                'method': result.method,
                'metadata': result.metadata
            }
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except Exception as e:
        logger.error(f"Error translating text: {e}")
        return jsonify({'success': False, 'error': 'Failed to translate text'}), 500


@i18n_bp.route('/translations/<key>', methods=['GET'])
def get_translation(key):
    """Get translation for a specific key."""
    try:
        language = request.args.get('language', 'en')
        
        result = translation_service.translate(key, language)
        
        return jsonify({
            'success': True,
            'data': {
                'key': key,
                'text': result.text,
                'language': result.language,
                'source': result.source,
                'confidence': result.confidence
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting translation: {e}")
        return jsonify({'success': False, 'error': 'Failed to get translation'}), 500


@i18n_bp.route('/translations', methods=['GET'])
def get_translations():
    """Get translation dictionary for a language."""
    try:
        language = request.args.get('language', 'en')
        section = request.args.get('section')
        
        translations = translation_service.get_translation_dict(language, section)
        
        return jsonify({
            'success': True,
            'data': {
                'language': language,
                'section': section,
                'translations': translations
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting translations: {e}")
        return jsonify({'success': False, 'error': 'Failed to get translations'}), 500


# Content Management Endpoints

@i18n_bp.route('/content', methods=['POST'])
@jwt_required()
def create_multilingual_content():
    """Create multilingual content."""
    try:
        schema = MultilingualContentSchema()
        data = schema.load(request.get_json())
        
        user_id = get_jwt_identity()
        
        content = MultilingualContent(
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            field_name=data['field_name'],
            language_code=data['language_code'],
            content=data['content'],
            content_type=data['content_type'],
            is_original=data['is_original'],
            translation_method=data.get('translation_method'),
            created_by=user_id,
            updated_by=user_id
        )
        
        db.session.add(content)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': content.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except Exception as e:
        logger.error(f"Error creating multilingual content: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to create content'}), 500


@i18n_bp.route('/content/<entity_type>/<entity_id>', methods=['GET'])
def get_multilingual_content(entity_type, entity_id):
    """Get multilingual content for an entity."""
    try:
        language = request.args.get('language')
        field_name = request.args.get('field')
        
        query = MultilingualContent.query.filter_by(
            entity_type=entity_type,
            entity_id=entity_id,
            is_current=True
        )
        
        if language:
            query = query.filter_by(language_code=language)
        
        if field_name:
            query = query.filter_by(field_name=field_name)
        
        content_items = query.all()
        
        # Group by field and language
        result = {}
        for item in content_items:
            if item.field_name not in result:
                result[item.field_name] = {}
            result[item.field_name][item.language_code] = item.to_dict()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error getting multilingual content: {e}")
        return jsonify({'success': False, 'error': 'Failed to get content'}), 500


@i18n_bp.route('/content/<int:content_id>', methods=['PUT'])
@jwt_required()
def update_multilingual_content(content_id):
    """Update multilingual content."""
    try:
        content = MultilingualContent.query.get(content_id)
        if not content:
            return jsonify({'success': False, 'error': 'Content not found'}), 404
        
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Update content
        if 'content' in data:
            content.content = data['content']
        if 'translation_status' in data:
            content.translation_status = data['translation_status']
        if 'quality_score' in data:
            content.quality_score = data['quality_score']
        
        content.updated_by = user_id
        content.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': content.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error updating multilingual content: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to update content'}), 500


# User Language Preferences

@i18n_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_user_language_preferences():
    """Get user's language preferences."""
    try:
        user_id = get_jwt_identity()
        
        preferences = UserLanguagePreference.query.filter_by(user_id=user_id).first()
        
        if not preferences:
            # Create default preferences
            preferences = UserLanguagePreference(
                user_id=user_id,
                primary_language='en',
                secondary_languages='[]'
            )
            db.session.add(preferences)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'data': preferences.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting user language preferences: {e}")
        return jsonify({'success': False, 'error': 'Failed to get preferences'}), 500


@i18n_bp.route('/preferences', methods=['PUT'])
@jwt_required()
def update_user_language_preferences():
    """Update user's language preferences."""
    try:
        schema = UserLanguagePreferenceSchema()
        data = schema.load(request.get_json())
        
        user_id = get_jwt_identity()
        
        preferences = UserLanguagePreference.query.filter_by(user_id=user_id).first()
        
        if not preferences:
            preferences = UserLanguagePreference(user_id=user_id)
            db.session.add(preferences)
        
        # Update preferences
        preferences.primary_language = data['primary_language']
        preferences.secondary_languages = json.dumps(data['secondary_languages'])
        preferences.enable_auto_detection = data['enable_auto_detection']
        preferences.detect_from_browser = data['detect_from_browser']
        preferences.detect_from_content = data['detect_from_content']
        preferences.detect_from_location = data['detect_from_location']
        preferences.fallback_language = data['fallback_language']
        preferences.show_original_content = data['show_original_content']
        preferences.auto_translate_content = data['auto_translate_content']
        preferences.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': preferences.to_dict()
        })
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': e.messages}), 400
    except Exception as e:
        logger.error(f"Error updating user language preferences: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to update preferences'}), 500


# Locale and Formatting Endpoints

@i18n_bp.route('/locale/<language_code>/format', methods=['POST'])
def format_locale_data():
    """Format data according to locale."""
    try:
        data = request.get_json()
        format_type = data.get('type')
        value = data.get('value')
        options = data.get('options', {})
        
        if format_type == 'date':
            from datetime import datetime
            date_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
            result = locale_service.format_date(date_obj.date(), language_code, options.get('format', 'medium'))
        elif format_type == 'datetime':
            from datetime import datetime
            datetime_obj = datetime.fromisoformat(value.replace('Z', '+00:00'))
            result = locale_service.format_datetime(datetime_obj, language_code, options.get('format', 'medium'))
        elif format_type == 'currency':
            result = locale_service.format_currency(value, language_code, options.get('currency'))
        elif format_type == 'number':
            result = locale_service.format_number(value, language_code, options.get('decimal_places'))
        elif format_type == 'percent':
            result = locale_service.format_percent(value, language_code, options.get('decimal_places', 1))
        else:
            return jsonify({'success': False, 'error': 'Invalid format type'}), 400
        
        return jsonify({
            'success': True,
            'data': {
                'formatted_value': result,
                'language_code': language_code,
                'format_type': format_type
            }
        })
        
    except Exception as e:
        logger.error(f"Error formatting locale data: {e}")
        return jsonify({'success': False, 'error': 'Failed to format data'}), 500


# Translation Statistics

@i18n_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_translation_stats():
    """Get translation statistics."""
    try:
        language = request.args.get('language')
        
        stats = content_translation_service.get_translation_stats(language)
        
        # Additional stats
        total_languages = Language.query.filter_by(is_active=True).count()
        total_content_items = MultilingualContent.query.filter_by(is_current=True).count()
        
        stats.update({
            'total_languages': total_languages,
            'total_content_items': total_content_items
        })
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting translation stats: {e}")
        return jsonify({'success': False, 'error': 'Failed to get stats'}), 500


# Bulk Operations

@i18n_bp.route('/bulk-translate', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin', 'trainer'])
def bulk_translate():
    """Bulk translate content items."""
    try:
        data = request.get_json()
        content_items = data.get('content_items', [])
        target_languages = data.get('target_languages', [])
        
        user_id = get_jwt_identity()
        
        result = content_translation_service.bulk_translate_content(
            content_items, target_languages, user_id
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in bulk translate: {e}")
        return jsonify({'success': False, 'error': 'Failed to bulk translate'}), 500


# Export/Import

@i18n_bp.route('/export/<language_code>', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def export_translations(language_code):
    """Export translations for a language."""
    try:
        translations = translation_service.get_translation_dict(language_code)
        
        return jsonify({
            'success': True,
            'data': {
                'language_code': language_code,
                'translations': translations,
                'exported_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error exporting translations: {e}")
        return jsonify({'success': False, 'error': 'Failed to export translations'}), 500


@i18n_bp.route('/import/<language_code>', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'tenant_admin'])
def import_translations(language_code):
    """Import translations for a language."""
    try:
        data = request.get_json()
        translations = data.get('translations', {})
        
        # Validate and import translations
        for key, value in translations.items():
            translation_service.update_translation(key, language_code, value, save_to_file=False)
        
        # Save all changes to file
        translation_service._save_translation_file(language_code)
        
        return jsonify({
            'success': True,
            'data': {
                'imported_count': len(translations),
                'language_code': language_code
            }
        })
        
    except Exception as e:
        logger.error(f"Error importing translations: {e}")
        return jsonify({'success': False, 'error': 'Failed to import translations'}), 500