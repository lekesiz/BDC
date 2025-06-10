_('services_ai_report_service.message.ai_powered_report_synthesis_se')
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session
import openai
from jinja2 import Template
from app.extensions import db, cache
from app.models import Beneficiary, User, Appointment, Document, Program, Evaluation, TestSession, EvaluationResponse
from app.models.notification import Note
from app.models.assessment import Assessment, AssessmentSection, AssessmentResponse
from app.services.analytics_service import AnalyticsService
from app.utils.logging import logger
from flask_babel import _, lazy_gettext as _l


class AIReportService:
    _('services_ai_report_service.message.service_for_generating_ai_powe')

    def __init__(self):
        _('services_ai_report_service.message.initialize_ai_report_service')
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        self.analytics_service = AnalyticsService()

    def generate_beneficiary_report(self, beneficiary_id: int, report_type:
        str='comprehensive', time_period: str='last_month',
        include_sections: Optional[List[str]]=None) ->Tuple[Optional[Dict[
        str, Any]], Optional[str]]:
        _('services_ai_report_service.error.generate_a_comprehensive_ai_po')
        try:
            cache_key = (
                f'ai_report:{beneficiary_id}:{report_type}:{time_period}')
            cached_report = cache.get(cache_key)
            if cached_report:
                return json.loads(cached_report), None
            beneficiary = Beneficiary.query.get(beneficiary_id)
            if not beneficiary:
                return None, _(
                    'services_ai_report_service.label.beneficiary_not_found_1')
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(time_period, end_date)
            data = self._gather_beneficiary_data(beneficiary_id, start_date,
                end_date, include_sections or self._get_default_sections(
                report_type))
            if report_type == 'comprehensive':
                report = self._generate_comprehensive_report(beneficiary, data)
            elif report_type == 'progress':
                report = self._generate_progress_report(beneficiary, data)
            elif report_type == 'assessment':
                report = self._generate_assessment_report(beneficiary, data)
            else:
                return None, f'Unknown report type: {report_type}'
            report['metadata'] = {'beneficiary_id': beneficiary_id,
                'beneficiary_name':
                f'{beneficiary.user.first_name} {beneficiary.user.last_name}',
                'report_type': report_type, 'time_period': time_period,
                'start_date': start_date.isoformat(), 'end_date': end_date.
                isoformat(), 'generated_at': datetime.utcnow().isoformat(),
                'generated_by': _(
                'services_ai_report_service.message.ai_report_service_v2_0')}
            cache.set(cache_key, json.dumps(report), timeout=3600)
            return report, None
        except Exception as e:
            logger.error(f'Error generating beneficiary report: {str(e)}')
            return None, f'Error generating report: {str(e)}'

    def generate_program_report(self, program_id: int, time_period: str=
        'last_month') ->Tuple[Optional[Dict[str, Any]], Optional[str]]:
        _('services_ai_report_service.error.generate_ai_powered_report_for')
        try:
            program = Program.query.get(program_id)
            if not program:
                return None, _(
                    'services_ai_report_service.label.program_not_found')
            end_date = datetime.utcnow()
            start_date = self._calculate_start_date(time_period, end_date)
            analytics = self.analytics_service.get_program_analytics(program_id
                , start_date, end_date)
            beneficiary_data = []
            for beneficiary in program.beneficiaries:
                data = self._gather_beneficiary_data(beneficiary.id,
                    start_date, end_date, ['assessments', 'appointments',
                    'progress'])
                beneficiary_data.append({'beneficiary': beneficiary, 'data':
                    data})
            insights = self._generate_program_insights(program, analytics,
                beneficiary_data)
            report = {'program_overview': {'id': program.id, 'name':
                program.name, 'description': program.description,
                'total_beneficiaries': len(program.beneficiaries),
                'duration_weeks': program.duration_weeks, 'status': program
                .status}, 'analytics': analytics, 'ai_insights': insights,
                'beneficiary_summaries': self._summarize_beneficiaries(
                beneficiary_data), 'recommendations': self.
                _generate_program_recommendations(program, analytics, insights)
                }
            report['metadata'] = {'program_id': program_id, 'report_type':
                'program_analysis', 'time_period': time_period,
                'generated_at': datetime.utcnow().isoformat()}
            return report, None
        except Exception as e:
            logger.error(f'Error generating program report: {str(e)}')
            return None, f'Error generating report: {str(e)}'

    def generate_comparative_report(self, beneficiary_ids: List[int],
        metrics: Optional[List[str]]=None) ->Tuple[Optional[Dict[str, Any]],
        Optional[str]]:
        _('services_ai_report_service.error.generate_comparative_report_fo')
        try:
            if len(beneficiary_ids) < 2:
                return None, _(
                    'services_ai_report_service.validation.at_least_2_beneficiaries_requi'
                    )
            beneficiaries = Beneficiary.query.filter(Beneficiary.id.in_(
                beneficiary_ids)).all()
            if len(beneficiaries) != len(beneficiary_ids):
                return None, _(
                    'services_ai_report_service.message.some_beneficiaries_not_found'
                    )
            if not metrics:
                metrics = ['assessment_scores', 'attendance_rate',
                    'progress_rate', 'engagement_level', 'completion_rate']
            comparison_data = {}
            for beneficiary in beneficiaries:
                data = self._gather_comparison_metrics(beneficiary.id, metrics)
                comparison_data[beneficiary.id] = {'beneficiary':
                    beneficiary, 'metrics': data}
            insights = self._generate_comparative_insights(comparison_data,
                metrics)
            report = {'comparison_summary': self._create_comparison_summary
                (comparison_data), 'metric_comparisons': self.
                _create_metric_comparisons(comparison_data, metrics),
                'ai_insights': insights, 'rankings': self._create_rankings(
                comparison_data, metrics), 'recommendations': self.
                _generate_comparative_recommendations(comparison_data,
                insights)}
            report['metadata'] = {'beneficiary_ids': beneficiary_ids,
                'metrics_compared': metrics, 'report_type':
                'comparative_analysis', 'generated_at': datetime.utcnow().
                isoformat()}
            return report, None
        except Exception as e:
            logger.error(f'Error generating comparative report: {str(e)}')
            return None, f'Error generating report: {str(e)}'

    def synthesize_multi_source_data(self, beneficiary_id: int, sources:
        List[str]) ->Tuple[Optional[Dict[str, Any]], Optional[str]]:
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
                return None, _(
                    'services_ai_report_service.label.beneficiary_not_found_1')
            source_data = {}
            for source in sources:
                if source == 'assessments':
                    source_data['assessments'] = self._get_assessment_data(
                        beneficiary_id)
                elif source == 'appointments':
                    source_data['appointments'] = self._get_appointment_data(
                        beneficiary_id)
                elif source == 'documents':
                    source_data['documents'] = self._get_document_data(
                        beneficiary_id)
                elif source == 'notes':
                    source_data['notes'] = self._get_notes_data(beneficiary_id)
                elif source == 'programs':
                    source_data['programs'] = self._get_program_data(
                        beneficiary_id)
            synthesis = self._ai_synthesize_data(beneficiary, source_data)
            report = {'beneficiary_profile': {'id': beneficiary.id, 'name':
                f'{beneficiary.user.first_name} {beneficiary.user.last_name}',
                'email': beneficiary.user.email}, 'source_summaries': self.
                _create_source_summaries(source_data),
                'synthesized_insights': synthesis['insights'],
                'key_patterns': synthesis['patterns'], 'timeline_analysis':
                synthesis['timeline'], 'recommendations': synthesis[
                'recommendations'], 'action_items': self.
                _generate_action_items(synthesis)}
            report['metadata'] = {'beneficiary_id': beneficiary_id,
                'sources_analyzed': sources, 'report_type':
                'multi_source_synthesis', 'generated_at': datetime.utcnow()
                .isoformat()}
            return report, None
        except Exception as e:
            logger.error(f'Error synthesizing multi-source data: {str(e)}')
            return None, f'Error synthesizing data: {str(e)}'

    def _calculate_start_date(self, time_period: str, end_date: datetime
        ) ->datetime:
        _('services_ai_report_service.message.calculate_start_date_based_on')
        if time_period == 'last_week':
            return end_date - timedelta(days=7)
        elif time_period == 'last_month':
            return end_date - timedelta(days=30)
        elif time_period == 'last_quarter':
            return end_date - timedelta(days=90)
        elif time_period == 'last_year':
            return end_date - timedelta(days=365)
        else:
            return datetime(2020, 1, 1)

    def _get_default_sections(self, report_type: str) ->List[str]:
        _('services_ai_report_service.message.get_default_sections_for_repor')
        if report_type == 'comprehensive':
            return ['profile', 'assessments', 'appointments', 'progress',
                'documents', 'notes']
        elif report_type == 'progress':
            return ['assessments', 'appointments', 'progress']
        elif report_type == 'assessment':
            return ['assessments', 'progress']
        return []

    def _gather_beneficiary_data(self, beneficiary_id: int, start_date:
        datetime, end_date: datetime, sections: List[str]) ->Dict[str, Any]:
        _('services_ai_report_service.message.gather_all_relevant_data_for_a')
        data = {}
        if 'profile' in sections:
            data['profile'] = self._get_beneficiary_profile(beneficiary_id)
        if 'assessments' in sections:
            data['assessments'] = self._get_assessment_data(beneficiary_id,
                start_date, end_date)
        if 'appointments' in sections:
            data['appointments'] = self._get_appointment_data(beneficiary_id,
                start_date, end_date)
        if 'progress' in sections:
            data['progress'] = self._get_progress_data(beneficiary_id,
                start_date, end_date)
        if 'documents' in sections:
            data['documents'] = self._get_document_data(beneficiary_id,
                start_date, end_date)
        if 'notes' in sections:
            data['notes'] = self._get_notes_data(beneficiary_id, start_date,
                end_date)
        return data

    def _get_beneficiary_profile(self, beneficiary_id: int) ->Dict[str, Any]:
        _('services_ai_report_service.validation.get_beneficiary_profile_inform'
            )
        beneficiary = Beneficiary.query.get(beneficiary_id)
        return {'id': beneficiary.id, 'name':
            f'{beneficiary.user.first_name} {beneficiary.user.last_name}',
            'email': beneficiary.user.email, 'phone': beneficiary.user.
            phone, 'date_of_birth': beneficiary.date_of_birth.isoformat() if
            beneficiary.date_of_birth else None, 'enrollment_date': 
            beneficiary.enrollment_date.isoformat() if beneficiary.
            enrollment_date else None, 'status': beneficiary.status,
            'emergency_contact': {'name': beneficiary.
            emergency_contact_name, 'phone': beneficiary.
            emergency_contact_phone, 'relationship': beneficiary.
            emergency_contact_relationship} if beneficiary.
            emergency_contact_name else None}

    def _get_assessment_data(self, beneficiary_id: int, start_date:
        Optional[datetime]=None, end_date: Optional[datetime]=None) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.get_assessment_data_for_benefi')
        query = TestSession.query.filter_by(beneficiary_id=beneficiary_id)
        if start_date and end_date:
            query = query.filter(TestSession.created_at.between(start_date,
                end_date))
        sessions = query.order_by(desc(TestSession.created_at)).all()
        total_assessments = len(sessions)
        completed_assessments = len([s for s in sessions if s.status ==
            'completed'])
        scores = []
        for session in sessions:
            if session.score is not None:
                scores.append(session.score)
        avg_score = sum(scores) / len(scores) if scores else 0
        return {'total_assessments': total_assessments,
            'completed_assessments': completed_assessments, 'average_score':
            round(avg_score, 2), 'score_trend': self._calculate_score_trend
            (sessions), 'recent_assessments': [{'id': s.id,
            'evaluation_title': s.evaluation.title if s.evaluation else _(
            'analytics_data_export.label.unknown'), 'score': s.score,
            'status': s.status, 'completed_at': s.submitted_at.isoformat() if
            s.submitted_at else None} for s in sessions[:5]]}

    def _get_appointment_data(self, beneficiary_id: int, start_date:
        Optional[datetime]=None, end_date: Optional[datetime]=None) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.get_appointment_data_for_benef')
        query = Appointment.query.filter_by(beneficiary_id=beneficiary_id)
        if start_date and end_date:
            query = query.filter(Appointment.start_time.between(start_date,
                end_date))
        appointments = query.all()
        total_appointments = len(appointments)
        completed = len([a for a in appointments if a.status == 'completed'])
        cancelled = len([a for a in appointments if a.status == 'cancelled'])
        upcoming = len([a for a in appointments if a.status == 'scheduled' and
            a.start_time > datetime.utcnow()])
        attendance_rate = (completed / total_appointments * 100 if 
            total_appointments > 0 else 0)
        return {'total_appointments': total_appointments,
            'completed_appointments': completed, 'cancelled_appointments':
            cancelled, 'upcoming_appointments': upcoming, 'attendance_rate':
            round(attendance_rate, 2), 'recent_appointments': [{'id': a.id,
            'title': a.title, 'trainer': 
            f'{a.trainer.first_name} {a.trainer.last_name}' if a.trainer else
            None, 'start_time': a.start_time.isoformat(), 'status': a.
            status} for a in sorted(appointments, key=lambda x: x.
            start_time, reverse=True)[:5]]}

    def _get_progress_data(self, beneficiary_id: int, start_date: Optional[
        datetime]=None, end_date: Optional[datetime]=None) ->Dict[str, Any]:
        _('services_ai_report_service.message.get_progress_data_for_benefici')
        sessions = TestSession.query.filter_by(beneficiary_id=
            beneficiary_id, status='completed').filter(TestSession.score.
            isnot(None)).order_by(TestSession.submitted_at).all()
        if len(sessions) >= 2:
            first_score = sessions[0].score
            last_score = sessions[-1].score
            improvement = (last_score - first_score
                ) / first_score * 100 if first_score > 0 else 0
        else:
            improvement = 0
        beneficiary = Beneficiary.query.get(beneficiary_id)
        program_progress = []
        for program in beneficiary.programs:
            completed_modules = 0
            total_modules = 10
            program_progress.append({'program_name': program.name,
                'completion_percentage': completed_modules / total_modules *
                100 if total_modules > 0 else 0, 'status': program.status})
        return {'overall_improvement': round(improvement, 2),
            'score_history': [{'date': s.submitted_at.isoformat(), 'score':
            s.score, 'evaluation': s.evaluation.title if s.evaluation else
            _('analytics_data_export.label.unknown')} for s in sessions],
            'program_progress': program_progress, 'milestones_achieved': []}

    def _get_document_data(self, beneficiary_id: int, start_date: Optional[
        datetime]=None, end_date: Optional[datetime]=None) ->Dict[str, Any]:
        _('services_ai_report_service.message.get_document_data_for_benefici')
        query = Document.query.filter_by(beneficiary_id=beneficiary_id)
        if start_date and end_date:
            query = query.filter(Document.created_at.between(start_date,
                end_date))
        documents = query.all()
        doc_types = {}
        for doc in documents:
            doc_type = doc.document_type or 'other'
            if doc_type not in doc_types:
                doc_types[doc_type] = 0
            doc_types[doc_type] += 1
        return {'total_documents': len(documents), 'document_types':
            doc_types, 'recent_documents': [{'id': d.id, 'title': d.title,
            'type': d.document_type, 'created_at': d.created_at.isoformat()
            } for d in sorted(documents, key=lambda x: x.created_at,
            reverse=True)[:5]]}

    def _get_notes_data(self, beneficiary_id: int, start_date: Optional[
        datetime]=None, end_date: Optional[datetime]=None) ->Dict[str, Any]:
        _('services_ai_report_service.message.get_notes_data_for_beneficiary')
        query = Note.query.filter_by(beneficiary_id=beneficiary_id)
        if start_date and end_date:
            query = query.filter(Note.created_at.between(start_date, end_date))
        notes = query.order_by(desc(Note.created_at)).all()
        return {'total_notes': len(notes), 'recent_notes': [{'id': n.id,
            'content': n.content[:100] + '...' if len(n.content) > 100 else
            n.content, 'created_by': 
            f'{n.created_by_user.first_name} {n.created_by_user.last_name}' if
            n.created_by_user else None, 'created_at': n.created_at.
            isoformat()} for n in notes[:5]]}

    def _get_program_data(self, beneficiary_id: int) ->List[Dict[str, Any]]:
        _('services_ai_report_service.message.get_program_data_for_beneficia')
        beneficiary = Beneficiary.query.get(beneficiary_id)
        return [{'id': p.id, 'name': p.name, 'status': p.status,
            'start_date': p.start_date.isoformat() if p.start_date else
            None, 'end_date': p.end_date.isoformat() if p.end_date else
            None} for p in beneficiary.programs]

    def _calculate_score_trend(self, sessions: List[TestSession]) ->str:
        """Calculate score trend from sessions."""
        if len(sessions) < 2:
            return 'insufficient_data'
        recent_scores = []
        for session in sessions[:5]:
            if session.score is not None:
                recent_scores.append(session.score)
        if len(recent_scores) < 2:
            return 'insufficient_data'
        avg_recent = sum(recent_scores[:2]) / 2
        avg_older = sum(recent_scores[2:]) / len(recent_scores[2:]) if len(
            recent_scores) > 2 else recent_scores[-1]
        if avg_recent > avg_older * 1.05:
            return 'improving'
        elif avg_recent < avg_older * 0.95:
            return 'declining'
        else:
            return 'stable'

    def _generate_comprehensive_report(self, beneficiary: Beneficiary, data:
        Dict[str, Any]) ->Dict[str, Any]:
        _('services_ai_report_service.message.generate_comprehensive_report')
        context = self._prepare_ai_context(beneficiary, data)
        if self.api_key:
            insights = self._call_openai_api(context, 'comprehensive')
        else:
            insights = self._generate_mock_insights(context, 'comprehensive')
        return {'executive_summary': insights['executive_summary'],
            'key_findings': insights['key_findings'], 'detailed_analysis':
            {'academic_performance': self._analyze_academic_performance(
            data), 'attendance_engagement': self.
            _analyze_attendance_engagement(data), 'progress_trends': self.
            _analyze_progress_trends(data), 'strengths_weaknesses':
            insights['strengths_weaknesses']}, 'recommendations': insights[
            'recommendations'], 'action_items': insights['action_items']}

    def _generate_progress_report(self, beneficiary: Beneficiary, data:
        Dict[str, Any]) ->Dict[str, Any]:
        _('services_ai_report_service.label.generate_progress_focused_repo')
        progress_data = data.get('progress', {})
        assessment_data = data.get('assessments', {})
        return {'progress_summary': {'overall_improvement': progress_data.
            get('overall_improvement', 0), 'current_performance': 
            'above_average' if assessment_data.get('average_score', 0) > 70
             else 'below_average', 'trend': assessment_data.get(
            'score_trend', 'stable')}, 'milestone_analysis': {'achieved':
            progress_data.get('milestones_achieved', []), 'in_progress': [],
            'upcoming': []}, 'performance_metrics': {'assessment_scores':
            assessment_data.get('average_score', 0), 'attendance_rate':
            data.get('appointments', {}).get('attendance_rate', 0),
            'engagement_level': self._calculate_engagement_level(data)},
            'recommendations': self._generate_progress_recommendations(data)}

    def _generate_assessment_report(self, beneficiary: Beneficiary, data:
        Dict[str, Any]) ->Dict[str, Any]:
        _('services_ai_report_service.label.generate_assessment_focused_re')
        assessment_data = data.get('assessments', {})
        return {'assessment_overview': {'total_completed': assessment_data.
            get('completed_assessments', 0), 'average_score':
            assessment_data.get('average_score', 0), 'trend':
            assessment_data.get('score_trend', 'stable')},
            'performance_analysis': {'strengths': self.
            _identify_assessment_strengths(assessment_data),
            'areas_for_improvement': self._identify_improvement_areas(
            assessment_data), 'score_distribution': self.
            _calculate_score_distribution(assessment_data)},
            'recent_results': assessment_data.get('recent_assessments', []),
            'recommendations': self._generate_assessment_recommendations(
            assessment_data)}

    def _prepare_ai_context(self, beneficiary: Beneficiary, data: Dict[str,
        Any]) ->str:
        _('services_ai_report_service.message.prepare_context_for_ai_analysi')
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

    def _call_openai_api(self, context: str, report_type: str) ->Dict[str, Any
        ]:
        _('services_ai_report_service.message.call_openai_api_for_insights_g')
        try:
            prompt = self._create_ai_prompt(context, report_type)
            response = openai.ChatCompletion.create(model=_(
                'orchestration_examples.message.gpt_4_2'), messages=[{
                'role': 'system', 'content': _(
                'services_ai_report_service.message.you_are_an_ai_assistant_specia'
                )}, {'role': 'user', 'content': prompt}], temperature=0.7,
                max_tokens=2000)
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response, report_type)
        except Exception as e:
            logger.error(f'OpenAI API error: {str(e)}')
            return self._generate_mock_insights(context, report_type)

    def _create_ai_prompt(self, context: str, report_type: str) ->str:
        _('services_ai_report_service.message.create_prompt_for_ai_based_on')
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

    def _parse_ai_response(self, response: str, report_type: str) ->Dict[
        str, Any]:
        _('services_ai_report_service.validation.parse_ai_response_into_structu'
            )
        return self._generate_mock_insights('', report_type)

    def _generate_mock_insights(self, context: str, report_type: str) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.generate_mock_insights_when_ai')
        if report_type == 'comprehensive':
            return {'executive_summary': _(
                'services_ai_report_service.message.the_beneficiary_shows_consiste'
                ), 'key_findings': [_(
                'services_ai_report_service.message.assessment_scores_show_an_upwa'
                ), _(
                'services_ai_report_service.message.attendance_rate_of_85_indicat'
                ), _(
                'services_ai_report_service.message.recent_performance_suggests_re'
                ), _(
                'services_ai_report_service.message.engagement_metrics_indicate_hi'
                ), _(
                'services_ai_report_service.message.documentation_completion_rate'
                )], 'strengths_weaknesses': {'strengths': [_(
                'services_ai_report_service.message.consistent_attendance_and_part'
                ), _(
                'services_ai_report_service.message.strong_improvement_in_assessme'
                ), _(
                'services_ai_report_service.message.excellent_engagement_with_trai'
                ), _(
                'services_ai_report_service.message.proactive_in_seeking_help_when'
                )], 'areas_for_improvement': [_(
                'services_ai_report_service.message.time_management_skills_could_b'
                ), _(
                'services_ai_report_service.message.written_communication_needs_de'
                ), _(
                'services_ai_report_service.message.more_practice_needed_in_practi'
                )]}, 'recommendations': [_(
                'services_ai_report_service.message.continue_current_learning_path'
                ), _(
                'services_ai_report_service.message.implement_weekly_goal_setting'
                ), _(
                'services_ai_report_service.message.introduce_peer_mentoring_oppor'
                ), _(
                'services_ai_report_service.message.focus_on_practical_skill_appli'
                ), _(
                'services_ai_report_service.message.schedule_regular_progress_revi'
                )], 'action_items': [{'priority': 'high', 'action': _(
                'services_ai_report_service.message.schedule_advanced_skills_asses'
                ), 'timeline': _(
                'services_ai_report_service.label.within_2_weeks')}, {
                'priority': 'medium', 'action': _(
                'services_ai_report_service.message.develop_personalized_learning'
                ), 'timeline': _(
                'services_ai_report_service.label.within_1_month')}, {
                'priority': 'medium', 'action': _(
                'services_ai_report_service.message.arrange_peer_learning_sessions'
                ), 'timeline': _('services_ai_report_service.label.ongoing')}]}
        else:
            return {'summary': _(
                'services_ai_report_service.success.analysis_complete'),
                'findings': [_('services_ai_report_service.label.finding_1'
                ), _('services_ai_report_service.label.finding_2')],
                'recommendations': [_(
                'services_ai_report_service.label.recommendation_1'), _(
                'services_ai_report_service.label.recommendation_2')]}

    def _analyze_academic_performance(self, data: Dict[str, Any]) ->Dict[
        str, Any]:
        """Analyze academic performance from data."""
        assessment_data = data.get('assessments', {})
        return {'current_level': self._determine_performance_level(
            assessment_data.get('average_score', 0)), 'trend_analysis':
            assessment_data.get('score_trend', 'stable'), 'consistency':
            self._calculate_consistency(assessment_data),
            'peak_performance': self._identify_peak_performance(
            assessment_data)}

    def _analyze_attendance_engagement(self, data: Dict[str, Any]) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.analyze_attendance_and_engagem')
        appointment_data = data.get('appointments', {})
        return {'attendance_rate': appointment_data.get('attendance_rate', 
            0), 'engagement_score': self._calculate_engagement_score(data),
            'participation_level': self._determine_participation_level(
            appointment_data), 'consistency_rating': self.
            _calculate_attendance_consistency(appointment_data)}

    def _analyze_progress_trends(self, data: Dict[str, Any]) ->Dict[str, Any]:
        """Analyze progress trends from data."""
        progress_data = data.get('progress', {})
        return {'overall_trajectory': 'positive' if progress_data.get(
            'overall_improvement', 0) > 0 else 'needs_attention',
            'improvement_rate': progress_data.get('overall_improvement', 0),
            'milestone_completion': len(progress_data.get(
            'milestones_achieved', [])), 'projected_outcomes': self.
            _project_outcomes(progress_data)}

    def _determine_performance_level(self, average_score: float) ->str:
        _('services_ai_report_service.message.determine_performance_level_ba')
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

    def _calculate_consistency(self, assessment_data: Dict[str, Any]) ->float:
        """Calculate consistency score from assessment data."""
        recent_assessments = assessment_data.get('recent_assessments', [])
        if len(recent_assessments) < 2:
            return 0.0
        scores = [a['score'] for a in recent_assessments if a.get('score')
             is not None]
        if len(scores) < 2:
            return 0.0
        avg = sum(scores) / len(scores)
        variance = sum((x - avg) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        consistency = max(0, 100 - std_dev * 2)
        return round(consistency, 2)

    def _identify_peak_performance(self, assessment_data: Dict[str, Any]
        ) ->Dict[str, Any]:
        """Identify peak performance from assessments."""
        recent_assessments = assessment_data.get('recent_assessments', [])
        if not recent_assessments:
            return {'score': 0, 'date': None}
        best = max(recent_assessments, key=lambda x: x.get('score', 0))
        return {'score': best.get('score', 0), 'date': best.get(
            'completed_at'), 'assessment': best.get('evaluation_title')}

    def _calculate_engagement_score(self, data: Dict[str, Any]) ->float:
        _('services_ai_report_service.message.calculate_overall_engagement_s')
        factors = []
        attendance_rate = data.get('appointments', {}).get('attendance_rate', 0
            )
        factors.append(attendance_rate)
        assessment_data = data.get('assessments', {})
        if assessment_data.get('total_assessments', 0) > 0:
            completion_rate = assessment_data.get('completed_assessments', 0
                ) / assessment_data.get('total_assessments', 1) * 100
            factors.append(completion_rate)
        doc_count = data.get('documents', {}).get('total_documents', 0)
        doc_factor = min(100, doc_count * 10)
        factors.append(doc_factor)
        engagement_score = sum(factors) / len(factors) if factors else 0
        return round(engagement_score, 2)

    def _determine_participation_level(self, appointment_data: Dict[str, Any]
        ) ->str:
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

    def _calculate_attendance_consistency(self, appointment_data: Dict[str,
        Any]) ->str:
        _('services_ai_report_service.message.calculate_attendance_consisten')
        completed = appointment_data.get('completed_appointments', 0)
        cancelled = appointment_data.get('cancelled_appointments', 0)
        total = appointment_data.get('total_appointments', 0)
        if total == 0:
            return 'no_data'
        consistency_score = completed / total * 100
        if consistency_score >= 90:
            return 'excellent'
        elif consistency_score >= 75:
            return 'good'
        elif consistency_score >= 50:
            return 'fair'
        else:
            return 'poor'

    def _project_outcomes(self, progress_data: Dict[str, Any]) ->Dict[str, Any
        ]:
        _('services_ai_report_service.message.project_future_outcomes_based')
        improvement_rate = progress_data.get('overall_improvement', 0)
        projected_3_months = improvement_rate * 1.5
        projected_6_months = improvement_rate * 2.5
        return {_('services_ai_report_service.message.3_month_projection'):
            round(projected_3_months, 2), _(
            'services_ai_report_service.message.6_month_projection'): round
            (projected_6_months, 2), 'confidence_level': 'high' if 
            improvement_rate > 10 else 'moderate'}

    def _calculate_engagement_level(self, data: Dict[str, Any]) ->float:
        """Calculate engagement level from various data points."""
        return self._calculate_engagement_score(data)

    def _generate_progress_recommendations(self, data: Dict[str, Any]) ->List[
        str]:
        _('services_ai_report_service.label.generate_progress_specific_rec')
        recommendations = []
        progress_data = data.get('progress', {})
        improvement = progress_data.get('overall_improvement', 0)
        if improvement < 5:
            recommendations.append(_(
                'services_ai_report_service.message.consider_adjusting_learning_ap'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.schedule_additional_support_se'
                ))
        elif improvement < 15:
            recommendations.append(_(
                'services_ai_report_service.message.maintain_current_learning_pace'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.introduce_advanced_topics_to_s'
                ))
        else:
            recommendations.append(_(
                'services_ai_report_service.message.excellent_progress_consider'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.explore_specialized_advanced_t'
                ))
        attendance_rate = data.get('appointments', {}).get('attendance_rate', 0
            )
        if attendance_rate < 70:
            recommendations.append(_(
                'services_ai_report_service.message.improve_attendance_to_maximize'
                ))
        return recommendations

    def _identify_assessment_strengths(self, assessment_data: Dict[str, Any]
        ) ->List[str]:
        """Identify strengths from assessment data."""
        strengths = []
        avg_score = assessment_data.get('average_score', 0)
        if avg_score >= 80:
            strengths.append(_(
                'services_ai_report_service.message.consistently_high_performance'
                ))
        if assessment_data.get('score_trend') == 'improving':
            strengths.append(_(
                'services_ai_report_service.label.demonstrating_continuous_impro'
                ))
        completed = assessment_data.get('completed_assessments', 0)
        total = assessment_data.get('total_assessments', 0)
        if total > 0 and completed / total >= 0.9:
            strengths.append(_(
                'services_ai_report_service.message.excellent_assessment_completio'
                ))
        return strengths if strengths else [_(
            'services_ai_report_service.label.building_foundational_skills')]

    def _identify_improvement_areas(self, assessment_data: Dict[str, Any]
        ) ->List[str]:
        """Identify areas for improvement from assessment data."""
        areas = []
        avg_score = assessment_data.get('average_score', 0)
        if avg_score < 70:
            areas.append(_(
                'services_ai_report_service.message.focus_on_improving_overall_ass'
                ))
        if assessment_data.get('score_trend') == 'declining':
            areas.append(_(
                'services_ai_report_service.message.address_factors_contributing_t'
                ))
        recent = assessment_data.get('recent_assessments', [])
        if len(recent) >= 3:
            scores = [a['score'] for a in recent if a.get('score') is not None]
            if scores and max(scores) - min(scores) > 20:
                areas.append(_(
                    'services_ai_report_service.message.work_on_maintaining_consistent'
                    ))
        return areas if areas else [_(
            'services_ai_report_service.message.continue_building_on_current_p'
            )]

    def _calculate_score_distribution(self, assessment_data: Dict[str, Any]
        ) ->Dict[str, int]:
        _('services_ai_report_service.message.calculate_distribution_of_asse')
        distribution = {'excellent': 0, 'very_good': 0, 'good': 0, 'fair': 
            0, 'needs_improvement': 0}
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

    def _generate_assessment_recommendations(self, assessment_data: Dict[
        str, Any]) ->List[str]:
        _('services_ai_report_service.label.generate_assessment_specific_r')
        recommendations = []
        avg_score = assessment_data.get('average_score', 0)
        trend = assessment_data.get('score_trend', 'stable')
        if avg_score < 60:
            recommendations.append(_(
                'services_ai_report_service.message.provide_additional_study_mater'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.consider_reassessing_learning'
                ))
        elif avg_score < 70:
            recommendations.append(_(
                'services_ai_report_service.message.focus_on_strengthening_weak_ar'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.implement_targeted_practice_se'
                ))
        elif avg_score < 80:
            recommendations.append(_(
                'services_ai_report_service.message.continue_current_approach_with'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.introduce_more_challenging_ass'
                ))
        else:
            recommendations.append(_(
                'services_ai_report_service.message.maintain_excellence_with_advan'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.consider_peer_tutoring_opportu'
                ))
        if trend == 'declining':
            recommendations.append(_(
                'services_ai_report_service.message.investigate_causes_of_performa'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.provide_additional_motivation'
                ))
        elif trend == 'improving':
            recommendations.append(_(
                'services_ai_report_service.message.recognize_and_celebrate_improv'
                ))
            recommendations.append(_(
                'services_ai_report_service.message.maintain_current_strategies_th'
                ))
        return recommendations

    def _generate_program_insights(self, program: Program, analytics: Dict[
        str, Any], beneficiary_data: List[Dict[str, Any]]) ->Dict[str, Any]:
        _('services_ai_report_service.message.generate_ai_insights_for_progr')
        total_beneficiaries = len(beneficiary_data)
        avg_scores = []
        attendance_rates = []
        for bd in beneficiary_data:
            data = bd['data']
            if 'assessments' in data:
                avg_scores.append(data['assessments'].get('average_score', 0))
            if 'appointments' in data:
                attendance_rates.append(data['appointments'].get(
                    'attendance_rate', 0))
        program_avg_score = sum(avg_scores) / len(avg_scores
            ) if avg_scores else 0
        program_attendance = sum(attendance_rates) / len(attendance_rates
            ) if attendance_rates else 0
        return {'overall_performance': self._determine_performance_level(
            program_avg_score), 'engagement_level': self.
            _determine_participation_level({'attendance_rate':
            program_attendance}), 'key_insights': [
            f'Program has {total_beneficiaries} active beneficiaries',
            f'Average performance score: {round(program_avg_score, 2)}%',
            f'Average attendance rate: {round(program_attendance, 2)}%',
            f"Program completion rate: {analytics.get('completion_rate', 0)}%"
            ], 'success_factors': self._identify_program_success_factors(
            analytics, beneficiary_data), 'risk_factors': self.
            _identify_program_risk_factors(analytics, beneficiary_data)}

    def _summarize_beneficiaries(self, beneficiary_data: List[Dict[str, Any]]
        ) ->List[Dict[str, Any]]:
        _('services_ai_report_service.message.create_summaries_for_each_bene')
        summaries = []
        for bd in beneficiary_data:
            beneficiary = bd['beneficiary']
            data = bd['data']
            summary = {'beneficiary_id': beneficiary.id, 'name':
                f'{beneficiary.user.first_name} {beneficiary.user.last_name}',
                'performance_score': data.get('assessments', {}).get(
                'average_score', 0), 'attendance_rate': data.get(
                'appointments', {}).get('attendance_rate', 0),
                'progress_trend': data.get('assessments', {}).get(
                'score_trend', 'unknown'), 'engagement_level': self.
                _calculate_engagement_level(data), 'risk_level': self.
                _assess_beneficiary_risk(data)}
            summaries.append(summary)
        summaries.sort(key=lambda x: x['performance_score'], reverse=True)
        return summaries

    def _generate_program_recommendations(self, program: Program, analytics:
        Dict[str, Any], insights: Dict[str, Any]) ->List[Dict[str, Any]]:
        _('services_ai_report_service.message.generate_recommendations_for_p')
        recommendations = []
        if insights['overall_performance'] in ['needs_improvement',
            'satisfactory']:
            recommendations.append({'priority': 'high', 'category':
                'performance', 'recommendation':
                'Review and update curriculum to address performance gaps',
                'rationale': _(
                'services_ai_report_service.message.overall_program_performance_is'
                )})
        if insights['engagement_level'] in ['low', 'moderate']:
            recommendations.append({'priority': 'high', 'category':
                'engagement', 'recommendation': _(
                'services_ai_report_service.message.implement_engagement_improveme'
                ), 'rationale': _(
                'services_ai_report_service.message.low_engagement_levels_may_impa'
                )})
        for risk in insights.get('risk_factors', []):
            recommendations.append({'priority': 'medium', 'category':
                'risk_mitigation', 'recommendation':
                f'Address risk: {risk}', 'rationale': _(
                'services_ai_report_service.success.proactive_risk_management_impr'
                )})
        return recommendations

    def _identify_program_success_factors(self, analytics: Dict[str, Any],
        beneficiary_data: List[Dict[str, Any]]) ->List[str]:
        _('services_ai_report_service.success.identify_factors_contributing')
        factors = []
        if analytics.get('completion_rate', 0) > 80:
            factors.append(_(
                'services_ai_report_service.message.high_program_completion_rate'
                ))
        high_performers = sum(1 for bd in beneficiary_data if bd['data'].
            get('assessments', {}).get('average_score', 0) > 80)
        if high_performers / len(beneficiary_data) > 0.5:
            factors.append(_(
                'services_ai_report_service.message.majority_of_beneficiaries_perf'
                ))
        return factors

    def _identify_program_risk_factors(self, analytics: Dict[str, Any],
        beneficiary_data: List[Dict[str, Any]]) ->List[str]:
        _('services_ai_report_service.message.identify_risk_factors_for_prog')
        risks = []
        low_attendance = sum(1 for bd in beneficiary_data if bd['data'].get
            ('appointments', {}).get('attendance_rate', 0) < 70)
        if low_attendance / len(beneficiary_data) > 0.3:
            risks.append(_(
                'services_ai_report_service.message.significant_portion_of_benefic'
                ))
        declining = sum(1 for bd in beneficiary_data if bd['data'].get(
            'assessments', {}).get('score_trend') == 'declining')
        if declining / len(beneficiary_data) > 0.2:
            risks.append(_(
                'services_ai_report_service.message.multiple_beneficiaries_showing'
                ))
        return risks

    def _assess_beneficiary_risk(self, data: Dict[str, Any]) ->str:
        _('services_ai_report_service.message.assess_risk_level_for_a_benefi')
        risk_score = 0
        if data.get('appointments', {}).get('attendance_rate', 100) < 70:
            risk_score += 2
        if data.get('assessments', {}).get('average_score', 100) < 60:
            risk_score += 2
        if data.get('assessments', {}).get('score_trend') == 'declining':
            risk_score += 1
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'

    def _gather_comparison_metrics(self, beneficiary_id: int, metrics: List
        [str]) ->Dict[str, Any]:
        _('services_ai_report_service.message.gather_specific_metrics_for_co')
        data = {}
        if 'assessment_scores' in metrics:
            sessions = TestSession.query.filter_by(beneficiary_id=
                beneficiary_id, status='completed').all()
            scores = [s.score for s in sessions if s.score is not None]
            data['assessment_scores'] = {'average': sum(scores) / len(
                scores) if scores else 0, 'highest': max(scores) if scores else
                0, 'lowest': min(scores) if scores else 0, 'count': len(scores)
                }
        if 'attendance_rate' in metrics:
            appointments = Appointment.query.filter_by(beneficiary_id=
                beneficiary_id).all()
            total = len(appointments)
            completed = len([a for a in appointments if a.status ==
                'completed'])
            data['attendance_rate'
                ] = completed / total * 100 if total > 0 else 0
        if 'progress_rate' in metrics:
            early_sessions = TestSession.query.filter_by(beneficiary_id=
                beneficiary_id, status='completed').order_by(TestSession.
                submitted_at).limit(3).all()
            recent_sessions = TestSession.query.filter_by(beneficiary_id=
                beneficiary_id, status='completed').order_by(desc(
                TestSession.submitted_at)).limit(3).all()
            early_avg = sum(s.score for s in early_sessions if s.score) / len(
                early_sessions) if early_sessions else 0
            recent_avg = sum(s.score for s in recent_sessions if s.score
                ) / len(recent_sessions) if recent_sessions else 0
            data['progress_rate'] = (recent_avg - early_avg
                ) / early_avg * 100 if early_avg > 0 else 0
        if 'engagement_level' in metrics:
            all_data = self._gather_beneficiary_data(beneficiary_id, 
                datetime.utcnow() - timedelta(days=90), datetime.utcnow(),
                ['appointments', 'assessments', 'documents'])
            data['engagement_level'] = self._calculate_engagement_level(
                all_data)
        if 'completion_rate' in metrics:
            total_assessments = TestSession.query.filter_by(beneficiary_id=
                beneficiary_id).count()
            completed_assessments = TestSession.query.filter_by(beneficiary_id
                =beneficiary_id, status='completed').count()
            data['completion_rate'] = (completed_assessments /
                total_assessments * 100 if total_assessments > 0 else 0)
        return data

    def _generate_comparative_insights(self, comparison_data: Dict[int,
        Dict[str, Any]], metrics: List[str]) ->Dict[str, Any]:
        """Generate insights from comparative data."""
        insights = {'top_performers': {}, 'areas_of_concern': [],
            'interesting_patterns': [], 'recommendations_by_beneficiary': {}}
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
                insights['top_performers'][metric] = {'beneficiary_id':
                    scores[0][0], 'value': scores[0][1]}
        for ben_id, data in comparison_data.items():
            concerns = []
            if 'attendance_rate' in data['metrics'] and data['metrics'][
                'attendance_rate'] < 70:
                concerns.append(
                    f"Low attendance rate: {data['metrics']['attendance_rate']:.1f}%"
                    )
            if 'assessment_scores' in data['metrics'] and data['metrics'][
                'assessment_scores']['average'] < 60:
                concerns.append(
                    f"Low average score: {data['metrics']['assessment_scores']['average']:.1f}%"
                    )
            if concerns:
                insights['areas_of_concern'].append({'beneficiary_id':
                    ben_id, 'concerns': concerns})
        if len(comparison_data) > 2:
            attendance_values = []
            score_values = []
            for data in comparison_data.values():
                if 'attendance_rate' in data['metrics'
                    ] and 'assessment_scores' in data['metrics']:
                    attendance_values.append(data['metrics']['attendance_rate']
                        )
                    score_values.append(data['metrics']['assessment_scores'
                        ]['average'])
            if attendance_values and score_values:
                avg_attendance = sum(attendance_values) / len(attendance_values
                    )
                avg_scores = sum(score_values) / len(score_values)
                high_attendance_high_scores = sum(1 for i in range(len(
                    attendance_values)) if attendance_values[i] >
                    avg_attendance and score_values[i] > avg_scores)
                if high_attendance_high_scores / len(attendance_values) > 0.6:
                    insights['interesting_patterns'].append(_(
                        'services_ai_report_service.message.strong_correlation_between_att'
                        ))
        for ben_id, data in comparison_data.items():
            recommendations = []
            metrics_data = data['metrics']
            if 'attendance_rate' in metrics_data and metrics_data[
                'attendance_rate'] < 80:
                recommendations.append(_(
                    'services_ai_report_service.message.focus_on_improving_attendance'
                    ))
            if 'progress_rate' in metrics_data and metrics_data['progress_rate'
                ] < 5:
                recommendations.append(_(
                    'services_ai_report_service.message.implement_strategies_to_accele'
                    ))
            insights['recommendations_by_beneficiary'][ben_id
                ] = recommendations
        return insights

    def _create_comparison_summary(self, comparison_data: Dict[int, Dict[
        str, Any]]) ->Dict[str, Any]:
        _('services_ai_report_service.message.create_summary_of_comparison_d')
        summary = {'total_beneficiaries': len(comparison_data),
            'date_generated': datetime.utcnow().isoformat(),
            'beneficiaries': []}
        for ben_id, data in comparison_data.items():
            beneficiary = data['beneficiary']
            summary['beneficiaries'].append({'id': ben_id, 'name':
                f'{beneficiary.user.first_name} {beneficiary.user.last_name}',
                'enrollment_date': beneficiary.enrollment_date.isoformat() if
                beneficiary.enrollment_date else None})
        return summary

    def _create_metric_comparisons(self, comparison_data: Dict[int, Dict[
        str, Any]], metrics: List[str]) ->Dict[str, Any]:
        _('services_ai_report_service.message.create_detailed_metric_compari')
        comparisons = {}
        for metric in metrics:
            metric_data = []
            for ben_id, data in comparison_data.items():
                if metric in data['metrics']:
                    value = data['metrics'][metric]
                    if isinstance(value, dict):
                        metric_data.append({'beneficiary_id': ben_id,
                            'values': value})
                    else:
                        metric_data.append({'beneficiary_id': ben_id,
                            'value': value})
            if metric_data:
                comparisons[metric] = {'data': metric_data, 'average': self
                    ._calculate_metric_average(metric_data), 'highest':
                    self._find_metric_highest(metric_data), 'lowest': self.
                    _find_metric_lowest(metric_data)}
        return comparisons

    def _create_rankings(self, comparison_data: Dict[int, Dict[str, Any]],
        metrics: List[str]) ->Dict[str, List[Dict[str, Any]]]:
        _('services_ai_report_service.message.create_rankings_for_each_metri')
        rankings = {}
        for metric in metrics:
            ranking = []
            for ben_id, data in comparison_data.items():
                if metric in data['metrics']:
                    value = data['metrics'][metric]
                    if isinstance(value, dict):
                        value = value.get('average', 0)
                    ranking.append({'beneficiary_id': ben_id, 'rank': 0,
                        'value': value})
            ranking.sort(key=lambda x: x['value'], reverse=True)
            for i, item in enumerate(ranking):
                item['rank'] = i + 1
            rankings[metric] = ranking
        return rankings

    def _generate_comparative_recommendations(self, comparison_data: Dict[
        int, Dict[str, Any]], insights: Dict[str, Any]) ->List[str]:
        _('services_ai_report_service.message.generate_recommendations_based')
        recommendations = []
        if 'assessment_scores' in insights.get('top_performers', {}):
            recommendations.append(_(
                'services_ai_report_service.message.consider_peer_mentoring_betwee'
                ))
        if len(insights.get('areas_of_concern', [])) > len(comparison_data
            ) * 0.5:
            recommendations.append(_(
                'services_ai_report_service.message.review_program_structure_as_ma'
                ))
        for pattern in insights.get('interesting_patterns', []):
            if 'correlation' in pattern.lower():
                recommendations.append(_(
                    'services_ai_report_service.message.leverage_identified_correlatio'
                    ))
        return recommendations

    def _calculate_metric_average(self, metric_data: List[Dict[str, Any]]
        ) ->float:
        _('services_ai_report_service.message.calculate_average_for_a_metric')
        values = []
        for item in metric_data:
            if 'value' in item:
                values.append(item['value'])
            elif 'values' in item and 'average' in item['values']:
                values.append(item['values']['average'])
        return sum(values) / len(values) if values else 0

    def _find_metric_highest(self, metric_data: List[Dict[str, Any]]) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.find_highest_value_for_a_metri')
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

    def _find_metric_lowest(self, metric_data: List[Dict[str, Any]]) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.find_lowest_value_for_a_metric')
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

    def _ai_synthesize_data(self, beneficiary: Beneficiary, source_data:
        Dict[str, Any]) ->Dict[str, Any]:
        """Use AI to synthesize insights from multiple data sources."""
        context = self._prepare_synthesis_context(beneficiary, source_data)
        if self.api_key:
            synthesis = self._call_synthesis_api(context)
        else:
            synthesis = self._generate_mock_synthesis(source_data)
        return synthesis

    def _prepare_synthesis_context(self, beneficiary: Beneficiary,
        source_data: Dict[str, Any]) ->str:
        _('services_ai_report_service.message.prepare_context_for_ai_synthes')
        context_parts = [
            f'Beneficiary: {beneficiary.user.first_name} {beneficiary.user.last_name}'
            , f'Status: {beneficiary.status}', '']
        for source, data in source_data.items():
            if source == 'assessments':
                context_parts.append(f'Assessment Data:')
                context_parts.append(
                    f"- Total: {data.get('total_assessments', 0)}")
                context_parts.append(
                    f"- Average Score: {data.get('average_score', 0)}%")
                context_parts.append(
                    f"- Trend: {data.get('score_trend', 'unknown')}")
            elif source == 'appointments':
                context_parts.append(f'Appointment Data:')
                context_parts.append(
                    f"- Attendance Rate: {data.get('attendance_rate', 0)}%")
                context_parts.append(
                    f"- Total: {data.get('total_appointments', 0)}")
            elif source == 'documents':
                context_parts.append(f'Document Data:')
                context_parts.append(
                    f"- Total Documents: {data.get('total_documents', 0)}")
                context_parts.append(
                    f"- Types: {', '.join(data.get('document_types', {}).keys())}"
                    )
            elif source == 'notes':
                context_parts.append(f'Notes Data:')
                context_parts.append(
                    f"- Total Notes: {data.get('total_notes', 0)}")
            elif source == 'programs':
                context_parts.append(f'Program Data:')
                context_parts.append(f'- Active Programs: {len(data)}')
            context_parts.append('')
        return '\n'.join(context_parts)

    def _call_synthesis_api(self, context: str) ->Dict[str, Any]:
        _('services_ai_report_service.message.call_ai_api_for_data_synthesis')
        return self._generate_mock_synthesis({})

    def _generate_mock_synthesis(self, source_data: Dict[str, Any]) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.generate_mock_synthesis_when_a')
        return {'insights': [_(
            'services_ai_report_service.message.beneficiary_shows_consistent_e'
            ), _(
            'services_ai_report_service.message.performance_metrics_indicate_s'
            ), _(
            'services_ai_report_service.message.documentation_and_notes_sugges'
            ), _(
            'services_ai_report_service.message.cross_source_analysis_reveals'
            )], 'patterns': [{'pattern': _(
            'services_ai_report_service.label.engagement_consistency'),
            'description': _(
            'services_ai_report_service.message.regular_participation_across_a'
            ), 'impact': 'positive'}, {'pattern': _(
            'services_ai_report_service.label.performance_trajectory'),
            'description': _(
            'services_ai_report_service.message.gradual_improvement_trend_acro'
            ), 'impact': 'positive'}], 'timeline': {'recent_activity': _(
            'services_ai_report_service.message.high_activity_in_the_last_30_d'
            ), 'peak_periods': [_(
            'services_ai_report_service.label.morning_sessions'), _(
            'services_ai_report_service.label.mid_week_appointments')],
            'quiet_periods': [_(
            'services_ai_report_service.message.weekend_activities_show_lower'
            )]}, 'recommendations': [_(
            'services_ai_report_service.message.maintain_current_engagement_le'
            ), _(
            'services_ai_report_service.message.schedule_regular_check_ins_dur'
            ), _(
            'services_ai_report_service.message.consider_peer_learning_opportu'
            ), _(
            'services_ai_report_service.success.document_successful_strategies'
            )]}

    def _create_source_summaries(self, source_data: Dict[str, Any]) ->Dict[
        str, Any]:
        _('services_ai_report_service.message.create_summaries_for_each_data')
        summaries = {}
        for source, data in source_data.items():
            if source == 'assessments':
                summaries[source] = {'key_metric':
                    f"{data.get('average_score', 0):.1f}% average score",
                    'trend': data.get('score_trend', 'unknown'), 'volume':
                    f"{data.get('total_assessments', 0)} assessments"}
            elif source == 'appointments':
                summaries[source] = {'key_metric':
                    f"{data.get('attendance_rate', 0):.1f}% attendance",
                    'volume':
                    f"{data.get('total_appointments', 0)} appointments"}
            elif source == 'documents':
                summaries[source] = {'volume':
                    f"{data.get('total_documents', 0)} documents", 'types':
                    list(data.get('document_types', {}).keys())}
            elif source == 'notes':
                summaries[source] = {'volume':
                    f"{data.get('total_notes', 0)} notes"}
            elif source == 'programs':
                summaries[source] = {'active': len([p for p in data if p[
                    'status'] == 'active']), 'total': len(data)}
        return summaries

    def _generate_action_items(self, synthesis: Dict[str, Any]) ->List[Dict
        [str, Any]]:
        """Generate actionable items from synthesis."""
        action_items = []
        for i, rec in enumerate(synthesis.get('recommendations', [])):
            priority = 'high' if i < 2 else 'medium'
            action_items.append({'priority': priority, 'action': rec,
                'timeline': _('ai_recommendations.message.2_weeks') if 
                priority == 'high' else _(
                'services_ai_report_service.message.1_month'), 'category':
                self._categorize_action(rec)})
        return action_items

    def _categorize_action(self, action: str) ->str:
        _('services_ai_report_service.message.categorize_an_action_item')
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


ai_report_service = AIReportService()
