"""
Analytics System Configuration

Central configuration for all analytics components including
settings, thresholds, and environment-specific parameters.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration for analytics"""
    connection_pool_size: int = 10
    query_timeout: int = 30
    batch_size: int = 1000
    enable_query_cache: bool = True
    cache_ttl: int = 3600  # 1 hour


@dataclass
class DashboardConfig:
    """Real-time dashboard configuration"""
    update_interval: int = 30  # seconds
    max_connections: int = 100
    enable_websocket: bool = True
    chart_data_points: int = 100
    enable_caching: bool = True
    cache_duration: int = 900  # 15 minutes


@dataclass
class PredictiveConfig:
    """Predictive analytics configuration"""
    model_retrain_interval: int = 24  # hours
    prediction_confidence_threshold: float = 0.7
    enable_auto_retrain: bool = True
    model_cache_duration: int = 86400  # 24 hours
    feature_importance_threshold: float = 0.05
    cross_validation_folds: int = 5


@dataclass
class BehaviorConfig:
    """User behavior analytics configuration"""
    cohort_analysis_months: int = 12
    engagement_calculation_window: int = 30  # days
    journey_analysis_limit: int = 1000
    session_timeout: int = 1800  # 30 minutes
    enable_real_time_tracking: bool = True


@dataclass
class PerformanceConfig:
    """Performance metrics configuration"""
    metric_collection_interval: int = 300  # 5 minutes
    alert_check_interval: int = 60  # 1 minute
    historical_data_retention: int = 90  # days
    enable_predictive_alerts: bool = True
    health_score_weights: Dict[str, float] = None
    
    def __post_init__(self):
        if self.health_score_weights is None:
            self.health_score_weights = {
                'business_metrics': 0.3,
                'operational_metrics': 0.3,
                'technical_metrics': 0.25,
                'user_experience_metrics': 0.15
            }


@dataclass
class ReportConfig:
    """Report generation configuration"""
    default_template: str = "executive_summary"
    max_report_size: int = 50 * 1024 * 1024  # 50MB
    report_retention_days: int = 30
    enable_email_delivery: bool = False
    enable_auto_scheduling: bool = True
    concurrent_report_limit: int = 5


@dataclass
class ExportConfig:
    """Data export configuration"""
    max_export_rows: int = 1000000
    export_timeout: int = 3600  # 1 hour
    enable_compression: bool = True
    compression_format: str = "gzip"
    chunk_size: int = 10000
    enable_background_export: bool = True


@dataclass
class AlertConfig:
    """Alert system configuration"""
    enable_email_alerts: bool = False
    enable_slack_alerts: bool = False
    alert_cooldown: int = 300  # 5 minutes
    max_alerts_per_hour: int = 10
    escalation_threshold: int = 3
    
    # Threshold configurations
    critical_thresholds: Dict[str, float] = None
    warning_thresholds: Dict[str, float] = None
    
    def __post_init__(self):
        if self.critical_thresholds is None:
            self.critical_thresholds = {
                'system_uptime': 95.0,
                'response_time_avg': 1000.0,  # ms
                'error_rate': 5.0,  # %
                'user_retention_rate': 60.0,  # %
                'appointment_completion_rate': 70.0  # %
            }
        
        if self.warning_thresholds is None:
            self.warning_thresholds = {
                'system_uptime': 98.0,
                'response_time_avg': 500.0,  # ms
                'error_rate': 2.0,  # %
                'user_retention_rate': 75.0,  # %
                'appointment_completion_rate': 85.0  # %
            }


@dataclass
class SecurityConfig:
    """Security configuration for analytics"""
    enable_data_anonymization: bool = True
    enable_audit_logging: bool = True
    sensitive_fields: List[str] = None
    data_retention_policy: int = 365  # days
    enable_encryption_at_rest: bool = True
    
    def __post_init__(self):
        if self.sensitive_fields is None:
            self.sensitive_fields = [
                'email', 'phone', 'ssn', 'address',
                'personal_details', 'medical_info'
            ]


