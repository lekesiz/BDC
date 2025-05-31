"""
Comprehensive input validation and sanitization.
"""

import re
import html
import bleach
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse
import sqlalchemy.sql.sqltypes as sql_types
from werkzeug.datastructures import FileStorage

class InputValidator:
    """Comprehensive input validation and sanitization service."""
    
    # XSS Protection patterns
    XSS_PATTERNS = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onmouseover\s*=',
        r'<iframe.*?>.*?</iframe>',
        r'<object.*?>.*?</object>',
        r'<embed.*?>.*?</embed>',
        r'<link.*?>',
        r'<meta.*?>',
        r'<style.*?>.*?</style>',
        r'expression\s*\(',
        r'url\s*\(',
        r'@import',
    ]
    
    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)',
        r'(\b(UNION|JOIN)\b.*\b(SELECT|FROM)\b)',
        r'(\b(OR|AND)\b.*[\'"].*[\'"])',
        r'(--|\/\*|\*\/)',
        r'(\bxp_\w+)',
        r'(\bsp_\w+)',
        r'(\b(CHAR|NCHAR|VARCHAR|NVARCHAR)\s*\(\s*\d+\s*\))',
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r'[;&|`$()]',
        r'\b(cat|ls|pwd|whoami|id|uname|ps|kill|rm|mv|cp|chmod|chown)\b',
        r'(\\|\/)(bin|etc|usr|var|tmp|home)',
        r'(\.\.|\.\/|~\/)',
    ]
    
    # Allowed HTML tags for rich text
    ALLOWED_HTML_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre', 'a', 'img'
    ]
    
    ALLOWED_HTML_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
        '*': ['class']
    }
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: Optional[int] = None, 
                       allow_html: bool = False) -> str:
        """Sanitize string input to prevent XSS and other attacks."""
        if not isinstance(value, str):
            value = str(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Limit length
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        if allow_html:
            # Use bleach to clean HTML
            value = bleach.clean(
                value,
                tags=cls.ALLOWED_HTML_TAGS,
                attributes=cls.ALLOWED_HTML_ATTRIBUTES,
                strip=True
            )
        else:
            # HTML escape for plain text
            value = html.escape(value)
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"Potentially malicious content detected: {pattern}")
        
        return value.strip()
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate and sanitize email address."""
        email = cls.sanitize_string(email, max_length=254)
        
        # RFC 5322 email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        
        return email.lower()
    
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate password against security policy."""
        if not isinstance(password, str):
            raise ValueError("Password must be a string")
        
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters long")
        
        if len(password) > 128:
            raise ValueError("Password is too long")
        
        # Check for required character types
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            raise ValueError("Password must contain at least one special character")
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            raise ValueError("Password cannot contain three or more consecutive identical characters")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):
            raise ValueError("Password cannot contain sequential numbers")
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            raise ValueError("Password cannot contain sequential letters")
        
        return password
    
    @classmethod
    def validate_url(cls, url: str, allowed_schemes: List[str] = None) -> str:
        """Validate and sanitize URL."""
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        url = cls.sanitize_string(url, max_length=2000)
        
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValueError("Invalid URL format")
        
        if parsed.scheme not in allowed_schemes:
            raise ValueError(f"URL scheme must be one of: {', '.join(allowed_schemes)}")
        
        if not parsed.netloc:
            raise ValueError("URL must have a valid domain")
        
        return url
    
    @classmethod
    def validate_sql_safe(cls, value: str) -> str:
        """Check for SQL injection patterns."""
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"Potentially malicious SQL content detected")
        
        return value
    
    @classmethod
    def validate_command_safe(cls, value: str) -> str:
        """Check for command injection patterns."""
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"Potentially malicious command content detected")
        
        return value
    
    @classmethod
    def validate_file_upload(cls, file: FileStorage) -> Dict[str, Any]:
        """Validate file upload security."""
        if not file or not file.filename:
            raise ValueError("No file provided")
        
        # Sanitize filename
        filename = cls.sanitize_string(file.filename, max_length=255)
        
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Check file extension
        if '.' not in filename:
            raise ValueError("File must have an extension")
        
        extension = filename.rsplit('.', 1)[1].lower()
        
        # Get all allowed extensions
        all_allowed = set()
        from .security_config import SecurityConfig
        for extensions in SecurityConfig.ALLOWED_FILE_EXTENSIONS.values():
            all_allowed.update(extensions)
        
        if extension not in all_allowed:
            raise ValueError(f"File type not allowed: {extension}")
        
        # Check file size
        if hasattr(file, 'content_length') and file.content_length:
            if file.content_length > SecurityConfig.MAX_FILE_SIZE:
                raise ValueError("File too large")
        
        # Additional security checks
        if extension in ['exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar', 'php', 'asp', 'aspx', 'jsp']:
            raise ValueError("Executable files are not allowed")
        
        return {
            'filename': filename,
            'extension': extension,
            'safe': True
        }
    
    @classmethod
    def validate_json_payload(cls, data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """Validate JSON payload for security issues."""
        if not isinstance(data, dict):
            raise ValueError("Payload must be a dictionary")
        
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise ValueError("JSON payload too deeply nested")
            
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if not isinstance(key, str) or len(key) > 100:
                        raise ValueError("Invalid key in JSON payload")
                    check_depth(value, current_depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1)
        
        check_depth(data)
        return data
    
    @classmethod
    def sanitize_form_data(cls, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize form data dictionary."""
        sanitized = {}
        
        for key, value in form_data.items():
            # Validate key
            key = cls.sanitize_string(str(key), max_length=100)
            
            if isinstance(value, str):
                sanitized[key] = cls.sanitize_string(value, max_length=10000)
            elif isinstance(value, (int, float, bool)):
                sanitized[key] = value
            elif isinstance(value, list):
                sanitized[key] = [
                    cls.sanitize_string(str(item), max_length=1000) 
                    if isinstance(item, str) else item 
                    for item in value[:100]  # Limit list size
                ]
            else:
                sanitized[key] = cls.sanitize_string(str(value), max_length=1000)
        
        return sanitized