"""
Synchronization Configuration Management

Centralized configuration for all synchronization components:
- Service-wide settings and parameters
- Component-specific configurations
- Environment-based configuration loading
- Runtime configuration updates
- Validation and defaults
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import yaml

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CompressionType(Enum):
    """Compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"
    LZ4 = "lz4"


class EncryptionType(Enum):
    """Encryption algorithms"""
    NONE = "none"
    AES256 = "aes256"
    CHACHA20 = "chacha20"


@dataclass
class WebSocketConfig:
    """WebSocket manager configuration"""
    heartbeat_interval: int = 30
    max_connections: int = 10000
    message_size_limit: int = 1024 * 1024  # 1MB
    compression_enabled: bool = True
    ping_timeout: int = 60
    connection_timeout: int = 120
    rate_limit_per_minute: int = 1000
    allowed_origins: List[str] = field(default_factory=list)
    cors_enabled: bool = True


@dataclass
class OfflineConfig:
    """Offline handler configuration"""
    storage_path: str = "/tmp/bdc_offline_queue"
    max_queue_size: int = 10000
    connectivity_check_interval: int = 5
    retry_base_delay: float = 1.0
    retry_max_delay: float = 300.0
    max_retries: int = 5
    batch_size: int = 100
    persistence_enabled: bool = True
    cleanup_interval: int = 3600


@dataclass
class ConflictConfig:
    """Conflict resolver configuration"""
    default_strategy: str = "three_way_merge"
    auto_resolve_enabled: bool = True
    user_intervention_timeout: int = 86400  # 24 hours
    max_conflict_history: int = 1000
    resolution_algorithms: List[str] = field(default_factory=lambda: [
        "last_write_wins", "first_write_wins", "three_way_merge",
        "operational_transform", "custom_rules", "user_decision"
    ])


@dataclass
class VersionConfig:
    """Version manager configuration"""
    enable_compression: bool = True
    compression_type: CompressionType = CompressionType.GZIP
    max_versions_per_entity: int = 1000
    version_cleanup_interval: int = 86400  # 24 hours
    snapshot_frequency: int = 100  # Create snapshot every 100 versions
    enable_branch_management: bool = True
    max_branches_per_entity: int = 10


@dataclass
class EventConfig:
    """Event sourcing configuration"""
    enable_compression: bool = True
    compression_type: CompressionType = CompressionType.GZIP
    enable_encryption: bool = False
    encryption_type: EncryptionType = EncryptionType.AES256
    max_events_per_aggregate: int = 10000
    snapshot_frequency: int = 1000
    cleanup_interval: int = 86400
    projection_processing_interval: int = 1


@dataclass
class DeviceSyncConfig:
    """Device synchronization configuration"""
    max_devices_per_user: int = 10
    device_timeout: int = 300  # 5 minutes
    sync_batch_size: int = 100
    bandwidth_optimization: bool = True
    selective_sync_enabled: bool = True
    real_time_sync_enabled: bool = True
    background_sync_interval: int = 300


@dataclass
class SecurityConfig:
    """Security-related configuration"""
    jwt_secret: str = ""
    encryption_key: str = ""
    enable_rate_limiting: bool = True
    rate_limit_per_minute: int = 1000
    enable_ip_whitelist: bool = False
    allowed_ips: List[str] = field(default_factory=list)
    session_timeout: int = 3600
    require_authentication: bool = True


@dataclass
class StorageConfig:
    """Storage backend configuration"""
    backend_type: str = "memory"  # memory, redis, postgres, mongodb
    connection_string: str = ""
    pool_size: int = 10
    timeout: int = 30
    enable_ssl: bool = False
    backup_enabled: bool = False
    backup_interval: int = 86400


@dataclass
class MonitoringConfig:
    """Monitoring and metrics configuration"""
    enable_metrics: bool = True
    metrics_interval: int = 60
    enable_health_checks: bool = True
    health_check_interval: int = 30
    log_level: LogLevel = LogLevel.INFO
    enable_tracing: bool = False
    enable_profiling: bool = False


