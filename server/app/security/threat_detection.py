"""Enhanced threat detection system for BDC application."""

import re
import time
import ipaddress
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from flask import request, current_app
import redis
import json

logger = logging.getLogger(__name__)


@dataclass
class ThreatIndicator:
    """Represents a potential security threat indicator."""
    threat_type: str
    severity: str  # low, medium, high, critical
    description: str
    source_ip: str
    user_id: Optional[str] = None
    details: Dict = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.details is None:
            self.details = {}


class ThreatDetectionEngine:
    """Advanced threat detection engine with pattern recognition and anomaly detection."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        
        # In-memory tracking for real-time analysis
        self.request_patterns = defaultdict(lambda: deque(maxlen=1000))
        self.failed_logins = defaultdict(lambda: deque(maxlen=100))
        self.suspicious_ips = defaultdict(int)
        self.geo_anomalies = defaultdict(list)
        
        # Threat patterns
        self.xss_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'<iframe', re.IGNORECASE),
            re.compile(r'<object', re.IGNORECASE),
            re.compile(r'<embed', re.IGNORECASE),
            re.compile(r'<applet', re.IGNORECASE),
            re.compile(r'<meta[^>]*http-equiv', re.IGNORECASE),
            re.compile(r'<link[^>]*href.*javascript:', re.IGNORECASE),
        ]
        
        self.sql_injection_patterns = [
            re.compile(r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(from|where|table|database|column)\b)", re.IGNORECASE),
            re.compile(r"(';|\";\s*--)"),
            re.compile(r"(\bor\b\s*\d+\s*=\s*\d+)", re.IGNORECASE),
            re.compile(r"(\band\b\s*\d+\s*=\s*\d+)", re.IGNORECASE),
            re.compile(r"(xp_cmdshell|sp_executesql)", re.IGNORECASE),
            re.compile(r"(waitfor\s+delay|benchmark\s*\()", re.IGNORECASE),
        ]
        
        self.path_traversal_patterns = [
            re.compile(r'\.\./'),
            re.compile(r'\.\.\\'),
            re.compile(r'/etc/passwd'),
            re.compile(r'c:\\windows'),
            re.compile(r'/proc/self'),
        ]
        
        self.command_injection_patterns = [
            re.compile(r'[;&|]\s*(?:ls|cat|rm|mv|cp|wget|curl|nc|python|perl|ruby|php)', re.IGNORECASE),
            re.compile(r'\$\([^)]+\)'),
            re.compile(r'`[^`]+`'),
            re.compile(r'\|{2}'),
            re.compile(r'&&'),
        ]
        
        # Thresholds
        self.FAILED_LOGIN_THRESHOLD = 5
        self.RAPID_REQUEST_THRESHOLD = 100  # requests per minute
        self.SUSPICIOUS_SCORE_THRESHOLD = 10
        self.GEO_ANOMALY_DISTANCE = 1000  # km
        
    def analyze_request(self, request_data: Dict) -> List[ThreatIndicator]:
        """Analyze a request for potential threats."""
        threats = []
        
        # Extract request details
        ip = request_data.get('ip', '0.0.0.0')
        user_id = request_data.get('user_id')
        path = request_data.get('path', '')
        method = request_data.get('method', '')
        headers = request_data.get('headers', {})
        params = request_data.get('params', {})
        body = request_data.get('body', '')
        
        # Check for various threat types
        threats.extend(self._check_injection_attacks(ip, path, params, body))
        threats.extend(self._check_authentication_attacks(ip, user_id))
        threats.extend(self._check_rate_anomalies(ip, user_id))
        threats.extend(self._check_suspicious_headers(ip, headers))
        threats.extend(self._check_geo_anomalies(ip, user_id))
        threats.extend(self._check_behavior_anomalies(ip, user_id, path, method))
        
        # Update suspicious score
        if threats:
            self._update_suspicious_score(ip, len(threats))
        
        return threats
    
    def _check_injection_attacks(self, ip: str, path: str, params: Dict, body: str) -> List[ThreatIndicator]:
        """Check for various injection attacks."""
        threats = []
        
        # Combine all input for analysis
        input_data = f"{path} {json.dumps(params)} {body}"
        
        # XSS Detection
        for pattern in self.xss_patterns:
            if pattern.search(input_data):
                threats.append(ThreatIndicator(
                    threat_type='xss_attempt',
                    severity='high',
                    description='Potential XSS attack detected',
                    source_ip=ip,
                    details={'pattern': pattern.pattern, 'input': input_data[:200]}
                ))
                break
        
        # SQL Injection Detection
        for pattern in self.sql_injection_patterns:
            if pattern.search(input_data):
                threats.append(ThreatIndicator(
                    threat_type='sql_injection_attempt',
                    severity='critical',
                    description='Potential SQL injection attack detected',
                    source_ip=ip,
                    details={'pattern': pattern.pattern, 'input': input_data[:200]}
                ))
                break
        
        # Path Traversal Detection
        for pattern in self.path_traversal_patterns:
            if pattern.search(input_data):
                threats.append(ThreatIndicator(
                    threat_type='path_traversal_attempt',
                    severity='high',
                    description='Potential path traversal attack detected',
                    source_ip=ip,
                    details={'pattern': pattern.pattern, 'path': path}
                ))
                break
        
        # Command Injection Detection
        for pattern in self.command_injection_patterns:
            if pattern.search(input_data):
                threats.append(ThreatIndicator(
                    threat_type='command_injection_attempt',
                    severity='critical',
                    description='Potential command injection attack detected',
                    source_ip=ip,
                    details={'pattern': pattern.pattern, 'input': input_data[:200]}
                ))
                break
        
        return threats
    
    def _check_authentication_attacks(self, ip: str, user_id: Optional[str]) -> List[ThreatIndicator]:
        """Check for authentication-related attacks."""
        threats = []
        
        # Check failed login attempts
        key = f"failed_login:{ip}"
        if self.redis_client:
            failed_count = int(self.redis_client.get(key) or 0)
            if failed_count >= self.FAILED_LOGIN_THRESHOLD:
                threats.append(ThreatIndicator(
                    threat_type='brute_force_attempt',
                    severity='high',
                    description=f'Multiple failed login attempts ({failed_count}) from IP',
                    source_ip=ip,
                    user_id=user_id,
                    details={'failed_count': failed_count}
                ))
        
        return threats
    
    def _check_rate_anomalies(self, ip: str, user_id: Optional[str]) -> List[ThreatIndicator]:
        """Check for rate-based anomalies."""
        threats = []
        
        # Track request rate
        now = time.time()
        self.request_patterns[ip].append(now)
        
        # Count requests in last minute
        one_minute_ago = now - 60
        recent_requests = [t for t in self.request_patterns[ip] if t > one_minute_ago]
        
        if len(recent_requests) > self.RAPID_REQUEST_THRESHOLD:
            threats.append(ThreatIndicator(
                threat_type='rate_anomaly',
                severity='medium',
                description=f'Abnormally high request rate ({len(recent_requests)}/min)',
                source_ip=ip,
                user_id=user_id,
                details={'request_count': len(recent_requests), 'threshold': self.RAPID_REQUEST_THRESHOLD}
            ))
        
        return threats
    
    def _check_suspicious_headers(self, ip: str, headers: Dict) -> List[ThreatIndicator]:
        """Check for suspicious headers."""
        threats = []
        
        # Check for missing or suspicious User-Agent
        user_agent = headers.get('User-Agent', '').lower()
        if not user_agent:
            threats.append(ThreatIndicator(
                threat_type='suspicious_headers',
                severity='low',
                description='Missing User-Agent header',
                source_ip=ip,
                details={'missing_header': 'User-Agent'}
            ))
        elif any(bot in user_agent for bot in ['bot', 'crawler', 'spider', 'scraper']):
            threats.append(ThreatIndicator(
                threat_type='bot_activity',
                severity='low',
                description='Bot or crawler detected',
                source_ip=ip,
                details={'user_agent': user_agent}
            ))
        
        # Check for suspicious referrers
        referrer = headers.get('Referer', '').lower()
        if referrer and any(domain in referrer for domain in ['evil.com', 'malicious.org', 'hack']):
            threats.append(ThreatIndicator(
                threat_type='suspicious_referrer',
                severity='medium',
                description='Suspicious referrer detected',
                source_ip=ip,
                details={'referrer': referrer}
            ))
        
        return threats
    
    def _check_geo_anomalies(self, ip: str, user_id: Optional[str]) -> List[ThreatIndicator]:
        """Check for geographic anomalies."""
        threats = []
        
        # This would integrate with a GeoIP service in production
        # For now, we'll implement a simple check based on rapid location changes
        
        if user_id and self.redis_client:
            key = f"user_location:{user_id}"
            last_location = self.redis_client.get(key)
            
            if last_location:
                # In production, calculate actual distance between IPs
                # For now, just check if IP changed significantly
                last_ip = last_location.decode('utf-8')
                if last_ip != ip:
                    # Check if IPs are in different subnets (simplified check)
                    try:
                        last_network = ipaddress.ip_network(f"{last_ip}/24", strict=False)
                        current_network = ipaddress.ip_network(f"{ip}/24", strict=False)
                        
                        if last_network != current_network:
                            threats.append(ThreatIndicator(
                                threat_type='geo_anomaly',
                                severity='medium',
                                description='Login from unusual location',
                                source_ip=ip,
                                user_id=user_id,
                                details={'previous_ip': last_ip, 'current_ip': ip}
                            ))
                    except:
                        pass
            
            # Update location
            self.redis_client.setex(key, 86400, ip)  # 24 hour TTL
        
        return threats
    
    def _check_behavior_anomalies(self, ip: str, user_id: Optional[str], path: str, method: str) -> List[ThreatIndicator]:
        """Check for behavioral anomalies."""
        threats = []
        
        # Check for access to admin paths from non-admin IPs
        admin_paths = ['/admin', '/api/admin', '/config', '/system']
        if any(path.startswith(admin_path) for admin_path in admin_paths):
            if not self._is_admin_ip(ip):
                threats.append(ThreatIndicator(
                    threat_type='unauthorized_admin_access',
                    severity='high',
                    description='Attempt to access admin path from non-admin IP',
                    source_ip=ip,
                    user_id=user_id,
                    details={'path': path}
                ))
        
        # Check for suspicious file access patterns
        sensitive_extensions = ['.env', '.config', '.key', '.pem', '.sql', '.db']
        if any(path.endswith(ext) for ext in sensitive_extensions):
            threats.append(ThreatIndicator(
                threat_type='sensitive_file_access',
                severity='high',
                description='Attempt to access sensitive file',
                source_ip=ip,
                user_id=user_id,
                details={'path': path}
            ))
        
        return threats
    
    def _update_suspicious_score(self, ip: str, threat_count: int):
        """Update suspicious score for an IP."""
        self.suspicious_ips[ip] += threat_count
        
        # If score exceeds threshold, add to blacklist
        if self.suspicious_ips[ip] >= self.SUSPICIOUS_SCORE_THRESHOLD:
            if self.redis_client:
                self.redis_client.setex(f"blacklist:{ip}", 3600, 1)  # 1 hour ban
    
    def _is_admin_ip(self, ip: str) -> bool:
        """Check if IP is in admin whitelist."""
        admin_ips = current_app.config.get('ADMIN_IP_WHITELIST', [])
        try:
            ip_addr = ipaddress.ip_address(ip)
            for admin_ip in admin_ips:
                if '/' in admin_ip:
                    if ip_addr in ipaddress.ip_network(admin_ip):
                        return True
                elif ip_addr == ipaddress.ip_address(admin_ip):
                    return True
        except:
            pass
        return False
    
    def record_failed_login(self, ip: str, username: str):
        """Record a failed login attempt."""
        # Update in-memory tracking
        self.failed_logins[ip].append({
            'username': username,
            'timestamp': datetime.utcnow()
        })
        
        # Update Redis
        if self.redis_client:
            key = f"failed_login:{ip}"
            self.redis_client.incr(key)
            self.redis_client.expire(key, 300)  # 5 minute window
    
    def is_ip_blacklisted(self, ip: str) -> bool:
        """Check if an IP is blacklisted."""
        if self.redis_client:
            return bool(self.redis_client.get(f"blacklist:{ip}"))
        return self.suspicious_ips.get(ip, 0) >= self.SUSPICIOUS_SCORE_THRESHOLD
    
    def get_threat_summary(self, ip: Optional[str] = None) -> Dict:
        """Get a summary of current threats."""
        summary = {
            'total_suspicious_ips': len(self.suspicious_ips),
            'high_risk_ips': [ip for ip, score in self.suspicious_ips.items() 
                             if score >= self.SUSPICIOUS_SCORE_THRESHOLD],
            'recent_threats': []
        }
        
        if ip:
            summary['ip_details'] = {
                'suspicious_score': self.suspicious_ips.get(ip, 0),
                'failed_logins': len(self.failed_logins.get(ip, [])),
                'request_rate': len([t for t in self.request_patterns.get(ip, []) 
                                   if t > time.time() - 60]),
                'is_blacklisted': self.is_ip_blacklisted(ip)
            }
        
        return summary