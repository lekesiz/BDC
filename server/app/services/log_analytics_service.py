"""
Automated Log Analytics Service for BDC Application
Provides intelligent log analysis, pattern detection, and trend reporting
"""

import json
import logging
import re
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import redis
from sqlalchemy import create_engine, text
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from app.services.alert_service import alert_service, AlertSeverity
from app.utils.logger import get_logger

logger = get_logger(__name__)

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AnalysisType(Enum):
    """Type of log analysis"""
    ERROR_PATTERN = "error_pattern"
    PERFORMANCE_TREND = "performance_trend"
    SECURITY_INCIDENT = "security_incident"
    USAGE_PATTERN = "usage_pattern"
    ANOMALY_DETECTION = "anomaly_detection"

@dataclass
class LogEntry:
    """Standardized log entry structure"""
    timestamp: datetime
    level: LogLevel
    message: str
    source: str
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        return data

@dataclass
class AnalysisResult:
    """Result of log analysis"""
    analysis_type: AnalysisType
    severity: AlertSeverity
    title: str
    summary: str
    details: Dict[str, Any]
    affected_period: Tuple[datetime, datetime]
    log_count: int
    correlation_ids: List[str]
    recommendations: List[str]
    confidence_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['analysis_type'] = self.analysis_type.value
        data['severity'] = self.severity.value
        data['affected_period'] = [
            self.affected_period[0].isoformat(),
            self.affected_period[1].isoformat()
        ]
        return data

