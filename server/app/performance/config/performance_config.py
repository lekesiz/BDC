"""
Performance Configuration

Central configuration management for all performance optimization settings.
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class OptimizationLevel(Enum):
    BASIC = "basic"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"


@dataclass
class DatabaseConfig:
    """Database optimization configuration"""
    enable_query_optimization: bool = True
    enable_auto_indexing: bool = True
    slow_query_threshold: float = 1.0  # seconds
    connection_pool_size: int = 20
    connection_pool_timeout: int = 30
    enable_query_cache: bool = True
    query_cache_size: int = 1000
    enable_prepared_statements: bool = True
    index_analysis_interval: int = 3600  # 1 hour


@dataclass
class CacheConfig:
    """Caching configuration"""
    enable_redis: bool = True
    redis_url: str = "redis://localhost:6379/0"
    redis_pool_size: int = 50
    enable_memory_cache: bool = True
    memory_cache_size: int = 100 * 1024 * 1024  # 100MB
    default_ttl: int = 3600  # 1 hour
    enable_compression: bool = True
    compression_threshold: int = 1024  # 1KB
    cache_strategy: CacheStrategy = CacheStrategy.LRU
    enable_cache_warming: bool = True
    enable_distributed_cache: bool = False


@dataclass
class APIConfig:
    """API optimization configuration"""
    enable_response_compression: bool = True
    compression_level: int = 6
    compression_threshold: int = 1024  # 1KB
    enable_response_caching: bool = True
    enable_etag: bool = True
    enable_conditional_requests: bool = True
    enable_pagination_optimization: bool = True
    default_page_size: int = 25
    max_page_size: int = 100
    enable_request_batching: bool = True
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 1000
    rate_limit_window: int = 3600  # 1 hour


@dataclass
class MonitoringConfig:
    """Performance monitoring configuration"""
    enable_performance_monitoring: bool = True
    enable_web_vitals: bool = True
    enable_profiling: bool = True
    enable_memory_tracking: bool = True
    monitoring_interval: int = 30  # seconds
    metrics_retention_days: int = 30
    alert_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'response_time_ms': 1000,
        'error_rate_percent': 5,
        'memory_usage_mb': 512,
        'cpu_usage_percent': 80
    })
    enable_real_time_alerts: bool = True
    enable_performance_reports: bool = True


@dataclass
class AssetConfig:
    """Asset optimization configuration"""
    enable_image_optimization: bool = True
    image_quality_jpeg: int = 85
    image_quality_webp: int = 80
    enable_responsive_images: bool = True
    responsive_breakpoints: List[int] = field(default_factory=lambda: [320, 480, 768, 1024, 1920])
    enable_lazy_loading: bool = True
    enable_cdn: bool = False
    cdn_base_url: Optional[str] = None
    enable_asset_versioning: bool = True
    enable_asset_minification: bool = True
    enable_css_optimization: bool = True
    enable_js_optimization: bool = True


@dataclass
class LoadTestConfig:
    """Load testing configuration"""
    enable_load_testing: bool = False
    default_concurrent_users: int = 10
    default_duration_seconds: int = 60
    default_ramp_up_seconds: int = 10
    max_concurrent_users: int = 1000
    enable_stress_testing: bool = False
    enable_spike_testing: bool = False
    test_data_cleanup: bool = True
    generate_reports: bool = True


@dataclass
class SecurityConfig:
    """Performance-related security configuration"""
    enable_rate_limiting: bool = True
    enable_ddos_protection: bool = True
    enable_input_validation: bool = True
    enable_sql_injection_protection: bool = True
    enable_xss_protection: bool = True
    enable_csrf_protection: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    max_upload_size: int = 100 * 1024 * 1024  # 100MB


class PerformanceConfig:
    """
    Central performance configuration manager.
    """
    
    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        config_dict = config_dict or {}
        
        # Load configuration from environment or provided dict
        self.optimization_level = OptimizationLevel(
            config_dict.get('optimization_level', os.getenv('OPTIMIZATION_LEVEL', 'moderate'))
        )
        
        # Initialize component configurations
        self.database = DatabaseConfig(**config_dict.get('database', {}))
        self.cache = CacheConfig(**config_dict.get('cache', {}))
        self.api = APIConfig(**config_dict.get('api', {}))
        self.monitoring = MonitoringConfig(**config_dict.get('monitoring', {}))
        self.assets = AssetConfig(**config_dict.get('assets', {}))
        self.load_testing = LoadTestConfig(**config_dict.get('load_testing', {}))
        self.security = SecurityConfig(**config_dict.get('security', {}))
        
        # Global performance settings
        self.enable_debug_mode = config_dict.get('debug_mode', os.getenv('DEBUG', 'false').lower() == 'true')
        self.enable_metrics_collection = config_dict.get('metrics_collection', True)
        self.enable_auto_optimization = config_dict.get('auto_optimization', True)
        self.performance_budget = config_dict.get('performance_budget', {
            'max_response_time_ms': 1000,
            'max_page_size_kb': 1024,
            'max_bundle_size_kb': 512,
            'max_image_size_kb': 200
        })
        
        # Apply optimization level adjustments
        self._apply_optimization_level()
    
    def _apply_optimization_level(self):
        """Apply optimization level to all configurations"""
        if self.optimization_level == OptimizationLevel.BASIC:
            self._apply_basic_optimizations()
        elif self.optimization_level == OptimizationLevel.MODERATE:
            self._apply_moderate_optimizations()
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            self._apply_aggressive_optimizations()
    
    def _apply_basic_optimizations(self):
        """Apply basic optimization settings"""
        # Conservative settings for basic optimization
        self.cache.default_ttl = 1800  # 30 minutes
        self.api.compression_level = 3
        self.assets.image_quality_jpeg = 90
        self.assets.image_quality_webp = 85
        self.database.connection_pool_size = 10
        self.monitoring.monitoring_interval = 60  # 1 minute
    
    def _apply_moderate_optimizations(self):
        """Apply moderate optimization settings"""
        # Balanced settings (already set as defaults)
        pass
    
    def _apply_aggressive_optimizations(self):
        """Apply aggressive optimization settings"""
        # Aggressive settings for maximum performance
        self.cache.default_ttl = 7200  # 2 hours
        self.api.compression_level = 9
        self.assets.image_quality_jpeg = 75
        self.assets.image_quality_webp = 70
        self.database.connection_pool_size = 50
        self.monitoring.monitoring_interval = 15  # 15 seconds
        self.database.slow_query_threshold = 0.5  # 500ms
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get configuration for current environment"""
        env = os.getenv('ENVIRONMENT', 'development').lower()
        
        if env == 'production':
            return self._get_production_config()
        elif env == 'staging':
            return self._get_staging_config()
        else:
            return self._get_development_config()
    
    def _get_production_config(self) -> Dict[str, Any]:
        """Production-specific configuration"""
        return {
            'optimization_level': OptimizationLevel.AGGRESSIVE,
            'enable_debug_mode': False,
            'monitoring': {
                'enable_performance_monitoring': True,
                'enable_real_time_alerts': True,
                'metrics_retention_days': 90
            },
            'cache': {
                'enable_redis': True,
                'enable_distributed_cache': True,
                'default_ttl': 7200
            },
            'api': {
                'enable_response_compression': True,
                'enable_response_caching': True,
                'rate_limit_enabled': True
            },
            'security': {
                'enable_rate_limiting': True,
                'enable_ddos_protection': True,
                'enable_input_validation': True
            }
        }
    
    def _get_staging_config(self) -> Dict[str, Any]:
        """Staging-specific configuration"""
        return {
            'optimization_level': OptimizationLevel.MODERATE,
            'enable_debug_mode': False,
            'monitoring': {
                'enable_performance_monitoring': True,
                'enable_real_time_alerts': False,
                'metrics_retention_days': 30
            },
            'load_testing': {
                'enable_load_testing': True,
                'enable_stress_testing': True
            }
        }
    
    def _get_development_config(self) -> Dict[str, Any]:
        """Development-specific configuration"""
        return {
            'optimization_level': OptimizationLevel.BASIC,
            'enable_debug_mode': True,
            'monitoring': {
                'enable_performance_monitoring': True,
                'enable_real_time_alerts': False,
                'monitoring_interval': 60
            },
            'cache': {
                'enable_redis': False,
                'enable_memory_cache': True
            },
            'api': {
                'rate_limit_enabled': False
            },
            'security': {
                'enable_rate_limiting': False,
                'enable_ddos_protection': False
            }
        }
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Validate cache configuration
        if self.cache.enable_redis and not self.cache.redis_url:
            issues.append("Redis enabled but no Redis URL provided")
        
        # Validate monitoring configuration
        if self.monitoring.monitoring_interval < 5:
            issues.append("Monitoring interval too low (minimum 5 seconds)")
        
        # Validate database configuration
        if self.database.connection_pool_size > 100:
            issues.append("Database connection pool size too high (maximum 100)")
        
        # Validate asset configuration
        if self.assets.enable_cdn and not self.assets.cdn_base_url:
            issues.append("CDN enabled but no CDN base URL provided")
        
        # Validate performance budget
        if self.performance_budget['max_response_time_ms'] < 100:
            issues.append("Performance budget response time too strict (minimum 100ms)")
        
        return issues
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'optimization_level': self.optimization_level.value,
            'enable_debug_mode': self.enable_debug_mode,
            'enable_metrics_collection': self.enable_metrics_collection,
            'enable_auto_optimization': self.enable_auto_optimization,
            'performance_budget': self.performance_budget,
            'database': {
                'enable_query_optimization': self.database.enable_query_optimization,
                'enable_auto_indexing': self.database.enable_auto_indexing,
                'slow_query_threshold': self.database.slow_query_threshold,
                'connection_pool_size': self.database.connection_pool_size,
                'connection_pool_timeout': self.database.connection_pool_timeout,
                'enable_query_cache': self.database.enable_query_cache,
                'query_cache_size': self.database.query_cache_size
            },
            'cache': {
                'enable_redis': self.cache.enable_redis,
                'redis_url': self.cache.redis_url,
                'redis_pool_size': self.cache.redis_pool_size,
                'enable_memory_cache': self.cache.enable_memory_cache,
                'memory_cache_size': self.cache.memory_cache_size,
                'default_ttl': self.cache.default_ttl,
                'enable_compression': self.cache.enable_compression,
                'cache_strategy': self.cache.cache_strategy.value
            },
            'api': {
                'enable_response_compression': self.api.enable_response_compression,
                'compression_level': self.api.compression_level,
                'enable_response_caching': self.api.enable_response_caching,
                'enable_pagination_optimization': self.api.enable_pagination_optimization,
                'default_page_size': self.api.default_page_size,
                'max_page_size': self.api.max_page_size,
                'rate_limit_enabled': self.api.rate_limit_enabled,
                'rate_limit_requests': self.api.rate_limit_requests
            },
            'monitoring': {
                'enable_performance_monitoring': self.monitoring.enable_performance_monitoring,
                'enable_web_vitals': self.monitoring.enable_web_vitals,
                'enable_profiling': self.monitoring.enable_profiling,
                'monitoring_interval': self.monitoring.monitoring_interval,
                'alert_thresholds': self.monitoring.alert_thresholds,
                'enable_real_time_alerts': self.monitoring.enable_real_time_alerts
            },
            'assets': {
                'enable_image_optimization': self.assets.enable_image_optimization,
                'image_quality_jpeg': self.assets.image_quality_jpeg,
                'image_quality_webp': self.assets.image_quality_webp,
                'enable_responsive_images': self.assets.enable_responsive_images,
                'responsive_breakpoints': self.assets.responsive_breakpoints,
                'enable_lazy_loading': self.assets.enable_lazy_loading,
                'enable_cdn': self.assets.enable_cdn,
                'cdn_base_url': self.assets.cdn_base_url
            },
            'load_testing': {
                'enable_load_testing': self.load_testing.enable_load_testing,
                'default_concurrent_users': self.load_testing.default_concurrent_users,
                'default_duration_seconds': self.load_testing.default_duration_seconds,
                'max_concurrent_users': self.load_testing.max_concurrent_users,
                'enable_stress_testing': self.load_testing.enable_stress_testing
            },
            'security': {
                'enable_rate_limiting': self.security.enable_rate_limiting,
                'enable_ddos_protection': self.security.enable_ddos_protection,
                'enable_input_validation': self.security.enable_input_validation,
                'max_request_size': self.security.max_request_size,
                'max_upload_size': self.security.max_upload_size
            }
        }
    
    @classmethod
    def from_file(cls, config_file: str) -> 'PerformanceConfig':
        """Load configuration from file"""
        import json
        import yaml
        
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                config_dict = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        return cls(config_dict)
    
    def save_to_file(self, config_file: str, format: str = 'yaml'):
        """Save configuration to file"""
        import json
        import yaml
        
        config_dict = self.to_dict()
        
        with open(config_file, 'w') as f:
            if format.lower() in ['yml', 'yaml']:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            elif format.lower() == 'json':
                json.dump(config_dict, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags for performance optimizations"""
        return {
            'query_optimization': self.database.enable_query_optimization,
            'auto_indexing': self.database.enable_auto_indexing,
            'redis_cache': self.cache.enable_redis,
            'memory_cache': self.cache.enable_memory_cache,
            'response_compression': self.api.enable_response_compression,
            'response_caching': self.api.enable_response_caching,
            'pagination_optimization': self.api.enable_pagination_optimization,
            'performance_monitoring': self.monitoring.enable_performance_monitoring,
            'profiling': self.monitoring.enable_profiling,
            'image_optimization': self.assets.enable_image_optimization,
            'responsive_images': self.assets.enable_responsive_images,
            'lazy_loading': self.assets.enable_lazy_loading,
            'cdn': self.assets.enable_cdn,
            'load_testing': self.load_testing.enable_load_testing,
            'rate_limiting': self.security.enable_rate_limiting,
            'ddos_protection': self.security.enable_ddos_protection
        }