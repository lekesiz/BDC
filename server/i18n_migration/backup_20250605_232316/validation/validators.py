"""
Specialized validators for different data types and security concerns.
"""

import re
import ipaddress
import mimetypes
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
import phonenumbers
from email_validator import validate_email as validate_email_lib, EmailNotValidError


class BaseValidator:
    """Base class for all validators."""
    
    def validate(self, value: Any) -> Any:
        """Validate value. Should raise ValueError if invalid."""
        raise NotImplementedError
    
    def is_valid(self, value: Any) -> bool:
        """Check if value is valid without raising exception."""
        try:
            self.validate(value)
            return True
        except ValueError:
            return False


class EmailValidator(BaseValidator):
    """Email validation with advanced checks."""
    
    def __init__(self, check_deliverability: bool = False, 
                 allowed_domains: List[str] = None,
                 blocked_domains: List[str] = None):
        """
        Initialize email validator.
        
        Args:
            check_deliverability: Whether to check if email is deliverable
            allowed_domains: List of allowed email domains
            blocked_domains: List of blocked email domains
        """
        self.check_deliverability = check_deliverability
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or ['tempmail.com', 'throwaway.email', 'guerrillamail.com']
    
    def validate(self, email: str) -> str:
        """Validate email address."""
        if not email or not isinstance(email, str):
            raise ValueError("Email address is required")
        
        # Basic format validation using email-validator library
        try:
            validation = validate_email_lib(
                email,
                check_deliverability=self.check_deliverability
            )
            normalized_email = validation.email
        except EmailNotValidError as e:
            raise ValueError(str(e))
        
        # Extract domain
        domain = normalized_email.split('@')[1].lower()
        
        # Check allowed domains
        if self.allowed_domains and domain not in self.allowed_domains:
            raise ValueError(f"Email domain '{domain}' is not allowed")
        
        # Check blocked domains
        if domain in self.blocked_domains:
            raise ValueError(f"Email domain '{domain}' is not allowed")
        
        # Check for suspicious patterns
        local_part = normalized_email.split('@')[0]
        if re.search(r'(test|temp|fake|dummy)', local_part, re.IGNORECASE):
            raise ValueError("Email appears to be temporary or fake")
        
        return normalized_email


class PasswordValidator(BaseValidator):
    """Password validation with configurable complexity rules."""
    
    def __init__(self, min_length: int = 12, max_length: int = 128,
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_digits: bool = True,
                 require_special: bool = True,
                 special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?",
                 check_common: bool = True):
        """Initialize password validator."""
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.special_chars = special_chars
        self.check_common = check_common
        
        # Common weak passwords
        self.common_passwords = {
            'password', '12345678', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', '123123', 'dragon', 'iloveyou'
        }
    
    def validate(self, password: str) -> str:
        """Validate password against security requirements."""
        if not password or not isinstance(password, str):
            raise ValueError("Password is required")
        
        # Length check
        if len(password) < self.min_length:
            raise ValueError(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            raise ValueError(f"Password must not exceed {self.max_length} characters")
        
        # Complexity checks
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        
        if self.require_special and not re.search(f'[{re.escape(self.special_chars)}]', password):
            raise ValueError("Password must contain at least one special character")
        
        # Pattern checks
        if re.search(r'(.)\1{2,}', password):
            raise ValueError("Password cannot contain three or more consecutive identical characters")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890|098|987|876|765|654|543|432|321|210)', password):
            raise ValueError("Password cannot contain sequential numbers")
        
        if re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            raise ValueError("Password cannot contain sequential letters")
        
        # Common password check
        if self.check_common and password.lower() in self.common_passwords:
            raise ValueError("Password is too common. Please choose a more secure password")
        
        # Check for personal information patterns
        if re.search(r'(password|admin|user|login)', password, re.IGNORECASE):
            raise ValueError("Password cannot contain common words like 'password', 'admin', etc.")
        
        return password
    
    def get_strength(self, password: str) -> Dict[str, Any]:
        """Calculate password strength score and provide feedback."""
        score = 0
        feedback = []
        
        # Length score
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Complexity score
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(f'[{re.escape(self.special_chars)}]', password):
            score += 1
        
        # Diversity score
        unique_chars = len(set(password))
        if unique_chars >= 10:
            score += 1
        if unique_chars >= 15:
            score += 1
        
        # Determine strength level
        if score <= 3:
            strength = "weak"
            feedback.append("Consider using a longer password with more character variety")
        elif score <= 6:
            strength = "medium"
            feedback.append("Good password, but could be stronger")
        elif score <= 8:
            strength = "strong"
            feedback.append("Strong password")
        else:
            strength = "very_strong"
            feedback.append("Excellent password strength")
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback
        }


