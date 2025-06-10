"""AI-Powered Question Generation Service."""

import os
import re
import json
import uuid
import hashlib
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
import openai
from flask import current_app
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

# Import content processing libraries
try:
    import PyPDF2
    import docx
    import whisper
    import requests
    from bs4 import BeautifulSoup
    import nltk
    from textstat import flesch_reading_ease
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import spacy
    HAS_NLP_LIBRARIES = True
except ImportError as e:
    # Will log when app context is available
    HAS_NLP_LIBRARIES = False

from app.extensions import db
from app.models.ai_question_generation import (
    ContentType, QuestionType, BloomsTaxonomy,
    LearningObjective, QuestionGenerationRequest, GeneratedQuestion,
    QuestionDuplicate, QuestionBank, QuestionBankQuestion,
    GenerationAnalytics
)
from app.utils.ai import configure_openai


class ContentProcessor:
    """Process various content types for question generation."""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': self._process_pdf,
            'docx': self._process_docx,
            'txt': self._process_txt,
            'mp3': self._process_audio,
            'mp4': self._process_video,
            'wav': self._process_audio,
            'url': self._process_url
        }
        
        # Initialize NLP models if available
        if HAS_NLP_LIBRARIES:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # SpaCy model not found - will log when needed
                pass
                self.nlp = None
        else:
            self.nlp = None
    
    def process_content(self, source_content: SourceContent) -> Dict[str, Any]:
        """Process source content and extract text and metadata."""
        try:
            result = {
                'extracted_text': '',
                'keywords': [],
                'topics': [],
                'difficulty_level': 5.0,
                'readability_score': 0.0,
                'metadata': {},
                'error': None
            }
            
            # Determine content type and process accordingly
            if source_content.file_path:
                file_ext = Path(source_content.file_path).suffix.lower().lstrip('.')
                if file_ext in self.supported_formats:
                    result = self.supported_formats[file_ext](source_content.file_path)
                else:
                    result['error'] = f"Unsupported file format: {file_ext}"
            elif source_content.url:
                result = self.supported_formats['url'](source_content.url)
            elif source_content.text_content:
                result = self._process_text(source_content.text_content)
            else:
                result['error'] = "No content source provided"
            
            # Enhance with NLP analysis if available
            if result['extracted_text'] and not result['error']:
                result = self._enhance_with_nlp(result)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error processing content: {str(e)}")
            return {
                'extracted_text': '',
                'keywords': [],
                'topics': [],
                'difficulty_level': 5.0,
                'readability_score': 0.0,
                'metadata': {},
                'error': str(e)
            }
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Process PDF files."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return self._process_text(text)
        except Exception as e:
            return {'error': f"PDF processing failed: {str(e)}"}
    
    def _process_docx(self, file_path: str) -> Dict[str, Any]:
        """Process Word documents."""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return self._process_text(text)
        except Exception as e:
            return {'error': f"DOCX processing failed: {str(e)}"}
    
    def _process_txt(self, file_path: str) -> Dict[str, Any]:
        """Process text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return self._process_text(text)
        except Exception as e:
            return {'error': f"TXT processing failed: {str(e)}"}
    
    def _process_audio(self, file_path: str) -> Dict[str, Any]:
        """Process audio files using Whisper."""
        try:
            model = whisper.load_model("base")
            result = model.transcribe(file_path)
            text = result["text"]
            
            metadata = {
                'duration': result.get('duration', 0),
                'language': result.get('language', 'unknown'),
                'segments': len(result.get('segments', []))
            }
            
            processed = self._process_text(text)
            processed['metadata'].update(metadata)
            return processed
            
        except Exception as e:
            return {'error': f"Audio processing failed: {str(e)}"}
    
    def _process_video(self, file_path: str) -> Dict[str, Any]:
        """Process video files (extract audio and transcribe)."""
        # For video, we would typically extract audio first
        # This is a simplified version - in production, you'd use ffmpeg
        return self._process_audio(file_path)
    
    def _process_url(self, url: str) -> Dict[str, Any]:
        """Process web content."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            metadata = {
                'url': url,
                'title': soup.title.string if soup.title else 'Unknown',
                'content_length': len(text)
            }
            
            processed = self._process_text(text)
            processed['metadata'].update(metadata)
            return processed
            
        except Exception as e:
            return {'error': f"URL processing failed: {str(e)}"}
    
    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process raw text content."""
        try:
            # Basic text cleaning
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Calculate readability score
            readability_score = 0.0
            if HAS_NLP_LIBRARIES:
                try:
                    readability_score = flesch_reading_ease(text)
                except:
                    pass
            
            # Estimate difficulty based on readability and text complexity
            difficulty_level = self._estimate_difficulty(text, readability_score)
            
            return {
                'extracted_text': text,
                'keywords': [],
                'topics': [],
                'difficulty_level': difficulty_level,
                'readability_score': readability_score,
                'metadata': {
                    'word_count': len(text.split()),
                    'character_count': len(text)
                },
                'error': None
            }
            
        except Exception as e:
            return {'error': f"Text processing failed: {str(e)}"}
    
    def _enhance_with_nlp(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance text analysis with NLP techniques."""
        if not HAS_NLP_LIBRARIES or not self.nlp:
            return result
        
        try:
            text = result['extracted_text']
            
            # Process with spaCy
            doc = self.nlp(text[:1000000])  # Limit to 1M characters
            
            # Extract keywords (named entities and important nouns)
            keywords = []
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT', 'WORK_OF_ART']:
                    keywords.append(ent.text)
            
            # Add important nouns and proper nouns
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    len(token.text) > 3 and 
                    not token.is_stop and 
                    token.is_alpha):
                    keywords.append(token.text)
            
            # Remove duplicates and limit
            keywords = list(set(keywords))[:20]
            
            # Extract topics using simple keyword clustering
            topics = self._extract_topics(keywords, text)
            
            result['keywords'] = keywords
            result['topics'] = topics
            
        except Exception as e:
            current_app.logger.warning(f"NLP enhancement failed: {str(e)}")
        
        return result
    
    def _extract_topics(self, keywords: List[str], text: str) -> List[str]:
        """Extract main topics from text."""
        # Simple topic extraction based on keyword frequency and context
        topics = []
        
        # Common topic domains
        topic_domains = {
            'technology': ['computer', 'software', 'digital', 'internet', 'data'],
            'science': ['research', 'study', 'analysis', 'experiment', 'theory'],
            'business': ['company', 'market', 'business', 'profit', 'customer'],
            'education': ['learning', 'teaching', 'student', 'school', 'education'],
            'health': ['health', 'medical', 'patient', 'treatment', 'disease'],
            'history': ['history', 'historical', 'past', 'ancient', 'century'],
            'literature': ['book', 'author', 'story', 'novel', 'literature']
        }
        
        text_lower = text.lower()
        for topic, domain_words in topic_domains.items():
            score = sum(1 for word in domain_words if word in text_lower)
            if score >= 2:  # Minimum threshold
                topics.append(topic)
        
        return topics[:5]  # Limit to top 5 topics
    
    def _estimate_difficulty(self, text: str, readability_score: float) -> float:
        """Estimate content difficulty on a 1-10 scale."""
        # Base difficulty on readability score
        if readability_score >= 90:
            base_difficulty = 2.0  # Very easy
        elif readability_score >= 80:
            base_difficulty = 3.0  # Easy
        elif readability_score >= 70:
            base_difficulty = 4.0  # Fairly easy
        elif readability_score >= 60:
            base_difficulty = 5.0  # Standard
        elif readability_score >= 50:
            base_difficulty = 6.0  # Fairly difficult
        elif readability_score >= 30:
            base_difficulty = 7.0  # Difficult
        else:
            base_difficulty = 8.0  # Very difficult
        
        # Adjust based on text complexity indicators
        complexity_indicators = [
            len(re.findall(r'\b\w{10,}\b', text)),  # Long words
            len(re.findall(r'[;:]', text)),  # Complex punctuation
            len(re.findall(r'\b(?:however|moreover|furthermore|nevertheless)\b', text.lower()))  # Complex connectors
        ]
        
        complexity_score = sum(complexity_indicators) / max(len(text.split()), 1) * 100
        
        # Adjust difficulty based on complexity
        if complexity_score > 5:
            base_difficulty = min(10.0, base_difficulty + 1.0)
        elif complexity_score > 10:
            base_difficulty = min(10.0, base_difficulty + 2.0)
        
        return round(base_difficulty, 1)


