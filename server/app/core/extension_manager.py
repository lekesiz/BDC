"""Extension initialization and management system."""

import logging
from typing import List, Dict, Any, Callable, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from flask import Flask


class ExtensionPriority(Enum):
    """Extension initialization priorities."""
    CRITICAL = 1      # Database, logging - must be first
    HIGH = 2          # Security, authentication
    MEDIUM = 3        # Caching, rate limiting
    LOW = 4           # Monitoring, optional features


@dataclass
class ExtensionInfo:
    """Information about an extension."""
    name: str
    initializer: Callable[[Flask], None]
    priority: ExtensionPriority
    dependencies: List[str] = None
    optional: bool = False
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class IExtensionInitializer(ABC):
    """Interface for extension initializers."""
    
    @abstractmethod
    def initialize(self, app: Flask) -> bool:
        """Initialize the extension.
        
        Args:
            app: Flask application instance
            
        Returns:
            True if initialization was successful
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the extension name."""
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """Get list of extension dependencies."""
        pass


class DatabaseExtensionInitializer(IExtensionInitializer):
    """Initializes database extensions."""
    
    def initialize(self, app: Flask) -> bool:
        """Initialize database extensions."""
        try:
            from app.extensions import db, migrate
            
            # Initialize SQLAlchemy
            db.init_app(app)
            
            # Initialize Flask-Migrate
            migrate.init_app(app, db)
            
            app.logger.info("Database extensions initialized successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to initialize database extensions: {e}")
            return False
    
    def get_name(self) -> str:
        return "database"
    
    def get_dependencies(self) -> List[str]:
        return []


class AuthenticationExtensionInitializer(IExtensionInitializer):
    """Initializes authentication extensions."""
    
    def initialize(self, app: Flask) -> bool:
        """Initialize authentication extensions."""
        try:
            from app.extensions import jwt, ma
            
            # Initialize JWT
            jwt.init_app(app)
            
            # Initialize Marshmallow
            ma.init_app(app)
            
            # Register JWT callbacks
            self._register_jwt_callbacks(app, jwt)
            
            app.logger.info("Authentication extensions initialized successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to initialize authentication extensions: {e}")
            return False
    
    def _register_jwt_callbacks(self, app: Flask, jwt_manager) -> None:
        """Register JWT callbacks."""
        from flask import jsonify
        
        @jwt_manager.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            """Load user from JWT token."""
            try:
                from app.models.user import User
                identity = jwt_data["sub"]
                return User.query.filter_by(id=identity).one_or_none()
            except Exception as e:
                app.logger.error(f"Error in user lookup: {e}")
                return None

        @jwt_manager.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload):
            """Check if token is revoked."""
            try:
                from app.models.user import TokenBlocklist
                from app.extensions import db
                jti = jwt_payload["jti"]
                token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
                return token is not None
            except Exception as e:
                app.logger.error(f"Error checking token blocklist: {e}")
                return False

        @jwt_manager.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            """Handle expired token."""
            return jsonify({
                'error': 'token_expired',
                'message': 'The token has expired',
                'status_code': 401
            }), 401

        @jwt_manager.invalid_token_loader
        def invalid_token_callback(error):
            """Handle invalid token."""
            return jsonify({
                'error': 'invalid_token',
                'message': 'Signature verification failed',
                'status_code': 401
            }), 401

        @jwt_manager.unauthorized_loader
        def missing_token_callback(error):
            """Handle missing token."""
            return jsonify({
                'error': 'authorization_required',
                'message': 'Authorization is required',
                'status_code': 401
            }), 401
    
    def get_name(self) -> str:
        return "authentication"
    
    def get_dependencies(self) -> List[str]:
        return ["database"]


class CorsExtensionInitializer(IExtensionInitializer):
    """Initializes CORS extensions."""
    
    def initialize(self, app: Flask) -> bool:
        """Initialize CORS extensions."""
        try:
            from app.extensions import cors
            
            cors_config = {
                'resources': {
                    r"/*": {
                        "origins": app.config.get('CORS_ORIGINS', ['*']),
                        "methods": ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
                        "allow_headers": ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept'],
                        "supports_credentials": True,
                        "expose_headers": ['Content-Type', 'Authorization'],
                        "send_wildcard": False,
                        "allow_credentials": True,
                        "max_age": 3600
                    }
                },
                'supports_credentials': True,
                'intercept_exceptions': False
            }
            
            cors.init_app(app, **cors_config)
            
            app.logger.info("CORS extensions initialized successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to initialize CORS extensions: {e}")
            return False
    
    def get_name(self) -> str:
        return "cors"
    
    def get_dependencies(self) -> List[str]:
        return []


class CachingExtensionInitializer(IExtensionInitializer):
    """Initializes caching extensions."""
    
    def initialize(self, app: Flask) -> bool:
        """Initialize caching extensions."""
        try:
            from app.extensions import cache
            
            cache.init_app(app)
            
            app.logger.info("Caching extensions initialized successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to initialize caching extensions: {e}")
            return False
    
    def get_name(self) -> str:
        return "caching"
    
    def get_dependencies(self) -> List[str]:
        return []