class URLValidator(BaseValidator):
    """URL validation with security checks."""
    
    def __init__(self, allowed_schemes: List[str] = None,
                 allowed_domains: List[str] = None,
                 blocked_domains: List[str] = None,
                 require_tld: bool = True):
        """Initialize URL validator."""
        self.allowed_schemes = allowed_schemes or ['http', 'https']
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
        self.require_tld = require_tld
    
    def validate(self, url: str) -> str:
        """Validate URL."""
        if not url or not isinstance(url, str):
            raise ValueError("URL is required")
        
        # Basic URL parsing
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValueError("Invalid URL format")
        
        # Scheme validation
        if not parsed.scheme:
            raise ValueError("URL must include a scheme (e.g., http://)")
        
        if parsed.scheme not in self.allowed_schemes:
            raise ValueError(f"URL scheme must be one of: {', '.join(self.allowed_schemes)}")
        
        # Domain validation
        if not parsed.netloc:
            raise ValueError("URL must include a domain")
        
        domain = parsed.netloc.lower()
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Check for IP address
        try:
            ipaddress.ip_address(domain)
            # It's an IP address - you might want to block these
            raise ValueError("IP addresses are not allowed in URLs")
        except ValueError:
            # Not an IP address, continue validation
            pass
        
        # TLD check
        if self.require_tld and '.' not in domain:
            raise ValueError("URL must include a valid top-level domain")
        
        # Allowed domains check
        if self.allowed_domains and domain not in self.allowed_domains:
            raise ValueError(f"Domain '{domain}' is not allowed")
        
        # Blocked domains check
        if domain in self.blocked_domains:
            raise ValueError(f"Domain '{domain}' is blocked")
        
        # Security checks
        if re.search(r'[<>\"\'`]', url):
            raise ValueError("URL contains invalid characters")
        
        # Check for URL injection attempts
        if re.search(r'(javascript:|data:|vbscript:)', url, re.IGNORECASE):
            raise ValueError("URL contains potentially dangerous protocol")
        
        return url


