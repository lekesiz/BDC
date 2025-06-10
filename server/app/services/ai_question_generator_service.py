from flask_babel import _

_('services_ai_question_generator_service.message.ai_powered_question_generation'
    )
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
from flask_babel import _, lazy_gettext as _l
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
    HAS_NLP_LIBRARIES = False
from app.extensions import db
from app.models.ai_question_generation import ContentType, QuestionType, BloomsTaxonomy, LearningObjective, QuestionGenerationRequest, GeneratedQuestion, QuestionDuplicate, QuestionBank, QuestionBankQuestion, GenerationAnalytics
from app.utils.ai import configure_openai


class ContentProcessor:
    _('services_ai_question_generator_service.message.process_various_content_types'
        )

    def __init__(self):
        self.supported_formats = {'pdf': self._process_pdf, 'docx': self.
            _process_docx, 'txt': self._process_txt, _(
            'services_ai_question_generator_service.message.mp3_1'): self.
            _process_audio, _('services_storage_service.message.mp4'): self
            ._process_video, 'wav': self._process_audio, 'url': self.
            _process_url}
        if HAS_NLP_LIBRARIES:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                pass
                self.nlp = None
        else:
            self.nlp = None

    def process_content(self, source_content: Any) -> Dict[str, Any]:
        _('services_ai_question_generator_service.message.process_source_content_and_ext'
            )
        try:
            result = {'extracted_text': '', 'keywords': [], 'topics': [],
                'difficulty_level': 5.0, 'readability_score': 0.0,
                'metadata': {}, 'error': None}
            if source_content.file_path:
                file_ext = Path(source_content.file_path).suffix.lower(
                    ).lstrip('.')
                if file_ext in self.supported_formats:
                    result = self.supported_formats[file_ext](source_content
                        .file_path)
                else:
                    result['error'] = f'Unsupported file format: {file_ext}'
            elif source_content.url:
                result = self.supported_formats['url'](source_content.url)
            elif source_content.text_content:
                result = self._process_text(source_content.text_content)
            else:
                result['error'] = _(
                    'services_ai_question_generator_service.message.no_content_source_provided'
                    )
            if result['extracted_text'] and not result['error']:
                result = self._enhance_with_nlp(result)
            return result
        except Exception as e:
            current_app.logger.error(f'Error processing content: {str(e)}')
            return {'extracted_text': '', 'keywords': [], 'topics': [],
                'difficulty_level': 5.0, 'readability_score': 0.0,
                'metadata': {}, 'error': str(e)}

    def _process_pdf(self, file_path: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.label.process_pdf_files')
        try:
            text = ''
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + '\n'
            return self._process_text(text)
        except Exception as e:
            return {'error': f'PDF processing failed: {str(e)}'}

    def _process_docx(self, file_path: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.label.process_word_documents'
            )
        try:
            doc = docx.Document(file_path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return self._process_text(text)
        except Exception as e:
            return {'error': f'DOCX processing failed: {str(e)}'}

    def _process_txt(self, file_path: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.label.process_text_files')
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            return self._process_text(text)
        except Exception as e:
            return {'error': f'TXT processing failed: {str(e)}'}

    def _process_audio(self, file_path: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.process_audio_files_using_whis'
            )
        try:
            model = whisper.load_model('base')
            result = model.transcribe(file_path)
            text = result['text']
            metadata = {'duration': result.get('duration', 0), 'language':
                result.get('language', 'unknown'), 'segments': len(result.
                get('segments', []))}
            processed = self._process_text(text)
            processed['metadata'].update(metadata)
            return processed
        except Exception as e:
            return {'error': f'Audio processing failed: {str(e)}'}

    def _process_video(self, file_path: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.process_video_files_extract_a'
            )
        return self._process_audio(file_path)

    def _process_url(self, url: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.label.process_web_content')
        try:
            headers = {_('file_upload_api_example.label.user_agent_1'): _(
                'services_ai_question_generator_service.message.mozilla_5_0_windows_nt_10_0'
                )}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(['script', 'style']):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.
                split('  '))
            text = ' '.join(chunk for chunk in chunks if chunk)
            metadata = {'url': url, 'title': soup.title.string if soup.
                title else _('analytics_data_export.label.unknown'),
                'content_length': len(text)}
            processed = self._process_text(text)
            processed['metadata'].update(metadata)
            return processed
        except Exception as e:
            return {'error': f'URL processing failed: {str(e)}'}

    def _process_text(self, text: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.process_raw_text_content'
            )
        try:
            text = re.sub(_(
                'services_ai_question_generator_service.message.s'), ' ', text
                ).strip()
            readability_score = 0.0
            if HAS_NLP_LIBRARIES:
                try:
                    readability_score = flesch_reading_ease(text)
                except:
                    pass
            difficulty_level = self._estimate_difficulty(text,
                readability_score)
            return {'extracted_text': text, 'keywords': [], 'topics': [],
                'difficulty_level': difficulty_level, 'readability_score':
                readability_score, 'metadata': {'word_count': len(text.
                split()), 'character_count': len(text)}, 'error': None}
        except Exception as e:
            return {'error': f'Text processing failed: {str(e)}'}

    def _enhance_with_nlp(self, result: Dict[str, Any]) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.enhance_text_analysis_with_nlp'
            )
        if not HAS_NLP_LIBRARIES or not self.nlp:
            return result
        try:
            text = result['extracted_text']
            doc = self.nlp(text[:1000000])
            keywords = []
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'EVENT',
                    'WORK_OF_ART']:
                    keywords.append(ent.text)
            for token in doc:
                if token.pos_ in ['NOUN', 'PROPN'] and len(token.text
                    ) > 3 and not token.is_stop and token.is_alpha:
                    keywords.append(token.text)
            keywords = list(set(keywords))[:20]
            topics = self._extract_topics(keywords, text)
            result['keywords'] = keywords
            result['topics'] = topics
        except Exception as e:
            current_app.logger.warning(f'NLP enhancement failed: {str(e)}')
        return result

    def _extract_topics(self, keywords: List[str], text: str) ->List[str]:
        """Extract main topics from text."""
        topics = []
        topic_domains = {'technology': ['computer', 'software', 'digital',
            'internet', 'data'], 'science': ['research', 'study',
            'analysis', 'experiment', 'theory'], 'business': ['company',
            'market', 'business', 'profit', 'customer'], 'education': [
            'learning', 'teaching', 'student', 'school', 'education'],
            'health': ['health', 'medical', 'patient', 'treatment',
            'disease'], 'history': ['history', 'historical', 'past',
            'ancient', 'century'], 'literature': ['book', 'author', 'story',
            'novel', 'literature']}
        text_lower = text.lower()
        for topic, domain_words in topic_domains.items():
            score = sum(1 for word in domain_words if word in text_lower)
            if score >= 2:
                topics.append(topic)
        return topics[:5]

    def _estimate_difficulty(self, text: str, readability_score: float
        ) ->float:
        _('services_ai_question_generator_service.message.estimate_content_difficulty_on'
            )
        if readability_score >= 90:
            base_difficulty = 2.0
        elif readability_score >= 80:
            base_difficulty = 3.0
        elif readability_score >= 70:
            base_difficulty = 4.0
        elif readability_score >= 60:
            base_difficulty = 5.0
        elif readability_score >= 50:
            base_difficulty = 6.0
        elif readability_score >= 30:
            base_difficulty = 7.0
        else:
            base_difficulty = 8.0
        complexity_indicators = [len(re.findall(_(
            'services_ai_question_generator_service.message.b_w_10_b'),
            text)), len(re.findall(_(
            'services_ai_question_generator_service.message.'), text)), len
            (re.findall(_(
            'services_ai_question_generator_service.message.b_however_moreover_furtherm'
            ), text.lower()))]
        complexity_score = sum(complexity_indicators) / max(len(text.split(
            )), 1) * 100
        if complexity_score > 5:
            base_difficulty = min(10.0, base_difficulty + 1.0)
        elif complexity_score > 10:
            base_difficulty = min(10.0, base_difficulty + 2.0)
        return round(base_difficulty, 1)


class QuestionGenerator:
    _('services_ai_question_generator_service.message.generate_questions_using_ai_mo'
        )

    def __init__(self):
        self.question_type_prompts = {'multiple_choice': self.
            _get_mcq_prompt, 'true_false': self._get_tf_prompt,
            'fill_in_blank': self._get_fib_prompt, 'short_answer': self.
            _get_sa_prompt, 'essay': self._get_essay_prompt, 'matching':
            self._get_matching_prompt, 'ordering': self._get_ordering_prompt}

    async def generate_questions(self, request: QuestionGenerationRequest
        ) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.generate_questions_based_on_th'
            )
        configure_openai()
        if not openai.api_key:
            return {'success': False, 'error': _(
                'services_ai_question_generator_service.message.openai_api_key_not_configured'
                ), 'questions': []}
        try:
            request.status = 'processing'
            request.started_at = datetime.utcnow()
            db.session.commit()
            source_content = request.source_content
            if not source_content.extracted_text:
                return {'success': False, 'error': _(
                    'services_ai_question_generator_service.message.source_content_not_processed'
                    ), 'questions': []}
            question_types = self._get_question_types(request.question_types)
            if not question_types:
                return {'success': False, 'error': _(
                    'services_ai_question_generator_service.validation.no_valid_question_types_specif'
                    ), 'questions': []}
            all_questions = []
            total_tokens = 0
            questions_per_type = max(1, request.question_count // len(
                question_types))
            for i, question_type in enumerate(question_types):
                if i == len(question_types) - 1:
                    questions_count = request.question_count - len(
                        all_questions)
                else:
                    questions_count = questions_per_type
                if questions_count <= 0:
                    continue
                type_result = await self._generate_questions_for_type(request,
                    question_type, questions_count)
                if type_result['success']:
                    all_questions.extend(type_result['questions'])
                    total_tokens += type_result.get('tokens_used', 0)
                progress = (i + 1) / len(question_types) * 0.8
                request.progress = progress
                db.session.commit()
            processed_questions = await self._post_process_questions(
                all_questions, request)
            request.status = 'completed'
            request.completed_at = datetime.utcnow()
            request.questions_generated = len(processed_questions)
            request.total_tokens_used = total_tokens
            request.cost_estimate = self._calculate_cost(total_tokens)
            request.progress = 1.0
            db.session.commit()
            return {'success': True, 'questions': processed_questions,
                'tokens_used': total_tokens, 'cost_estimate': request.
                cost_estimate}
        except Exception as e:
            current_app.logger.error(f'Question generation failed: {str(e)}')
            request.status = 'failed'
            request.error_message = str(e)
            db.session.commit()
            return {'success': False, 'error': str(e), 'questions': []}

    async def _generate_questions_for_type(self, request:
        QuestionGenerationRequest, question_type: QuestionType, count: int
        ) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.generate_questions_for_a_speci'
            )
        try:
            prompt_func = self.question_type_prompts.get(question_type.name)
            if not prompt_func:
                return {'success': False, 'error':
                    f'No prompt template for question type: {question_type.name}'
                    , 'questions': []}
            prompt = prompt_func(request, count)
            response = await self._call_openai_api(prompt, request.ai_model)
            if not response['success']:
                return response
            questions = self._parse_ai_response(response['content'],
                question_type, request)
            return {'success': True, 'questions': questions, 'tokens_used':
                response.get('tokens_used', 0)}
        except Exception as e:
            current_app.logger.error(
                f'Error generating {question_type.name} questions: {str(e)}')
            return {'success': False, 'error': str(e), 'questions': []}

    async def _call_openai_api(self, prompt: str, model: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.make_api_call_to_openai'
            )
        try:
            response = openai.ChatCompletion.create(model=model, messages=[
                {'role': 'system', 'content': _(
                'services_ai_question_generator_service.message.you_are_an_expert_educational'
                )}, {'role': 'user', 'content': prompt}], temperature=0.7,
                max_tokens=3000)
            return {'success': True, 'content': response.choices[0].message
                ['content'], 'tokens_used': response['usage']['total_tokens']}
        except Exception as e:
            current_app.logger.error(f'OpenAI API call failed: {str(e)}')
            return {'success': False, 'error': str(e)}

    def _parse_ai_response(self, response_content: str, question_type:
        QuestionType, request: QuestionGenerationRequest) ->List[Dict[str, Any]
        ]:
        _('services_ai_question_generator_service.message.parse_ai_response_into_structu'
            )
        questions = []
        try:
            json_match = re.search(_(
                'services_ai_question_generator_service.message.json_n_n'),
                response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response_content
            json_str = re.sub(_(
                'services_ai_question_generator_service.message._1'), '',
                json_str)
            json_str = re.sub(_(
                'services_ai_question_generator_service.message._2'), '',
                json_str)
            parsed_data = json.loads(json_str)
            if isinstance(parsed_data, list):
                questions_data = parsed_data
            elif isinstance(parsed_data, dict) and 'questions' in parsed_data:
                questions_data = parsed_data['questions']
            else:
                questions_data = [parsed_data]
            for q_data in questions_data:
                question = self._create_question_from_data(q_data,
                    question_type, request)
                if question:
                    questions.append(question)
        except json.JSONDecodeError:
            questions = self._parse_text_response(response_content,
                question_type, request)
        return questions

    def _create_question_from_data(self, q_data: Dict[str, Any],
        question_type: QuestionType, request: QuestionGenerationRequest
        ) ->Optional[Dict[str, Any]]:
        """Create a question object from parsed data."""
        try:
            question = {'question_text': q_data.get('question', q_data.get(
                'text', '')), 'question_type_id': question_type.id,
                'difficulty_level': q_data.get('difficulty', 5.0),
                'explanation': q_data.get('explanation', ''), 'keywords':
                q_data.get('keywords', []), 'topics': q_data.get('topics',
                []), 'correct_answer': q_data.get('correct_answer'),
                'question_options': q_data.get('options'),
                'blooms_level_id': self._get_blooms_level_id(q_data.get(
                'blooms_level')), 'quality_score': q_data.get(
                'quality_score', 0.8), 'ai_confidence': q_data.get(
                'confidence', 0.8)}
            if not question['question_text']:
                return None
            return question
        except Exception as e:
            current_app.logger.error(
                f'Error creating question from data: {str(e)}')
            return None

    def _parse_text_response(self, response_content: str, question_type:
        QuestionType, request: QuestionGenerationRequest) ->List[Dict[str, Any]
        ]:
        _('services_ai_question_generator_service.message.fallback_text_parsing_for_non'
            )
        questions = []
        question_patterns = [_(
            'services_ai_question_generator_service.message.d_s'), _(
            'services_ai_question_generator_service.label.question_d'), _(
            'services_ai_question_generator_service.label.q_d'), _(
            'services_ai_question_generator_service.message.n_n')]
        sections = response_content.split('\n\n')
        for section in sections:
            section = section.strip()
            if len(section) > 20:
                lines = section.split('\n')
                question_text = lines[0].strip()
                question_text = re.sub(_(
                    'services_ai_question_generator_service.message.d_s_1'),
                    '', question_text)
                question_text = re.sub(_(
                    'services_ai_question_generator_service.message.question_d_s'
                    ), '', question_text)
                question_text = re.sub(_(
                    'services_ai_question_generator_service.message.q_d_s'),
                    '', question_text)
                if question_text:
                    question = {'question_text': question_text,
                        'question_type_id': question_type.id,
                        'difficulty_level': 5.0, 'explanation': '',
                        'keywords': [], 'topics': [], 'correct_answer':
                        None, 'question_options': None, 'quality_score': 
                        0.7, 'ai_confidence': 0.7}
                    questions.append(question)
        return questions

    async def _post_process_questions(self, questions: List[Dict[str, Any]],
        request: QuestionGenerationRequest) ->List[GeneratedQuestion]:
        _('services_ai_question_generator_service.label.post_process_generated_questio'
            )
        processed_questions = []
        for q_data in questions:
            try:
                question = GeneratedQuestion(generation_request_id=request.
                    id, question_type_id=q_data['question_type_id'],
                    question_text=q_data['question_text'], question_options
                    =q_data.get('question_options'), correct_answer=q_data.
                    get('correct_answer'), explanation=q_data.get(
                    'explanation', ''), difficulty_level=q_data.get(
                    'difficulty_level', 5.0), blooms_level_id=q_data.get(
                    'blooms_level_id'), keywords=q_data.get('keywords', []),
                    topics=q_data.get('topics', []), quality_score=q_data.
                    get('quality_score', 0.8), ai_confidence=q_data.get(
                    'ai_confidence', 0.8), generation_prompt=
                    f'Generated for request {request.id}', tokens_used=50)
                db.session.add(question)
                processed_questions.append(question)
            except Exception as e:
                current_app.logger.error(
                    f'Error creating question object: {str(e)}')
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f'Error saving questions: {str(e)}')
            db.session.rollback()
        return processed_questions

    def _get_question_types(self, type_ids: List[int]) ->List[QuestionType]:
        """Get question type objects from IDs."""
        if not type_ids:
            return db.session.query(QuestionType).filter(QuestionType.name ==
                'multiple_choice', QuestionType.is_active == True).all()
        return db.session.query(QuestionType).filter(QuestionType.id.in_(
            type_ids), QuestionType.is_active == True).all()

    def _get_blooms_level_id(self, level_name: Optional[str]) ->Optional[int]:
        """Get Bloom's taxonomy level ID from name."""
        if not level_name:
            return None
        level = db.session.query(BloomsTaxonomy).filter(func.lower(
            BloomsTaxonomy.level) == level_name.lower()).first()
        return level.id if level else None

    def _calculate_cost(self, tokens_used: int) ->float:
        _('services_ai_question_generator_service.message.calculate_estimated_cost_based'
            )
        cost_per_1k_tokens = 0.03
        return tokens_used / 1000 * cost_per_1k_tokens

    def _get_mcq_prompt(self, request: QuestionGenerationRequest, count: int
        ) ->str:
        _('services_ai_question_generator_service.message.generate_prompt_for_multiple_c'
            )
        content = request.source_content.extracted_text[:4000]
        difficulty_text = self._get_difficulty_text(request.difficulty_range)
        topics_text = ', '.join(request.topic_focus
            ) if request.topic_focus else _(
            'services_ai_question_generator_service.message.any_relevant_topics'
            )
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

    def _get_tf_prompt(self, request: QuestionGenerationRequest, count: int
        ) ->str:
        _('services_ai_question_generator_service.message.generate_prompt_for_true_false'
            )
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

    def _get_fib_prompt(self, request: QuestionGenerationRequest, count: int
        ) ->str:
        _('services_ai_question_generator_service.message.generate_prompt_for_fill_in_th'
            )
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

    def _get_sa_prompt(self, request: QuestionGenerationRequest, count: int
        ) ->str:
        _('services_ai_question_generator_service.message.generate_prompt_for_short_answ'
            )
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

    def _get_essay_prompt(self, request: QuestionGenerationRequest, count: int
        ) ->str:
        _('services_ai_question_generator_service.message.generate_prompt_for_essay_ques'
            )
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

    def _get_matching_prompt(self, request: QuestionGenerationRequest,
        count: int) ->str:
        _('services_ai_question_generator_service.message.generate_prompt_for_matching_q'
            )
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

    def _get_ordering_prompt(self, request: QuestionGenerationRequest,
        count: int) ->str:
        _('services_ai_question_generator_service.message.generate_prompt_for_ordering_s'
            )
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

    def _get_difficulty_text(self, difficulty_range: List[float]) ->str:
        _('services_ai_question_generator_service.message.convert_difficulty_range_to_de'
            )
        min_diff, max_diff = difficulty_range
        if max_diff <= 3:
            return _(
                'services_ai_question_generator_service.message.easy_basic_recall_and_recogni'
                )
        elif max_diff <= 5:
            return _(
                'services_ai_question_generator_service.message.easy_to_medium_understanding'
                )
        elif max_diff <= 7:
            return _(
                'services_ai_question_generator_service.message.medium_application_and_analys'
                )
        elif max_diff <= 9:
            return _(
                'services_ai_question_generator_service.message.hard_synthesis_and_evaluation'
                )
        else:
            return _(
                'services_ai_question_generator_service.message.very_hard_expert_level_analys'
                )


