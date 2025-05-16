"""
AI-powered content recommendation service
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import openai
from app.models.beneficiary import Beneficiary
# Henüz taşınmamış model modülleri için notlar
# Assessment ve TestResult modellerini eklemek gerekecek
# from app.models.assessment import Assessment, TestResult
# from app.models.note import Note
from app.models.user import User
from app.extensions import db, cache
from app.utils.logging import logger

# Geçici olarak eksik model sınıflarını tanımlayalım
class Assessment:
    pass

class TestResult:
    pass

class Note:
    pass

class Document:
    pass

# Monitör servisi henüz taşınmadığı için
class ErrorTracker:
    def capture_exception(self, exception):
        logger.error(f"Exception captured: {str(exception)}")

error_tracker = ErrorTracker()

class ContentRecommendationService:
    """AI-powered content recommendation service"""
    
    def __init__(self):
        self.api_key = None  # settings.OPENAI_API_KEY değeri daha sonra yapılandırılacak
        openai.api_key = self.api_key
        
    def generate_content_recommendations(self, beneficiary_id: int, db: Session,
                                       context_type: str = 'general',
                                       specific_need: Optional[str] = None) -> Dict[str, Any]:
        """Generate personalized content recommendations"""
        try:
            # Check cache first
            cache_key = f"content_rec:{beneficiary_id}:{context_type}:{specific_need or 'none'}"
            cached_recommendations = cache.get(cache_key)
            if cached_recommendations:
                return cached_recommendations
                
            # Get beneficiary information
            beneficiary = db.query(Beneficiary).filter_by(id=beneficiary_id).first()
            if not beneficiary:
                raise ValueError(f"Beneficiary {beneficiary_id} not found")
                
            # Gather context data
            context_data = self._gather_context_data(beneficiary_id, db, context_type)
            
            # Generate recommendations using AI
            recommendations = self._generate_recommendations(
                context_data, context_type, specific_need
            )
            
            # Enhance with available resources
            enhanced_recommendations = self._enhance_with_resources(
                recommendations, db, beneficiary_id
            )
            
            # Add metadata
            enhanced_recommendations['metadata'] = {
                'beneficiary_id': beneficiary_id,
                'beneficiary_name': f"{beneficiary.first_name} {beneficiary.last_name}",
                'context_type': context_type,
                'specific_need': specific_need,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Cache the recommendations
            cache.set(cache_key, enhanced_recommendations, 1800)  # 30 minutes
            
            return enhanced_recommendations
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error generating content recommendations: {str(e)}")
            raise
            
    def generate_structure_suggestions(self, content_type: str,
                                     current_content: Optional[str] = None,
                                     requirements: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate structure suggestions for content creation"""
        try:
            prompt = self._build_structure_prompt(content_type, current_content, requirements)
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert content strategist and educational designer. 
                        Provide detailed, actionable structure suggestions for various types of content."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            suggestions = json.loads(response['choices'][0]['message']['content'])
            
            return {
                'content_type': content_type,
                'suggestions': suggestions,
                'templates': self._generate_templates(content_type, suggestions),
                'best_practices': self._get_best_practices(content_type),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating structure suggestions: {str(e)}")
            return self._get_fallback_structure(content_type)
            
    def _gather_context_data(self, beneficiary_id: int, db: Session,
                           context_type: str) -> Dict[str, Any]:
        """Gather relevant context data for recommendations"""
        context = {
            'beneficiary_id': beneficiary_id,
            'context_type': context_type
        }
        
        # Get recent assessments
        recent_assessments = db.query(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id
        ).order_by(Assessment.created_at.desc()).limit(5).all()
        
        context['recent_assessments'] = [{
            'type': a.assessment_type,
            'score': a.score,
            'status': a.status,
            'completed_at': a.completed_at.isoformat() if a.completed_at else None
        } for a in recent_assessments]
        
        # Get skill gaps
        context['skill_gaps'] = self._identify_skill_gaps(beneficiary_id, db)
        
        # Get learning preferences
        context['learning_preferences'] = self._analyze_learning_preferences(beneficiary_id, db)
        
        # Get recent notes and topics
        recent_notes = db.query(Note).filter(
            Note.beneficiary_id == beneficiary_id
        ).order_by(Note.created_at.desc()).limit(10).all()
        
        context['recent_topics'] = self._extract_topics_from_notes(recent_notes)
        
        # Get performance trends
        context['performance_trends'] = self._analyze_performance_trends(beneficiary_id, db)
        
        return context
        
    def _generate_recommendations(self, context_data: Dict[str, Any],
                                context_type: str,
                                specific_need: Optional[str]) -> Dict[str, Any]:
        """Generate recommendations using AI"""
        prompt = self._build_recommendation_prompt(context_data, context_type, specific_need)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational content curator and learning advisor. 
                        Generate highly personalized, actionable content recommendations based on learner data."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            recommendations = json.loads(response['choices'][0]['message']['content'])
            
        except json.JSONDecodeError:
            recommendations = {
                'summary': response['choices'][0]['message']['content'],
                'categories': {}
            }
        except Exception as e:
            logger.error(f"AI recommendation generation failed: {str(e)}")
            recommendations = self._generate_fallback_recommendations(context_data)
            
        return recommendations
        
    def _build_recommendation_prompt(self, context_data: Dict[str, Any],
                                   context_type: str,
                                   specific_need: Optional[str]) -> str:
        """Build the prompt for AI recommendations"""
        skill_gaps = context_data.get('skill_gaps', [])
        recent_topics = context_data.get('recent_topics', [])
        performance_trends = context_data.get('performance_trends', {})
        
        base_prompt = f"""
        Generate personalized content recommendations based on the following learner profile:
        
        Context Type: {context_type}
        Specific Need: {specific_need or 'General learning support'}
        
        Skill Gaps: {', '.join(skill_gaps[:5]) if skill_gaps else 'None identified'}
        Recent Topics of Interest: {', '.join(recent_topics[:5]) if recent_topics else 'None identified'}
        Performance Trend: {performance_trends.get('overall_trend', 'stable')}
        
        Recent Assessment Scores:
        {json.dumps(context_data.get('recent_assessments', []), indent=2)}
        
        Learning Preferences:
        {json.dumps(context_data.get('learning_preferences', {}), indent=2)}
        """
        
        if context_type == 'skill_development':
            base_prompt += """
            
            Focus on skill-building resources and exercises.
            Prioritize practical applications and hands-on learning.
            Include progressive difficulty levels.
            """
        elif context_type == 'knowledge_gaps':
            base_prompt += """
            
            Focus on foundational concepts and theory.
            Include explanatory content and tutorials.
            Provide multiple learning modalities.
            """
        elif context_type == 'assessment_prep':
            base_prompt += """
            
            Focus on practice materials and sample questions.
            Include test-taking strategies and tips.
            Provide timed practice opportunities.
            """
            
        base_prompt += """
        
        Generate recommendations in the following JSON format:
        {
            "primary_recommendations": [
                {
                    "title": "...",
                    "description": "...",
                    "type": "video/article/exercise/etc",
                    "difficulty": "beginner/intermediate/advanced",
                    "estimated_time": "...",
                    "learning_objectives": ["..."],
                    "relevance_score": 0.95
                }
            ],
            "supplementary_resources": [...],
            "learning_path": {
                "immediate": ["Resource 1", "Resource 2"],
                "short_term": ["Resource 3", "Resource 4"],
                "long_term": ["Resource 5", "Resource 6"]
            },
            "personalized_tips": ["Tip 1", "Tip 2", ...],
            "engagement_strategies": ["Strategy 1", "Strategy 2", ...]
        }
        """
        
        return base_prompt
        
    def _enhance_with_resources(self, recommendations: Dict[str, Any], db: Session,
                              beneficiary_id: int) -> Dict[str, Any]:
        """Enhance recommendations with available database resources"""
        enhanced = recommendations.copy()
        
        # Get relevant documents from the database
        available_documents = db.query(Document).filter(
            Document.is_active == True
        ).all()
        
        # Match recommendations with available resources
        if 'primary_recommendations' in enhanced:
            for rec in enhanced['primary_recommendations']:
                matching_docs = self._find_matching_documents(
                    rec.get('title', ''),
                    rec.get('description', ''),
                    available_documents
                )
                rec['available_resources'] = [{
                    'id': doc.id,
                    'title': doc.title,
                    'type': doc.document_type,
                    'url': f"/documents/{doc.id}"
                } for doc in matching_docs[:3]]
                
        # Add personalization based on beneficiary history
        enhanced['personalization'] = {
            'previous_completions': self._get_completion_history(beneficiary_id, db),
            'preference_match': self._calculate_preference_match(
                recommendations, beneficiary_id, db
            )
        }
        
        return enhanced
        
    def _build_structure_prompt(self, content_type: str,
                              current_content: Optional[str],
                              requirements: Optional[Dict]) -> str:
        """Build prompt for structure suggestions"""
        base_prompt = f"""
        Generate detailed structure suggestions for creating {content_type} content.
        """
        
        if current_content:
            base_prompt += f"""
            
            Current content to improve:
            {current_content[:1000]}
            """
            
        if requirements:
            base_prompt += f"""
            
            Specific requirements:
            {json.dumps(requirements, indent=2)}
            """
            
        base_prompt += """
        
        Provide suggestions in the following JSON format:
        {
            "overall_structure": {
                "introduction": {...},
                "main_sections": [{...}],
                "conclusion": {...}
            },
            "content_elements": {
                "required": ["..."],
                "recommended": ["..."],
                "optional": ["..."]
            },
            "formatting_guidelines": {...},
            "enhancement_suggestions": ["..."],
            "common_pitfalls": ["..."],
            "examples": [{
                "type": "...",
                "content": "..."
            }]
        }
        """
        
        return base_prompt
        
    def _generate_templates(self, content_type: str,
                          suggestions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate content templates based on suggestions"""
        templates = []
        
        if content_type == 'lesson_plan':
            templates.append({
                'name': 'Standard Lesson Plan',
                'sections': [
                    {'title': 'Learning Objectives', 'content': ''},
                    {'title': 'Materials Needed', 'content': ''},
                    {'title': 'Introduction', 'content': ''},
                    {'title': 'Main Activity', 'content': ''},
                    {'title': 'Assessment', 'content': ''},
                    {'title': 'Closure', 'content': ''}
                ]
            })
        elif content_type == 'assessment':
            templates.append({
                'name': 'Standard Assessment',
                'sections': [
                    {'title': 'Instructions', 'content': ''},
                    {'title': 'Multiple Choice', 'content': ''},
                    {'title': 'Short Answer', 'content': ''},
                    {'title': 'Essay Questions', 'content': ''},
                    {'title': 'Practical Tasks', 'content': ''}
                ]
            })
        elif content_type == 'report':
            templates.append({
                'name': 'Progress Report',
                'sections': [
                    {'title': 'Executive Summary', 'content': ''},
                    {'title': 'Assessment Results', 'content': ''},
                    {'title': 'Skill Development', 'content': ''},
                    {'title': 'Recommendations', 'content': ''},
                    {'title': 'Next Steps', 'content': ''}
                ]
            })
            
        # Customize templates based on AI suggestions
        if suggestions and 'overall_structure' in suggestions:
            custom_template = {
                'name': 'AI-Suggested Structure',
                'sections': []
            }
            
            structure = suggestions['overall_structure']
            if 'introduction' in structure:
                custom_template['sections'].append({
                    'title': 'Introduction',
                    'content': structure['introduction'].get('template', '')
                })
                
            for section in structure.get('main_sections', []):
                custom_template['sections'].append({
                    'title': section.get('title', 'Section'),
                    'content': section.get('template', '')
                })
                
            if 'conclusion' in structure:
                custom_template['sections'].append({
                    'title': 'Conclusion',
                    'content': structure['conclusion'].get('template', '')
                })
                
            templates.append(custom_template)
            
        return templates
        
    def _get_best_practices(self, content_type: str) -> List[str]:
        """Get best practices for content type"""
        best_practices = {
            'lesson_plan': [
                'Start with clear, measurable learning objectives',
                'Include diverse activities to accommodate different learning styles',
                'Build in assessment checkpoints throughout the lesson',
                'Allow time for questions and discussion',
                'End with a summary and preview of next lesson'
            ],
            'assessment': [
                'Align questions directly with learning objectives',
                'Use a variety of question types',
                'Progress from simple to complex questions',
                'Provide clear instructions and scoring rubrics',
                'Include both formative and summative elements'
            ],
            'report': [
                'Lead with key findings and recommendations',
                'Use data visualizations to support points',
                'Keep language clear and jargon-free',
                'Include specific, actionable next steps',
                'Proofread for clarity and professionalism'
            ]
        }
        
        return best_practices.get(content_type, [
            'Define clear objectives',
            'Know your audience',
            'Use clear, concise language',
            'Include relevant examples',
            'Review and revise before finalizing'
        ])
        
    def _identify_skill_gaps(self, beneficiary_id: int, db: Session) -> List[str]:
        """Identify skill gaps from assessment data"""
        # Get recent test results
        recent_results = db.query(TestResult).join(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id,
            TestResult.score < 70  # Threshold for identifying gaps
        ).order_by(TestResult.created_at.desc()).limit(20).all()
        
        skill_gaps = []
        for result in recent_results:
            if result.question and result.question.category:
                skill_gaps.append(result.question.category)
                
        # Return unique skill gaps
        return list(set(skill_gaps))
        
    def _analyze_learning_preferences(self, beneficiary_id: int, db: Session) -> Dict[str, Any]:
        """Analyze learning preferences from activity data"""
        # This is a simplified version - in production, this would involve
        # more sophisticated analysis of user behavior patterns
        
        preferences = {
            'preferred_content_types': [],
            'optimal_session_length': 30,  # minutes
            'best_performance_time': 'morning',
            'learning_style': 'visual'
        }
        
        # Analyze document access patterns
        document_access = db.query(Document.document_type, 
                                 db.func.count(Document.id)).filter(
            Document.created_by == beneficiary_id
        ).group_by(Document.document_type).all()
        
        if document_access:
            preferences['preferred_content_types'] = [
                doc_type for doc_type, count in sorted(
                    document_access, key=lambda x: x[1], reverse=True
                )[:3]
            ]
            
        return preferences
        
    def _extract_topics_from_notes(self, notes: List[Note]) -> List[str]:
        """Extract topics from recent notes"""
        topics = []
        
        for note in notes:
            if note.tags:
                topics.extend(note.tags)
                
            # Simple keyword extraction from note content
            # In production, this would use NLP techniques
            content_words = note.content.lower().split()
            common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at'}
            keywords = [w for w in content_words if len(w) > 4 and w not in common_words]
            topics.extend(keywords[:3])
            
        # Return unique topics, most common first
        topic_counts = {}
        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
        return [topic for topic, count in sorted(
            topic_counts.items(), key=lambda x: x[1], reverse=True
        )][:10]
        
    def _analyze_performance_trends(self, beneficiary_id: int, db: Session) -> Dict[str, Any]:
        """Analyze performance trends from assessment data"""
        recent_assessments = db.query(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id,
            Assessment.status == 'completed'
        ).order_by(Assessment.completed_at.desc()).limit(10).all()
        
        if not recent_assessments:
            return {'overall_trend': 'no_data'}
            
        scores = [a.score for a in recent_assessments if a.score is not None]
        
        if len(scores) < 2:
            return {'overall_trend': 'insufficient_data'}
            
        # Simple trend analysis
        recent_avg = sum(scores[:3]) / 3
        older_avg = sum(scores[-3:]) / 3
        
        if recent_avg > older_avg + 5:
            trend = 'improving'
        elif recent_avg < older_avg - 5:
            trend = 'declining'
        else:
            trend = 'stable'
            
        return {
            'overall_trend': trend,
            'recent_average': recent_avg,
            'score_range': {'min': min(scores), 'max': max(scores)}
        }
        
    def _find_matching_documents(self, title: str, description: str,
                               documents: List[Document]) -> List[Document]:
        """Find documents matching recommendation criteria"""
        matches = []
        
        search_terms = (title + ' ' + description).lower().split()
        
        for doc in documents:
            doc_text = (doc.title + ' ' + (doc.description or '')).lower()
            match_score = sum(1 for term in search_terms if term in doc_text)
            
            if match_score > 0:
                matches.append((doc, match_score))
                
        # Sort by match score and return top matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in matches[:5]]
        
    def _get_completion_history(self, beneficiary_id: int, db: Session) -> List[Dict]:
        """Get history of completed assessments and activities"""
        completed_assessments = db.query(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id,
            Assessment.status == 'completed'
        ).order_by(Assessment.completed_at.desc()).limit(5).all()
        
        return [{
            'id': a.id,
            'type': a.assessment_type,
            'completed_at': a.completed_at.isoformat() if a.completed_at else None,
            'score': a.score
        } for a in completed_assessments]
        
    def _calculate_preference_match(self, recommendations: Dict[str, Any],
                                  beneficiary_id: int, db: Session) -> float:
        """Calculate how well recommendations match user preferences"""
        preferences = self._analyze_learning_preferences(beneficiary_id, db)
        
        if not preferences.get('preferred_content_types'):
            return 0.5  # Neutral match
            
        match_count = 0
        total_count = 0
        
        for rec in recommendations.get('primary_recommendations', []):
            total_count += 1
            if rec.get('type') in preferences['preferred_content_types']:
                match_count += 1
                
        return match_count / total_count if total_count > 0 else 0.5
        
    def _get_fallback_structure(self, content_type: str) -> Dict[str, Any]:
        """Get fallback structure when AI fails"""
        return {
            'content_type': content_type,
            'suggestions': {
                'overall_structure': {
                    'introduction': {'template': 'Start with context and objectives'},
                    'main_sections': [
                        {'title': 'Main Content', 'template': 'Core information here'},
                        {'title': 'Examples', 'template': 'Practical examples'},
                        {'title': 'Summary', 'template': 'Key takeaways'}
                    ],
                    'conclusion': {'template': 'Wrap up and next steps'}
                },
                'content_elements': {
                    'required': ['Clear objectives', 'Main content', 'Summary'],
                    'recommended': ['Examples', 'Visuals', 'Activities'],
                    'optional': ['Additional resources', 'Advanced topics']
                }
            },
            'templates': self._generate_templates(content_type, {}),
            'best_practices': self._get_best_practices(content_type)
        }
        
    def _generate_fallback_recommendations(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback recommendations when AI fails"""
        return {
            'primary_recommendations': [
                {
                    'title': 'Skill Development Resources',
                    'description': 'Resources to address identified skill gaps',
                    'type': 'mixed',
                    'difficulty': 'intermediate',
                    'estimated_time': '1-2 hours',
                    'learning_objectives': ['Improve core skills'],
                    'relevance_score': 0.7
                }
            ],
            'supplementary_resources': [],
            'learning_path': {
                'immediate': ['Review fundamentals'],
                'short_term': ['Practice exercises'],
                'long_term': ['Advanced topics']
            },
            'personalized_tips': [
                'Focus on consistent practice',
                'Review previous materials regularly',
                'Seek help when needed'
            ],
            'engagement_strategies': [
                'Set small, achievable goals',
                'Track your progress',
                'Celebrate improvements'
            ]
        }

# Initialize the service
content_recommendation_service = ContentRecommendationService() 