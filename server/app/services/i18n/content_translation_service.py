"""Content translation service for multi-language content management."""

import logging
import openai
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db
from app.services.i18n.language_detection_service import LanguageDetectionService
from app.services.i18n.translation_service import TranslationService

logger = logging.getLogger(__name__)


@dataclass
class TranslationRequest:
    """Translation request data."""
    content: str
    source_language: str
    target_language: str
    content_type: str  # 'text', 'html', 'markdown'
    context: Optional[str] = None
    priority: str = 'normal'  # 'low', 'normal', 'high', 'urgent'


@dataclass
class TranslationResponse:
    """Translation response data."""
    translated_content: str
    source_language: str
    target_language: str
    confidence: float
    method: str  # 'ai', 'human', 'mixed'
    metadata: Dict[str, Any]


class ContentTranslation(db.Model):
    """Model for storing content translations."""
    __tablename__ = 'content_translations'
    
    id = Column(Integer, primary_key=True)
    content_id = Column(String(255), nullable=False, index=True)  # Reference to source content
    content_type = Column(String(50), nullable=False)  # 'program', 'document', 'notification', etc.
    field_name = Column(String(100), nullable=False)  # 'title', 'description', 'content', etc.
    
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    source_content = Column(Text, nullable=False)
    translated_content = Column(Text, nullable=False)
    
    translation_method = Column(String(20), nullable=False)  # 'ai', 'human', 'mixed'
    confidence_score = Column(db.Float, nullable=True)
    quality_score = Column(db.Float, nullable=True)  # Human review score
    
    # Status tracking
    status = Column(String(20), default='pending')  # 'pending', 'completed', 'reviewed', 'rejected'
    is_approved = Column(Boolean, default=False)
    needs_review = Column(Boolean, default=True)
    
    # Workflow tracking
    translator_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    translated_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Metadata
    extra_data = Column(Text, nullable=True)  # JSON metadata
    version = Column(Integer, default=1)
    
    # Relationships
    translator = relationship('User', foreign_keys=[translator_id], backref='translations_done')
    reviewer = relationship('User', foreign_keys=[reviewer_id], backref='translations_reviewed')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'content_type': self.content_type,
            'field_name': self.field_name,
            'source_language': self.source_language,
            'target_language': self.target_language,
            'source_content': self.source_content,
            'translated_content': self.translated_content,
            'translation_method': self.translation_method,
            'confidence_score': self.confidence_score,
            'quality_score': self.quality_score,
            'status': self.status,
            'is_approved': self.is_approved,
            'needs_review': self.needs_review,
            'translator_id': self.translator_id,
            'reviewer_id': self.reviewer_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'translated_at': self.translated_at.isoformat() if self.translated_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'version': self.version
        }


class TranslationMemory(db.Model):
    """Model for translation memory (TM) segments."""
    __tablename__ = 'translation_memory'
    
    id = Column(Integer, primary_key=True)
    source_text_hash = Column(String(64), nullable=False, index=True)  # MD5 hash of source text
    source_language = Column(String(10), nullable=False)
    target_language = Column(String(10), nullable=False)
    source_text = Column(Text, nullable=False)
    target_text = Column(Text, nullable=False)
    
    # Context and domain
    domain = Column(String(100), nullable=True)  # 'medical', 'education', 'legal', etc.
    context = Column(String(255), nullable=True)
    
    # Quality and usage tracking
    quality_score = Column(db.Float, default=1.0)
    usage_count = Column(Integer, default=0)
    last_used = Column(DateTime, nullable=True)
    
    # Source tracking
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = relationship('User', backref='translation_memories')


