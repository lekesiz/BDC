"""
Comprehensive password policy enforcement and validation.
"""

import re
import hashlib
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import secrets
import requests
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging

@dataclass
class PasswordPolicy:
    """Password policy configuration."""
    min_length: int = 12
    max_length: int = 128
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    max_consecutive_identical: int = 2
    max_consecutive_sequential: int = 2
    min_unique_chars: int = 8
    history_count: int = 12  # Remember last N passwords
    max_age_days: int = 90
    min_age_hours: int = 24
    lockout_attempts: int = 5
    lockout_duration_minutes: int = 30
    require_mfa_after_days: int = 60
    complexity_score_threshold: int = 60

class PasswordValidator:
    """Comprehensive password validation service."""
    
    def __init__(self, policy: Optional[PasswordPolicy] = None):
        """Initialize password validator with policy."""
        self.policy = policy or PasswordPolicy()
        self.logger = logging.getLogger(__name__)
        
        # Load common password lists
        self.common_passwords = self._load_common_passwords()
        self.pwned_cache = {}  # Cache for pwned password checks
    
    def _load_common_passwords(self) -> set:
        """Load common passwords from various sources."""
        common_passwords = set()
        
        # Built-in common passwords
        builtin_common = [
            'password', '123456', '123456789', '12345678', '12345',
            'qwerty', 'abc123', 'password123', 'admin', 'letmein',
            'welcome', 'monkey', '1234567890', 'dragon', 'master',
            'iloveyou', 'sunshine', 'princess', 'football', 'charlie',
            'aa123456', 'donald', 'password1', 'guest', '123123'
        ]
        common_passwords.update(builtin_common)
        
        # Try to load from external files if available
        try:
            with open('common_passwords.txt', 'r') as f:
                for line in f:
                    common_passwords.add(line.strip().lower())
        except FileNotFoundError:
            pass
        
        return common_passwords
    
    def validate_password(self, password: str, username: str = "", 
                         email: str = "", user_data: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """Comprehensive password validation."""
        errors = []
        
        if not isinstance(password, str):
            errors.append("Password must be a string")
            return False, errors
        
        # Basic length checks
        if len(password) < self.policy.min_length:
            errors.append(f"Password must be at least {self.policy.min_length} characters long")
        
        if len(password) > self.policy.max_length:
            errors.append(f"Password must be no more than {self.policy.max_length} characters long")
        
        # Character composition checks
        if self.policy.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.policy.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.policy.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.policy.require_special:
            special_pattern = f'[{re.escape(self.policy.special_chars)}]'
            if not re.search(special_pattern, password):
                errors.append(f"Password must contain at least one special character ({self.policy.special_chars})")
        
        # Complexity checks
        unique_chars = len(set(password))
        if unique_chars < self.policy.min_unique_chars:
            errors.append(f"Password must contain at least {self.policy.min_unique_chars} unique characters")
        
        # Pattern checks
        if self._has_excessive_repetition(password):
            errors.append(f"Password cannot contain more than {self.policy.max_consecutive_identical} consecutive identical characters")
        
        if self._has_sequential_chars(password):
            errors.append(f"Password cannot contain more than {self.policy.max_consecutive_sequential} consecutive sequential characters")
        
        # Personal information checks
        if self._contains_personal_info(password, username, email, user_data):
            errors.append("Password cannot contain personal information")
        
        # Common password checks
        if self._is_common_password(password):
            errors.append("Password is too common and easily guessable")
        
        # Dictionary word checks
        if self._contains_dictionary_words(password):
            errors.append("Password should not contain common dictionary words")
        
        # Keyboard pattern checks
        if self._has_keyboard_patterns(password):
            errors.append("Password cannot contain keyboard patterns")
        
        # Complexity score check
        complexity_score = self._calculate_complexity_score(password)
        if complexity_score < self.policy.complexity_score_threshold:
            errors.append(f"Password complexity score ({complexity_score}) is below required threshold ({self.policy.complexity_score_threshold})")
        
        # Check against breached passwords (if enabled)
        if self._is_pwned_password(password):
            errors.append("This password has been found in data breaches and should not be used")
        
        return len(errors) == 0, errors
    
    def _has_excessive_repetition(self, password: str) -> bool:
        """Check for excessive character repetition."""
        count = 1
        for i in range(1, len(password)):
            if password[i] == password[i-1]:
                count += 1
                if count > self.policy.max_consecutive_identical:
                    return True
            else:
                count = 1
        return False
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters (abc, 123, etc.)."""
        sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            '0123456789',
            'qwertyuiop',
            'asdfghjkl',
            'zxcvbnm'
        ]
        
        password_lower = password.lower()
        
        for sequence in sequences:
            for i in range(len(sequence) - self.policy.max_consecutive_sequential):
                subseq = sequence[i:i + self.policy.max_consecutive_sequential + 1]
                if subseq in password_lower or subseq[::-1] in password_lower:
                    return True
        
        return False
    
    def _contains_personal_info(self, password: str, username: str, 
                               email: str, user_data: Optional[Dict]) -> bool:
        """Check if password contains personal information."""
        password_lower = password.lower()
        
        # Check username
        if username and len(username) >= 3 and username.lower() in password_lower:
            return True
        
        # Check email parts
        if email:
            email_parts = email.lower().split('@')[0]
            if len(email_parts) >= 3 and email_parts in password_lower:
                return True
        
        # Check user data if provided
        if user_data:
            personal_fields = ['first_name', 'last_name', 'name', 'company', 'phone']
            for field in personal_fields:
                value = user_data.get(field, '')
                if value and len(value) >= 3 and value.lower() in password_lower:
                    return True
        
        return False
    
    def _is_common_password(self, password: str) -> bool:
        """Check if password is in common passwords list."""
        return password.lower() in self.common_passwords
    
    def _contains_dictionary_words(self, password: str) -> bool:
        """Check for common English dictionary words."""
        # Simple dictionary words check
        common_words = [
            'password', 'welcome', 'computer', 'internet', 'security',
            'company', 'system', 'network', 'service', 'account',
            'login', 'access', 'admin', 'user', 'guest'
        ]
        
        password_lower = password.lower()
        for word in common_words:
            if len(word) >= 4 and word in password_lower:
                return True
        
        return False
    
    def _has_keyboard_patterns(self, password: str) -> bool:
        """Check for keyboard patterns."""
        keyboard_patterns = [
            'qwerty', 'qwertz', 'azerty', 'asdf', 'zxcv',
            '12345', '54321', 'abcde', 'edcba'
        ]
        
        password_lower = password.lower()
        for pattern in keyboard_patterns:
            if pattern in password_lower:
                return True
        
        return False
    
    def _calculate_complexity_score(self, password: str) -> int:
        """Calculate password complexity score (0-100)."""
        score = 0
        
        # Length bonus
        score += min(25, len(password) * 2)
        
        # Character variety bonus
        if re.search(r'[a-z]', password):
            score += 5
        if re.search(r'[A-Z]', password):
            score += 5
        if re.search(r'\d', password):
            score += 5
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 10
        
        # Unique characters bonus
        unique_chars = len(set(password))
        score += min(15, unique_chars)
        
        # Entropy bonus
        entropy = self._calculate_entropy(password)
        score += min(25, int(entropy / 2))
        
        # Penalty for patterns
        if self._has_keyboard_patterns(password):
            score -= 10
        
        if self._has_sequential_chars(password):
            score -= 10
        
        if self._has_excessive_repetition(password):
            score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy."""
        charset_size = 0
        
        if re.search(r'[a-z]', password):
            charset_size += 26
        if re.search(r'[A-Z]', password):
            charset_size += 26
        if re.search(r'\d', password):
            charset_size += 10
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            charset_size += 32
        
        if charset_size == 0:
            return 0
        
        import math
        return len(password) * math.log2(charset_size)
    
    def _is_pwned_password(self, password: str, timeout: int = 2) -> bool:
        """Check if password has been pwned using HaveIBeenPwned API."""
        try:
            # Hash the password
            sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            # Check cache first
            if sha1_hash in self.pwned_cache:
                return self.pwned_cache[sha1_hash]
            
            # Query HaveIBeenPwned API
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self._query_pwned_api, prefix)
                try:
                    response = future.result(timeout=timeout)
                    
                    if response and suffix in response:
                        self.pwned_cache[sha1_hash] = True
                        return True
                    
                    self.pwned_cache[sha1_hash] = False
                    return False
                    
                except TimeoutError:
                    self.logger.warning("Pwned password check timed out")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error checking pwned passwords: {e}")
            return False
    
    def _query_pwned_api(self, prefix: str) -> Optional[str]:
        """Query the HaveIBeenPwned API."""
        try:
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            headers = {'User-Agent': 'BDC-Security-Check'}
            
            response = requests.get(url, headers=headers, timeout=2)
            response.raise_for_status()
            
            return response.text
            
        except requests.RequestException as e:
            self.logger.warning(f"Pwned password API request failed: {e}")
            return None
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure password that meets policy requirements."""
        while True:
            # Ensure we have required character types
            chars = []
            
            if self.policy.require_lowercase:
                chars.extend(secrets.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(2))
            
            if self.policy.require_uppercase:
                chars.extend(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(2))
            
            if self.policy.require_digits:
                chars.extend(secrets.choice('0123456789') for _ in range(2))
            
            if self.policy.require_special:
                chars.extend(secrets.choice(self.policy.special_chars) for _ in range(2))
            
            # Fill remaining length with random characters from all allowed sets
            all_chars = ''
            if self.policy.require_lowercase:
                all_chars += 'abcdefghijklmnopqrstuvwxyz'
            if self.policy.require_uppercase:
                all_chars += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            if self.policy.require_digits:
                all_chars += '0123456789'
            if self.policy.require_special:
                all_chars += self.policy.special_chars
            
            while len(chars) < length:
                chars.append(secrets.choice(all_chars))
            
            # Shuffle the characters
            secrets.SystemRandom().shuffle(chars)
            password = ''.join(chars)
            
            # Validate the generated password
            is_valid, _ = self.validate_password(password)
            if is_valid:
                return password
    
    def check_password_age(self, last_changed: datetime) -> Tuple[bool, int]:
        """Check if password has expired."""
        days_since_change = (datetime.now() - last_changed).days
        expired = days_since_change >= self.policy.max_age_days
        return expired, days_since_change
    
    def can_change_password(self, last_changed: datetime) -> bool:
        """Check if password can be changed (minimum age check)."""
        hours_since_change = (datetime.now() - last_changed).total_seconds() / 3600
        return hours_since_change >= self.policy.min_age_hours
    
    def is_password_in_history(self, new_password: str, 
                              password_history: List[str]) -> bool:
        """Check if password was used recently."""
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        for old_password_hash in password_history[-self.policy.history_count:]:
            if new_hash == old_password_hash:
                return True
        
        return False
    
    def get_password_strength_feedback(self, password: str) -> Dict[str, Any]:
        """Get detailed feedback on password strength."""
        is_valid, errors = self.validate_password(password)
        complexity_score = self._calculate_complexity_score(password)
        entropy = self._calculate_entropy(password)
        
        # Strength categories
        if complexity_score >= 80:
            strength = "Very Strong"
        elif complexity_score >= 60:
            strength = "Strong"
        elif complexity_score >= 40:
            strength = "Medium"
        elif complexity_score >= 20:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return {
            'is_valid': is_valid,
            'strength': strength,
            'complexity_score': complexity_score,
            'entropy': round(entropy, 2),
            'errors': errors,
            'length': len(password),
            'unique_chars': len(set(password)),
            'has_uppercase': bool(re.search(r'[A-Z]', password)),
            'has_lowercase': bool(re.search(r'[a-z]', password)),
            'has_digits': bool(re.search(r'\d', password)),
            'has_special': bool(re.search(f'[{re.escape(self.policy.special_chars)}]', password)),
            'suggestions': self._get_improvement_suggestions(password, errors)
        }
    
    def _get_improvement_suggestions(self, password: str, errors: List[str]) -> List[str]:
        """Get suggestions for improving password."""
        suggestions = []
        
        if len(password) < self.policy.min_length:
            suggestions.append(f"Increase length to at least {self.policy.min_length} characters")
        
        if not re.search(r'[A-Z]', password):
            suggestions.append("Add uppercase letters")
        
        if not re.search(r'[a-z]', password):
            suggestions.append("Add lowercase letters")
        
        if not re.search(r'\d', password):
            suggestions.append("Add numbers")
        
        if not re.search(f'[{re.escape(self.policy.special_chars)}]', password):
            suggestions.append("Add special characters")
        
        if len(set(password)) < self.policy.min_unique_chars:
            suggestions.append("Use more unique characters")
        
        if self._has_keyboard_patterns(password):
            suggestions.append("Avoid keyboard patterns")
        
        if self._is_common_password(password):
            suggestions.append("Avoid common passwords")
        
        return suggestions