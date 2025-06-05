"""Locale service for date, time, and number formatting."""

import locale
import logging
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, Dict, Any, List
from babel import Locale, dates, numbers
from babel.core import UnknownLocaleError
from app.services.i18n.language_detection_service import LanguageDetectionService

logger = logging.getLogger(__name__)


class LocaleService:
    """Service for handling locale-specific formatting."""
    
    # Locale mappings for supported languages
    LOCALE_MAPPINGS = {
        'en': 'en_US',
        'tr': 'tr_TR',
        'ar': 'ar_SA',
        'es': 'es_ES',
        'fr': 'fr_FR',
        'de': 'de_DE',
        'ru': 'ru_RU'
    }
    
    # Currency mappings for locales
    CURRENCY_MAPPINGS = {
        'en_US': 'USD',
        'tr_TR': 'TRY',
        'ar_SA': 'SAR',
        'es_ES': 'EUR',
        'fr_FR': 'EUR',
        'de_DE': 'EUR',
        'ru_RU': 'RUB'
    }
    
    # Time zone mappings
    TIMEZONE_MAPPINGS = {
        'en_US': 'America/New_York',
        'tr_TR': 'Europe/Istanbul',
        'ar_SA': 'Asia/Riyadh',
        'es_ES': 'Europe/Madrid',
        'fr_FR': 'Europe/Paris',
        'de_DE': 'Europe/Berlin',
        'ru_RU': 'Europe/Moscow'
    }
    
    def __init__(self):
        """Initialize locale service."""
        self.language_service = LanguageDetectionService()
        self._locale_cache = {}
    
    def get_locale(self, language_code: str) -> Optional[Locale]:
        """
        Get Babel Locale object for language code.
        
        Args:
            language_code: Language code
            
        Returns:
            Babel Locale object or None
        """
        try:
            language_code = self.language_service.normalize_language_code(language_code)
            
            if language_code in self._locale_cache:
                return self._locale_cache[language_code]
            
            locale_code = self.LOCALE_MAPPINGS.get(language_code, 'en_US')
            
            try:
                babel_locale = Locale.parse(locale_code)
                self._locale_cache[language_code] = babel_locale
                return babel_locale
            except UnknownLocaleError:
                # Fallback to English
                fallback_locale = Locale.parse('en_US')
                self._locale_cache[language_code] = fallback_locale
                return fallback_locale
                
        except Exception as e:
            logger.error(f"Error getting locale for {language_code}: {e}")
            return None
    
    def format_date(self, date_obj: date, language_code: str, format_type: str = 'medium') -> str:
        """
        Format date according to locale.
        
        Args:
            date_obj: Date object to format
            language_code: Language code
            format_type: Format type ('short', 'medium', 'long', 'full')
            
        Returns:
            Formatted date string
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return date_obj.strftime('%Y-%m-%d')
            
            return dates.format_date(date_obj, format=format_type, locale=babel_locale)
            
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            return date_obj.strftime('%Y-%m-%d')
    
    def format_datetime(self, datetime_obj: datetime, language_code: str, format_type: str = 'medium') -> str:
        """
        Format datetime according to locale.
        
        Args:
            datetime_obj: Datetime object to format
            language_code: Language code
            format_type: Format type ('short', 'medium', 'long', 'full')
            
        Returns:
            Formatted datetime string
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            return dates.format_datetime(datetime_obj, format=format_type, locale=babel_locale)
            
        except Exception as e:
            logger.error(f"Error formatting datetime: {e}")
            return datetime_obj.strftime('%Y-%m-%d %H:%M:%S')
    
    def format_time(self, time_obj: time, language_code: str, format_type: str = 'medium') -> str:
        """
        Format time according to locale.
        
        Args:
            time_obj: Time object to format
            language_code: Language code
            format_type: Format type ('short', 'medium', 'long', 'full')
            
        Returns:
            Formatted time string
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return time_obj.strftime('%H:%M:%S')
            
            return dates.format_time(time_obj, format=format_type, locale=babel_locale)
            
        except Exception as e:
            logger.error(f"Error formatting time: {e}")
            return time_obj.strftime('%H:%M:%S')
    
    def format_currency(self, amount: float, language_code: str, currency_code: Optional[str] = None) -> str:
        """
        Format currency amount according to locale.
        
        Args:
            amount: Amount to format
            language_code: Language code
            currency_code: Currency code (e.g., 'USD', 'EUR')
            
        Returns:
            Formatted currency string
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return f"{amount:.2f}"
            
            # Use provided currency or default for locale
            if not currency_code:
                locale_code = self.LOCALE_MAPPINGS.get(language_code, 'en_US')
                currency_code = self.CURRENCY_MAPPINGS.get(locale_code, 'USD')
            
            return numbers.format_currency(amount, currency_code, locale=babel_locale)
            
        except Exception as e:
            logger.error(f"Error formatting currency: {e}")
            return f"{amount:.2f} {currency_code or 'USD'}"
    
    def format_number(self, number: float, language_code: str, decimal_places: Optional[int] = None) -> str:
        """
        Format number according to locale.
        
        Args:
            number: Number to format
            language_code: Language code
            decimal_places: Number of decimal places
            
        Returns:
            Formatted number string
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                if decimal_places is not None:
                    return f"{number:.{decimal_places}f}"
                return str(number)
            
            if decimal_places is not None:
                format_pattern = f"#,##0.{'0' * decimal_places}"
                return numbers.format_decimal(number, format=format_pattern, locale=babel_locale)
            
            return numbers.format_decimal(number, locale=babel_locale)
            
        except Exception as e:
            logger.error(f"Error formatting number: {e}")
            return str(number)
    
    def format_percent(self, number: float, language_code: str, decimal_places: int = 1) -> str:
        """
        Format percentage according to locale.
        
        Args:
            number: Number to format as percentage (0.0-1.0)
            language_code: Language code
            decimal_places: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return f"{number * 100:.{decimal_places}f}%"
            
            format_pattern = f"#,##0.{'0' * decimal_places}%"
            return numbers.format_percent(number, format=format_pattern, locale=babel_locale)
            
        except Exception as e:
            logger.error(f"Error formatting percent: {e}")
            return f"{number * 100:.{decimal_places}f}%"
    
    def get_relative_time(self, datetime_obj: datetime, language_code: str, base_datetime: Optional[datetime] = None) -> str:
        """
        Get relative time description (e.g., "2 hours ago", "in 3 days").
        
        Args:
            datetime_obj: Datetime to describe
            language_code: Language code
            base_datetime: Base datetime (defaults to now)
            
        Returns:
            Relative time string
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return str(datetime_obj)
            
            if base_datetime is None:
                base_datetime = datetime.now()
            
            return dates.format_timedelta(
                datetime_obj - base_datetime,
                granularity='second',
                locale=babel_locale
            )
            
        except Exception as e:
            logger.error(f"Error formatting relative time: {e}")
            return str(datetime_obj)
    
    def get_weekday_names(self, language_code: str, width: str = 'wide') -> List[str]:
        """
        Get weekday names for a locale.
        
        Args:
            language_code: Language code
            width: Width ('narrow', 'abbreviated', 'wide')
            
        Returns:
            List of weekday names
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            weekdays = []
            for i in range(7):  # Monday = 0, Sunday = 6
                weekday_name = babel_locale.days[width][i]
                weekdays.append(weekday_name)
            
            return weekdays
            
        except Exception as e:
            logger.error(f"Error getting weekday names: {e}")
            return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    def get_month_names(self, language_code: str, width: str = 'wide') -> List[str]:
        """
        Get month names for a locale.
        
        Args:
            language_code: Language code
            width: Width ('narrow', 'abbreviated', 'wide')
            
        Returns:
            List of month names
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
            
            months = []
            for i in range(1, 13):  # January = 1, December = 12
                month_name = babel_locale.months[width][i]
                months.append(month_name)
            
            return months
            
        except Exception as e:
            logger.error(f"Error getting month names: {e}")
            return ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    def get_locale_info(self, language_code: str) -> Dict[str, Any]:
        """
        Get comprehensive locale information.
        
        Args:
            language_code: Language code
            
        Returns:
            Locale information dictionary
        """
        try:
            babel_locale = self.get_locale(language_code)
            language_info = self.language_service.get_language_info(language_code)
            
            if not babel_locale:
                return language_info
            
            locale_code = self.LOCALE_MAPPINGS.get(language_code, 'en_US')
            
            return {
                **language_info,
                'locale_code': locale_code,
                'display_name': babel_locale.display_name,
                'english_name': babel_locale.english_name,
                'currency': self.CURRENCY_MAPPINGS.get(locale_code, 'USD'),
                'timezone': self.TIMEZONE_MAPPINGS.get(locale_code, 'UTC'),
                'number_symbols': {
                    'decimal': babel_locale.number_symbols.get('decimal', '.'),
                    'group': babel_locale.number_symbols.get('group', ','),
                    'percent': babel_locale.number_symbols.get('percentSign', '%')
                },
                'date_formats': {
                    'short': babel_locale.date_formats['short'].pattern,
                    'medium': babel_locale.date_formats['medium'].pattern,
                    'long': babel_locale.date_formats['long'].pattern,
                    'full': babel_locale.date_formats['full'].pattern
                },
                'time_formats': {
                    'short': babel_locale.time_formats['short'].pattern,
                    'medium': babel_locale.time_formats['medium'].pattern,
                    'long': babel_locale.time_formats['long'].pattern,
                    'full': babel_locale.time_formats['full'].pattern
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting locale info: {e}")
            return self.language_service.get_language_info(language_code)
    
    def get_first_day_of_week(self, language_code: str) -> int:
        """
        Get first day of week for locale (0=Monday, 6=Sunday).
        
        Args:
            language_code: Language code
            
        Returns:
            First day of week (0-6)
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return 0  # Monday
            
            # Babel uses 0=Monday, 6=Sunday
            return babel_locale.first_week_day
            
        except Exception as e:
            logger.error(f"Error getting first day of week: {e}")
            return 0  # Default to Monday
    
    def parse_date(self, date_string: str, language_code: str, format_type: str = 'medium') -> Optional[date]:
        """
        Parse date string according to locale.
        
        Args:
            date_string: Date string to parse
            language_code: Language code
            format_type: Format type ('short', 'medium', 'long', 'full')
            
        Returns:
            Parsed date object or None
        """
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return datetime.strptime(date_string, '%Y-%m-%d').date()
            
            parsed_datetime = dates.parse_date(date_string, locale=babel_locale)
            return parsed_datetime
            
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            # Try common formats as fallback
            common_formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d.%m.%Y']
            for fmt in common_formats:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            return None
    
    def get_calendar_data(self, language_code: str) -> Dict[str, Any]:
        """
        Get calendar data for locale (weekday/month names, first day of week, etc.).
        
        Args:
            language_code: Language code
            
        Returns:
            Calendar data dictionary
        """
        try:
            return {
                'weekdays': {
                    'narrow': self.get_weekday_names(language_code, 'narrow'),
                    'abbreviated': self.get_weekday_names(language_code, 'abbreviated'),
                    'wide': self.get_weekday_names(language_code, 'wide')
                },
                'months': {
                    'narrow': self.get_month_names(language_code, 'narrow'),
                    'abbreviated': self.get_month_names(language_code, 'abbreviated'),
                    'wide': self.get_month_names(language_code, 'wide')
                },
                'first_day_of_week': self.get_first_day_of_week(language_code),
                'is_rtl': self.language_service.is_rtl_language(language_code)
            }
            
        except Exception as e:
            logger.error(f"Error getting calendar data: {e}")
            return {
                'weekdays': {
                    'narrow': ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
                    'abbreviated': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    'wide': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                },
                'months': {
                    'narrow': ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
                    'abbreviated': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    'wide': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
                },
                'first_day_of_week': 0,
                'is_rtl': False
            }