class QuestionGenerator:
    """Generate questions using AI models."""
    
    def __init__(self):
        self.question_type_prompts = {
            'multiple_choice': self._get_mcq_prompt,
            'true_false': self._get_tf_prompt,
            'fill_in_blank': self._get_fib_prompt,
            'short_answer': self._get_sa_prompt,
            'essay': self._get_essay_prompt,
            'matching': self._get_matching_prompt,
            'ordering': self._get_ordering_prompt
        }
    
    async def generate_questions(self, request: QuestionGenerationRequest) -> Dict[str, Any]:
        """Generate questions based on the request parameters."""
        configure_openai()
        
        if not openai.api_key:
            return {
                'success': False,
                'error': 'OpenAI API key not configured',
                'questions': []
            }
        
        try:
            # Update request status
            request.status = 'processing'
            request.started_at = datetime.utcnow()
            db.session.commit()
            
            # Get source content
            source_content = request.source_content
            if not source_content.extracted_text:
                return {
                    'success': False,
                    'error': 'Source content not processed',
                    'questions': []
                }
            
            # Get question types
            question_types = self._get_question_types(request.question_types)
            if not question_types:
                return {
                    'success': False,
                    'error': 'No valid question types specified',
                    'questions': []
                }
            
            # Generate questions for each type
            all_questions = []
            total_tokens = 0
            
            questions_per_type = max(1, request.question_count // len(question_types))
            
            for i, question_type in enumerate(question_types):
                # Calculate questions for this type
                if i == len(question_types) - 1:  # Last type gets remaining questions
                    questions_count = request.question_count - len(all_questions)
                else:
                    questions_count = questions_per_type
                
                if questions_count <= 0:
                    continue
                
                # Generate questions for this type
                type_result = await self._generate_questions_for_type(
                    request, question_type, questions_count
                )
                
                if type_result['success']:
                    all_questions.extend(type_result['questions'])
                    total_tokens += type_result.get('tokens_used', 0)
                
                # Update progress
                progress = (i + 1) / len(question_types) * 0.8  # 80% for generation
                request.progress = progress
                db.session.commit()
            
            # Post-process questions
            processed_questions = await self._post_process_questions(
                all_questions, request
            )
            
            # Update request with results
            request.status = 'completed'
            request.completed_at = datetime.utcnow()
            request.questions_generated = len(processed_questions)
            request.total_tokens_used = total_tokens
            request.cost_estimate = self._calculate_cost(total_tokens)
            request.progress = 1.0
            
            db.session.commit()
            
            return {
                'success': True,
                'questions': processed_questions,
                'tokens_used': total_tokens,
                'cost_estimate': request.cost_estimate
            }
            
        except Exception as e:
            current_app.logger.error(f"Question generation failed: {str(e)}")
            
            # Update request status
            request.status = 'failed'
            request.error_message = str(e)
            db.session.commit()
            
            return {
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    async def _generate_questions_for_type(
        self, 
        request: QuestionGenerationRequest, 
        question_type: QuestionType, 
        count: int
    ) -> Dict[str, Any]:
        """Generate questions for a specific type."""
        try:
            # Get the appropriate prompt
            prompt_func = self.question_type_prompts.get(question_type.name)
            if not prompt_func:
                return {
                    'success': False,
                    'error': f'No prompt template for question type: {question_type.name}',
                    'questions': []
                }
            
            prompt = prompt_func(request, count)
            
            # Make OpenAI API call
            response = await self._call_openai_api(prompt, request.ai_model)
            
            if not response['success']:
                return response
            
            # Parse the response
            questions = self._parse_ai_response(
                response['content'], question_type, request
            )
            
            return {
                'success': True,
                'questions': questions,
                'tokens_used': response.get('tokens_used', 0)
            }
            
        except Exception as e:
            current_app.logger.error(f"Error generating {question_type.name} questions: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'questions': []
            }
    
    async def _call_openai_api(self, prompt: str, model: str) -> Dict[str, Any]:
        """Make API call to OpenAI."""
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert educational content creator specialized in generating high-quality assessment questions."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            return {
                'success': True,
                'content': response.choices[0].message['content'],
                'tokens_used': response['usage']['total_tokens']
            }
            
        except Exception as e:
            current_app.logger.error(f"OpenAI API call failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _parse_ai_response(
        self, 
        response_content: str, 
        question_type: QuestionType, 
        request: QuestionGenerationRequest
    ) -> List[Dict[str, Any]]:
        """Parse AI response into structured questions."""
        questions = []
        
        try:
            # Try to parse as JSON first
            json_match = re.search(r'```json\n(.*?)\n```', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Look for JSON-like structure
                json_str = response_content
            
            # Clean up the JSON string
            json_str = re.sub(r'^[^{\[]*', '', json_str)
            json_str = re.sub(r'[^}\]]*$', '', json_str)
            
            parsed_data = json.loads(json_str)
            
            # Handle different response formats
            if isinstance(parsed_data, list):
                questions_data = parsed_data
            elif isinstance(parsed_data, dict) and 'questions' in parsed_data:
                questions_data = parsed_data['questions']
            else:
                questions_data = [parsed_data]
            
            # Process each question
            for q_data in questions_data:
                question = self._create_question_from_data(
                    q_data, question_type, request
                )
                if question:
                    questions.append(question)
            
        except json.JSONDecodeError:
            # Fallback to text parsing
            questions = self._parse_text_response(
                response_content, question_type, request
            )
        
        return questions
    
    def _create_question_from_data(
        self, 
        q_data: Dict[str, Any], 
        question_type: QuestionType, 
        request: QuestionGenerationRequest
    ) -> Optional[Dict[str, Any]]:
        """Create a question object from parsed data."""
        try:
            question = {
                'question_text': q_data.get('question', q_data.get('text', '')),
                'question_type_id': question_type.id,
                'difficulty_level': q_data.get('difficulty', 5.0),
                'explanation': q_data.get('explanation', ''),
                'keywords': q_data.get('keywords', []),
                'topics': q_data.get('topics', []),
                'correct_answer': q_data.get('correct_answer'),
                'question_options': q_data.get('options'),
                'blooms_level_id': self._get_blooms_level_id(q_data.get('blooms_level')),
                'quality_score': q_data.get('quality_score', 0.8),
                'ai_confidence': q_data.get('confidence', 0.8)
            }
            
            # Validate required fields
            if not question['question_text']:
                return None
            
            return question
            
        except Exception as e:
            current_app.logger.error(f"Error creating question from data: {str(e)}")
            return None
    
    def _parse_text_response(
        self, 
        response_content: str, 
        question_type: QuestionType, 
        request: QuestionGenerationRequest
    ) -> List[Dict[str, Any]]:
        """Fallback text parsing for non-JSON responses."""
        questions = []
        
        # Split by question markers
        question_patterns = [
            r'\d+\.\s*',
            r'Question \d+:',
            r'Q\d+:',
            r'\n\n'
        ]
        
        sections = response_content.split('\n\n')
        
        for section in sections:
            section = section.strip()
            if len(section) > 20:  # Minimum question length
                # Extract question text (first line usually)
                lines = section.split('\n')
                question_text = lines[0].strip()
                
                # Remove question number if present
                question_text = re.sub(r'^\d+\.\s*', '', question_text)
                question_text = re.sub(r'^Question \d+:\s*', '', question_text)
                question_text = re.sub(r'^Q\d+:\s*', '', question_text)
                
                if question_text:
                    question = {
                        'question_text': question_text,
                        'question_type_id': question_type.id,
                        'difficulty_level': 5.0,
                        'explanation': '',
                        'keywords': [],
                        'topics': [],
                        'correct_answer': None,
                        'question_options': None,
                        'quality_score': 0.7,
                        'ai_confidence': 0.7
                    }
                    questions.append(question)
        
        return questions
    
    async def _post_process_questions(
        self, 
        questions: List[Dict[str, Any]], 
        request: QuestionGenerationRequest
    ) -> List[GeneratedQuestion]:
        """Post-process generated questions."""
        processed_questions = []
        
        for q_data in questions:
            try:
                # Create database object
                question = GeneratedQuestion(
                    generation_request_id=request.id,
                    question_type_id=q_data['question_type_id'],
                    question_text=q_data['question_text'],
                    question_options=q_data.get('question_options'),
                    correct_answer=q_data.get('correct_answer'),
                    explanation=q_data.get('explanation', ''),
                    difficulty_level=q_data.get('difficulty_level', 5.0),
                    blooms_level_id=q_data.get('blooms_level_id'),
                    keywords=q_data.get('keywords', []),
                    topics=q_data.get('topics', []),
                    quality_score=q_data.get('quality_score', 0.8),
                    ai_confidence=q_data.get('ai_confidence', 0.8),
                    generation_prompt=f"Generated for request {request.id}",
                    tokens_used=50  # Estimate
                )
                
                db.session.add(question)
                processed_questions.append(question)
                
            except Exception as e:
                current_app.logger.error(f"Error creating question object: {str(e)}")
        
        # Commit all questions
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error saving questions: {str(e)}")
            db.session.rollback()
        
        return processed_questions
    
    def _get_question_types(self, type_ids: List[int]) -> List[QuestionType]:
        """Get question type objects from IDs."""
        if not type_ids:
            # Default to multiple choice if none specified
            return db.session.query(QuestionType).filter(
                QuestionType.name == 'multiple_choice',
                QuestionType.is_active == True
            ).all()
        
        return db.session.query(QuestionType).filter(
            QuestionType.id.in_(type_ids),
            QuestionType.is_active == True
        ).all()
    
    def _get_blooms_level_id(self, level_name: Optional[str]) -> Optional[int]:
        """Get Bloom's taxonomy level ID from name."""
        if not level_name:
            return None
        
        level = db.session.query(BloomsTaxonomy).filter(
            func.lower(BloomsTaxonomy.level) == level_name.lower()
        ).first()
        
        return level.id if level else None
    
    def _calculate_cost(self, tokens_used: int) -> float:
        """Calculate estimated cost based on tokens used."""
        # OpenAI GPT-4 pricing (approximate)
        cost_per_1k_tokens = 0.03  # $0.03 per 1K tokens
        return (tokens_used / 1000) * cost_per_1k_tokens
    
    # Prompt templates for different question types
    
    def _get_mcq_prompt(self, request: QuestionGenerationRequest, count: int) -> str:
        """Generate prompt for multiple choice questions."""
        content = request.source_content.extracted_text[:4000]  # Limit content length
        
        difficulty_text = self._get_difficulty_text(request.difficulty_range)
        topics_text = ', '.join(request.topic_focus) if request.topic_focus else 'any relevant topics'
        
        prompt = f"""
Generate {count} high-quality multiple choice questions based on the following content:

CONTENT:
{content}

REQUIREMENTS:
- Difficulty level: {difficulty_text}
- Focus on topics: {topics_text}
- Language: {request.language}
- Each question should have 4 options (A, B, C, D)
- Only one correct answer per question
- Include explanations for correct answers
- Vary difficulty across questions
- Ensure questions test understanding, not just memorization

{request.custom_instructions if request.custom_instructions else ''}

Please respond with a JSON array in this format:
[
  {{
    "question": "Question text here?",
    "options": {{
      "A": "First option",
      "B": "Second option", 
      "C": "Third option",
      "D": "Fourth option"
    }},
    "correct_answer": "A",
    "explanation": "Explanation of why A is correct",
    "difficulty": 5.5,
    "blooms_level": "understand",
    "keywords": ["keyword1", "keyword2"],
    "topics": ["topic1"],
    "confidence": 0.9
  }}
]
"""
        return prompt
    
    def _get_tf_prompt(self, request: QuestionGenerationRequest, count: int) -> str:
        """Generate prompt for true/false questions."""
        content = request.source_content.extracted_text[:4000]
        
        difficulty_text = self._get_difficulty_text(request.difficulty_range)
        
        prompt = f"""
Generate {count} true/false questions based on the following content:

CONTENT:
{content}

REQUIREMENTS:
- Difficulty level: {difficulty_text}
- Clear, unambiguous statements
- Mix of true and false answers
- Include explanations
- Avoid trick questions

Please respond with a JSON array in this format:
[
  {{
    "question": "Statement to evaluate",
    "correct_answer": true,
    "explanation": "Explanation of why this is true/false",
    "difficulty": 4.0,
    "blooms_level": "remember",
    "keywords": ["keyword1"],
    "confidence": 0.85
  }}
]
"""
        return prompt
    
    def _get_fib_prompt(self, request: QuestionGenerationRequest, count: int) -> str:
        """Generate prompt for fill-in-the-blank questions."""
        content = request.source_content.extracted_text[:4000]
        
        prompt = f"""
Generate {count} fill-in-the-blank questions based on the following content:

CONTENT:
{content}

REQUIREMENTS:
- Use underscores (____) for blanks
- Provide clear context clues
- Include correct answers
- Vary the difficulty

Please respond with a JSON array in this format:
[
  {{
    "question": "The ____ is responsible for ____.",
    "correct_answer": ["brain", "thinking"],
    "explanation": "The brain is the organ responsible for thinking and cognitive functions.",
    "difficulty": 5.0,
    "keywords": ["brain", "thinking"]
  }}
]
"""
        return prompt
    
    def _get_sa_prompt(self, request: QuestionGenerationRequest, count: int) -> str:
        """Generate prompt for short answer questions."""
        content = request.source_content.extracted_text[:4000]
        
        prompt = f"""
Generate {count} short answer questions based on the following content:

CONTENT:
{content}

REQUIREMENTS:
- Questions should require 2-3 sentence answers
- Test comprehension and application
- Include sample answers
- Focus on key concepts

Please respond with a JSON array in this format:
[
  {{
    "question": "Explain the main concept discussed in the passage.",
    "correct_answer": "Sample answer showing expected response length and content.",
    "explanation": "Key points that should be covered in the answer.",
    "difficulty": 6.0,
    "blooms_level": "understand"
  }}
]
"""
        return prompt
    
    def _get_essay_prompt(self, request: QuestionGenerationRequest, count: int) -> str:
        """Generate prompt for essay questions."""
        content = request.source_content.extracted_text[:4000]
        
        prompt = f"""
Generate {count} essay questions based on the following content:

CONTENT:
{content}

REQUIREMENTS:
- Questions should require detailed, multi-paragraph responses
- Encourage critical thinking and analysis
- Include grading criteria
- Test higher-order thinking skills

Please respond with a JSON array in this format:
[
  {{
    "question": "Analyze and discuss the implications of...",
    "correct_answer": "Essay should include: 1) Introduction with thesis, 2) Analysis of key points, 3) Examples and evidence, 4) Conclusion with synthesis",
    "explanation": "Grading criteria and key points to address",
    "difficulty": 8.0,
    "blooms_level": "analyze"
  }}
]
"""
        return prompt
    
    def _get_matching_prompt(self, request: QuestionGenerationRequest, count: int) -> str:
        """Generate prompt for matching questions."""
        content = request.source_content.extracted_text[:4000]
        
        prompt = f"""
Generate {count} matching questions based on the following content:

CONTENT:
{content}

REQUIREMENTS:
- Create pairs of related items
- Include at least 5 pairs per question
- Ensure clear relationships
- Avoid ambiguous matches

Please respond with a JSON array in this format:
[
  {{
    "question": "Match the following terms with their definitions:",
    "options": {{
      "terms": ["Term 1", "Term 2", "Term 3"],
      "definitions": ["Definition A", "Definition B", "Definition C"]
    }},
    "correct_answer": {{"Term 1": "Definition A", "Term 2": "Definition B", "Term 3": "Definition C"}},
    "difficulty": 5.5
  }}
]
"""
        return prompt
    
    def _get_ordering_prompt(self, request: QuestionGenerationRequest, count: int) -> str:
        """Generate prompt for ordering/sequencing questions."""
        content = request.source_content.extracted_text[:4000]
        
        prompt = f"""
Generate {count} ordering/sequencing questions based on the following content:

CONTENT:
{content}

REQUIREMENTS:
- Create logical sequences (steps, chronological order, etc.)
- Include 4-6 items to order
- Ensure clear correct sequence
- Test understanding of processes or relationships

Please respond with a JSON array in this format:
[
  {{
    "question": "Arrange the following steps in the correct order:",
    "options": ["Step A", "Step B", "Step C", "Step D"],
    "correct_answer": ["Step C", "Step A", "Step D", "Step B"],
    "explanation": "The correct sequence is based on...",
    "difficulty": 6.0
  }}
]
"""
        return prompt
    
    def _get_difficulty_text(self, difficulty_range: List[float]) -> str:
        """Convert difficulty range to descriptive text."""
        min_diff, max_diff = difficulty_range
        
        if max_diff <= 3:
            return "Easy (basic recall and recognition)"
        elif max_diff <= 5:
            return "Easy to Medium (understanding and simple application)"
        elif max_diff <= 7:
            return "Medium (application and analysis)"
        elif max_diff <= 9:
            return "Hard (synthesis and evaluation)"
        else:
            return "Very Hard (expert-level analysis and creation)"


class DuplicateDetector:
    """Detect duplicate questions using various methods."""
    
    def __init__(self):
        self.similarity_threshold = 0.8
        if HAS_NLP_LIBRARIES:
            self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        else:
            self.vectorizer = None
    
    def detect_duplicates(self, questions: List[GeneratedQuestion]) -> List[QuestionDuplicate]:
        """Detect potential duplicate questions."""
        duplicates = []
        
        if len(questions) < 2:
            return duplicates
        
        # Text-based similarity
        text_duplicates = self._detect_text_similarity(questions)
        duplicates.extend(text_duplicates)
        
        # Semantic similarity (if NLP libraries available)
        if self.vectorizer:
            semantic_duplicates = self._detect_semantic_similarity(questions)
            duplicates.extend(semantic_duplicates)
        
        # Keyword overlap
        keyword_duplicates = self._detect_keyword_overlap(questions)
        duplicates.extend(keyword_duplicates)
        
        return duplicates
    
    def _detect_text_similarity(self, questions: List[GeneratedQuestion]) -> List[QuestionDuplicate]:
        """Detect duplicates based on text similarity."""
        duplicates = []
        
        for i in range(len(questions)):
            for j in range(i + 1, len(questions)):
                q1, q2 = questions[i], questions[j]
                
                # Simple text similarity using character overlap
                similarity = self._calculate_text_similarity(
                    q1.question_text, q2.question_text
                )
                
                if similarity >= self.similarity_threshold:
                    duplicate = QuestionDuplicate(
                        question1_id=q1.id,
                        question2_id=q2.id,
                        similarity_score=similarity,
                        similarity_type='text',
                        detection_method='text_similarity'
                    )
                    duplicates.append(duplicate)
        
        return duplicates
    
    def _detect_semantic_similarity(self, questions: List[GeneratedQuestion]) -> List[QuestionDuplicate]:
        """Detect duplicates based on semantic similarity."""
        duplicates = []
        
        try:
            # Get question texts
            texts = [q.question_text for q in questions]
            
            # Vectorize texts
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Calculate similarity matrix
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Find similar pairs
            for i in range(len(questions)):
                for j in range(i + 1, len(questions)):
                    similarity = similarity_matrix[i][j]
                    
                    if similarity >= 0.7:  # Lower threshold for semantic similarity
                        duplicate = QuestionDuplicate(
                            question1_id=questions[i].id,
                            question2_id=questions[j].id,
                            similarity_score=float(similarity),
                            similarity_type='semantic',
                            detection_method='tfidf_cosine'
                        )
                        duplicates.append(duplicate)
            
        except Exception as e:
            current_app.logger.error(f"Semantic similarity detection failed: {str(e)}")
        
        return duplicates
    
    def _detect_keyword_overlap(self, questions: List[GeneratedQuestion]) -> List[QuestionDuplicate]:
        """Detect duplicates based on keyword overlap."""
        duplicates = []
        
        for i in range(len(questions)):
            for j in range(i + 1, len(questions)):
                q1, q2 = questions[i], questions[j]
                
                if not q1.keywords or not q2.keywords:
                    continue
                
                # Calculate keyword overlap
                set1 = set(q1.keywords)
                set2 = set(q2.keywords)
                
                if not set1 or not set2:
                    continue
                
                overlap = len(set1.intersection(set2))
                union = len(set1.union(set2))
                
                if union > 0:
                    similarity = overlap / union
                    
                    if similarity >= 0.6:  # 60% keyword overlap
                        duplicate = QuestionDuplicate(
                            question1_id=q1.id,
                            question2_id=q2.id,
                            similarity_score=similarity,
                            similarity_type='concept',
                            detection_method='keyword_overlap'
                        )
                        duplicates.append(duplicate)
        
        return duplicates
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using character-based approach."""
        # Normalize texts
        text1 = re.sub(r'\W+', ' ', text1.lower()).strip()
        text2 = re.sub(r'\W+', ' ', text2.lower()).strip()
        
        if not text1 or not text2:
            return 0.0
        
        # Calculate similarity using longest common subsequence
        return self._lcs_similarity(text1, text2)
    
    def _lcs_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity using longest common subsequence."""
        words1 = text1.split()
        words2 = text2.split()
        
        if not words1 or not words2:
            return 0.0
        
        # Dynamic programming for LCS
        m, n = len(words1), len(words2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if words1[i-1] == words2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        lcs_length = dp[m][n]
        max_length = max(m, n)
        
        return lcs_length / max_length if max_length > 0 else 0.0


class QualityAssessment:
    """Assess and score question quality."""
    
    def assess_question_quality(self, question: GeneratedQuestion) -> Dict[str, float]:
        """Assess the quality of a generated question."""
        scores = {
            'clarity': self._assess_clarity(question),
            'relevance': self._assess_relevance(question),
            'difficulty_appropriateness': self._assess_difficulty(question),
            'educational_value': self._assess_educational_value(question),
            'technical_quality': self._assess_technical_quality(question)
        }
        
        # Calculate overall quality score
        weights = {
            'clarity': 0.25,
            'relevance': 0.25,
            'difficulty_appropriateness': 0.20,
            'educational_value': 0.20,
            'technical_quality': 0.10
        }
        
        overall_score = sum(
            scores[metric] * weights[metric] 
            for metric in scores
        )
        
        scores['overall'] = overall_score
        
        # Update question with scores
        question.quality_score = overall_score
        question.clarity_score = scores['clarity']
        question.relevance_score = scores['relevance']
        
        return scores
    
    def _assess_clarity(self, question: GeneratedQuestion) -> float:
        """Assess question clarity."""
        text = question.question_text
        
        # Check for clear, well-formed questions
        clarity_score = 0.5  # Base score
        
        # Question ends with question mark
        if text.strip().endswith('?'):
            clarity_score += 0.2
        
        # Reasonable length (not too short or too long)
        word_count = len(text.split())
        if 5 <= word_count <= 50:
            clarity_score += 0.2
        
        # No grammatical issues (basic check)
        if not re.search(r'\b(a an|an a)\b', text.lower()):
            clarity_score += 0.1
        
        return min(1.0, clarity_score)
    
    def _assess_relevance(self, question: GeneratedQuestion) -> float:
        """Assess question relevance to source content."""
        # This would ideally use the source content for comparison
        # For now, use available metadata
        
        relevance_score = 0.5  # Base score
        
        # Has keywords
        if question.keywords:
            relevance_score += 0.2
        
        # Has topics
        if question.topics:
            relevance_score += 0.2
        
        # Appropriate difficulty level
        if 1 <= question.difficulty_level <= 10:
            relevance_score += 0.1
        
        return min(1.0, relevance_score)
    
    def _assess_difficulty(self, question: GeneratedQuestion) -> float:
        """Assess if difficulty level is appropriate."""
        # Check if difficulty aligns with question complexity
        text_complexity = self._calculate_text_complexity(question.question_text)
        
        expected_difficulty = text_complexity * 10  # Scale to 1-10
        actual_difficulty = question.difficulty_level
        
        # Calculate how close actual is to expected
        difference = abs(expected_difficulty - actual_difficulty)
        
        # Convert to score (closer = higher score)
        if difference <= 1:
            return 1.0
        elif difference <= 2:
            return 0.8
        elif difference <= 3:
            return 0.6
        else:
            return 0.4
    
    def _assess_educational_value(self, question: GeneratedQuestion) -> float:
        """Assess educational value of the question."""
        score = 0.5  # Base score
        
        # Has explanation
        if question.explanation and len(question.explanation) > 10:
            score += 0.2
        
        # Aligned with learning objectives
        if question.learning_objective_id:
            score += 0.2
        
        # Appropriate Bloom's level
        if question.blooms_level_id:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_technical_quality(self, question: GeneratedQuestion) -> float:
        """Assess technical quality (formatting, structure, etc.)."""
        score = 0.5  # Base score
        
        text = question.question_text
        
        # No formatting issues
        if not re.search(r'[{}[\]|\\]', text):
            score += 0.2
        
        # Proper capitalization
        if text[0].isupper():
            score += 0.1
        
        # No repeated words
        words = text.lower().split()
        if len(words) == len(set(words)):
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_text_complexity(self, text: str) -> float:
        """Calculate text complexity (0-1 scale)."""
        # Simple complexity metrics
        word_count = len(text.split())
        avg_word_length = sum(len(word) for word in text.split()) / max(word_count, 1)
        
        # Normalize to 0-1 scale
        complexity = min(1.0, (avg_word_length - 3) / 7 + word_count / 100)
        
        return max(0.0, complexity)


class AIQuestionGeneratorService:
    """Main service for AI-powered question generation."""
    
    def __init__(self):
        self.content_processor = ContentProcessor()
        self.question_generator = QuestionGenerator()
        self.duplicate_detector = DuplicateDetector()
        self.quality_assessor = QualityAssessment()
    
    def create_source_content(
        self, 
        tenant_id: int, 
        creator_id: int, 
        title: str,
        description: str = None,
        content_type_name: str = 'text',
        file_path: str = None,
        url: str = None,
        text_content: str = None
    ) -> SourceContent:
        """Create and process source content."""
        
        # Get content type
        content_type = db.session.query(ContentType).filter(
            ContentType.name == content_type_name
        ).first()
        
        if not content_type:
            # Create default content type
            content_type = ContentType(
                name=content_type_name,
                description=f"Content type: {content_type_name}",
                supported_formats=['txt', 'pdf', 'docx']
            )
            db.session.add(content_type)
            db.session.commit()
        
        # Create source content
        source_content = SourceContent(
            tenant_id=tenant_id,
            creator_id=creator_id,
            title=title,
            description=description,
            content_type_id=content_type.id,
            file_path=file_path,
            url=url,
            text_content=text_content,
            processing_status='pending'
        )
        
        db.session.add(source_content)
        db.session.commit()
        
        # Process content
        self.process_source_content(source_content.id)
        
        return source_content
    
    def process_source_content(self, content_id: int) -> Dict[str, Any]:
        """Process source content to extract text and metadata."""
        source_content = db.session.query(SourceContent).get(content_id)
        if not source_content:
            return {'success': False, 'error': 'Source content not found'}
        
        try:
            # Update status
            source_content.processing_status = 'processing'
            db.session.commit()
            
            # Process content
            result = self.content_processor.process_content(source_content)
            
            if result.get('error'):
                source_content.processing_status = 'failed'
                source_content.processing_error = result['error']
            else:
                source_content.processing_status = 'completed'
                source_content.extracted_text = result['extracted_text']
                source_content.keywords = result['keywords']
                source_content.topics = result['topics']
                source_content.difficulty_level = result['difficulty_level']
                source_content.readability_score = result['readability_score']
                source_content.metadata = result['metadata']
                source_content.processed_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': not result.get('error'),
                'content': source_content.to_dict()
            }
            
        except Exception as e:
            current_app.logger.error(f"Content processing failed: {str(e)}")
            source_content.processing_status = 'failed'
            source_content.processing_error = str(e)
            db.session.commit()
            
            return {'success': False, 'error': str(e)}
    
    async def generate_questions(
        self,
        tenant_id: int,
        creator_id: int,
        source_content_id: int,
        question_count: int = 10,
        question_types: List[int] = None,
        difficulty_range: List[float] = None,
        blooms_levels: List[int] = None,
        learning_objectives: List[int] = None,
        language: str = 'en',
        topic_focus: List[str] = None,
        avoid_topics: List[str] = None,
        custom_instructions: str = None,
        ai_model: str = 'gpt-4'
    ) -> Dict[str, Any]:
        """Generate questions from source content."""
        
        # Validate source content
        source_content = db.session.query(SourceContent).filter(
            SourceContent.id == source_content_id,
            SourceContent.tenant_id == tenant_id,
            SourceContent.processing_status == 'completed'
        ).first()
        
        if not source_content:
            return {
                'success': False,
                'error': 'Source content not found or not processed'
            }
        
        # Create generation request
        request = QuestionGenerationRequest(
            tenant_id=tenant_id,
            creator_id=creator_id,
            source_content_id=source_content_id,
            question_count=question_count,
            question_types=question_types or [],
            difficulty_range=difficulty_range or [1, 10],
            blooms_levels=blooms_levels or [],
            learning_objectives=learning_objectives or [],
            language=language,
            topic_focus=topic_focus or [],
            avoid_topics=avoid_topics or [],
            custom_instructions=custom_instructions,
            ai_model=ai_model
        )
        
        db.session.add(request)
        db.session.commit()
        
        # Generate questions
        result = await self.question_generator.generate_questions(request)
        
        if result['success']:
            # Detect duplicates
            questions = result['questions']
            if len(questions) > 1:
                duplicates = self.duplicate_detector.detect_duplicates(questions)
                for duplicate in duplicates:
                    db.session.add(duplicate)
            
            # Assess quality
            for question in questions:
                self.quality_assessor.assess_question_quality(question)
            
            db.session.commit()
            
            # Update analytics
            self._update_analytics(tenant_id, request, questions)
        
        return {
            'success': result['success'],
            'request_id': request.request_id,
            'questions_generated': len(result.get('questions', [])),
            'error': result.get('error')
        }
    
    def get_generation_status(self, request_id: str) -> Dict[str, Any]:
        """Get the status of a question generation request."""
        request = db.session.query(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.request_id == request_id
        ).first()
        
        if not request:
            return {'success': False, 'error': 'Request not found'}
        
        return {
            'success': True,
            'status': request.status,
            'progress': request.progress,
            'questions_generated': request.questions_generated,
            'error_message': request.error_message
        }
    
    def get_generated_questions(
        self,
        tenant_id: int,
        request_id: str = None,
        status: str = None,
        min_quality: float = None,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """Get generated questions with filtering options."""
        
        query = db.session.query(GeneratedQuestion).join(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.tenant_id == tenant_id
        )
        
        if request_id:
            query = query.filter(QuestionGenerationRequest.request_id == request_id)
        
        if status:
            query = query.filter(GeneratedQuestion.status == status)
        
        if min_quality:
            query = query.filter(GeneratedQuestion.quality_score >= min_quality)
        
        # Pagination
        total = query.count()
        questions = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'success': True,
            'questions': [q.to_dict() for q in questions],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def approve_question(self, question_id: int, reviewer_id: int, notes: str = None) -> Dict[str, Any]:
        """Approve a generated question."""
        question = db.session.query(GeneratedQuestion).get(question_id)
        if not question:
            return {'success': False, 'error': 'Question not found'}
        
        question.status = 'approved'
        question.reviewed_by = reviewer_id
        question.review_notes = notes
        question.review_date = datetime.utcnow()
        
        # Update request stats
        request = question.generation_request
        request.questions_approved = db.session.query(GeneratedQuestion).filter(
            GeneratedQuestion.generation_request_id == request.id,
            GeneratedQuestion.status == 'approved'
        ).count()
        
        db.session.commit()
        
        return {'success': True}
    
    def reject_question(self, question_id: int, reviewer_id: int, notes: str) -> Dict[str, Any]:
        """Reject a generated question."""
        question = db.session.query(GeneratedQuestion).get(question_id)
        if not question:
            return {'success': False, 'error': 'Question not found'}
        
        question.status = 'rejected'
        question.reviewed_by = reviewer_id
        question.review_notes = notes
        question.review_date = datetime.utcnow()
        
        db.session.commit()
        
        return {'success': True}
    
    def create_question_bank(
        self,
        tenant_id: int,
        creator_id: int,
        name: str,
        description: str = None,
        category: str = None,
        auto_add_criteria: Dict[str, Any] = None
    ) -> QuestionBank:
        """Create a new question bank."""
        
        bank = QuestionBank(
            tenant_id=tenant_id,
            creator_id=creator_id,
            name=name,
            description=description,
            category=category,
            auto_add_criteria=auto_add_criteria or {}
        )
        
        db.session.add(bank)
        db.session.commit()
        
        return bank
    
    def add_question_to_bank(
        self,
        bank_id: int,
        question_id: int,
        user_id: int,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """Add a question to a question bank."""
        
        # Check if already exists
        existing = db.session.query(QuestionBankQuestion).filter(
            QuestionBankQuestion.question_bank_id == bank_id,
            QuestionBankQuestion.generated_question_id == question_id
        ).first()
        
        if existing:
            return {'success': False, 'error': 'Question already in bank'}
        
        # Add to bank
        bank_question = QuestionBankQuestion(
            question_bank_id=bank_id,
            generated_question_id=question_id,
            added_by=user_id,
            tags=tags or []
        )
        
        db.session.add(bank_question)
        
        # Update bank stats
        bank = db.session.query(QuestionBank).get(bank_id)
        if bank:
            bank.total_questions = db.session.query(QuestionBankQuestion).filter(
                QuestionBankQuestion.question_bank_id == bank_id
            ).count() + 1
            
            # Update approved questions count
            bank.approved_questions = db.session.query(QuestionBankQuestion).join(
                GeneratedQuestion
            ).filter(
                QuestionBankQuestion.question_bank_id == bank_id,
                GeneratedQuestion.status == 'approved'
            ).count()
        
        db.session.commit()
        
        return {'success': True}
    
    def get_analytics(self, tenant_id: int, days: int = 30) -> Dict[str, Any]:
        """Get question generation analytics."""
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        analytics = db.session.query(GenerationAnalytics).filter(
            GenerationAnalytics.tenant_id == tenant_id,
            GenerationAnalytics.date >= start_date
        ).all()
        
        # Aggregate data
        total_requests = sum(a.requests_created for a in analytics)
        total_questions = sum(a.questions_generated for a in analytics)
        total_approved = sum(a.questions_approved for a in analytics)
        total_cost = sum(a.total_cost for a in analytics)
        
        avg_quality = 0.0
        quality_count = 0
        for a in analytics:
            if a.avg_quality_score:
                avg_quality += a.avg_quality_score
                quality_count += 1
        
        if quality_count > 0:
            avg_quality /= quality_count
        
        return {
            'success': True,
            'period_days': days,
            'total_requests': total_requests,
            'total_questions_generated': total_questions,
            'total_questions_approved': total_approved,
            'approval_rate': total_approved / max(total_questions, 1),
            'total_cost': total_cost,
            'average_quality_score': avg_quality,
            'daily_analytics': [a.to_dict() for a in analytics]
        }
    
    def _update_analytics(
        self,
        tenant_id: int,
        request: QuestionGenerationRequest,
        questions: List[GeneratedQuestion]
    ):
        """Update daily analytics."""
        
        today = datetime.utcnow().date()
        
        # Get or create analytics record
        analytics = db.session.query(GenerationAnalytics).filter(
            GenerationAnalytics.tenant_id == tenant_id,
            func.date(GenerationAnalytics.date) == today
        ).first()
        
        if not analytics:
            analytics = GenerationAnalytics(
                tenant_id=tenant_id,
                date=datetime.combine(today, datetime.min.time())
            )
            db.session.add(analytics)
        
        # Update metrics
        analytics.requests_completed += 1
        analytics.questions_generated += len(questions)
        analytics.total_tokens_used += request.total_tokens_used
        analytics.total_cost += request.cost_estimate
        
        if questions:
            quality_scores = [q.quality_score for q in questions if q.quality_score]
            if quality_scores:
                analytics.avg_quality_score = sum(quality_scores) / len(quality_scores)
        
        db.session.commit()
    
    def initialize_default_data(self):
        """Initialize default question types and Bloom's taxonomy levels."""
        
        # Create default question types
        default_types = [
            ('multiple_choice', 'Multiple Choice', 'Questions with multiple options and one correct answer'),
            ('true_false', 'True/False', 'Questions requiring true or false responses'),
            ('fill_in_blank', 'Fill in the Blank', 'Questions with missing words to be filled'),
            ('short_answer', 'Short Answer', 'Questions requiring brief written responses'),
            ('essay', 'Essay', 'Questions requiring detailed written responses'),
            ('matching', 'Matching', 'Questions requiring matching of related items'),
            ('ordering', 'Ordering/Sequencing', 'Questions requiring items to be put in order')
        ]
        
        for name, display_name, description in default_types:
            existing = db.session.query(QuestionType).filter(
                QuestionType.name == name
            ).first()
            
            if not existing:
                question_type = QuestionType(
                    name=name,
                    display_name=display_name,
                    description=description
                )
                db.session.add(question_type)
        
        # Create Bloom's taxonomy levels
        blooms_levels = [
            ('remember', 1, 'Recall facts and basic concepts', ['define', 'list', 'identify', 'name', 'state']),
            ('understand', 2, 'Explain ideas or concepts', ['explain', 'describe', 'summarize', 'interpret', 'compare']),
            ('apply', 3, 'Use information in new situations', ['apply', 'demonstrate', 'use', 'solve', 'implement']),
            ('analyze', 4, 'Draw connections among ideas', ['analyze', 'compare', 'contrast', 'examine', 'categorize']),
            ('evaluate', 5, 'Justify a stand or decision', ['evaluate', 'critique', 'assess', 'judge', 'defend']),
            ('create', 6, 'Produce new or original work', ['create', 'design', 'compose', 'develop', 'formulate'])
        ]
        
        for level, order, description, keywords in blooms_levels:
            existing = db.session.query(BloomsTaxonomy).filter(
                BloomsTaxonomy.level == level
            ).first()
            
            if not existing:
                blooms = BloomsTaxonomy(
                    level=level,
                    order=order,
                    description=description,
                    keywords=keywords
                )
                db.session.add(blooms)
        
        # Create default content types
        default_content_types = [
            ('text', 'Plain Text', ['txt']),
            ('document', 'Document', ['pdf', 'docx', 'doc']),
            ('audio', 'Audio', ['mp3', 'wav', 'm4a']),
            ('video', 'Video', ['mp4', 'avi', 'mov']),
            ('web', 'Web Content', ['url'])
        ]
        
        for name, description, formats in default_content_types:
            existing = db.session.query(ContentType).filter(
                ContentType.name == name
            ).first()
            
            if not existing:
                content_type = ContentType(
                    name=name,
                    description=description,
                    supported_formats=formats
                )
                db.session.add(content_type)
        
        db.session.commit()