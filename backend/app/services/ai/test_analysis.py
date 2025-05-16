"""
AI-powered test result analysis service
"""
import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import openai
from sqlalchemy.orm import Session

from backend.app.models import Assessment, AssessmentResult, Question, Response, Beneficiary
from backend.app.utils.config import get_config
from backend.app.services.cache import cache_service

logger = logging.getLogger(__name__)
config = get_config()


class TestAnalysisService:
    """AI-powered test analysis service"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.AI_MODEL or "gpt-4"
        
    def analyze_test_results(self, assessment_id: int, db: Session) -> Dict[str, Any]:
        """
        Analyze test results using AI
        
        Args:
            assessment_id: ID of the assessment to analyze
            db: Database session
            
        Returns:
            Dictionary containing AI analysis results
        """
        # Check cache first
        cache_key = f"ai_analysis:assessment:{assessment_id}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Get assessment data
        assessment = db.query(Assessment).filter_by(id=assessment_id).first()
        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")
        
        assessment_result = db.query(AssessmentResult).filter_by(
            assessment_id=assessment_id
        ).order_by(AssessmentResult.created_at.desc()).first()
        
        if not assessment_result:
            raise ValueError(f"No results found for assessment {assessment_id}")
        
        # Get responses and questions
        responses = db.query(Response).filter_by(
            assessment_id=assessment_id,
            beneficiary_id=assessment_result.beneficiary_id
        ).all()
        
        questions = db.query(Question).filter_by(
            assessment_id=assessment_id
        ).all()
        
        # Prepare data for AI analysis
        test_data = self._prepare_test_data(assessment, assessment_result, questions, responses)
        
        # Perform AI analysis
        analysis = self._perform_ai_analysis(test_data)
        
        # Get beneficiary history for context
        beneficiary_history = self._get_beneficiary_history(
            assessment_result.beneficiary_id, 
            db
        )
        
        # Generate comprehensive analysis
        comprehensive_analysis = self._generate_comprehensive_analysis(
            test_data,
            analysis,
            beneficiary_history
        )
        
        # Cache the results
        cache_service.set(
            cache_key,
            json.dumps(comprehensive_analysis),
            expiry=3600  # 1 hour cache
        )
        
        # Store in database
        self._store_analysis_results(
            assessment_result,
            comprehensive_analysis,
            db
        )
        
        return comprehensive_analysis
    
    def _prepare_test_data(self, assessment: Assessment, result: AssessmentResult,
                          questions: List[Question], responses: List[Response]) -> Dict[str, Any]:
        """Prepare test data for AI analysis"""
        question_map = {q.id: q for q in questions}
        
        response_data = []
        for response in responses:
            question = question_map.get(response.question_id)
            if question:
                response_data.append({
                    'question': question.text,
                    'question_type': question.type,
                    'correct_answer': question.correct_answer,
                    'user_answer': response.answer,
                    'is_correct': response.is_correct,
                    'points_earned': response.points_earned,
                    'max_points': question.points,
                    'time_spent': response.time_spent,
                    'category': question.metadata.get('category') if question.metadata else None
                })
        
        return {
            'assessment_info': {
                'title': assessment.title,
                'type': assessment.type,
                'description': assessment.description,
                'total_questions': len(questions),
                'time_limit': assessment.time_limit
            },
            'result_info': {
                'total_score': result.score,
                'percentage': result.percentage,
                'passed': result.passed,
                'time_taken': result.time_taken,
                'completed_at': result.created_at.isoformat()
            },
            'responses': response_data,
            'performance_metrics': self._calculate_performance_metrics(responses, questions)
        }
    
    def _calculate_performance_metrics(self, responses: List[Response], 
                                     questions: List[Question]) -> Dict[str, Any]:
        """Calculate detailed performance metrics"""
        metrics = {
            'total_questions': len(questions),
            'answered_questions': len(responses),
            'correct_answers': sum(1 for r in responses if r.is_correct),
            'incorrect_answers': sum(1 for r in responses if not r.is_correct),
            'average_time_per_question': np.mean([r.time_spent for r in responses]) if responses else 0,
            'accuracy_rate': sum(1 for r in responses if r.is_correct) / len(responses) if responses else 0
        }
        
        # Category-wise performance
        category_performance = {}
        question_categories = {}
        
        for q in questions:
            category = q.metadata.get('category', 'General') if q.metadata else 'General'
            question_categories[q.id] = category
        
        for response in responses:
            category = question_categories.get(response.question_id, 'General')
            if category not in category_performance:
                category_performance[category] = {
                    'total': 0,
                    'correct': 0,
                    'time_spent': 0
                }
            
            category_performance[category]['total'] += 1
            if response.is_correct:
                category_performance[category]['correct'] += 1
            category_performance[category]['time_spent'] += response.time_spent
        
        # Calculate accuracy for each category
        for category, data in category_performance.items():
            data['accuracy'] = data['correct'] / data['total'] if data['total'] > 0 else 0
            data['avg_time'] = data['time_spent'] / data['total'] if data['total'] > 0 else 0
        
        metrics['category_performance'] = category_performance
        
        return metrics
    
    def _perform_ai_analysis(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform AI analysis on test data"""
        try:
            # Prepare prompt for AI
            prompt = self._create_analysis_prompt(test_data)
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational psychologist and assessment analyst. Analyze test results and provide detailed insights about the student's performance, learning patterns, and areas for improvement."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_analysis = response.choices[0].message.content
            
            # Structure the analysis
            structured_analysis = self._structure_ai_response(ai_analysis)
            
            return structured_analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return self._get_fallback_analysis(test_data)
    
    def _create_analysis_prompt(self, test_data: Dict[str, Any]) -> str:
        """Create detailed prompt for AI analysis"""
        prompt = f"""
        Please analyze the following test results and provide comprehensive insights:
        
        Assessment Information:
        - Title: {test_data['assessment_info']['title']}
        - Type: {test_data['assessment_info']['type']}
        - Total Questions: {test_data['assessment_info']['total_questions']}
        
        Overall Performance:
        - Score: {test_data['result_info']['total_score']}
        - Percentage: {test_data['result_info']['percentage']}%
        - Pass Status: {'Passed' if test_data['result_info']['passed'] else 'Failed'}
        - Time Taken: {test_data['result_info']['time_taken']} seconds
        
        Performance Metrics:
        - Correct Answers: {test_data['performance_metrics']['correct_answers']}
        - Incorrect Answers: {test_data['performance_metrics']['incorrect_answers']}
        - Accuracy Rate: {test_data['performance_metrics']['accuracy_rate']*100:.1f}%
        - Average Time per Question: {test_data['performance_metrics']['average_time_per_question']:.1f} seconds
        
        Category Performance:
        {self._format_category_performance(test_data['performance_metrics']['category_performance'])}
        
        Detailed Responses:
        {self._format_responses(test_data['responses'][:10])}  # Limit to first 10 for token efficiency
        
        Please provide:
        1. Overall assessment of the student's performance
        2. Identification of strong areas and areas needing improvement
        3. Analysis of learning patterns and cognitive strengths
        4. Specific skills demonstrated or lacking
        5. Personalized recommendations for improvement
        6. Suggested next steps for the learning journey
        7. Comparison with typical performance patterns
        8. Emotional and motivational insights if applicable
        """
        
        return prompt
    
    def _format_category_performance(self, category_data: Dict[str, Any]) -> str:
        """Format category performance for prompt"""
        lines = []
        for category, data in category_data.items():
            lines.append(f"- {category}: {data['accuracy']*100:.1f}% accuracy, "
                        f"{data['avg_time']:.1f}s avg time")
        return '\n'.join(lines)
    
    def _format_responses(self, responses: List[Dict[str, Any]]) -> str:
        """Format response data for prompt"""
        lines = []
        for i, response in enumerate(responses, 1):
            status = "✓" if response['is_correct'] else "✗"
            lines.append(f"{i}. {status} {response['question']} "
                        f"(Answer: {response['user_answer']}, "
                        f"Time: {response['time_spent']}s)")
        return '\n'.join(lines)
    
    def _structure_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Structure the AI response into a standardized format"""
        # This is a simplified version - in production, you'd use more sophisticated parsing
        sections = {
            'overall_assessment': '',
            'strong_areas': [],
            'improvement_areas': [],
            'learning_patterns': [],
            'skills_analysis': {},
            'recommendations': [],
            'next_steps': [],
            'comparative_analysis': '',
            'motivational_insights': ''
        }
        
        # Parse AI response into sections
        current_section = None
        lines = ai_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if 'overall assessment' in line.lower():
                current_section = 'overall_assessment'
            elif 'strong areas' in line.lower() or 'strengths' in line.lower():
                current_section = 'strong_areas'
            elif 'improvement' in line.lower() or 'weaknesses' in line.lower():
                current_section = 'improvement_areas'
            elif 'learning patterns' in line.lower():
                current_section = 'learning_patterns'
            elif 'skills' in line.lower():
                current_section = 'skills_analysis'
            elif 'recommendations' in line.lower():
                current_section = 'recommendations'
            elif 'next steps' in line.lower():
                current_section = 'next_steps'
            elif 'comparison' in line.lower() or 'comparative' in line.lower():
                current_section = 'comparative_analysis'
            elif 'motivation' in line.lower() or 'emotional' in line.lower():
                current_section = 'motivational_insights'
            else:
                # Add content to current section
                if current_section:
                    if isinstance(sections[current_section], list):
                        if line.startswith('-') or line.startswith('•'):
                            sections[current_section].append(line[1:].strip())
                    elif isinstance(sections[current_section], str):
                        sections[current_section] += line + ' '
                    elif isinstance(sections[current_section], dict):
                        # Parse key-value pairs for skills
                        if ':' in line:
                            key, value = line.split(':', 1)
                            sections[current_section][key.strip()] = value.strip()
        
        # Clean up string sections
        for key in sections:
            if isinstance(sections[key], str):
                sections[key] = sections[key].strip()
        
        return sections
    
    def _get_fallback_analysis(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback analysis when AI is unavailable"""
        metrics = test_data['performance_metrics']
        
        # Determine strong and weak areas based on category performance
        strong_areas = []
        improvement_areas = []
        
        for category, data in metrics['category_performance'].items():
            if data['accuracy'] >= 0.8:
                strong_areas.append(f"{category} ({data['accuracy']*100:.0f}% accuracy)")
            elif data['accuracy'] < 0.6:
                improvement_areas.append(f"{category} ({data['accuracy']*100:.0f}% accuracy)")
        
        return {
            'overall_assessment': f"The student achieved {test_data['result_info']['percentage']}% "
                                f"on this assessment, {'passing' if test_data['result_info']['passed'] else 'not meeting'} "
                                f"the required standard.",
            'strong_areas': strong_areas,
            'improvement_areas': improvement_areas,
            'learning_patterns': [
                f"Average time per question: {metrics['average_time_per_question']:.1f} seconds",
                f"Overall accuracy: {metrics['accuracy_rate']*100:.1f}%"
            ],
            'skills_analysis': {
                'Problem Solving': 'Needs assessment',
                'Time Management': 'Needs assessment',
                'Critical Thinking': 'Needs assessment'
            },
            'recommendations': [
                "Focus on categories with lower performance",
                "Review incorrect answers and understand concepts",
                "Practice time management skills"
            ],
            'next_steps': [
                "Review weak areas with instructor",
                "Complete practice exercises",
                "Take follow-up assessment"
            ],
            'comparative_analysis': 'Comparative analysis requires historical data',
            'motivational_insights': 'Continue practicing to improve performance'
        }
    
    def _get_beneficiary_history(self, beneficiary_id: int, db: Session) -> Dict[str, Any]:
        """Get beneficiary's assessment history for context"""
        # Get last 5 assessments
        recent_results = db.query(AssessmentResult).filter_by(
            beneficiary_id=beneficiary_id
        ).order_by(AssessmentResult.created_at.desc()).limit(5).all()
        
        history = {
            'total_assessments': len(recent_results),
            'average_score': np.mean([r.percentage for r in recent_results]) if recent_results else 0,
            'trend': self._calculate_trend(recent_results),
            'consistency': self._calculate_consistency(recent_results),
            'recent_performance': []
        }
        
        for result in recent_results:
            history['recent_performance'].append({
                'date': result.created_at.isoformat(),
                'score': result.percentage,
                'passed': result.passed
            })
        
        return history
    
    def _calculate_trend(self, results: List[AssessmentResult]) -> str:
        """Calculate performance trend"""
        if len(results) < 2:
            return 'insufficient_data'
        
        scores = [r.percentage for r in results]
        scores.reverse()  # Oldest to newest
        
        # Simple linear regression
        x = np.arange(len(scores))
        coefficients = np.polyfit(x, scores, 1)
        slope = coefficients[0]
        
        if slope > 1:
            return 'improving'
        elif slope < -1:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_consistency(self, results: List[AssessmentResult]) -> float:
        """Calculate performance consistency"""
        if len(results) < 2:
            return 0.0
        
        scores = [r.percentage for r in results]
        return 1 - (np.std(scores) / np.mean(scores)) if np.mean(scores) > 0 else 0
    
    def _generate_comprehensive_analysis(self, test_data: Dict[str, Any], 
                                       ai_analysis: Dict[str, Any],
                                       beneficiary_history: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis combining AI insights and historical data"""
        
        # Enhance AI analysis with historical context
        enhanced_analysis = ai_analysis.copy()
        
        # Add trend analysis
        if beneficiary_history['trend'] == 'improving':
            enhanced_analysis['trend_analysis'] = {
                'trend': 'improving',
                'message': 'Performance has been consistently improving over recent assessments.'
            }
        elif beneficiary_history['trend'] == 'declining':
            enhanced_analysis['trend_analysis'] = {
                'trend': 'declining',
                'message': 'Performance has been declining. Additional support may be needed.'
            }
        else:
            enhanced_analysis['trend_analysis'] = {
                'trend': 'stable',
                'message': 'Performance has been stable across recent assessments.'
            }
        
        # Add consistency score
        enhanced_analysis['consistency_score'] = beneficiary_history['consistency']
        
        # Add comparative analysis if not provided by AI
        if not enhanced_analysis.get('comparative_analysis'):
            avg_score = beneficiary_history['average_score']
            current_score = test_data['result_info']['percentage']
            
            if current_score > avg_score + 10:
                enhanced_analysis['comparative_analysis'] = 'Significantly above average performance'
            elif current_score < avg_score - 10:
                enhanced_analysis['comparative_analysis'] = 'Below average performance'
            else:
                enhanced_analysis['comparative_analysis'] = 'Performance consistent with average'
        
        # Add personalized insights
        enhanced_analysis['personalized_insights'] = self._generate_personalized_insights(
            test_data,
            ai_analysis,
            beneficiary_history
        )
        
        # Add metadata
        enhanced_analysis['analysis_metadata'] = {
            'generated_at': datetime.utcnow().isoformat(),
            'ai_model': self.model,
            'confidence_score': self._calculate_confidence_score(ai_analysis),
            'data_quality': self._assess_data_quality(test_data)
        }
        
        return enhanced_analysis
    
    def _generate_personalized_insights(self, test_data: Dict[str, Any],
                                      ai_analysis: Dict[str, Any],
                                      history: Dict[str, Any]) -> List[str]:
        """Generate personalized insights based on comprehensive data"""
        insights = []
        
        # Performance-based insights
        current_score = test_data['result_info']['percentage']
        if current_score >= 90:
            insights.append("Exceptional performance! Consider advanced challenges.")
        elif current_score >= 80:
            insights.append("Strong performance. Focus on mastering remaining concepts.")
        elif current_score >= 70:
            insights.append("Good progress. Identify specific areas for targeted improvement.")
        else:
            insights.append("Additional support recommended to strengthen foundation.")
        
        # Time management insights
        avg_time = test_data['performance_metrics']['average_time_per_question']
        if test_data['assessment_info']['time_limit']:
            time_pressure = test_data['result_info']['time_taken'] / test_data['assessment_info']['time_limit']
            if time_pressure > 0.9:
                insights.append("Time management needs attention - using nearly all available time.")
            elif time_pressure < 0.5:
                insights.append("Excellent time management - consider reviewing answers if time permits.")
        
        # Category-specific insights
        cat_performance = test_data['performance_metrics']['category_performance']
        for category, data in cat_performance.items():
            if data['accuracy'] < 0.5:
                insights.append(f"Priority focus area: {category} (needs significant improvement)")
            elif data['accuracy'] > 0.9:
                insights.append(f"Mastery demonstrated in {category}")
        
        # Trend-based insights
        if history['trend'] == 'improving' and history['consistency'] > 0.8:
            insights.append("Consistent improvement shows effective learning strategies.")
        elif history['trend'] == 'declining':
            insights.append("Recent decline suggests need for learning approach review.")
        
        return insights
    
    def _calculate_confidence_score(self, ai_analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        # Simple heuristic based on completeness of analysis
        total_sections = len(ai_analysis)
        filled_sections = sum(1 for v in ai_analysis.values() 
                            if v and (isinstance(v, str) and v.strip() or 
                                     isinstance(v, list) and len(v) > 0 or
                                     isinstance(v, dict) and len(v) > 0))
        
        return filled_sections / total_sections if total_sections > 0 else 0
    
    def _assess_data_quality(self, test_data: Dict[str, Any]) -> str:
        """Assess the quality of input data"""
        total_questions = test_data['assessment_info']['total_questions']
        answered_questions = test_data['performance_metrics']['answered_questions']
        
        completion_rate = answered_questions / total_questions if total_questions > 0 else 0
        
        if completion_rate >= 0.95:
            return 'excellent'
        elif completion_rate >= 0.8:
            return 'good'
        elif completion_rate >= 0.6:
            return 'fair'
        else:
            return 'poor'
    
    def _store_analysis_results(self, assessment_result: AssessmentResult,
                              analysis: Dict[str, Any], db: Session):
        """Store AI analysis results in database"""
        try:
            # Update assessment result with AI analysis
            assessment_result.ai_analysis = analysis
            db.commit()
            
            logger.info(f"Stored AI analysis for assessment result {assessment_result.id}")
            
        except Exception as e:
            logger.error(f"Error storing AI analysis: {str(e)}")
            db.rollback()
    
    def compare_with_peers(self, assessment_result_id: int, db: Session) -> Dict[str, Any]:
        """Compare assessment results with peer group"""
        result = db.query(AssessmentResult).filter_by(id=assessment_result_id).first()
        if not result:
            raise ValueError(f"Assessment result {assessment_result_id} not found")
        
        # Get peer results (same assessment type, similar time period)
        peer_results = db.query(AssessmentResult).join(Assessment).filter(
            Assessment.type == result.assessment.type,
            AssessmentResult.created_at >= datetime.utcnow() - timedelta(days=30),
            AssessmentResult.id != assessment_result_id
        ).all()
        
        if not peer_results:
            return {
                'peer_comparison': 'No peer data available',
                'percentile': None,
                'relative_performance': None
            }
        
        # Calculate percentile
        peer_scores = [r.percentage for r in peer_results]
        peer_scores.append(result.percentage)
        peer_scores.sort()
        
        percentile = (peer_scores.index(result.percentage) + 1) / len(peer_scores) * 100
        
        # Calculate relative performance
        avg_peer_score = np.mean(peer_scores[:-1])  # Exclude current result
        relative_performance = (result.percentage - avg_peer_score) / avg_peer_score * 100
        
        return {
            'peer_comparison': {
                'total_peers': len(peer_results),
                'average_peer_score': avg_peer_score,
                'highest_peer_score': max(peer_scores[:-1]),
                'lowest_peer_score': min(peer_scores[:-1])
            },
            'percentile': percentile,
            'relative_performance': relative_performance,
            'performance_level': self._get_performance_level(percentile)
        }
    
    def _get_performance_level(self, percentile: float) -> str:
        """Determine performance level based on percentile"""
        if percentile >= 90:
            return 'exceptional'
        elif percentile >= 75:
            return 'above_average'
        elif percentile >= 50:
            return 'average'
        elif percentile >= 25:
            return 'below_average'
        else:
            return 'needs_improvement'
    
    def generate_improvement_plan(self, assessment_result_id: int, db: Session) -> Dict[str, Any]:
        """Generate personalized improvement plan based on analysis"""
        result = db.query(AssessmentResult).filter_by(id=assessment_result_id).first()
        if not result or not result.ai_analysis:
            raise ValueError(f"No AI analysis found for assessment result {assessment_result_id}")
        
        ai_analysis = result.ai_analysis
        improvement_plan = {
            'focus_areas': [],
            'recommended_resources': [],
            'practice_exercises': [],
            'timeline': {},
            'milestones': []
        }
        
        # Identify focus areas from improvement areas
        for area in ai_analysis.get('improvement_areas', []):
            improvement_plan['focus_areas'].append({
                'area': area,
                'priority': 'high' if 'critical' in area.lower() else 'medium',
                'estimated_hours': 5  # Default estimate
            })
        
        # Generate timeline
        total_weeks = max(4, len(improvement_plan['focus_areas']) * 2)
        improvement_plan['timeline'] = {
            'total_duration': f"{total_weeks} weeks",
            'hours_per_week': 10,
            'sessions_per_week': 3
        }
        
        # Create milestones
        for i in range(0, total_weeks, 2):
            improvement_plan['milestones'].append({
                'week': i + 2,
                'goal': f"Complete focus area {i//2 + 1}",
                'assessment': 'Progress quiz',
                'success_criteria': '80% accuracy'
            })
        
        # Add AI-generated recommendations
        if 'recommendations' in ai_analysis:
            for rec in ai_analysis['recommendations']:
                improvement_plan['recommended_resources'].append({
                    'type': 'recommendation',
                    'content': rec,
                    'priority': 'high'
                })
        
        return improvement_plan


# Singleton instance
test_analysis_service = TestAnalysisService()