class ContentTranslationService:
    """Service for managing content translations."""
    
    def __init__(self):
        """Initialize content translation service."""
        self.language_service = LanguageDetectionService()
        self.translation_service = TranslationService()
        
        # AI translation settings
        self.ai_confidence_threshold = 0.8
        self.max_ai_translation_length = 5000
        
        # Translation memory settings
        self.tm_match_threshold = 0.9
    
    def translate_content(self, request: TranslationRequest, user_id: Optional[int] = None) -> TranslationResponse:
        """
        Translate content using the best available method.
        
        Args:
            request: Translation request
            user_id: ID of requesting user
            
        Returns:
            Translation response
        """
        try:
            # Check translation memory first
            tm_result = self._check_translation_memory(
                request.content, 
                request.source_language, 
                request.target_language
            )
            
            if tm_result and tm_result['confidence'] >= self.tm_match_threshold:
                return TranslationResponse(
                    translated_content=tm_result['target_text'],
                    source_language=request.source_language,
                    target_language=request.target_language,
                    confidence=tm_result['confidence'],
                    method='memory',
                    metadata={'tm_id': tm_result['id'], 'match_type': 'exact'}
                )
            
            # Use AI translation for supported content
            if len(request.content) <= self.max_ai_translation_length:
                ai_result = self._translate_with_ai(request)
                if ai_result and ai_result.confidence >= self.ai_confidence_threshold:
                    # Store in translation memory for future use
                    self._store_in_translation_memory(
                        request.content,
                        ai_result.translated_content,
                        request.source_language,
                        request.target_language,
                        user_id
                    )
                    return ai_result
            
            # Fallback to basic translation service
            fallback_result = self.translation_service.translate(
                request.content, 
                request.target_language
            )
            
            return TranslationResponse(
                translated_content=fallback_result.text,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence=fallback_result.confidence,
                method='fallback',
                metadata={'source': fallback_result.source}
            )
            
        except Exception as e:
            logger.error(f"Error translating content: {e}")
            return TranslationResponse(
                translated_content=request.content,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence=0.0,
                method='error',
                metadata={'error': str(e)}
            )
    
    def _translate_with_ai(self, request: TranslationRequest) -> Optional[TranslationResponse]:
        """
        Translate content using AI (OpenAI GPT).
        
        Args:
            request: Translation request
            
        Returns:
            Translation response or None
        """
        try:
            # Prepare system prompt based on content type
            system_prompts = {
                'text': "You are a professional translator. Translate the given text accurately while preserving meaning and tone.",
                'html': "You are a professional translator. Translate the HTML content while preserving all HTML tags and structure.",
                'markdown': "You are a professional translator. Translate the Markdown content while preserving all formatting and structure."
            }
            
            system_prompt = system_prompts.get(request.content_type, system_prompts['text'])
            
            # Add context if provided
            if request.context:
                system_prompt += f" Context: {request.context}"
            
            # Get language names for better AI understanding
            source_lang_info = self.language_service.get_language_info(request.source_language)
            target_lang_info = self.language_service.get_language_info(request.target_language)
            
            user_prompt = f"""
Translate the following {request.content_type} from {source_lang_info['name']} to {target_lang_info['name']}:

{request.content}

Please provide only the translation without any explanations or additional text.
"""
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=2000
            )
            
            translated_content = response.choices[0].message.content.strip()
            
            # Calculate confidence based on response quality
            confidence = self._calculate_ai_confidence(request.content, translated_content, response)
            
            return TranslationResponse(
                translated_content=translated_content,
                source_language=request.source_language,
                target_language=request.target_language,
                confidence=confidence,
                method='ai',
                metadata={
                    'model': 'gpt-3.5-turbo',
                    'tokens_used': response.usage.total_tokens,
                    'finish_reason': response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            logger.error(f"Error in AI translation: {e}")
            return None
    
    def _calculate_ai_confidence(self, source: str, translation: str, response) -> float:
        """
        Calculate confidence score for AI translation.
        
        Args:
            source: Source text
            translation: Translated text
            response: OpenAI response object
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            base_confidence = 0.8
            
            # Adjust based on finish reason
            if response.choices[0].finish_reason == 'length':
                base_confidence -= 0.3  # Incomplete translation
            elif response.choices[0].finish_reason == 'content_filter':
                base_confidence -= 0.5
            
            # Adjust based on length ratio
            length_ratio = len(translation) / len(source) if len(source) > 0 else 0
            if length_ratio < 0.3 or length_ratio > 3.0:
                base_confidence -= 0.2  # Suspicious length ratio
            
            # Adjust based on content type preservation
            if '<' in source and '<' not in translation:
                base_confidence -= 0.2  # Lost HTML tags
            
            return max(0.0, min(1.0, base_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating AI confidence: {e}")
            return 0.5
    
    def _check_translation_memory(self, source_text: str, source_lang: str, target_lang: str) -> Optional[Dict]:
        """
        Check translation memory for existing translations.
        
        Args:
            source_text: Source text
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            Translation memory result or None
        """
        try:
            import hashlib
            
            text_hash = hashlib.md5(source_text.encode('utf-8')).hexdigest()
            
            # Exact match first
            exact_match = db.session.query(TranslationMemory).filter_by(
                source_text_hash=text_hash,
                source_language=source_lang,
                target_language=target_lang
            ).first()
            
            if exact_match:
                # Update usage statistics
                exact_match.usage_count += 1
                exact_match.last_used = datetime.utcnow()
                db.session.commit()
                
                return {
                    'id': exact_match.id,
                    'target_text': exact_match.target_text,
                    'confidence': 1.0,
                    'match_type': 'exact'
                }
            
            # Fuzzy matching (simplified - in production, use proper fuzzy matching)
            similar_entries = db.session.query(TranslationMemory).filter_by(
                source_language=source_lang,
                target_language=target_lang
            ).limit(50).all()
            
            best_match = None
            best_similarity = 0.0
            
            for entry in similar_entries:
                similarity = self._calculate_text_similarity(source_text, entry.source_text)
                if similarity > best_similarity and similarity >= self.tm_match_threshold:
                    best_similarity = similarity
                    best_match = entry
            
            if best_match:
                return {
                    'id': best_match.id,
                    'target_text': best_match.target_text,
                    'confidence': best_similarity,
                    'match_type': 'fuzzy'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking translation memory: {e}")
            return None
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts (simplified implementation).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            # Simple word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {e}")
            return 0.0
    
    def _store_in_translation_memory(self, source_text: str, target_text: str, 
                                   source_lang: str, target_lang: str, user_id: Optional[int]):
        """
        Store translation in translation memory.
        
        Args:
            source_text: Source text
            target_text: Target text
            source_lang: Source language
            target_lang: Target language
            user_id: User ID
        """
        try:
            import hashlib
            
            text_hash = hashlib.md5(source_text.encode('utf-8')).hexdigest()
            
            # Check if already exists
            existing = db.session.query(TranslationMemory).filter_by(
                source_text_hash=text_hash,
                source_language=source_lang,
                target_language=target_lang
            ).first()
            
            if existing:
                # Update existing entry
                existing.target_text = target_text
                existing.usage_count += 1
                existing.last_used = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
            else:
                # Create new entry
                tm_entry = TranslationMemory(
                    source_text_hash=text_hash,
                    source_text=source_text,
                    target_text=target_text,
                    source_language=source_lang,
                    target_language=target_lang,
                    usage_count=1,
                    last_used=datetime.utcnow(),
                    created_by=user_id
                )
                db.session.add(tm_entry)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing in translation memory: {e}")
            db.session.rollback()
    
    def store_content_translation(self, content_id: str, content_type: str, field_name: str,
                                source_content: str, translated_content: str,
                                source_language: str, target_language: str,
                                method: str, confidence: float, user_id: Optional[int] = None) -> Optional[ContentTranslation]:
        """
        Store content translation in database.
        
        Args:
            content_id: ID of source content
            content_type: Type of content
            field_name: Field name being translated
            source_content: Original content
            translated_content: Translated content
            source_language: Source language
            target_language: Target language
            method: Translation method
            confidence: Confidence score
            user_id: User ID
            
        Returns:
            ContentTranslation object or None
        """
        try:
            translation = ContentTranslation(
                content_id=content_id,
                content_type=content_type,
                field_name=field_name,
                source_content=source_content,
                translated_content=translated_content,
                source_language=source_language,
                target_language=target_language,
                translation_method=method,
                confidence_score=confidence,
                translator_id=user_id,
                translated_at=datetime.utcnow(),
                status='completed' if confidence >= self.ai_confidence_threshold else 'pending',
                needs_review=confidence < self.ai_confidence_threshold
            )
            
            db.session.add(translation)
            db.session.commit()
            
            return translation
            
        except Exception as e:
            logger.error(f"Error storing content translation: {e}")
            db.session.rollback()
            return None
    
    def get_content_translations(self, content_id: str, content_type: str, target_language: Optional[str] = None) -> List[ContentTranslation]:
        """
        Get translations for content.
        
        Args:
            content_id: Content ID
            content_type: Content type
            target_language: Optional target language filter
            
        Returns:
            List of ContentTranslation objects
        """
        try:
            query = db.session.query(ContentTranslation).filter_by(
                content_id=content_id,
                content_type=content_type
            )
            
            if target_language:
                query = query.filter_by(target_language=target_language)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting content translations: {e}")
            return []
    
    def get_translation_stats(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get translation statistics.
        
        Args:
            language: Optional language filter
            
        Returns:
            Translation statistics
        """
        try:
            query = db.session.query(ContentTranslation)
            
            if language:
                query = query.filter_by(target_language=language)
            
            total = query.count()
            completed = query.filter_by(status='completed').count()
            pending = query.filter_by(status='pending').count()
            reviewed = query.filter_by(status='reviewed').count()
            
            # Method breakdown
            ai_count = query.filter_by(translation_method='ai').count()
            human_count = query.filter_by(translation_method='human').count()
            mixed_count = query.filter_by(translation_method='mixed').count()
            
            return {
                'total_translations': total,
                'completed': completed,
                'pending': pending,
                'reviewed': reviewed,
                'methods': {
                    'ai': ai_count,
                    'human': human_count,
                    'mixed': mixed_count
                },
                'completion_rate': completed / total if total > 0 else 0,
                'review_rate': reviewed / total if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting translation stats: {e}")
            return {}
    
    def bulk_translate_content(self, content_items: List[Dict], target_languages: List[str], 
                             user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Bulk translate multiple content items.
        
        Args:
            content_items: List of content items to translate
            target_languages: List of target languages
            user_id: User ID
            
        Returns:
            Bulk translation results
        """
        try:
            results = {
                'success_count': 0,
                'error_count': 0,
                'translations': [],
                'errors': []
            }
            
            for item in content_items:
                for target_lang in target_languages:
                    try:
                        request = TranslationRequest(
                            content=item['content'],
                            source_language=item['source_language'],
                            target_language=target_lang,
                            content_type=item.get('content_type', 'text'),
                            context=item.get('context')
                        )
                        
                        response = self.translate_content(request, user_id)
                        
                        # Store translation
                        translation = self.store_content_translation(
                            content_id=item['content_id'],
                            content_type=item['content_type'],
                            field_name=item['field_name'],
                            source_content=item['content'],
                            translated_content=response.translated_content,
                            source_language=request.source_language,
                            target_language=target_lang,
                            method=response.method,
                            confidence=response.confidence,
                            user_id=user_id
                        )
                        
                        if translation:
                            results['success_count'] += 1
                            results['translations'].append(translation.to_dict())
                        else:
                            results['error_count'] += 1
                            results['errors'].append(f"Failed to store translation for {item['content_id']}")
                        
                    except Exception as e:
                        results['error_count'] += 1
                        results['errors'].append(f"Error translating {item['content_id']}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk translate: {e}")
            return {'success_count': 0, 'error_count': len(content_items) * len(target_languages), 'errors': [str(e)]}