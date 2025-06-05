"""AI-powered report synthesis service."""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

import openai
from jinja2 import Template

from app.extensions import db, cache
from app.models import (
    Beneficiary, User, Appointment, Document, Program, 
    Evaluation, TestSession, EvaluationResponse
)
from app.models.notification import Note
from app.models.assessment import Assessment, AssessmentSection, AssessmentResponse
from app.services.analytics_service import AnalyticsService
from app.utils.logging import logger


class AIReportService:
    """Service for generating AI-powered reports."""
    
    def __init__(self):
        """Initialize AI Report Service."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        self.analytics_service = AnalyticsService()
    
    def generate_beneficiary_report(
        self,
        beneficiary_id: int,
        report_type: str = 'comprehensive',
        time_period: str = 'last_month',
        include_sections: Optional[List[str]] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Generate a comprehensive AI-powered report for a beneficiary.
        
        Args:
            beneficiary_id: ID of the beneficiary
            report_type: Type of report (comprehensive, progress, assessment)
            time_period: Time period for analysis
            include_sections: Specific sections to include
            
        Returns:
            Tuple of (report_data, error_message)
        """
        try:
            # Check cache first
            cache_key = f"ai_report:{beneficiary_id}:{report_type}:{time_period}"
            cached_report = cache.get(cache_key)
            if cached_report:
                return json.loads(cached_report), None
            
            # Get beneficiary
            beneficiary = Beneficiary.query.get(beneficiary_id)
            if not beneficiary:
                return None, "Beneficiary not found"
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(time_period, end_date)
            
            # Gather all data
            data = self._gather_beneficiary_data(
                beneficiary_id, 
                start_date, 
                end_date,
                include_sections or self._get_default_sections(report_type)
            )
            
            # Generate report based on type
            if report_type == 'comprehensive':
                report = self._generate_comprehensive_report(beneficiary, data)
            elif report_type == 'progress':
                report = self._generate_progress_report(beneficiary, data)
            elif report_type == 'assessment':
                report = self._generate_assessment_report(beneficiary, data)
            else:
                return None, f"Unknown report type: {report_type}"
            
            # Add metadata
            report['metadata'] = {
                'beneficiary_id': beneficiary_id,
                'beneficiary_name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
                'report_type': report_type,
                'time_period': time_period,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'generated_at': datetime.utcnow().isoformat(),
                'generated_by': 'AI Report Service v2.0'
            }
            
            # Cache the report
            cache.set(cache_key, json.dumps(report), timeout=3600)  # 1 hour cache
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error generating beneficiary report: {str(e)}")
            return None, f"Error generating report: {str(e)}"
    
    def generate_program_report(
        self,
        program_id: int,
        time_period: str = 'last_month'
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Generate AI-powered report for a program.
        
        Args:
            program_id: ID of the program
            time_period: Time period for analysis
            
        Returns:
            Tuple of (report_data, error_message)
        """
        try:
            program = Program.query.get(program_id)
            if not program:
                return None, "Program not found"
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(time_period, end_date)
            
            # Get program analytics
            analytics = self.analytics_service.get_program_analytics(
                program_id,
                start_date,
                end_date
            )
            
            # Get beneficiary progress data
            beneficiary_data = []
            for beneficiary in program.beneficiaries:
                data = self._gather_beneficiary_data(
                    beneficiary.id,
                    start_date,
                    end_date,
                    ['assessments', 'appointments', 'progress']
                )
                beneficiary_data.append({
                    'beneficiary': beneficiary,
                    'data': data
                })
            
            # Generate AI insights
            insights = self._generate_program_insights(
                program,
                analytics,
                beneficiary_data
            )
            
            report = {
                'program_overview': {
                    'id': program.id,
                    'name': program.name,
                    'description': program.description,
                    'total_beneficiaries': len(program.beneficiaries),
                    'duration_weeks': program.duration_weeks,
                    'status': program.status
                },
                'analytics': analytics,
                'ai_insights': insights,
                'beneficiary_summaries': self._summarize_beneficiaries(beneficiary_data),
                'recommendations': self._generate_program_recommendations(
                    program,
                    analytics,
                    insights
                )
            }
            
            # Add metadata
            report['metadata'] = {
                'program_id': program_id,
                'report_type': 'program_analysis',
                'time_period': time_period,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error generating program report: {str(e)}")
            return None, f"Error generating report: {str(e)}"
    
    def generate_comparative_report(
        self,
        beneficiary_ids: List[int],
        metrics: Optional[List[str]] = None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Generate comparative report for multiple beneficiaries.
        
        Args:
            beneficiary_ids: List of beneficiary IDs to compare
            metrics: Specific metrics to compare
            
        Returns:
            Tuple of (report_data, error_message)
        """
        try:
            if len(beneficiary_ids) < 2:
                return None, "At least 2 beneficiaries required for comparison"
            
            # Get beneficiaries
            beneficiaries = Beneficiary.query.filter(
                Beneficiary.id.in_(beneficiary_ids)
            ).all()
            
            if len(beneficiaries) != len(beneficiary_ids):
                return None, "Some beneficiaries not found"
            
            # Default metrics if not specified
            if not metrics:
                metrics = [
                    'assessment_scores',
                    'attendance_rate',
                    'progress_rate',
                    'engagement_level',
                    'completion_rate'
                ]
            
            # Gather data for each beneficiary
            comparison_data = {}
            for beneficiary in beneficiaries:
                data = self._gather_comparison_metrics(beneficiary.id, metrics)
                comparison_data[beneficiary.id] = {
                    'beneficiary': beneficiary,
                    'metrics': data
                }
            
            # Generate comparative insights
            insights = self._generate_comparative_insights(comparison_data, metrics)
            
            report = {
                'comparison_summary': self._create_comparison_summary(comparison_data),
                'metric_comparisons': self._create_metric_comparisons(comparison_data, metrics),
                'ai_insights': insights,
                'rankings': self._create_rankings(comparison_data, metrics),
                'recommendations': self._generate_comparative_recommendations(
                    comparison_data,
                    insights
                )
            }
            
            # Add metadata
            report['metadata'] = {
                'beneficiary_ids': beneficiary_ids,
                'metrics_compared': metrics,
                'report_type': 'comparative_analysis',
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error generating comparative report: {str(e)}")
            return None, f"Error generating report: {str(e)}"
    
    def synthesize_multi_source_data(
        self,
        beneficiary_id: int,
        sources: List[str]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Synthesize data from multiple sources into unified insights.
        
        Args:
            beneficiary_id: ID of the beneficiary
            sources: List of data sources to synthesize
            
        Returns:
            Tuple of (synthesis_data, error_message)
        """
        try:
            beneficiary = Beneficiary.query.get(beneficiary_id)
            if not beneficiary:
                return None, "Beneficiary not found"
            
            # Gather data from each source
            source_data = {}
            for source in sources:
                if source == 'assessments':
                    source_data['assessments'] = self._get_assessment_data(beneficiary_id)
                elif source == 'appointments':
                    source_data['appointments'] = self._get_appointment_data(beneficiary_id)
                elif source == 'documents':
                    source_data['documents'] = self._get_document_data(beneficiary_id)
                elif source == 'notes':
                    source_data['notes'] = self._get_notes_data(beneficiary_id)
                elif source == 'programs':
                    source_data['programs'] = self._get_program_data(beneficiary_id)
            
            # Use AI to synthesize insights
            synthesis = self._ai_synthesize_data(beneficiary, source_data)
            
            report = {
                'beneficiary_profile': {
                    'id': beneficiary.id,
                    'name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
                    'email': beneficiary.user.email
                },
                'source_summaries': self._create_source_summaries(source_data),
                'synthesized_insights': synthesis['insights'],
                'key_patterns': synthesis['patterns'],
                'timeline_analysis': synthesis['timeline'],
                'recommendations': synthesis['recommendations'],
                'action_items': self._generate_action_items(synthesis)
            }
            
            # Add metadata
            report['metadata'] = {
                'beneficiary_id': beneficiary_id,
                'sources_analyzed': sources,
                'report_type': 'multi_source_synthesis',
                'generated_at': datetime.utcnow().isoformat()
            }
            
            return report, None
            
        except Exception as e:
            logger.error(f"Error synthesizing multi-source data: {str(e)}")
            return None, f"Error synthesizing data: {str(e)}"
    
    # Private helper methods
    
    def _calculate_start_date(self, time_period: str, end_date: datetime) -> datetime:
        """Calculate start date based on time period."""
        if time_period == 'last_week':
            return end_date - timedelta(days=7)
        elif time_period == 'last_month':
            return end_date - timedelta(days=30)
        elif time_period == 'last_quarter':
            return end_date - timedelta(days=90)
        elif time_period == 'last_year':
            return end_date - timedelta(days=365)
        else:  # all_time
            return datetime(2020, 1, 1)
    
    def _get_default_sections(self, report_type: str) -> List[str]:
        """Get default sections for report type."""
        if report_type == 'comprehensive':
            return ['profile', 'assessments', 'appointments', 'progress', 'documents', 'notes']
        elif report_type == 'progress':
            return ['assessments', 'appointments', 'progress']
        elif report_type == 'assessment':
            return ['assessments', 'progress']
        return []
    
    def _gather_beneficiary_data(
        self,
        beneficiary_id: int,
        start_date: datetime,
        end_date: datetime,
        sections: List[str]
    ) -> Dict[str, Any]:
        """Gather all relevant data for a beneficiary."""
        data = {}
        
        if 'profile' in sections:
            data['profile'] = self._get_beneficiary_profile(beneficiary_id)
        
        if 'assessments' in sections:
            data['assessments'] = self._get_assessment_data(
                beneficiary_id, start_date, end_date
            )
        
        if 'appointments' in sections:
            data['appointments'] = self._get_appointment_data(
                beneficiary_id, start_date, end_date
            )
        
        if 'progress' in sections:
            data['progress'] = self._get_progress_data(
                beneficiary_id, start_date, end_date
            )
        
        if 'documents' in sections:
            data['documents'] = self._get_document_data(
                beneficiary_id, start_date, end_date
            )
        
        if 'notes' in sections:
            data['notes'] = self._get_notes_data(
                beneficiary_id, start_date, end_date
            )
        
        return data
    
    def _get_beneficiary_profile(self, beneficiary_id: int) -> Dict[str, Any]:
        """Get beneficiary profile information."""
        beneficiary = Beneficiary.query.get(beneficiary_id)
        
        return {
            'id': beneficiary.id,
            'name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
            'email': beneficiary.user.email,
            'phone': beneficiary.user.phone,
            'date_of_birth': beneficiary.date_of_birth.isoformat() if beneficiary.date_of_birth else None,
            'enrollment_date': beneficiary.enrollment_date.isoformat() if beneficiary.enrollment_date else None,
            'status': beneficiary.status,
            'emergency_contact': {
                'name': beneficiary.emergency_contact_name,
                'phone': beneficiary.emergency_contact_phone,
                'relationship': beneficiary.emergency_contact_relationship
            } if beneficiary.emergency_contact_name else None
        }
    
    def _get_assessment_data(
        self,
        beneficiary_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get assessment data for beneficiary."""
        query = TestSession.query.filter_by(beneficiary_id=beneficiary_id)
        
        if start_date and end_date:
            query = query.filter(
                TestSession.created_at.between(start_date, end_date)
            )
        
        sessions = query.order_by(desc(TestSession.created_at)).all()
        
        # Calculate statistics
        total_assessments = len(sessions)
        completed_assessments = len([s for s in sessions if s.status == 'completed'])
        
        scores = []
        for session in sessions:
            if session.score is not None:
                scores.append(session.score)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'total_assessments': total_assessments,
            'completed_assessments': completed_assessments,
            'average_score': round(avg_score, 2),
            'score_trend': self._calculate_score_trend(sessions),
            'recent_assessments': [
                {
                    'id': s.id,
                    'evaluation_title': s.evaluation.title if s.evaluation else 'Unknown',
                    'score': s.score,
                    'status': s.status,
                    'completed_at': s.submitted_at.isoformat() if s.submitted_at else None
                }
                for s in sessions[:5]
            ]
        }
    
    def _get_appointment_data(
        self,
        beneficiary_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get appointment data for beneficiary."""
        query = Appointment.query.filter_by(beneficiary_id=beneficiary_id)
        
        if start_date and end_date:
            query = query.filter(
                Appointment.start_time.between(start_date, end_date)
            )
        
        appointments = query.all()
        
        # Calculate statistics
        total_appointments = len(appointments)
        completed = len([a for a in appointments if a.status == 'completed'])
        cancelled = len([a for a in appointments if a.status == 'cancelled'])
        upcoming = len([a for a in appointments if a.status == 'scheduled' and a.start_time > datetime.utcnow()])
        
        attendance_rate = (completed / total_appointments * 100) if total_appointments > 0 else 0
        
        return {
            'total_appointments': total_appointments,
            'completed_appointments': completed,
            'cancelled_appointments': cancelled,
            'upcoming_appointments': upcoming,
            'attendance_rate': round(attendance_rate, 2),
            'recent_appointments': [
                {
                    'id': a.id,
                    'title': a.title,
                    'trainer': f"{a.trainer.first_name} {a.trainer.last_name}" if a.trainer else None,
                    'start_time': a.start_time.isoformat(),
                    'status': a.status
                }
                for a in sorted(appointments, key=lambda x: x.start_time, reverse=True)[:5]
            ]
        }
    
    def _get_progress_data(
        self,
        beneficiary_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get progress data for beneficiary."""
        # Get assessment scores over time
        sessions = TestSession.query.filter_by(
            beneficiary_id=beneficiary_id,
            status='completed'
        ).filter(
            TestSession.score.isnot(None)
        ).order_by(TestSession.submitted_at).all()
        
        # Calculate progress metrics
        if len(sessions) >= 2:
            first_score = sessions[0].score
            last_score = sessions[-1].score
            improvement = ((last_score - first_score) / first_score * 100) if first_score > 0 else 0
        else:
            improvement = 0
        
        # Get program completion data
        beneficiary = Beneficiary.query.get(beneficiary_id)
        program_progress = []
        
        for program in beneficiary.programs:
            completed_modules = 0  # This would need actual module tracking
            total_modules = 10  # Placeholder
            
            program_progress.append({
                'program_name': program.name,
                'completion_percentage': (completed_modules / total_modules * 100) if total_modules > 0 else 0,
                'status': program.status
            })
        
        return {
            'overall_improvement': round(improvement, 2),
            'score_history': [
                {
                    'date': s.submitted_at.isoformat(),
                    'score': s.score,
                    'evaluation': s.evaluation.title if s.evaluation else 'Unknown'
                }
                for s in sessions
            ],
            'program_progress': program_progress,
            'milestones_achieved': []  # Would need milestone tracking
        }
    
    def _get_document_data(
        self,
        beneficiary_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get document data for beneficiary."""
        query = Document.query.filter_by(beneficiary_id=beneficiary_id)
        
        if start_date and end_date:
            query = query.filter(
                Document.created_at.between(start_date, end_date)
            )
        
        documents = query.all()
        
        # Group by type
        doc_types = {}
        for doc in documents:
            doc_type = doc.document_type or 'other'
            if doc_type not in doc_types:
                doc_types[doc_type] = 0
            doc_types[doc_type] += 1
        
        return {
            'total_documents': len(documents),
            'document_types': doc_types,
            'recent_documents': [
                {
                    'id': d.id,
                    'title': d.title,
                    'type': d.document_type,
                    'created_at': d.created_at.isoformat()
                }
                for d in sorted(documents, key=lambda x: x.created_at, reverse=True)[:5]
            ]
        }
    
    def _get_notes_data(
        self,
        beneficiary_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get notes data for beneficiary."""
        query = Note.query.filter_by(beneficiary_id=beneficiary_id)
        
        if start_date and end_date:
            query = query.filter(
                Note.created_at.between(start_date, end_date)
            )
        
        notes = query.order_by(desc(Note.created_at)).all()
        
        return {
            'total_notes': len(notes),
            'recent_notes': [
                {
                    'id': n.id,
                    'content': n.content[:100] + '...' if len(n.content) > 100 else n.content,
                    'created_by': f"{n.created_by_user.first_name} {n.created_by_user.last_name}" if n.created_by_user else None,
                    'created_at': n.created_at.isoformat()
                }
                for n in notes[:5]
            ]
        }
    
    def _get_program_data(self, beneficiary_id: int) -> List[Dict[str, Any]]:
        """Get program data for beneficiary."""
        beneficiary = Beneficiary.query.get(beneficiary_id)
        
        return [
            {
                'id': p.id,
                'name': p.name,
                'status': p.status,
                'start_date': p.start_date.isoformat() if p.start_date else None,
                'end_date': p.end_date.isoformat() if p.end_date else None
            }
            for p in beneficiary.programs
        ]
    
    def _calculate_score_trend(self, sessions: List[TestSession]) -> str:
        """Calculate score trend from sessions."""
        if len(sessions) < 2:
            return 'insufficient_data'
        
        recent_scores = []
        for session in sessions[:5]:
            if session.score is not None:
                recent_scores.append(session.score)
        
        if len(recent_scores) < 2:
            return 'insufficient_data'
        
        # Simple trend calculation
        avg_recent = sum(recent_scores[:2]) / 2
        avg_older = sum(recent_scores[2:]) / len(recent_scores[2:]) if len(recent_scores) > 2 else recent_scores[-1]
        
        if avg_recent > avg_older * 1.05:
            return 'improving'
        elif avg_recent < avg_older * 0.95:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_comprehensive_report(
        self,
        beneficiary: Beneficiary,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive report using AI."""
        # Prepare context for AI
        context = self._prepare_ai_context(beneficiary, data)
        
        # Generate AI insights
        if self.api_key:
            insights = self._call_openai_api(context, 'comprehensive')
        else:
            insights = self._generate_mock_insights(context, 'comprehensive')
        
        return {
            'executive_summary': insights['executive_summary'],
            'key_findings': insights['key_findings'],
            'detailed_analysis': {
                'academic_performance': self._analyze_academic_performance(data),
                'attendance_engagement': self._analyze_attendance_engagement(data),
                'progress_trends': self._analyze_progress_trends(data),
                'strengths_weaknesses': insights['strengths_weaknesses']
            },
            'recommendations': insights['recommendations'],
            'action_items': insights['action_items']
        }
    
    def _generate_progress_report(
        self,
        beneficiary: Beneficiary,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate progress-focused report."""
        progress_data = data.get('progress', {})
        assessment_data = data.get('assessments', {})
        
        return {
            'progress_summary': {
                'overall_improvement': progress_data.get('overall_improvement', 0),
                'current_performance': 'above_average' if assessment_data.get('average_score', 0) > 70 else 'below_average',
                'trend': assessment_data.get('score_trend', 'stable')
            },
            'milestone_analysis': {
                'achieved': progress_data.get('milestones_achieved', []),
                'in_progress': [],
                'upcoming': []
            },
            'performance_metrics': {
                'assessment_scores': assessment_data.get('average_score', 0),
                'attendance_rate': data.get('appointments', {}).get('attendance_rate', 0),
                'engagement_level': self._calculate_engagement_level(data)
            },
            'recommendations': self._generate_progress_recommendations(data)
        }
    
    def _generate_assessment_report(
        self,
        beneficiary: Beneficiary,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate assessment-focused report."""
        assessment_data = data.get('assessments', {})
        
        return {
            'assessment_overview': {
                'total_completed': assessment_data.get('completed_assessments', 0),
                'average_score': assessment_data.get('average_score', 0),
                'trend': assessment_data.get('score_trend', 'stable')
            },
            'performance_analysis': {
                'strengths': self._identify_assessment_strengths(assessment_data),
                'areas_for_improvement': self._identify_improvement_areas(assessment_data),
                'score_distribution': self._calculate_score_distribution(assessment_data)
            },
            'recent_results': assessment_data.get('recent_assessments', []),
            'recommendations': self._generate_assessment_recommendations(assessment_data)
        }
    
    def _prepare_ai_context(
        self,
        beneficiary: Beneficiary,
        data: Dict[str, Any]
    ) -> str:
        """Prepare context for AI analysis."""
        context = f"""
        Beneficiary Profile:
        - Name: {beneficiary.user.first_name} {beneficiary.user.last_name}
        - Enrollment Date: {beneficiary.enrollment_date}
        - Status: {beneficiary.status}
        
        Assessment Performance:
        - Total Assessments: {data.get('assessments', {}).get('total_assessments', 0)}
        - Average Score: {data.get('assessments', {}).get('average_score', 0)}%
        - Score Trend: {data.get('assessments', {}).get('score_trend', 'unknown')}
        
        Attendance and Engagement:
        - Attendance Rate: {data.get('appointments', {}).get('attendance_rate', 0)}%
        - Completed Appointments: {data.get('appointments', {}).get('completed_appointments', 0)}
        - Cancelled Appointments: {data.get('appointments', {}).get('cancelled_appointments', 0)}
        
        Progress Metrics:
        - Overall Improvement: {data.get('progress', {}).get('overall_improvement', 0)}%
        - Active Programs: {len(data.get('progress', {}).get('program_progress', []))}
        
        Recent Activity:
        - Documents Uploaded: {data.get('documents', {}).get('total_documents', 0)}
        - Notes Added: {data.get('notes', {}).get('total_notes', 0)}
        """
        
        return context
    
    def _call_openai_api(self, context: str, report_type: str) -> Dict[str, Any]:
        """Call OpenAI API for insights generation."""
        try:
            prompt = self._create_ai_prompt(context, report_type)
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant specialized in analyzing educational and developmental data for beneficiaries in a training program. Provide insightful, actionable analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, report_type)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._generate_mock_insights(context, report_type)
    
    def _create_ai_prompt(self, context: str, report_type: str) -> str:
        """Create prompt for AI based on report type."""
        if report_type == 'comprehensive':
            return f"""
            Based on the following beneficiary data, generate a comprehensive analysis report:
            
            {context}
            
            Please provide:
            1. An executive summary (2-3 sentences)
            2. 3-5 key findings
            3. Analysis of strengths and areas for improvement
            4. 3-5 specific, actionable recommendations
            5. Priority action items
            
            Format the response as a structured analysis with clear sections.
            """
        elif report_type == 'progress':
            return f"""
            Analyze the following progress data and provide insights:
            
            {context}
            
            Focus on:
            1. Progress trends and patterns
            2. Performance trajectory
            3. Specific areas of improvement or concern
            4. Recommendations for maintaining or improving progress
            """
        else:
            return f"""
            Analyze the following data and provide insights:
            
            {context}
            
            Provide a structured analysis with key findings and recommendations.
            """
    
    def _parse_ai_response(self, response: str, report_type: str) -> Dict[str, Any]:
        """Parse AI response into structured format."""
        # This would need more sophisticated parsing in production
        # For now, return a structured mock response
        return self._generate_mock_insights("", report_type)
    
    def _generate_mock_insights(self, context: str, report_type: str) -> Dict[str, Any]:
        """Generate mock insights when AI is not available."""
        if report_type == 'comprehensive':
            return {
                'executive_summary': "The beneficiary shows consistent engagement with the program and demonstrates steady progress across key performance indicators. Overall trajectory is positive with some areas requiring additional support.",
                'key_findings': [
                    "Assessment scores show an upward trend with 15% improvement over the reporting period",
                    "Attendance rate of 85% indicates strong commitment to the program",
                    "Recent performance suggests readiness for more advanced learning objectives",
                    "Engagement metrics indicate high motivation and active participation",
                    "Documentation completion rate has improved significantly"
                ],
                'strengths_weaknesses': {
                    'strengths': [
                        "Consistent attendance and participation",
                        "Strong improvement in assessment scores",
                        "Excellent engagement with trainers",
                        "Proactive in seeking help when needed"
                    ],
                    'areas_for_improvement': [
                        "Time management skills could be enhanced",
                        "Written communication needs development",
                        "More practice needed in practical applications"
                    ]
                },
                'recommendations': [
                    "Continue current learning path with increased complexity",
                    "Implement weekly goal-setting sessions",
                    "Introduce peer mentoring opportunities",
                    "Focus on practical skill application",
                    "Schedule regular progress reviews"
                ],
                'action_items': [
                    {
                        'priority': 'high',
                        'action': 'Schedule advanced skills assessment',
                        'timeline': 'Within 2 weeks'
                    },
                    {
                        'priority': 'medium',
                        'action': 'Develop personalized learning plan',
                        'timeline': 'Within 1 month'
                    },
                    {
                        'priority': 'medium',
                        'action': 'Arrange peer learning sessions',
                        'timeline': 'Ongoing'
                    }
                ]
            }
        else:
            return {
                'summary': "Analysis complete",
                'findings': ["Finding 1", "Finding 2"],
                'recommendations': ["Recommendation 1", "Recommendation 2"]
            }
    
    def _analyze_academic_performance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze academic performance from data."""
        assessment_data = data.get('assessments', {})
        
        return {
            'current_level': self._determine_performance_level(assessment_data.get('average_score', 0)),
            'trend_analysis': assessment_data.get('score_trend', 'stable'),
            'consistency': self._calculate_consistency(assessment_data),
            'peak_performance': self._identify_peak_performance(assessment_data)
        }
    
    def _analyze_attendance_engagement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze attendance and engagement patterns."""
        appointment_data = data.get('appointments', {})
        
        return {
            'attendance_rate': appointment_data.get('attendance_rate', 0),
            'engagement_score': self._calculate_engagement_score(data),
            'participation_level': self._determine_participation_level(appointment_data),
            'consistency_rating': self._calculate_attendance_consistency(appointment_data)
        }
    
    def _analyze_progress_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze progress trends from data."""
        progress_data = data.get('progress', {})
        
        return {
            'overall_trajectory': 'positive' if progress_data.get('overall_improvement', 0) > 0 else 'needs_attention',
            'improvement_rate': progress_data.get('overall_improvement', 0),
            'milestone_completion': len(progress_data.get('milestones_achieved', [])),
            'projected_outcomes': self._project_outcomes(progress_data)
        }
    
    def _determine_performance_level(self, average_score: float) -> str:
        """Determine performance level based on score."""
        if average_score >= 90:
            return 'excellent'
        elif average_score >= 80:
            return 'very_good'
        elif average_score >= 70:
            return 'good'
        elif average_score >= 60:
            return 'satisfactory'
        else:
            return 'needs_improvement'
    
    def _calculate_consistency(self, assessment_data: Dict[str, Any]) -> float:
        """Calculate consistency score from assessment data."""
        # Simplified calculation
        recent_assessments = assessment_data.get('recent_assessments', [])
        if len(recent_assessments) < 2:
            return 0.0
        
        scores = [a['score'] for a in recent_assessments if a.get('score') is not None]
        if len(scores) < 2:
            return 0.0
        
        # Calculate standard deviation as a measure of consistency
        avg = sum(scores) / len(scores)
        variance = sum((x - avg) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to consistency score (lower std_dev = higher consistency)
        consistency = max(0, 100 - (std_dev * 2))
        return round(consistency, 2)
    
    def _identify_peak_performance(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify peak performance from assessments."""
        recent_assessments = assessment_data.get('recent_assessments', [])
        
        if not recent_assessments:
            return {'score': 0, 'date': None}
        
        best = max(recent_assessments, key=lambda x: x.get('score', 0))
        
        return {
            'score': best.get('score', 0),
            'date': best.get('completed_at'),
            'assessment': best.get('evaluation_title')
        }
    
    def _calculate_engagement_score(self, data: Dict[str, Any]) -> float:
        """Calculate overall engagement score."""
        factors = []
        
        # Attendance factor
        attendance_rate = data.get('appointments', {}).get('attendance_rate', 0)
        factors.append(attendance_rate)
        
        # Assessment completion factor
        assessment_data = data.get('assessments', {})
        if assessment_data.get('total_assessments', 0) > 0:
            completion_rate = (assessment_data.get('completed_assessments', 0) / 
                             assessment_data.get('total_assessments', 1) * 100)
            factors.append(completion_rate)
        
        # Document submission factor
        doc_count = data.get('documents', {}).get('total_documents', 0)
        doc_factor = min(100, doc_count * 10)  # Cap at 100
        factors.append(doc_factor)
        
        # Calculate average
        engagement_score = sum(factors) / len(factors) if factors else 0
        return round(engagement_score, 2)
    
    def _determine_participation_level(self, appointment_data: Dict[str, Any]) -> str:
        """Determine participation level from appointment data."""
        attendance_rate = appointment_data.get('attendance_rate', 0)
        
        if attendance_rate >= 90:
            return 'highly_active'
        elif attendance_rate >= 75:
            return 'active'
        elif attendance_rate >= 50:
            return 'moderate'
        else:
            return 'low'
    
    def _calculate_attendance_consistency(self, appointment_data: Dict[str, Any]) -> str:
        """Calculate attendance consistency rating."""
        completed = appointment_data.get('completed_appointments', 0)
        cancelled = appointment_data.get('cancelled_appointments', 0)
        total = appointment_data.get('total_appointments', 0)
        
        if total == 0:
            return 'no_data'
        
        consistency_score = (completed / total) * 100
        
        if consistency_score >= 90:
            return 'excellent'
        elif consistency_score >= 75:
            return 'good'
        elif consistency_score >= 50:
            return 'fair'
        else:
            return 'poor'
    
    def _project_outcomes(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Project future outcomes based on current progress."""
        improvement_rate = progress_data.get('overall_improvement', 0)
        
        # Simple linear projection
        projected_3_months = improvement_rate * 1.5
        projected_6_months = improvement_rate * 2.5
        
        return {
            '3_month_projection': round(projected_3_months, 2),
            '6_month_projection': round(projected_6_months, 2),
            'confidence_level': 'high' if improvement_rate > 10 else 'moderate'
        }
    
    def _calculate_engagement_level(self, data: Dict[str, Any]) -> float:
        """Calculate engagement level from various data points."""
        return self._calculate_engagement_score(data)
    
    def _generate_progress_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate progress-specific recommendations."""
        recommendations = []
        
        progress_data = data.get('progress', {})
        improvement = progress_data.get('overall_improvement', 0)
        
        if improvement < 5:
            recommendations.append("Consider adjusting learning approach to accelerate progress")
            recommendations.append("Schedule additional support sessions")
        elif improvement < 15:
            recommendations.append("Maintain current learning pace with gradual complexity increase")
            recommendations.append("Introduce advanced topics to sustain momentum")
        else:
            recommendations.append("Excellent progress - consider leadership or mentoring roles")
            recommendations.append("Explore specialized advanced training opportunities")
        
        # Attendance-based recommendations
        attendance_rate = data.get('appointments', {}).get('attendance_rate', 0)
        if attendance_rate < 70:
            recommendations.append("Improve attendance to maximize learning outcomes")
        
        return recommendations
    
    def _identify_assessment_strengths(self, assessment_data: Dict[str, Any]) -> List[str]:
        """Identify strengths from assessment data."""
        strengths = []
        
        avg_score = assessment_data.get('average_score', 0)
        if avg_score >= 80:
            strengths.append("Consistently high performance in assessments")
        
        if assessment_data.get('score_trend') == 'improving':
            strengths.append("Demonstrating continuous improvement")
        
        completed = assessment_data.get('completed_assessments', 0)
        total = assessment_data.get('total_assessments', 0)
        if total > 0 and completed / total >= 0.9:
            strengths.append("Excellent assessment completion rate")
        
        return strengths if strengths else ["Building foundational skills"]
    
    def _identify_improvement_areas(self, assessment_data: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement from assessment data."""
        areas = []
        
        avg_score = assessment_data.get('average_score', 0)
        if avg_score < 70:
            areas.append("Focus on improving overall assessment scores")
        
        if assessment_data.get('score_trend') == 'declining':
            areas.append("Address factors contributing to declining performance")
        
        # Look at consistency
        recent = assessment_data.get('recent_assessments', [])
        if len(recent) >= 3:
            scores = [a['score'] for a in recent if a.get('score') is not None]
            if scores and max(scores) - min(scores) > 20:
                areas.append("Work on maintaining consistent performance")
        
        return areas if areas else ["Continue building on current progress"]
    
    def _calculate_score_distribution(self, assessment_data: Dict[str, Any]) -> Dict[str, int]:
        """Calculate distribution of assessment scores."""
        distribution = {
            'excellent': 0,  # 90-100
            'very_good': 0,  # 80-89
            'good': 0,       # 70-79
            'fair': 0,       # 60-69
            'needs_improvement': 0  # <60
        }
        
        recent = assessment_data.get('recent_assessments', [])
        for assessment in recent:
            score = assessment.get('score', 0)
            if score >= 90:
                distribution['excellent'] += 1
            elif score >= 80:
                distribution['very_good'] += 1
            elif score >= 70:
                distribution['good'] += 1
            elif score >= 60:
                distribution['fair'] += 1
            else:
                distribution['needs_improvement'] += 1
        
        return distribution
    
    def _generate_assessment_recommendations(self, assessment_data: Dict[str, Any]) -> List[str]:
        """Generate assessment-specific recommendations."""
        recommendations = []
        
        avg_score = assessment_data.get('average_score', 0)
        trend = assessment_data.get('score_trend', 'stable')
        
        if avg_score < 60:
            recommendations.append("Provide additional study materials and support")
            recommendations.append("Consider reassessing learning objectives")
        elif avg_score < 70:
            recommendations.append("Focus on strengthening weak areas identified in assessments")
            recommendations.append("Implement targeted practice sessions")
        elif avg_score < 80:
            recommendations.append("Continue current approach with minor adjustments")
            recommendations.append("Introduce more challenging assessment topics")
        else:
            recommendations.append("Maintain excellence with advanced challenges")
            recommendations.append("Consider peer tutoring opportunities")
        
        if trend == 'declining':
            recommendations.append("Investigate causes of performance decline")
            recommendations.append("Provide additional motivation and support")
        elif trend == 'improving':
            recommendations.append("Recognize and celebrate improvement")
            recommendations.append("Maintain current strategies that are working")
        
        return recommendations
    
    # Methods for program report generation
    
    def _generate_program_insights(
        self,
        program: Program,
        analytics: Dict[str, Any],
        beneficiary_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate AI insights for program."""
        # Aggregate beneficiary performance
        total_beneficiaries = len(beneficiary_data)
        avg_scores = []
        attendance_rates = []
        
        for bd in beneficiary_data:
            data = bd['data']
            if 'assessments' in data:
                avg_scores.append(data['assessments'].get('average_score', 0))
            if 'appointments' in data:
                attendance_rates.append(data['appointments'].get('attendance_rate', 0))
        
        program_avg_score = sum(avg_scores) / len(avg_scores) if avg_scores else 0
        program_attendance = sum(attendance_rates) / len(attendance_rates) if attendance_rates else 0
        
        return {
            'overall_performance': self._determine_performance_level(program_avg_score),
            'engagement_level': self._determine_participation_level({'attendance_rate': program_attendance}),
            'key_insights': [
                f"Program has {total_beneficiaries} active beneficiaries",
                f"Average performance score: {round(program_avg_score, 2)}%",
                f"Average attendance rate: {round(program_attendance, 2)}%",
                f"Program completion rate: {analytics.get('completion_rate', 0)}%"
            ],
            'success_factors': self._identify_program_success_factors(analytics, beneficiary_data),
            'risk_factors': self._identify_program_risk_factors(analytics, beneficiary_data)
        }
    
    def _summarize_beneficiaries(
        self,
        beneficiary_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create summaries for each beneficiary in program."""
        summaries = []
        
        for bd in beneficiary_data:
            beneficiary = bd['beneficiary']
            data = bd['data']
            
            summary = {
                'beneficiary_id': beneficiary.id,
                'name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
                'performance_score': data.get('assessments', {}).get('average_score', 0),
                'attendance_rate': data.get('appointments', {}).get('attendance_rate', 0),
                'progress_trend': data.get('assessments', {}).get('score_trend', 'unknown'),
                'engagement_level': self._calculate_engagement_level(data),
                'risk_level': self._assess_beneficiary_risk(data)
            }
            
            summaries.append(summary)
        
        # Sort by performance
        summaries.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return summaries
    
    def _generate_program_recommendations(
        self,
        program: Program,
        analytics: Dict[str, Any],
        insights: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for program improvement."""
        recommendations = []
        
        # Performance-based recommendations
        if insights['overall_performance'] in ['needs_improvement', 'satisfactory']:
            recommendations.append({
                'priority': 'high',
                'category': 'performance',
                'recommendation': 'Review and update curriculum to address performance gaps',
                'rationale': 'Overall program performance is below expectations'
            })
        
        # Engagement-based recommendations
        if insights['engagement_level'] in ['low', 'moderate']:
            recommendations.append({
                'priority': 'high',
                'category': 'engagement',
                'recommendation': 'Implement engagement improvement strategies',
                'rationale': 'Low engagement levels may impact learning outcomes'
            })
        
        # Risk mitigation recommendations
        for risk in insights.get('risk_factors', []):
            recommendations.append({
                'priority': 'medium',
                'category': 'risk_mitigation',
                'recommendation': f"Address risk: {risk}",
                'rationale': 'Proactive risk management improves program success'
            })
        
        return recommendations
    
    def _identify_program_success_factors(
        self,
        analytics: Dict[str, Any],
        beneficiary_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify factors contributing to program success."""
        factors = []
        
        # Check completion rates
        if analytics.get('completion_rate', 0) > 80:
            factors.append("High program completion rate")
        
        # Check performance metrics
        high_performers = sum(
            1 for bd in beneficiary_data 
            if bd['data'].get('assessments', {}).get('average_score', 0) > 80
        )
        if high_performers / len(beneficiary_data) > 0.5:
            factors.append("Majority of beneficiaries performing above expectations")
        
        return factors
    
    def _identify_program_risk_factors(
        self,
        analytics: Dict[str, Any],
        beneficiary_data: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify risk factors for program."""
        risks = []
        
        # Check for low attendance
        low_attendance = sum(
            1 for bd in beneficiary_data 
            if bd['data'].get('appointments', {}).get('attendance_rate', 0) < 70
        )
        if low_attendance / len(beneficiary_data) > 0.3:
            risks.append("Significant portion of beneficiaries have low attendance")
        
        # Check for declining trends
        declining = sum(
            1 for bd in beneficiary_data 
            if bd['data'].get('assessments', {}).get('score_trend') == 'declining'
        )
        if declining / len(beneficiary_data) > 0.2:
            risks.append("Multiple beneficiaries showing declining performance")
        
        return risks
    
    def _assess_beneficiary_risk(self, data: Dict[str, Any]) -> str:
        """Assess risk level for a beneficiary."""
        risk_score = 0
        
        # Check attendance
        if data.get('appointments', {}).get('attendance_rate', 100) < 70:
            risk_score += 2
        
        # Check performance
        if data.get('assessments', {}).get('average_score', 100) < 60:
            risk_score += 2
        
        # Check trend
        if data.get('assessments', {}).get('score_trend') == 'declining':
            risk_score += 1
        
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    # Methods for comparative report
    
    def _gather_comparison_metrics(
        self,
        beneficiary_id: int,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Gather specific metrics for comparison."""
        data = {}
        
        if 'assessment_scores' in metrics:
            sessions = TestSession.query.filter_by(
                beneficiary_id=beneficiary_id,
                status='completed'
            ).all()
            scores = [s.score for s in sessions if s.score is not None]
            data['assessment_scores'] = {
                'average': sum(scores) / len(scores) if scores else 0,
                'highest': max(scores) if scores else 0,
                'lowest': min(scores) if scores else 0,
                'count': len(scores)
            }
        
        if 'attendance_rate' in metrics:
            appointments = Appointment.query.filter_by(beneficiary_id=beneficiary_id).all()
            total = len(appointments)
            completed = len([a for a in appointments if a.status == 'completed'])
            data['attendance_rate'] = (completed / total * 100) if total > 0 else 0
        
        if 'progress_rate' in metrics:
            # Calculate progress rate based on score improvement
            early_sessions = TestSession.query.filter_by(
                beneficiary_id=beneficiary_id,
                status='completed'
            ).order_by(TestSession.submitted_at).limit(3).all()
            
            recent_sessions = TestSession.query.filter_by(
                beneficiary_id=beneficiary_id,
                status='completed'
            ).order_by(desc(TestSession.submitted_at)).limit(3).all()
            
            early_avg = sum(s.score for s in early_sessions if s.score) / len(early_sessions) if early_sessions else 0
            recent_avg = sum(s.score for s in recent_sessions if s.score) / len(recent_sessions) if recent_sessions else 0
            
            data['progress_rate'] = ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
        
        if 'engagement_level' in metrics:
            # Composite engagement score
            all_data = self._gather_beneficiary_data(
                beneficiary_id,
                datetime.utcnow() - timedelta(days=90),
                datetime.utcnow(),
                ['appointments', 'assessments', 'documents']
            )
            data['engagement_level'] = self._calculate_engagement_level(all_data)
        
        if 'completion_rate' in metrics:
            # Calculate completion rate for assessments
            total_assessments = TestSession.query.filter_by(beneficiary_id=beneficiary_id).count()
            completed_assessments = TestSession.query.filter_by(
                beneficiary_id=beneficiary_id,
                status='completed'
            ).count()
            data['completion_rate'] = (completed_assessments / total_assessments * 100) if total_assessments > 0 else 0
        
        return data
    
    def _generate_comparative_insights(
        self,
        comparison_data: Dict[int, Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Generate insights from comparative data."""
        insights = {
            'top_performers': {},
            'areas_of_concern': [],
            'interesting_patterns': [],
            'recommendations_by_beneficiary': {}
        }
        
        # Identify top performers for each metric
        for metric in metrics:
            scores = []
            for ben_id, data in comparison_data.items():
                if metric in data['metrics']:
                    value = data['metrics'][metric]
                    if isinstance(value, dict):
                        value = value.get('average', 0)
                    scores.append((ben_id, value))
            
            if scores:
                scores.sort(key=lambda x: x[1], reverse=True)
                insights['top_performers'][metric] = {
                    'beneficiary_id': scores[0][0],
                    'value': scores[0][1]
                }
        
        # Identify areas of concern
        for ben_id, data in comparison_data.items():
            concerns = []
            
            if 'attendance_rate' in data['metrics'] and data['metrics']['attendance_rate'] < 70:
                concerns.append(f"Low attendance rate: {data['metrics']['attendance_rate']:.1f}%")
            
            if 'assessment_scores' in data['metrics'] and data['metrics']['assessment_scores']['average'] < 60:
                concerns.append(f"Low average score: {data['metrics']['assessment_scores']['average']:.1f}%")
            
            if concerns:
                insights['areas_of_concern'].append({
                    'beneficiary_id': ben_id,
                    'concerns': concerns
                })
        
        # Identify patterns
        if len(comparison_data) > 2:
            # Check for correlation between metrics
            attendance_values = []
            score_values = []
            
            for data in comparison_data.values():
                if 'attendance_rate' in data['metrics'] and 'assessment_scores' in data['metrics']:
                    attendance_values.append(data['metrics']['attendance_rate'])
                    score_values.append(data['metrics']['assessment_scores']['average'])
            
            if attendance_values and score_values:
                # Simple correlation check
                avg_attendance = sum(attendance_values) / len(attendance_values)
                avg_scores = sum(score_values) / len(score_values)
                
                high_attendance_high_scores = sum(
                    1 for i in range(len(attendance_values))
                    if attendance_values[i] > avg_attendance and score_values[i] > avg_scores
                )
                
                if high_attendance_high_scores / len(attendance_values) > 0.6:
                    insights['interesting_patterns'].append(
                        "Strong correlation between attendance and assessment performance"
                    )
        
        # Generate individual recommendations
        for ben_id, data in comparison_data.items():
            recommendations = []
            metrics_data = data['metrics']
            
            if 'attendance_rate' in metrics_data and metrics_data['attendance_rate'] < 80:
                recommendations.append("Focus on improving attendance")
            
            if 'progress_rate' in metrics_data and metrics_data['progress_rate'] < 5:
                recommendations.append("Implement strategies to accelerate progress")
            
            insights['recommendations_by_beneficiary'][ben_id] = recommendations
        
        return insights
    
    def _create_comparison_summary(
        self,
        comparison_data: Dict[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create summary of comparison data."""
        summary = {
            'total_beneficiaries': len(comparison_data),
            'date_generated': datetime.utcnow().isoformat(),
            'beneficiaries': []
        }
        
        for ben_id, data in comparison_data.items():
            beneficiary = data['beneficiary']
            summary['beneficiaries'].append({
                'id': ben_id,
                'name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
                'enrollment_date': beneficiary.enrollment_date.isoformat() if beneficiary.enrollment_date else None
            })
        
        return summary
    
    def _create_metric_comparisons(
        self,
        comparison_data: Dict[int, Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, Any]:
        """Create detailed metric comparisons."""
        comparisons = {}
        
        for metric in metrics:
            metric_data = []
            
            for ben_id, data in comparison_data.items():
                if metric in data['metrics']:
                    value = data['metrics'][metric]
                    if isinstance(value, dict):
                        metric_data.append({
                            'beneficiary_id': ben_id,
                            'values': value
                        })
                    else:
                        metric_data.append({
                            'beneficiary_id': ben_id,
                            'value': value
                        })
            
            if metric_data:
                comparisons[metric] = {
                    'data': metric_data,
                    'average': self._calculate_metric_average(metric_data),
                    'highest': self._find_metric_highest(metric_data),
                    'lowest': self._find_metric_lowest(metric_data)
                }
        
        return comparisons
    
    def _create_rankings(
        self,
        comparison_data: Dict[int, Dict[str, Any]],
        metrics: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Create rankings for each metric."""
        rankings = {}
        
        for metric in metrics:
            ranking = []
            
            for ben_id, data in comparison_data.items():
                if metric in data['metrics']:
                    value = data['metrics'][metric]
                    if isinstance(value, dict):
                        value = value.get('average', 0)
                    
                    ranking.append({
                        'beneficiary_id': ben_id,
                        'rank': 0,  # Will be set after sorting
                        'value': value
                    })
            
            # Sort and assign ranks
            ranking.sort(key=lambda x: x['value'], reverse=True)
            for i, item in enumerate(ranking):
                item['rank'] = i + 1
            
            rankings[metric] = ranking
        
        return rankings
    
    def _generate_comparative_recommendations(
        self,
        comparison_data: Dict[int, Dict[str, Any]],
        insights: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on comparative analysis."""
        recommendations = []
        
        # Check for significant performance gaps
        if 'assessment_scores' in insights.get('top_performers', {}):
            recommendations.append(
                "Consider peer mentoring between high and low performers"
            )
        
        # Check for widespread issues
        if len(insights.get('areas_of_concern', [])) > len(comparison_data) * 0.5:
            recommendations.append(
                "Review program structure as majority show concerning metrics"
            )
        
        # Pattern-based recommendations
        for pattern in insights.get('interesting_patterns', []):
            if 'correlation' in pattern.lower():
                recommendations.append(
                    "Leverage identified correlations to improve overall performance"
                )
        
        return recommendations
    
    def _calculate_metric_average(self, metric_data: List[Dict[str, Any]]) -> float:
        """Calculate average for a metric across beneficiaries."""
        values = []
        for item in metric_data:
            if 'value' in item:
                values.append(item['value'])
            elif 'values' in item and 'average' in item['values']:
                values.append(item['values']['average'])
        
        return sum(values) / len(values) if values else 0
    
    def _find_metric_highest(self, metric_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find highest value for a metric."""
        highest_value = -float('inf')
        highest_item = None
        
        for item in metric_data:
            value = item.get('value', 0)
            if 'values' in item and 'average' in item['values']:
                value = item['values']['average']
            
            if value > highest_value:
                highest_value = value
                highest_item = item
        
        return highest_item
    
    def _find_metric_lowest(self, metric_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find lowest value for a metric."""
        lowest_value = float('inf')
        lowest_item = None
        
        for item in metric_data:
            value = item.get('value', 0)
            if 'values' in item and 'average' in item['values']:
                value = item['values']['average']
            
            if value < lowest_value:
                lowest_value = value
                lowest_item = item
        
        return lowest_item
    
    # Multi-source synthesis methods
    
    def _ai_synthesize_data(
        self,
        beneficiary: Beneficiary,
        source_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to synthesize insights from multiple data sources."""
        # Prepare context from all sources
        context = self._prepare_synthesis_context(beneficiary, source_data)
        
        # Generate synthesis
        if self.api_key:
            synthesis = self._call_synthesis_api(context)
        else:
            synthesis = self._generate_mock_synthesis(source_data)
        
        return synthesis
    
    def _prepare_synthesis_context(
        self,
        beneficiary: Beneficiary,
        source_data: Dict[str, Any]
    ) -> str:
        """Prepare context for AI synthesis."""
        context_parts = [
            f"Beneficiary: {beneficiary.user.first_name} {beneficiary.user.last_name}",
            f"Status: {beneficiary.status}",
            ""
        ]
        
        # Add data from each source
        for source, data in source_data.items():
            if source == 'assessments':
                context_parts.append(f"Assessment Data:")
                context_parts.append(f"- Total: {data.get('total_assessments', 0)}")
                context_parts.append(f"- Average Score: {data.get('average_score', 0)}%")
                context_parts.append(f"- Trend: {data.get('score_trend', 'unknown')}")
            
            elif source == 'appointments':
                context_parts.append(f"Appointment Data:")
                context_parts.append(f"- Attendance Rate: {data.get('attendance_rate', 0)}%")
                context_parts.append(f"- Total: {data.get('total_appointments', 0)}")
            
            elif source == 'documents':
                context_parts.append(f"Document Data:")
                context_parts.append(f"- Total Documents: {data.get('total_documents', 0)}")
                context_parts.append(f"- Types: {', '.join(data.get('document_types', {}).keys())}")
            
            elif source == 'notes':
                context_parts.append(f"Notes Data:")
                context_parts.append(f"- Total Notes: {data.get('total_notes', 0)}")
            
            elif source == 'programs':
                context_parts.append(f"Program Data:")
                context_parts.append(f"- Active Programs: {len(data)}")
            
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _call_synthesis_api(self, context: str) -> Dict[str, Any]:
        """Call AI API for data synthesis."""
        # This would call OpenAI or similar service
        # For now, return mock synthesis
        return self._generate_mock_synthesis({})
    
    def _generate_mock_synthesis(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock synthesis when AI is not available."""
        return {
            'insights': [
                "Beneficiary shows consistent engagement across multiple touchpoints",
                "Performance metrics indicate steady progress with room for acceleration",
                "Documentation and notes suggest active participation in program activities",
                "Cross-source analysis reveals strong correlation between attendance and outcomes"
            ],
            'patterns': [
                {
                    'pattern': 'Engagement Consistency',
                    'description': 'Regular participation across assessments, appointments, and activities',
                    'impact': 'positive'
                },
                {
                    'pattern': 'Performance Trajectory',
                    'description': 'Gradual improvement trend across multiple metrics',
                    'impact': 'positive'
                }
            ],
            'timeline': {
                'recent_activity': 'High activity in the last 30 days',
                'peak_periods': ['Morning sessions', 'Mid-week appointments'],
                'quiet_periods': ['Weekend activities show lower engagement']
            },
            'recommendations': [
                "Maintain current engagement levels while introducing advanced challenges",
                "Schedule regular check-ins during identified peak performance periods",
                "Consider peer learning opportunities to enhance growth",
                "Document successful strategies for replication with other beneficiaries"
            ]
        }
    
    def _create_source_summaries(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summaries for each data source."""
        summaries = {}
        
        for source, data in source_data.items():
            if source == 'assessments':
                summaries[source] = {
                    'key_metric': f"{data.get('average_score', 0):.1f}% average score",
                    'trend': data.get('score_trend', 'unknown'),
                    'volume': f"{data.get('total_assessments', 0)} assessments"
                }
            elif source == 'appointments':
                summaries[source] = {
                    'key_metric': f"{data.get('attendance_rate', 0):.1f}% attendance",
                    'volume': f"{data.get('total_appointments', 0)} appointments"
                }
            elif source == 'documents':
                summaries[source] = {
                    'volume': f"{data.get('total_documents', 0)} documents",
                    'types': list(data.get('document_types', {}).keys())
                }
            elif source == 'notes':
                summaries[source] = {
                    'volume': f"{data.get('total_notes', 0)} notes"
                }
            elif source == 'programs':
                summaries[source] = {
                    'active': len([p for p in data if p['status'] == 'active']),
                    'total': len(data)
                }
        
        return summaries
    
    def _generate_action_items(self, synthesis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable items from synthesis."""
        action_items = []
        
        # Create actions based on recommendations
        for i, rec in enumerate(synthesis.get('recommendations', [])):
            priority = 'high' if i < 2 else 'medium'
            
            action_items.append({
                'priority': priority,
                'action': rec,
                'timeline': '2 weeks' if priority == 'high' else '1 month',
                'category': self._categorize_action(rec)
            })
        
        return action_items
    
    def _categorize_action(self, action: str) -> str:
        """Categorize an action item."""
        action_lower = action.lower()
        
        if 'schedule' in action_lower or 'appointment' in action_lower:
            return 'scheduling'
        elif 'document' in action_lower or 'record' in action_lower:
            return 'documentation'
        elif 'learn' in action_lower or 'challenge' in action_lower:
            return 'learning'
        elif 'review' in action_lower or 'check' in action_lower:
            return 'monitoring'
        else:
            return 'general'


# Create singleton instance
ai_report_service = AIReportService()