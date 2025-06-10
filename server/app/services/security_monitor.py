"""
Security Monitoring and Audit Service for BDC Platform
Provides comprehensive security monitoring, audit logging, and compliance tracking.
"""

import os
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from flask import request, session, current_app
from functools import wraps
import ipaddress
import re
from collections import defaultdict, deque
import time
import jwt

logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    """Security event data structure"""
    id: str
    event_type: str
    severity: str  # low, medium, high, critical
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    risk_score: Optional[int] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = hashlib.md5(f"{self.timestamp}{self.event_type}{self.ip_address}".encode()).hexdigest()

@dataclass
class AuditLogEntry:
    """Audit log entry structure"""
    id: str
    timestamp: datetime
    user_id: Optional[str] = None
    action: str = None
    resource_type: str = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool = True
    details: Optional[Dict[str, Any]] = None

class SecurityMonitorService:
    """Comprehensive security monitoring service"""
    
    def __init__(self, app=None):
        self.app = app
        self.security_events = deque(maxlen=10000)
        self.audit_logs = deque(maxlen=50000)
        self.rate_limit_cache = defaultdict(deque)
        self.suspicious_ips = set()
        self.blocked_ips = set()
        self.failed_login_attempts = defaultdict(list)
        
        # Security thresholds
        self.thresholds = {
            'max_failed_logins': 5,
            'failed_login_window_minutes': 15,
            'rate_limit_requests_per_minute': 100,
            'suspicious_activity_threshold': 10,
            'high_risk_score_threshold': 80
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.security_monitor = self
        
        # Register security middleware
        app.before_request(self._before_request_security_check)
        app.after_request(self._after_request_audit_log)
    
    def _before_request_security_check(self):
        """Security checks before processing request"""
        client_ip = self._get_client_ip()
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            self.log_security_event(
                'blocked_ip_access',
                'high',
                ip_address=client_ip,
                details={'reason': 'IP is blocked due to suspicious activity'}
            )
            return {'error': 'Access denied'}, 403
        
        # Rate limiting check
        if self._is_rate_limited(client_ip):
            self.log_security_event(
                'rate_limit_exceeded',
                'medium',
                ip_address=client_ip,
                details={'endpoint': request.endpoint}
            )
            return {'error': 'Rate limit exceeded'}, 429
        
        # SQL injection detection
        if self._detect_sql_injection():
            self.log_security_event(
                'sql_injection_attempt',
                'critical',
                ip_address=client_ip,
                details={'payload': str(request.get_data())}
            )
            return {'error': 'Malicious request detected'}, 400
        
        # XSS detection
        if self._detect_xss():
            self.log_security_event(
                'xss_attempt',
                'high',
                ip_address=client_ip,
                details={'payload': str(request.get_data())}
            )
            return {'error': 'Malicious request detected'}, 400
    
    def _after_request_audit_log(self, response):
        """Log audit information after request"""
        try:
            # Extract user information
            user_id = None
            if hasattr(request, 'current_user') and request.current_user:
                user_id = request.current_user.id
            
            # Create audit log entry
            audit_entry = AuditLogEntry(
                id=hashlib.md5(f"{datetime.utcnow()}{request.endpoint}{user_id}".encode()).hexdigest(),
                timestamp=datetime.utcnow(),
                user_id=user_id,
                action=f"{request.method} {request.endpoint}",
                ip_address=self._get_client_ip(),
                user_agent=request.headers.get('User-Agent'),
                success=200 <= response.status_code < 400,
                details={
                    'status_code': response.status_code,
                    'content_length': response.content_length,
                    'endpoint': request.endpoint,
                    'method': request.method
                }
            )
            
            self.audit_logs.append(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
        
        return response
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log a security event"""
        try:
            if ip_address is None:
                ip_address = self._get_client_ip()
            
            if endpoint is None and request:
                endpoint = request.endpoint
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(event_type, severity, ip_address, user_id)
            
            event = SecurityEvent(
                id=None,  # Will be generated in __post_init__
                event_type=event_type,
                severity=severity,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                ip_address=ip_address,
                user_agent=request.headers.get('User-Agent') if request else None,
                endpoint=endpoint,
                method=request.method if request else None,
                details=details or {},
                risk_score=risk_score
            )
            
            self.security_events.append(event)
            
            # Take action based on severity and risk score
            self._handle_security_event(event)
            
            logger.warning(f"Security event: {event_type} - {severity} - IP: {ip_address}")
            
        except Exception as e:
            logger.error(f"Failed to log security event: {str(e)}")
    
    def log_audit_event(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log an audit event"""
        try:
            audit_entry = AuditLogEntry(
                id=hashlib.md5(f"{datetime.utcnow()}{action}{user_id}".encode()).hexdigest(),
                timestamp=datetime.utcnow(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=self._get_client_ip(),
                user_agent=request.headers.get('User-Agent') if request else None,
                success=success,
                details=details or {}
            )
            
            self.audit_logs.append(audit_entry)
            
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
    
    def track_failed_login(self, username_or_email: str, ip_address: Optional[str] = None):
        """Track failed login attempts"""
        if ip_address is None:
            ip_address = self._get_client_ip()
        
        key = f"{username_or_email}:{ip_address}"
        now = datetime.utcnow()
        
        # Add failed attempt
        self.failed_login_attempts[key].append(now)
        
        # Clean old attempts
        cutoff = now - timedelta(minutes=self.thresholds['failed_login_window_minutes'])
        self.failed_login_attempts[key] = [
            attempt for attempt in self.failed_login_attempts[key]
            if attempt > cutoff
        ]
        
        # Check if threshold exceeded
        if len(self.failed_login_attempts[key]) >= self.thresholds['max_failed_logins']:
            self.log_security_event(
                'brute_force_attempt',
                'high',
                ip_address=ip_address,
                details={
                    'username': username_or_email,
                    'attempts': len(self.failed_login_attempts[key])
                }
            )
            
            # Add IP to suspicious list
            self.suspicious_ips.add(ip_address)
    
    def track_successful_login(self, user_id: str, ip_address: Optional[str] = None):
        """Track successful login"""
        if ip_address is None:
            ip_address = self._get_client_ip()
        
        # Check for unusual login location/time
        risk_factors = self._analyze_login_risk(user_id, ip_address)
        
        if risk_factors:
            self.log_security_event(
                'unusual_login',
                'medium',
                user_id=user_id,
                ip_address=ip_address,
                details={'risk_factors': risk_factors}
            )
        
        # Clear failed attempts for this user/IP
        key_pattern = f"*:{ip_address}"
        keys_to_clear = [k for k in self.failed_login_attempts.keys() if k.endswith(f":{ip_address}")]
        for key in keys_to_clear:
            del self.failed_login_attempts[key]
    
    def _get_client_ip(self) -> str:
        """Get client IP address"""
        if not request:
            return '127.0.0.1'
        
        # Check for forwarded headers
        forwarded_ips = request.headers.get('X-Forwarded-For')
        if forwarded_ips:
            return forwarded_ips.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr or '127.0.0.1'
    
    def _is_rate_limited(self, ip_address: str) -> bool:
        """Check if IP is rate limited"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        self.rate_limit_cache[ip_address] = deque([
            timestamp for timestamp in self.rate_limit_cache[ip_address]
            if timestamp > minute_ago
        ])
        
        # Add current request
        self.rate_limit_cache[ip_address].append(now)
        
        # Check if over limit
        return len(self.rate_limit_cache[ip_address]) > self.thresholds['rate_limit_requests_per_minute']
    
    def _detect_sql_injection(self) -> bool:
        """Detect potential SQL injection attempts"""
        sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(--|;|\/\*|\*\/)",
            r"(\bOR\b.*=.*\bOR\b)",
            r"(\bAND\b.*=.*\bAND\b)",
            r"(\b1=1\b|\b1=0\b)",
            r"(\bCONCAT\b|\bCOALESCE\b|\bCAST\b)"
        ]
        
        # Check URL parameters
        for value in request.args.values():
            for pattern in sql_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    return True
        
        # Check form data
        if request.is_json and request.json:
            json_str = json.dumps(request.json)
            for pattern in sql_patterns:
                if re.search(pattern, json_str, re.IGNORECASE):
                    return True
        
        return False
    
    def _detect_xss(self) -> bool:
        """Detect potential XSS attempts"""
        xss_patterns = [
            r"<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe\b",
            r"<object\b",
            r"<embed\b",
            r"<link\b.*rel\s*=\s*[\"']?stylesheet",
            r"<style\b"
        ]
        
        # Check URL parameters
        for value in request.args.values():
            for pattern in xss_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    return True
        
        # Check form data
        if request.is_json and request.json:
            json_str = json.dumps(request.json)
            for pattern in xss_patterns:
                if re.search(pattern, json_str, re.IGNORECASE):
                    return True
        
        return False
    
    def _calculate_risk_score(
        self,
        event_type: str,
        severity: str,
        ip_address: str,
        user_id: Optional[str]
    ) -> int:
        """Calculate risk score for security event"""
        score = 0
        
        # Base score by severity
        severity_scores = {
            'low': 10,
            'medium': 30,
            'high': 60,
            'critical': 90
        }
        score += severity_scores.get(severity, 10)
        
        # Event type scores
        event_scores = {
            'sql_injection_attempt': 40,
            'xss_attempt': 35,
            'brute_force_attempt': 30,
            'blocked_ip_access': 25,
            'rate_limit_exceeded': 15,
            'unusual_login': 20,
            'permission_violation': 25
        }
        score += event_scores.get(event_type, 5)
        
        # IP reputation
        if ip_address in self.suspicious_ips:
            score += 20
        if ip_address in self.blocked_ips:
            score += 30
        
        # Recent activity from same IP
        recent_events = [
            event for event in self.security_events
            if event.ip_address == ip_address
            and event.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        score += min(len(recent_events) * 5, 30)
        
        return min(score, 100)
    
    def _handle_security_event(self, event: SecurityEvent):
        """Handle security event based on severity and risk score"""
        if event.severity == 'critical' or event.risk_score >= self.thresholds['high_risk_score_threshold']:
            # Block IP for critical events or high risk scores
            if event.ip_address:
                self.blocked_ips.add(event.ip_address)
                logger.critical(f"Blocked IP {event.ip_address} due to security event: {event.event_type}")
        
        elif event.severity == 'high' or event.risk_score >= 60:
            # Add to suspicious IPs
            if event.ip_address:
                self.suspicious_ips.add(event.ip_address)
    
    def _analyze_login_risk(self, user_id: str, ip_address: str) -> List[str]:
        """Analyze login for risk factors"""
        risk_factors = []
        
        # Check for new IP address
        recent_logins = [
            entry for entry in self.audit_logs
            if entry.user_id == user_id
            and entry.action.startswith('POST /auth/login')
            and entry.success
            and entry.timestamp > datetime.utcnow() - timedelta(days=30)
        ]
        
        known_ips = set(entry.ip_address for entry in recent_logins)
        if ip_address not in known_ips:
            risk_factors.append('new_ip_address')
        
        # Check for unusual time
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:  # Outside normal hours
            risk_factors.append('unusual_time')
        
        # Check geographic location (would need GeoIP service)
        # This is a placeholder for geo-location checking
        # if self._is_unusual_location(ip_address, user_id):
        #     risk_factors.append('unusual_location')
        
        return risk_factors
    
    def get_security_events(
        self,
        hours: int = 24,
        severity_filter: Optional[List[str]] = None,
        event_type_filter: Optional[str] = None
    ) -> List[SecurityEvent]:
        """Get security events"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        events = [
            event for event in self.security_events
            if event.timestamp > cutoff_time
        ]
        
        if severity_filter:
            events = [e for e in events if e.severity in severity_filter]
        
        if event_type_filter:
            events = [e for e in events if event_type_filter in e.event_type]
        
        return sorted(events, key=lambda x: x.timestamp, reverse=True)
    
    def get_audit_logs(
        self,
        hours: int = 24,
        user_id: Optional[str] = None,
        action_filter: Optional[str] = None,
        success_only: Optional[bool] = None
    ) -> List[AuditLogEntry]:
        """Get audit logs"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        logs = [
            log for log in self.audit_logs
            if log.timestamp > cutoff_time
        ]
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        if action_filter:
            logs = [l for l in logs if action_filter in l.action]
        
        if success_only is not None:
            logs = [l for l in logs if l.success == success_only]
        
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)
    
    def get_security_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get security metrics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_events = [
            event for event in self.security_events
            if event.timestamp > cutoff_time
        ]
        
        recent_logs = [
            log for log in self.audit_logs
            if log.timestamp > cutoff_time
        ]
        
        return {
            'total_security_events': len(recent_events),
            'events_by_severity': {
                'critical': len([e for e in recent_events if e.severity == 'critical']),
                'high': len([e for e in recent_events if e.severity == 'high']),
                'medium': len([e for e in recent_events if e.severity == 'medium']),
                'low': len([e for e in recent_events if e.severity == 'low'])
            },
            'events_by_type': {
                event_type: len([e for e in recent_events if e.event_type == event_type])
                for event_type in set(e.event_type for e in recent_events)
            },
            'total_audit_logs': len(recent_logs),
            'failed_operations': len([l for l in recent_logs if not l.success]),
            'unique_ips': len(set(e.ip_address for e in recent_events if e.ip_address)),
            'blocked_ips_count': len(self.blocked_ips),
            'suspicious_ips_count': len(self.suspicious_ips),
            'active_sessions': len(self.failed_login_attempts),
            'avg_risk_score': sum(e.risk_score for e in recent_events if e.risk_score) / len(recent_events) if recent_events else 0
        }
    
    def block_ip(self, ip_address: str, reason: str = 'Manual block'):
        """Manually block an IP address"""
        self.blocked_ips.add(ip_address)
        self.log_security_event(
            'manual_ip_block',
            'high',
            ip_address=ip_address,
            details={'reason': reason}
        )
    
    def unblock_ip(self, ip_address: str):
        """Unblock an IP address"""
        self.blocked_ips.discard(ip_address)
        self.suspicious_ips.discard(ip_address)
        self.log_security_event(
            'ip_unblocked',
            'low',
            ip_address=ip_address
        )
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of blocked IPs"""
        return list(self.blocked_ips)
    
    def get_suspicious_ips(self) -> List[str]:
        """Get list of suspicious IPs"""
        return list(self.suspicious_ips)

# Global instance
security_monitor = SecurityMonitorService()