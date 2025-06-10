"""
User-Friendly Error Message Management and Localization.

Provides mapping of technical errors to user-friendly messages with internationalization support.
"""

import logging
from typing import Any, Dict, Optional, Union
from enum import Enum
from dataclasses import dataclass
import json
import os

from .error_manager import ErrorCategory, ErrorSeverity
from .exceptions import ErrorHandlingException


class MessageType(Enum):
    """Types of user messages."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUCCESS = "success"


@dataclass
class UserMessage:
    """User-friendly message structure."""
    code: str
    message: str
    message_type: MessageType
    suggested_actions: list[str]
    support_info: Optional[str] = None
    technical_details: Optional[str] = None


class ErrorMessageMapper:
    """Maps technical errors to user-friendly messages."""
    
    def __init__(self, default_locale: str = "en", logger: Optional[logging.Logger] = None):
        self.default_locale = default_locale
        self.logger = logger or logging.getLogger(__name__)
        self._message_mappings: Dict[str, Dict[str, UserMessage]] = {}
        self._fallback_messages: Dict[str, UserMessage] = {}
        
        # Initialize default mappings
        self._setup_default_mappings()
    
    def _setup_default_mappings(self):
        """Setup default error message mappings."""
        
        # Validation error messages
        validation_messages = {
            "en": {
                "VALIDATION_ERROR": UserMessage(
                    code="VALIDATION_ERROR",
                    message="The information you provided is not valid. Please check your input and try again.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Check that all required fields are filled out",
                        "Ensure email addresses are in the correct format",
                        "Verify that dates are valid and in the correct format"
                    ],
                    support_info="If you continue to have problems, please contact support."
                ),
                "INVALID_EMAIL": UserMessage(
                    code="INVALID_EMAIL",
                    message="Please enter a valid email address.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Check that your email address contains an @ symbol",
                        "Ensure there are no spaces in your email address",
                        "Make sure you've included a domain (e.g., @example.com)"
                    ]
                ),
                "PASSWORD_TOO_WEAK": UserMessage(
                    code="PASSWORD_TOO_WEAK",
                    message="Your password doesn't meet our security requirements.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Use at least 8 characters",
                        "Include both uppercase and lowercase letters",
                        "Add at least one number",
                        "Include at least one special character (!@#$%^&*)"
                    ]
                )
            },
            "es": {
                "VALIDATION_ERROR": UserMessage(
                    code="VALIDATION_ERROR",
                    message="La información que proporcionó no es válida. Por favor verifique su entrada e intente nuevamente.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Verifique que todos los campos requeridos estén completados",
                        "Asegúrese de que las direcciones de correo electrónico estén en el formato correcto",
                        "Verifique que las fechas sean válidas y estén en el formato correcto"
                    ],
                    support_info="Si continúa teniendo problemas, por favor contacte al soporte."
                ),
                "INVALID_EMAIL": UserMessage(
                    code="INVALID_EMAIL",
                    message="Por favor ingrese una dirección de correo electrónico válida.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Verifique que su dirección de correo electrónico contenga un símbolo @",
                        "Asegúrese de que no haya espacios en su dirección de correo electrónico",
                        "Asegúrese de haber incluido un dominio (ej: @ejemplo.com)"
                    ]
                )
            }
        }
        
        # Authentication error messages
        auth_messages = {
            "en": {
                "INVALID_CREDENTIALS": UserMessage(
                    code="INVALID_CREDENTIALS",
                    message="The email or password you entered is incorrect.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Check that you've entered your email address correctly",
                        "Verify that your password is correct",
                        "Try using the 'Forgot Password' link if you can't remember your password"
                    ]
                ),
                "ACCOUNT_LOCKED": UserMessage(
                    code="ACCOUNT_LOCKED",
                    message="Your account has been temporarily locked for security reasons.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Wait 15 minutes before trying to log in again",
                        "Use the 'Forgot Password' link to reset your password",
                        "Contact support if you believe this is an error"
                    ],
                    support_info="Account lockouts are automatically lifted after 15 minutes."
                ),
                "SESSION_EXPIRED": UserMessage(
                    code="SESSION_EXPIRED",
                    message="Your session has expired. Please log in again.",
                    message_type=MessageType.WARNING,
                    suggested_actions=[
                        "Click the login button to sign in again",
                        "Your data has been saved and will be available after you log in"
                    ]
                )
            },
            "es": {
                "INVALID_CREDENTIALS": UserMessage(
                    code="INVALID_CREDENTIALS",
                    message="El correo electrónico o la contraseña que ingresó es incorrecta.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Verifique que haya ingresado su dirección de correo electrónico correctamente",
                        "Verifique que su contraseña sea correcta",
                        "Intente usar el enlace 'Olvidé mi contraseña' si no puede recordar su contraseña"
                    ]
                ),
                "SESSION_EXPIRED": UserMessage(
                    code="SESSION_EXPIRED",
                    message="Su sesión ha expirado. Por favor inicie sesión nuevamente.",
                    message_type=MessageType.WARNING,
                    suggested_actions=[
                        "Haga clic en el botón de inicio de sesión para ingresar nuevamente",
                        "Sus datos han sido guardados y estarán disponibles después de iniciar sesión"
                    ]
                )
            }
        }
        
        # System error messages
        system_messages = {
            "en": {
                "SYSTEM_ERROR": UserMessage(
                    code="SYSTEM_ERROR",
                    message="We're experiencing technical difficulties. Please try again in a few moments.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Wait a few minutes and try again",
                        "Refresh the page",
                        "Clear your browser cache if the problem persists"
                    ],
                    support_info="Our technical team has been notified and is working to resolve this issue."
                ),
                "SERVICE_UNAVAILABLE": UserMessage(
                    code="SERVICE_UNAVAILABLE",
                    message="This service is temporarily unavailable. We're working to restore it as quickly as possible.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Try again in a few minutes",
                        "Check our status page for updates"
                    ],
                    support_info="We apologize for the inconvenience."
                ),
                "NETWORK_ERROR": UserMessage(
                    code="NETWORK_ERROR",
                    message="We're having trouble connecting to our servers. Please check your internet connection.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Check your internet connection",
                        "Try refreshing the page",
                        "Disable any VPN or proxy connections temporarily"
                    ]
                )
            },
            "es": {
                "SYSTEM_ERROR": UserMessage(
                    code="SYSTEM_ERROR",
                    message="Estamos experimentando dificultades técnicas. Por favor intente nuevamente en unos momentos.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Espere unos minutos e intente nuevamente",
                        "Actualice la página",
                        "Limpie la caché de su navegador si el problema persiste"
                    ],
                    support_info="Nuestro equipo técnico ha sido notificado y está trabajando para resolver este problema."
                ),
                "NETWORK_ERROR": UserMessage(
                    code="NETWORK_ERROR",
                    message="Tenemos problemas para conectarnos a nuestros servidores. Por favor verifique su conexión a internet.",
                    message_type=MessageType.ERROR,
                    suggested_actions=[
                        "Verifique su conexión a internet",
                        "Intente actualizar la página",
                        "Desactive temporalmente cualquier conexión VPN o proxy"
                    ]
                )
            }
        }
        
        # Merge all message categories
        for locale in ["en", "es"]:
            if locale not in self._message_mappings:
                self._message_mappings[locale] = {}
            
            if locale in validation_messages:
                self._message_mappings[locale].update(validation_messages[locale])
            if locale in auth_messages:
                self._message_mappings[locale].update(auth_messages[locale])
            if locale in system_messages:
                self._message_mappings[locale].update(system_messages[locale])
        
        # Setup fallback messages for unknown errors
        self._fallback_messages = {
            "en": UserMessage(
                code="UNKNOWN_ERROR",
                message="An unexpected error occurred. Please try again or contact support if the problem persists.",
                message_type=MessageType.ERROR,
                suggested_actions=[
                    "Try the action again",
                    "Refresh the page",
                    "Contact support if the problem continues"
                ],
                support_info="Please include details about what you were trying to do when this error occurred."
            ),
            "es": UserMessage(
                code="UNKNOWN_ERROR",
                message="Ocurrió un error inesperado. Por favor intente nuevamente o contacte al soporte si el problema persiste.",
                message_type=MessageType.ERROR,
                suggested_actions=[
                    "Intente la acción nuevamente",
                    "Actualice la página",
                    "Contacte al soporte si el problema continúa"
                ],
                support_info="Por favor incluya detalles sobre lo que estaba tratando de hacer cuando ocurrió este error."
            )
        }
    
    def add_message_mapping(self, locale: str, error_code: str, message: UserMessage):
        """Add a custom message mapping for a specific locale and error code."""
        if locale not in self._message_mappings:
            self._message_mappings[locale] = {}
        
        self._message_mappings[locale][error_code] = message
        self.logger.info(f"Added message mapping: {locale}.{error_code}")
    
    def load_messages_from_file(self, file_path: str, locale: str):
        """Load message mappings from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if locale not in self._message_mappings:
                self._message_mappings[locale] = {}
            
            for error_code, message_data in data.items():
                message = UserMessage(
                    code=error_code,
                    message=message_data['message'],
                    message_type=MessageType(message_data.get('message_type', 'error')),
                    suggested_actions=message_data.get('suggested_actions', []),
                    support_info=message_data.get('support_info'),
                    technical_details=message_data.get('technical_details')
                )
                self._message_mappings[locale][error_code] = message
            
            self.logger.info(f"Loaded {len(data)} message mappings for locale: {locale}")
            
        except Exception as e:
            self.logger.error(f"Failed to load messages from {file_path}: {e}")
            raise
    
    def get_user_message(
        self,
        error_code: str,
        locale: Optional[str] = None,
        fallback_to_default: bool = True
    ) -> UserMessage:
        """Get a user-friendly message for an error code."""
        locale = locale or self.default_locale
        
        # Try to get message for requested locale
        if locale in self._message_mappings and error_code in self._message_mappings[locale]:
            return self._message_mappings[locale][error_code]
        
        # Fallback to default locale if requested
        if fallback_to_default and locale != self.default_locale:
            if (self.default_locale in self._message_mappings and 
                error_code in self._message_mappings[self.default_locale]):
                return self._message_mappings[self.default_locale][error_code]
        
        # Return fallback message
        fallback_locale = locale if locale in self._fallback_messages else self.default_locale
        return self._fallback_messages.get(fallback_locale, self._fallback_messages["en"])
    
    def map_exception_to_message(
        self,
        exception: Exception,
        locale: Optional[str] = None,
        include_technical_details: bool = False
    ) -> UserMessage:
        """Map an exception to a user-friendly message."""
        from ..exceptions import (
            ValidationException, NotFoundException, UnauthorizedException,
            ForbiddenException, ConflictException, ExternalServiceException
        )
        from .exceptions import CircuitBreakerError, RetryExhaustedError
        
        # Map specific exception types to error codes
        exception_mappings = {
            ValidationException: "VALIDATION_ERROR",
            UnauthorizedException: "INVALID_CREDENTIALS", 
            ForbiddenException: "ACCESS_DENIED",
            NotFoundException: "RESOURCE_NOT_FOUND",
            ConflictException: "CONFLICT_ERROR",
            ExternalServiceException: "SERVICE_UNAVAILABLE",
            CircuitBreakerError: "SERVICE_UNAVAILABLE",
            RetryExhaustedError: "SYSTEM_ERROR",
            ConnectionError: "NETWORK_ERROR",
            TimeoutError: "NETWORK_ERROR"
        }
        
        # Find matching error code
        error_code = "UNKNOWN_ERROR"
        for exc_type, code in exception_mappings.items():
            if isinstance(exception, exc_type):
                error_code = code
                break
        
        # Get the user message
        user_message = self.get_user_message(error_code, locale)
        
        # Add technical details if requested
        if include_technical_details:
            user_message.technical_details = f"{type(exception).__name__}: {str(exception)}"
        
        return user_message
    
    def get_available_locales(self) -> list[str]:
        """Get list of available locales."""
        return list(self._message_mappings.keys())
    
    def get_error_codes_for_locale(self, locale: str) -> list[str]:
        """Get list of error codes available for a locale."""
        return list(self._message_mappings.get(locale, {}).keys())


