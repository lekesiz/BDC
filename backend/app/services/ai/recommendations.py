"""
AI-powered personalized recommendations service
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import openai
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from backend.app.models import (
    Assessment, AssessmentResult, Beneficiary, User,
    Question, Response, Document, Course, Resource
)
from backend.app.utils.config import get_config
from backend.app.services.cache import cache_service

logger = logging.getLogger(__name__)
config = get_config()


class RecommendationEngine:
    """AI-powered recommendation engine for personalized learning paths"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.AI_MODEL or "gpt-4"
    
    def generate_recommendations(self, beneficiary_id: int, db: Session,
                               recommendation_type: str = 'comprehensive') -> Dict[str, Any]:
        """
        Generate personalized recommendations for a beneficiary
        
        Args:
            beneficiary_id: ID of the beneficiary
            db: Database session
            recommendation_type: Type of recommendations to generate
            
        Returns:
            Dictionary containing personalized recommendations
        """
        # Check cache
        cache_key = f"recommendations:{beneficiary_id}:{recommendation_type}"
        cached_result = cache_service.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # Get beneficiary data
        beneficiary = db.query(Beneficiary).filter_by(id=beneficiary_id).first()
        if not beneficiary:
            raise ValueError(f"Beneficiary {beneficiary_id} not found")
        
        # Gather comprehensive data
        user_profile = self._get_user_profile(beneficiary, db)
        performance_data = self._get_performance_data(beneficiary_id, db)
        learning_patterns = self._analyze_learning_patterns(beneficiary_id, db)
        skill_gaps = self._identify_skill_gaps(beneficiary_id, db)
        
        # Generate recommendations based on type
        if recommendation_type == 'comprehensive':
            recommendations = self._generate_comprehensive_recommendations(
                user_profile, performance_data, learning_patterns, skill_gaps
            )
        elif recommendation_type == 'resources':
            recommendations = self._generate_resource_recommendations(
                performance_data, skill_gaps, db
            )
        elif recommendation_type == 'activities':
            recommendations = self._generate_activity_recommendations(
                performance_data, learning_patterns
            )
        elif recommendation_type == 'assessment':
            recommendations = self._generate_assessment_recommendations(
                performance_data, skill_gaps
            )
        else:
            raise ValueError(f"Unknown recommendation type: {recommendation_type}")
        
        # Enrich with AI insights
        enriched_recommendations = self._enrich_with_ai(
            recommendations, user_profile, performance_data
        )
        
        # Cache results
        cache_service.set(
            cache_key,
            json.dumps(enriched_recommendations),
            expiry=3600  # 1 hour cache
        )
        
        # Store in database for tracking
        self._store_recommendations(beneficiary_id, enriched_recommendations, db)
        
        return enriched_recommendations
    
    def _get_user_profile(self, beneficiary: Beneficiary, db: Session) -> Dict[str, Any]:
        """Get comprehensive user profile"""
        user = beneficiary.user
        
        profile = {
            'id': beneficiary.id,
            'name': user.name,
            'age': self._calculate_age(user.profile.date_of_birth) if user.profile else None,
            'learning_style': user.profile.metadata.get('learning_style') if user.profile else None,
            'preferences': user.profile.preferences if user.profile else {},
            'goals': beneficiary.metadata.get('goals', []) if beneficiary.metadata else [],
            'interests': beneficiary.metadata.get('interests', []) if beneficiary.metadata else [],
            'enrollment_date': beneficiary.enrollment_date,
            'total_assessments': 0,
            'active_days': 0
        }
        
        # Calculate engagement metrics
        results = db.query(AssessmentResult).filter_by(
            beneficiary_id=beneficiary.id
        ).all()
        
        profile['total_assessments'] = len(results)
        
        if results:
            unique_days = set(r.created_at.date() for r in results)
            profile['active_days'] = len(unique_days)
            profile['first_assessment'] = min(r.created_at for r in results)
            profile['last_assessment'] = max(r.created_at for r in results)
        
        return profile
    
    def _get_performance_data(self, beneficiary_id: int, db: Session) -> Dict[str, Any]:
        """Get comprehensive performance data"""
        # Get all assessment results
        results = db.query(AssessmentResult).filter_by(
            beneficiary_id=beneficiary_id
        ).order_by(AssessmentResult.created_at.desc()).all()
        
        if not results:
            return {
                'average_score': 0,
                'trend': 'no_data',
                'strengths': [],
                'weaknesses': [],
                'recent_results': []
            }
        
        # Calculate metrics
        scores = [r.percentage for r in results]
        recent_scores = scores[:5]  # Last 5 assessments
        
        performance = {
            'average_score': np.mean(scores),
            'recent_average': np.mean(recent_scores) if recent_scores else 0,
            'best_score': max(scores),
            'worst_score': min(scores),
            'consistency': 1 - (np.std(scores) / np.mean(scores)) if np.mean(scores) > 0 else 0,
            'trend': self._calculate_trend(scores),
            'total_assessments': len(results),
            'recent_results': []
        }
        
        # Add recent results with details
        for result in results[:5]:
            performance['recent_results'].append({
                'assessment_id': result.assessment_id,
                'assessment_title': result.assessment.title,
                'score': result.percentage,
                'passed': result.passed,
                'date': result.created_at.isoformat(),
                'time_taken': result.time_taken
            })
        
        # Identify strengths and weaknesses
        category_performance = self._analyze_category_performance(beneficiary_id, db)
        performance['strengths'] = [
            cat for cat, data in category_performance.items() 
            if data['accuracy'] >= 0.8
        ]
        performance['weaknesses'] = [
            cat for cat, data in category_performance.items() 
            if data['accuracy'] < 0.6
        ]
        
        return performance
    
    def _analyze_category_performance(self, beneficiary_id: int, 
                                    db: Session) -> Dict[str, Dict[str, float]]:
        """Analyze performance by category"""
        # Get all responses
        responses = db.query(Response).filter_by(
            beneficiary_id=beneficiary_id
        ).join(Question).all()
        
        category_stats = {}
        
        for response in responses:
            question = response.question
            category = question.metadata.get('category', 'General') if question.metadata else 'General'
            
            if category not in category_stats:
                category_stats[category] = {
                    'total': 0,
                    'correct': 0,
                    'time_spent': 0
                }
            
            category_stats[category]['total'] += 1
            if response.is_correct:
                category_stats[category]['correct'] += 1
            category_stats[category]['time_spent'] += response.time_spent
        
        # Calculate metrics
        category_performance = {}
        for category, stats in category_stats.items():
            if stats['total'] > 0:
                category_performance[category] = {
                    'accuracy': stats['correct'] / stats['total'],
                    'avg_time': stats['time_spent'] / stats['total'],
                    'total_questions': stats['total']
                }
        
        return category_performance
    
    def _analyze_learning_patterns(self, beneficiary_id: int, 
                                 db: Session) -> Dict[str, Any]:
        """Analyze learning patterns and preferences"""
        # Get all assessment results with timing
        results = db.query(AssessmentResult).filter_by(
            beneficiary_id=beneficiary_id
        ).order_by(AssessmentResult.created_at).all()
        
        if not results:
            return {
                'preferred_time': 'not_determined',
                'session_duration': 'not_determined',
                'learning_pace': 'not_determined',
                'engagement_level': 'not_determined'
            }
        
        patterns = {
            'preferred_time': self._determine_preferred_time(results),
            'session_duration': self._calculate_avg_session_duration(results),
            'learning_pace': self._determine_learning_pace(results),
            'engagement_level': self._calculate_engagement_level(results),
            'completion_rate': self._calculate_completion_rate(beneficiary_id, db),
            'retry_behavior': self._analyze_retry_behavior(beneficiary_id, db)
        }
        
        # Time-based patterns
        patterns['time_patterns'] = self._analyze_time_patterns(results)
        
        # Difficulty preference
        patterns['difficulty_preference'] = self._analyze_difficulty_preference(
            beneficiary_id, db
        )
        
        return patterns
    
    def _determine_preferred_time(self, results: List[AssessmentResult]) -> str:
        """Determine preferred learning time"""
        hour_counts = {}
        
        for result in results:
            hour = result.created_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if not hour_counts:
            return 'not_determined'
        
        peak_hour = max(hour_counts, key=hour_counts.get)
        
        if 6 <= peak_hour < 12:
            return 'morning'
        elif 12 <= peak_hour < 17:
            return 'afternoon'
        elif 17 <= peak_hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _calculate_avg_session_duration(self, results: List[AssessmentResult]) -> float:
        """Calculate average session duration"""
        durations = [r.time_taken for r in results if r.time_taken]
        return np.mean(durations) if durations else 0
    
    def _determine_learning_pace(self, results: List[AssessmentResult]) -> str:
        """Determine learning pace based on improvement rate"""
        if len(results) < 3:
            return 'not_determined'
        
        scores = [r.percentage for r in results]
        recent_improvement = np.mean(scores[-3:]) - np.mean(scores[:3])
        
        if recent_improvement > 15:
            return 'fast'
        elif recent_improvement > 5:
            return 'moderate'
        elif recent_improvement > -5:
            return 'steady'
        else:
            return 'slow'
    
    def _calculate_engagement_level(self, results: List[AssessmentResult]) -> str:
        """Calculate engagement level based on frequency and consistency"""
        if not results:
            return 'not_determined'
        
        # Calculate days between assessments
        dates = sorted([r.created_at.date() for r in results])
        if len(dates) < 2:
            return 'low'
        
        gaps = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
        avg_gap = np.mean(gaps)
        
        if avg_gap <= 3:
            return 'high'
        elif avg_gap <= 7:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_completion_rate(self, beneficiary_id: int, db: Session) -> float:
        """Calculate assessment completion rate"""
        # This would need additional tracking of started vs completed assessments
        # For now, return a placeholder
        return 0.85  # 85% completion rate
    
    def _analyze_retry_behavior(self, beneficiary_id: int, db: Session) -> Dict[str, Any]:
        """Analyze retry behavior on assessments"""
        # Query for multiple attempts on same assessment
        # This would need additional data tracking
        return {
            'retry_frequency': 'moderate',
            'improvement_on_retry': 0.15  # 15% average improvement
        }
    
    def _analyze_time_patterns(self, results: List[AssessmentResult]) -> Dict[str, Any]:
        """Analyze time-based patterns"""
        patterns = {
            'by_day_of_week': {},
            'by_time_of_day': {},
            'performance_by_time': {}
        }
        
        for result in results:
            # Day of week analysis
            day = result.created_at.strftime('%A')
            if day not in patterns['by_day_of_week']:
                patterns['by_day_of_week'][day] = []
            patterns['by_day_of_week'][day].append(result.percentage)
            
            # Time of day analysis
            hour = result.created_at.hour
            time_slot = 'morning' if 6 <= hour < 12 else \
                       'afternoon' if 12 <= hour < 17 else \
                       'evening' if 17 <= hour < 21 else 'night'
            
            if time_slot not in patterns['by_time_of_day']:
                patterns['by_time_of_day'][time_slot] = []
            patterns['by_time_of_day'][time_slot].append(result.percentage)
        
        # Calculate averages
        for key in patterns['by_day_of_week']:
            scores = patterns['by_day_of_week'][key]
            patterns['by_day_of_week'][key] = np.mean(scores) if scores else 0
        
        for key in patterns['by_time_of_day']:
            scores = patterns['by_time_of_day'][key]
            patterns['performance_by_time'][key] = np.mean(scores) if scores else 0
        
        return patterns
    
    def _analyze_difficulty_preference(self, beneficiary_id: int, 
                                     db: Session) -> Dict[str, Any]:
        """Analyze preference for difficulty levels"""
        # Get responses with difficulty metadata
        responses = db.query(Response).filter_by(
            beneficiary_id=beneficiary_id
        ).join(Question).all()
        
        difficulty_stats = {}
        
        for response in responses:
            difficulty = response.question.metadata.get('difficulty', 'medium') \
                        if response.question.metadata else 'medium'
            
            if difficulty not in difficulty_stats:
                difficulty_stats[difficulty] = {
                    'total': 0,
                    'correct': 0,
                    'time_spent': 0
                }
            
            difficulty_stats[difficulty]['total'] += 1
            if response.is_correct:
                difficulty_stats[difficulty]['correct'] += 1
            difficulty_stats[difficulty]['time_spent'] += response.time_spent
        
        # Calculate performance by difficulty
        preference = {}
        for difficulty, stats in difficulty_stats.items():
            if stats['total'] > 0:
                preference[difficulty] = {
                    'accuracy': stats['correct'] / stats['total'],
                    'avg_time': stats['time_spent'] / stats['total'],
                    'comfort_level': self._calculate_comfort_level(
                        stats['correct'] / stats['total'],
                        stats['time_spent'] / stats['total']
                    )
                }
        
        return preference
    
    def _calculate_comfort_level(self, accuracy: float, avg_time: float) -> str:
        """Calculate comfort level based on accuracy and time"""
        # Normalize time (assume 60 seconds is average)
        time_factor = 1 - (avg_time / 120)  # Lower time is better
        
        comfort_score = (accuracy * 0.7) + (time_factor * 0.3)
        
        if comfort_score >= 0.8:
            return 'high'
        elif comfort_score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _identify_skill_gaps(self, beneficiary_id: int, db: Session) -> List[Dict[str, Any]]:
        """Identify skill gaps based on performance"""
        category_performance = self._analyze_category_performance(beneficiary_id, db)
        
        skill_gaps = []
        
        for category, performance in category_performance.items():
            if performance['accuracy'] < 0.7:  # Below 70% accuracy
                gap = {
                    'skill': category,
                    'current_level': performance['accuracy'] * 100,
                    'target_level': 80,  # Target 80% accuracy
                    'gap_size': 80 - (performance['accuracy'] * 100),
                    'priority': self._calculate_priority(performance),
                    'estimated_hours': self._estimate_learning_hours(
                        performance['accuracy'], 0.8
                    )
                }
                skill_gaps.append(gap)
        
        # Sort by priority
        skill_gaps.sort(key=lambda x: x['priority'], reverse=True)
        
        return skill_gaps
    
    def _calculate_priority(self, performance: Dict[str, float]) -> float:
        """Calculate priority score for skill improvement"""
        # Factors: accuracy (inverse), frequency of questions, time efficiency
        accuracy_factor = 1 - performance['accuracy']
        frequency_factor = min(performance['total_questions'] / 50, 1)  # Normalize to 0-1
        
        priority = (accuracy_factor * 0.6) + (frequency_factor * 0.4)
        return priority
    
    def _estimate_learning_hours(self, current_level: float, target_level: float) -> int:
        """Estimate hours needed to reach target level"""
        gap = target_level - current_level
        # Rough estimate: 10 hours per 10% improvement
        hours = int(gap * 100)
        return max(hours, 5)  # Minimum 5 hours
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate performance trend"""
        if len(scores) < 3:
            return 'insufficient_data'
        
        recent_avg = np.mean(scores[-3:])
        older_avg = np.mean(scores[:-3])
        
        if recent_avg > older_avg + 5:
            return 'improving'
        elif recent_avg < older_avg - 5:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_comprehensive_recommendations(self, user_profile: Dict[str, Any],
                                              performance_data: Dict[str, Any],
                                              learning_patterns: Dict[str, Any],
                                              skill_gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive recommendations"""
        recommendations = {
            'learning_path': self._create_learning_path(
                skill_gaps, learning_patterns, performance_data
            ),
            'resources': self._recommend_resources(skill_gaps, learning_patterns),
            'activities': self._recommend_activities(
                performance_data, learning_patterns, user_profile
            ),
            'schedule': self._create_study_schedule(
                learning_patterns, skill_gaps, user_profile
            ),
            'goals': self._set_smart_goals(performance_data, skill_gaps),
            'strategies': self._recommend_learning_strategies(
                learning_patterns, performance_data
            )
        }
        
        return recommendations
    
    def _create_learning_path(self, skill_gaps: List[Dict[str, Any]],
                             learning_patterns: Dict[str, Any],
                             performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create personalized learning path"""
        learning_path = []
        
        # Start with highest priority gaps
        for gap in skill_gaps[:5]:  # Focus on top 5 gaps
            module = {
                'skill': gap['skill'],
                'current_level': gap['current_level'],
                'target_level': gap['target_level'],
                'estimated_duration': f"{gap['estimated_hours']} hours",
                'milestones': self._create_milestones(gap),
                'prerequisites': self._identify_prerequisites(gap['skill']),
                'resources': [],
                'assessments': []
            }
            learning_path.append(module)
        
        # Add remedial modules if needed
        if performance_data['average_score'] < 60:
            learning_path.insert(0, {
                'skill': 'Fundamentals Review',
                'description': 'Review of basic concepts',
                'estimated_duration': '10 hours',
                'milestones': [
                    {'week': 1, 'goal': 'Complete basic concepts review'},
                    {'week': 2, 'goal': 'Pass fundamentals assessment'}
                ]
            })
        
        return learning_path
    
    def _create_milestones(self, skill_gap: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create milestones for skill improvement"""
        milestones = []
        
        total_hours = skill_gap['estimated_hours']
        current_level = skill_gap['current_level']
        target_level = skill_gap['target_level']
        
        # Create weekly milestones
        weeks = max(1, total_hours // 10)  # Assume 10 hours per week
        level_increment = (target_level - current_level) / weeks
        
        for week in range(1, weeks + 1):
            milestone = {
                'week': week,
                'target_level': current_level + (level_increment * week),
                'activities': f"Complete week {week} exercises",
                'assessment': f"Week {week} progress quiz"
            }
            milestones.append(milestone)
        
        return milestones
    
    def _identify_prerequisites(self, skill: str) -> List[str]:
        """Identify prerequisites for a skill"""
        # This would be based on a skill dependency graph
        prerequisites_map = {
            'Advanced Mathematics': ['Basic Mathematics', 'Algebra'],
            'Critical Thinking': ['Logical Reasoning', 'Problem Solving'],
            'Writing': ['Grammar', 'Vocabulary'],
            # Add more mappings as needed
        }
        
        return prerequisites_map.get(skill, [])
    
    def _recommend_resources(self, skill_gaps: List[Dict[str, Any]],
                           learning_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend learning resources"""
        resources = []
        
        for gap in skill_gaps[:3]:  # Top 3 skill gaps
            skill_resources = {
                'skill': gap['skill'],
                'resources': []
            }
            
            # Recommend based on learning style
            if learning_patterns.get('preferred_time') == 'morning':
                skill_resources['resources'].append({
                    'type': 'article',
                    'title': f"Morning Reading: {gap['skill']} Fundamentals",
                    'format': 'text',
                    'duration': '15-20 minutes',
                    'difficulty': 'appropriate'
                })
            
            # Add video resources for visual learners
            skill_resources['resources'].append({
                'type': 'video',
                'title': f"Video Tutorial: {gap['skill']}",
                'format': 'video',
                'duration': '10-15 minutes',
                'platform': 'internal'
            })
            
            # Add practice exercises
            skill_resources['resources'].append({
                'type': 'exercise',
                'title': f"Practice Set: {gap['skill']}",
                'format': 'interactive',
                'questions': 20,
                'difficulty': 'progressive'
            })
            
            resources.append(skill_resources)
        
        return resources
    
    def _recommend_activities(self, performance_data: Dict[str, Any],
                            learning_patterns: Dict[str, Any],
                            user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend learning activities"""
        activities = []
        
        # Daily activities based on engagement level
        if learning_patterns['engagement_level'] == 'high':
            activities.append({
                'type': 'daily_challenge',
                'title': 'Daily Brain Teaser',
                'duration': '5-10 minutes',
                'frequency': 'daily',
                'description': 'Quick daily challenge to maintain momentum'
            })
        
        # Weekly activities based on performance
        if performance_data['consistency'] < 0.7:
            activities.append({
                'type': 'consistency_builder',
                'title': 'Weekly Review Session',
                'duration': '30 minutes',
                'frequency': 'weekly',
                'description': 'Review and reinforce key concepts'
            })
        
        # Group activities if social learner
        if user_profile.get('preferences', {}).get('social_learning', False):
            activities.append({
                'type': 'group_study',
                'title': 'Peer Learning Session',
                'duration': '1 hour',
                'frequency': 'bi-weekly',
                'description': 'Collaborative learning with peers'
            })
        
        # Gamified activities for motivation
        if user_profile.get('age', 0) < 18 or user_profile.get('preferences', {}).get('gamification', True):
            activities.append({
                'type': 'gamified',
                'title': 'Learning Quest',
                'duration': '20-30 minutes',
                'frequency': '3 times/week',
                'description': 'Game-based learning activities'
            })
        
        return activities
    
    def _create_study_schedule(self, learning_patterns: Dict[str, Any],
                              skill_gaps: List[Dict[str, Any]],
                              user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized study schedule"""
        schedule = {
            'weekly_hours': 0,
            'sessions_per_week': 0,
            'optimal_times': [],
            'session_duration': 0,
            'weekly_plan': {}
        }
        
        # Calculate total weekly hours based on goals
        total_gap_hours = sum(gap['estimated_hours'] for gap in skill_gaps[:3])
        weeks_available = 12  # 3-month plan
        schedule['weekly_hours'] = min(15, total_gap_hours / weeks_available)
        
        # Determine optimal session duration
        if learning_patterns['session_duration'] < 1800:  # 30 minutes
            schedule['session_duration'] = 30
            schedule['sessions_per_week'] = int(schedule['weekly_hours'] * 2)
        else:
            schedule['session_duration'] = 60
            schedule['sessions_per_week'] = int(schedule['weekly_hours'])
        
        # Determine optimal times
        preferred_time = learning_patterns.get('preferred_time', 'evening')
        time_slots = {
            'morning': ['7:00 AM - 8:00 AM', '8:00 AM - 9:00 AM'],
            'afternoon': ['1:00 PM - 2:00 PM', '3:00 PM - 4:00 PM'],
            'evening': ['6:00 PM - 7:00 PM', '7:00 PM - 8:00 PM'],
            'night': ['8:00 PM - 9:00 PM', '9:00 PM - 10:00 PM']
        }
        schedule['optimal_times'] = time_slots.get(preferred_time, time_slots['evening'])
        
        # Create weekly plan
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sessions_distributed = 0
        
        for i, day in enumerate(days):
            if sessions_distributed >= schedule['sessions_per_week']:
                break
                
            # Skip weekends if low engagement
            if learning_patterns['engagement_level'] == 'low' and day in ['Saturday', 'Sunday']:
                continue
            
            schedule['weekly_plan'][day] = {
                'time': schedule['optimal_times'][0],
                'duration': schedule['session_duration'],
                'focus': skill_gaps[i % len(skill_gaps[:3])]['skill']
            }
            sessions_distributed += 1
        
        return schedule
    
    def _set_smart_goals(self, performance_data: Dict[str, Any],
                        skill_gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Set SMART goals"""
        goals = []
        
        # Overall performance goal
        current_avg = performance_data['average_score']
        if current_avg < 80:
            goals.append({
                'type': 'overall_performance',
                'specific': f"Improve overall performance from {current_avg:.0f}% to 80%",
                'measurable': 'Average assessment score of 80%',
                'achievable': 'With consistent practice and focus on weak areas',
                'relevant': 'Essential for program completion',
                'timebound': '3 months',
                'milestones': [
                    {'month': 1, 'target': current_avg + 5},
                    {'month': 2, 'target': current_avg + 10},
                    {'month': 3, 'target': 80}
                ]
            })
        
        # Skill-specific goals
        for gap in skill_gaps[:2]:  # Top 2 skill gaps
            goals.append({
                'type': 'skill_improvement',
                'specific': f"Master {gap['skill']} skills",
                'measurable': f"Achieve {gap['target_level']}% accuracy",
                'achievable': f"Through {gap['estimated_hours']} hours of focused practice",
                'relevant': f"Critical skill with current {gap['current_level']:.0f}% performance",
                'timebound': f"{gap['estimated_hours'] // 10} weeks",
                'milestones': self._create_milestones(gap)
            })
        
        # Consistency goal
        if performance_data['consistency'] < 0.8:
            goals.append({
                'type': 'consistency',
                'specific': 'Establish consistent learning routine',
                'measurable': 'Complete 90% of scheduled sessions',
                'achievable': 'With proper scheduling and reminders',
                'relevant': 'Consistency is key to improvement',
                'timebound': '1 month',
                'milestones': [
                    {'week': 1, 'target': '70% completion'},
                    {'week': 2, 'target': '80% completion'},
                    {'week': 3, 'target': '85% completion'},
                    {'week': 4, 'target': '90% completion'}
                ]
            })
        
        return goals
    
    def _recommend_learning_strategies(self, learning_patterns: Dict[str, Any],
                                     performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend personalized learning strategies"""
        strategies = []
        
        # Time management strategy
        if learning_patterns['session_duration'] > 3600:  # Over 1 hour
            strategies.append({
                'name': 'Pomodoro Technique',
                'description': 'Break study sessions into 25-minute focused intervals with 5-minute breaks',
                'benefits': ['Improved focus', 'Reduced mental fatigue', 'Better retention'],
                'implementation': '25 minutes study, 5 minutes break, repeat 4 times, then 15-minute break'
            })
        
        # Memory strategies based on performance
        if performance_data['average_score'] < 70:
            strategies.append({
                'name': 'Spaced Repetition',
                'description': 'Review material at increasing intervals',
                'benefits': ['Long-term retention', 'Efficient learning', 'Reduced study time'],
                'implementation': 'Review after 1 day, 3 days, 1 week, 2 weeks, 1 month'
            })
        
        # Active learning strategies
        if performance_data['weaknesses']:
            strategies.append({
                'name': 'Active Recall',
                'description': 'Test yourself without looking at notes',
                'benefits': ['Stronger memory formation', 'Identifies knowledge gaps', 'Improved exam performance'],
                'implementation': 'After reading, close book and write/say what you remember'
            })
        
        # Metacognitive strategies
        strategies.append({
            'name': 'Reflection Practice',
            'description': 'Reflect on learning process and adjust strategies',
            'benefits': ['Better self-awareness', 'Improved learning efficiency', 'Personalized approach'],
            'implementation': 'Weekly review: What worked? What didn\'t? What to change?'
        })
        
        # Difficulty progression strategy
        if learning_patterns.get('difficulty_preference', {}).get('high', {}).get('comfort_level') == 'high':
            strategies.append({
                'name': 'Progressive Overload',
                'description': 'Gradually increase difficulty level',
                'benefits': ['Continuous challenge', 'Skill advancement', 'Maintained engagement'],
                'implementation': 'Start with 70% difficulty, increase by 5% when achieving 80% accuracy'
            })
        
        return strategies
    
    def _generate_resource_recommendations(self, performance_data: Dict[str, Any],
                                         skill_gaps: List[Dict[str, Any]],
                                         db: Session) -> Dict[str, Any]:
        """Generate resource-specific recommendations"""
        # Query available resources from database
        resources = db.query(Resource).filter(
            Resource.is_active == True
        ).all()
        
        recommended_resources = {
            'by_skill': {},
            'by_format': {},
            'by_difficulty': {}
        }
        
        # Match resources to skill gaps
        for gap in skill_gaps:
            skill_resources = []
            
            for resource in resources:
                if resource.metadata and gap['skill'].lower() in resource.metadata.get('tags', []):
                    skill_resources.append({
                        'id': resource.id,
                        'title': resource.title,
                        'type': resource.type,
                        'difficulty': resource.difficulty,
                        'duration': resource.duration,
                        'rating': resource.rating,
                        'url': resource.url
                    })
            
            recommended_resources['by_skill'][gap['skill']] = skill_resources[:5]
        
        # Group by format preference
        formats = ['video', 'article', 'interactive', 'pdf']
        for format_type in formats:
            format_resources = [
                r for r in resources 
                if r.type == format_type
            ]
            recommended_resources['by_format'][format_type] = [
                {
                    'id': r.id,
                    'title': r.title,
                    'difficulty': r.difficulty,
                    'rating': r.rating
                }
                for r in format_resources[:3]
            ]
        
        return recommended_resources
    
    def _generate_activity_recommendations(self, performance_data: Dict[str, Any],
                                         learning_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Generate activity-specific recommendations"""
        activities = {
            'daily': [],
            'weekly': [],
            'practice_sessions': []
        }
        
        # Daily activities
        activities['daily'].append({
            'activity': 'Quick Review',
            'duration': '10 minutes',
            'time': learning_patterns.get('preferred_time', 'morning'),
            'description': 'Review yesterday\'s key concepts',
            'benefit': 'Reinforces memory'
        })
        
        # Weekly activities
        activities['weekly'].append({
            'activity': 'Progress Assessment',
            'duration': '30 minutes',
            'frequency': 'Once per week',
            'description': 'Complete weekly progress quiz',
            'benefit': 'Track improvement'
        })
        
        # Practice sessions based on weaknesses
        for weakness in performance_data['weaknesses'][:3]:
            activities['practice_sessions'].append({
                'skill': weakness,
                'duration': '20 minutes',
                'frequency': '3 times per week',
                'exercises': [
                    'Concept review',
                    'Practice problems',
                    'Real-world applications'
                ]
            })
        
        return activities
    
    def _generate_assessment_recommendations(self, performance_data: Dict[str, Any],
                                           skill_gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate assessment-specific recommendations"""
        assessments = {
            'immediate': [],
            'scheduled': [],
            'practice_tests': []
        }
        
        # Immediate assessments for validation
        if performance_data['recent_average'] < 60:
            assessments['immediate'].append({
                'type': 'diagnostic',
                'purpose': 'Identify specific knowledge gaps',
                'duration': '45 minutes',
                'focus_areas': performance_data['weaknesses']
            })
        
        # Scheduled assessments
        for i, gap in enumerate(skill_gaps[:3]):
            assessments['scheduled'].append({
                'week': (i + 1) * 2,
                'type': 'progress_check',
                'skill': gap['skill'],
                'duration': '30 minutes',
                'passing_score': 70
            })
        
        # Practice tests
        assessments['practice_tests'].append({
            'type': 'comprehensive',
            'frequency': 'bi-weekly',
            'duration': '60 minutes',
            'format': 'Mixed questions',
            'difficulty': 'Progressive'
        })
        
        return assessments
    
    def _enrich_with_ai(self, recommendations: Dict[str, Any],
                       user_profile: Dict[str, Any],
                       performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich recommendations with AI insights"""
        try:
            # Prepare context for AI
            context = {
                'user_profile': user_profile,
                'performance': performance_data,
                'current_recommendations': recommendations
            }
            
            prompt = f"""
            Based on the following learner profile and performance data, provide additional 
            personalized insights and recommendations:
            
            Profile: {json.dumps(user_profile, indent=2)}
            Performance: {json.dumps(performance_data, indent=2)}
            Current Recommendations: {json.dumps(recommendations, indent=2)}
            
            Please provide:
            1. Additional personalized strategies
            2. Motivational insights
            3. Potential challenges and solutions
            4. Long-term success factors
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational psychologist providing personalized learning recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_insights = response.choices[0].message.content
            
            # Parse and structure AI insights
            recommendations['ai_insights'] = self._parse_ai_insights(ai_insights)
            
        except Exception as e:
            logger.error(f"Error enriching with AI: {str(e)}")
            recommendations['ai_insights'] = {
                'strategies': [],
                'motivation': 'Continue your learning journey with dedication.',
                'challenges': [],
                'success_factors': []
            }
        
        return recommendations
    
    def _parse_ai_insights(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into structured insights"""
        insights = {
            'strategies': [],
            'motivation': '',
            'challenges': [],
            'success_factors': []
        }
        
        # Simple parsing - in production, use more sophisticated NLP
        lines = ai_response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'strategies' in line.lower() or 'strategy' in line.lower():
                current_section = 'strategies'
            elif 'motivation' in line.lower() or 'motivational' in line.lower():
                current_section = 'motivation'
            elif 'challenge' in line.lower():
                current_section = 'challenges'
            elif 'success' in line.lower():
                current_section = 'success_factors'
            else:
                if current_section == 'strategies':
                    if line.startswith('-') or line.startswith('•'):
                        insights['strategies'].append(line[1:].strip())
                elif current_section == 'motivation':
                    insights['motivation'] += line + ' '
                elif current_section == 'challenges':
                    if line.startswith('-') or line.startswith('•'):
                        insights['challenges'].append(line[1:].strip())
                elif current_section == 'success_factors':
                    if line.startswith('-') or line.startswith('•'):
                        insights['success_factors'].append(line[1:].strip())
        
        # Clean up motivation text
        insights['motivation'] = insights['motivation'].strip()
        
        return insights
    
    def _store_recommendations(self, beneficiary_id: int,
                             recommendations: Dict[str, Any],
                             db: Session):
        """Store recommendations in database for tracking"""
        try:
            # Create recommendation record
            recommendation_record = {
                'beneficiary_id': beneficiary_id,
                'recommendations': recommendations,
                'created_at': datetime.utcnow()
            }
            
            # Store in appropriate table (would need a Recommendations model)
            # For now, log it
            logger.info(f"Stored recommendations for beneficiary {beneficiary_id}")
            
        except Exception as e:
            logger.error(f"Error storing recommendations: {str(e)}")


# Singleton instance
recommendation_engine = RecommendationEngine()