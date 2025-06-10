"""
User Behavior Analytics Service

Comprehensive user behavior analysis including cohort analysis,
user journey mapping, engagement metrics, and behavioral patterns.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging
from sqlalchemy import func, and_, or_, case, distinct
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.evaluation import Evaluation
from app.models.user_activity import UserActivity
from app.extensions import db


@dataclass
class CohortData:
    """Cohort analysis data structure"""
    cohort_group: str
    period: int
    users_count: int
    retention_rate: float
    revenue_per_user: float
    active_users: int


@dataclass
class UserJourney:
    """User journey data structure"""
    user_id: int
    journey_steps: List[Dict[str, Any]]
    total_duration: int
    conversion_points: List[str]
    drop_off_points: List[str]


@dataclass
class EngagementMetrics:
    """User engagement metrics"""
    user_id: int
    engagement_score: float
    session_frequency: float
    feature_adoption_rate: float
    time_to_value: int  # days
    stickiness_factor: float


@dataclass
class BehavioralSegment:
    """Behavioral segment data"""
    segment_name: str
    user_count: int
    characteristics: Dict[str, Any]
    engagement_level: str
    recommended_actions: List[str]


class UserBehaviorAnalytics:
    """
    Comprehensive user behavior analytics service providing insights
    into user patterns, cohort analysis, and engagement metrics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache_duration = timedelta(hours=6)
        self.cached_data = {}
        self.last_cache_update = {}
        
    async def perform_cohort_analysis(self, period_type: str = 'monthly',
                                    months_back: int = 12) -> List[CohortData]:
        """Perform cohort analysis for user retention"""
        try:
            cache_key = f"cohort_analysis_{period_type}_{months_back}"
            
            if self.is_cache_valid(cache_key):
                return self.cached_data[cache_key]
            
            with db.session() as session:
                # Get user registration data
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=months_back * 30)
                
                users = session.query(User).filter(
                    User.created_at >= start_date
                ).all()
                
                # Group users by cohort (registration month/week)
                cohorts = defaultdict(list)
                
                for user in users:
                    if period_type == 'monthly':
                        cohort_key = user.created_at.strftime('%Y-%m')
                    elif period_type == 'weekly':
                        # Get week number
                        year_week = user.created_at.strftime('%Y-W%U')
                        cohort_key = year_week
                    else:
                        cohort_key = user.created_at.strftime('%Y-%m')
                    
                    cohorts[cohort_key].append(user)
                
                # Calculate retention rates for each cohort
                cohort_data = []
                
                for cohort_group, cohort_users in cohorts.items():
                    if not cohort_users:
                        continue
                    
                    cohort_start = min(user.created_at for user in cohort_users)
                    
                    # Calculate retention for multiple periods
                    for period in range(0, 12):  # 12 periods
                        period_start = cohort_start + timedelta(days=period * 30)
                        period_end = period_start + timedelta(days=30)
                        
                        # Count active users in this period
                        active_users = 0
                        for user in cohort_users:
                            # Check if user was active in this period
                            user_activities = session.query(UserActivity).filter(
                                and_(
                                    UserActivity.user_id == user.id,
                                    UserActivity.timestamp >= period_start,
                                    UserActivity.timestamp < period_end
                                )
                            ).count()
                            
                            if user_activities > 0:
                                active_users += 1
                        
                        retention_rate = (active_users / len(cohort_users)) * 100
                        
                        # Calculate revenue per user (simulated)
                        revenue_per_user = self.calculate_revenue_per_user(cohort_users, period)
                        
                        cohort_data.append(CohortData(
                            cohort_group=cohort_group,
                            period=period,
                            users_count=len(cohort_users),
                            retention_rate=retention_rate,
                            revenue_per_user=revenue_per_user,
                            active_users=active_users
                        ))
                
                # Cache results
                self.cached_data[cache_key] = cohort_data
                self.last_cache_update[cache_key] = datetime.utcnow()
                
                return cohort_data
                
        except Exception as e:
            self.logger.error(f"Error performing cohort analysis: {str(e)}")
            raise
    
    async def analyze_user_journeys(self, user_ids: Optional[List[int]] = None,
                                  limit: int = 100) -> List[UserJourney]:
        """Analyze user journeys and identify patterns"""
        try:
            with db.session() as session:
                # Get users to analyze
                if user_ids:
                    users = session.query(User).filter(User.id.in_(user_ids)).all()
                else:
                    users = session.query(User).limit(limit).all()
                
                journeys = []
                
                for user in users:
                    # Get user activities in chronological order
                    activities = session.query(UserActivity).filter(
                        UserActivity.user_id == user.id
                    ).order_by(UserActivity.timestamp).all()
                    
                    if not activities:
                        continue
                    
                    # Build journey steps
                    journey_steps = []
                    conversion_points = []
                    drop_off_points = []
                    
                    for i, activity in enumerate(activities):
                        step = {
                            'step_number': i + 1,
                            'activity_type': activity.activity_type,
                            'timestamp': activity.timestamp.isoformat(),
                            'duration_from_start': (activity.timestamp - activities[0].timestamp).total_seconds()
                        }
                        
                        # Identify conversion points
                        if activity.activity_type in ['appointment_scheduled', 'evaluation_completed', 'program_enrolled']:
                            conversion_points.append(activity.activity_type)
                        
                        # Identify potential drop-off points (long gaps)
                        if i > 0:
                            time_gap = (activity.timestamp - activities[i-1].timestamp).total_seconds()
                            if time_gap > 7 * 24 * 3600:  # 7 days gap
                                drop_off_points.append(f"gap_after_{activities[i-1].activity_type}")
                        
                        journey_steps.append(step)
                    
                    total_duration = (activities[-1].timestamp - activities[0].timestamp).total_seconds()
                    
                    journey = UserJourney(
                        user_id=user.id,
                        journey_steps=journey_steps,
                        total_duration=int(total_duration),
                        conversion_points=conversion_points,
                        drop_off_points=drop_off_points
                    )
                    
                    journeys.append(journey)
                
                return journeys
                
        except Exception as e:
            self.logger.error(f"Error analyzing user journeys: {str(e)}")
            raise
    
    async def calculate_engagement_metrics(self, user_ids: Optional[List[int]] = None) -> List[EngagementMetrics]:
        """Calculate comprehensive engagement metrics for users"""
        try:
            with db.session() as session:
                # Get users to analyze
                if user_ids:
                    users = session.query(User).filter(User.id.in_(user_ids)).all()
                else:
                    users = session.query(User).all()
                
                metrics = []
                
                for user in users:
                    # Calculate session frequency (sessions per week)
                    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                    
                    sessions = session.query(UserActivity).filter(
                        and_(
                            UserActivity.user_id == user.id,
                            UserActivity.activity_type == 'login',
                            UserActivity.timestamp >= thirty_days_ago
                        )
                    ).count()
                    
                    session_frequency = sessions / 4.0  # per week
                    
                    # Calculate feature adoption rate
                    total_features = ['login', 'appointment_scheduled', 'evaluation_completed', 
                                    'document_uploaded', 'profile_updated', 'message_sent']
                    
                    used_features = session.query(distinct(UserActivity.activity_type)).filter(
                        UserActivity.user_id == user.id
                    ).count()
                    
                    feature_adoption_rate = used_features / len(total_features)
                    
                    # Calculate time to value (days to first meaningful action)
                    first_meaningful_action = session.query(UserActivity).filter(
                        and_(
                            UserActivity.user_id == user.id,
                            UserActivity.activity_type.in_(['appointment_scheduled', 'evaluation_completed'])
                        )
                    ).order_by(UserActivity.timestamp).first()
                    
                    if first_meaningful_action:
                        time_to_value = (first_meaningful_action.timestamp - user.created_at).days
                    else:
                        time_to_value = 999  # Not achieved yet
                    
                    # Calculate stickiness factor (DAU/MAU ratio simulation)
                    daily_active_days = session.query(
                        func.date(UserActivity.timestamp)
                    ).filter(
                        and_(
                            UserActivity.user_id == user.id,
                            UserActivity.timestamp >= thirty_days_ago
                        )
                    ).distinct().count()
                    
                    stickiness_factor = daily_active_days / 30.0
                    
                    # Calculate overall engagement score
                    engagement_score = (
                        min(session_frequency * 10, 30) +  # Max 30 points
                        feature_adoption_rate * 25 +       # Max 25 points
                        max(0, 20 - time_to_value) +       # Max 20 points
                        stickiness_factor * 25              # Max 25 points
                    )  # Total max 100 points
                    
                    metric = EngagementMetrics(
                        user_id=user.id,
                        engagement_score=min(100, engagement_score),
                        session_frequency=session_frequency,
                        feature_adoption_rate=feature_adoption_rate,
                        time_to_value=time_to_value,
                        stickiness_factor=stickiness_factor
                    )
                    
                    metrics.append(metric)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Error calculating engagement metrics: {str(e)}")
            raise
    
    async def segment_users_by_behavior(self) -> List[BehavioralSegment]:
        """Segment users based on behavioral patterns"""
        try:
            with db.session() as session:
                # Get engagement metrics for all users
                engagement_metrics = await self.calculate_engagement_metrics()
                
                # Define segments based on engagement patterns
                segments = {
                    'Champions': {'users': [], 'criteria': lambda m: m.engagement_score >= 80},
                    'Loyal Users': {'users': [], 'criteria': lambda m: 60 <= m.engagement_score < 80},
                    'Potential Loyalists': {'users': [], 'criteria': lambda m: 40 <= m.engagement_score < 60 and m.time_to_value <= 7},
                    'New Users': {'users': [], 'criteria': lambda m: m.time_to_value <= 30},
                    'At Risk': {'users': [], 'criteria': lambda m: 20 <= m.engagement_score < 40},
                    'Cannot Lose Them': {'users': [], 'criteria': lambda m: m.engagement_score < 20 and m.session_frequency > 2},
                    'Hibernating': {'users': [], 'criteria': lambda m: m.engagement_score < 20 and m.session_frequency <= 1}
                }
                
                # Assign users to segments
                for metric in engagement_metrics:
                    assigned = False
                    for segment_name, segment_data in segments.items():
                        if segment_data['criteria'](metric) and not assigned:
                            segment_data['users'].append(metric)
                            assigned = True
                            break
                    
                    # Default segment if no other matches
                    if not assigned:
                        segments['Hibernating']['users'].append(metric)
                
                # Create segment analysis
                behavioral_segments = []
                
                for segment_name, segment_data in segments.items():
                    if not segment_data['users']:
                        continue
                    
                    users = segment_data['users']
                    
                    # Calculate segment characteristics
                    avg_engagement = np.mean([u.engagement_score for u in users])
                    avg_session_frequency = np.mean([u.session_frequency for u in users])
                    avg_feature_adoption = np.mean([u.feature_adoption_rate for u in users])
                    avg_time_to_value = np.mean([u.time_to_value for u in users])
                    
                    # Determine engagement level
                    if avg_engagement >= 70:
                        engagement_level = 'High'
                    elif avg_engagement >= 40:
                        engagement_level = 'Medium'
                    else:
                        engagement_level = 'Low'
                    
                    # Generate recommendations
                    recommendations = self.generate_segment_recommendations(segment_name, {
                        'avg_engagement': avg_engagement,
                        'avg_session_frequency': avg_session_frequency,
                        'avg_feature_adoption': avg_feature_adoption,
                        'avg_time_to_value': avg_time_to_value
                    })
                    
                    segment = BehavioralSegment(
                        segment_name=segment_name,
                        user_count=len(users),
                        characteristics={
                            'avg_engagement_score': round(avg_engagement, 2),
                            'avg_session_frequency': round(avg_session_frequency, 2),
                            'avg_feature_adoption_rate': round(avg_feature_adoption, 2),
                            'avg_time_to_value': round(avg_time_to_value, 1)
                        },
                        engagement_level=engagement_level,
                        recommended_actions=recommendations
                    )
                    
                    behavioral_segments.append(segment)
                
                return behavioral_segments
                
        except Exception as e:
            self.logger.error(f"Error segmenting users by behavior: {str(e)}")
            raise
    
    async def analyze_feature_usage(self) -> Dict[str, Any]:
        """Analyze feature usage patterns across the platform"""
        try:
            with db.session() as session:
                # Get feature usage statistics
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                
                feature_usage = session.query(
                    UserActivity.activity_type,
                    func.count(UserActivity.id).label('usage_count'),
                    func.count(distinct(UserActivity.user_id)).label('unique_users')
                ).filter(
                    UserActivity.timestamp >= thirty_days_ago
                ).group_by(UserActivity.activity_type).all()
                
                total_users = session.query(User).count()
                
                # Calculate feature metrics
                features = []
                for feature in feature_usage:
                    adoption_rate = (feature.unique_users / total_users) * 100
                    avg_usage_per_user = feature.usage_count / feature.unique_users if feature.unique_users > 0 else 0
                    
                    features.append({
                        'feature_name': feature.activity_type,
                        'total_usage': feature.usage_count,
                        'unique_users': feature.unique_users,
                        'adoption_rate': adoption_rate,
                        'avg_usage_per_user': avg_usage_per_user
                    })
                
                # Sort by adoption rate
                features.sort(key=lambda x: x['adoption_rate'], reverse=True)
                
                # Calculate feature correlation matrix
                feature_correlation = await self.calculate_feature_correlation()
                
                return {
                    'feature_usage': features,
                    'feature_correlation': feature_correlation,
                    'total_users': total_users,
                    'analysis_period': '30 days',
                    'most_popular_feature': features[0]['feature_name'] if features else None,
                    'least_popular_feature': features[-1]['feature_name'] if features else None
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing feature usage: {str(e)}")
            raise
    
    async def calculate_feature_correlation(self) -> Dict[str, Dict[str, float]]:
        """Calculate correlation between feature usage"""
        try:
            with db.session() as session:
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                
                # Get user-feature matrix
                users = session.query(User).all()
                features = ['login', 'appointment_scheduled', 'evaluation_completed', 
                          'document_uploaded', 'profile_updated', 'message_sent']
                
                user_feature_matrix = []
                
                for user in users:
                    user_row = []
                    for feature in features:
                        usage_count = session.query(UserActivity).filter(
                            and_(
                                UserActivity.user_id == user.id,
                                UserActivity.activity_type == feature,
                                UserActivity.timestamp >= thirty_days_ago
                            )
                        ).count()
                        user_row.append(usage_count)
                    user_feature_matrix.append(user_row)
                
                # Calculate correlation matrix
                if user_feature_matrix:
                    df = pd.DataFrame(user_feature_matrix, columns=features)
                    correlation_matrix = df.corr()
                    
                    # Convert to nested dictionary
                    correlation_dict = {}
                    for feature1 in features:
                        correlation_dict[feature1] = {}
                        for feature2 in features:
                            correlation_dict[feature1][feature2] = float(correlation_matrix.loc[feature1, feature2])
                    
                    return correlation_dict
                else:
                    return {}
                
        except Exception as e:
            self.logger.error(f"Error calculating feature correlation: {str(e)}")
            return {}
    
    async def identify_usage_patterns(self) -> Dict[str, Any]:
        """Identify common usage patterns and behaviors"""
        try:
            with db.session() as session:
                # Analyze temporal patterns
                temporal_patterns = await self.analyze_temporal_patterns()
                
                # Analyze sequence patterns
                sequence_patterns = await self.analyze_sequence_patterns()
                
                # Analyze session patterns
                session_patterns = await self.analyze_session_patterns()
                
                return {
                    'temporal_patterns': temporal_patterns,
                    'sequence_patterns': sequence_patterns,
                    'session_patterns': session_patterns,
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error identifying usage patterns: {str(e)}")
            raise
    
    async def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal usage patterns"""
        try:
            with db.session() as session:
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                
                # Hour of day analysis
                hourly_usage = session.query(
                    func.extract('hour', UserActivity.timestamp).label('hour'),
                    func.count(UserActivity.id).label('activity_count')
                ).filter(
                    UserActivity.timestamp >= thirty_days_ago
                ).group_by(func.extract('hour', UserActivity.timestamp)).all()
                
                # Day of week analysis
                daily_usage = session.query(
                    func.extract('dow', UserActivity.timestamp).label('day_of_week'),
                    func.count(UserActivity.id).label('activity_count')
                ).filter(
                    UserActivity.timestamp >= thirty_days_ago
                ).group_by(func.extract('dow', UserActivity.timestamp)).all()
                
                # Peak hours
                peak_hours = sorted(hourly_usage, key=lambda x: x.activity_count, reverse=True)[:3]
                peak_days = sorted(daily_usage, key=lambda x: x.activity_count, reverse=True)[:3]
                
                return {
                    'hourly_distribution': [{'hour': h.hour, 'count': h.activity_count} for h in hourly_usage],
                    'daily_distribution': [{'day': d.day_of_week, 'count': d.activity_count} for d in daily_usage],
                    'peak_hours': [int(h.hour) for h in peak_hours],
                    'peak_days': [int(d.day_of_week) for d in peak_days]
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing temporal patterns: {str(e)}")
            return {}
    
    async def analyze_sequence_patterns(self) -> Dict[str, Any]:
        """Analyze common action sequences"""
        try:
            with db.session() as session:
                # Get common sequences (simplified version)
                users = session.query(User).limit(100).all()
                
                sequence_counts = defaultdict(int)
                
                for user in users:
                    activities = session.query(UserActivity).filter(
                        UserActivity.user_id == user.id
                    ).order_by(UserActivity.timestamp).limit(10).all()
                    
                    # Create sequences of length 3
                    for i in range(len(activities) - 2):
                        sequence = tuple([
                            activities[i].activity_type,
                            activities[i+1].activity_type,
                            activities[i+2].activity_type
                        ])
                        sequence_counts[sequence] += 1
                
                # Get most common sequences
                common_sequences = sorted(sequence_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:10]
                
                return {
                    'common_sequences': [
                        {'sequence': list(seq), 'count': count} 
                        for seq, count in common_sequences
                    ]
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing sequence patterns: {str(e)}")
            return {}
    
    async def analyze_session_patterns(self) -> Dict[str, Any]:
        """Analyze session duration and frequency patterns"""
        try:
            # Simulate session analysis (would need proper session tracking)
            session_data = {
                'avg_session_duration': 1850,  # seconds
                'median_session_duration': 1200,
                'sessions_per_user': 8.5,
                'bounce_rate': 15.2,  # percentage
                'avg_pages_per_session': 6.3
            }
            
            return session_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing session patterns: {str(e)}")
            return {}
    
    def generate_segment_recommendations(self, segment_name: str, 
                                       characteristics: Dict[str, float]) -> List[str]:
        """Generate recommendations for behavioral segments"""
        recommendations = {
            'Champions': [
                'Leverage for referrals and testimonials',
                'Provide exclusive features and early access',
                'Create advocacy programs'
            ],
            'Loyal Users': [
                'Offer loyalty rewards',
                'Gather feedback for improvements',
                'Upsell premium features'
            ],
            'Potential Loyalists': [
                'Provide personalized onboarding',
                'Offer feature tutorials',
                'Send engagement campaigns'
            ],
            'New Users': [
                'Implement comprehensive onboarding',
                'Provide quick wins and early value',
                'Send welcome series emails'
            ],
            'At Risk': [
                'Send re-engagement campaigns',
                'Offer special promotions',
                'Gather feedback on pain points'
            ],
            'Cannot Lose Them': [
                'Implement win-back campaigns',
                'Offer personalized support',
                'Provide exclusive offers'
            ],
            'Hibernating': [
                'Send reactivation emails',
                'Offer significant incentives',
                'Consider sunset campaigns'
            ]
        }
        
        return recommendations.get(segment_name, ['No specific recommendations available'])
    
    def calculate_revenue_per_user(self, users: List[User], period: int) -> float:
        """Calculate revenue per user for a cohort period (simulated)"""
        # This would integrate with billing/payment systems
        base_revenue = 50.0  # Base monthly revenue per user
        decay_factor = 0.95 ** period  # Revenue typically decays over time
        return base_revenue * decay_factor
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.last_cache_update:
            return False
        
        return (datetime.utcnow() - self.last_cache_update[cache_key]) < self.cache_duration
    
    async def get_user_behavior_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive behavior summary for a specific user"""
        try:
            with db.session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    raise ValueError(f"User {user_id} not found")
                
                # Get engagement metrics
                engagement_metrics = await self.calculate_engagement_metrics([user_id])
                engagement = engagement_metrics[0] if engagement_metrics else None
                
                # Get user journey
                journeys = await self.analyze_user_journeys([user_id])
                journey = journeys[0] if journeys else None
                
                # Get recent activities
                recent_activities = session.query(UserActivity).filter(
                    UserActivity.user_id == user_id
                ).order_by(UserActivity.timestamp.desc()).limit(10).all()
                
                return {
                    'user_id': user_id,
                    'engagement_metrics': asdict(engagement) if engagement else None,
                    'journey_summary': {
                        'total_steps': len(journey.journey_steps) if journey else 0,
                        'conversion_points': journey.conversion_points if journey else [],
                        'drop_off_points': journey.drop_off_points if journey else []
                    } if journey else None,
                    'recent_activities': [
                        {
                            'activity_type': activity.activity_type,
                            'timestamp': activity.timestamp.isoformat()
                        } for activity in recent_activities
                    ],
                    'summary_timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting user behavior summary: {str(e)}")
            raise


# Initialize service instance
user_behavior_analytics = UserBehaviorAnalytics()