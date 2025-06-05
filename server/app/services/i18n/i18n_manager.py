"""Comprehensive internationalization manager service."""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy import and_, or_, func

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
from app.utils.cache import cache_manager

logger = logging.getLogger(__name__)


class I18nManager:
    """Comprehensive internationalization manager."""
    
    def __init__(self):
        """Initialize I18n Manager."""
        self.language_detection_service = LanguageDetectionService()
        self.translation_service = TranslationService()
        self.locale_service = LocaleService()
        self.content_translation_service = ContentTranslationService()
        
        # Cache timeout settings
        self.cache_timeout = 3600  # 1 hour
        self.long_cache_timeout = 86400  # 24 hours
    
    # Language Management
    
    def get_active_languages(self) -> List[Dict]:
        """Get all active languages."""
        try:
            languages = Language.query.filter_by(is_active=True).order_by(
                Language.sort_order, Language.name
            ).all()
            
            return [lang.to_dict() for lang in languages]
            
        except Exception as e:
            logger.error(f"Error getting active languages: {e}")
            return []
    
    def create_language(self, language_data: Dict) -> Optional[Language]:
        """Create a new language."""
        try:
            language = Language(**language_data)
            db.session.add(language)
            db.session.commit()
            
            # Clear cache
            cache_manager.delete_pattern('languages_*')
            
            return language
            
        except Exception as e:
            logger.error(f"Error creating language: {e}")
            db.session.rollback()
            return None
    
    def update_language(self, language_code: str, update_data: Dict) -> Optional[Language]:
        """Update an existing language."""
        try:
            language = Language.query.filter_by(code=language_code).first()
            if not language:
                return None
            
            for key, value in update_data.items():
                setattr(language, key, value)
            
            language.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Clear cache
            cache_manager.delete_pattern('languages_*')
            
            return language
            
        except Exception as e:
            logger.error(f"Error updating language: {e}")
            db.session.rollback()
            return None
    
    # Content Localization
    
    def create_multilingual_content(self, entity_type: str, entity_id: str, 
                                  field_name: str, content_data: Dict[str, str],
                                  user_id: Optional[int] = None) -> List[MultilingualContent]:
        """
        Create multilingual content for an entity.
        
        Args:
            entity_type: Type of entity (e.g., 'program', 'document')
            entity_id: ID of the entity
            field_name: Name of the field being localized
            content_data: Dictionary of {language_code: content}
            user_id: ID of user creating content
            
        Returns:
            List of created MultilingualContent objects
        """
        try:
            created_content = []
            
            for language_code, content in content_data.items():
                # Check if content already exists
                existing = MultilingualContent.query.filter_by(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    field_name=field_name,
                    language_code=language_code,
                    is_current=True
                ).first()
                
                if existing:
                    # Update existing content
                    existing.content = content
                    existing.updated_by = user_id
                    existing.updated_at = datetime.utcnow()
                    created_content.append(existing)
                else:
                    # Create new content
                    ml_content = MultilingualContent(
                        entity_type=entity_type,
                        entity_id=entity_id,
                        field_name=field_name,
                        language_code=language_code,
                        content=content,
                        is_original=(language_code == 'en'),  # Assume English is original
                        created_by=user_id,
                        updated_by=user_id
                    )
                    db.session.add(ml_content)
                    created_content.append(ml_content)
            
            db.session.commit()
            return created_content
            
        except Exception as e:
            logger.error(f"Error creating multilingual content: {e}")
            db.session.rollback()
            return []
    
    def get_multilingual_content(self, entity_type: str, entity_id: str, 
                               language_code: Optional[str] = None,
                               field_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get multilingual content for an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            language_code: Optional language filter
            field_name: Optional field filter
            
        Returns:
            Dictionary of content organized by field and language
        """
        try:
            query = MultilingualContent.query.filter_by(
                entity_type=entity_type,
                entity_id=entity_id,
                is_current=True
            )
            
            if language_code:
                query = query.filter_by(language_code=language_code)
            
            if field_name:
                query = query.filter_by(field_name=field_name)
            
            content_items = query.all()
            
            # Organize by field and language
            result = {}
            for item in content_items:
                if item.field_name not in result:
                    result[item.field_name] = {}
                result[item.field_name][item.language_code] = item.to_dict()
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting multilingual content: {e}")
            return {}
    
    def translate_entity_content(self, entity_type: str, entity_id: str,
                               source_language: str, target_languages: List[str],
                               user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Translate all content for an entity to target languages.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            source_language: Source language code
            target_languages: List of target language codes
            user_id: ID of user requesting translation
            
        Returns:
            Translation results
        """
        try:
            # Get source content
            source_content = MultilingualContent.query.filter_by(
                entity_type=entity_type,
                entity_id=entity_id,
                language_code=source_language,
                is_current=True
            ).all()
            
            if not source_content:
                return {'error': 'No source content found'}
            
            results = {
                'success_count': 0,
                'error_count': 0,
                'translations': []
            }
            
            for content_item in source_content:
                for target_lang in target_languages:
                    try:
                        # Create translation request
                        request = TranslationRequest(
                            content=content_item.content,
                            source_language=source_language,
                            target_language=target_lang,
                            content_type=content_item.content_type,
                            context=f"{entity_type}:{entity_id}:{content_item.field_name}"
                        )
                        
                        # Translate content
                        response = self.content_translation_service.translate_content(request, user_id)
                        
                        # Store translated content
                        translated_content = MultilingualContent(
                            entity_type=entity_type,
                            entity_id=entity_id,
                            field_name=content_item.field_name,
                            language_code=target_lang,
                            content=response.translated_content,
                            content_type=content_item.content_type,
                            translation_method=response.method,
                            quality_score=response.confidence,
                            translation_status='translated' if response.confidence > 0.8 else 'needs_review',
                            translated_by=user_id,
                            translated_at=datetime.utcnow(),
                            created_by=user_id,
                            updated_by=user_id
                        )
                        
                        db.session.add(translated_content)
                        results['success_count'] += 1
                        results['translations'].append(translated_content.to_dict())
                        
                    except Exception as e:
                        logger.error(f"Error translating field {content_item.field_name} to {target_lang}: {e}")
                        results['error_count'] += 1
            
            db.session.commit()
            return results
            
        except Exception as e:
            logger.error(f"Error translating entity content: {e}")
            db.session.rollback()
            return {'error': str(e)}
    
    # User Language Management
    
    def get_user_language_preferences(self, user_id: int) -> Optional[UserLanguagePreference]:
        """Get user's language preferences."""
        try:
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
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error getting user language preferences: {e}")
            return None
    
    def update_user_language_preferences(self, user_id: int, preferences_data: Dict) -> Optional[UserLanguagePreference]:
        """Update user's language preferences."""
        try:
            preferences = self.get_user_language_preferences(user_id)
            if not preferences:
                return None
            
            # Update preferences
            for key, value in preferences_data.items():
                if hasattr(preferences, key):
                    if key == 'secondary_languages':
                        setattr(preferences, key, json.dumps(value))
                    else:
                        setattr(preferences, key, value)
            
            preferences.updated_at = datetime.utcnow()
            db.session.commit()
            
            return preferences
            
        except Exception as e:
            logger.error(f"Error updating user language preferences: {e}")
            db.session.rollback()
            return None
    
    def detect_user_language(self, user_id: Optional[int] = None, 
                           accept_language: Optional[str] = None,
                           content: Optional[str] = None,
                           country_code: Optional[str] = None) -> str:
        """Detect the best language for a user."""
        try:
            user_preference = None
            
            # Get user preference if user is authenticated
            if user_id:
                preferences = self.get_user_language_preferences(user_id)
                if preferences and preferences.enable_auto_detection:
                    user_preference = preferences.primary_language
            
            # Use language detection service
            return self.language_detection_service.detect_best_language(
                user_preference=user_preference,
                accept_language=accept_language,
                content=content,
                country_code=country_code
            )
            
        except Exception as e:
            logger.error(f"Error detecting user language: {e}")
            return self.language_detection_service.DEFAULT_LANGUAGE
    
    # Translation Projects and Workflows
    
    def create_translation_project(self, project_data: Dict, user_id: int) -> Optional[TranslationProject]:
        """Create a new translation project."""
        try:
            project = TranslationProject(
                name=project_data['name'],
                description=project_data.get('description'),
                source_language=project_data['source_language'],
                target_languages=json.dumps(project_data['target_languages']),
                entity_types=json.dumps(project_data.get('entity_types', [])),
                entity_ids=json.dumps(project_data.get('entity_ids', [])),
                field_names=json.dumps(project_data.get('field_names', [])),
                project_manager_id=user_id,
                require_review=project_data.get('require_review', True),
                auto_approve_ai=project_data.get('auto_approve_ai', False),
                quality_threshold=project_data.get('quality_threshold', 0.8)
            )
            
            db.session.add(project)
            db.session.commit()
            
            # Calculate project scope
            self._calculate_project_scope(project)
            
            return project
            
        except Exception as e:
            logger.error(f"Error creating translation project: {e}")
            db.session.rollback()
            return None
    
    def _calculate_project_scope(self, project: TranslationProject):
        """Calculate the scope and total items for a translation project."""
        try:
            entity_types = json.loads(project.entity_types) if project.entity_types else []
            entity_ids = json.loads(project.entity_ids) if project.entity_ids else []
            field_names = json.loads(project.field_names) if project.field_names else []
            target_languages = json.loads(project.target_languages)
            
            # Count content items that need translation
            query = MultilingualContent.query.filter_by(
                language_code=project.source_language,
                is_current=True
            )
            
            if entity_types:
                query = query.filter(MultilingualContent.entity_type.in_(entity_types))
            
            if entity_ids:
                query = query.filter(MultilingualContent.entity_id.in_(entity_ids))
            
            if field_names:
                query = query.filter(MultilingualContent.field_name.in_(field_names))
            
            source_items = query.count()
            total_items = source_items * len(target_languages)
            
            project.total_items = total_items
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error calculating project scope: {e}")
    
    def get_translation_project_status(self, project_id: int) -> Dict[str, Any]:
        """Get detailed status of a translation project."""
        try:
            project = TranslationProject.query.get(project_id)
            if not project:
                return {'error': 'Project not found'}
            
            # Get workflow statistics
            workflows = TranslationWorkflow.query.filter_by(project_id=project_id).all()
            
            status_counts = {}
            for workflow in workflows:
                status = workflow.current_state
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Calculate progress
            completed_states = ['completed', 'published']
            completed_count = sum(status_counts.get(state, 0) for state in completed_states)
            progress_percentage = (completed_count / project.total_items * 100) if project.total_items > 0 else 0
            
            # Update project progress
            project.completed_items = completed_count
            project.progress_percentage = progress_percentage
            db.session.commit()
            
            return {
                'project': project.to_dict(),
                'workflow_stats': status_counts,
                'progress': {
                    'total_items': project.total_items,
                    'completed_items': completed_count,
                    'percentage': progress_percentage
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting translation project status: {e}")
            return {'error': str(e)}
    
    # Analytics and Reporting
    
    @cache_manager.memoize(timeout=3600)
    def get_translation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive translation analytics."""
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Translation activity
            recent_translations = MultilingualContent.query.filter(
                MultilingualContent.created_at >= cutoff_date
            ).count()
            
            # Language usage
            language_usage = db.session.query(
                MultilingualContent.language_code,
                func.count(MultilingualContent.id)
            ).filter(
                MultilingualContent.created_at >= cutoff_date
            ).group_by(MultilingualContent.language_code).all()
            
            # Translation methods
            method_stats = db.session.query(
                MultilingualContent.translation_method,
                func.count(MultilingualContent.id)
            ).filter(
                MultilingualContent.created_at >= cutoff_date,
                MultilingualContent.translation_method.isnot(None)
            ).group_by(MultilingualContent.translation_method).all()
            
            # Content types
            content_type_stats = db.session.query(
                MultilingualContent.content_type,
                func.count(MultilingualContent.id)
            ).filter(
                MultilingualContent.created_at >= cutoff_date
            ).group_by(MultilingualContent.content_type).all()
            
            # Quality scores
            avg_quality = db.session.query(
                func.avg(MultilingualContent.quality_score)
            ).filter(
                MultilingualContent.created_at >= cutoff_date,
                MultilingualContent.quality_score.isnot(None)
            ).scalar()
            
            return {
                'period_days': days,
                'recent_translations': recent_translations,
                'language_usage': dict(language_usage),
                'translation_methods': dict(method_stats),
                'content_types': dict(content_type_stats),
                'average_quality': float(avg_quality) if avg_quality else None,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting translation analytics: {e}")
            return {}
    
    def get_language_coverage_report(self) -> Dict[str, Any]:
        """Get language coverage report for all entities."""
        try:
            active_languages = [lang['code'] for lang in self.get_active_languages()]
            
            # Get all entities with content
            entities = db.session.query(
                MultilingualContent.entity_type,
                MultilingualContent.entity_id
            ).distinct().all()
            
            coverage_report = {}
            
            for entity_type, entity_id in entities:
                entity_key = f"{entity_type}:{entity_id}"
                
                # Get available languages for this entity
                available_languages = db.session.query(
                    MultilingualContent.language_code
                ).filter_by(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    is_current=True
                ).distinct().all()
                
                available_langs = [lang[0] for lang in available_languages]
                missing_langs = [lang for lang in active_languages if lang not in available_langs]
                
                coverage_percentage = (len(available_langs) / len(active_languages)) * 100
                
                coverage_report[entity_key] = {
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'available_languages': available_langs,
                    'missing_languages': missing_langs,
                    'coverage_percentage': coverage_percentage,
                    'is_complete': len(missing_langs) == 0
                }
            
            # Summary statistics
            total_entities = len(entities)
            complete_entities = len([r for r in coverage_report.values() if r['is_complete']])
            overall_coverage = (complete_entities / total_entities * 100) if total_entities > 0 else 0
            
            return {
                'entities': coverage_report,
                'summary': {
                    'total_entities': total_entities,
                    'complete_entities': complete_entities,
                    'overall_coverage_percentage': overall_coverage,
                    'active_languages': active_languages
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting language coverage report: {e}")
            return {}
    
    # Utility Methods
    
    def cleanup_old_translations(self, days_old: int = 90) -> Dict[str, int]:
        """Clean up old translation versions and unused data."""
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Remove old non-current translation versions
            old_versions = MultilingualContent.query.filter(
                and_(
                    MultilingualContent.is_current == False,
                    MultilingualContent.created_at < cutoff_date
                )
            ).all()
            
            removed_versions = len(old_versions)
            for version in old_versions:
                db.session.delete(version)
            
            # Remove unused translation memory entries
            unused_tm = db.session.query(self.content_translation_service.TranslationMemory).filter(
                and_(
                    self.content_translation_service.TranslationMemory.usage_count == 0,
                    self.content_translation_service.TranslationMemory.created_at < cutoff_date
                )
            ).all()
            
            removed_tm = len(unused_tm)
            for tm_entry in unused_tm:
                db.session.delete(tm_entry)
            
            db.session.commit()
            
            return {
                'removed_versions': removed_versions,
                'removed_translation_memory': removed_tm,
                'cleanup_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old translations: {e}")
            db.session.rollback()
            return {'error': str(e)}
    
    def export_language_data(self, language_code: str) -> Dict[str, Any]:
        """Export all data for a specific language."""
        try:
            # Get UI translations
            ui_translations = self.translation_service.get_translation_dict(language_code)
            
            # Get content translations
            content_translations = MultilingualContent.query.filter_by(
                language_code=language_code,
                is_current=True
            ).all()
            
            content_data = {}
            for content in content_translations:
                key = f"{content.entity_type}:{content.entity_id}:{content.field_name}"
                content_data[key] = content.to_dict()
            
            # Get language info
            language_info = self.language_detection_service.get_language_info(language_code)
            locale_info = self.locale_service.get_locale_info(language_code)
            
            return {
                'language_code': language_code,
                'language_info': language_info,
                'locale_info': locale_info,
                'ui_translations': ui_translations,
                'content_translations': content_data,
                'export_timestamp': datetime.utcnow().isoformat(),
                'total_ui_keys': len(self._flatten_dict(ui_translations)),
                'total_content_items': len(content_data)
            }
            
        except Exception as e:
            logger.error(f"Error exporting language data: {e}")
            return {'error': str(e)}
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)