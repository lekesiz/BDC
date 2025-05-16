"""
AI-powered note analysis service
"""
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from textstat import flesch_reading_ease, flesch_kincaid_grade
import spacy
from collections import Counter
from sqlalchemy.orm import Session

from backend.app.models import Note, Beneficiary, User
from backend.app.utils.config import get_config
from backend.app.services.cache import cache_service

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Fallback if model not available
    nlp = None

logger = logging.getLogger(__name__)
config = get_config()


class NoteAnalysisService:
    """AI-powered note analysis service"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.AI_MODEL or "gpt-4"
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
    
    def analyze_note(self, note_id: int, db: Session, 
                    analysis_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Analyze a note using AI and NLP techniques
        
        Args:
            note_id: ID of the note to analyze
            db: Database session
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary containing analysis results
        """
        # Check cache
        cache_key = f"note_analysis:{note_id}:{analysis_type}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Get note from database
        note = db.query(Note).filter_by(id=note_id).first()
        if not note:
            raise ValueError(f"Note {note_id} not found")
        
        # Perform analysis based on type
        if analysis_type == 'comprehensive':
            analysis = self._comprehensive_analysis(note)
        elif analysis_type == 'summary':
            analysis = self._summary_analysis(note)
        elif analysis_type == 'themes':
            analysis = self._theme_analysis(note)
        elif analysis_type == 'skills':
            analysis = self._skill_identification(note)
        elif analysis_type == 'sentiment':
            analysis = self._sentiment_analysis(note)
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # Store analysis metadata
        analysis['metadata'] = {
            'note_id': note_id,
            'analysis_type': analysis_type,
            'analyzed_at': datetime.utcnow().isoformat(),
            'note_created_at': note.created_at.isoformat(),
            'note_author': note.author.name if note.author else 'Unknown'
        }
        
        # Cache results
        cache_service.set(
            cache_key,
            json.dumps(analysis),
            expiry=3600  # 1 hour cache
        )
        
        # Store in database
        self._store_analysis(note, analysis, db)
        
        return analysis
    
    def _comprehensive_analysis(self, note: Note) -> Dict[str, Any]:
        """Perform comprehensive analysis of a note"""
        text = note.content
        
        # Basic text statistics
        text_stats = self._calculate_text_statistics(text)
        
        # NLP analysis
        nlp_analysis = self._perform_nlp_analysis(text)
        
        # AI-powered analysis
        ai_analysis = self._perform_ai_analysis(text, 'comprehensive')
        
        # Sentiment analysis
        sentiment = self._perform_sentiment_analysis(text)
        
        # Key phrases and entities
        key_elements = self._extract_key_elements(text)
        
        # Theme identification
        themes = self._identify_themes(text)
        
        # Skill identification
        skills = self._identify_skills(text)
        
        # Summary generation
        summary = self._generate_summary(text)
        
        return {
            'text_statistics': text_stats,
            'nlp_analysis': nlp_analysis,
            'ai_insights': ai_analysis,
            'sentiment': sentiment,
            'key_elements': key_elements,
            'themes': themes,
            'skills': skills,
            'summary': summary,
            'quality_score': self._calculate_quality_score(text_stats, nlp_analysis)
        }
    
    def _calculate_text_statistics(self, text: str) -> Dict[str, Any]:
        """Calculate basic text statistics"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Filter out stopwords for meaningful word count
        meaningful_words = [w for w in words if w.lower() not in self.stop_words and w.isalpha()]
        
        stats = {
            'character_count': len(text),
            'word_count': len(words),
            'meaningful_word_count': len(meaningful_words),
            'sentence_count': len(sentences),
            'average_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'average_sentence_length': len(words) / len(sentences) if sentences else 0,
            'lexical_diversity': len(set(words)) / len(words) if words else 0,
            'readability_score': flesch_reading_ease(text) if len(text) > 100 else None,
            'grade_level': flesch_kincaid_grade(text) if len(text) > 100 else None
        }
        
        return stats
    
    def _perform_nlp_analysis(self, text: str) -> Dict[str, Any]:
        """Perform NLP analysis using spaCy"""
        if not nlp:
            return {'error': 'spaCy model not available'}
        
        doc = nlp(text)
        
        # Extract linguistic features
        pos_counts = Counter(token.pos_ for token in doc)
        
        # Extract named entities
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        
        # Extract noun phrases
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        
        # Extract dependencies
        dependency_patterns = Counter(f"{token.dep_}({token.pos_})" for token in doc)
        
        return {
            'pos_distribution': dict(pos_counts),
            'named_entities': entities,
            'noun_phrases': noun_phrases[:20],  # Top 20 noun phrases
            'dependency_patterns': dict(dependency_patterns.most_common(10)),
            'sentence_types': self._classify_sentences(doc)
        }
    
    def _classify_sentences(self, doc) -> Dict[str, int]:
        """Classify sentences by type"""
        sentence_types = Counter()
        
        for sent in doc.sents:
            if sent.text.strip().endswith('?'):
                sentence_types['question'] += 1
            elif sent.text.strip().endswith('!'):
                sentence_types['exclamation'] += 1
            else:
                sentence_types['statement'] += 1
        
        return dict(sentence_types)
    
    def _perform_ai_analysis(self, text: str, analysis_type: str) -> Dict[str, Any]:
        """Perform AI-powered analysis using OpenAI"""
        try:
            prompt = self._create_ai_prompt(text, analysis_type)
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert analyst specializing in educational content analysis. Analyze notes and provide detailed insights about learning, understanding, and skill development."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, analysis_type)
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return {'error': 'AI analysis failed', 'fallback': True}
    
    def _create_ai_prompt(self, text: str, analysis_type: str) -> str:
        """Create prompt for AI analysis"""
        if analysis_type == 'comprehensive':
            return f"""
            Analyze the following note and provide comprehensive insights:
            
            Note Content:
            {text[:2000]}  # Limit for token efficiency
            
            Please provide:
            1. Main topics and concepts discussed
            2. Key insights and understanding demonstrated
            3. Learning progress indicators
            4. Areas of strength and confusion
            5. Suggestions for improvement
            6. Overall assessment of comprehension level
            7. Recommended next steps for learning
            """
        
        elif analysis_type == 'summary':
            return f"""
            Create a concise summary of the following note:
            
            Note Content:
            {text[:2000]}
            
            Provide:
            1. A 2-3 sentence executive summary
            2. Key points (bullet list)
            3. Main takeaways
            4. Action items if any
            """
        
        elif analysis_type == 'themes':
            return f"""
            Identify and analyze the main themes in this note:
            
            Note Content:
            {text[:2000]}
            
            Provide:
            1. Primary themes (rank by importance)
            2. Secondary themes
            3. Recurring concepts
            4. Thematic connections
            5. Theme evolution throughout the note
            """
        
        elif analysis_type == 'skills':
            return f"""
            Identify skills and competencies demonstrated or discussed in this note:
            
            Note Content:
            {text[:2000]}
            
            Provide:
            1. Technical skills mentioned or demonstrated
            2. Soft skills evident in the writing
            3. Subject matter expertise shown
            4. Learning skills displayed
            5. Areas for skill development
            """
        
        return f"Analyze this text: {text[:1000]}"
    
    def _parse_ai_response(self, ai_response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        parsed = {
            'raw_response': ai_response,
            'sections': {}
        }
        
        # Split response into sections
        lines = ai_response.strip().split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line is a section header (numbered or contains colon)
            if re.match(r'^\d+\.', line) or line.endswith(':'):
                if current_section and current_content:
                    parsed['sections'][current_section] = '\n'.join(current_content)
                current_section = line.rstrip(':').strip()
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_section and current_content:
            parsed['sections'][current_section] = '\n'.join(current_content)
        
        # Extract specific elements based on analysis type
        if analysis_type == 'comprehensive':
            parsed['main_topics'] = self._extract_list_items(parsed['sections'].get('1. Main topics and concepts discussed', ''))
            parsed['key_insights'] = self._extract_list_items(parsed['sections'].get('2. Key insights and understanding demonstrated', ''))
            parsed['progress_indicators'] = self._extract_list_items(parsed['sections'].get('3. Learning progress indicators', ''))
            parsed['strengths_weaknesses'] = parsed['sections'].get('4. Areas of strength and confusion', '')
            parsed['improvement_suggestions'] = self._extract_list_items(parsed['sections'].get('5. Suggestions for improvement', ''))
            parsed['comprehension_assessment'] = parsed['sections'].get('6. Overall assessment of comprehension level', '')
            parsed['next_steps'] = self._extract_list_items(parsed['sections'].get('7. Recommended next steps for learning', ''))
        
        return parsed
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line):
                items.append(re.sub(r'^[-•\d.]\s*', '', line))
            elif line:
                items.append(line)
        return items
    
    def _perform_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Perform sentiment analysis"""
        # Overall sentiment
        scores = self.sentiment_analyzer.polarity_scores(text)
        
        # Sentence-level sentiment
        sentences = sent_tokenize(text)
        sentence_sentiments = []
        
        for sentence in sentences[:10]:  # Analyze first 10 sentences
            sent_scores = self.sentiment_analyzer.polarity_scores(sentence)
            sentence_sentiments.append({
                'sentence': sentence[:100] + '...' if len(sentence) > 100 else sentence,
                'scores': sent_scores,
                'dominant': max(sent_scores.items(), key=lambda x: x[1] if x[0] != 'compound' else 0)[0]
            })
        
        # Emotional tone analysis
        emotion_words = self._analyze_emotion_words(text)
        
        return {
            'overall_scores': scores,
            'sentiment_label': self._get_sentiment_label(scores['compound']),
            'sentence_analysis': sentence_sentiments,
            'emotion_words': emotion_words,
            'confidence': abs(scores['compound'])
        }
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        """Convert compound score to sentiment label"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_emotion_words(self, text: str) -> Dict[str, List[str]]:
        """Analyze emotional words in text"""
        emotion_categories = {
            'positive': ['happy', 'excited', 'confident', 'proud', 'satisfied', 'hopeful'],
            'negative': ['frustrated', 'confused', 'worried', 'anxious', 'disappointed', 'struggling'],
            'neutral': ['understand', 'think', 'believe', 'know', 'consider', 'realize']
        }
        
        found_emotions = defaultdict(list)
        words = word_tokenize(text.lower())
        
        for category, emotion_words in emotion_categories.items():
            for word in words:
                if word in emotion_words:
                    found_emotions[category].append(word)
        
        return dict(found_emotions)
    
    def _extract_key_elements(self, text: str) -> Dict[str, Any]:
        """Extract key phrases, entities, and concepts"""
        if not nlp:
            return {'error': 'NLP model not available'}
        
        doc = nlp(text)
        
        # Extract key phrases using noun chunks
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        
        # Extract entities
        entities = defaultdict(list)
        for ent in doc.ents:
            entities[ent.label_].append(ent.text)
        
        # Extract important terms using TF-IDF-like approach
        words = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]
        word_freq = Counter(words)
        
        # Calculate importance scores
        important_terms = []
        for word, freq in word_freq.most_common(20):
            if freq > 1:  # Only consider words that appear more than once
                important_terms.append({
                    'term': word,
                    'frequency': freq,
                    'importance': freq / len(words)
                })
        
        return {
            'key_phrases': list(set(noun_phrases))[:15],
            'entities': dict(entities),
            'important_terms': important_terms,
            'technical_terms': self._identify_technical_terms(doc),
            'concepts': self._identify_concepts(text)
        }
    
    def _identify_technical_terms(self, doc) -> List[str]:
        """Identify technical or domain-specific terms"""
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+(?:tion|ment|ity|ness|ance|ence)\b',  # Technical suffixes
            r'\b\w+(?:ify|ize|ate)\b',  # Technical verbs
        ]
        
        technical_terms = set()
        
        for token in doc:
            for pattern in technical_patterns:
                if re.match(pattern, token.text):
                    technical_terms.add(token.text)
        
        return list(technical_terms)[:20]
    
    def _identify_concepts(self, text: str) -> List[Dict[str, Any]]:
        """Identify main concepts discussed"""
        # Use AI to identify concepts
        try:
            prompt = f"""
            Identify the main concepts discussed in this text. For each concept, provide:
            1. The concept name
            2. A brief definition or explanation
            3. How it's used in the context
            
            Text: {text[:1000]}
            
            Format as a list of concepts.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying and explaining academic concepts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            concepts_text = response.choices[0].message.content
            return self._parse_concepts(concepts_text)
            
        except Exception as e:
            logger.error(f"Error identifying concepts: {str(e)}")
            return []
    
    def _parse_concepts(self, concepts_text: str) -> List[Dict[str, Any]]:
        """Parse concepts from AI response"""
        concepts = []
        lines = concepts_text.strip().split('\n')
        current_concept = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_concept:
                    concepts.append(current_concept)
                    current_concept = {}
                continue
            
            if line.startswith('Concept:') or re.match(r'^\d+\.\s*Concept:', line):
                if current_concept:
                    concepts.append(current_concept)
                current_concept = {'name': line.split(':', 1)[1].strip()}
            elif line.startswith('Definition:') or 'definition' in line.lower():
                current_concept['definition'] = line.split(':', 1)[1].strip()
            elif line.startswith('Context:') or 'context' in line.lower():
                current_concept['context'] = line.split(':', 1)[1].strip()
            elif current_concept:
                # Add to previous field
                if 'context' in current_concept:
                    current_concept['context'] += ' ' + line
                elif 'definition' in current_concept:
                    current_concept['definition'] += ' ' + line
        
        if current_concept:
            concepts.append(current_concept)
        
        return concepts[:10]  # Limit to top 10 concepts
    
    def _identify_themes(self, text: str) -> List[Dict[str, Any]]:
        """Identify main themes in the text"""
        # Use AI to identify themes
        try:
            prompt = f"""
            Identify the main themes in this note. For each theme:
            1. Name the theme
            2. Explain what it encompasses
            3. Provide evidence from the text
            4. Rate its prominence (1-5)
            
            Text: {text[:1500]}
            
            Format as a structured list of themes.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at thematic analysis of educational content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            themes_text = response.choices[0].message.content
            return self._parse_themes(themes_text)
            
        except Exception as e:
            logger.error(f"Error identifying themes: {str(e)}")
            return self._fallback_theme_identification(text)
    
    def _parse_themes(self, themes_text: str) -> List[Dict[str, Any]]:
        """Parse themes from AI response"""
        themes = []
        lines = themes_text.strip().split('\n')
        current_theme = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_theme:
                    themes.append(current_theme)
                    current_theme = {}
                continue
            
            if re.match(r'^(Theme|^\d+\.)', line):
                if current_theme:
                    themes.append(current_theme)
                current_theme = {'name': re.sub(r'^(Theme:|^\d+\.)\s*', '', line)}
            elif 'encompasses' in line.lower() or 'explanation' in line.lower():
                current_theme['explanation'] = line.split(':', 1)[-1].strip()
            elif 'evidence' in line.lower():
                current_theme['evidence'] = line.split(':', 1)[-1].strip()
            elif 'prominence' in line.lower() or 'rating' in line.lower():
                # Extract rating
                match = re.search(r'(\d+)(?:/5)?', line)
                if match:
                    current_theme['prominence'] = int(match.group(1))
        
        if current_theme:
            themes.append(current_theme)
        
        return sorted(themes, key=lambda x: x.get('prominence', 0), reverse=True)[:5]
    
    def _fallback_theme_identification(self, text: str) -> List[Dict[str, Any]]:
        """Fallback theme identification using keyword clustering"""
        # Extract noun phrases and important terms
        if not nlp:
            return []
        
        doc = nlp(text)
        
        # Extract noun phrases
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
        
        # Group similar phrases
        theme_clusters = defaultdict(list)
        
        for phrase in noun_phrases:
            # Simple clustering based on shared words
            words = set(phrase.split())
            matched = False
            
            for theme, phrases in theme_clusters.items():
                theme_words = set(theme.split())
                if len(words & theme_words) >= len(words) * 0.5:
                    phrases.append(phrase)
                    matched = True
                    break
            
            if not matched:
                theme_clusters[phrase].append(phrase)
        
        # Convert to theme format
        themes = []
        for theme, phrases in sorted(theme_clusters.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            themes.append({
                'name': theme.title(),
                'frequency': len(phrases),
                'related_phrases': list(set(phrases))[:5],
                'prominence': min(5, len(phrases))
            })
        
        return themes
    
    def _identify_skills(self, text: str) -> Dict[str, List[str]]:
        """Identify skills mentioned or demonstrated in the text"""
        skills = {
            'technical_skills': [],
            'soft_skills': [],
            'cognitive_skills': [],
            'subject_knowledge': []
        }
        
        # Define skill keywords
        skill_patterns = {
            'technical_skills': [
                'programming', 'coding', 'analysis', 'design', 'implementation',
                'debugging', 'testing', 'optimization', 'database', 'algorithm'
            ],
            'soft_skills': [
                'communication', 'teamwork', 'leadership', 'creativity', 'problem-solving',
                'critical thinking', 'time management', 'organization', 'presentation'
            ],
            'cognitive_skills': [
                'understanding', 'comprehension', 'synthesis', 'evaluation', 'application',
                'analysis', 'inference', 'deduction', 'reasoning', 'logic'
            ],
            'subject_knowledge': [
                'mathematics', 'science', 'history', 'literature', 'geography',
                'physics', 'chemistry', 'biology', 'economics', 'psychology'
            ]
        }
        
        # Search for skill mentions
        text_lower = text.lower()
        words = word_tokenize(text_lower)
        
        for category, keywords in skill_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Check context
                    for i, word in enumerate(words):
                        if word == keyword:
                            context = ' '.join(words[max(0, i-3):min(len(words), i+4)])
                            skills[category].append({
                                'skill': keyword,
                                'context': context,
                                'confidence': 0.8
                            })
        
        # Use AI for more sophisticated skill identification
        ai_skills = self._ai_skill_identification(text)
        
        # Merge AI results
        for category, ai_skill_list in ai_skills.items():
            if category in skills:
                skills[category].extend(ai_skill_list)
        
        # Deduplicate
        for category in skills:
            seen = set()
            unique_skills = []
            for skill in skills[category]:
                skill_name = skill['skill'] if isinstance(skill, dict) else skill
                if skill_name not in seen:
                    seen.add(skill_name)
                    unique_skills.append(skill)
            skills[category] = unique_skills
        
        return skills
    
    def _ai_skill_identification(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Use AI to identify skills"""
        try:
            prompt = f"""
            Identify skills mentioned or demonstrated in this text. Categorize them as:
            1. Technical skills
            2. Soft skills
            3. Cognitive skills
            4. Subject knowledge
            
            For each skill, note:
            - The skill name
            - How it's demonstrated or mentioned
            - Confidence level (high/medium/low)
            
            Text: {text[:1000]}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying skills and competencies in educational content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            skills_text = response.choices[0].message.content
            return self._parse_ai_skills(skills_text)
            
        except Exception as e:
            logger.error(f"Error in AI skill identification: {str(e)}")
            return {}
    
    def _parse_ai_skills(self, skills_text: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse skills from AI response"""
        skills = {
            'technical_skills': [],
            'soft_skills': [],
            'cognitive_skills': [],
            'subject_knowledge': []
        }
        
        current_category = None
        lines = skills_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for category headers
            if 'technical skill' in line.lower():
                current_category = 'technical_skills'
            elif 'soft skill' in line.lower():
                current_category = 'soft_skills'
            elif 'cognitive skill' in line.lower():
                current_category = 'cognitive_skills'
            elif 'subject knowledge' in line.lower():
                current_category = 'subject_knowledge'
            elif current_category and (line.startswith('-') or line.startswith('•')):
                # Parse skill entry
                skill_text = line[1:].strip()
                
                # Extract skill name and details
                if ':' in skill_text:
                    skill_name, details = skill_text.split(':', 1)
                else:
                    skill_name = skill_text
                    details = ''
                
                # Determine confidence
                confidence = 'medium'
                if 'high' in details.lower():
                    confidence = 'high'
                elif 'low' in details.lower():
                    confidence = 'low'
                
                skills[current_category].append({
                    'skill': skill_name.strip(),
                    'details': details.strip(),
                    'confidence': confidence
                })
        
        return skills
    
    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate various types of summaries"""
        summaries = {}
        
        # Extractive summary (using sentence ranking)
        summaries['extractive'] = self._extractive_summary(text)
        
        # AI-generated abstractive summary
        summaries['abstractive'] = self._abstractive_summary(text)
        
        # Key points summary
        summaries['key_points'] = self._key_points_summary(text)
        
        # One-line summary
        summaries['one_line'] = self._one_line_summary(text)
        
        return summaries
    
    def _extractive_summary(self, text: str, num_sentences: int = 3) -> str:
        """Create extractive summary using sentence ranking"""
        sentences = sent_tokenize(text)
        if len(sentences) <= num_sentences:
            return text
        
        # Score sentences based on word frequency
        word_freq = Counter(word.lower() for word in word_tokenize(text) 
                          if word.isalpha() and word.lower() not in self.stop_words)
        
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = word_tokenize(sentence.lower())
            score = sum(word_freq[word] for word in words if word in word_freq)
            sentence_scores[i] = score / len(words) if words else 0
        
        # Get top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        top_sentences.sort(key=lambda x: x[0])  # Sort by original order
        
        return ' '.join(sentences[i] for i, _ in top_sentences)
    
    def _abstractive_summary(self, text: str) -> str:
        """Generate abstractive summary using AI"""
        try:
            prompt = f"""
            Create a concise summary of this note in 2-3 sentences. Focus on the main ideas and key takeaways.
            
            Text: {text[:1500]}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating concise, informative summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating abstractive summary: {str(e)}")
            return self._extractive_summary(text, 2)
    
    def _key_points_summary(self, text: str) -> List[str]:
        """Extract key points from text"""
        try:
            prompt = f"""
            Extract the main key points from this note as a bullet list. Include only the most important information.
            
            Text: {text[:1500]}
            
            Format as:
            • Key point 1
            • Key point 2
            • Key point 3
            (etc.)
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at identifying and extracting key points from text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            key_points_text = response.choices[0].message.content
            return [line.strip()[1:].strip() for line in key_points_text.split('\n') 
                   if line.strip().startswith('•')]
            
        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return []
    
    def _one_line_summary(self, text: str) -> str:
        """Generate one-line summary"""
        try:
            prompt = f"""
            Summarize this note in exactly one sentence (maximum 20 words).
            
            Text: {text[:1000]}
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating ultra-concise summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=50
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating one-line summary: {str(e)}")
            first_sentence = sent_tokenize(text)[0]
            return first_sentence[:100] + '...' if len(first_sentence) > 100 else first_sentence
    
    def _calculate_quality_score(self, text_stats: Dict[str, Any], 
                               nlp_analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score for the note"""
        score = 0.0
        max_score = 100.0
        
        # Readability (20 points)
        if text_stats.get('readability_score'):
            readability = text_stats['readability_score']
            if 60 <= readability <= 80:  # Optimal range
                score += 20
            elif 50 <= readability < 60 or 80 < readability <= 90:
                score += 15
            elif 40 <= readability < 50 or 90 < readability <= 100:
                score += 10
            else:
                score += 5
        
        # Length appropriateness (15 points)
        word_count = text_stats.get('word_count', 0)
        if 200 <= word_count <= 800:  # Optimal range for a note
            score += 15
        elif 100 <= word_count < 200 or 800 < word_count <= 1000:
            score += 10
        elif 50 <= word_count < 100 or 1000 < word_count <= 1500:
            score += 5
        
        # Lexical diversity (15 points)
        diversity = text_stats.get('lexical_diversity', 0)
        if diversity >= 0.7:
            score += 15
        elif diversity >= 0.5:
            score += 10
        elif diversity >= 0.3:
            score += 5
        
        # Sentence variety (15 points)
        if nlp_analysis and 'sentence_types' in nlp_analysis:
            types = nlp_analysis['sentence_types']
            variety = len([t for t in types.values() if t > 0])
            if variety >= 3:
                score += 15
            elif variety == 2:
                score += 10
            elif variety == 1:
                score += 5
        
        # Entity richness (15 points)
        if nlp_analysis and 'named_entities' in nlp_analysis:
            entity_count = sum(len(entities) for entities in nlp_analysis['named_entities'].values())
            if entity_count >= 5:
                score += 15
            elif entity_count >= 3:
                score += 10
            elif entity_count >= 1:
                score += 5
        
        # Structure quality (20 points)
        # Based on POS distribution
        if nlp_analysis and 'pos_distribution' in nlp_analysis:
            pos_dist = nlp_analysis['pos_distribution']
            
            # Check for balanced distribution
            noun_ratio = pos_dist.get('NOUN', 0) / sum(pos_dist.values()) if pos_dist else 0
            verb_ratio = pos_dist.get('VERB', 0) / sum(pos_dist.values()) if pos_dist else 0
            
            if 0.2 <= noun_ratio <= 0.4 and 0.1 <= verb_ratio <= 0.3:
                score += 20
            elif 0.15 <= noun_ratio <= 0.45 and 0.05 <= verb_ratio <= 0.35:
                score += 15
            else:
                score += 10
        
        return round(score, 2)
    
    def _store_analysis(self, note: Note, analysis: Dict[str, Any], db: Session):
        """Store analysis results in database"""
        try:
            # Update note with analysis metadata
            if not note.metadata:
                note.metadata = {}
            
            note.metadata['last_analysis'] = {
                'timestamp': datetime.utcnow().isoformat(),
                'type': analysis['metadata']['analysis_type'],
                'quality_score': analysis.get('quality_score'),
                'summary': analysis.get('summary', {}).get('one_line')
            }
            
            db.commit()
            logger.info(f"Stored analysis for note {note.id}")
            
        except Exception as e:
            logger.error(f"Error storing analysis: {str(e)}")
            db.rollback()
    
    def batch_analyze_notes(self, note_ids: List[int], db: Session, 
                          analysis_type: str = 'summary') -> Dict[int, Dict[str, Any]]:
        """Analyze multiple notes in batch"""
        results = {}
        
        for note_id in note_ids:
            try:
                results[note_id] = self.analyze_note(note_id, db, analysis_type)
            except Exception as e:
                logger.error(f"Error analyzing note {note_id}: {str(e)}")
                results[note_id] = {'error': str(e)}
        
        return results
    
    def search_notes_by_theme(self, theme: str, db: Session, 
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Search notes by theme using analysis results"""
        # This would require a proper search index in production
        # For now, we'll do a simple implementation
        notes = db.query(Note).limit(100).all()  # Sample of notes
        
        theme_matches = []
        
        for note in notes:
            # Check if note has been analyzed
            cache_key = f"note_analysis:{note.id}:themes"
            cached_analysis = cache_service.get(cache_key)
            
            if cached_analysis:
                analysis = json.loads(cached_analysis)
                themes = analysis.get('themes', [])
                
                # Check for theme match
                for theme_data in themes:
                    if theme.lower() in theme_data.get('name', '').lower():
                        theme_matches.append({
                            'note_id': note.id,
                            'title': note.title,
                            'theme_match': theme_data,
                            'relevance_score': theme_data.get('prominence', 0)
                        })
                        break
        
        # Sort by relevance
        theme_matches.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return theme_matches[:limit]
    
    def compare_notes(self, note_ids: List[int], db: Session) -> Dict[str, Any]:
        """Compare multiple notes"""
        if len(note_ids) < 2:
            raise ValueError("At least 2 notes required for comparison")
        
        # Analyze all notes
        analyses = {}
        for note_id in note_ids:
            analyses[note_id] = self.analyze_note(note_id, db, 'comprehensive')
        
        # Compare themes
        all_themes = defaultdict(list)
        for note_id, analysis in analyses.items():
            for theme in analysis.get('themes', []):
                all_themes[theme['name']].append(note_id)
        
        # Compare skills
        all_skills = defaultdict(list)
        for note_id, analysis in analyses.items():
            skills = analysis.get('skills', {})
            for category, skill_list in skills.items():
                for skill in skill_list:
                    skill_name = skill['skill'] if isinstance(skill, dict) else skill
                    all_skills[skill_name].append(note_id)
        
        # Compare sentiment
        sentiments = {}
        for note_id, analysis in analyses.items():
            sentiments[note_id] = analysis.get('sentiment', {}).get('sentiment_label')
        
        # Compare quality scores
        quality_scores = {}
        for note_id, analysis in analyses.items():
            quality_scores[note_id] = analysis.get('quality_score', 0)
        
        return {
            'common_themes': {theme: notes for theme, notes in all_themes.items() 
                           if len(notes) > 1},
            'unique_themes': {theme: notes[0] for theme, notes in all_themes.items() 
                            if len(notes) == 1},
            'common_skills': {skill: notes for skill, notes in all_skills.items() 
                            if len(notes) > 1},
            'sentiment_comparison': sentiments,
            'quality_comparison': quality_scores,
            'similarity_matrix': self._calculate_similarity_matrix(analyses)
        }
    
    def _calculate_similarity_matrix(self, analyses: Dict[int, Dict[str, Any]]) -> Dict[str, float]:
        """Calculate similarity between notes"""
        similarity_matrix = {}
        note_ids = list(analyses.keys())
        
        for i, note_id_1 in enumerate(note_ids):
            for j, note_id_2 in enumerate(note_ids[i+1:], i+1):
                # Calculate similarity based on themes and skills
                themes_1 = set(t['name'] for t in analyses[note_id_1].get('themes', []))
                themes_2 = set(t['name'] for t in analyses[note_id_2].get('themes', []))
                
                theme_similarity = len(themes_1 & themes_2) / len(themes_1 | themes_2) if themes_1 | themes_2 else 0
                
                # Calculate skill similarity
                skills_1 = set()
                skills_2 = set()
                
                for category, skills in analyses[note_id_1].get('skills', {}).items():
                    skills_1.update(s['skill'] if isinstance(s, dict) else s for s in skills)
                    
                for category, skills in analyses[note_id_2].get('skills', {}).items():
                    skills_2.update(s['skill'] if isinstance(s, dict) else s for s in skills)
                
                skill_similarity = len(skills_1 & skills_2) / len(skills_1 | skills_2) if skills_1 | skills_2 else 0
                
                # Combined similarity
                similarity = (theme_similarity * 0.6) + (skill_similarity * 0.4)
                similarity_matrix[f"{note_id_1}-{note_id_2}"] = round(similarity, 3)
        
        return similarity_matrix


# Summary analysis service (simplified version)
class NoteSummaryService(NoteAnalysisService):
    """Specialized service for note summarization"""
    
    def summarize_note(self, note_id: int, db: Session, 
                      summary_type: str = 'comprehensive') -> Dict[str, Any]:
        """Generate various types of summaries for a note"""
        return self.analyze_note(note_id, db, 'summary')
    
    def generate_executive_summary(self, note_id: int, db: Session) -> str:
        """Generate executive summary for a note"""
        analysis = self.analyze_note(note_id, db, 'summary')
        return analysis.get('summary', {}).get('abstractive', '')


# Singleton instances
note_analysis_service = NoteAnalysisService()
note_summary_service = NoteSummaryService()