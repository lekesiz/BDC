"""Analytics service for generating metrics and insights."""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session

from app.extensions import db
from app.models import (
    Beneficiary, Program, Appointment, TestSession, 
    Document, User
)


class AnalyticsService:
    """Service for generating analytics and metrics."""
    
    def get_program_analytics(
        self,
        program_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics for a program.
        
        Args:
            program_id: ID of the program
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dictionary containing program analytics
        """
        program = Program.query.get(program_id)
        if not program:
            return {}
        
        # Default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get beneficiaries in program
        beneficiary_ids = [b.id for b in program.beneficiaries]
        
        # Calculate metrics
        analytics = {
            'program_id': program_id,
            'program_name': program.name,
            'total_beneficiaries': len(beneficiary_ids),
            'active_beneficiaries': self._count_active_beneficiaries(beneficiary_ids, start_date, end_date),
            'completion_rate': self._calculate_program_completion_rate(program),
            'average_attendance': self._calculate_average_attendance(beneficiary_ids, start_date, end_date),
            'average_performance': self._calculate_average_performance(beneficiary_ids, start_date, end_date),
            'engagement_metrics': self._calculate_engagement_metrics(beneficiary_ids, start_date, end_date),
            'progress_summary': self._generate_progress_summary(beneficiary_ids, start_date, end_date)
        }
        
        return analytics
    
    def get_beneficiary_analytics(
        self,
        beneficiary_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics for a beneficiary.
        
        Args:
            beneficiary_id: ID of the beneficiary
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dictionary containing beneficiary analytics
        """
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            return {}
        
        # Default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        analytics = {
            'beneficiary_id': beneficiary_id,
            'attendance_rate': self._calculate_attendance_rate(beneficiary_id, start_date, end_date),
            'assessment_performance': self._get_assessment_performance(beneficiary_id, start_date, end_date),
            'engagement_score': self._calculate_engagement_score(beneficiary_id, start_date, end_date),
            'progress_metrics': self._calculate_progress_metrics(beneficiary_id, start_date, end_date),
            'activity_summary': self._get_activity_summary(beneficiary_id, start_date, end_date)
        }
        
        return analytics
    
    def get_trainer_analytics(
        self,
        trainer_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get analytics for a trainer.
        
        Args:
            trainer_id: ID of the trainer
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Dictionary containing trainer analytics
        """
        trainer = User.query.get(trainer_id)
        if not trainer or trainer.role not in ['trainer', 'tenant_admin', 'super_admin']:
            return {}
        
        # Default date range if not provided
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get appointments for trainer
        appointments = Appointment.query.filter(
            and_(
                Appointment.trainer_id == trainer_id,
                Appointment.start_time.between(start_date, end_date)
            )
        ).all()
        
        # Get beneficiaries trained
        beneficiary_ids = list(set([a.beneficiary_id for a in appointments]))
        
        analytics = {
            'trainer_id': trainer_id,
            'trainer_name': f"{trainer.first_name} {trainer.last_name}",
            'total_appointments': len(appointments),
            'completed_appointments': len([a for a in appointments if a.status == 'completed']),
            'cancelled_appointments': len([a for a in appointments if a.status == 'cancelled']),
            'unique_beneficiaries': len(beneficiary_ids),
            'appointment_completion_rate': self._calculate_trainer_completion_rate(appointments),
            'beneficiary_performance': self._get_trainer_beneficiary_performance(beneficiary_ids, start_date, end_date)
        }
        
        return analytics
    
    # Private helper methods
    
    def _count_active_beneficiaries(
        self,
        beneficiary_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Count beneficiaries who were active in the given period."""
        active_count = 0
        
        for ben_id in beneficiary_ids:
            # Check if beneficiary had any activity
            has_appointment = Appointment.query.filter(
                and_(
                    Appointment.beneficiary_id == ben_id,
                    Appointment.start_time.between(start_date, end_date),
                    Appointment.status.in_(['completed', 'scheduled'])
                )
            ).first() is not None
            
            has_assessment = TestSession.query.filter(
                and_(
                    TestSession.beneficiary_id == ben_id,
                    TestSession.created_at.between(start_date, end_date)
                )
            ).first() is not None
            
            if has_appointment or has_assessment:
                active_count += 1
        
        return active_count
    
    def _calculate_program_completion_rate(self, program: Program) -> float:
        """Calculate completion rate for a program."""
        if not program.beneficiaries:
            return 0.0
        
        # For now, consider a beneficiary completed if they have status 'completed'
        # In a real implementation, this would check module completion, etc.
        completed = len([b for b in program.beneficiaries if b.status == 'completed'])
        total = len(program.beneficiaries)
        
        return round((completed / total * 100) if total > 0 else 0, 2)
    
    def _calculate_average_attendance(
        self,
        beneficiary_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate average attendance rate for beneficiaries."""
        if not beneficiary_ids:
            return 0.0
        
        attendance_rates = []
        for ben_id in beneficiary_ids:
            rate = self._calculate_attendance_rate(ben_id, start_date, end_date)
            attendance_rates.append(rate)
        
        return round(sum(attendance_rates) / len(attendance_rates) if attendance_rates else 0, 2)
    
    def _calculate_average_performance(
        self,
        beneficiary_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate average performance score for beneficiaries."""
        if not beneficiary_ids:
            return 0.0
        
        all_scores = []
        for ben_id in beneficiary_ids:
            performance = self._get_assessment_performance(ben_id, start_date, end_date)
            if performance.get('average_score'):
                all_scores.append(performance['average_score'])
        
        return round(sum(all_scores) / len(all_scores) if all_scores else 0, 2)
    
    def _calculate_engagement_metrics(
        self,
        beneficiary_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate engagement metrics for beneficiaries."""
        total_appointments = 0
        total_assessments = 0
        total_documents = 0
        
        for ben_id in beneficiary_ids:
            appointments = Appointment.query.filter(
                and_(
                    Appointment.beneficiary_id == ben_id,
                    Appointment.start_time.between(start_date, end_date)
                )
            ).count()
            total_appointments += appointments
            
            assessments = TestSession.query.filter(
                and_(
                    TestSession.beneficiary_id == ben_id,
                    TestSession.created_at.between(start_date, end_date)
                )
            ).count()
            total_assessments += assessments
            
            documents = Document.query.filter(
                and_(
                    Document.beneficiary_id == ben_id,
                    Document.created_at.between(start_date, end_date)
                )
            ).count()
            total_documents += documents
        
        return {
            'total_appointments': total_appointments,
            'total_assessments': total_assessments,
            'total_documents': total_documents,
            'average_per_beneficiary': {
                'appointments': round(total_appointments / len(beneficiary_ids) if beneficiary_ids else 0, 2),
                'assessments': round(total_assessments / len(beneficiary_ids) if beneficiary_ids else 0, 2),
                'documents': round(total_documents / len(beneficiary_ids) if beneficiary_ids else 0, 2)
            }
        }
    
    def _generate_progress_summary(
        self,
        beneficiary_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate progress summary for beneficiaries."""
        improving = 0
        stable = 0
        declining = 0
        
        for ben_id in beneficiary_ids:
            progress = self._calculate_progress_metrics(ben_id, start_date, end_date)
            trend = progress.get('trend', 'stable')
            
            if trend == 'improving':
                improving += 1
            elif trend == 'declining':
                declining += 1
            else:
                stable += 1
        
        total = len(beneficiary_ids)
        
        return {
            'improving': improving,
            'stable': stable,
            'declining': declining,
            'percentages': {
                'improving': round(improving / total * 100 if total > 0 else 0, 2),
                'stable': round(stable / total * 100 if total > 0 else 0, 2),
                'declining': round(declining / total * 100 if total > 0 else 0, 2)
            }
        }
    
    def _calculate_attendance_rate(
        self,
        beneficiary_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate attendance rate for a beneficiary."""
        appointments = Appointment.query.filter(
            and_(
                Appointment.beneficiary_id == beneficiary_id,
                Appointment.start_time.between(start_date, end_date)
            )
        ).all()
        
        if not appointments:
            return 0.0
        
        completed = len([a for a in appointments if a.status == 'completed'])
        total = len(appointments)
        
        return round((completed / total * 100) if total > 0 else 0, 2)
    
    def _get_assessment_performance(
        self,
        beneficiary_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get assessment performance metrics."""
        sessions = TestSession.query.filter(
            and_(
                TestSession.beneficiary_id == beneficiary_id,
                TestSession.created_at.between(start_date, end_date),
                TestSession.status == 'completed'
            )
        ).all()
        
        if not sessions:
            return {
                'total_assessments': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0
            }
        
        scores = [s.score for s in sessions if s.score is not None]
        
        return {
            'total_assessments': len(sessions),
            'average_score': round(sum(scores) / len(scores) if scores else 0, 2),
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0
        }
    
    def _calculate_engagement_score(
        self,
        beneficiary_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Calculate engagement score for a beneficiary."""
        # Get activity counts
        appointment_count = Appointment.query.filter(
            and_(
                Appointment.beneficiary_id == beneficiary_id,
                Appointment.start_time.between(start_date, end_date),
                Appointment.status == 'completed'
            )
        ).count()
        
        assessment_count = TestSession.query.filter(
            and_(
                TestSession.beneficiary_id == beneficiary_id,
                TestSession.created_at.between(start_date, end_date),
                TestSession.status == 'completed'
            )
        ).count()
        
        document_count = Document.query.filter(
            and_(
                Document.beneficiary_id == beneficiary_id,
                Document.created_at.between(start_date, end_date)
            )
        ).count()
        
        # Calculate engagement score (weighted average)
        # Appointments: 40%, Assessments: 40%, Documents: 20%
        days_in_period = (end_date - start_date).days or 1
        
        appointment_score = min(100, (appointment_count / (days_in_period / 7)) * 100)  # Weekly expectation
        assessment_score = min(100, (assessment_count / (days_in_period / 30)) * 100)  # Monthly expectation
        document_score = min(100, document_count * 20)  # Up to 5 documents = 100%
        
        engagement_score = (
            appointment_score * 0.4 +
            assessment_score * 0.4 +
            document_score * 0.2
        )
        
        return round(engagement_score, 2)
    
    def _calculate_progress_metrics(
        self,
        beneficiary_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate progress metrics for a beneficiary."""
        # Get assessments in chronological order
        sessions = TestSession.query.filter(
            and_(
                TestSession.beneficiary_id == beneficiary_id,
                TestSession.created_at.between(start_date, end_date),
                TestSession.status == 'completed',
                TestSession.score.isnot(None)
            )
        ).order_by(TestSession.created_at).all()
        
        if len(sessions) < 2:
            return {
                'trend': 'insufficient_data',
                'improvement_rate': 0,
                'consistency': 0
            }
        
        # Calculate trend
        first_half = sessions[:len(sessions)//2]
        second_half = sessions[len(sessions)//2:]
        
        first_avg = sum(s.score for s in first_half) / len(first_half)
        second_avg = sum(s.score for s in second_half) / len(second_half)
        
        improvement_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        # Determine trend
        if improvement_rate > 5:
            trend = 'improving'
        elif improvement_rate < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Calculate consistency (standard deviation)
        scores = [s.score for s in sessions]
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        consistency = max(0, 100 - (std_dev * 2))  # Lower std_dev = higher consistency
        
        return {
            'trend': trend,
            'improvement_rate': round(improvement_rate, 2),
            'consistency': round(consistency, 2)
        }
    
    def _get_activity_summary(
        self,
        beneficiary_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get activity summary for a beneficiary."""
        return {
            'appointments': {
                'total': Appointment.query.filter(
                    and_(
                        Appointment.beneficiary_id == beneficiary_id,
                        Appointment.start_time.between(start_date, end_date)
                    )
                ).count(),
                'completed': Appointment.query.filter(
                    and_(
                        Appointment.beneficiary_id == beneficiary_id,
                        Appointment.start_time.between(start_date, end_date),
                        Appointment.status == 'completed'
                    )
                ).count()
            },
            'assessments': {
                'total': TestSession.query.filter(
                    and_(
                        TestSession.beneficiary_id == beneficiary_id,
                        TestSession.created_at.between(start_date, end_date)
                    )
                ).count(),
                'completed': TestSession.query.filter(
                    and_(
                        TestSession.beneficiary_id == beneficiary_id,
                        TestSession.created_at.between(start_date, end_date),
                        TestSession.status == 'completed'
                    )
                ).count()
            },
            'documents': Document.query.filter(
                and_(
                    Document.beneficiary_id == beneficiary_id,
                    Document.created_at.between(start_date, end_date)
                )
            ).count()
        }
    
    def _calculate_trainer_completion_rate(self, appointments: List[Appointment]) -> float:
        """Calculate completion rate for trainer appointments."""
        if not appointments:
            return 0.0
        
        completed = len([a for a in appointments if a.status == 'completed'])
        total = len(appointments)
        
        return round((completed / total * 100) if total > 0 else 0, 2)
    
    def _get_trainer_beneficiary_performance(
        self,
        beneficiary_ids: List[int],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get performance metrics for trainer's beneficiaries."""
        if not beneficiary_ids:
            return {
                'average_score': 0,
                'improvement_rate': 0,
                'high_performers': 0,
                'needs_attention': 0
            }
        
        scores = []
        improvements = []
        high_performers = 0
        needs_attention = 0
        
        for ben_id in beneficiary_ids:
            performance = self._get_assessment_performance(ben_id, start_date, end_date)
            progress = self._calculate_progress_metrics(ben_id, start_date, end_date)
            
            if performance.get('average_score'):
                scores.append(performance['average_score'])
                
                if performance['average_score'] >= 80:
                    high_performers += 1
                elif performance['average_score'] < 60:
                    needs_attention += 1
            
            if progress.get('improvement_rate') is not None:
                improvements.append(progress['improvement_rate'])
        
        return {
            'average_score': round(sum(scores) / len(scores) if scores else 0, 2),
            'improvement_rate': round(sum(improvements) / len(improvements) if improvements else 0, 2),
            'high_performers': high_performers,
            'needs_attention': needs_attention
        }


# Create singleton instance
analytics_service = AnalyticsService()