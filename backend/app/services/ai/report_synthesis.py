"""
AI-powered report synthesis service
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc, distinct
import openai
from app.models.beneficiary import Beneficiary
from app.models.assessment import Assessment, TestResult
from app.models.appointment import Appointment
from app.models.note import Note
from app.models.user import User
from app.core.config import settings
from app.core.cache import cache_service
from app.services.monitoring.error_tracking import error_tracker
import logging

logger = logging.getLogger(__name__)

class ReportSynthesisService:
    """AI-powered report synthesis service"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        
    def generate_comprehensive_report(self, beneficiary_id: int, db: Session,
                                    report_type: str = 'comprehensive',
                                    time_period: str = 'all_time') -> Dict[str, Any]:
        """Generate a comprehensive AI-powered report for a beneficiary"""
        try:
            # Check cache first
            cache_key = f"ai_report:{beneficiary_id}:{report_type}:{time_period}"
            cached_report = cache_service.get(cache_key)
            if cached_report:
                return cached_report
                
            # Get beneficiary information
            beneficiary = db.query(Beneficiary).filter_by(id=beneficiary_id).first()
            if not beneficiary:
                raise ValueError(f"Beneficiary {beneficiary_id} not found")
                
            # Gather all relevant data
            data = self._gather_beneficiary_data(beneficiary_id, db, time_period)
            
            # Generate report using AI
            report = self._synthesize_report(data, report_type)
            
            # Add metadata
            report['metadata'] = {
                'beneficiary_id': beneficiary_id,
                'beneficiary_name': f"{beneficiary.first_name} {beneficiary.last_name}",
                'report_type': report_type,
                'time_period': time_period,
                'generated_at': datetime.utcnow().isoformat(),
                'data_sources': list(data.keys())
            }
            
            # Cache the report
            cache_service.set(cache_key, report, expire=3600)  # Cache for 1 hour
            
            return report
            
        except Exception as e:
            error_tracker.capture_exception(e)
            logger.error(f"Error generating report: {str(e)}")
            raise
            
    def _gather_beneficiary_data(self, beneficiary_id: int, db: Session,
                               time_period: str) -> Dict[str, Any]:
        """Gather all relevant data for report generation"""
        # Calculate date filter
        date_filter = self._get_date_filter(time_period)
        
        data = {}
        
        # Get assessment data
        assessments = db.query(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id
        )
        if date_filter:
            assessments = assessments.filter(Assessment.created_at >= date_filter)
        data['assessments'] = [{
            'id': a.id,
            'type': a.assessment_type,
            'score': a.score,
            'status': a.status,
            'completed_at': a.completed_at.isoformat() if a.completed_at else None,
            'results': self._serialize_results(a.results)
        } for a in assessments.all()]
        
        # Get test results
        test_results = db.query(TestResult).join(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id
        )
        if date_filter:
            test_results = test_results.filter(TestResult.created_at >= date_filter)
        data['test_results'] = [{
            'question': tr.question.content if tr.question else None,
            'answer': tr.answer,
            'score': tr.score,
            'time_spent': tr.time_spent,
            'feedback': tr.feedback
        } for tr in test_results.all()]
        
        # Get appointments
        appointments = db.query(Appointment).filter(
            Appointment.beneficiary_id == beneficiary_id
        )
        if date_filter:
            appointments = appointments.filter(Appointment.scheduled_at >= date_filter)
        data['appointments'] = [{
            'type': a.appointment_type,
            'scheduled_at': a.scheduled_at.isoformat(),
            'duration': a.duration,
            'status': a.status,
            'notes': a.notes,
            'trainer': f"{a.trainer.first_name} {a.trainer.last_name}" if a.trainer else None
        } for a in appointments.all()]
        
        # Get notes
        notes = db.query(Note).filter(
            Note.beneficiary_id == beneficiary_id
        )
        if date_filter:
            notes = notes.filter(Note.created_at >= date_filter)
        data['notes'] = [{
            'content': n.content,
            'type': n.note_type,
            'created_at': n.created_at.isoformat(),
            'author': f"{n.author.first_name} {n.author.last_name}" if n.author else None,
            'tags': n.tags
        } for n in notes.all()]
        
        # Get progress metrics
        data['progress_metrics'] = self._calculate_progress_metrics(beneficiary_id, db, date_filter)
        
        # Get skill analysis
        data['skills'] = self._analyze_skills(beneficiary_id, db, date_filter)
        
        return data
        
    def _synthesize_report(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Synthesize report using AI"""
        # Prepare the prompt based on report type
        prompt = self._build_synthesis_prompt(data, report_type)
        
        # Generate report sections using AI
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational psychologist and report writer. 
                        Generate comprehensive, well-structured reports that provide actionable insights 
                        about beneficiary progress and development. Use clear, professional language 
                        and organize information logically."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            ai_report = json.loads(response['choices'][0]['message']['content'])
            
        except json.JSONDecodeError:
            # If JSON parsing fails, use the text response
            ai_report = {
                'summary': response['choices'][0]['message']['content'],
                'sections': {}
            }
        except Exception as e:
            logger.error(f"AI report generation failed: {str(e)}")
            # Fallback to template-based report
            ai_report = self._generate_template_report(data, report_type)
            
        # Enhance with data-driven insights
        report = self._enhance_report(ai_report, data)
        
        return report
        
    def _build_synthesis_prompt(self, data: Dict[str, Any], report_type: str) -> str:
        """Build the prompt for AI synthesis"""
        data_summary = {
            'assessment_count': len(data.get('assessments', [])),
            'average_score': self._calculate_average_score(data.get('assessments', [])),
            'appointment_count': len(data.get('appointments', [])),
            'note_count': len(data.get('notes', [])),
            'key_skills': data.get('skills', {}).get('top_skills', []),
            'progress_trend': data.get('progress_metrics', {}).get('trend', 'stable')
        }
        
        if report_type == 'comprehensive':
            return f"""
            Based on the following data, generate a comprehensive progress report in JSON format:
            
            Data Summary:
            - {data_summary['assessment_count']} assessments completed
            - Average score: {data_summary['average_score']:.2f}%
            - {data_summary['appointment_count']} appointments
            - {data_summary['note_count']} notes recorded
            - Top skills: {', '.join(data_summary['key_skills'])}
            - Progress trend: {data_summary['progress_trend']}
            
            Full Data:
            {json.dumps(data, indent=2)}
            
            Generate a JSON report with the following structure:
            {{
                "executive_summary": "Brief overview of the beneficiary's progress",
                "key_findings": ["Finding 1", "Finding 2", ...],
                "sections": {{
                    "academic_progress": {{
                        "overview": "...",
                        "strengths": ["..."],
                        "areas_for_improvement": ["..."],
                        "recommendations": ["..."]
                    }},
                    "skill_development": {{
                        "overview": "...",
                        "developed_skills": ["..."],
                        "emerging_skills": ["..."],
                        "skill_gaps": ["..."]
                    }},
                    "engagement_analysis": {{
                        "overview": "...",
                        "participation_level": "...",
                        "consistency": "...",
                        "motivation_indicators": ["..."]
                    }},
                    "behavioral_insights": {{
                        "overview": "...",
                        "positive_behaviors": ["..."],
                        "challenges": ["..."],
                        "support_strategies": ["..."]
                    }}
                }},
                "action_plan": {{
                    "immediate_actions": ["..."],
                    "short_term_goals": ["..."],
                    "long_term_objectives": ["..."]
                }},
                "recommendations": {{
                    "for_educators": ["..."],
                    "for_beneficiary": ["..."],
                    "for_support_team": ["..."]
                }}
            }}
            """
        elif report_type == 'progress':
            return f"""
            Generate a focused progress report based on this data:
            {json.dumps(data_summary, indent=2)}
            
            Focus on recent progress, achievements, and immediate next steps.
            Format as JSON with sections for: overview, achievements, challenges, next_steps.
            """
        elif report_type == 'skills':
            return f"""
            Generate a skills-focused report based on this data:
            {json.dumps(data.get('skills', {}), indent=2)}
            
            Analyze skill development, identify patterns, and recommend skill-building activities.
            Format as JSON with sections for: skill_overview, strengths, development_areas, recommendations.
            """
        else:
            return f"""
            Generate a {report_type} report based on this data:
            {json.dumps(data_summary, indent=2)}
            
            Format as JSON with appropriate sections for the report type.
            """
            
    def _enhance_report(self, ai_report: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance AI report with data-driven insights"""
        enhanced_report = ai_report.copy()
        
        # Add visualizations data
        enhanced_report['visualizations'] = {
            'progress_chart': self._prepare_progress_chart_data(data),
            'skill_radar': self._prepare_skill_radar_data(data),
            'engagement_timeline': self._prepare_engagement_timeline_data(data),
            'assessment_distribution': self._prepare_assessment_distribution_data(data)
        }
        
        # Add statistical insights
        enhanced_report['statistics'] = {
            'total_assessments': len(data.get('assessments', [])),
            'average_score': self._calculate_average_score(data.get('assessments', [])),
            'completion_rate': self._calculate_completion_rate(data.get('assessments', [])),
            'engagement_score': self._calculate_engagement_score(data),
            'skill_diversity': len(data.get('skills', {}).get('all_skills', [])),
            'progress_percentage': data.get('progress_metrics', {}).get('overall_progress', 0)
        }
        
        # Add trend analysis
        enhanced_report['trends'] = {
            'score_trend': self._analyze_score_trend(data.get('assessments', [])),
            'engagement_trend': self._analyze_engagement_trend(data),
            'skill_growth_trend': self._analyze_skill_growth_trend(data)
        }
        
        return enhanced_report
        
    def _calculate_average_score(self, assessments: List[Dict]) -> float:
        """Calculate average assessment score"""
        scores = [a['score'] for a in assessments if a.get('score') is not None]
        return sum(scores) / len(scores) if scores else 0.0
        
    def _calculate_completion_rate(self, assessments: List[Dict]) -> float:
        """Calculate assessment completion rate"""
        total = len(assessments)
        completed = len([a for a in assessments if a.get('status') == 'completed'])
        return (completed / total * 100) if total > 0 else 0.0
        
    def _calculate_engagement_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall engagement score"""
        factors = {
            'assessments': len(data.get('assessments', [])) * 2,
            'appointments': len(data.get('appointments', [])) * 3,
            'notes': len(data.get('notes', [])) * 1,
            'consistency': self._calculate_consistency_score(data) * 5
        }
        
        total_weight = sum([2, 3, 1, 5])
        weighted_sum = sum(factors.values())
        
        # Normalize to 0-100 scale
        max_possible = total_weight * 10  # Assuming 10 is max for each factor
        return min((weighted_sum / max_possible * 100), 100)
        
    def _calculate_consistency_score(self, data: Dict[str, Any]) -> float:
        """Calculate consistency score based on activity regularity"""
        activities = []
        
        # Collect all timestamped activities
        for assessment in data.get('assessments', []):
            if assessment.get('completed_at'):
                activities.append(datetime.fromisoformat(assessment['completed_at']))
                
        for appointment in data.get('appointments', []):
            if appointment.get('scheduled_at'):
                activities.append(datetime.fromisoformat(appointment['scheduled_at']))
                
        for note in data.get('notes', []):
            if note.get('created_at'):
                activities.append(datetime.fromisoformat(note['created_at']))
                
        if len(activities) < 2:
            return 0.0
            
        # Sort activities by date
        activities.sort()
        
        # Calculate gaps between activities
        gaps = []
        for i in range(1, len(activities)):
            gap = (activities[i] - activities[i-1]).days
            gaps.append(gap)
            
        if not gaps:
            return 0.0
            
        # Lower variance in gaps = higher consistency
        avg_gap = sum(gaps) / len(gaps)
        variance = sum((gap - avg_gap) ** 2 for gap in gaps) / len(gaps)
        
        # Convert to 0-10 scale (lower variance = higher score)
        consistency = max(0, 10 - (variance ** 0.5) / 3)
        
        return consistency
        
    def _prepare_progress_chart_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for progress visualization"""
        assessments = sorted(
            data.get('assessments', []),
            key=lambda x: x.get('completed_at', '')
        )
        
        return {
            'labels': [a.get('completed_at', '')[:10] for a in assessments],
            'datasets': [{
                'label': 'Assessment Scores',
                'data': [a.get('score', 0) for a in assessments],
                'borderColor': '#3B82F6',
                'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                'tension': 0.4
            }]
        }
        
    def _prepare_skill_radar_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for skill radar chart"""
        skills = data.get('skills', {}).get('skill_scores', {})
        
        return {
            'labels': list(skills.keys()),
            'datasets': [{
                'label': 'Skill Proficiency',
                'data': list(skills.values()),
                'backgroundColor': 'rgba(99, 102, 241, 0.2)',
                'borderColor': '#6366F1',
                'pointBackgroundColor': '#6366F1',
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': '#6366F1'
            }]
        }
        
    def _prepare_engagement_timeline_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for engagement timeline"""
        activities = []
        
        for assessment in data.get('assessments', []):
            if assessment.get('completed_at'):
                activities.append({
                    'date': assessment['completed_at'],
                    'type': 'assessment',
                    'score': assessment.get('score', 0)
                })
                
        for appointment in data.get('appointments', []):
            if appointment.get('scheduled_at'):
                activities.append({
                    'date': appointment['scheduled_at'],
                    'type': 'appointment',
                    'status': appointment.get('status', 'scheduled')
                })
                
        for note in data.get('notes', []):
            if note.get('created_at'):
                activities.append({
                    'date': note['created_at'],
                    'type': 'note',
                    'category': note.get('type', 'general')
                })
                
        # Sort by date
        activities.sort(key=lambda x: x['date'])
        
        return activities
        
    def _prepare_assessment_distribution_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for assessment distribution chart"""
        assessments = data.get('assessments', [])
        type_counts = {}
        
        for assessment in assessments:
            assessment_type = assessment.get('type', 'unknown')
            type_counts[assessment_type] = type_counts.get(assessment_type, 0) + 1
            
        return {
            'labels': list(type_counts.keys()),
            'datasets': [{
                'data': list(type_counts.values()),
                'backgroundColor': [
                    '#3B82F6',
                    '#10B981',
                    '#F59E0B',
                    '#EF4444',
                    '#8B5CF6'
                ][:len(type_counts)]
            }]
        }
        
    def _analyze_score_trend(self, assessments: List[Dict]) -> str:
        """Analyze trend in assessment scores"""
        if len(assessments) < 2:
            return 'insufficient_data'
            
        sorted_assessments = sorted(
            assessments,
            key=lambda x: x.get('completed_at', '')
        )
        
        recent_scores = [a.get('score', 0) for a in sorted_assessments[-5:]]
        
        if len(recent_scores) < 2:
            return 'insufficient_data'
            
        # Simple linear trend analysis
        trend_sum = 0
        for i in range(1, len(recent_scores)):
            trend_sum += recent_scores[i] - recent_scores[i-1]
            
        if trend_sum > 5:
            return 'improving'
        elif trend_sum < -5:
            return 'declining'
        else:
            return 'stable'
            
    def _analyze_engagement_trend(self, data: Dict[str, Any]) -> str:
        """Analyze engagement trend"""
        # Count activities per month
        monthly_activities = {}
        
        for assessment in data.get('assessments', []):
            if assessment.get('completed_at'):
                month = assessment['completed_at'][:7]
                monthly_activities[month] = monthly_activities.get(month, 0) + 1
                
        for appointment in data.get('appointments', []):
            if appointment.get('scheduled_at'):
                month = appointment['scheduled_at'][:7]
                monthly_activities[month] = monthly_activities.get(month, 0) + 1
                
        if len(monthly_activities) < 2:
            return 'insufficient_data'
            
        # Get recent months
        months = sorted(monthly_activities.keys())[-3:]
        recent_counts = [monthly_activities[m] for m in months]
        
        # Simple trend analysis
        if len(recent_counts) >= 2:
            if recent_counts[-1] > recent_counts[-2]:
                return 'increasing'
            elif recent_counts[-1] < recent_counts[-2]:
                return 'decreasing'
                
        return 'stable'
        
    def _analyze_skill_growth_trend(self, data: Dict[str, Any]) -> str:
        """Analyze skill development trend"""
        skills_data = data.get('skills', {})
        
        if not skills_data:
            return 'insufficient_data'
            
        skill_count = len(skills_data.get('all_skills', []))
        proficiency_avg = sum(skills_data.get('skill_scores', {}).values()) / max(skill_count, 1)
        
        if proficiency_avg > 0.7:
            return 'strong_growth'
        elif proficiency_avg > 0.5:
            return 'moderate_growth'
        elif proficiency_avg > 0.3:
            return 'emerging_growth'
        else:
            return 'initial_stage'
            
    def _calculate_progress_metrics(self, beneficiary_id: int, db: Session,
                                  date_filter: Optional[datetime]) -> Dict[str, Any]:
        """Calculate progress metrics"""
        query = db.query(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id
        )
        
        if date_filter:
            query = query.filter(Assessment.created_at >= date_filter)
            
        assessments = query.all()
        
        if not assessments:
            return {
                'overall_progress': 0,
                'trend': 'no_data',
                'milestones_achieved': 0
            }
            
        completed_count = len([a for a in assessments if a.status == 'completed'])
        total_count = len(assessments)
        
        return {
            'overall_progress': (completed_count / total_count * 100) if total_count > 0 else 0,
            'trend': self._analyze_score_trend([{
                'score': a.score,
                'completed_at': a.completed_at.isoformat() if a.completed_at else None
            } for a in assessments]),
            'milestones_achieved': len([a for a in assessments if a.score and a.score >= 80])
        }
        
    def _analyze_skills(self, beneficiary_id: int, db: Session,
                       date_filter: Optional[datetime]) -> Dict[str, Any]:
        """Analyze skills from assessments and notes"""
        # This would typically involve more sophisticated skill extraction
        # For now, we'll use a simplified version
        
        skills = {}
        skill_scores = {}
        
        # Extract skills from test results
        query = db.query(TestResult).join(Assessment).filter(
            Assessment.beneficiary_id == beneficiary_id
        )
        
        if date_filter:
            query = query.filter(TestResult.created_at >= date_filter)
            
        test_results = query.all()
        
        for result in test_results:
            if result.question and result.question.category:
                skill = result.question.category
                if skill not in skills:
                    skills[skill] = []
                skills[skill].append(result.score or 0)
                
        # Calculate average scores per skill
        for skill, scores in skills.items():
            skill_scores[skill] = sum(scores) / len(scores) if scores else 0
            
        # Get top skills
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'all_skills': list(skills.keys()),
            'skill_scores': skill_scores,
            'top_skills': [skill[0] for skill in top_skills],
            'skill_count': len(skills)
        }
        
    def _get_date_filter(self, time_period: str) -> Optional[datetime]:
        """Get date filter based on time period"""
        if time_period == 'all_time':
            return None
            
        now = datetime.utcnow()
        
        if time_period == 'last_week':
            return now - timedelta(days=7)
        elif time_period == 'last_month':
            return now - timedelta(days=30)
        elif time_period == 'last_quarter':
            return now - timedelta(days=90)
        elif time_period == 'last_year':
            return now - timedelta(days=365)
        else:
            return None
            
    def _serialize_results(self, results: Any) -> Any:
        """Safely serialize assessment results"""
        if results is None:
            return None
        if isinstance(results, (dict, list)):
            return results
        if isinstance(results, str):
            try:
                return json.loads(results)
            except:
                return results
        return str(results)
        
    def _generate_template_report(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate a template-based report as fallback"""
        return {
            'executive_summary': f"Progress report for beneficiary based on {len(data.get('assessments', []))} assessments",
            'key_findings': [
                f"Completed {len(data.get('assessments', []))} assessments",
                f"Average score: {self._calculate_average_score(data.get('assessments', [])):.1f}%",
                f"Attended {len(data.get('appointments', []))} appointments",
                f"Progress trend: {data.get('progress_metrics', {}).get('trend', 'stable')}"
            ],
            'sections': {
                'overview': {
                    'summary': 'Based on available data',
                    'details': data
                }
            },
            'recommendations': [
                'Continue regular assessments',
                'Focus on identified skill gaps',
                'Maintain consistent engagement'
            ]
        }

# Initialize the service
report_synthesis_service = ReportSynthesisService()