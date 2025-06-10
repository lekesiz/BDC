_('monitoring_alarm_system.message.alarm_system_for_bdc_applicat')
import time
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
import threading
from dataclasses import dataclass
from flask import Flask, request
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.monitoring import AlarmRule, AlarmHistory
from app.utils.notifications import send_notification
from app.utils.logging import logger
from flask_babel import _, lazy_gettext as _l


class AlarmSeverity(Enum):
    _('monitoring_alarm_system.label.alarm_severity_levels')
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'


class AlarmStatus(Enum):
    _('monitoring_alarm_system.label.alarm_status')
    ACTIVE = 'active'
    RESOLVED = 'resolved'
    ACKNOWLEDGED = 'acknowledged'
    SILENCED = 'silenced'


@dataclass
class AlarmRule:
    _('monitoring_alarm_system.label.alarm_rule_definition')
    name: str
    description: str
    metric_type: str
    threshold_value: float
    operator: str
    severity: AlarmSeverity
    duration: int
    cooldown: int
    notification_channels: List[str]
    enabled: bool = True
    metadata: Dict[str, Any] = None


class AlarmSystem:
    _('monitoring_alarm_system.message.central_alarm_system_for_monit')

    def __init__(self, app: Optional[Flask]=None, redis_client: Optional[
        redis.Redis]=None, db_session: Optional[sessionmaker]=None):
        self.app = app
        self.redis_client = redis_client
        self.db_session = db_session
        self.rules: Dict[str, AlarmRule] = {}
        self.active_alarms: Dict[str, Dict[str, Any]] = {}
        self.alarm_history: List[Dict[str, Any]] = []
        self.metric_evaluators: Dict[str, Callable] = {}
        self.notification_handlers: Dict[str, Callable] = {'email': self.
            _send_email_notification, 'slack': self.
            _send_slack_notification, 'webhook': self.
            _send_webhook_notification, 'sms': self._send_sms_notification}
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
        self._lock = threading.Lock()
        if app:
            self.init_app(app, redis_client, db_session)

    def init_app(self, app: Flask, redis_client: redis.Redis, db_session:
        sessionmaker):
        _('monitoring_alarm_system.message.initialize_with_flask_app')
        self.app = app
        self.redis_client = redis_client
        self.db_session = db_session
        self._load_alarm_rules()
        self._register_metric_evaluators()
        self.start_monitoring()

    def _load_alarm_rules(self):
        """Load alarm rules from configuration"""
        default_rules = [AlarmRule(name='high_error_rate', description=_(
            'monitoring_alarm_system.error.high_application_error_rate'),
            metric_type='error_rate', threshold_value=0.05, operator='gt',
            severity=AlarmSeverity.ERROR, duration=300, cooldown=900,
            notification_channels=['email', 'slack']), AlarmRule(name=
            'high_response_time', description=_(
            'monitoring_alarm_system.message.high_average_response_time'),
            metric_type='response_time', threshold_value=1000, operator=
            'gt', severity=AlarmSeverity.WARNING, duration=300, cooldown=
            600, notification_channels=['slack']), AlarmRule(name=
            'high_cpu_usage', description=_(
            'monitoring_performance_monitor.label.high_cpu_usage_1'),
            metric_type='cpu_percent', threshold_value=80, operator='gt',
            severity=AlarmSeverity.WARNING, duration=300, cooldown=600,
            notification_channels=['email']), AlarmRule(name=
            'high_memory_usage', description=_(
            'monitoring_performance_monitor.label.high_memory_usage_1'),
            metric_type='memory_percent', threshold_value=85, operator='gt',
            severity=AlarmSeverity.ERROR, duration=300, cooldown=600,
            notification_channels=['email', 'slack']), AlarmRule(name=
            'disk_space_low', description=_(
            'monitoring_alarm_system.label.low_disk_space'), metric_type=
            'disk_free_percent', threshold_value=10, operator='lt',
            severity=AlarmSeverity.CRITICAL, duration=0, cooldown=3600,
            notification_channels=['email', 'slack', 'sms']), AlarmRule(
            name='database_connection_failed', description=_(
            'monitoring_alarm_system.error.database_connection_failures'),
            metric_type='db_connection_errors', threshold_value=5, operator
            ='gt', severity=AlarmSeverity.CRITICAL, duration=60, cooldown=
            300, notification_channels=['email', 'slack', 'sms'])]
        if self.db_session:
            try:
                session = self.db_session()
                db_rules = session.query(AlarmRule).filter_by(enabled=True
                    ).all()
                for rule in db_rules:
                    self.rules[rule.name] = rule
                session.close()
            except Exception as e:
                logger.error(
                    f'Failed to load alarm rules from database: {str(e)}')
        for rule in default_rules:
            if rule.name not in self.rules:
                self.rules[rule.name] = rule

    def _register_metric_evaluators(self):
        _('monitoring_alarm_system.message.register_metric_evaluation_fun')
        self.metric_evaluators = {'error_rate': self._evaluate_error_rate,
            'response_time': self._evaluate_response_time, 'cpu_percent':
            self._evaluate_cpu_percent, 'memory_percent': self.
            _evaluate_memory_percent, 'disk_free_percent': self.
            _evaluate_disk_free_percent, 'db_connection_errors': self.
            _evaluate_db_errors}

    def add_rule(self, rule: AlarmRule):
        """Add or update an alarm rule"""
        with self._lock:
            self.rules[rule.name] = rule
            if self.db_session:
                try:
                    session = self.db_session()
                    db_rule = session.query(AlarmRule).filter_by(name=rule.name
                        ).first()
                    if db_rule:
                        for key, value in rule.__dict__.items():
                            setattr(db_rule, key, value)
                    else:
                        session.add(rule)
                    session.commit()
                    session.close()
                except Exception as e:
                    logger.error(f'Failed to save alarm rule: {str(e)}')

    def remove_rule(self, rule_name: str):
        _('monitoring_alarm_system.message.remove_an_alarm_rule')
        with self._lock:
            if rule_name in self.rules:
                del self.rules[rule_name]
                if self.db_session:
                    try:
                        session = self.db_session()
                        rule = session.query(AlarmRule).filter_by(name=
                            rule_name).first()
                        if rule:
                            session.delete(rule)
                            session.commit()
                        session.close()
                    except Exception as e:
                        logger.error(f'Failed to remove alarm rule: {str(e)}')

    def evaluate_metrics(self):
        _('monitoring_alarm_system.message.evaluate_all_metrics_against_a')
        with self._lock:
            current_time = time.time()
            for rule_name, rule in self.rules.items():
                if not rule.enabled:
                    continue
                evaluator = self.metric_evaluators.get(rule.metric_type)
                if not evaluator:
                    logger.warning(
                        f'No evaluator for metric type: {rule.metric_type}')
                    continue
                try:
                    metric_value = evaluator()
                    triggered = self._check_threshold(metric_value, rule.
                        threshold_value, rule.operator)
                    self._handle_alarm_state(rule, triggered, metric_value,
                        current_time)
                except Exception as e:
                    logger.error(
                        f'Error evaluating metric {rule.metric_type}: {str(e)}'
                        )

    def _check_threshold(self, value: float, threshold: float, operator: str
        ) ->bool:
        _('monitoring_alarm_system.message.check_if_value_crosses_thresho')
        operators = {'gt': lambda x, y: x > y, 'lt': lambda x, y: x < y,
            'eq': lambda x, y: x == y, 'gte': lambda x, y: x >= y, 'lte': 
            lambda x, y: x <= y}
        return operators.get(operator, lambda x, y: False)(value, threshold)

    def _handle_alarm_state(self, rule: AlarmRule, triggered: bool,
        metric_value: float, current_time: float):
        _('monitoring_alarm_system.message.handle_alarm_state_transitions')
        alarm_key = f'alarm:{rule.name}'
        if triggered:
            if alarm_key in self.active_alarms:
                alarm = self.active_alarms[alarm_key]
                alarm['duration'] = current_time - alarm['triggered_at']
                if alarm['duration'] >= rule.duration and not alarm['notified'
                    ]:
                    self._send_alarm_notification(rule, metric_value, alarm)
                    alarm['notified'] = True
                    alarm['notified_at'] = current_time
            else:
                self.active_alarms[alarm_key] = {'rule_name': rule.name,
                    'triggered_at': current_time, 'metric_value':
                    metric_value, 'duration': 0, 'notified': False,
                    'acknowledged': False, 'status': AlarmStatus.ACTIVE.value}
        elif alarm_key in self.active_alarms:
            alarm = self.active_alarms[alarm_key]
            self._resolve_alarm(rule, alarm, current_time)
            del self.active_alarms[alarm_key]

    def _send_alarm_notification(self, rule: AlarmRule, metric_value: float,
        alarm: Dict[str, Any]):
        _('monitoring_alarm_system.label.send_alarm_notification')
        if self._is_in_cooldown(rule.name):
            return
        notification_data = {'alarm_name': rule.name, 'description': rule.
            description, 'severity': rule.severity.value, 'metric_value':
            metric_value, 'threshold_value': rule.threshold_value,
            'triggered_at': alarm['triggered_at'], 'duration': alarm[
            'duration']}
        for channel in rule.notification_channels:
            handler = self.notification_handlers.get(channel)
            if handler:
                try:
                    handler(notification_data)
                except Exception as e:
                    logger.error(
                        f'Failed to send {channel} notification: {str(e)}')
        self._record_alarm_history(rule, notification_data, 'triggered')
        self._set_cooldown(rule.name, rule.cooldown)

    def _resolve_alarm(self, rule: AlarmRule, alarm: Dict[str, Any],
        current_time: float):
        _('monitoring_alarm_system.label.resolve_an_alarm')
        resolution_data = {'alarm_name': rule.name, 'description': rule.
            description, 'resolved_at': current_time, 'duration': 
            current_time - alarm['triggered_at'], 'was_notified': alarm[
            'notified']}
        if alarm['notified']:
            for channel in rule.notification_channels:
                handler = self.notification_handlers.get(channel)
                if handler:
                    try:
                        handler({**resolution_data, 'type': 'resolution'})
                    except Exception as e:
                        logger.error(
                            f'Failed to send resolution notification: {str(e)}'
                            )
        self._record_alarm_history(rule, resolution_data, 'resolved')

    def _is_in_cooldown(self, rule_name: str) ->bool:
        _('monitoring_alarm_system.message.check_if_alarm_is_in_cooldown')
        if self.redis_client:
            cooldown_key = f'alarm:cooldown:{rule_name}'
            return self.redis_client.exists(cooldown_key)
        return False

    def _set_cooldown(self, rule_name: str, cooldown_seconds: int):
        _('monitoring_alarm_system.message.set_cooldown_for_alarm')
        if self.redis_client:
            cooldown_key = f'alarm:cooldown:{rule_name}'
            self.redis_client.setex(cooldown_key, cooldown_seconds, '1')

    def _record_alarm_history(self, rule: AlarmRule, data: Dict[str, Any],
        event_type: str):
        _('monitoring_alarm_system.message.record_alarm_event_in_history')
        history_entry = {'timestamp': time.time(), 'rule_name': rule.name,
            'event_type': event_type, 'severity': rule.severity.value,
            'data': data}
        self.alarm_history.append(history_entry)
        if len(self.alarm_history) > 1000:
            self.alarm_history.pop(0)
        if self.redis_client:
            history_key = f"alarm:history:{datetime.now().strftime('%Y%m%d')}"
            self.redis_client.zadd(history_key, {json.dumps(history_entry):
                history_entry['timestamp']})
            self.redis_client.expire(history_key, 30 * 86400)
        if self.db_session:
            try:
                session = self.db_session()
                db_history = AlarmHistory(timestamp=datetime.fromtimestamp(
                    history_entry['timestamp']), rule_name=rule.name,
                    event_type=event_type, severity=rule.severity.value,
                    data=json.dumps(data))
                session.add(db_history)
                session.commit()
                session.close()
            except Exception as e:
                logger.error(f'Failed to store alarm history: {str(e)}')

    def _evaluate_error_rate(self) ->float:
        _('monitoring_alarm_system.error.evaluate_application_error_rat')
        if hasattr(self.app, 'performance_collector'):
            summary = self.app.performance_collector.get_performance_summary(
                hours=1)
            return summary.get('error_rate', 0)
        return 0

    def _evaluate_response_time(self) ->float:
        _('monitoring_alarm_system.message.evaluate_average_response_time')
        if hasattr(self.app, 'performance_collector'):
            summary = self.app.performance_collector.get_performance_summary(
                hours=1)
            return summary.get('average_response_time', 0)
        return 0

    def _evaluate_cpu_percent(self) ->float:
        _('monitoring_alarm_system.message.evaluate_cpu_usage_percentage')
        if hasattr(self.app, 'performance_collector'):
            metrics = self.app.performance_collector.collect_system_metrics()
            return metrics.get('cpu', {}).get('percent', 0)
        return 0

    def _evaluate_memory_percent(self) ->float:
        _('monitoring_alarm_system.message.evaluate_memory_usage_percenta')
        if hasattr(self.app, 'performance_collector'):
            metrics = self.app.performance_collector.collect_system_metrics()
            return metrics.get('memory', {}).get('percent', 0)
        return 0

    def _evaluate_disk_free_percent(self) ->float:
        _('monitoring_alarm_system.message.evaluate_free_disk_space_perce')
        if hasattr(self.app, 'performance_collector'):
            metrics = self.app.performance_collector.collect_system_metrics()
            disk = metrics.get('disk', {})
            if disk.get('total', 0) > 0:
                return disk.get('free', 0) / disk.get('total', 1) * 100
        return 100

    def _evaluate_db_errors(self) ->int:
        _('monitoring_alarm_system.error.evaluate_database_connection_e')
        if self.redis_client:
            error_key = _(
                'monitoring_alarm_system.error.metrics_db_errors_count')
            count = self.redis_client.get(error_key)
            return int(count) if count else 0
        return 0

    def _send_email_notification(self, data: Dict[str, Any]):
        _('monitoring_alarm_system.label.send_email_notification')
        from app.utils.notifications import send_email
        try:
            recipients = self.app.config.get('ALARM_EMAIL_RECIPIENTS', [])
            if not recipients:
                logger.warning(_(
                    'monitoring_alarm_system.message.no_email_recipients_configured'
                    ))
                return
            subject = data.get('subject',
                f"BDC Alert: {data.get('alarm_name', 'System Alert')}")
            body = f"""
            Alert Details:
            
            Type: {data.get('type', 'Alert')}
            Severity: {data.get('severity', 'Unknown')}
            Description: {data.get('description', 'No description')}
            Metric Value: {data.get('metric_value', 'N/A')}
            Threshold: {data.get('threshold_value', 'N/A')}
            Time: {datetime.fromtimestamp(data.get('triggered_at', time.time())).strftime('%Y-%m-%d %H:%M:%S')}
            
            Additional Information:
            {data.get('message', '')}
            """
            for recipient in recipients:
                send_email(to=recipient, subject=subject, body=body,
                    html_body=f'<pre>{body}</pre>')
            logger.info(
                f'Email notifications sent to {len(recipients)} recipients')
        except Exception as e:
            logger.error(f'Failed to send email notification: {str(e)}')

    def _send_slack_notification(self, data: Dict[str, Any]):
        _('monitoring_alarm_system.label.send_slack_notification')
        import requests
        try:
            webhook_url = self.app.config.get('SLACK_WEBHOOK_URL')
            if not webhook_url:
                logger.warning(_(
                    'monitoring_alarm_system.message.no_slack_webhook_url_configure'
                    ))
                return
            message = {'text': data.get('text',
                f"BDC Alert: {data.get('alarm_name', 'System Alert')}"),
                'color': data.get('color', 'warning'), 'fields': data.get(
                'fields', [{'title': _(
                'services_alert_service.label.severity_2'), 'value': data.
                get('severity', _('analytics_data_export.label.unknown')),
                'short': True}, {'title': _(
                'monitoring_alarm_system.label.metric_value'), 'value': str
                (data.get('metric_value', _(
                'services_beneficiary_service.label.n_a_4'))), 'short': 
                True}, {'title': _(
                'monitoring_alarm_system.label.threshold'), 'value': str(
                data.get('threshold_value', _(
                'services_beneficiary_service.label.n_a_4'))), 'short': 
                True}, {'title': _(
                'i18n_translation_service.label.description'), 'value':
                data.get('description', _(
                'monitoring_alarm_system.label.no_description_1')), 'short':
                False}]), 'footer': _(
                'monitoring_alarm_system.label.bdc_monitoring_system_1'),
                'ts': int(data.get('triggered_at', time.time()))}
            response = requests.post(webhook_url, json=message, timeout=10)
            response.raise_for_status()
            logger.info(_(
                'monitoring_alarm_system.success.slack_notification_sent_succes'
                ))
        except Exception as e:
            logger.error(f'Failed to send Slack notification: {str(e)}')

    def _send_webhook_notification(self, data: Dict[str, Any]):
        _('monitoring_alarm_system.label.send_webhook_notification')
        import requests
        try:
            webhook_url = self.app.config.get('ALARM_WEBHOOK_URL')
            if not webhook_url:
                logger.warning(_(
                    'monitoring_alarm_system.message.no_webhook_url_configured_for'
                    ))
                return
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()
            data['source'] = _(
                'monitoring_alarm_system.label.bdc_monitoring_system_1')
            data['host'] = self.app.config.get('HOSTNAME', 'unknown')
            headers = {_(
                'video_conference_providers_microsoft_teams_provider.label.content_type_1'
                ): 'application/json', _(
                'monitoring_alarm_system.label.x_bdc_alert'): 'true'}
            auth_token = self.app.config.get('ALARM_WEBHOOK_TOKEN')
            if auth_token:
                headers[_(
                    'video_conference_providers_microsoft_teams_provider.label.authorization'
                    )] = f'Bearer {auth_token}'
            response = requests.post(webhook_url, json=data, headers=
                headers, timeout=10)
            response.raise_for_status()
            logger.info(f'Webhook notification sent to {webhook_url}')
        except Exception as e:
            logger.error(f'Failed to send webhook notification: {str(e)}')

    def _send_sms_notification(self, data: Dict[str, Any]):
        _('monitoring_alarm_system.label.send_sms_notification')
        try:
            twilio_account_sid = self.app.config.get('TWILIO_ACCOUNT_SID')
            twilio_auth_token = self.app.config.get('TWILIO_AUTH_TOKEN')
            twilio_from_number = self.app.config.get('TWILIO_FROM_NUMBER')
            if not all([twilio_account_sid, twilio_auth_token,
                twilio_from_number]):
                logger.warning(_(
                    'monitoring_alarm_system.message.twilio_credentials_not_configu'
                    ))
                return
            from twilio.rest import Client
            client = Client(twilio_account_sid, twilio_auth_token)
            recipients = self.app.config.get('ALARM_SMS_RECIPIENTS', [])
            if not recipients:
                logger.warning(_(
                    'monitoring_alarm_system.message.no_sms_recipients_configured_f'
                    ))
                return
            message = f"""BDC Alert: {data.get('alarm_name', 'System Alert')}
Severity: {data.get('severity', 'Unknown')}
Value: {data.get('metric_value', 'N/A')}
Threshold: {data.get('threshold_value', 'N/A')}
{data.get('description', '')[:50]}"""
            for recipient in recipients:
                try:
                    client.messages.create(body=message, from_=
                        twilio_from_number, to=recipient)
                    logger.info(f'SMS notification sent to {recipient}')
                except Exception as e:
                    logger.error(f'Failed to send SMS to {recipient}: {str(e)}'
                        )
        except ImportError:
            logger.warning(_(
                'monitoring_alarm_system.message.twilio_library_not_installed_f'
                ))
        except Exception as e:
            logger.error(f'Failed to send SMS notification: {str(e)}')

    def acknowledge_alarm(self, alarm_name: str, user_id: Optional[int]=None):
        _('monitoring_alarm_system.message.acknowledge_an_active_alarm')
        alarm_key = f'alarm:{alarm_name}'
        with self._lock:
            if alarm_key in self.active_alarms:
                alarm = self.active_alarms[alarm_key]
                alarm['acknowledged'] = True
                alarm['acknowledged_at'] = time.time()
                alarm['acknowledged_by'] = user_id
                alarm['status'] = AlarmStatus.ACKNOWLEDGED.value
                self._record_alarm_history(self.rules[alarm_name], {
                    'acknowledged_at': alarm['acknowledged_at'],
                    'acknowledged_by': user_id}, 'acknowledged')

    def silence_alarm(self, alarm_name: str, duration: int, user_id:
        Optional[int]=None):
        _('monitoring_alarm_system.message.silence_an_alarm_for_specified')
        with self._lock:
            if alarm_name in self.rules:
                if self.redis_client:
                    silence_key = f'alarm:silence:{alarm_name}'
                    self.redis_client.setex(silence_key, duration, json.
                        dumps({'silenced_by': user_id, 'silenced_at': time.
                        time(), 'duration': duration}))
                alarm_key = f'alarm:{alarm_name}'
                if alarm_key in self.active_alarms:
                    self.active_alarms[alarm_key]['status'
                        ] = AlarmStatus.SILENCED.value
                self._record_alarm_history(self.rules[alarm_name], {
                    'silenced_by': user_id, 'duration': duration}, 'silenced')

    def get_active_alarms(self) ->List[Dict[str, Any]]:
        _('monitoring_alarm_system.message.get_list_of_active_alarms')
        with self._lock:
            return [{**alarm, 'rule': self.rules[alarm['rule_name']].
                __dict__} for alarm in self.active_alarms.values()]

    def get_alarm_history(self, hours: int=24) ->List[Dict[str, Any]]:
        _('monitoring_alarm_system.message.get_alarm_history_for_specifie')
        cutoff_time = time.time() - hours * 3600
        history = [entry for entry in self.alarm_history if entry[
            'timestamp'] > cutoff_time]
        return sorted(history, key=lambda x: x['timestamp'], reverse=True)

    def start_monitoring(self):
        _('monitoring_alarm_system.label.start_alarm_monitoring')
        if self._monitoring_thread is None:
            self._monitoring_thread = threading.Thread(target=self.
                _monitor_loop, daemon=True)
            self._monitoring_thread.start()

    def stop_monitoring(self):
        _('monitoring_alarm_system.label.stop_alarm_monitoring')
        self._stop_monitoring.set()
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5)

    def _monitor_loop(self):
        _('monitoring_performance_monitor.label.background_monitoring_loop')
        while not self._stop_monitoring.is_set():
            try:
                self.evaluate_metrics()
                self._stop_monitoring.wait(30)
            except Exception as e:
                logger.error(f'Error in alarm monitoring loop: {str(e)}')