class LogAnalyticsService:
    """
    Advanced log analytics service with machine learning capabilities
    """
    
    def __init__(self):
        self.es_client = None
        self.redis_client = None
        self.enabled = False
        
        # Analysis configuration
        self.analysis_interval = 300  # 5 minutes
        self.retention_days = 30
        self.min_pattern_frequency = 5
        self.anomaly_threshold = 2.0  # Standard deviations
        
        # Pattern recognition
        self.error_patterns = {}
        self.performance_baselines = {}
        self.security_indicators = set()
        
        # ML models
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.clustering_model = DBSCAN(eps=0.3, min_samples=5)
        self.topic_model = LatentDirichletAllocation(n_components=10, random_state=42)
        
        # Analysis cache
        self.analysis_cache = {}
        self.cache_duration = 1800  # 30 minutes
        
        # Background processing
        self.analysis_executor = ThreadPoolExecutor(max_workers=4)
        self.running = False
        
        # Initialize if analytics is enabled
        if self._should_enable():
            self.initialize()
    
    def _should_enable(self) -> bool:
        """Check if log analytics should be enabled"""
        import os
        return os.getenv('LOG_ANALYTICS_ENABLED', 'true').lower() == 'true'
    
    def initialize(self):
        """Initialize the log analytics service"""
        try:
            # Initialize Elasticsearch client
            self._init_elasticsearch()
            
            # Initialize Redis client
            self._init_redis()
            
            # Load security indicators
            self._load_security_indicators()
            
            # Start background analysis
            self._start_background_analysis()
            
            self.enabled = True
            logger.info("Log analytics service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize log analytics service: {str(e)}")
            self.enabled = False
    
    def _init_elasticsearch(self):
        """Initialize Elasticsearch connection"""
        import os
        
        es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        es_port = int(os.getenv('ELASTICSEARCH_PORT', '9200'))
        
        self.es_client = Elasticsearch([
            {'host': es_host, 'port': es_port}
        ])
        
        # Test connection
        if not self.es_client.ping():
            raise Exception("Cannot connect to Elasticsearch")
        
        logger.info("Elasticsearch connection established")
    
    def _init_redis(self):
        """Initialize Redis connection"""
        import os
        
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        self.redis_client = redis.from_url(redis_url)
        
        # Test connection
        self.redis_client.ping()
        
        logger.info("Redis connection established")
    
    def _load_security_indicators(self):
        """Load security threat indicators"""
        self.security_indicators = {
            # Authentication threats
            'failed login', 'brute force', 'password attack',
            'unauthorized access', 'privilege escalation',
            
            # Injection attacks
            'sql injection', 'xss attack', 'command injection',
            'script injection', 'code injection',
            
            # System threats
            'malware', 'virus', 'trojan', 'backdoor',
            'suspicious activity', 'anomalous behavior',
            
            # Network threats
            'ddos', 'port scan', 'network intrusion',
            'suspicious ip', 'blocked connection',
            
            # Data threats
            'data breach', 'data leak', 'unauthorized export',
            'sensitive data access', 'data exfiltration'
        }
    
    def _start_background_analysis(self):
        """Start background analysis thread"""
        self.running = True
        
        def analysis_loop():
            while self.running:
                try:
                    self.run_periodic_analysis()
                    time.sleep(self.analysis_interval)
                except Exception as e:
                    logger.error(f"Error in background analysis: {str(e)}")
                    time.sleep(60)  # Wait before retrying
        
        analysis_thread = threading.Thread(target=analysis_loop, daemon=True)
        analysis_thread.start()
        
        logger.info("Background analysis started")
    
    def stop(self):
        """Stop background analysis"""
        self.running = False
        self.analysis_executor.shutdown(wait=True)
    
    def get_logs(self, 
                 start_time: datetime,
                 end_time: datetime,
                 log_levels: List[LogLevel] = None,
                 sources: List[str] = None,
                 max_logs: int = 10000) -> List[LogEntry]:
        """Retrieve logs from Elasticsearch"""
        if not self.es_client:
            return []
        
        query = {
            "bool": {
                "must": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time.isoformat(),
                                "lte": end_time.isoformat()
                            }
                        }
                    }
                ]
            }
        }
        
        # Add log level filter
        if log_levels:
            query["bool"]["must"].append({
                "terms": {
                    "level": [level.value for level in log_levels]
                }
            })
        
        # Add source filter
        if sources:
            query["bool"]["must"].append({
                "terms": {
                    "source": sources
                }
            })
        
        try:
            response = self.es_client.search(
                index="bdc-*",
                body={
                    "query": query,
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "size": max_logs
                }
            )
            
            logs = []
            for hit in response['hits']['hits']:
                source_data = hit['_source']
                
                log_entry = LogEntry(
                    timestamp=datetime.fromisoformat(source_data.get('@timestamp', '')),
                    level=LogLevel(source_data.get('level', 'INFO')),
                    message=source_data.get('message', ''),
                    source=source_data.get('source', 'unknown'),
                    correlation_id=source_data.get('correlation_id'),
                    user_id=source_data.get('user_id'),
                    request_id=source_data.get('request_id'),
                    metadata=source_data.get('metadata', {})
                )
                logs.append(log_entry)
            
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving logs: {str(e)}")
            return []
    
    def analyze_error_patterns(self, time_window: int = 3600) -> List[AnalysisResult]:
        """Analyze error patterns in logs"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get error logs
        error_logs = self.get_logs(
            start_time=start_time,
            end_time=end_time,
            log_levels=[LogLevel.ERROR, LogLevel.CRITICAL]
        )
        
        if len(error_logs) < self.min_pattern_frequency:
            return []
        
        results = []
        
        # Group errors by similarity
        error_groups = self._group_similar_errors(error_logs)
        
        for group_id, group_logs in error_groups.items():
            if len(group_logs) >= self.min_pattern_frequency:
                result = self._analyze_error_group(group_logs, start_time, end_time)
                if result:
                    results.append(result)
        
        return results
    
    def analyze_performance_trends(self, time_window: int = 3600) -> List[AnalysisResult]:
        """Analyze performance trends"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get performance-related logs
        perf_logs = self.get_logs(
            start_time=start_time,
            end_time=end_time,
            sources=['flask-app', 'database', 'cache']
        )
        
        results = []
        
        # Analyze response times
        response_time_analysis = self._analyze_response_times(perf_logs, start_time, end_time)
        if response_time_analysis:
            results.append(response_time_analysis)
        
        # Analyze database performance
        db_analysis = self._analyze_database_performance(perf_logs, start_time, end_time)
        if db_analysis:
            results.append(db_analysis)
        
        # Analyze cache performance
        cache_analysis = self._analyze_cache_performance(perf_logs, start_time, end_time)
        if cache_analysis:
            results.append(cache_analysis)
        
        return results
    
    def analyze_security_incidents(self, time_window: int = 3600) -> List[AnalysisResult]:
        """Analyze security-related incidents"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get all logs for security analysis
        all_logs = self.get_logs(
            start_time=start_time,
            end_time=end_time
        )
        
        security_logs = []
        for log in all_logs:
            if self._is_security_related(log):
                security_logs.append(log)
        
        if not security_logs:
            return []
        
        results = []
        
        # Analyze authentication failures
        auth_analysis = self._analyze_authentication_failures(security_logs, start_time, end_time)
        if auth_analysis:
            results.append(auth_analysis)
        
        # Analyze suspicious activities
        suspicious_analysis = self._analyze_suspicious_activities(security_logs, start_time, end_time)
        if suspicious_analysis:
            results.append(suspicious_analysis)
        
        return results
    
    def analyze_usage_patterns(self, time_window: int = 86400) -> List[AnalysisResult]:
        """Analyze usage patterns (24 hour window)"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get application logs
        app_logs = self.get_logs(
            start_time=start_time,
            end_time=end_time,
            log_levels=[LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        )
        
        results = []
        
        # Analyze user activity patterns
        user_activity = self._analyze_user_activity(app_logs, start_time, end_time)
        if user_activity:
            results.append(user_activity)
        
        # Analyze API usage patterns
        api_usage = self._analyze_api_usage(app_logs, start_time, end_time)
        if api_usage:
            results.append(api_usage)
        
        return results
    
    def detect_anomalies(self, time_window: int = 3600) -> List[AnalysisResult]:
        """Detect anomalies in log patterns"""
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(seconds=time_window)
        
        # Get recent logs
        recent_logs = self.get_logs(
            start_time=start_time,
            end_time=end_time
        )
        
        if len(recent_logs) < 100:  # Need sufficient data for anomaly detection
            return []
        
        results = []
        
        # Detect volume anomalies
        volume_anomaly = self._detect_volume_anomaly(recent_logs, start_time, end_time)
        if volume_anomaly:
            results.append(volume_anomaly)
        
        # Detect pattern anomalies
        pattern_anomaly = self._detect_pattern_anomaly(recent_logs, start_time, end_time)
        if pattern_anomaly:
            results.append(pattern_anomaly)
        
        return results
    
    def _group_similar_errors(self, error_logs: List[LogEntry]) -> Dict[str, List[LogEntry]]:
        """Group similar error messages using TF-IDF and clustering"""
        if len(error_logs) < 2:
            return {}
        
        # Extract error messages
        messages = [log.message for log in error_logs]
        
        try:
            # Vectorize messages
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(messages)
            
            # Cluster similar messages
            clusters = self.clustering_model.fit_predict(tfidf_matrix)
            
            # Group by cluster
            groups = defaultdict(list)
            for i, cluster_id in enumerate(clusters):
                if cluster_id != -1:  # -1 indicates noise/outlier
                    groups[f"cluster_{cluster_id}"].append(error_logs[i])
            
            return dict(groups)
            
        except Exception as e:
            logger.error(f"Error clustering error messages: {str(e)}")
            # Fallback: group by exact message
            groups = defaultdict(list)
            for log in error_logs:
                groups[hashlib.md5(log.message.encode()).hexdigest()[:8]].append(log)
            return dict(groups)
    
    def _analyze_error_group(self, 
                           error_logs: List[LogEntry],
                           start_time: datetime,
                           end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze a group of similar errors"""
        if not error_logs:
            return None
        
        # Extract common patterns
        messages = [log.message for log in error_logs]
        common_message = self._extract_common_pattern(messages)
        
        # Determine severity based on frequency and error level
        error_count = len(error_logs)
        critical_count = sum(1 for log in error_logs if log.level == LogLevel.CRITICAL)
        
        if critical_count > 0 or error_count > 50:
            severity = AlertSeverity.CRITICAL
        elif error_count > 20:
            severity = AlertSeverity.HIGH
        elif error_count > 10:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        # Get affected users and correlation IDs
        correlation_ids = list(set(log.correlation_id for log in error_logs if log.correlation_id))
        affected_users = list(set(log.user_id for log in error_logs if log.user_id))
        
        # Generate recommendations
        recommendations = self._generate_error_recommendations(error_logs, common_message)
        
        return AnalysisResult(
            analysis_type=AnalysisType.ERROR_PATTERN,
            severity=severity,
            title=f"Recurring Error Pattern Detected",
            summary=f"Found {error_count} similar errors: {common_message[:100]}...",
            details={
                "error_count": error_count,
                "critical_count": critical_count,
                "common_pattern": common_message,
                "affected_users_count": len(affected_users),
                "sources": list(set(log.source for log in error_logs)),
                "first_occurrence": min(log.timestamp for log in error_logs).isoformat(),
                "last_occurrence": max(log.timestamp for log in error_logs).isoformat(),
                "frequency": error_count / ((end_time - start_time).total_seconds() / 60),  # per minute
            },
            affected_period=(start_time, end_time),
            log_count=error_count,
            correlation_ids=correlation_ids[:10],  # Limit to 10
            recommendations=recommendations,
            confidence_score=min(0.9, error_count / 100)  # Higher confidence with more occurrences
        )
    
    def _analyze_response_times(self,
                              logs: List[LogEntry],
                              start_time: datetime,
                              end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze response time trends"""
        # Extract response times from logs
        response_times = []
        for log in logs:
            if 'response_time' in str(log.message).lower():
                # Extract numeric response time
                import re
                match = re.search(r'(\d+\.?\d*)\s*(ms|milliseconds|s|seconds)', log.message.lower())
                if match:
                    time_value = float(match.group(1))
                    unit = match.group(2)
                    
                    # Convert to milliseconds
                    if unit in ['s', 'seconds']:
                        time_value *= 1000
                    
                    response_times.append((log.timestamp, time_value))
        
        if len(response_times) < 10:
            return None
        
        # Calculate statistics
        times = [rt[1] for rt in response_times]
        avg_response_time = np.mean(times)
        p95_response_time = np.percentile(times, 95)
        p99_response_time = np.percentile(times, 99)
        
        # Check against thresholds
        if avg_response_time > 5000 or p95_response_time > 10000:  # 5s avg, 10s p95
            severity = AlertSeverity.HIGH
        elif avg_response_time > 2000 or p95_response_time > 5000:  # 2s avg, 5s p95
            severity = AlertSeverity.MEDIUM
        else:
            return None  # Performance is acceptable
        
        return AnalysisResult(
            analysis_type=AnalysisType.PERFORMANCE_TREND,
            severity=severity,
            title="High Response Time Detected",
            summary=f"Average response time: {avg_response_time:.0f}ms, P95: {p95_response_time:.0f}ms",
            details={
                "avg_response_time": avg_response_time,
                "p50_response_time": np.percentile(times, 50),
                "p95_response_time": p95_response_time,
                "p99_response_time": p99_response_time,
                "max_response_time": max(times),
                "sample_count": len(times)
            },
            affected_period=(start_time, end_time),
            log_count=len(response_times),
            correlation_ids=[],
            recommendations=[
                "Check database query performance",
                "Review application code for bottlenecks",
                "Consider scaling infrastructure",
                "Enable caching for slow operations"
            ],
            confidence_score=min(0.8, len(times) / 100)
        )
    
    def _analyze_database_performance(self,
                                    logs: List[LogEntry],
                                    start_time: datetime,
                                    end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze database performance from logs"""
        db_logs = [log for log in logs if 'database' in log.source.lower() or 'sql' in log.message.lower()]
        
        if len(db_logs) < 5:
            return None
        
        # Analyze database errors
        db_errors = [log for log in db_logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        
        if len(db_errors) > len(db_logs) * 0.1:  # More than 10% errors
            return AnalysisResult(
                analysis_type=AnalysisType.PERFORMANCE_TREND,
                severity=AlertSeverity.HIGH,
                title="High Database Error Rate",
                summary=f"Database error rate: {len(db_errors)/len(db_logs)*100:.1f}%",
                details={
                    "total_db_operations": len(db_logs),
                    "error_count": len(db_errors),
                    "error_rate": len(db_errors) / len(db_logs),
                    "common_errors": self._get_common_patterns([log.message for log in db_errors])
                },
                affected_period=(start_time, end_time),
                log_count=len(db_errors),
                correlation_ids=[log.correlation_id for log in db_errors if log.correlation_id][:10],
                recommendations=[
                    "Check database connectivity",
                    "Review slow query logs",
                    "Monitor database resource usage",
                    "Consider connection pooling optimization"
                ],
                confidence_score=0.8
            )
        
        return None
    
    def _analyze_cache_performance(self,
                                 logs: List[LogEntry],
                                 start_time: datetime,
                                 end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze cache performance from logs"""
        cache_logs = [log for log in logs if 'cache' in log.source.lower() or 'redis' in log.message.lower()]
        
        if len(cache_logs) < 5:
            return None
        
        # Look for cache miss patterns
        cache_misses = [log for log in cache_logs if 'miss' in log.message.lower()]
        
        if len(cache_misses) > len(cache_logs) * 0.8:  # More than 80% misses
            return AnalysisResult(
                analysis_type=AnalysisType.PERFORMANCE_TREND,
                severity=AlertSeverity.MEDIUM,
                title="High Cache Miss Rate",
                summary=f"Cache miss rate: {len(cache_misses)/len(cache_logs)*100:.1f}%",
                details={
                    "total_cache_operations": len(cache_logs),
                    "cache_misses": len(cache_misses),
                    "miss_rate": len(cache_misses) / len(cache_logs)
                },
                affected_period=(start_time, end_time),
                log_count=len(cache_misses),
                correlation_ids=[],
                recommendations=[
                    "Review cache key strategies",
                    "Check cache expiration policies",
                    "Consider increasing cache size",
                    "Analyze cache hit patterns"
                ],
                confidence_score=0.7
            )
        
        return None
    
    def _is_security_related(self, log: LogEntry) -> bool:
        """Check if a log entry is security-related"""
        message_lower = log.message.lower()
        
        # Check for security indicators
        for indicator in self.security_indicators:
            if indicator in message_lower:
                return True
        
        # Check for authentication-related logs
        if any(keyword in message_lower for keyword in ['login', 'auth', 'permission', 'access']):
            return True
        
        # Check for error logs from security components
        if log.level in [LogLevel.ERROR, LogLevel.CRITICAL] and 'security' in log.source.lower():
            return True
        
        return False
    
    def _analyze_authentication_failures(self,
                                       security_logs: List[LogEntry],
                                       start_time: datetime,
                                       end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze authentication failure patterns"""
        auth_failures = [
            log for log in security_logs
            if any(keyword in log.message.lower() for keyword in ['login failed', 'authentication failed', 'invalid credentials'])
        ]
        
        if len(auth_failures) < 5:
            return None
        
        # Analyze by IP/user patterns
        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        ip_counts = Counter()
        user_counts = Counter()
        
        for log in auth_failures:
            # Extract IP addresses
            ips = ip_pattern.findall(log.message)
            for ip in ips:
                ip_counts[ip] += 1
            
            # Count by user ID
            if log.user_id:
                user_counts[log.user_id] += 1
        
        # Check for potential brute force attacks
        suspicious_ips = [ip for ip, count in ip_counts.items() if count >= 10]
        
        if suspicious_ips:
            severity = AlertSeverity.HIGH
        elif len(auth_failures) > 20:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        return AnalysisResult(
            analysis_type=AnalysisType.SECURITY_INCIDENT,
            severity=severity,
            title="Authentication Failure Pattern Detected",
            summary=f"Detected {len(auth_failures)} authentication failures",
            details={
                "total_failures": len(auth_failures),
                "suspicious_ips": suspicious_ips,
                "affected_users": len(user_counts),
                "top_failed_ips": dict(ip_counts.most_common(5)),
                "failure_rate": len(auth_failures) / ((end_time - start_time).total_seconds() / 60)
            },
            affected_period=(start_time, end_time),
            log_count=len(auth_failures),
            correlation_ids=[log.correlation_id for log in auth_failures if log.correlation_id][:10],
            recommendations=[
                "Block suspicious IP addresses",
                "Implement account lockout policies",
                "Enable multi-factor authentication",
                "Monitor for credential stuffing attacks",
                "Review authentication logs"
            ],
            confidence_score=0.9
        )
    
    def _analyze_suspicious_activities(self,
                                     security_logs: List[LogEntry],
                                     start_time: datetime,
                                     end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze suspicious activity patterns"""
        suspicious_logs = [
            log for log in security_logs
            if any(indicator in log.message.lower() for indicator in ['suspicious', 'anomalous', 'blocked', 'denied'])
        ]
        
        if len(suspicious_logs) < 3:
            return None
        
        # Analyze patterns
        activity_types = Counter()
        for log in suspicious_logs:
            # Categorize suspicious activities
            message_lower = log.message.lower()
            if 'ip' in message_lower or 'address' in message_lower:
                activity_types['suspicious_ip'] += 1
            elif 'request' in message_lower:
                activity_types['suspicious_request'] += 1
            elif 'access' in message_lower:
                activity_types['unauthorized_access'] += 1
            else:
                activity_types['other'] += 1
        
        severity = AlertSeverity.HIGH if len(suspicious_logs) > 10 else AlertSeverity.MEDIUM
        
        return AnalysisResult(
            analysis_type=AnalysisType.SECURITY_INCIDENT,
            severity=severity,
            title="Suspicious Activity Detected",
            summary=f"Detected {len(suspicious_logs)} suspicious activities",
            details={
                "total_suspicious": len(suspicious_logs),
                "activity_breakdown": dict(activity_types),
                "sources": list(set(log.source for log in suspicious_logs))
            },
            affected_period=(start_time, end_time),
            log_count=len(suspicious_logs),
            correlation_ids=[log.correlation_id for log in suspicious_logs if log.correlation_id][:10],
            recommendations=[
                "Investigate suspicious patterns",
                "Review security policies",
                "Consider blocking malicious IPs",
                "Enhance monitoring rules"
            ],
            confidence_score=0.8
        )
    
    def _analyze_user_activity(self,
                             logs: List[LogEntry],
                             start_time: datetime,
                             end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze user activity patterns"""
        user_logs = [log for log in logs if log.user_id]
        
        if len(user_logs) < 10:
            return None
        
        # Analyze user activity patterns
        user_activity = Counter(log.user_id for log in user_logs)
        hourly_activity = defaultdict(int)
        
        for log in user_logs:
            hour = log.timestamp.hour
            hourly_activity[hour] += 1
        
        # Find peak activity times
        peak_hour = max(hourly_activity, key=hourly_activity.get)
        peak_activity = hourly_activity[peak_hour]
        
        # Check for unusual patterns
        total_hours = len(hourly_activity)
        avg_activity = sum(hourly_activity.values()) / total_hours if total_hours > 0 else 0
        
        if peak_activity > avg_activity * 3:  # Peak is 3x average
            return AnalysisResult(
                analysis_type=AnalysisType.USAGE_PATTERN,
                severity=AlertSeverity.LOW,
                title="Unusual User Activity Pattern",
                summary=f"Peak activity at hour {peak_hour} with {peak_activity} events",
                details={
                    "total_users": len(user_activity),
                    "total_activity": len(user_logs),
                    "peak_hour": peak_hour,
                    "peak_activity": peak_activity,
                    "average_hourly": avg_activity,
                    "top_users": dict(user_activity.most_common(5))
                },
                affected_period=(start_time, end_time),
                log_count=len(user_logs),
                correlation_ids=[],
                recommendations=[
                    "Monitor capacity during peak hours",
                    "Consider load balancing",
                    "Review user behavior patterns",
                    "Plan for scaling"
                ],
                confidence_score=0.6
            )
        
        return None
    
    def _analyze_api_usage(self,
                         logs: List[LogEntry],
                         start_time: datetime,
                         end_time: datetime) -> Optional[AnalysisResult]:
        """Analyze API usage patterns"""
        api_logs = [log for log in logs if 'api' in log.message.lower() or '/api/' in log.message]
        
        if len(api_logs) < 20:
            return None
        
        # Extract API endpoints
        endpoint_pattern = re.compile(r'/api/[^\s]*')
        endpoint_counts = Counter()
        
        for log in api_logs:
            endpoints = endpoint_pattern.findall(log.message)
            for endpoint in endpoints:
                endpoint_counts[endpoint] += 1
        
        if not endpoint_counts:
            return None
        
        # Find most used endpoints
        top_endpoints = endpoint_counts.most_common(5)
        total_requests = sum(endpoint_counts.values())
        
        return AnalysisResult(
            analysis_type=AnalysisType.USAGE_PATTERN,
            severity=AlertSeverity.LOW,
            title="API Usage Pattern Analysis",
            summary=f"Analyzed {total_requests} API requests across {len(endpoint_counts)} endpoints",
            details={
                "total_requests": total_requests,
                "unique_endpoints": len(endpoint_counts),
                "top_endpoints": [{"endpoint": ep, "count": count} for ep, count in top_endpoints],
                "requests_per_minute": total_requests / ((end_time - start_time).total_seconds() / 60)
            },
            affected_period=(start_time, end_time),
            log_count=len(api_logs),
            correlation_ids=[],
            recommendations=[
                "Monitor high-traffic endpoints",
                "Consider API rate limiting",
                "Optimize popular endpoints",
                "Review API usage policies"
            ],
            confidence_score=0.7
        )
    
    def _detect_volume_anomaly(self,
                             logs: List[LogEntry],
                             start_time: datetime,
                             end_time: datetime) -> Optional[AnalysisResult]:
        """Detect anomalies in log volume"""
        # Group logs by time intervals (5-minute buckets)
        interval_counts = defaultdict(int)
        interval_size = 300  # 5 minutes in seconds
        
        for log in logs:
            interval = int(log.timestamp.timestamp() // interval_size) * interval_size
            interval_counts[interval] += 1
        
        if len(interval_counts) < 3:
            return None
        
        # Calculate statistics
        counts = list(interval_counts.values())
        mean_count = np.mean(counts)
        std_count = np.std(counts)
        
        if std_count == 0:
            return None
        
        # Find anomalous intervals
        anomalous_intervals = []
        for interval, count in interval_counts.items():
            z_score = abs(count - mean_count) / std_count
            if z_score > self.anomaly_threshold:
                anomalous_intervals.append((interval, count, z_score))
        
        if not anomalous_intervals:
            return None
        
        # Determine severity based on how anomalous
        max_z_score = max(z_score for _, _, z_score in anomalous_intervals)
        if max_z_score > 4:
            severity = AlertSeverity.HIGH
        elif max_z_score > 3:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        return AnalysisResult(
            analysis_type=AnalysisType.ANOMALY_DETECTION,
            severity=severity,
            title="Log Volume Anomaly Detected",
            summary=f"Detected {len(anomalous_intervals)} time intervals with anomalous log volumes",
            details={
                "mean_logs_per_interval": mean_count,
                "std_deviation": std_count,
                "anomalous_intervals": len(anomalous_intervals),
                "max_z_score": max_z_score,
                "threshold": self.anomaly_threshold
            },
            affected_period=(start_time, end_time),
            log_count=len(logs),
            correlation_ids=[],
            recommendations=[
                "Investigate cause of log volume spikes",
                "Check for system issues",
                "Review application behavior",
                "Consider log rate limiting"
            ],
            confidence_score=min(0.9, max_z_score / 5)
        )
    
    def _detect_pattern_anomaly(self,
                              logs: List[LogEntry],
                              start_time: datetime,
                              end_time: datetime) -> Optional[AnalysisResult]:
        """Detect anomalies in log patterns using topic modeling"""
        if len(logs) < 50:
            return None
        
        messages = [log.message for log in logs]
        
        try:
            # Vectorize messages
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(messages)
            
            # Apply topic modeling
            topics = self.topic_model.fit_transform(tfidf_matrix)
            
            # Find dominant topics
            topic_weights = np.mean(topics, axis=0)
            dominant_topic = np.argmax(topic_weights)
            
            # Check if there's an unusual concentration in one topic
            max_weight = topic_weights[dominant_topic]
            if max_weight > 0.5:  # More than 50% of logs in one topic
                # Get feature names for the dominant topic
                feature_names = self.tfidf_vectorizer.get_feature_names_out()
                topic_features = self.topic_model.components_[dominant_topic]
                top_features = [feature_names[i] for i in topic_features.argsort()[-10:][::-1]]
                
                return AnalysisResult(
                    analysis_type=AnalysisType.ANOMALY_DETECTION,
                    severity=AlertSeverity.MEDIUM,
                    title="Log Pattern Anomaly Detected",
                    summary=f"Unusual concentration of logs in topic: {', '.join(top_features[:3])}",
                    details={
                        "dominant_topic_weight": max_weight,
                        "dominant_topic_keywords": top_features,
                        "total_topics": len(topic_weights),
                        "logs_analyzed": len(logs)
                    },
                    affected_period=(start_time, end_time),
                    log_count=len(logs),
                    correlation_ids=[],
                    recommendations=[
                        "Investigate unusual log patterns",
                        "Check for system malfunctions",
                        "Review recent code changes",
                        "Monitor for recurring issues"
                    ],
                    confidence_score=max_weight
                )
                
        except Exception as e:
            logger.error(f"Error in pattern anomaly detection: {str(e)}")
        
        return None
    
    def _extract_common_pattern(self, messages: List[str]) -> str:
        """Extract common pattern from error messages"""
        if not messages:
            return ""
        
        if len(messages) == 1:
            return messages[0]
        
        # Find longest common subsequence approach
        common_parts = []
        
        # Split messages into words
        word_sets = [set(msg.split()) for msg in messages]
        
        # Find common words
        common_words = set.intersection(*word_sets) if word_sets else set()
        
        if common_words:
            return " ".join(sorted(common_words)[:10])  # Limit to 10 words
        
        # Fallback: return first message truncated
        return messages[0][:200]
    
    def _generate_error_recommendations(self, 
                                      error_logs: List[LogEntry], 
                                      common_pattern: str) -> List[str]:
        """Generate recommendations based on error patterns"""
        recommendations = []
        
        # Analyze error types
        if 'database' in common_pattern.lower():
            recommendations.extend([
                "Check database connectivity and performance",
                "Review database query optimization",
                "Monitor database resource usage"
            ])
        
        if 'connection' in common_pattern.lower():
            recommendations.extend([
                "Check network connectivity",
                "Review connection pool settings",
                "Monitor external service availability"
            ])
        
        if 'timeout' in common_pattern.lower():
            recommendations.extend([
                "Increase timeout values",
                "Optimize slow operations",
                "Check for blocking operations"
            ])
        
        if 'memory' in common_pattern.lower():
            recommendations.extend([
                "Monitor memory usage",
                "Check for memory leaks",
                "Consider increasing memory allocation"
            ])
        
        # Generic recommendations
        recommendations.extend([
            "Review application logs for more context",
            "Check system resources and performance",
            "Consider implementing retry logic"
        ])
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_common_patterns(self, messages: List[str]) -> List[str]:
        """Get common patterns from a list of messages"""
        if not messages:
            return []
        
        # Count message frequencies
        message_counts = Counter(messages)
        
        # Return top 3 most common messages
        return [msg for msg, count in message_counts.most_common(3)]
    
    def run_periodic_analysis(self):
        """Run periodic log analysis"""
        if not self.enabled:
            return
        
        try:
            logger.info("Starting periodic log analysis")
            
            # Run different types of analysis
            all_results = []
            
            # Error pattern analysis (1 hour window)
            error_results = self.analyze_error_patterns(3600)
            all_results.extend(error_results)
            
            # Performance trend analysis (1 hour window)
            perf_results = self.analyze_performance_trends(3600)
            all_results.extend(perf_results)
            
            # Security incident analysis (1 hour window)
            security_results = self.analyze_security_incidents(3600)
            all_results.extend(security_results)
            
            # Anomaly detection (1 hour window)
            anomaly_results = self.detect_anomalies(3600)
            all_results.extend(anomaly_results)
            
            # Usage pattern analysis (24 hour window, run less frequently)
            current_time = datetime.now()
            if current_time.minute == 0:  # Run once per hour
                usage_results = self.analyze_usage_patterns(86400)
                all_results.extend(usage_results)
            
            # Send alerts for significant findings
            for result in all_results:
                if result.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                    self._send_analysis_alert(result)
            
            # Cache results
            self._cache_analysis_results(all_results)
            
            logger.info(f"Periodic analysis completed. Found {len(all_results)} insights")
            
        except Exception as e:
            logger.error(f"Error in periodic analysis: {str(e)}")
    
    def _send_analysis_alert(self, result: AnalysisResult):
        """Send alert for analysis result"""
        try:
            alert_service.create_alert(
                title=result.title,
                message=result.summary,
                severity=result.severity,
                source="log-analytics",
                event_type=result.analysis_type.value,
                metadata={
                    "analysis_details": result.details,
                    "log_count": result.log_count,
                    "confidence_score": result.confidence_score,
                    "recommendations": result.recommendations
                },
                correlation_id=result.correlation_ids[0] if result.correlation_ids else None
            )
        except Exception as e:
            logger.error(f"Failed to send analysis alert: {str(e)}")
    
    def _cache_analysis_results(self, results: List[AnalysisResult]):
        """Cache analysis results in Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"log_analysis:{int(time.time())}"
            cache_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "results": [result.to_dict() for result in results]
            }
            
            self.redis_client.setex(
                cache_key,
                self.cache_duration,
                json.dumps(cache_data)
            )
            
            # Keep only recent cache entries
            pattern = "log_analysis:*"
            keys = self.redis_client.keys(pattern)
            if len(keys) > 100:  # Keep only last 100 entries
                oldest_keys = sorted(keys)[:len(keys)-100]
                if oldest_keys:
                    self.redis_client.delete(*oldest_keys)
                    
        except Exception as e:
            logger.error(f"Failed to cache analysis results: {str(e)}")
    
    def get_analysis_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get cached analysis results"""
        if not self.redis_client:
            return []
        
        try:
            pattern = "log_analysis:*"
            keys = self.redis_client.keys(pattern)
            
            if not keys:
                return []
            
            # Sort by timestamp and get recent entries
            sorted_keys = sorted(keys)[-limit:]
            
            results = []
            for key in sorted_keys:
                data = self.redis_client.get(key)
                if data:
                    try:
                        parsed_data = json.loads(data)
                        results.append(parsed_data)
                    except json.JSONDecodeError:
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get analysis history: {str(e)}")
            return []

# Global log analytics service instance
log_analytics_service = LogAnalyticsService()