class UserMessageFormatter:
    """Formats user messages for different output formats."""
    
    @staticmethod
    def to_dict(message: UserMessage, include_technical: bool = False) -> Dict[str, Any]:
        """Convert UserMessage to dictionary."""
        result = {
            "code": message.code,
            "message": message.message,
            "type": message.message_type.value,
            "suggested_actions": message.suggested_actions
        }
        
        if message.support_info:
            result["support_info"] = message.support_info
        
        if include_technical and message.technical_details:
            result["technical_details"] = message.technical_details
        
        return result
    
    @staticmethod
    def to_json(message: UserMessage, include_technical: bool = False) -> str:
        """Convert UserMessage to JSON string."""
        return json.dumps(
            UserMessageFormatter.to_dict(message, include_technical),
            ensure_ascii=False,
            indent=2
        )
    
    @staticmethod
    def to_html(message: UserMessage, include_technical: bool = False) -> str:
        """Convert UserMessage to HTML format."""
        css_class = {
            MessageType.ERROR: "error",
            MessageType.WARNING: "warning", 
            MessageType.INFO: "info",
            MessageType.SUCCESS: "success"
        }.get(message.message_type, "error")
        
        html = f'<div class="user-message {css_class}">'
        html += f'<h4>Error Code: {message.code}</h4>'
        html += f'<p class="message">{message.message}</p>'
        
        if message.suggested_actions:
            html += '<div class="suggested-actions">'
            html += '<h5>What you can do:</h5>'
            html += '<ul>'
            for action in message.suggested_actions:
                html += f'<li>{action}</li>'
            html += '</ul>'
            html += '</div>'
        
        if message.support_info:
            html += f'<div class="support-info">{message.support_info}</div>'
        
        if include_technical and message.technical_details:
            html += f'<div class="technical-details"><strong>Technical Details:</strong> {message.technical_details}</div>'
        
        html += '</div>'
        return html


# Global error message mapper instance
error_message_mapper = ErrorMessageMapper()