def init_alarm_system(app: Flask, redis_client: redis.Redis, db_session:
    sessionmaker):
    _('monitoring_alarm_system.label.initialize_alarm_system')
    alarm_system = AlarmSystem(app, redis_client, db_session)
    app.alarm_system = alarm_system

    @app.route('/api/alarms/active')
    def get_active_alarms():
        _('monitoring_alarm_system.message.get_active_alarms_endpoint')
        return {'alarms': alarm_system.get_active_alarms()}

    @app.route('/api/alarms/history')
    def get_alarm_history():
        _('monitoring_alarm_system.message.get_alarm_history_endpoint')
        hours = int(request.args.get('hours', 24))
        return {'history': alarm_system.get_alarm_history(hours)}

    @app.route('/api/alarms/<alarm_name>/acknowledge', methods=['POST'])
    def acknowledge_alarm(alarm_name):
        _('monitoring_alarm_system.label.acknowledge_alarm_endpoint')
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        alarm_system.acknowledge_alarm(alarm_name, user_id)
        return {'status': 'acknowledged'}

    @app.route('/api/alarms/<alarm_name>/silence', methods=['POST'])
    def silence_alarm(alarm_name):
        _('monitoring_alarm_system.label.silence_alarm_endpoint')
        duration = int(request.json.get('duration', 3600))
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        alarm_system.silence_alarm(alarm_name, duration, user_id)
        return {'status': 'silenced', 'duration': duration}
    return alarm_system