class DuplicateDetector:
    _('services_ai_question_generator_service.message.detect_duplicate_questions_usi'
        )

    def __init__(self):
        self.similarity_threshold = 0.8
        if HAS_NLP_LIBRARIES:
            self.vectorizer = TfidfVectorizer(stop_words='english',
                max_features=1000)
        else:
            self.vectorizer = None

    def detect_duplicates(self, questions: List[GeneratedQuestion]) ->List[
        QuestionDuplicate]:
        _('services_ai_question_generator_service.message.detect_potential_duplicate_que'
            )
        duplicates = []
        if len(questions) < 2:
            return duplicates
        text_duplicates = self._detect_text_similarity(questions)
        duplicates.extend(text_duplicates)
        if self.vectorizer:
            semantic_duplicates = self._detect_semantic_similarity(questions)
            duplicates.extend(semantic_duplicates)
        keyword_duplicates = self._detect_keyword_overlap(questions)
        duplicates.extend(keyword_duplicates)
        return duplicates

    def _detect_text_similarity(self, questions: List[GeneratedQuestion]
        ) ->List[QuestionDuplicate]:
        _('services_ai_question_generator_service.message.detect_duplicates_based_on_tex'
            )
        duplicates = []
        for i in range(len(questions)):
            for j in range(i + 1, len(questions)):
                q1, q2 = questions[i], questions[j]
                similarity = self._calculate_text_similarity(q1.
                    question_text, q2.question_text)
                if similarity >= self.similarity_threshold:
                    duplicate = QuestionDuplicate(question1_id=q1.id,
                        question2_id=q2.id, similarity_score=similarity,
                        similarity_type='text', detection_method=
                        'text_similarity')
                    duplicates.append(duplicate)
        return duplicates

    def _detect_semantic_similarity(self, questions: List[GeneratedQuestion]
        ) ->List[QuestionDuplicate]:
        _('services_ai_question_generator_service.message.detect_duplicates_based_on_sem'
            )
        duplicates = []
        try:
            texts = [q.question_text for q in questions]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            for i in range(len(questions)):
                for j in range(i + 1, len(questions)):
                    similarity = similarity_matrix[i][j]
                    if similarity >= 0.7:
                        duplicate = QuestionDuplicate(question1_id=
                            questions[i].id, question2_id=questions[j].id,
                            similarity_score=float(similarity),
                            similarity_type='semantic', detection_method=
                            'tfidf_cosine')
                        duplicates.append(duplicate)
        except Exception as e:
            current_app.logger.error(
                f'Semantic similarity detection failed: {str(e)}')
        return duplicates

    def _detect_keyword_overlap(self, questions: List[GeneratedQuestion]
        ) ->List[QuestionDuplicate]:
        _('services_ai_question_generator_service.message.detect_duplicates_based_on_key'
            )
        duplicates = []
        for i in range(len(questions)):
            for j in range(i + 1, len(questions)):
                q1, q2 = questions[i], questions[j]
                if not q1.keywords or not q2.keywords:
                    continue
                set1 = set(q1.keywords)
                set2 = set(q2.keywords)
                if not set1 or not set2:
                    continue
                overlap = len(set1.intersection(set2))
                union = len(set1.union(set2))
                if union > 0:
                    similarity = overlap / union
                    if similarity >= 0.6:
                        duplicate = QuestionDuplicate(question1_id=q1.id,
                            question2_id=q2.id, similarity_score=similarity,
                            similarity_type='concept', detection_method=
                            'keyword_overlap')
                        duplicates.append(duplicate)
        return duplicates

    def _calculate_text_similarity(self, text1: str, text2: str) ->float:
        _('services_ai_question_generator_service.message.calculate_text_similarity_usin'
            )
        text1 = re.sub(_(
            'services_ai_question_generator_service.message.w_1'), ' ',
            text1.lower()).strip()
        text2 = re.sub(_(
            'services_ai_question_generator_service.message.w_1'), ' ',
            text2.lower()).strip()
        if not text1 or not text2:
            return 0.0
        return self._lcs_similarity(text1, text2)

    def _lcs_similarity(self, text1: str, text2: str) ->float:
        _('services_ai_question_generator_service.message.calculate_similarity_using_lon'
            )
        words1 = text1.split()
        words2 = text2.split()
        if not words1 or not words2:
            return 0.0
        m, n = len(words1), len(words2)
        dp = [([0] * (n + 1)) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if words1[i - 1] == words2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        lcs_length = dp[m][n]
        max_length = max(m, n)
        return lcs_length / max_length if max_length > 0 else 0.0


class QualityAssessment:
    _('services_ai_question_generator_service.message.assess_and_score_question_qual'
        )

    def assess_question_quality(self, question: GeneratedQuestion) ->Dict[
        str, float]:
        _('services_ai_question_generator_service.message.assess_the_quality_of_a_genera'
            )
        scores = {'clarity': self._assess_clarity(question), 'relevance':
            self._assess_relevance(question), 'difficulty_appropriateness':
            self._assess_difficulty(question), 'educational_value': self.
            _assess_educational_value(question), 'technical_quality': self.
            _assess_technical_quality(question)}
        weights = {'clarity': 0.25, 'relevance': 0.25,
            'difficulty_appropriateness': 0.2, 'educational_value': 0.2,
            'technical_quality': 0.1}
        overall_score = sum(scores[metric] * weights[metric] for metric in
            scores)
        scores['overall'] = overall_score
        question.quality_score = overall_score
        question.clarity_score = scores['clarity']
        question.relevance_score = scores['relevance']
        return scores

    def _assess_clarity(self, question: GeneratedQuestion) ->float:
        _('services_ai_question_generator_service.label.assess_question_clarity'
            )
        text = question.question_text
        clarity_score = 0.5
        if text.strip().endswith('?'):
            clarity_score += 0.2
        word_count = len(text.split())
        if 5 <= word_count <= 50:
            clarity_score += 0.2
        if not re.search(_(
            'services_ai_question_generator_service.message.b_a_an_an_a_b'),
            text.lower()):
            clarity_score += 0.1
        return min(1.0, clarity_score)

    def _assess_relevance(self, question: GeneratedQuestion) ->float:
        _('services_ai_question_generator_service.message.assess_question_relevance_to_s'
            )
        relevance_score = 0.5
        if question.keywords:
            relevance_score += 0.2
        if question.topics:
            relevance_score += 0.2
        if 1 <= question.difficulty_level <= 10:
            relevance_score += 0.1
        return min(1.0, relevance_score)

    def _assess_difficulty(self, question: GeneratedQuestion) ->float:
        _('services_ai_question_generator_service.message.assess_if_difficulty_level_is'
            )
        text_complexity = self._calculate_text_complexity(question.
            question_text)
        expected_difficulty = text_complexity * 10
        actual_difficulty = question.difficulty_level
        difference = abs(expected_difficulty - actual_difficulty)
        if difference <= 1:
            return 1.0
        elif difference <= 2:
            return 0.8
        elif difference <= 3:
            return 0.6
        else:
            return 0.4

    def _assess_educational_value(self, question: GeneratedQuestion) ->float:
        _('services_ai_question_generator_service.message.assess_educational_value_of_th'
            )
        score = 0.5
        if question.explanation and len(question.explanation) > 10:
            score += 0.2
        if question.learning_objective_id:
            score += 0.2
        if question.blooms_level_id:
            score += 0.1
        return min(1.0, score)

    def _assess_technical_quality(self, question: GeneratedQuestion) ->float:
        _('services_ai_question_generator_service.validation.assess_technical_quality_form'
            )
        score = 0.5
        text = question.question_text
        if not re.search(_(
            'services_ai_question_generator_service.message._3'), text):
            score += 0.2
        if text[0].isupper():
            score += 0.1
        words = text.lower().split()
        if len(words) == len(set(words)):
            score += 0.2
        return min(1.0, score)

    def _calculate_text_complexity(self, text: str) ->float:
        _('services_ai_question_generator_service.message.calculate_text_complexity_0_1'
            )
        word_count = len(text.split())
        avg_word_length = sum(len(word) for word in text.split()) / max(
            word_count, 1)
        complexity = min(1.0, (avg_word_length - 3) / 7 + word_count / 100)
        return max(0.0, complexity)


class AIQuestionGeneratorService:
    _('services_ai_question_generator_service.message.main_service_for_ai_powered_qu'
        )

    def __init__(self):
        self.content_processor = ContentProcessor()
        self.question_generator = QuestionGenerator()
        self.duplicate_detector = DuplicateDetector()
        self.quality_assessor = QualityAssessment()

    def create_source_content(self, tenant_id: int, creator_id: int, title:
        str, description: str=None, content_type_name: str='text',
        file_path: str=None, url: str=None, text_content: str=None
        ) -> Any:
        _('services_ai_question_generator_service.message.create_and_process_source_cont'
            )
        content_type = db.session.query(ContentType).filter(ContentType.
            name == content_type_name).first()
        if not content_type:
            content_type = ContentType(name=content_type_name, description=
                f'Content type: {content_type_name}', supported_formats=[
                'txt', 'pdf', 'docx'])
            db.session.add(content_type)
            db.session.commit()
        source_content = SourceContent(tenant_id=tenant_id, creator_id=
            creator_id, title=title, description=description,
            content_type_id=content_type.id, file_path=file_path, url=url,
            text_content=text_content, processing_status='pending')
        db.session.add(source_content)
        db.session.commit()
        self.process_source_content(source_content.id)
        return source_content

    def process_source_content(self, content_id: int) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.process_source_content_to_extr'
            )
        source_content = db.session.query(SourceContent).get(content_id)
        if not source_content:
            return {'success': False, 'error': _(
                'services_ai_question_generator_service.message.source_content_not_found'
                )}
        try:
            source_content.processing_status = 'processing'
            db.session.commit()
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
            return {'success': not result.get('error'), 'content':
                source_content.to_dict()}
        except Exception as e:
            current_app.logger.error(f'Content processing failed: {str(e)}')
            source_content.processing_status = 'failed'
            source_content.processing_error = str(e)
            db.session.commit()
            return {'success': False, 'error': str(e)}

    async def generate_questions(self, tenant_id: int, creator_id: int,
        source_content_id: int, question_count: int=10, question_types:
        List[int]=None, difficulty_range: List[float]=None, blooms_levels:
        List[int]=None, learning_objectives: List[int]=None, language: str=
        'en', topic_focus: List[str]=None, avoid_topics: List[str]=None,
        custom_instructions: str=None, ai_model: str=_(
        'orchestration_examples.message.gpt_4_2')) ->Dict[str, Any]:
        """Generate questions from source content."""
        source_content = db.session.query(SourceContent).filter(
            SourceContent.id == source_content_id, SourceContent.tenant_id ==
            tenant_id, SourceContent.processing_status == 'completed').first()
        if not source_content:
            return {'success': False, 'error': _(
                'services_ai_question_generator_service.message.source_content_not_found_or_no'
                )}
        request = QuestionGenerationRequest(tenant_id=tenant_id, creator_id
            =creator_id, source_content_id=source_content_id,
            question_count=question_count, question_types=question_types or
            [], difficulty_range=difficulty_range or [1, 10], blooms_levels
            =blooms_levels or [], learning_objectives=learning_objectives or
            [], language=language, topic_focus=topic_focus or [],
            avoid_topics=avoid_topics or [], custom_instructions=
            custom_instructions, ai_model=ai_model)
        db.session.add(request)
        db.session.commit()
        result = await self.question_generator.generate_questions(request)
        if result['success']:
            questions = result['questions']
            if len(questions) > 1:
                duplicates = self.duplicate_detector.detect_duplicates(
                    questions)
                for duplicate in duplicates:
                    db.session.add(duplicate)
            for question in questions:
                self.quality_assessor.assess_question_quality(question)
            db.session.commit()
            self._update_analytics(tenant_id, request, questions)
        return {'success': result['success'], 'request_id': request.
            request_id, 'questions_generated': len(result.get('questions',
            [])), 'error': result.get('error')}

    def get_generation_status(self, request_id: str) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.get_the_status_of_a_question_g'
            )
        request = db.session.query(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.request_id == request_id).first()
        if not request:
            return {'success': False, 'error': _(
                'services_ai_question_generator_service.label.request_not_found'
                )}
        return {'success': True, 'status': request.status, 'progress':
            request.progress, 'questions_generated': request.
            questions_generated, 'error_message': request.error_message}

    def get_generated_questions(self, tenant_id: int, request_id: str=None,
        status: str=None, min_quality: float=None, page: int=1, per_page:
        int=20) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.get_generated_questions_with_f'
            )
        query = db.session.query(GeneratedQuestion).join(
            QuestionGenerationRequest).filter(QuestionGenerationRequest.
            tenant_id == tenant_id)
        if request_id:
            query = query.filter(QuestionGenerationRequest.request_id ==
                request_id)
        if status:
            query = query.filter(GeneratedQuestion.status == status)
        if min_quality:
            query = query.filter(GeneratedQuestion.quality_score >= min_quality
                )
        total = query.count()
        questions = query.offset((page - 1) * per_page).limit(per_page).all()
        return {'success': True, 'questions': [q.to_dict() for q in
            questions], 'total': total, 'page': page, 'per_page': per_page,
            'pages': (total + per_page - 1) // per_page}

    def approve_question(self, question_id: int, reviewer_id: int, notes:
        str=None) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.approve_a_generated_question'
            )
        question = db.session.query(GeneratedQuestion).get(question_id)
        if not question:
            return {'success': False, 'error': _(
                'services_ai_question_generator_service.label.question_not_found_1'
                )}
        question.status = 'approved'
        question.reviewed_by = reviewer_id
        question.review_notes = notes
        question.review_date = datetime.utcnow()
        request = question.generation_request
        request.questions_approved = db.session.query(GeneratedQuestion
            ).filter(GeneratedQuestion.generation_request_id == request.id,
            GeneratedQuestion.status == 'approved').count()
        db.session.commit()
        return {'success': True}

    def reject_question(self, question_id: int, reviewer_id: int, notes: str
        ) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.reject_a_generated_question'
            )
        question = db.session.query(GeneratedQuestion).get(question_id)
        if not question:
            return {'success': False, 'error': _(
                'services_ai_question_generator_service.label.question_not_found_1'
                )}
        question.status = 'rejected'
        question.reviewed_by = reviewer_id
        question.review_notes = notes
        question.review_date = datetime.utcnow()
        db.session.commit()
        return {'success': True}

    def create_question_bank(self, tenant_id: int, creator_id: int, name:
        str, description: str=None, category: str=None, auto_add_criteria:
        Dict[str, Any]=None) ->QuestionBank:
        _('services_ai_question_generator_service.message.create_a_new_question_bank'
            )
        bank = QuestionBank(tenant_id=tenant_id, creator_id=creator_id,
            name=name, description=description, category=category,
            auto_add_criteria=auto_add_criteria or {})
        db.session.add(bank)
        db.session.commit()
        return bank

    def add_question_to_bank(self, bank_id: int, question_id: int, user_id:
        int, tags: List[str]=None) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.add_a_question_to_a_question_b'
            )
        existing = db.session.query(QuestionBankQuestion).filter(
            QuestionBankQuestion.question_bank_id == bank_id, 
            QuestionBankQuestion.generated_question_id == question_id).first()
        if existing:
            return {'success': False, 'error': _(
                'services_ai_question_generator_service.message.question_already_in_bank'
                )}
        bank_question = QuestionBankQuestion(question_bank_id=bank_id,
            generated_question_id=question_id, added_by=user_id, tags=tags or
            [])
        db.session.add(bank_question)
        bank = db.session.query(QuestionBank).get(bank_id)
        if bank:
            bank.total_questions = db.session.query(QuestionBankQuestion
                ).filter(QuestionBankQuestion.question_bank_id == bank_id
                ).count() + 1
            bank.approved_questions = db.session.query(QuestionBankQuestion
                ).join(GeneratedQuestion).filter(QuestionBankQuestion.
                question_bank_id == bank_id, GeneratedQuestion.status ==
                'approved').count()
        db.session.commit()
        return {'success': True}

    def get_analytics(self, tenant_id: int, days: int=30) ->Dict[str, Any]:
        _('services_ai_question_generator_service.message.get_question_generation_analyt'
            )
        start_date = datetime.utcnow() - timedelta(days=days)
        analytics = db.session.query(GenerationAnalytics).filter(
            GenerationAnalytics.tenant_id == tenant_id, GenerationAnalytics
            .date >= start_date).all()
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
        return {'success': True, 'period_days': days, 'total_requests':
            total_requests, 'total_questions_generated': total_questions,
            'total_questions_approved': total_approved, 'approval_rate': 
            total_approved / max(total_questions, 1), 'total_cost':
            total_cost, 'average_quality_score': avg_quality,
            'daily_analytics': [a.to_dict() for a in analytics]}

    def _update_analytics(self, tenant_id: int, request:
        QuestionGenerationRequest, questions: List[GeneratedQuestion]):
        """Update daily analytics."""
        today = datetime.utcnow().date()
        analytics = db.session.query(GenerationAnalytics).filter(
            GenerationAnalytics.tenant_id == tenant_id, func.date(
            GenerationAnalytics.date) == today).first()
        if not analytics:
            analytics = GenerationAnalytics(tenant_id=tenant_id, date=
                datetime.combine(today, datetime.min.time()))
            db.session.add(analytics)
        analytics.requests_completed += 1
        analytics.questions_generated += len(questions)
        analytics.total_tokens_used += request.total_tokens_used
        analytics.total_cost += request.cost_estimate
        if questions:
            quality_scores = [q.quality_score for q in questions if q.
                quality_score]
            if quality_scores:
                analytics.avg_quality_score = sum(quality_scores) / len(
                    quality_scores)
        db.session.commit()

    def initialize_default_data(self):
        _('services_ai_question_generator_service.message.initialize_default_question_ty'
            )
        default_types = [('multiple_choice', _(
            'ai_content_recommendations.label.multiple_choice'), _(
            'services_ai_question_generator_service.message.questions_with_multiple_option'
            )), ('true_false', _(
            'services_ai_question_generator_service.label.true_false'), _(
            'services_ai_question_generator_service.message.questions_requiring_true_or_fa'
            )), ('fill_in_blank', _(
            'services_ai_question_generator_service.message.fill_in_the_blank'
            ), _(
            'services_ai_question_generator_service.message.questions_with_missing_words_t'
            )), ('short_answer', _(
            'ai_content_recommendations.label.short_answer'), _(
            'services_ai_question_generator_service.message.questions_requiring_brief_writ'
            )), ('essay', _(
            'services_ai_question_generator_service.label.essay'), _(
            'services_ai_question_generator_service.message.questions_requiring_detailed_w'
            )), ('matching', _(
            'services_ai_question_generator_service.label.matching'), _(
            'services_ai_question_generator_service.message.questions_requiring_matching_o'
            )), ('ordering', _(
            'services_ai_question_generator_service.label.ordering_sequencing'
            ), _(
            'services_ai_question_generator_service.message.questions_requiring_items_to_b'
            ))]
        for name, display_name, description in default_types:
            existing = db.session.query(QuestionType).filter(QuestionType.
                name == name).first()
            if not existing:
                question_type = QuestionType(name=name, display_name=
                    display_name, description=description)
                db.session.add(question_type)
        blooms_levels = [('remember', 1, _(
            'services_ai_question_generator_service.message.recall_facts_and_basic_concept'
            ), ['define', 'list', 'identify', 'name', 'state']), (
            'understand', 2, _(
            'services_ai_question_generator_service.message.explain_ideas_or_concepts'
            ), ['explain', 'describe', 'summarize', 'interpret', 'compare']
            ), ('apply', 3, _(
            'services_ai_question_generator_service.validation.use_information_in_new_situati'
            ), ['apply', 'demonstrate', 'use', 'solve', 'implement']), (
            'analyze', 4, _(
            'services_ai_question_generator_service.message.draw_connections_among_ideas'
            ), ['analyze', 'compare', 'contrast', 'examine', 'categorize']),
            ('evaluate', 5, _(
            'services_ai_question_generator_service.message.justify_a_stand_or_decision'
            ), ['evaluate', 'critique', 'assess', 'judge', 'defend']), (
            'create', 6, _(
            'services_ai_question_generator_service.message.produce_new_or_original_work'
            ), ['create', 'design', 'compose', 'develop', 'formulate'])]
        for level, order, description, keywords in blooms_levels:
            existing = db.session.query(BloomsTaxonomy).filter(
                BloomsTaxonomy.level == level).first()
            if not existing:
                blooms = BloomsTaxonomy(level=level, order=order,
                    description=description, keywords=keywords)
                db.session.add(blooms)
        default_content_types = [('text', _(
            'services_ai_question_generator_service.label.plain_text'), [
            'txt']), ('document', _('sync_sync_service.label.document'), [
            'pdf', 'docx', 'doc']), ('audio', _(
            'services_ai_question_generator_service.label.audio'), [_(
            'services_ai_question_generator_service.message.mp3_1'), 'wav',
            _('services_ai_question_generator_service.message.m4a')]), (
            'video', _('services_ai_question_generator_service.label.video'
            ), [_('services_storage_service.message.mp4'), 'avi', 'mov']),
            ('web', _(
            'services_ai_question_generator_service.label.web_content'), [
            'url'])]
        for name, description, formats in default_content_types:
            existing = db.session.query(ContentType).filter(ContentType.
                name == name).first()
            if not existing:
                content_type = ContentType(name=name, description=
                    description, supported_formats=formats)
                db.session.add(content_type)
        db.session.commit()