class AnalyticsConfig:
    """Main analytics configuration class"""
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        self.environment = environment
        
        # Load configurations based on environment
        self.database = self._load_database_config()
        self.dashboard = self._load_dashboard_config()
        self.predictive = self._load_predictive_config()
        self.behavior = self._load_behavior_config()
        self.performance = self._load_performance_config()
        self.reports = self._load_report_config()
        self.exports = self._load_export_config()
        self.alerts = self._load_alert_config()
        self.security = self._load_security_config()
        
        # Environment-specific overrides
        self._apply_environment_overrides()
    
    def _load_database_config(self) -> DatabaseConfig:
        """Load database configuration"""
        return DatabaseConfig(
            connection_pool_size=int(os.getenv('ANALYTICS_DB_POOL_SIZE', '10')),
            query_timeout=int(os.getenv('ANALYTICS_QUERY_TIMEOUT', '30')),
            batch_size=int(os.getenv('ANALYTICS_BATCH_SIZE', '1000')),
            enable_query_cache=os.getenv('ANALYTICS_QUERY_CACHE', 'true').lower() == 'true',
            cache_ttl=int(os.getenv('ANALYTICS_CACHE_TTL', '3600'))
        )
    
    def _load_dashboard_config(self) -> DashboardConfig:
        """Load dashboard configuration"""
        return DashboardConfig(
            update_interval=int(os.getenv('DASHBOARD_UPDATE_INTERVAL', '30')),
            max_connections=int(os.getenv('DASHBOARD_MAX_CONNECTIONS', '100')),
            enable_websocket=os.getenv('DASHBOARD_WEBSOCKET', 'true').lower() == 'true',
            chart_data_points=int(os.getenv('DASHBOARD_CHART_POINTS', '100')),
            enable_caching=os.getenv('DASHBOARD_CACHING', 'true').lower() == 'true',
            cache_duration=int(os.getenv('DASHBOARD_CACHE_DURATION', '900'))
        )
    
    def _load_predictive_config(self) -> PredictiveConfig:
        """Load predictive analytics configuration"""
        return PredictiveConfig(
            model_retrain_interval=int(os.getenv('PREDICTIVE_RETRAIN_INTERVAL', '24')),
            prediction_confidence_threshold=float(os.getenv('PREDICTIVE_CONFIDENCE_THRESHOLD', '0.7')),
            enable_auto_retrain=os.getenv('PREDICTIVE_AUTO_RETRAIN', 'true').lower() == 'true',
            model_cache_duration=int(os.getenv('PREDICTIVE_CACHE_DURATION', '86400')),
            feature_importance_threshold=float(os.getenv('PREDICTIVE_FEATURE_THRESHOLD', '0.05')),
            cross_validation_folds=int(os.getenv('PREDICTIVE_CV_FOLDS', '5'))
        )
    
    def _load_behavior_config(self) -> BehaviorConfig:
        """Load behavior analytics configuration"""
        return BehaviorConfig(
            cohort_analysis_months=int(os.getenv('BEHAVIOR_COHORT_MONTHS', '12')),
            engagement_calculation_window=int(os.getenv('BEHAVIOR_ENGAGEMENT_WINDOW', '30')),
            journey_analysis_limit=int(os.getenv('BEHAVIOR_JOURNEY_LIMIT', '1000')),
            session_timeout=int(os.getenv('BEHAVIOR_SESSION_TIMEOUT', '1800')),
            enable_real_time_tracking=os.getenv('BEHAVIOR_REAL_TIME', 'true').lower() == 'true'
        )
    
    def _load_performance_config(self) -> PerformanceConfig:
        """Load performance metrics configuration"""
        return PerformanceConfig(
            metric_collection_interval=int(os.getenv('PERFORMANCE_COLLECTION_INTERVAL', '300')),
            alert_check_interval=int(os.getenv('PERFORMANCE_ALERT_INTERVAL', '60')),
            historical_data_retention=int(os.getenv('PERFORMANCE_DATA_RETENTION', '90')),
            enable_predictive_alerts=os.getenv('PERFORMANCE_PREDICTIVE_ALERTS', 'true').lower() == 'true'
        )
    
    def _load_report_config(self) -> ReportConfig:
        """Load report generation configuration"""
        return ReportConfig(
            default_template=os.getenv('REPORTS_DEFAULT_TEMPLATE', 'executive_summary'),
            max_report_size=int(os.getenv('REPORTS_MAX_SIZE', str(50 * 1024 * 1024))),
            report_retention_days=int(os.getenv('REPORTS_RETENTION_DAYS', '30')),
            enable_email_delivery=os.getenv('REPORTS_EMAIL_DELIVERY', 'false').lower() == 'true',
            enable_auto_scheduling=os.getenv('REPORTS_AUTO_SCHEDULING', 'true').lower() == 'true',
            concurrent_report_limit=int(os.getenv('REPORTS_CONCURRENT_LIMIT', '5'))
        )
    
    def _load_export_config(self) -> ExportConfig:
        """Load data export configuration"""
        return ExportConfig(
            max_export_rows=int(os.getenv('EXPORT_MAX_ROWS', '1000000')),
            export_timeout=int(os.getenv('EXPORT_TIMEOUT', '3600')),
            enable_compression=os.getenv('EXPORT_COMPRESSION', 'true').lower() == 'true',
            compression_format=os.getenv('EXPORT_COMPRESSION_FORMAT', 'gzip'),
            chunk_size=int(os.getenv('EXPORT_CHUNK_SIZE', '10000')),
            enable_background_export=os.getenv('EXPORT_BACKGROUND', 'true').lower() == 'true'
        )
    
    def _load_alert_config(self) -> AlertConfig:
        """Load alert system configuration"""
        return AlertConfig(
            enable_email_alerts=os.getenv('ALERTS_EMAIL', 'false').lower() == 'true',
            enable_slack_alerts=os.getenv('ALERTS_SLACK', 'false').lower() == 'true',
            alert_cooldown=int(os.getenv('ALERTS_COOLDOWN', '300')),
            max_alerts_per_hour=int(os.getenv('ALERTS_MAX_PER_HOUR', '10')),
            escalation_threshold=int(os.getenv('ALERTS_ESCALATION_THRESHOLD', '3'))
        )
    
    def _load_security_config(self) -> SecurityConfig:
        """Load security configuration"""
        return SecurityConfig(
            enable_data_anonymization=os.getenv('SECURITY_ANONYMIZATION', 'true').lower() == 'true',
            enable_audit_logging=os.getenv('SECURITY_AUDIT_LOGGING', 'true').lower() == 'true',
            data_retention_policy=int(os.getenv('SECURITY_DATA_RETENTION', '365')),
            enable_encryption_at_rest=os.getenv('SECURITY_ENCRYPTION', 'true').lower() == 'true'
        )
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        if self.environment == Environment.DEVELOPMENT:
            # Development overrides
            self.dashboard.update_interval = 10  # Faster updates for development
            self.predictive.enable_auto_retrain = False  # Disable auto-retrain in dev
            self.security.enable_data_anonymization = False  # Disable anonymization in dev
            self.alerts.enable_email_alerts = False  # Disable email alerts in dev
            
        elif self.environment == Environment.STAGING:
            # Staging overrides
            self.dashboard.max_connections = 50  # Reduced capacity for staging
            self.exports.max_export_rows = 100000  # Reduced export limits
            self.alerts.enable_email_alerts = False  # Disable email alerts in staging
            
        elif self.environment == Environment.PRODUCTION:
            # Production overrides
            self.dashboard.enable_caching = True  # Ensure caching is enabled
            self.predictive.enable_auto_retrain = True  # Enable auto-retrain in production
            self.security.enable_data_anonymization = True  # Ensure anonymization in production
            self.alerts.enable_email_alerts = True  # Enable email alerts in production
            self.performance.enable_predictive_alerts = True  # Enable predictive alerts
    
    def get_ml_model_config(self, model_name: str) -> Dict[str, Any]:
        """Get machine learning model specific configuration"""
        base_config = {
            'random_state': 42,
            'n_jobs': -1,
            'validation_split': 0.2
        }
        
        model_configs = {
            'appointment_noshow': {
                **base_config,
                'n_estimators': 100,
                'max_depth': 10,
                'class_weight': 'balanced'
            },
            'user_churn': {
                **base_config,
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 6
            },
            'evaluation_outcome': {
                **base_config,
                'fit_intercept': True,
                'normalize': False
            },
            'engagement_prediction': {
                **base_config,
                'n_estimators': 50,
                'max_depth': 8
            },
            'capacity_forecasting': {
                **base_config,
                'n_estimators': 100,
                'learning_rate': 0.1,
                'max_depth': 6
            }
        }
        
        return model_configs.get(model_name, base_config)
    
    def get_chart_config(self, chart_type: str) -> Dict[str, Any]:
        """Get chart-specific configuration"""
        base_config = {
            'width': 800,
            'height': 400,
            'theme': 'plotly',
            'responsive': True
        }
        
        chart_configs = {
            'line': {
                **base_config,
                'line_smoothing': 0.3,
                'show_markers': True
            },
            'bar': {
                **base_config,
                'orientation': 'vertical',
                'show_values': True
            },
            'pie': {
                **base_config,
                'show_labels': True,
                'show_percent': True
            },
            'heatmap': {
                **base_config,
                'colorscale': 'RdBu',
                'show_colorbar': True
            }
        }
        
        return chart_configs.get(chart_type, base_config)
    
    def get_export_format_config(self, format_type: str) -> Dict[str, Any]:
        """Get export format specific configuration"""
        configs = {
            'csv': {
                'separator': ',',
                'encoding': 'utf-8',
                'include_index': False
            },
            'excel': {
                'engine': 'xlsxwriter',
                'include_charts': True,
                'freeze_panes': (1, 0)
            },
            'json': {
                'indent': 2,
                'ensure_ascii': False,
                'date_format': 'iso'
            },
            'parquet': {
                'compression': 'snappy',
                'index': False
            }
        }
        
        return configs.get(format_type, {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'environment': self.environment.value,
            'database': self.database.__dict__,
            'dashboard': self.dashboard.__dict__,
            'predictive': self.predictive.__dict__,
            'behavior': self.behavior.__dict__,
            'performance': self.performance.__dict__,
            'reports': self.reports.__dict__,
            'exports': self.exports.__dict__,
            'alerts': self.alerts.__dict__,
            'security': self.security.__dict__
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyticsConfig':
        """Create configuration from dictionary"""
        config = cls(Environment(data.get('environment', 'development')))
        
        # Update configurations from dictionary
        for section_name, section_data in data.items():
            if hasattr(config, section_name) and isinstance(section_data, dict):
                section = getattr(config, section_name)
                for key, value in section_data.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
        
        return config


# Global configuration instance
_config = None

def get_analytics_config() -> AnalyticsConfig:
    """Get global analytics configuration instance"""
    global _config
    if _config is None:
        environment = Environment(os.getenv('ANALYTICS_ENVIRONMENT', 'development'))
        _config = AnalyticsConfig(environment)
    return _config


def set_analytics_config(config: AnalyticsConfig):
    """Set global analytics configuration instance"""
    global _config
    _config = config


# Environment-specific configuration presets
DEVELOPMENT_CONFIG = {
    'dashboard': {
        'update_interval': 10,
        'enable_caching': False
    },
    'predictive': {
        'enable_auto_retrain': False,
        'model_retrain_interval': 168  # 1 week
    },
    'security': {
        'enable_data_anonymization': False,
        'enable_audit_logging': False
    },
    'alerts': {
        'enable_email_alerts': False,
        'enable_slack_alerts': False
    }
}

PRODUCTION_CONFIG = {
    'dashboard': {
        'update_interval': 30,
        'enable_caching': True,
        'max_connections': 200
    },
    'predictive': {
        'enable_auto_retrain': True,
        'model_retrain_interval': 24
    },
    'security': {
        'enable_data_anonymization': True,
        'enable_audit_logging': True,
        'enable_encryption_at_rest': True
    },
    'alerts': {
        'enable_email_alerts': True,
        'enable_slack_alerts': True
    },
    'performance': {
        'enable_predictive_alerts': True
    }
}