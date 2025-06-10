"""
Content Translation Manager
Handles dynamic content translation for database entities
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy import and_, or_

from app.extensions import db
from app.models.i18n import MultilingualContent, TranslationProject, TranslationWorkflow
from app.utils.cache import cache_manager
from .config import I18nConfig

logger = logging.getLogger(__name__)

class ContentTranslationManager:
    """Manager for content translations stored in database."""
    
    def __init__(self):
        """Initialize content translation manager."""
        self.config = I18nConfig()
        self._cache_prefix = f"{self.config.CACHE_KEY_PREFIX}:content"
    
    def get_translation(self, entity_type: str, entity_id: str,
                       field_name: str, language_code: str) -> Optional[str]:
        """Get translated content for an entity field."""
        # Check cache first
        cache_key = self._get_cache_key(entity_type, entity_id, field_name, language_code)
        
        if self.config.CONTENT_TRANSLATION_CACHE_ENABLED:
            cached = cache_manager.get(cache_key)
            if cached is not None:
                return cached
        
        try:
            # Query database
            translation = MultilingualContent.query.filter_by(
                entity_type=entity_type,
                entity_id=str(entity_id),
                field_name=field_name,
                language_code=language_code,
                is_current=True
            ).first()
            
            content = translation.content if translation else None
            
            # Cache result
            if self.config.CONTENT_TRANSLATION_CACHE_ENABLED:
                cache_manager.set(
                    cache_key,
                    content,
                    self.config.CONTENT_TRANSLATION_CACHE_TIMEOUT
                )
            
            return content
            
        except Exception as e:
            logger.error(f"Error getting translation: {e}")
            return None
    
    def get_translations(self, entity_type: str, entity_id: str,
                        field_name: Optional[str] = None,
                        language_codes: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get all translations for an entity."""
        try:
            query = MultilingualContent.query.filter_by(
                entity_type=entity_type,
                entity_id=str(entity_id),
                is_current=True
            )
            
            if field_name:
                query = query.filter_by(field_name=field_name)
            
            if language_codes:
                query = query.filter(MultilingualContent.language_code.in_(language_codes))
            
            translations = query.all()
            
            # Organize by field and language
            result = {}
            for trans in translations:
                if trans.field_name not in result:
                    result[trans.field_name] = {}
                result[trans.field_name][trans.language_code] = {
                    'content': trans.content,
                    'translation_status': trans.translation_status,
                    'quality_score': trans.quality_score,
                    'translated_at': trans.translated_at.isoformat() if trans.translated_at else None,
                    'translated_by': trans.translated_by
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting translations: {e}")
            return {}
    
    def save_translation(self, entity_type: str, entity_id: str,
                        field_name: str, content: str,
                        language_code: str, user_id: Optional[int] = None,
                        translation_method: str = 'manual',
                        quality_score: Optional[float] = None) -> bool:
        """Save or update a translation."""
        try:
            # Check if translation exists
            existing = MultilingualContent.query.filter_by(
                entity_type=entity_type,
                entity_id=str(entity_id),
                field_name=field_name,
                language_code=language_code,
                is_current=True
            ).first()
            
            if existing:
                # Archive current version
                existing.is_current = False
                existing.archived_at = datetime.utcnow()
            
            # Create new translation
            new_translation = MultilingualContent(
                entity_type=entity_type,
                entity_id=str(entity_id),
                field_name=field_name,
                language_code=language_code,
                content=content,
                content_type='text',
                is_original=(language_code == self.config.DEFAULT_LANGUAGE),
                is_current=True,
                translation_method=translation_method,
                translation_status='translated',
                quality_score=quality_score,
                translated_by=user_id,
                translated_at=datetime.utcnow() if translation_method != 'original' else None,
                created_by=user_id,
                updated_by=user_id
            )
            
            db.session.add(new_translation)
            db.session.commit()
            
            # Clear cache
            self._clear_cache(entity_type, entity_id, field_name, language_code)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving translation: {e}")
            db.session.rollback()
            return False
    
    def batch_save_translations(self, translations: List[Dict[str, Any]],
                              user_id: Optional[int] = None) -> Dict[str, Any]:
        """Save multiple translations in batch."""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            for trans in translations:
                try:
                    success = self.save_translation(
                        entity_type=trans['entity_type'],
                        entity_id=trans['entity_id'],
                        field_name=trans['field_name'],
                        content=trans['content'],
                        language_code=trans['language_code'],
                        user_id=user_id,
                        translation_method=trans.get('translation_method', 'manual'),
                        quality_score=trans.get('quality_score')
                    )
                    
                    if success:
                        results['success'] += 1
                    else:
                        results['failed'] += 1
                        
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(str(e))
            
        except Exception as e:
            logger.error(f"Error in batch save: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def delete_translation(self, entity_type: str, entity_id: str,
                          field_name: str, language_code: str) -> bool:
        """Delete a translation."""
        try:
            translation = MultilingualContent.query.filter_by(
                entity_type=entity_type,
                entity_id=str(entity_id),
                field_name=field_name,
                language_code=language_code,
                is_current=True
            ).first()
            
            if translation:
                db.session.delete(translation)
                db.session.commit()
                
                # Clear cache
                self._clear_cache(entity_type, entity_id, field_name, language_code)
                
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error deleting translation: {e}")
            db.session.rollback()
            return False
    
    def copy_translations(self, source_entity_type: str, source_entity_id: str,
                         target_entity_type: str, target_entity_id: str,
                         field_names: Optional[List[str]] = None,
                         language_codes: Optional[List[str]] = None,
                         user_id: Optional[int] = None) -> Dict[str, Any]:
        """Copy translations from one entity to another."""
        results = {
            'copied': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            # Get source translations
            query = MultilingualContent.query.filter_by(
                entity_type=source_entity_type,
                entity_id=str(source_entity_id),
                is_current=True
            )
            
            if field_names:
                query = query.filter(MultilingualContent.field_name.in_(field_names))
            
            if language_codes:
                query = query.filter(MultilingualContent.language_code.in_(language_codes))
            
            source_translations = query.all()
            
            # Copy each translation
            for trans in source_translations:
                try:
                    new_translation = MultilingualContent(
                        entity_type=target_entity_type,
                        entity_id=str(target_entity_id),
                        field_name=trans.field_name,
                        language_code=trans.language_code,
                        content=trans.content,
                        content_type=trans.content_type,
                        is_original=trans.is_original,
                        is_current=True,
                        translation_method='copied',
                        translation_status=trans.translation_status,
                        quality_score=trans.quality_score,
                        created_by=user_id,
                        updated_by=user_id
                    )
                    
                    db.session.add(new_translation)
                    results['copied'] += 1
                    
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append(str(e))
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error copying translations: {e}")
            db.session.rollback()
            results['errors'].append(str(e))
        
        return results
    
    def get_translation_coverage(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """Get translation coverage statistics for an entity."""
        try:
            # Get all translations for entity
            translations = MultilingualContent.query.filter_by(
                entity_type=entity_type,
                entity_id=str(entity_id),
                is_current=True
            ).all()
            
            # Get supported languages
            supported_languages = self.config.get_supported_language_codes()
            
            # Calculate coverage
            coverage = {}
            fields = set()
            
            for trans in translations:
                fields.add(trans.field_name)
                
                if trans.field_name not in coverage:
                    coverage[trans.field_name] = {
                        'languages': {},
                        'coverage_percentage': 0
                    }
                
                coverage[trans.field_name]['languages'][trans.language_code] = {
                    'translated': True,
                    'quality_score': trans.quality_score,
                    'status': trans.translation_status
                }
            
            # Calculate percentages
            for field in coverage:
                translated_count = len(coverage[field]['languages'])
                coverage[field]['coverage_percentage'] = (
                    translated_count / len(supported_languages) * 100
                )
                
                # Add missing languages
                for lang in supported_languages:
                    if lang not in coverage[field]['languages']:
                        coverage[field]['languages'][lang] = {
                            'translated': False,
                            'quality_score': None,
                            'status': 'missing'
                        }
            
            # Overall statistics
            total_combinations = len(fields) * len(supported_languages)
            translated_combinations = sum(
                len([l for l in f['languages'].values() if l['translated']])
                for f in coverage.values()
            )
            
            return {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'fields': list(fields),
                'languages': supported_languages,
                'coverage': coverage,
                'statistics': {
                    'total_fields': len(fields),
                    'total_languages': len(supported_languages),
                    'total_combinations': total_combinations,
                    'translated_combinations': translated_combinations,
                    'overall_coverage_percentage': (
                        translated_combinations / total_combinations * 100
                        if total_combinations > 0 else 0
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting translation coverage: {e}")
            return {}
    
    def _get_cache_key(self, entity_type: str, entity_id: str,
                      field_name: str, language_code: str) -> str:
        """Generate cache key for a translation."""
        return f"{self._cache_prefix}:{entity_type}:{entity_id}:{field_name}:{language_code}"
    
    def _clear_cache(self, entity_type: str, entity_id: str,
                    field_name: Optional[str] = None,
                    language_code: Optional[str] = None):
        """Clear cache for translations."""
        if not self.config.CONTENT_TRANSLATION_CACHE_ENABLED:
            return
        
        # Build pattern for cache deletion
        pattern_parts = [self._cache_prefix, entity_type, entity_id]
        
        if field_name:
            pattern_parts.append(field_name)
            if language_code:
                pattern_parts.append(language_code)
        
        pattern = ':'.join(pattern_parts) + '*'
        cache_manager.delete_pattern(pattern)