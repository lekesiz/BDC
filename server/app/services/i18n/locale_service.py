from flask_babel import _

_('i18n_locale_service.validation.locale_service_for_date_time')
import locale
import logging
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, Dict, Any, List
from babel import Locale, dates, numbers
from babel.core import UnknownLocaleError
from app.services.i18n.language_detection_service import LanguageDetectionService
from flask_babel import _, lazy_gettext as _l
logger = logging.getLogger(__name__)


class LocaleService:
    _('i18n_locale_service.validation.service_for_handling_locale_sp')
    LOCALE_MAPPINGS = {'en': _('i18n_locale_service.message.en_us_6'), 'tr':
        _('i18n_locale_service.message.tr_tr_2'), 'ar': _(
        'i18n_locale_service.message.ar_sa_2'), 'es': _(
        'i18n_locale_service.message.es_es_2'), 'fr': _(
        'i18n_locale_service.message.fr_fr_2'), 'de': _(
        'i18n_locale_service.message.de_de_2'), 'ru': _(
        'i18n_locale_service.message.ru_ru_2')}
    CURRENCY_MAPPINGS = {_('i18n_locale_service.message.en_us_6'): 'USD', _
        ('i18n_locale_service.message.tr_tr_2'): 'TRY', _(
        'i18n_locale_service.message.ar_sa_2'): 'SAR', _(
        'i18n_locale_service.message.es_es_2'): 'EUR', _(
        'i18n_locale_service.message.fr_fr_2'): 'EUR', _(
        'i18n_locale_service.message.de_de_2'): 'EUR', _(
        'i18n_locale_service.message.ru_ru_2'): 'RUB'}
    TIMEZONE_MAPPINGS = {_('i18n_locale_service.message.en_us_6'): _(
        'i18n_locale_service.label.america_new_york'), _(
        'i18n_locale_service.message.tr_tr_2'): _(
        'i18n_locale_service.label.europe_istanbul'), _(
        'i18n_locale_service.message.ar_sa_2'): _(
        'i18n_locale_service.label.asia_riyadh'), _(
        'i18n_locale_service.message.es_es_2'): _(
        'i18n_locale_service.label.europe_madrid'), _(
        'i18n_locale_service.message.fr_fr_2'): _(
        'i18n_locale_service.label.europe_paris'), _(
        'i18n_locale_service.message.de_de_2'): _(
        'i18n_locale_service.label.europe_berlin'), _(
        'i18n_locale_service.message.ru_ru_2'): _(
        'i18n_locale_service.label.europe_moscow')}

    def __init__(self):
        _('i18n_locale_service.label.initialize_locale_service')
        self.language_service = LanguageDetectionService()
        self._locale_cache = {}

    def get_locale(self, language_code: str) ->Optional[Locale]:
        _('i18n_locale_service.message.get_babel_locale_obje')
        try:
            language_code = self.language_service.normalize_language_code(
                language_code)
            if language_code in self._locale_cache:
                return self._locale_cache[language_code]
            locale_code = self.LOCALE_MAPPINGS.get(language_code, _(
                'i18n_locale_service.message.en_us_6'))
            try:
                babel_locale = Locale.parse(locale_code)
                self._locale_cache[language_code] = babel_locale
                return babel_locale
            except UnknownLocaleError:
                fallback_locale = Locale.parse(_(
                    'i18n_locale_service.message.en_us_6'))
                self._locale_cache[language_code] = fallback_locale
                return fallback_locale
        except Exception as e:
            logger.error(f'Error getting locale for {language_code}: {e}')
            return None

    def format_date(self, date_obj: date, language_code: str, format_type:
        str='medium') ->str:
        _('i18n_locale_service.validation.format_date_according')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return date_obj.strftime(_(
                    'analytics_predictive_analytics.message.y_m_d'))
            return dates.format_date(date_obj, format=format_type, locale=
                babel_locale)
        except Exception as e:
            logger.error(f'Error formatting date: {e}')
            return date_obj.strftime(_(
                'analytics_predictive_analytics.message.y_m_d'))

    def format_datetime(self, datetime_obj: datetime, language_code: str,
        format_type: str='medium') ->str:
        _('i18n_locale_service.validation.format_datetime_accor')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return datetime_obj.strftime(_(
                    'analytics_report_generator.message.y_m_d_h_m_s_1'))
            return dates.format_datetime(datetime_obj, format=format_type,
                locale=babel_locale)
        except Exception as e:
            logger.error(f'Error formatting datetime: {e}')
            return datetime_obj.strftime(_(
                'analytics_report_generator.message.y_m_d_h_m_s_1'))

    def format_time(self, time_obj: time, language_code: str, format_type:
        str='medium') ->str:
        _('i18n_locale_service.validation.format_time_according')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return time_obj.strftime(_(
                    'i18n_locale_service.message.h_m_s_1'))
            return dates.format_time(time_obj, format=format_type, locale=
                babel_locale)
        except Exception as e:
            logger.error(f'Error formatting time: {e}')
            return time_obj.strftime(_('i18n_locale_service.message.h_m_s_1'))

    def format_currency(self, amount: float, language_code: str,
        currency_code: Optional[str]=None) ->str:
        _('i18n_locale_service.validation.format_currency_amoun')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return f'{amount:.2f}'
            if not currency_code:
                locale_code = self.LOCALE_MAPPINGS.get(language_code, _(
                    'i18n_locale_service.message.en_us_6'))
                currency_code = self.CURRENCY_MAPPINGS.get(locale_code, 'USD')
            return numbers.format_currency(amount, currency_code, locale=
                babel_locale)
        except Exception as e:
            logger.error(f'Error formatting currency: {e}')
            return f"{amount:.2f} {currency_code or 'USD'}"

    def format_number(self, number: float, language_code: str,
        decimal_places: Optional[int]=None) ->str:
        _('i18n_locale_service.validation.format_number_accordi')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                if decimal_places is not None:
                    return f'{number:.{decimal_places}f}'
                return str(number)
            if decimal_places is not None:
                format_pattern = f"#,##0.{'0' * decimal_places}"
                return numbers.format_decimal(number, format=format_pattern,
                    locale=babel_locale)
            return numbers.format_decimal(number, locale=babel_locale)
        except Exception as e:
            logger.error(f'Error formatting number: {e}')
            return str(number)

    def format_percent(self, number: float, language_code: str,
        decimal_places: int=1) ->str:
        _('i18n_locale_service.validation.format_percentage_acc')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return f'{number * 100:.{decimal_places}f}%'
            format_pattern = f"#,##0.{'0' * decimal_places}%"
            return numbers.format_percent(number, format=format_pattern,
                locale=babel_locale)
        except Exception as e:
            logger.error(f'Error formatting percent: {e}')
            return f'{number * 100:.{decimal_places}f}%'

    def get_relative_time(self, datetime_obj: datetime, language_code: str,
        base_datetime: Optional[datetime]=None) ->str:
        _('i18n_locale_service.message.get_relative_time_des')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return str(datetime_obj)
            if base_datetime is None:
                base_datetime = datetime.now()
            return dates.format_timedelta(datetime_obj - base_datetime,
                granularity='second', locale=babel_locale)
        except Exception as e:
            logger.error(f'Error formatting relative time: {e}')
            return str(datetime_obj)

    def get_weekday_names(self, language_code: str, width: str='wide') ->List[
        str]:
        _('i18n_locale_service.message.get_weekday_names_for')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return [_('i18n_locale_service.label.monday_2'), _(
                    'i18n_locale_service.label.tuesday_2'), _(
                    'i18n_locale_service.label.wednesday_2'), _(
                    'i18n_locale_service.label.thursday_2'), _(
                    'i18n_locale_service.label.friday_2'), _(
                    'i18n_locale_service.label.saturday_2'), _(
                    'i18n_locale_service.label.sunday_2')]
            weekdays = []
            for i in range(7):
                weekday_name = babel_locale.days[width][i]
                weekdays.append(weekday_name)
            return weekdays
        except Exception as e:
            logger.error(f'Error getting weekday names: {e}')
            return [_('i18n_locale_service.label.monday_2'), _(
                'i18n_locale_service.label.tuesday_2'), _(
                'i18n_locale_service.label.wednesday_2'), _(
                'i18n_locale_service.label.thursday_2'), _(
                'i18n_locale_service.label.friday_2'), _(
                'i18n_locale_service.label.saturday_2'), _(
                'i18n_locale_service.label.sunday_2')]

    def get_month_names(self, language_code: str, width: str='wide') ->List[str
        ]:
        _('i18n_locale_service.message.get_month_names_for_a')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return [_('i18n_locale_service.label.january_2'), _(
                    'i18n_locale_service.label.february_2'), _(
                    'i18n_locale_service.label.march_2'), _(
                    'i18n_locale_service.label.april_2'), _(
                    'i18n_locale_service.label.may_3'), _(
                    'i18n_locale_service.label.june_2'), _(
                    'i18n_locale_service.label.july_2'), _(
                    'i18n_locale_service.label.august_2'), _(
                    'i18n_locale_service.label.september_2'), _(
                    'i18n_locale_service.label.october_2'), _(
                    'i18n_locale_service.label.november_2'), _(
                    'i18n_locale_service.label.december_2')]
            months = []
            for i in range(1, 13):
                month_name = babel_locale.months[width][i]
                months.append(month_name)
            return months
        except Exception as e:
            logger.error(f'Error getting month names: {e}')
            return [_('i18n_locale_service.label.january_2'), _(
                'i18n_locale_service.label.february_2'), _(
                'i18n_locale_service.label.march_2'), _(
                'i18n_locale_service.label.april_2'), _(
                'i18n_locale_service.label.may_3'), _(
                'i18n_locale_service.label.june_2'), _(
                'i18n_locale_service.label.july_2'), _(
                'i18n_locale_service.label.august_2'), _(
                'i18n_locale_service.label.september_2'), _(
                'i18n_locale_service.label.october_2'), _(
                'i18n_locale_service.label.november_2'), _(
                'i18n_locale_service.label.december_2')]

    def get_locale_info(self, language_code: str) ->Dict[str, Any]:
        _('i18n_locale_service.validation.get_comprehensive_loc')
        try:
            babel_locale = self.get_locale(language_code)
            language_info = self.language_service.get_language_info(
                language_code)
            if not babel_locale:
                return language_info
            locale_code = self.LOCALE_MAPPINGS.get(language_code, _(
                'i18n_locale_service.message.en_us_6'))
            return {**language_info, 'locale_code': locale_code,
                'display_name': babel_locale.display_name, 'english_name':
                babel_locale.english_name, 'currency': self.
                CURRENCY_MAPPINGS.get(locale_code, 'USD'), 'timezone': self
                .TIMEZONE_MAPPINGS.get(locale_code, 'UTC'),
                'number_symbols': {'decimal': babel_locale.number_symbols.
                get('decimal', '.'), 'group': babel_locale.number_symbols.
                get('group', ','), 'percent': babel_locale.number_symbols.
                get(_('i18n_locale_service.message.percentsign'), '%')},
                'date_formats': {'short': babel_locale.date_formats['short'
                ].pattern, 'medium': babel_locale.date_formats['medium'].
                pattern, 'long': babel_locale.date_formats['long'].pattern,
                'full': babel_locale.date_formats['full'].pattern},
                'time_formats': {'short': babel_locale.time_formats['short'
                ].pattern, 'medium': babel_locale.time_formats['medium'].
                pattern, 'long': babel_locale.time_formats['long'].pattern,
                'full': babel_locale.time_formats['full'].pattern}}
        except Exception as e:
            logger.error(f'Error getting locale info: {e}')
            return self.language_service.get_language_info(language_code)

    def get_first_day_of_week(self, language_code: str) ->int:
        _('i18n_locale_service.message.get_first_day_of_week')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return 0
            return babel_locale.first_week_day
        except Exception as e:
            logger.error(f'Error getting first day of week: {e}')
            return 0

    def parse_date(self, date_string: str, language_code: str, format_type:
        str='medium') ->Optional[date]:
        _('i18n_locale_service.validation.parse_date_string_acc')
        try:
            babel_locale = self.get_locale(language_code)
            if not babel_locale:
                return datetime.strptime(date_string, _(
                    'analytics_predictive_analytics.message.y_m_d')).date()
            parsed_datetime = dates.parse_date(date_string, locale=babel_locale
                )
            return parsed_datetime
        except Exception as e:
            logger.error(f'Error parsing date: {e}')
            common_formats = [_(
                'analytics_predictive_analytics.message.y_m_d'), _(
                'i18n_locale_service.message.d_m_y'), _(
                'i18n_locale_service.message.m_d_y'), _(
                'i18n_locale_service.message.d_m_y_1')]
            for fmt in common_formats:
                try:
                    return datetime.strptime(date_string, fmt).date()
                except ValueError:
                    continue
            return None

    def get_calendar_data(self, language_code: str) ->Dict[str, Any]:
        _('i18n_locale_service.message.get_calendar_data_for')
        try:
            return {'weekdays': {'narrow': self.get_weekday_names(
                language_code, 'narrow'), 'abbreviated': self.
                get_weekday_names(language_code, 'abbreviated'), 'wide':
                self.get_weekday_names(language_code, 'wide')}, 'months': {
                'narrow': self.get_month_names(language_code, 'narrow'),
                'abbreviated': self.get_month_names(language_code,
                'abbreviated'), 'wide': self.get_month_names(language_code,
                'wide')}, 'first_day_of_week': self.get_first_day_of_week(
                language_code), 'is_rtl': self.language_service.
                is_rtl_language(language_code)}
        except Exception as e:
            logger.error(f'Error getting calendar data: {e}')
            return {'weekdays': {'narrow': ['M', 'T', 'W', 'T', 'F', 'S',
                'S'], 'abbreviated': [_('i18n_locale_service.label.mon'), _
                ('i18n_locale_service.label.tue'), _(
                'i18n_locale_service.label.wed'), _(
                'i18n_locale_service.label.thu'), _(
                'i18n_locale_service.label.fri'), _(
                'i18n_locale_service.label.sat'), _(
                'i18n_locale_service.label.sun')], 'wide': [_(
                'i18n_locale_service.label.monday_2'), _(
                'i18n_locale_service.label.tuesday_2'), _(
                'i18n_locale_service.label.wednesday_2'), _(
                'i18n_locale_service.label.thursday_2'), _(
                'i18n_locale_service.label.friday_2'), _(
                'i18n_locale_service.label.saturday_2'), _(
                'i18n_locale_service.label.sunday_2')]}, 'months': {
                'narrow': ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O',
                'N', 'D'], 'abbreviated': [_(
                'i18n_locale_service.label.jan'), _(
                'i18n_locale_service.label.feb'), _(
                'i18n_locale_service.label.mar'), _(
                'i18n_locale_service.label.apr'), _(
                'i18n_locale_service.label.may_3'), _(
                'i18n_locale_service.label.jun'), _(
                'i18n_locale_service.label.jul'), _(
                'i18n_locale_service.label.aug'), _(
                'i18n_locale_service.label.sep'), _(
                'i18n_locale_service.label.oct'), _(
                'i18n_locale_service.label.nov'), _(
                'i18n_locale_service.label.dec')], 'wide': [_(
                'i18n_locale_service.label.january_2'), _(
                'i18n_locale_service.label.february_2'), _(
                'i18n_locale_service.label.march_2'), _(
                'i18n_locale_service.label.april_2'), _(
                'i18n_locale_service.label.may_3'), _(
                'i18n_locale_service.label.june_2'), _(
                'i18n_locale_service.label.july_2'), _(
                'i18n_locale_service.label.august_2'), _(
                'i18n_locale_service.label.september_2'), _(
                'i18n_locale_service.label.october_2'), _(
                'i18n_locale_service.label.november_2'), _(
                'i18n_locale_service.label.december_2')]},
                'first_day_of_week': 0, 'is_rtl': False}
