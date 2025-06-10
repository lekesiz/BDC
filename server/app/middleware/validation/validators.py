_('validation_validators.validation.specialized_validators_for_di')
import re
import ipaddress
import mimetypes
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse
import phonenumbers
from email_validator import validate_email as validate_email_lib, EmailNotValidError
from flask_babel import _, lazy_gettext as _l


class BaseValidator:
    _('validation_validators.validation.base_class_for_all_validators')

    def validate(self, value: Any) ->Any:
        _('validation_validators.error.validate_value_should_raise_v')
        raise NotImplementedError

    def is_valid(self, value: Any) ->bool:
        _('validation_validators.validation.check_if_value_is_valid_withou')
        try:
            self.validate(value)
            return True
        except ValueError:
            return False


class EmailValidator(BaseValidator):
    _('validation_validators.validation.email_validation_with_advanced')

    def __init__(self, check_deliverability: bool=False, allowed_domains:
        List[str]=None, blocked_domains: List[str]=None):
        _('validation_validators.validation.initialize_email_vali')
        self.check_deliverability = check_deliverability
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or ['tempmail.com',
            'throwaway.email', 'guerrillamail.com']

    def validate(self, email: str) ->str:
        _('validation_validators.validation.validate_email_address')
        if not email or not isinstance(email, str):
            raise ValueError(_(
                'validation_validators.validation.email_address_is_required'))
        try:
            validation = validate_email_lib(email, check_deliverability=
                self.check_deliverability)
            normalized_email = validation.email
        except EmailNotValidError as e:
            raise ValueError(str(e))
        domain = normalized_email.split('@')[1].lower()
        if self.allowed_domains and domain not in self.allowed_domains:
            raise ValueError(f"Email domain '{domain}' is not allowed")
        if domain in self.blocked_domains:
            raise ValueError(f"Email domain '{domain}' is not allowed")
        local_part = normalized_email.split('@')[0]
        if re.search(_('validation_validators.message.test_temp_fake_dummy'
            ), local_part, re.IGNORECASE):
            raise ValueError(_(
                'validation_validators.message.email_appears_to_be_temporary'))
        return normalized_email


class PasswordValidator(BaseValidator):
    _('validation_validators.validation.password_validation_with_confi')

    def __init__(self, min_length: int=12, max_length: int=128,
        require_uppercase: bool=True, require_lowercase: bool=True,
        require_digits: bool=True, require_special: bool=True,
        special_chars: str=_('security_security_config.message.'),
        check_common: bool=True):
        _('validation_validators.validation.initialize_password_validator')
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.special_chars = special_chars
        self.check_common = check_common
        self.common_passwords = {'password', '12345678', '123456789',
            'qwerty', _('orchestration_examples.message.abc123'), _(
            'security_password_policy.message.password123'), 'admin',
            'letmein', 'welcome', 'monkey', '1234567890', _(
            'security_password_policy.message.password1'), '123123',
            'dragon', 'iloveyou'}

    def validate(self, password: str) ->str:
        _('validation_validators.validation.validate_password_against_secu')
        if not password or not isinstance(password, str):
            raise ValueError(_(
                'core_user_service_example.validation.password_is_required'))
        if len(password) < self.min_length:
            raise ValueError(
                f'Password must be at least {self.min_length} characters long')
        if len(password) > self.max_length:
            raise ValueError(
                f'Password must not exceed {self.max_length} characters')
        if self.require_uppercase and not re.search(_(
            'security_input_validator.message.a_z'), password):
            raise ValueError(_(
                'security_input_validator.validation.password_must_contain_at_least'
                ))
        if self.require_lowercase and not re.search(_(
            'security_input_validator.message.a_z_1'), password):
            raise ValueError(_(
                'security_input_validator.validation.password_must_contain_at_least_1'
                ))
        if self.require_digits and not re.search('\\d', password):
            raise ValueError(_(
                'security_input_validator.validation.password_must_contain_at_least_2'
                ))
        if self.require_special and not re.search(
            f'[{re.escape(self.special_chars)}]', password):
            raise ValueError(_(
                'security_input_validator.validation.password_must_contain_at_least_3'
                ))
        if re.search(_('security_input_validator.message.1_2'), password):
            raise ValueError(_(
                'security_input_validator.error.password_cannot_contain_three')
                )
        if re.search(_(
            'validation_validators.message.012_123_234_345_456_567_678_7'),
            password):
            raise ValueError(_(
                'security_input_validator.error.password_cannot_contain_sequen'
                ))
        if re.search(_(
            'security_input_validator.message.abc_bcd_cde_def_efg_fgh_ghi_h'
            ), password.lower()):
            raise ValueError(_(
                'security_input_validator.error.password_cannot_contain_sequen_1'
                ))
        if self.check_common and password.lower() in self.common_passwords:
            raise ValueError(_(
                'validation_validators.message.password_is_too_common_please'))
        if re.search(_(
            'validation_validators.message.password_admin_user_login'),
            password, re.IGNORECASE):
            raise ValueError(_(
                'validation_validators.error.password_cannot_contain_common'))
        return password

    def get_strength(self, password: str) ->Dict[str, Any]:
        _('validation_validators.message.calculate_password_strength_sc')
        score = 0
        feedback = []
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if re.search(_('security_input_validator.message.a_z_1'), password):
            score += 1
        if re.search(_('security_input_validator.message.a_z'), password):
            score += 1
        if re.search('\\d', password):
            score += 1
        if re.search(f'[{re.escape(self.special_chars)}]', password):
            score += 1
        unique_chars = len(set(password))
        if unique_chars >= 10:
            score += 1
        if unique_chars >= 15:
            score += 1
        if score <= 3:
            strength = 'weak'
            feedback.append(_(
                'validation_validators.message.consider_using_a_longer_passwo')
                )
        elif score <= 6:
            strength = 'medium'
            feedback.append(_(
                'validation_validators.message.good_password_but_could_be_st'))
        elif score <= 8:
            strength = 'strong'
            feedback.append(_('validation_validators.label.strong_password'))
        else:
            strength = 'very_strong'
            feedback.append(_(
                'validation_validators.label.excellent_password_strength'))
        return {'score': score, 'strength': strength, 'feedback': feedback}