class FileValidator(BaseValidator):
    """File upload validation."""
    
    def __init__(self, allowed_extensions: List[str] = None,
                 allowed_mimetypes: List[str] = None,
                 max_size: int = 10 * 1024 * 1024,  # 10MB default
                 check_content: bool = True):
        """Initialize file validator."""
        self.allowed_extensions = allowed_extensions or [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'bmp'
        ]
        self.allowed_mimetypes = allowed_mimetypes or [
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'text/csv', 'image/jpeg', 'image/png', 'image/gif'
        ]
        self.max_size = max_size
        self.check_content = check_content
        
        # Dangerous file signatures
        self.dangerous_signatures = {
            b'MZ': 'Windows executable',
            b'\x7fELF': 'Linux executable',
            b'#!/': 'Shell script',
            b'<?php': 'PHP script',
            b'<%': 'Server-side script'
        }
    
    def validate(self, file_obj: Any) -> Dict[str, Any]:
        """Validate file upload."""
        if not file_obj:
            raise ValueError("No file provided")
        
        # Get filename
        filename = getattr(file_obj, 'filename', None)
        if not filename:
            raise ValueError("File must have a filename")
        
        # Extension check
        extension = self._get_extension(filename)
        if extension not in self.allowed_extensions:
            raise ValueError(f"File type '.{extension}' is not allowed")
        
        # MIME type check
        mimetype = getattr(file_obj, 'content_type', None) or mimetypes.guess_type(filename)[0]
        if mimetype and mimetype not in self.allowed_mimetypes:
            raise ValueError(f"MIME type '{mimetype}' is not allowed")
        
        # Size check
        file_obj.seek(0, 2)  # Seek to end
        size = file_obj.tell()
        file_obj.seek(0)  # Reset position
        
        if size > self.max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {self.max_size / 1024 / 1024:.1f}MB")
        
        # Content check
        if self.check_content:
            content = file_obj.read(1024)  # Read first 1KB
            file_obj.seek(0)  # Reset position
            
            for signature, description in self.dangerous_signatures.items():
                if content.startswith(signature):
                    raise ValueError(f"File appears to be {description}, which is not allowed")
        
        return {
            'filename': filename,
            'extension': extension,
            'mimetype': mimetype,
            'size': size
        }
    
    def _get_extension(self, filename: str) -> str:
        """Get file extension safely."""
        if '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower()


class JSONValidator(BaseValidator):
    """JSON data validation."""
    
    def __init__(self, max_depth: int = 10, max_size: int = 1024 * 1024):  # 1MB default
        """Initialize JSON validator."""
        self.max_depth = max_depth
        self.max_size = max_size
    
    def validate(self, data: Any, current_depth: int = 0) -> Any:
        """Validate JSON data structure."""
        if current_depth > self.max_depth:
            raise ValueError(f"JSON structure exceeds maximum depth of {self.max_depth}")
        
        if isinstance(data, dict):
            # Check dictionary size
            if len(str(data)) > self.max_size:
                raise ValueError(f"JSON data exceeds maximum size of {self.max_size} bytes")
            
            # Validate each key-value pair
            for key, value in data.items():
                if not isinstance(key, str):
                    raise ValueError("JSON keys must be strings")
                
                if len(key) > 255:
                    raise ValueError("JSON key too long")
                
                # Recursive validation
                self.validate(value, current_depth + 1)
        
        elif isinstance(data, list):
            # Check list size
            if len(data) > 10000:
                raise ValueError("JSON array too large")
            
            # Validate each item
            for item in data:
                self.validate(item, current_depth + 1)
        
        elif isinstance(data, str):
            # Check string length
            if len(data) > 100000:
                raise ValueError("JSON string value too long")
        
        elif not isinstance(data, (int, float, bool)) and data is not None:
            raise ValueError(f"Invalid JSON data type: {type(data).__name__}")
        
        return data


class SQLValidator(BaseValidator):
    """SQL injection prevention validator."""
    
    # Common SQL injection patterns
    SQL_PATTERNS = [
        r'\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|FROM|WHERE)\b',
        r'(--|#|\/\*|\*\/)',  # SQL comments
        r'(\bOR\b.*=.*\bOR\b|\bAND\b.*=.*\bAND\b)',  # OR/AND tricks
        r'(\'\s*OR\s*\'|\"\s*OR\s*\")',  # Quote-based injection
        r'(;|\||&&)',  # Command chaining
        r'(xp_|sp_)',  # SQL Server stored procedures
        r'(0x[0-9a-fA-F]+)',  # Hex encoding
        r'(CHAR\(|CONCAT\(|CHR\()',  # String manipulation functions
        r'(@@|@)',  # Variables
        r'(WAITFOR|DELAY|BENCHMARK)',  # Time-based attacks
        r'(INTO\s+(OUTFILE|DUMPFILE))',  # File operations
    ]
    
    def validate(self, value: str) -> str:
        """Validate input for SQL injection attempts."""
        if not isinstance(value, str):
            return str(value)
        
        # Check for SQL patterns
        for pattern in self.SQL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Input contains potentially dangerous SQL content")
        
        # Check for encoded attacks
        if self._contains_encoded_sql(value):
            raise ValueError("Input contains encoded SQL injection attempt")
        
        return value
    
    def _contains_encoded_sql(self, value: str) -> bool:
        """Check for encoded SQL injection attempts."""
        # URL decode check
        import urllib.parse
        decoded = urllib.parse.unquote(value)
        if decoded != value:
            # Check decoded value
            for pattern in self.SQL_PATTERNS:
                if re.search(pattern, decoded, re.IGNORECASE):
                    return True
        
        # Base64 check (if it looks like base64)
        if re.match(r'^[A-Za-z0-9+/]+=*$', value) and len(value) % 4 == 0:
            try:
                import base64
                decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
                for pattern in self.SQL_PATTERNS:
                    if re.search(pattern, decoded, re.IGNORECASE):
                        return True
            except:
                pass
        
        return False


