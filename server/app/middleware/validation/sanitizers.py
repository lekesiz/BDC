"""
Input sanitization utilities.
"""

import re
import html
import bleach
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse, quote
import unicodedata


class InputSanitizer:
    """
    Comprehensive input sanitization for various data types.
    """
    
    # Allowed HTML tags and attributes for rich text
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'i', 'b',
        'ol', 'ul', 'li', 'blockquote', 'code', 'pre',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'a', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th'
    ]
    
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'width', 'height', 'title'],
        'blockquote': ['cite'],
        '*': ['class', 'id']
    }
    
    # Allowed protocols for URLs
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto', 'tel']
    
    def sanitize_string(self, value: Any, max_length: Optional[int] = None,
                       trim: bool = True, lowercase: bool = False) -> str:
        """
        Sanitize a string value.
        
        Args:
            value: Value to sanitize
            max_length: Maximum allowed length
            trim: Whether to trim whitespace
            lowercase: Whether to convert to lowercase
            
        Returns:
            Sanitized string
        """
        if value is None:
            return ''
        
        # Convert to string
        sanitized = str(value)
        
        # Remove null bytes and other control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        # Normalize unicode
        sanitized = unicodedata.normalize('NFKC', sanitized)
        
        # Trim whitespace
        if trim:
            sanitized = sanitized.strip()
        
        # Convert to lowercase if requested
        if lowercase:
            sanitized = sanitized.lower()
        
        # Limit length
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def sanitize_html(self, html_content: str, allowed_tags: List[str] = None,
                     allowed_attributes: Dict[str, List[str]] = None) -> str:
        """
        Sanitize HTML content to prevent XSS.
        
        Args:
            html_content: HTML content to sanitize
            allowed_tags: List of allowed HTML tags
            allowed_attributes: Dict of allowed attributes per tag
            
        Returns:
            Sanitized HTML
        """
        if not html_content:
            return ''
        
        # Use default allowed tags/attributes if not provided
        if allowed_tags is None:
            allowed_tags = self.ALLOWED_TAGS
        
        if allowed_attributes is None:
            allowed_attributes = self.ALLOWED_ATTRIBUTES
        
        # Clean HTML using bleach
        cleaned = bleach.clean(
            html_content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            protocols=self.ALLOWED_PROTOCOLS,
            strip=True
        )
        
        # Additional XSS prevention
        cleaned = self._remove_dangerous_content(cleaned)
        
        return cleaned
    
    def sanitize_email(self, email: str) -> str:
        """
        Sanitize email address.
        
        Args:
            email: Email address to sanitize
            
        Returns:
            Sanitized email
        """
        if not email:
            return ''
        
        # Basic sanitization
        email = self.sanitize_string(email, max_length=254, lowercase=True)
        
        # Remove any HTML tags
        email = bleach.clean(email, tags=[], strip=True)
        
        # Validate basic email format
        if '@' not in email:
            return ''
        
        local, domain = email.rsplit('@', 1)
        
        # Sanitize local part (before @)
        local = re.sub(r'[^\w\.\-\+]', '', local)
        
        # Sanitize domain
        domain = re.sub(r'[^\w\.\-]', '', domain)
        
        return f"{local}@{domain}" if local and domain else ''
    
    def sanitize_url(self, url: str, allowed_schemes: List[str] = None) -> str:
        """
        Sanitize URL.
        
        Args:
            url: URL to sanitize
            allowed_schemes: List of allowed URL schemes
            
        Returns:
            Sanitized URL
        """
        if not url:
            return ''
        
        if allowed_schemes is None:
            allowed_schemes = self.ALLOWED_PROTOCOLS
        
        # Basic sanitization
        url = self.sanitize_string(url, max_length=2000)
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in allowed_schemes:
                return ''
            
            # Rebuild URL with only safe components
            safe_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            if parsed.query:
                safe_url += f"?{parsed.query}"
            
            if parsed.fragment:
                safe_url += f"#{parsed.fragment}"
            
            return safe_url
            
        except Exception:
            return ''
    
    def sanitize_filename(self, filename: str, max_length: int = 255) -> str:
        """
        Sanitize filename for safe storage.
        
        Args:
            filename: Filename to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return ''
        
        # Remove path components
        filename = filename.split('/')[-1].split('\\')[-1]
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\.\-]', '', filename)
        
        # Remove multiple dots (prevent directory traversal)
        filename = re.sub(r'\.+', '.', filename)
        
        # Ensure it has an extension
        if '.' not in filename:
            filename += '.txt'
        
        # Limit length
        if len(filename) > max_length:
            name, ext = filename.rsplit('.', 1)
            max_name_length = max_length - len(ext) - 1
            filename = f"{name[:max_name_length]}.{ext}"
        
        return filename
    
    def sanitize_dict(self, data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary values.
        
        Args:
            data: Dictionary to sanitize
            max_depth: Maximum recursion depth
            
        Returns:
            Sanitized dictionary
        """
        if max_depth <= 0:
            raise ValueError("Maximum recursion depth exceeded")
        
        sanitized = {}
        
        for key, value in data.items():
            # Sanitize key
            safe_key = self.sanitize_string(str(key), max_length=100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[safe_key] = self.sanitize_dict(value, max_depth - 1)
            elif isinstance(value, list):
                sanitized[safe_key] = self.sanitize_list(value, max_depth - 1)
            elif isinstance(value, (int, float, bool)) or value is None:
                sanitized[safe_key] = value
            else:
                # Convert other types to string and sanitize
                sanitized[safe_key] = self.sanitize_string(str(value))
        
        return sanitized
    
    def sanitize_list(self, data: List[Any], max_depth: int = 10) -> List[Any]:
        """
        Recursively sanitize list values.
        
        Args:
            data: List to sanitize
            max_depth: Maximum recursion depth
            
        Returns:
            Sanitized list
        """
        if max_depth <= 0:
            raise ValueError("Maximum recursion depth exceeded")
        
        sanitized = []
        
        for value in data[:1000]:  # Limit list size to prevent DoS
            if isinstance(value, str):
                sanitized.append(self.sanitize_string(value))
            elif isinstance(value, dict):
                sanitized.append(self.sanitize_dict(value, max_depth - 1))
            elif isinstance(value, list):
                sanitized.append(self.sanitize_list(value, max_depth - 1))
            elif isinstance(value, (int, float, bool)) or value is None:
                sanitized.append(value)
            else:
                sanitized.append(self.sanitize_string(str(value)))
        
        return sanitized
    
    def sanitize_sql_identifier(self, identifier: str) -> str:
        """
        Sanitize SQL identifier (table/column name).
        
        Args:
            identifier: SQL identifier to sanitize
            
        Returns:
            Sanitized identifier
        """
        # Only allow alphanumeric and underscore
        sanitized = re.sub(r'[^\w]', '', identifier)
        
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = 'col_' + sanitized
        
        # Limit length
        return sanitized[:64] if sanitized else 'column'
    
    def _remove_dangerous_content(self, content: str) -> str:
        """Remove potentially dangerous content from sanitized HTML."""
        # Remove javascript: protocol
        content = re.sub(r'javascript:', '', content, flags=re.IGNORECASE)
        
        # Remove vbscript: protocol
        content = re.sub(r'vbscript:', '', content, flags=re.IGNORECASE)
        
        # Remove data: protocol (can be used for XSS)
        content = re.sub(r'data:.*?base64', '', content, flags=re.IGNORECASE)
        
        # Remove event handlers
        content = re.sub(r'on\w+\s*=', '', content, flags=re.IGNORECASE)
        
        # Remove style tags with expression
        content = re.sub(r'expression\s*\(', '', content, flags=re.IGNORECASE)
        
        return content
    
    def escape_html(self, text: str) -> str:
        """
        HTML escape text for safe display.
        
        Args:
            text: Text to escape
            
        Returns:
            HTML-escaped text
        """
        if not text:
            return ''
        
        return html.escape(str(text))
    
    def unescape_html(self, text: str) -> str:
        """
        Unescape HTML entities.
        
        Args:
            text: Text to unescape
            
        Returns:
            Unescaped text
        """
        if not text:
            return ''
        
        return html.unescape(str(text))