class URLValidator(BaseValidator):
    _('validation_validators.validation.url_validation_with_security_c')

    def __init__(self, allowed_schemes: List[str]=None, allowed_domains:
        List[str]=None, blocked_domains: List[str]=None, require_tld: bool=True
        ):
        _('validation_validators.validation.initialize_url_validator')
        self.allowed_schemes = allowed_schemes or ['http', 'https']
        self.allowed_domains = allowed_domains or []
        self.blocked_domains = blocked_domains or []
        self.require_tld = require_tld

    def validate(self, url: str) ->str:
        _('validation_validators.validation.validate_url')
        if not url or not isinstance(url, str):
            raise ValueError(_(
                'validation_validators.validation.url_is_required'))
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValueError(_(
                'utils_content_processing.error.invalid_url_format'))
        if not parsed.scheme:
            raise ValueError(_(
                'validation_validators.validation.url_must_include_a_scheme_e_g'
                ))
        if parsed.scheme not in self.allowed_schemes:
            raise ValueError(
                f"URL scheme must be one of: {', '.join(self.allowed_schemes)}"
                )
        if not parsed.netloc:
            raise ValueError(_(
                'validation_validators.validation.url_must_include_a_domain'))
        domain = parsed.netloc.lower()
        if ':' in domain:
            domain = domain.split(':')[0]
        try:
            ipaddress.ip_address(domain)
            raise ValueError(_(
                'validation_validators.message.ip_addresses_are_not_allowed_i')
                )
        except ValueError:
            pass
        if self.require_tld and '.' not in domain:
            raise ValueError(_(
                'validation_validators.validation.url_must_include_a_valid_top_l'
                ))
        if self.allowed_domains and domain not in self.allowed_domains:
            raise ValueError(f"Domain '{domain}' is not allowed")
        if domain in self.blocked_domains:
            raise ValueError(f"Domain '{domain}' is blocked")
        if re.search(_('validation_validators.message._1'), url):
            raise ValueError(_(
                'validation_validators.error.url_contains_invalid_character'))
        if re.search(_(
            'validation_validators.message.javascript_data_vbscript'), url,
            re.IGNORECASE):
            raise ValueError(_(
                'validation_validators.message.url_contains_potentially_dange')
                )
        return url


