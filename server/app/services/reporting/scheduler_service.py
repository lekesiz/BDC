"""
Report Scheduler Service

Provides automated report scheduling and delivery:
- Flexible scheduling options (daily, weekly, monthly, custom)
- Multiple delivery methods (email, webhook, file system)
- Report generation queue management
- Conditional delivery based on data thresholds
- Delivery history and retry logic
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session
from celery import Celery
from crontab import CronTab

from app.models.report import Report
from app.core.database_manager import DatabaseManager
from .report_builder_service import ReportBuilderService
from .export_service import ExportService
from app.services.email_service import EmailService


class ReportSchedulerService:
    """Service for scheduling and delivering automated reports"""

    def __init__(self, db_session: Session = None, celery_app: Celery = None):
        self.db = db_session or DatabaseManager.get_session()
        self.report_builder = ReportBuilderService(self.db)
        self.export_service = ExportService()
        self.email_service = EmailService()
        self.celery_app = celery_app
        
    def create_scheduled_report(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new scheduled report"""
        
        # Validate schedule configuration
        validation_result = self.validate_schedule_config(schedule_data)
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid schedule configuration: {validation_result['errors']}")
        
        schedule_id = str(uuid.uuid4())
        schedule = {
            'id': schedule_id,
            'name': schedule_data.get('name', 'Untitled Scheduled Report'),
            'description': schedule_data.get('description', ''),
            'report_config': schedule_data.get('report_config', {}),
            'schedule_config': schedule_data.get('schedule_config', {}),
            'delivery_config': schedule_data.get('delivery_config', {}),
            'conditions': schedule_data.get('conditions', []),
            'is_active': schedule_data.get('is_active', True),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'created_by': schedule_data.get('created_by'),
            'last_run': None,
            'next_run': self._calculate_next_run(schedule_data.get('schedule_config', {})),
            'run_count': 0,
            'success_count': 0,
            'failure_count': 0,
            'last_status': 'pending'
        }
        
        # Save to database
        report = Report(
            name=schedule['name'],
            description=schedule['description'],
            template_data=json.dumps(schedule),
            created_by=schedule['created_by'],
            is_template=False,
            report_type='scheduled'
        )
        
        self.db.add(report)
        self.db.commit()
        
        schedule['id'] = str(report.id)
        
        # Register with task scheduler
        if self.celery_app and schedule['is_active']:
            self._register_celery_task(schedule)
        
        return schedule

    def update_scheduled_report(self, schedule_id: str, 
                              schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing scheduled report"""
        
        report = self.db.query(Report).filter(Report.id == schedule_id).first()
        if not report:
            raise ValueError(f"Scheduled report with ID {schedule_id} not found")
        
        # Update schedule data
        existing_schedule = json.loads(report.template_data) if report.template_data else {}
        existing_schedule.update({
            'name': schedule_data.get('name', existing_schedule.get('name')),
            'description': schedule_data.get('description', existing_schedule.get('description')),
            'report_config': schedule_data.get('report_config', existing_schedule.get('report_config', {})),
            'schedule_config': schedule_data.get('schedule_config', existing_schedule.get('schedule_config', {})),
            'delivery_config': schedule_data.get('delivery_config', existing_schedule.get('delivery_config', {})),
            'conditions': schedule_data.get('conditions', existing_schedule.get('conditions', [])),
            'is_active': schedule_data.get('is_active', existing_schedule.get('is_active', True)),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        # Recalculate next run if schedule changed
        if 'schedule_config' in schedule_data:
            existing_schedule['next_run'] = self._calculate_next_run(
                existing_schedule['schedule_config']
            )
        
        report.name = existing_schedule['name']
        report.description = existing_schedule['description']
        report.template_data = json.dumps(existing_schedule)
        
        self.db.commit()
        
        # Update celery task
        if self.celery_app:
            if existing_schedule['is_active']:
                self._register_celery_task(existing_schedule)
            else:
                self._unregister_celery_task(schedule_id)
        
        return existing_schedule

    def get_scheduled_reports(self, user_id: Optional[str] = None, 
                            include_inactive: bool = False) -> List[Dict[str, Any]]:
        """Get scheduled reports"""
        
        query = self.db.query(Report).filter(Report.report_type == 'scheduled')
        
        if user_id:
            query = query.filter(Report.created_by == user_id)
        
        schedules = []
        for report in query.all():
            schedule_data = json.loads(report.template_data) if report.template_data else {}
            
            if not include_inactive and not schedule_data.get('is_active', True):
                continue
            
            schedules.append({
                'id': str(report.id),
                'name': report.name,
                'description': report.description,
                'is_active': schedule_data.get('is_active', True),
                'schedule_type': schedule_data.get('schedule_config', {}).get('type', 'manual'),
                'delivery_method': schedule_data.get('delivery_config', {}).get('method', 'email'),
                'created_at': schedule_data.get('created_at'),
                'last_run': schedule_data.get('last_run'),
                'next_run': schedule_data.get('next_run'),
                'run_count': schedule_data.get('run_count', 0),
                'success_rate': self._calculate_success_rate(schedule_data),
                'last_status': schedule_data.get('last_status', 'pending')
            })
        
        return schedules

    def get_scheduled_report(self, schedule_id: str) -> Dict[str, Any]:
        """Get a specific scheduled report"""
        
        report = self.db.query(Report).filter(Report.id == schedule_id).first()
        if not report:
            raise ValueError(f"Scheduled report with ID {schedule_id} not found")
        
        schedule_data = json.loads(report.template_data) if report.template_data else {}
        schedule_data['id'] = str(report.id)
        
        return schedule_data

    def delete_scheduled_report(self, schedule_id: str) -> bool:
        """Delete a scheduled report"""
        
        report = self.db.query(Report).filter(Report.id == schedule_id).first()
        if not report:
            raise ValueError(f"Scheduled report with ID {schedule_id} not found")
        
        # Unregister from celery
        if self.celery_app:
            self._unregister_celery_task(schedule_id)
        
        self.db.delete(report)
        self.db.commit()
        
        return True

    def execute_scheduled_report(self, schedule_id: str, 
                               force_delivery: bool = False) -> Dict[str, Any]:
        """Execute a scheduled report immediately"""
        
        schedule = self.get_scheduled_report(schedule_id)
        
        execution_id = str(uuid.uuid4())
        execution_start = datetime.utcnow()
        
        try:
            # Generate report data
            report_result = self.report_builder.execute_report(
                schedule['report_config']
            )
            
            # Check conditions if not forced
            if not force_delivery and not self._check_delivery_conditions(
                report_result, schedule.get('conditions', [])
            ):
                return {
                    'execution_id': execution_id,
                    'status': 'skipped',
                    'reason': 'Delivery conditions not met',
                    'execution_time': (datetime.utcnow() - execution_start).total_seconds()
                }
            
            # Export report
            export_config = schedule['delivery_config'].get('export_config', {})
            export_format = export_config.get('format', 'pdf')
            
            exported_file = self.export_service.export_report(
                report_result, export_format, export_config
            )
            
            # Deliver report
            delivery_result = self._deliver_report(
                exported_file, schedule['delivery_config'], report_result
            )
            
            # Update schedule statistics
            self._update_schedule_stats(schedule_id, True)
            
            return {
                'execution_id': execution_id,
                'status': 'success',
                'delivery_result': delivery_result,
                'export_file': exported_file['file_path'],
                'record_count': len(report_result['data']),
                'execution_time': (datetime.utcnow() - execution_start).total_seconds()
            }
            
        except Exception as e:
            # Update schedule statistics
            self._update_schedule_stats(schedule_id, False)
            
            return {
                'execution_id': execution_id,
                'status': 'error',
                'error': str(e),
                'execution_time': (datetime.utcnow() - execution_start).total_seconds()
            }

    def _calculate_next_run(self, schedule_config: Dict[str, Any]) -> Optional[str]:
        """Calculate the next run time based on schedule configuration"""
        
        schedule_type = schedule_config.get('type', 'manual')
        
        if schedule_type == 'manual':
            return None
        
        now = datetime.utcnow()
        
        if schedule_type == 'once':
            run_time = schedule_config.get('run_time')
            if run_time:
                return run_time
            return None
        
        elif schedule_type == 'daily':
            time_str = schedule_config.get('time', '09:00')
            hour, minute = map(int, time_str.split(':'))
            
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            
            return next_run.isoformat()
        
        elif schedule_type == 'weekly':
            weekday = schedule_config.get('weekday', 1)  # Monday = 1
            time_str = schedule_config.get('time', '09:00')
            hour, minute = map(int, time_str.split(':'))
            
            days_ahead = weekday - now.weekday()
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_run.isoformat()
        
        elif schedule_type == 'monthly':
            day = schedule_config.get('day', 1)
            time_str = schedule_config.get('time', '09:00')
            hour, minute = map(int, time_str.split(':'))
            
            # Start with next month
            if now.month == 12:
                next_run = now.replace(year=now.year + 1, month=1, day=day,
                                     hour=hour, minute=minute, second=0, microsecond=0)
            else:
                next_run = now.replace(month=now.month + 1, day=day,
                                     hour=hour, minute=minute, second=0, microsecond=0)
            
            return next_run.isoformat()
        
        elif schedule_type == 'cron':
            cron_expression = schedule_config.get('cron_expression')
            if cron_expression:
                cron = CronTab(cron_expression)
                next_run = now + timedelta(seconds=cron.next())
                return next_run.isoformat()
        
        return None

    def _check_delivery_conditions(self, report_result: Dict[str, Any], 
                                 conditions: List[Dict[str, Any]]) -> bool:
        """Check if delivery conditions are met"""
        
        if not conditions:
            return True
        
        data = report_result.get('data', [])
        
        for condition in conditions:
            condition_type = condition.get('type')
            
            if condition_type == 'minimum_records':
                min_records = condition.get('value', 0)
                if len(data) < min_records:
                    return False
            
            elif condition_type == 'maximum_records':
                max_records = condition.get('value', 1000000)
                if len(data) > max_records:
                    return False
            
            elif condition_type == 'field_value':
                field_name = condition.get('field')
                operator = condition.get('operator', 'equals')
                expected_value = condition.get('value')
                
                # Check if any record meets the condition
                condition_met = False
                for record in data:
                    field_value = record.get(field_name)
                    
                    if operator == 'equals' and field_value == expected_value:
                        condition_met = True
                        break
                    elif operator == 'greater_than' and field_value > expected_value:
                        condition_met = True
                        break
                    elif operator == 'less_than' and field_value < expected_value:
                        condition_met = True
                        break
                
                if not condition_met:
                    return False
            
            elif condition_type == 'aggregation':
                field_name = condition.get('field')
                aggregation = condition.get('aggregation', 'sum')
                operator = condition.get('operator', 'greater_than')
                threshold = condition.get('threshold', 0)
                
                # Calculate aggregation
                values = [record.get(field_name, 0) for record in data if record.get(field_name) is not None]
                
                if aggregation == 'sum':
                    result = sum(values)
                elif aggregation == 'avg':
                    result = sum(values) / len(values) if values else 0
                elif aggregation == 'min':
                    result = min(values) if values else 0
                elif aggregation == 'max':
                    result = max(values) if values else 0
                elif aggregation == 'count':
                    result = len(values)
                else:
                    continue
                
                # Check threshold
                if operator == 'greater_than' and result <= threshold:
                    return False
                elif operator == 'less_than' and result >= threshold:
                    return False
                elif operator == 'equals' and result != threshold:
                    return False
        
        return True

    def _deliver_report(self, exported_file: Dict[str, Any], 
                       delivery_config: Dict[str, Any], 
                       report_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver the report using the configured method"""
        
        delivery_method = delivery_config.get('method', 'email')
        
        if delivery_method == 'email':
            return self._deliver_via_email(exported_file, delivery_config, report_result)
        elif delivery_method == 'webhook':
            return self._deliver_via_webhook(exported_file, delivery_config, report_result)
        elif delivery_method == 'ftp':
            return self._deliver_via_ftp(exported_file, delivery_config, report_result)
        elif delivery_method == 'filesystem':
            return self._deliver_via_filesystem(exported_file, delivery_config, report_result)
        else:
            raise ValueError(f"Unsupported delivery method: {delivery_method}")

    def _deliver_via_email(self, exported_file: Dict[str, Any], 
                          delivery_config: Dict[str, Any], 
                          report_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver report via email"""
        
        recipients = delivery_config.get('recipients', [])
        subject = delivery_config.get('subject', 'Scheduled Report')
        body = delivery_config.get('body', 'Please find the attached report.')
        
        # Replace template variables in subject and body
        template_vars = {
            'record_count': len(report_result.get('data', [])),
            'generation_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'file_name': exported_file.get('file_name', 'report')
        }
        
        for var, value in template_vars.items():
            subject = subject.replace(f'{{{var}}}', str(value))
            body = body.replace(f'{{{var}}}', str(value))
        
        # Send email
        result = self.email_service.send_email(
            to=recipients,
            subject=subject,
            body=body,
            attachments=[exported_file['file_path']]
        )
        
        return {
            'method': 'email',
            'recipients': recipients,
            'success': result.get('success', False),
            'message_id': result.get('message_id'),
            'error': result.get('error')
        }

    def _deliver_via_webhook(self, exported_file: Dict[str, Any], 
                           delivery_config: Dict[str, Any], 
                           report_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver report via webhook"""
        
        import requests
        
        webhook_url = delivery_config.get('webhook_url')
        headers = delivery_config.get('headers', {})
        method = delivery_config.get('http_method', 'POST')
        
        # Prepare payload
        payload = {
            'report_data': report_result['data'],
            'metadata': report_result.get('metadata', {}),
            'file_info': {
                'file_name': exported_file.get('file_name'),
                'file_size': exported_file.get('file_size'),
                'format': exported_file.get('format')
            },
            'delivery_time': datetime.utcnow().isoformat()
        }
        
        # Include file content if requested
        if delivery_config.get('include_file_content', False):
            with open(exported_file['file_path'], 'rb') as f:
                import base64
                payload['file_content'] = base64.b64encode(f.read()).decode('utf-8')
        
        try:
            if method.upper() == 'POST':
                response = requests.post(webhook_url, json=payload, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(webhook_url, json=payload, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            return {
                'method': 'webhook',
                'url': webhook_url,
                'success': True,
                'status_code': response.status_code,
                'response': response.text[:1000]  # Truncate long responses
            }
            
        except Exception as e:
            return {
                'method': 'webhook',
                'url': webhook_url,
                'success': False,
                'error': str(e)
            }

    def _deliver_via_ftp(self, exported_file: Dict[str, Any], 
                        delivery_config: Dict[str, Any], 
                        report_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver report via FTP"""
        
        import ftplib
        
        ftp_host = delivery_config.get('ftp_host')
        ftp_user = delivery_config.get('ftp_user')
        ftp_password = delivery_config.get('ftp_password')
        ftp_path = delivery_config.get('ftp_path', '/')
        
        try:
            with ftplib.FTP(ftp_host) as ftp:
                ftp.login(ftp_user, ftp_password)
                
                # Change to target directory
                if ftp_path != '/':
                    ftp.cwd(ftp_path)
                
                # Upload file
                file_name = exported_file.get('file_name')
                with open(exported_file['file_path'], 'rb') as f:
                    ftp.storbinary(f'STOR {file_name}', f)
                
                return {
                    'method': 'ftp',
                    'host': ftp_host,
                    'path': f"{ftp_path}/{file_name}",
                    'success': True
                }
                
        except Exception as e:
            return {
                'method': 'ftp',
                'host': ftp_host,
                'success': False,
                'error': str(e)
            }

    def _deliver_via_filesystem(self, exported_file: Dict[str, Any], 
                              delivery_config: Dict[str, Any], 
                              report_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver report to filesystem location"""
        
        import shutil
        import os
        
        target_path = delivery_config.get('target_path')
        file_name_template = delivery_config.get('file_name_template', '{original_name}')
        
        # Generate target file name
        template_vars = {
            'original_name': exported_file.get('file_name'),
            'timestamp': datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
            'date': datetime.utcnow().strftime('%Y%m%d'),
            'record_count': len(report_result.get('data', []))
        }
        
        target_file_name = file_name_template
        for var, value in template_vars.items():
            target_file_name = target_file_name.replace(f'{{{var}}}', str(value))
        
        target_file_path = os.path.join(target_path, target_file_name)
        
        try:
            # Ensure target directory exists
            os.makedirs(target_path, exist_ok=True)
            
            # Copy file
            shutil.copy2(exported_file['file_path'], target_file_path)
            
            return {
                'method': 'filesystem',
                'target_path': target_file_path,
                'success': True
            }
            
        except Exception as e:
            return {
                'method': 'filesystem',
                'target_path': target_file_path,
                'success': False,
                'error': str(e)
            }

    def _update_schedule_stats(self, schedule_id: str, success: bool):
        """Update schedule execution statistics"""
        
        schedule = self.get_scheduled_report(schedule_id)
        
        schedule['run_count'] = schedule.get('run_count', 0) + 1
        schedule['last_run'] = datetime.utcnow().isoformat()
        schedule['last_status'] = 'success' if success else 'error'
        
        if success:
            schedule['success_count'] = schedule.get('success_count', 0) + 1
        else:
            schedule['failure_count'] = schedule.get('failure_count', 0) + 1
        
        # Calculate next run
        schedule['next_run'] = self._calculate_next_run(
            schedule.get('schedule_config', {})
        )
        
        self.update_scheduled_report(schedule_id, schedule)

    def _calculate_success_rate(self, schedule_data: Dict[str, Any]) -> float:
        """Calculate success rate for a schedule"""
        
        run_count = schedule_data.get('run_count', 0)
        success_count = schedule_data.get('success_count', 0)
        
        if run_count == 0:
            return 0.0
        
        return (success_count / run_count) * 100

    def validate_schedule_config(self, schedule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate schedule configuration"""
        
        errors = []
        warnings = []
        
        # Check required fields
        if not schedule_data.get('name'):
            errors.append("Schedule name is required")
        
        if not schedule_data.get('report_config'):
            errors.append("Report configuration is required")
        
        if not schedule_data.get('delivery_config'):
            errors.append("Delivery configuration is required")
        
        # Validate schedule configuration
        schedule_config = schedule_data.get('schedule_config', {})
        schedule_type = schedule_config.get('type', 'manual')
        
        if schedule_type not in ['manual', 'once', 'daily', 'weekly', 'monthly', 'cron']:
            errors.append(f"Invalid schedule type: {schedule_type}")
        
        if schedule_type == 'cron':
            cron_expression = schedule_config.get('cron_expression')
            if not cron_expression:
                errors.append("Cron expression is required for cron schedule type")
            else:
                try:
                    CronTab(cron_expression)
                except Exception:
                    errors.append("Invalid cron expression")
        
        # Validate delivery configuration
        delivery_config = schedule_data.get('delivery_config', {})
        delivery_method = delivery_config.get('method')
        
        if not delivery_method:
            errors.append("Delivery method is required")
        elif delivery_method not in ['email', 'webhook', 'ftp', 'filesystem']:
            errors.append(f"Invalid delivery method: {delivery_method}")
        
        if delivery_method == 'email' and not delivery_config.get('recipients'):
            errors.append("Email recipients are required for email delivery")
        
        if delivery_method == 'webhook' and not delivery_config.get('webhook_url'):
            errors.append("Webhook URL is required for webhook delivery")
        
        if delivery_method == 'filesystem' and not delivery_config.get('target_path'):
            errors.append("Target path is required for filesystem delivery")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _register_celery_task(self, schedule: Dict[str, Any]):
        """Register schedule with Celery for automatic execution"""
        # This would integrate with Celery beat scheduler
        # Implementation depends on your Celery setup
        pass

    def _unregister_celery_task(self, schedule_id: str):
        """Unregister schedule from Celery"""
        # This would remove the task from Celery beat scheduler
        # Implementation depends on your Celery setup
        pass