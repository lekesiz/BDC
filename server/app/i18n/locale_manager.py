"""
Locale Manager
Handles date, time, number, and currency formatting
"""

import locale
import logging
from datetime import datetime, date, time
from typing import Union, Optional, Dict, Any
from decimal import Decimal
import babel
from babel import Locale
from babel.dates import format_date, format_datetime, format_time, format_timedelta
from babel.numbers import format_number, format_decimal, format_percent, format_currency
from babel.numbers import parse_number, parse_decimal

from .config import I18nConfig

logger = logging.getLogger(__name__)

class LocaleManager:
    """Manager for locale-specific formatting."""
    
    def __init__(self):
        """Initialize locale manager."""
        self.config = I18nConfig()
        self._locale_cache = {}
    
    def get_locale(self, language_code: str) -> Locale:
        """Get Babel locale object for a language."""
        if language_code not in self._locale_cache:
            language_config = self.config.get_language_config(language_code)
            if language_config:
                try:
                    self._locale_cache[language_code] = Locale.parse(
                        language_config.locale.replace('-', '_')
                    )
                except Exception as e:
                    logger.error(f"Failed to parse locale {language_config.locale}: {e}")
                    self._locale_cache[language_code] = Locale.parse('en_US')
            else:
                self._locale_cache[language_code] = Locale.parse('en_US')
        
        return self._locale_cache[language_code]
    
    def format_date(self, date_value: Union[datetime, date, str],
                   format_type: str = 'medium',
                   language_code: str = 'en') -> str:
        """Format date according to locale."""
        try:
            # Convert string to datetime if needed
            if isinstance(date_value, str):
                date_value = datetime.fromisoformat(date_value)
            
            locale_obj = self.get_locale(language_code)
            
            # Map format types to Babel formats
            format_map = {
                'short': 'short',
                'medium': 'medium',
                'long': 'long',
                'full': 'full'
            }
            
            babel_format = format_map.get(format_type, 'medium')
            
            return format_date(date_value, format=babel_format, locale=locale_obj)
            
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            return str(date_value)
    
    def format_time(self, time_value: Union[datetime, time, str],
                   format_type: str = 'medium',
                   language_code: str = 'en') -> str:
        """Format time according to locale."""
        try:
            # Convert string to datetime if needed
            if isinstance(time_value, str):
                time_value = datetime.fromisoformat(time_value)
            
            locale_obj = self.get_locale(language_code)
            
            # Map format types to Babel formats
            format_map = {
                'short': 'short',
                'medium': 'medium',
                'long': 'long',
                'full': 'full'
            }
            
            babel_format = format_map.get(format_type, 'medium')
            
            return format_time(time_value, format=babel_format, locale=locale_obj)
            
        except Exception as e:
            logger.error(f"Error formatting time: {e}")
            return str(time_value)
    
    def format_datetime(self, datetime_value: Union[datetime, str],
                       format_type: str = 'medium',
                       language_code: str = 'en') -> str:
        """Format datetime according to locale."""
        try:
            # Convert string to datetime if needed
            if isinstance(datetime_value, str):
                datetime_value = datetime.fromisoformat(datetime_value)
            
            locale_obj = self.get_locale(language_code)
            
            # Map format types to Babel formats
            format_map = {
                'short': 'short',
                'medium': 'medium',
                'long': 'long',
                'full': 'full'
            }
            
            babel_format = format_map.get(format_type, 'medium')
            
            return format_datetime(datetime_value, format=babel_format, locale=locale_obj)
            
        except Exception as e:
            logger.error(f"Error formatting datetime: {e}")
            return str(datetime_value)
    
    def format_timedelta(self, delta_value: Union[datetime, int],
                        granularity: str = 'second',
                        language_code: str = 'en',
                        add_direction: bool = True) -> str:
        """Format time delta (relative time)."""
        try:
            locale_obj = self.get_locale(language_code)
            
            # Convert to timedelta if needed
            if isinstance(delta_value, datetime):
                delta_value = datetime.now() - delta_value
            
            return format_timedelta(
                delta_value,
                granularity=granularity,
                locale=locale_obj,
                add_direction=add_direction
            )
            
        except Exception as e:
            logger.error(f"Error formatting timedelta: {e}")
            return str(delta_value)
    
    def format_number(self, number_value: Union[int, float, Decimal, str],
                     format_type: str = 'decimal',
                     language_code: str = 'en',
                     **kwargs) -> str:
        """Format number according to locale."""
        try:
            # Convert string to number if needed
            if isinstance(number_value, str):
                number_value = Decimal(number_value)
            
            locale_obj = self.get_locale(language_code)
            
            if format_type == 'decimal':
                return format_decimal(number_value, locale=locale_obj, **kwargs)
            elif format_type == 'percent':
                return format_percent(number_value, locale=locale_obj, **kwargs)
            elif format_type == 'scientific':
                return format_number(number_value, locale=locale_obj, **kwargs)
            else:
                return format_number(number_value, locale=locale_obj, **kwargs)
            
        except Exception as e:
            logger.error(f"Error formatting number: {e}")
            return str(number_value)
    
    def format_currency(self, amount: Union[int, float, Decimal, str],
                       currency_code: Optional[str] = None,
                       language_code: str = 'en',
                       **kwargs) -> str:
        """Format currency according to locale."""
        try:
            # Convert string to number if needed
            if isinstance(amount, str):
                amount = Decimal(amount)
            
            locale_obj = self.get_locale(language_code)
            
            # Get default currency for language if not specified
            if not currency_code:
                language_config = self.config.get_language_config(language_code)
                currency_code = language_config.currency if language_config else 'USD'
            
            return format_currency(
                amount,
                currency_code,
                locale=locale_obj,
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Error formatting currency: {e}")
            return f"{currency_code} {amount}"
    
    def parse_number(self, number_str: str, language_code: str = 'en') -> float:
        """Parse localized number string."""
        try:
            locale_obj = self.get_locale(language_code)
            return parse_number(number_str, locale=locale_obj)
        except Exception as e:
            logger.error(f"Error parsing number: {e}")
            # Try basic parsing
            return float(number_str.replace(',', '').replace(' ', ''))
    
    def parse_decimal(self, decimal_str: str, language_code: str = 'en') -> Decimal:
        """Parse localized decimal string."""
        try:
            locale_obj = self.get_locale(language_code)
            return parse_decimal(decimal_str, locale=locale_obj)
        except Exception as e:
            logger.error(f"Error parsing decimal: {e}")
            # Try basic parsing
            return Decimal(decimal_str.replace(',', '').replace(' ', ''))
    
    def get_calendar_info(self, language_code: str = 'en') -> Dict[str, Any]:
        """Get calendar information for a locale."""
        try:
            locale_obj = self.get_locale(language_code)
            
            # Get day and month names
            return {
                'months': list(locale_obj.months['format']['wide'].values()),
                'months_short': list(locale_obj.months['format']['abbreviated'].values()),
                'weekdays': list(locale_obj.days['format']['wide'].values()),
                'weekdays_short': list(locale_obj.days['format']['abbreviated'].values()),
                'first_week_day': locale_obj.first_week_day,
                'weekend_start': locale_obj.weekend_start,
                'weekend_end': locale_obj.weekend_end
            }
            
        except Exception as e:
            logger.error(f"Error getting calendar info: {e}")
            return {}
    
    def get_number_symbols(self, language_code: str = 'en') -> Dict[str, str]:
        """Get number formatting symbols for a locale."""
        try:
            locale_obj = self.get_locale(language_code)
            
            return {
                'decimal': locale_obj.number_symbols.get('decimal', '.'),
                'group': locale_obj.number_symbols.get('group', ','),
                'percent': locale_obj.number_symbols.get('percentSign', '%'),
                'plus': locale_obj.number_symbols.get('plusSign', '+'),
                'minus': locale_obj.number_symbols.get('minusSign', '-')
            }
            
        except Exception as e:
            logger.error(f"Error getting number symbols: {e}")
            return {
                'decimal': '.',
                'group': ',',
                'percent': '%',
                'plus': '+',
                'minus': '-'
            }
    
    def format_file_size(self, bytes_value: int, language_code: str = 'en') -> str:
        """Format file size with locale-specific units."""
        try:
            locale_obj = self.get_locale(language_code)
            
            # Define units
            units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
            
            size = float(bytes_value)
            unit_index = 0
            
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024
                unit_index += 1
            
            # Format the number
            formatted_size = format_decimal(size, format='#,##0.##', locale=locale_obj)
            
            return f"{formatted_size} {units[unit_index]}"
            
        except Exception as e:
            logger.error(f"Error formatting file size: {e}")
            return f"{bytes_value} B"
    
    def format_distance(self, meters: Union[int, float],
                       language_code: str = 'en',
                       unit_system: str = 'metric') -> str:
        """Format distance with appropriate units."""
        try:
            locale_obj = self.get_locale(language_code)
            
            if unit_system == 'imperial':
                # Convert to miles/feet
                if meters >= 1609.34:  # 1 mile
                    miles = meters / 1609.34
                    formatted = format_decimal(miles, format='#,##0.##', locale=locale_obj)
                    return f"{formatted} mi"
                else:
                    feet = meters * 3.28084
                    formatted = format_decimal(feet, format='#,##0', locale=locale_obj)
                    return f"{formatted} ft"
            else:
                # Metric system
                if meters >= 1000:
                    km = meters / 1000
                    formatted = format_decimal(km, format='#,##0.##', locale=locale_obj)
                    return f"{formatted} km"
                else:
                    formatted = format_decimal(meters, format='#,##0', locale=locale_obj)
                    return f"{formatted} m"
            
        except Exception as e:
            logger.error(f"Error formatting distance: {e}")
            return f"{meters} m"