class FileValidator(BaseValidator):
    _('validation_validators.validation.file_upload_validation')

    def __init__(self, allowed_extensions: List[str]=None,
        allowed_mimetypes: List[str]=None, max_size: int=10 * 1024 * 1024,
        check_content: bool=True):
        _('validation_validators.validation.initialize_file_validator')
        self.allowed_extensions = allowed_extensions or ['pdf', 'doc',
            'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'jpg',
            'jpeg', 'png', 'gif', 'bmp']
        self.allowed_mimetypes = allowed_mimetypes or ['application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            , 'text/plain', 'text/csv', _(
            'file_upload_tests_example.message.image_jpeg'), _(
            'file_upload_tests_example.message.image_png'), _(
            'file_upload_config.message.image_gif')]
        self.max_size = max_size
        self.check_content = check_content
        self.dangerous_signatures = {b'MZ': _(
            'validation_validators.label.windows_executable'), b'\x7fELF':
            _('validation_validators.label.linux_executable'), b'#!/': _(
            'validation_validators.label.shell_script'), b'<?php': _(
            'validation_validators.label.php_script'), b'<%': _(
            'validation_validators.label.server_side_script')}

    def validate(self, file_obj: Any) ->Dict[str, Any]:
        _('validation_validators.validation.validate_file_upload')
        if not file_obj:
            raise ValueError(_(
                'file_upload_api_example.label.no_file_provided_1'))
        filename = getattr(file_obj, 'filename', None)
        if not filename:
            raise ValueError(_(
                'validation_schemas.validation.file_must_have_a_filename'))
        extension = self._get_extension(filename)
        if extension not in self.allowed_extensions:
            raise ValueError(f"File type '.{extension}' is not allowed")
        mimetype = getattr(file_obj, 'content_type', None
            ) or mimetypes.guess_type(filename)[0]
        if mimetype and mimetype not in self.allowed_mimetypes:
            raise ValueError(f"MIME type '{mimetype}' is not allowed")
        file_obj.seek(0, 2)
        size = file_obj.tell()
        file_obj.seek(0)
        if size > self.max_size:
            raise ValueError(
                f'File size exceeds maximum allowed size of {self.max_size / 1024 / 1024:.1f}MB'
                )
        if self.check_content:
            content = file_obj.read(1024)
            file_obj.seek(0)
            for signature, description in self.dangerous_signatures.items():
                if content.startswith(signature):
                    raise ValueError(
                        f'File appears to be {description}, which is not allowed'
                        )
        return {'filename': filename, 'extension': extension, 'mimetype':
            mimetype, 'size': size}

    def _get_extension(self, filename: str) ->str:
        _('utils_file_upload_security.message.get_file_extension_safely')
        if '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[1].lower()


class JSONValidator(BaseValidator):
    _('validation_validators.validation.json_data_validation')

    def __init__(self, max_depth: int=10, max_size: int=1024 * 1024):
        _('validation_validators.validation.initialize_json_validator')
        self.max_depth = max_depth
        self.max_size = max_size

    def validate(self, data: Any, current_depth: int=0) ->Any:
        _('validation_validators.validation.validate_json_data_structure')
        if current_depth > self.max_depth:
            raise ValueError(
                f'JSON structure exceeds maximum depth of {self.max_depth}')
        if isinstance(data, dict):
            if len(str(data)) > self.max_size:
                raise ValueError(
                    f'JSON data exceeds maximum size of {self.max_size} bytes')
            for key, value in data.items():
                if not isinstance(key, str):
                    raise ValueError(_(
                        'validation_validators.validation.json_keys_must_be_strings'
                        ))
                if len(key) > 255:
                    raise ValueError(_(
                        'validation_validators.message.json_key_too_long'))
                self.validate(value, current_depth + 1)
        elif isinstance(data, list):
            if len(data) > 10000:
                raise ValueError(_(
                    'validation_validators.message.json_array_too_large'))
            for item in data:
                self.validate(item, current_depth + 1)
        elif isinstance(data, str):
            if len(data) > 100000:
                raise ValueError(_(
                    'validation_validators.message.json_string_value_too_long')
                    )
        elif not isinstance(data, (int, float, bool)) and data is not None:
            raise ValueError(f'Invalid JSON data type: {type(data).__name__}')
        return data


class SQLValidator(BaseValidator):
    _('validation_validators.validation.sql_injection_prevention_valid')
    SQL_PATTERNS = [
        '\\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|FROM|WHERE)\\b'
        , _('validation_validators.message._2'), _(
        'validation_validators.message.bor_b_bor_b_band_b'), _(
        'validation_validators.message.s_or_s_s_or_s'), _(
        'validation_validators.message._3'), _(
        'validation_validators.message.xp_sp'), _(
        'validation_validators.message.0x_0_9a_fa_f'), _(
        'validation_validators.message.char_concat_chr'), _(
        'validation_validators.message._4'), _(
        'validation_validators.message.waitfor_delay_benchmark'), _(
        'validation_validators.message.into_s_outfile_dumpfile')]

    def validate(self, value: str) ->str:
        _('validation_validators.validation.validate_input_for_sql_injecti')
        if not isinstance(value, str):
            return str(value)
        for pattern in self.SQL_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(_(
                    'validation_validators.message.input_contains_potentially_dan'
                    ))
        if self._contains_encoded_sql(value):
            raise ValueError(_(
                'validation_validators.message.input_contains_encoded_sql_inj')
                )
        return value

    def _contains_encoded_sql(self, value: str) ->bool:
        _('validation_validators.message.check_for_encoded_sql_injectio')
        import urllib.parse
        decoded = urllib.parse.unquote(value)
        if decoded != value:
            for pattern in self.SQL_PATTERNS:
                if re.search(pattern, decoded, re.IGNORECASE):
                    return True
        if re.match(_('validation_validators.message.a_za_z0_9'), value
            ) and len(value) % 4 == 0:
            try:
                import base64
                decoded = base64.b64decode(value).decode('utf-8', errors=
                    'ignore')
                for pattern in self.SQL_PATTERNS:
                    if re.search(pattern, decoded, re.IGNORECASE):
                        return True
            except:
                pass
        return False


