"""Report generation Celery tasks."""

from celery import shared_task
from datetime import datetime, timedelta
from app.models import User, Beneficiary, Program, Evaluation, TestSession
from app.services import ReportService, EmailService
from app.extensions import db
from flask import current_app


@shared_task(bind=True)
def generate_weekly_reports(self):
    """Generate weekly reports for all tenants."""
    try:
        from app.models import Tenant
        
        # Get all active tenants
        tenants = Tenant.query.filter_by(is_active=True).all()
        
        count = 0
        for tenant in tenants:
            try:
                # Generate tenant weekly report
                report_data = _generate_tenant_weekly_data(tenant.id)
                
                # Create report
                report = ReportService.create_report({
                    'title': f'Weekly Report - {tenant.name}',
                    'type': 'weekly_summary',
                    'tenant_id': tenant.id,
                    'data': report_data,
                    'format': 'pdf'
                })
                
                # Send to tenant admins
                admins = User.query.filter(
                    User.role == 'tenant_admin',
                    User.tenants.any(id=tenant.id),
                    User.is_active == True
                ).all()
                
                for admin in admins:
                    EmailService.send_weekly_report(
                        to_email=admin.email,
                        report_url=report.download_url,
                        report_data=report_data
                    )
                
                count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error generating report for tenant {tenant.id}: {str(e)}")
                continue
        
        return f"Generated {count} weekly reports"
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_weekly_reports task: {str(e)}")
        raise


@shared_task(bind=True)
def generate_monthly_analytics(self):
    """Generate monthly analytics reports."""
    try:
        from app.models import Tenant
        
        # Get all active tenants
        tenants = Tenant.query.filter_by(is_active=True).all()
        
        count = 0
        for tenant in tenants:
            try:
                # Generate analytics data
                analytics_data = _generate_tenant_monthly_analytics(tenant.id)
                
                # Create report
                report = ReportService.create_report({
                    'title': f'Monthly Analytics - {tenant.name}',
                    'type': 'monthly_analytics',
                    'tenant_id': tenant.id,
                    'data': analytics_data,
                    'format': 'pdf'
                })
                
                count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error generating analytics for tenant {tenant.id}: {str(e)}")
                continue
        
        return f"Generated {count} monthly analytics reports"
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_monthly_analytics task: {str(e)}")
        raise


@shared_task(bind=True)
def generate_beneficiary_progress_report(self, beneficiary_id):
    """Generate progress report for a specific beneficiary."""
    try:
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if not beneficiary:
            raise ValueError(f"Beneficiary {beneficiary_id} not found")
        
        # Generate progress data
        progress_data = _generate_beneficiary_progress_data(beneficiary_id)
        
        # Create report
        report = ReportService.create_report({
            'title': f'Progress Report - {beneficiary.user.first_name} {beneficiary.user.last_name}',
            'type': 'beneficiary_progress',
            'beneficiary_id': beneficiary_id,
            'data': progress_data,
            'format': 'pdf'
        })
        
        # Send to beneficiary and trainer
        if beneficiary.user.email:
            EmailService.send_progress_report(
                to_email=beneficiary.user.email,
                report_url=report.download_url,
                report_data=progress_data
            )
        
        if beneficiary.trainer and beneficiary.trainer.email:
            EmailService.send_progress_report(
                to_email=beneficiary.trainer.email,
                report_url=report.download_url,
                report_data=progress_data,
                is_trainer=True
            )
        
        return f"Generated progress report for beneficiary {beneficiary_id}"
        
    except Exception as e:
        current_app.logger.error(f"Error in generate_beneficiary_progress_report task: {str(e)}")
        raise


def _generate_tenant_weekly_data(tenant_id):
    """Generate weekly data for a tenant."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    # Get statistics
    new_beneficiaries = Beneficiary.query.filter(
        Beneficiary.tenant_id == tenant_id,
        Beneficiary.created_at >= start_date,
        Beneficiary.created_at <= end_date
    ).count()
    
    completed_evaluations = TestSession.query.join(Evaluation).filter(
        Evaluation.tenant_id == tenant_id,
        TestSession.completed_at >= start_date,
        TestSession.completed_at <= end_date,
        TestSession.status == 'completed'
    ).count()
    
    active_programs = Program.query.filter(
        Program.tenant_id == tenant_id,
        Program.status == 'active'
    ).count()
    
    return {
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'statistics': {
            'new_beneficiaries': new_beneficiaries,
            'completed_evaluations': completed_evaluations,
            'active_programs': active_programs
        }
    }


def _generate_tenant_monthly_analytics(tenant_id):
    """Generate monthly analytics for a tenant."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    # Get detailed analytics
    beneficiary_growth = []
    evaluation_completion = []
    
    # Calculate daily metrics for the month
    for i in range(30):
        day = start_date + timedelta(days=i)
        next_day = day + timedelta(days=1)
        
        # Beneficiary count
        beneficiary_count = Beneficiary.query.filter(
            Beneficiary.tenant_id == tenant_id,
            Beneficiary.created_at <= next_day
        ).count()
        
        beneficiary_growth.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': beneficiary_count
        })
        
        # Evaluation completions
        daily_completions = TestSession.query.join(Evaluation).filter(
            Evaluation.tenant_id == tenant_id,
            TestSession.completed_at >= day,
            TestSession.completed_at < next_day,
            TestSession.status == 'completed'
        ).count()
        
        evaluation_completion.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': daily_completions
        })
    
    return {
        'period': {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        },
        'analytics': {
            'beneficiary_growth': beneficiary_growth,
            'evaluation_completion': evaluation_completion
        }
    }


def _generate_beneficiary_progress_data(beneficiary_id):
    """Generate progress data for a beneficiary."""
    beneficiary = Beneficiary.query.get(beneficiary_id)
    
    # Get completed evaluations
    completed_sessions = TestSession.query.filter(
        TestSession.beneficiary_id == beneficiary_id,
        TestSession.status == 'completed'
    ).all()
    
    # Calculate average score
    total_score = 0
    scored_count = 0
    for session in completed_sessions:
        if session.score is not None:
            total_score += session.score
            scored_count += 1
    
    avg_score = total_score / scored_count if scored_count > 0 else 0
    
    # Get program enrollments
    from app.models import ProgramEnrollment
    enrollments = ProgramEnrollment.query.filter_by(
        beneficiary_id=beneficiary_id
    ).all()
    
    return {
        'beneficiary': {
            'id': beneficiary.id,
            'name': f"{beneficiary.user.first_name} {beneficiary.user.last_name}",
            'email': beneficiary.user.email
        },
        'progress': {
            'completed_evaluations': len(completed_sessions),
            'average_score': avg_score,
            'program_enrollments': len(enrollments),
            'active_programs': len([e for e in enrollments if e.status == 'active'])
        }
    }