"""
Translator
Handles translation of keys and text
"""

import re
import logging
from typing import Dict, Any, Optional, List, Union
from .config import I18nConfig

logger = logging.getLogger(__name__)

class Translator:
    """Translator for a specific language."""
    
    def __init__(self, language_code: str, translations: Dict[str, Any]):
        """Initialize translator with language and translations."""
        self.language_code = language_code
        self.translations = translations
        self.config = I18nConfig()
        self.missing_keys = set()
        self.language_config = self.config.get_language_config(language_code)
    
    def translate(self, key: str, **kwargs) -> str:
        """
        Translate a key with optional interpolation.
        
        Args:
            key: Translation key (e.g., 'common.welcome')
            **kwargs: Values for interpolation
            
        Returns:
            Translated string
        """
        # Handle array of keys (fallback)
        if isinstance(key, list):
            for k in key:
                translation = self._get_translation(k)
                if translation:
                    return self._interpolate(translation, **kwargs)
            # If no translation found, use first key
            key = key[0]
        
        # Get translation
        translation = self._get_translation(key)
        
        if not translation:
            # Track missing key
            self.missing_keys.add(key)
            
            # Return key with prefix if configured
            if self.config.TRANSLATION_MISSING_KEY_PREFIX:
                return f"{self.config.TRANSLATION_MISSING_KEY_PREFIX} {key}"
            return key
        
        # Handle pluralization
        if 'count' in kwargs:
            translation = self._pluralize(translation, kwargs['count'])
        
        # Handle context
        if 'context' in kwargs and isinstance(translation, dict):
            context_key = f"_{kwargs['context']}"
            if context_key in translation:
                translation = translation[context_key]
            elif '_default' in translation:
                translation = translation['_default']
        
        # Interpolate values
        return self._interpolate(translation, **kwargs)
    
    def _get_translation(self, key: str) -> Optional[Union[str, Dict]]:
        """Get translation value for a key."""
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def _interpolate(self, template: Union[str, Dict], **kwargs) -> str:
        """Interpolate values into translation template."""
        if isinstance(template, dict):
            # If still a dict, convert to string
            template = str(template)
        
        if not isinstance(template, str):
            return str(template)
        
        # Handle different interpolation patterns
        # {{variable}} style
        template = re.sub(
            r'\{\{([^}]+)\}\}',
            lambda m: str(kwargs.get(m.group(1).strip(), m.group(0))),
            template
        )
        
        # {variable} style
        template = re.sub(
            r'\{([^}]+)\}',
            lambda m: str(kwargs.get(m.group(1).strip(), m.group(0))),
            template
        )
        
        # %(variable)s style
        try:
            template = template % kwargs
        except (KeyError, ValueError, TypeError):
            pass
        
        return template
    
    def _pluralize(self, translation: Union[str, Dict], count: int) -> str:
        """Handle pluralization based on count."""
        if isinstance(translation, str):
            return translation
        
        if not isinstance(translation, dict):
            return str(translation)
        
        # Get pluralization rule for language
        plural_form = self._get_plural_form(count)
        
        # Try to find matching plural form
        if plural_form in translation:
            return translation[plural_form]
        
        # Fallback to other forms
        fallback_order = ['other', 'many', 'few', 'two', 'one', 'zero']
        for form in fallback_order:
            if form in translation:
                return translation[form]
        
        # If no plural forms found, return first value
        return next(iter(translation.values())) if translation else str(translation)
    
    def _get_plural_form(self, count: int) -> str:
        """Get plural form based on language rules."""
        if not self.language_config or not self.language_config.pluralization_rules:
            return 'other'
        
        rules = self.language_config.pluralization_rules
        n = abs(count)
        
        # Evaluate rules in order
        for form, rule in rules.items():
            try:
                # Safe evaluation of rule
                if self._evaluate_plural_rule(rule, n):
                    return form
            except Exception as e:
                logger.error(f"Error evaluating plural rule for {self.language_code}: {e}")
        
        return 'other'
    
    def _evaluate_plural_rule(self, rule: str, n: int) -> bool:
        """Safely evaluate a plural rule."""
        # Replace 'n' with actual number
        rule = rule.replace('n', str(n))
        
        # Only allow safe operations
        allowed_names = {
            'true': True,
            'false': False,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b,
            'not': lambda a: not a
        }
        
        try:
            # Use eval with restricted names
            return eval(rule, {"__builtins__": {}}, allowed_names)
        except:
            return False
    
    def translate_list(self, items: List[str], join_type: str = 'and') -> str:
        """Translate and join a list of items."""
        if not items:
            return ''
        
        if len(items) == 1:
            return items[0]
        
        # Get conjunction translation
        conjunction_key = f'common.{join_type}'
        conjunction = self.translate(conjunction_key)
        if conjunction == conjunction_key:
            conjunction = join_type
        
        if len(items) == 2:
            return f"{items[0]} {conjunction} {items[1]}"
        
        # For more than 2 items
        last_item = items[-1]
        other_items = ', '.join(items[:-1])
        return f"{other_items}, {conjunction} {last_item}"
    
    def has_translation(self, key: str) -> bool:
        """Check if a translation exists for a key."""
        return self._get_translation(key) is not None
    
    def get_namespace(self, namespace: str) -> Dict[str, Any]:
        """Get all translations for a namespace."""
        return self.translations.get(namespace, {})
    
    def get_missing_keys(self) -> List[str]:
        """Get list of missing translation keys."""
        return list(self.missing_keys)
    
    def clear_missing_keys(self):
        """Clear the missing keys set."""
        self.missing_keys.clear()
    
    def format_number(self, number: Union[int, float], style: str = 'decimal') -> str:
        """Format number according to language locale."""
        if not self.language_config:
            return str(number)
        
        # Get number format settings
        nf = self.language_config.number_format
        decimal_sep = nf.get('decimal', '.')
        thousand_sep = nf.get('thousand', ',')
        
        # Format based on style
        if style == 'decimal':
            # Convert to string with proper separators
            parts = str(float(number)).split('.')
            integer_part = parts[0]
            decimal_part = parts[1] if len(parts) > 1 else ''
            
            # Add thousand separators
            if thousand_sep and len(integer_part) > 3:
                integer_part = self._add_thousand_separators(integer_part, thousand_sep)
            
            # Combine parts
            if decimal_part:
                return f"{integer_part}{decimal_sep}{decimal_part}"
            return integer_part
            
        elif style == 'percent':
            formatted = self.format_number(number * 100)
            return f"{formatted}%"
            
        elif style == 'currency':
            formatted = self.format_number(number)
            currency = self.language_config.currency
            # Simple currency formatting - can be enhanced
            return f"{currency} {formatted}"
        
        return str(number)
    
    def _add_thousand_separators(self, number_str: str, separator: str) -> str:
        """Add thousand separators to a number string."""
        # Handle negative numbers
        negative = number_str.startswith('-')
        if negative:
            number_str = number_str[1:]
        
        # Add separators from right to left
        result = []
        for i, digit in enumerate(reversed(number_str)):
            if i > 0 and i % 3 == 0:
                result.append(separator)
            result.append(digit)
        
        formatted = ''.join(reversed(result))
        return f"-{formatted}" if negative else formatted