class PhoneValidator(BaseValidator):
    _('validation_validators.validation.phone_number_validation')

    def __init__(self, default_region: str='US', allowed_regions: List[str]
        =None):
        _('validation_validators.validation.initialize_phone_validator')
        self.default_region = default_region
        self.allowed_regions = allowed_regions

    def validate(self, phone_number: str) ->str:
        _('validation_validators.validation.validate_phone_number')
        if not phone_number:
            raise ValueError(_('api_sms.validation.phone_number_is_required'))
        try:
            parsed = phonenumbers.parse(phone_number, self.default_region)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError(_(
                    'services_sms_service.error.invalid_phone_number'))
            if self.allowed_regions:
                region = phonenumbers.region_code_for_number(parsed)
                if region not in self.allowed_regions:
                    raise ValueError(
                        f'Phone numbers from {region} are not allowed')
            return phonenumbers.format_number(parsed, phonenumbers.
                PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError(_(
                'validation_validators.error.invalid_phone_number_format'))


class DateValidator(BaseValidator):
    _('validation_validators.validation.date_and_datetime_validation')

    def __init__(self, min_date: date=None, max_date: date=None,
        allow_future: bool=True, allow_past: bool=True):
        _('validation_validators.validation.initialize_date_validator')
        self.min_date = min_date
        self.max_date = max_date
        self.allow_future = allow_future
        self.allow_past = allow_past

    def validate(self, value: Any) ->date:
        _('validation_validators.validation.validate_date')
        if isinstance(value, datetime):
            date_value = value.date()
        elif isinstance(value, date):
            date_value = value
        elif isinstance(value, str):
            for fmt in [_('analytics_predictive_analytics.message.y_m_d'),
                _('i18n_locale_service.message.d_m_y'), _(
                'i18n_locale_service.message.m_d_y'), _(
                'validation_validators.message.y_m_d_1')]:
                try:
                    date_value = datetime.strptime(value, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(_(
                    'services_appointment_service.error.invalid_date_format'))
        else:
            raise ValueError(_('validation_validators.error.invalid_date_type')
                )
        if self.min_date and date_value < self.min_date:
            raise ValueError(f'Date must be after {self.min_date}')
        if self.max_date and date_value > self.max_date:
            raise ValueError(f'Date must be before {self.max_date}')
        today = date.today()
        if not self.allow_future and date_value > today:
            raise ValueError(_(
                'validation_validators.message.future_dates_are_not_allowed'))
        if not self.allow_past and date_value < today:
            raise ValueError(_(
                'validation_validators.message.past_dates_are_not_allowed'))
        return date_value


class CreditCardValidator(BaseValidator):
    _('validation_validators.validation.credit_card_number_validation')

    def validate(self, card_number: str) ->str:
        _('validation_validators.validation.validate_credit_card_number_us')
        if not card_number:
            raise ValueError(_(
                'validation_validators.validation.credit_card_number_is_required'
                ))
        card_number = re.sub(_('validation_validators.message.s'), '',
            card_number)
        if not card_number.isdigit():
            raise ValueError(_(
                'validation_validators.validation.credit_card_number_must_contai'
                ))
        if len(card_number) < 13 or len(card_number) > 19:
            raise ValueError(_(
                'validation_validators.error.invalid_credit_card_number_len'))

        def luhn_check(number):
            digits = [int(d) for d in number]
            checksum = 0
            for i in range(len(digits) - 2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            return sum(digits) % 10 == 0
        if not luhn_check(card_number):
            raise ValueError(_(
                'validation_validators.error.invalid_credit_card_number'))
        masked = '*' * (len(card_number) - 4) + card_number[-4:]
        return masked