@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    enable_caching: bool = True
    cache_size: int = 1000
    cache_ttl: int = 3600
    enable_connection_pooling: bool = True
    max_concurrent_operations: int = 100
    operation_timeout: int = 30
    enable_batch_processing: bool = True


class SyncConfig:
    """
    Main synchronization configuration class
    
    Provides centralized configuration management for all sync components
    with support for environment variables, file-based config, and runtime updates.
    """
    
    def __init__(self, config_file: Optional[str] = None, env_prefix: str = "BDC_SYNC"):
        self.env_prefix = env_prefix
        self.config_file = config_file
        
        # Component configurations
        self.websocket = WebSocketConfig()
        self.offline = OfflineConfig()
        self.conflict = ConflictConfig()
        self.version = VersionConfig()
        self.event = EventConfig()
        self.device_sync = DeviceSyncConfig()
        self.security = SecurityConfig()
        self.storage = StorageConfig()
        self.monitoring = MonitoringConfig()
        self.performance = PerformanceConfig()
        
        # Legacy/compatibility properties
        self.jwt_secret = ""
        self.heartbeat_interval = 30
        self.offline_storage_path = "/tmp/bdc_offline_queue"
        self.max_queue_size = 10000
        self.connectivity_check_interval = 5
        self.enable_compression = True
        
        # Load configuration
        self._load_config()
        
    def _load_config(self):
        """Load configuration from various sources"""
        
        # 1. Load from file if specified
        if self.config_file:
            self._load_from_file(self.config_file)
            
        # 2. Load from environment variables
        self._load_from_env()
        
        # 3. Apply legacy compatibility
        self._apply_legacy_compatibility()
        
        # 4. Validate configuration
        self._validate_config()
        
    def _load_from_file(self, config_file: str):
        """Load configuration from file (JSON or YAML)"""
        
        try:
            if not os.path.exists(config_file):
                logger.warning(f"Config file not found: {config_file}")
                return
                
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
                    
            self._apply_config_data(config_data)
            logger.info(f"Loaded configuration from: {config_file}")
            
        except Exception as e:
            logger.error(f"Error loading config file {config_file}: {e}")
            
    def _load_from_env(self):
        """Load configuration from environment variables"""
        
        env_mappings = {
            # WebSocket config
            f"{self.env_prefix}_WS_HEARTBEAT_INTERVAL": ("websocket", "heartbeat_interval", int),
            f"{self.env_prefix}_WS_MAX_CONNECTIONS": ("websocket", "max_connections", int),
            f"{self.env_prefix}_WS_COMPRESSION": ("websocket", "compression_enabled", bool),
            
            # Offline config
            f"{self.env_prefix}_OFFLINE_STORAGE_PATH": ("offline", "storage_path", str),
            f"{self.env_prefix}_OFFLINE_MAX_QUEUE": ("offline", "max_queue_size", int),
            f"{self.env_prefix}_OFFLINE_CHECK_INTERVAL": ("offline", "connectivity_check_interval", int),
            
            # Security config
            f"{self.env_prefix}_JWT_SECRET": ("security", "jwt_secret", str),
            f"{self.env_prefix}_ENCRYPTION_KEY": ("security", "encryption_key", str),
            f"{self.env_prefix}_REQUIRE_AUTH": ("security", "require_authentication", bool),
            
            # Storage config
            f"{self.env_prefix}_STORAGE_BACKEND": ("storage", "backend_type", str),
            f"{self.env_prefix}_STORAGE_CONNECTION": ("storage", "connection_string", str),
            
            # Monitoring config
            f"{self.env_prefix}_LOG_LEVEL": ("monitoring", "log_level", str),
            f"{self.env_prefix}_ENABLE_METRICS": ("monitoring", "enable_metrics", bool),
            
            # Performance config
            f"{self.env_prefix}_ENABLE_CACHING": ("performance", "enable_caching", bool),
            f"{self.env_prefix}_CACHE_SIZE": ("performance", "cache_size", int),
        }
        
        for env_var, (config_section, config_key, value_type) in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    if value_type == bool:
                        typed_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        typed_value = int(env_value)
                    elif value_type == float:
                        typed_value = float(env_value)
                    else:
                        typed_value = env_value
                        
                    # Special handling for log level
                    if config_key == "log_level":
                        typed_value = LogLevel(env_value.upper())
                        
                    # Set the configuration value
                    config_obj = getattr(self, config_section)
                    setattr(config_obj, config_key, typed_value)
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {env_value} ({e})")
                    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data from file"""
        
        # Map configuration sections to objects
        section_mapping = {
            'websocket': self.websocket,
            'offline': self.offline,
            'conflict': self.conflict,
            'version': self.version,
            'event': self.event,
            'device_sync': self.device_sync,
            'security': self.security,
            'storage': self.storage,
            'monitoring': self.monitoring,
            'performance': self.performance
        }
        
        for section_name, section_data in config_data.items():
            if section_name in section_mapping and isinstance(section_data, dict):
                config_obj = section_mapping[section_name]
                
                for key, value in section_data.items():
                    if hasattr(config_obj, key):
                        # Handle enum values
                        current_value = getattr(config_obj, key)
                        if isinstance(current_value, Enum):
                            try:
                                enum_class = type(current_value)
                                setattr(config_obj, key, enum_class(value))
                            except ValueError:
                                logger.warning(f"Invalid enum value for {section_name}.{key}: {value}")
                        else:
                            setattr(config_obj, key, value)
                    else:
                        logger.warning(f"Unknown config key: {section_name}.{key}")
                        
    def _apply_legacy_compatibility(self):
        """Apply legacy configuration for backward compatibility"""
        
        # Update legacy properties from component configs
        self.jwt_secret = self.security.jwt_secret
        self.heartbeat_interval = self.websocket.heartbeat_interval
        self.offline_storage_path = self.offline.storage_path
        self.max_queue_size = self.offline.max_queue_size
        self.connectivity_check_interval = self.offline.connectivity_check_interval
        self.enable_compression = self.version.enable_compression
        
    def _validate_config(self):
        """Validate configuration values"""
        
        errors = []
        
        # Validate required security settings
        if self.security.require_authentication and not self.security.jwt_secret:
            errors.append("JWT secret is required when authentication is enabled")
            
        # Validate intervals and timeouts
        if self.websocket.heartbeat_interval <= 0:
            errors.append("WebSocket heartbeat interval must be positive")
            
        if self.offline.connectivity_check_interval <= 0:
            errors.append("Connectivity check interval must be positive")
            
        # Validate storage settings
        if self.storage.backend_type not in ['memory', 'redis', 'postgres', 'mongodb']:
            errors.append(f"Unsupported storage backend: {self.storage.backend_type}")
            
        # Validate paths
        try:
            os.makedirs(os.path.dirname(self.offline.storage_path), exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create offline storage path: {e}")
            
        if errors:
            error_msg = "Configuration validation errors:\n" + "\n".join(f"  - {error}" for error in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    def update_config(self, section: str, key: str, value: Any):
        """Update configuration at runtime"""
        
        if not hasattr(self, section):
            raise ValueError(f"Unknown configuration section: {section}")
            
        config_obj = getattr(self, section)
        
        if not hasattr(config_obj, key):
            raise ValueError(f"Unknown configuration key: {section}.{key}")
            
        # Type validation
        current_value = getattr(config_obj, key)
        if isinstance(current_value, Enum):
            try:
                enum_class = type(current_value)
                value = enum_class(value)
            except ValueError:
                raise ValueError(f"Invalid enum value for {section}.{key}: {value}")
                
        setattr(config_obj, key, value)
        
        # Update legacy compatibility if needed
        if section == "security" and key == "jwt_secret":
            self.jwt_secret = value
        elif section == "websocket" and key == "heartbeat_interval":
            self.heartbeat_interval = value
        elif section == "offline" and key == "storage_path":
            self.offline_storage_path = value
        # ... other legacy mappings
        
        logger.info(f"Updated configuration: {section}.{key} = {value}")
        
    def get_config_dict(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        
        def enum_to_value(obj):
            if isinstance(obj, Enum):
                return obj.value
            return obj
            
        def dataclass_to_dict(dc):
            result = {}
            for field_name in dc.__dataclass_fields__:
                value = getattr(dc, field_name)
                if isinstance(value, list):
                    result[field_name] = [enum_to_value(item) for item in value]
                else:
                    result[field_name] = enum_to_value(value)
            return result
            
        return {
            'websocket': dataclass_to_dict(self.websocket),
            'offline': dataclass_to_dict(self.offline),
            'conflict': dataclass_to_dict(self.conflict),
            'version': dataclass_to_dict(self.version),
            'event': dataclass_to_dict(self.event),
            'device_sync': dataclass_to_dict(self.device_sync),
            'security': dataclass_to_dict(self.security),
            'storage': dataclass_to_dict(self.storage),
            'monitoring': dataclass_to_dict(self.monitoring),
            'performance': dataclass_to_dict(self.performance)
        }
        
    def save_to_file(self, file_path: str):
        """Save current configuration to file"""
        
        config_dict = self.get_config_dict()
        
        try:
            with open(file_path, 'w') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False)
                else:
                    json.dump(config_dict, f, indent=2)
                    
            logger.info(f"Configuration saved to: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving configuration to {file_path}: {e}")
            raise
            
    def reload_config(self):
        """Reload configuration from sources"""
        logger.info("Reloading configuration")
        self._load_config()
        
    def get_database_url(self) -> str:
        """Get database URL based on storage configuration"""
        
        if self.storage.backend_type == "postgres":
            return self.storage.connection_string or "postgresql://localhost/bdc_sync"
        elif self.storage.backend_type == "mongodb":
            return self.storage.connection_string or "mongodb://localhost:27017/bdc_sync"
        elif self.storage.backend_type == "redis":
            return self.storage.connection_string or "redis://localhost:6379/0"
        else:
            return ""
            
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return os.environ.get("ENVIRONMENT", "development").lower() == "production"
        
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        return self.monitoring.log_level == LogLevel.DEBUG
        
    @classmethod
    def create_default_config_file(cls, file_path: str):
        """Create a default configuration file"""
        
        default_config = cls()
        default_config.save_to_file(file_path)
        
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"SyncConfig(websocket={self.websocket}, offline={self.offline}, ...)"
        
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"SyncConfig({self.get_config_dict()})"


# Environment-specific configuration factories
def create_development_config() -> SyncConfig:
    """Create configuration optimized for development"""
    config = SyncConfig()
    
    # Development-friendly settings
    config.monitoring.log_level = LogLevel.DEBUG
    config.monitoring.enable_metrics = True
    config.security.require_authentication = False
    config.websocket.rate_limit_per_minute = 10000
    config.performance.enable_caching = False
    
    return config


def create_production_config() -> SyncConfig:
    """Create configuration optimized for production"""
    config = SyncConfig()
    
    # Production-optimized settings
    config.monitoring.log_level = LogLevel.INFO
    config.security.require_authentication = True
    config.security.enable_rate_limiting = True
    config.performance.enable_caching = True
    config.event.enable_encryption = True
    config.storage.backup_enabled = True
    
    return config


def create_test_config() -> SyncConfig:
    """Create configuration for testing"""
    config = SyncConfig()
    
    # Test-friendly settings
    config.monitoring.log_level = LogLevel.WARNING
    config.offline.storage_path = "/tmp/test_bdc_offline_queue"
    config.security.require_authentication = False
    config.websocket.max_connections = 100
    config.offline.max_queue_size = 100
    
    return config