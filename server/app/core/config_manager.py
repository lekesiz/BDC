"""Enhanced configuration management system."""

import os
import sys
from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging
from flask import Flask


@dataclass
class ConfigValidationResult:
    """Result of configuration validation."""
    is_valid: bool
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


class IConfigValidator(ABC):
    """Interface for configuration validators."""
    
    @abstractmethod
    def validate(self, config: Dict[str, Any]) -> ConfigValidationResult:
        """Validate configuration."""
        pass


class DatabaseConfigValidator(IConfigValidator):
    """Validates database configuration."""
    
    def validate(self, config: Dict[str, Any]) -> ConfigValidationResult:
        """Validate database configuration."""
        result = ConfigValidationResult(is_valid=True)
        
        # Check required database configuration
        if not config.get('SQLALCHEMY_DATABASE_URI'):
            result.errors.append("SQLALCHEMY_DATABASE_URI is required")
            result.is_valid = False
        
        # Validate SQLite path for file-based databases
        db_uri = config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite://'):
            if db_uri != 'sqlite:///:memory:':
                db_path = db_uri.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if not os.path.exists(db_dir):
                    try:
                        os.makedirs(db_dir, exist_ok=True)
                    except Exception as e:
                        result.errors.append(f"Cannot create database directory: {e}")
                        result.is_valid = False
        
        return result


class SecurityConfigValidator(IConfigValidator):
    """Validates security configuration."""
    
    def validate(self, config: Dict[str, Any]) -> ConfigValidationResult:
        """Validate security configuration."""
        result = ConfigValidationResult(is_valid=True)
        
        # Check secret keys
        secret_key = config.get('SECRET_KEY')
        if not secret_key or secret_key == 'dev-secret-key-change-in-production':
            if config.get('ENV') == 'production':
                result.errors.append("Production SECRET_KEY must be set and not use default value")
                result.is_valid = False
            else:
                result.warnings.append("Using default SECRET_KEY in non-production environment")
        
        jwt_secret = config.get('JWT_SECRET_KEY')
        if not jwt_secret or jwt_secret == 'jwt-secret-key-change-in-production':
            if config.get('ENV') == 'production':
                result.errors.append("Production JWT_SECRET_KEY must be set and not use default value")
                result.is_valid = False
            else:
                result.warnings.append("Using default JWT_SECRET_KEY in non-production environment")
        
        return result


class RedisConfigValidator(IConfigValidator):
    """Validates Redis configuration."""
    
    def validate(self, config: Dict[str, Any]) -> ConfigValidationResult:
        """Validate Redis configuration."""
        result = ConfigValidationResult(is_valid=True)
        
        redis_url = config.get('REDIS_URL')
        if not redis_url:
            result.warnings.append("REDIS_URL not configured, some features may be disabled")
        
        return result


class ConfigurationManager:
    """Enhanced configuration manager with validation and environment handling."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self._validators: list[IConfigValidator] = [
            DatabaseConfigValidator(),
            SecurityConfigValidator(),
            RedisConfigValidator()
        ]
        self._logger = logging.getLogger(__name__)
    
    def load_configuration(self, app: Flask, config_object: Optional[object] = None) -> ConfigValidationResult:
        """Load and validate configuration for the Flask app.
        
        Args:
            app: Flask application instance
            config_object: Optional configuration object to use
            
        Returns:
            ConfigValidationResult with validation status
        """
        try:
            # Load configuration
            if config_object is None:
                config_object = self._determine_config_object()
            
            app.config.from_object(config_object)
            
            # Set up environment-specific defaults
            self._apply_environment_defaults(app)
            
            # Validate configuration
            validation_result = self._validate_configuration(app.config)
            
            # Log validation results
            self._log_validation_results(validation_result)
            
            return validation_result
            
        except Exception as e:
            self._logger.error(f"Failed to load configuration: {e}")
            result = ConfigValidationResult(is_valid=False)
            result.errors.append(f"Configuration loading failed: {e}")
            return result
    
    def _determine_config_object(self) -> Type:
        """Determine which configuration object to use based on environment."""
        env = os.getenv('FLASK_ENV', 'default').lower()
        
        # Add parent directory to path for config import
        config_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        if config_path not in sys.path:
            sys.path.insert(0, config_path)
        
        try:
            from config import config
            return config.get(env, config['default'])
        except ImportError as e:
            self._logger.error(f"Failed to import config: {e}")
            raise
    
    def _apply_environment_defaults(self, app: Flask) -> None:
        """Apply environment-specific defaults."""
        env = app.config.get('ENV', 'development')
        
        # Ensure uploads directory exists
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if upload_folder and not os.path.exists(upload_folder):
            try:
                os.makedirs(upload_folder, exist_ok=True)
                self._logger.info(f"Created upload folder: {upload_folder}")
            except Exception as e:
                self._logger.warning(f"Failed to create upload folder: {e}")
        
        # Set environment-specific settings
        if env == 'testing':
            # Disable certain features during testing
            app.config.setdefault('WTF_CSRF_ENABLED', False)
            app.config.setdefault('TESTING', True)
        
        elif env == 'production':
            # Ensure production security settings
            app.config.setdefault('SESSION_COOKIE_SECURE', True)
            app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
            app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
    
    def _validate_configuration(self, config: Dict[str, Any]) -> ConfigValidationResult:
        """Validate configuration using all validators."""
        combined_result = ConfigValidationResult(is_valid=True)
        
        for validator in self._validators:
            try:
                result = validator.validate(config)
                
                # Combine results
                if not result.is_valid:
                    combined_result.is_valid = False
                
                combined_result.errors.extend(result.errors)
                combined_result.warnings.extend(result.warnings)
                
            except Exception as e:
                self._logger.error(f"Validation error with {validator.__class__.__name__}: {e}")
                combined_result.errors.append(f"Validator {validator.__class__.__name__} failed: {e}")
                combined_result.is_valid = False
        
        return combined_result
    
    def _log_validation_results(self, result: ConfigValidationResult) -> None:
        """Log validation results."""
        if result.is_valid:
            self._logger.info("Configuration validation passed")
        else:
            self._logger.error("Configuration validation failed")
        
        for error in result.errors:
            self._logger.error(f"Config error: {error}")
        
        for warning in result.warnings:
            self._logger.warning(f"Config warning: {warning}")
    
    def add_validator(self, validator: IConfigValidator) -> None:
        """Add a custom configuration validator."""
        self._validators.append(validator)


# Global configuration manager instance
config_manager = ConfigurationManager()