class PhoneValidator(BaseValidator):
    """Phone number validation."""
    
    def __init__(self, default_region: str = 'US', 
                 allowed_regions: List[str] = None):
        """Initialize phone validator."""
        self.default_region = default_region
        self.allowed_regions = allowed_regions
    
    def validate(self, phone_number: str) -> str:
        """Validate phone number."""
        if not phone_number:
            raise ValueError("Phone number is required")
        
        try:
            # Parse phone number
            parsed = phonenumbers.parse(phone_number, self.default_region)
            
            # Check if valid
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            
            # Check region if restricted
            if self.allowed_regions:
                region = phonenumbers.region_code_for_number(parsed)
                if region not in self.allowed_regions:
                    raise ValueError(f"Phone numbers from {region} are not allowed")
            
            # Return formatted number
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )
            
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number format")


class DateValidator(BaseValidator):
    """Date and datetime validation."""
    
    def __init__(self, min_date: date = None, max_date: date = None,
                 allow_future: bool = True, allow_past: bool = True):
        """Initialize date validator."""
        self.min_date = min_date
        self.max_date = max_date
        self.allow_future = allow_future
        self.allow_past = allow_past
    
    def validate(self, value: Any) -> date:
        """Validate date."""
        if isinstance(value, datetime):
            date_value = value.date()
        elif isinstance(value, date):
            date_value = value
        elif isinstance(value, str):
            # Try common date formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d']:
                try:
                    date_value = datetime.strptime(value, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Invalid date format")
        else:
            raise ValueError("Invalid date type")
        
        # Range checks
        if self.min_date and date_value < self.min_date:
            raise ValueError(f"Date must be after {self.min_date}")
        
        if self.max_date and date_value > self.max_date:
            raise ValueError(f"Date must be before {self.max_date}")
        
        # Future/past checks
        today = date.today()
        if not self.allow_future and date_value > today:
            raise ValueError("Future dates are not allowed")
        
        if not self.allow_past and date_value < today:
            raise ValueError("Past dates are not allowed")
        
        return date_value


class CreditCardValidator(BaseValidator):
    """Credit card number validation."""
    
    def validate(self, card_number: str) -> str:
        """Validate credit card number using Luhn algorithm."""
        if not card_number:
            raise ValueError("Credit card number is required")
        
        # Remove spaces and hyphens
        card_number = re.sub(r'[\s\-]', '', card_number)
        
        # Check if all digits
        if not card_number.isdigit():
            raise ValueError("Credit card number must contain only digits")
        
        # Check length
        if len(card_number) < 13 or len(card_number) > 19:
            raise ValueError("Invalid credit card number length")
        
        # Luhn algorithm
        def luhn_check(number):
            digits = [int(d) for d in number]
            checksum = 0
            
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            
            return sum(digits) % 10 == 0
        
        if not luhn_check(card_number):
            raise ValueError("Invalid credit card number")
        
        # Mask for storage (show only last 4 digits)
        masked = '*' * (len(card_number) - 4) + card_number[-4:]
        
        return masked