class MailExtensionInitializer(IExtensionInitializer):
    """Initializes mail extensions."""
    
    def initialize(self, app: Flask) -> bool:
        """Initialize mail extensions."""
        try:
            from app.extensions import mail
            
            mail.init_app(app)
            
            app.logger.info("Mail extensions initialized successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to initialize mail extensions: {e}")
            return False
    
    def get_name(self) -> str:
        return "mail"
    
    def get_dependencies(self) -> List[str]:
        return []


class RateLimitingExtensionInitializer(IExtensionInitializer):
    """Initializes rate limiting extensions."""
    
    def initialize(self, app: Flask) -> bool:
        """Initialize rate limiting extensions."""
        try:
            from app.extensions import limiter
            
            # Only initialize if rate limiting is enabled
            if app.config.get('RATELIMIT_ENABLED', True):
                limiter.init_app(app)
                app.logger.info("Rate limiting extensions initialized successfully")
            else:
                app.logger.info("Rate limiting disabled by configuration")
            
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to initialize rate limiting extensions: {e}")
            return False
    
    def get_name(self) -> str:
        return "rate_limiting"
    
    def get_dependencies(self) -> List[str]:
        return []


class SocketIOExtensionInitializer(IExtensionInitializer):
    """Initializes SocketIO extensions."""
    
    def initialize(self, app: Flask) -> bool:
        """Initialize SocketIO extensions."""
        try:
            from app.extensions import socketio
            
            socketio_config = {
                'cors_allowed_origins': '*',
                'cors_credentials': True,
                'async_mode': 'eventlet',
                'allow_upgrades': True,
                'ping_timeout': 60,
                'ping_interval': 25,
                'logger': app.config.get('DEBUG', False),
                'engineio_logger': app.config.get('DEBUG', False)
            }
            
            socketio.init_app(app, **socketio_config)
            
            app.logger.info("SocketIO extensions initialized successfully")
            return True
            
        except Exception as e:
            app.logger.error(f"Failed to initialize SocketIO extensions: {e}")
            return False
    
    def get_name(self) -> str:
        return "socketio"
    
    def get_dependencies(self) -> List[str]:
        return []


class ExtensionManager:
    """Manages extension initialization with proper dependency ordering."""
    
    def __init__(self):
        """Initialize extension manager."""
        self._initializers: Dict[str, IExtensionInitializer] = {}
        self._initialized: Dict[str, bool] = {}
        self._logger = logging.getLogger(__name__)
        
        # Register default initializers
        self._register_default_initializers()
    
    def _register_default_initializers(self) -> None:
        """Register default extension initializers."""
        self.register_initializer(DatabaseExtensionInitializer())
        self.register_initializer(AuthenticationExtensionInitializer())
        self.register_initializer(CorsExtensionInitializer())
        self.register_initializer(CachingExtensionInitializer())
        self.register_initializer(MailExtensionInitializer())
        self.register_initializer(RateLimitingExtensionInitializer())
        self.register_initializer(SocketIOExtensionInitializer())
    
    def register_initializer(self, initializer: IExtensionInitializer) -> None:
        """Register an extension initializer."""
        name = initializer.get_name()
        self._initializers[name] = initializer
        self._initialized[name] = False
        self._logger.debug(f"Registered extension initializer: {name}")
    
    def initialize_extensions(self, app: Flask) -> bool:
        """Initialize all extensions in dependency order.
        
        Args:
            app: Flask application instance
            
        Returns:
            True if all extensions were initialized successfully
        """
        self._logger.info("Starting extension initialization")
        
        # Get initialization order
        init_order = self._get_initialization_order()
        
        success = True
        for name in init_order:
            if name not in self._initializers:
                self._logger.warning(f"Extension {name} not found in initializers")
                continue
            
            try:
                initializer = self._initializers[name]
                self._logger.info(f"Initializing extension: {name}")
                
                if initializer.initialize(app):
                    self._initialized[name] = True
                    self._logger.info(f"Successfully initialized extension: {name}")
                else:
                    self._logger.error(f"Failed to initialize extension: {name}")
                    success = False
                    
            except Exception as e:
                self._logger.error(f"Exception during initialization of {name}: {e}")
                success = False
        
        if success:
            self._logger.info("All extensions initialized successfully")
        else:
            self._logger.error("Some extensions failed to initialize")
        
        return success
    
    def _get_initialization_order(self) -> List[str]:
        """Get the order in which extensions should be initialized."""
        # Use topological sort to resolve dependencies
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(name: str) -> None:
            if name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {name}")
            if name in visited:
                return
            
            temp_visited.add(name)
            
            if name in self._initializers:
                dependencies = self._initializers[name].get_dependencies()
                for dep in dependencies:
                    visit(dep)
            
            temp_visited.remove(name)
            visited.add(name)
            result.append(name)
        
        # Visit all extensions
        for name in self._initializers.keys():
            if name not in visited:
                visit(name)
        
        return result
    
    def is_initialized(self, extension_name: str) -> bool:
        """Check if an extension is initialized."""
        return self._initialized.get(extension_name, False)
    
    def get_initialized_extensions(self) -> List[str]:
        """Get list of successfully initialized extensions."""
        return [name for name, initialized in self._initialized.items() if initialized]


# Global extension manager instance
extension_manager = ExtensionManager()