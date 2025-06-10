_('error_handling_examples.error.usage_examples_for_the_error')
import time
import random
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from .error_manager import error_manager, ErrorCategory, ErrorSeverity
from .circuit_breaker import circuit_breaker, CircuitBreaker, CircuitBreakerConfig
from .retry_manager import retry, RetryConfig, BackoffStrategy
from .error_monitor import error_monitor, AlertRule, AlertLevel, AlertChannel
from .user_messages import error_message_mapper, UserMessage, MessageType
from .error_recovery import with_recovery, with_fallback, error_recovery
from .middleware import ErrorHandlingMiddleware
from .config import config_manager
from .exceptions import *
logging.basicConfig(level=logging.INFO)
from flask_babel import _, lazy_gettext as _l
logger = logging.getLogger(__name__)


def example_basic_error_handling():
    _('error_handling_examples.error.example_of_basic_error_handlin')
    print(_('error_handling_examples.error.basic_error_handling_exam'))

    def risky_operation(fail_probability=0.3):
        _('error_handling_examples.error.simulates_an_operation_that_mi')
        if random.random() < fail_probability:
            raise ValueError(_(
                'error_handling_examples.error.simulated_failure_in_risky_ope')
                )
        return {'status': 'success', 'data': _(
            'error_handling_examples.success.operation_completed')}
    try:
        result = risky_operation()
        print(f'Operation succeeded: {result}')
    except Exception as e:
        error_context = error_manager.handle_error(e, context={'operation':
            'risky_operation', 'parameters': {'fail_probability': 0.3}},
            user_id=_('error_handling_examples.message.user_123'),
            request_id=_('error_handling_examples.message.req_456'))
        print(f'Error handled - ID: {error_context.error_id}')
        print(f'Category: {error_context.category.value}')
        print(f'Severity: {error_context.severity.value}')
        user_message = error_message_mapper.map_exception_to_message(e, 'en')
        print(f'User message: {user_message.message}')


class ExternalPaymentService:
    _('error_handling_examples.error.mock_external_payment_service')

    def __init__(self, failure_rate=0.4):
        self.failure_rate = failure_rate
        self.call_count = 0

    def process_payment(self, amount: float, currency: str='USD') ->Dict[
        str, Any]:
        _('error_handling_examples.error.simulates_payment_processing_t')
        self.call_count += 1
        if random.random() < self.failure_rate:
            raise ConnectionError(
                f'Payment service unavailable (call #{self.call_count})')
        return {'transaction_id': f'txn_{self.call_count}', 'amount':
            amount, 'currency': currency, 'status': 'completed'}


def example_circuit_breaker():
    _('error_handling_examples.message.example_of_using_circuit_break')
    print(_('error_handling_examples.message.circuit_breaker_example'))
    payment_service = ExternalPaymentService(failure_rate=0.6)

    @circuit_breaker(name='payment_service', failure_threshold=3,
        recovery_timeout=5, success_threshold=2)
    def make_payment(amount, currency='USD'):
        return payment_service.process_payment(amount, currency)
    for i in range(10):
        try:
            result = make_payment(100.0)
            print(f"Payment {i + 1} succeeded: {result['transaction_id']}")
        except CircuitBreakerError as e:
            print(f'Payment {i + 1} blocked by circuit breaker: {e.message}')
        except Exception as e:
            print(f'Payment {i + 1} failed: {e}')
        time.sleep(0.5)
    from .circuit_breaker import circuit_breaker_manager
    stats = circuit_breaker_manager.get_breaker('payment_service').get_stats()
    print(f'\nCircuit Breaker Stats:')
    print(f'State: {stats.state.value}')
    print(f'Total requests: {stats.total_requests}')
    print(f'Failed requests: {stats.failed_requests}')
    print(
        f'Success rate: {stats.successful_requests / stats.total_requests * 100:.1f}%'
        )


class UnstableDatabase:
    _('error_handling_examples.error.mock_database_service_with_int')

    def __init__(self):
        self.query_count = 0
        self.failure_pattern = [True, True, False, True, False, False]

    def query_user(self, user_id: int) ->Dict[str, Any]:
        _('error_handling_examples.error.simulates_database_query_that')
        self.query_count += 1
        pattern_index = (self.query_count - 1) % len(self.failure_pattern)
        if self.failure_pattern[pattern_index]:
            raise ConnectionError(
                f'Database connection timeout (query #{self.query_count})')
        return {'id': user_id, 'name': f'User {user_id}', 'email':
            f'user{user_id}@example.com', 'query_count': self.query_count}


def example_retry_mechanisms():
    _('error_handling_examples.message.example_of_different_retry_str')
    print(_('error_handling_examples.message.retry_mechanisms_example'))
    db = UnstableDatabase()

    @retry(max_attempts=5, base_delay=0.5, backoff_strategy=BackoffStrategy
        .EXPONENTIAL, retryable_exceptions=(ConnectionError,))
    def get_user_with_exponential_backoff(user_id):
        print(f'  Attempting to query user {user_id}...')
        return db.query_user(user_id)

    @retry(max_attempts=4, base_delay=0.3, backoff_strategy=BackoffStrategy
        .LINEAR, retryable_exceptions=(ConnectionError,))
    def get_user_with_linear_backoff(user_id):
        print(f'  Attempting to query user {user_id}...')
        return db.query_user(user_id)
    print(_('error_handling_examples.message.testing_exponential_backoff'))
    try:
        user = get_user_with_exponential_backoff(123)
        print(f'Success: {user}')
    except RetryExhaustedError as e:
        print(f'All retries failed: {e}')
    db.query_count = 0
    print(_('error_handling_examples.message.testing_linear_backoff'))
    try:
        user = get_user_with_linear_backoff(456)
        print(f'Success: {user}')
    except RetryExhaustedError as e:
        print(f'All retries failed: {e}')


def example_error_monitoring():
    _('error_handling_examples.error.example_of_error_monitoring_an')
    print(_('error_handling_examples.error.error_monitoring_example'))

    def critical_database_errors_condition(metrics: Dict[str, Any]) ->bool:
        _('error_handling_examples.error.alert_when_database_errors_exc')
        db_errors = metrics.get('errors_by_category', {}).get('database', 0)
        return db_errors >= 3
    alert_rule = AlertRule(name='critical_database_errors', description=_(
        'error_handling_examples.error.high_number_of_database_errors'),
        condition=critical_database_errors_condition, level=AlertLevel.
        CRITICAL, channels=[AlertChannel.LOG], cooldown_minutes=1)
    error_monitor.add_alert_rule(alert_rule)
    from ..exceptions import ExternalServiceException
    print(_('error_handling_examples.error.simulating_database_errors'))
    for i in range(5):
        try:
            if i % 2 == 0:
                raise ConnectionError(f'Database connection failed #{i + 1}')
            else:
                raise TimeoutError(f'Database query timeout #{i + 1}')
        except Exception as e:
            error_context = error_manager.handle_error(e, context={
                'operation': 'database_query', 'query_id': f'q_{i + 1}'})
            error_monitor.record_error(error_context)
    metrics = error_monitor.get_current_metrics()
    print(f'\nCurrent metrics:')
    print(f"Total errors: {metrics['total_errors']}")
    print(f"Error rate: {metrics['error_rate_per_minute']:.2f}/min")
    print(f"Errors by category: {metrics['errors_by_category']}")
    alert_history = error_monitor.get_alert_history(hours=1)
    print(f'\nAlerts triggered: {len(alert_history)}')
    for alert in alert_history:
        print(f"  - {alert['rule_name']}: {alert['message']}")


def example_user_friendly_messages():
    _('error_handling_examples.error.example_of_user_friendly_error')
    print(_('error_handling_examples.message.user_friendly_messages_ex'))
    custom_message_en = UserMessage(code='PAYMENT_DECLINED', message=_(
        'error_handling_examples.message.your_payment_was_declined_by_y'),
        message_type=MessageType.ERROR, suggested_actions=[_(
        'error_handling_examples.message.check_that_your_card_has_suffi'),
        _('error_handling_examples.message.verify_your_card_details_are_c'),
        _('error_handling_examples.message.try_a_different_payment_method'),
        _('error_handling_examples.message.contact_your_bank_if_the_probl')
        ], support_info=_(
        'error_handling_examples.message.if_you_need_help_contact_our'))
    custom_message_es = UserMessage(code='PAYMENT_DECLINED', message=_(
        'error_handling_examples.message.su_pago_fue_rechazado_por_su_b'),
        message_type=MessageType.ERROR, suggested_actions=[_(
        'error_handling_examples.message.verifique_que_su_tarjeta_tenga'),
        _('error_handling_examples.message.verifique_que_los_detalles_de'),
        _('error_handling_examples.message.intente_con_un_m_todo_de_pago'),
        _('error_handling_examples.message.contacte_a_su_banco_si_el_prob')
        ], support_info=_(
        'error_handling_examples.message.si_necesita_ayuda_contacte_a'))
    error_message_mapper.add_message_mapping('en', 'PAYMENT_DECLINED',
        custom_message_en)
    error_message_mapper.add_message_mapping('es', 'PAYMENT_DECLINED',
        custom_message_es)
    test_exceptions = [(ValueError(_(
        'core_user_service_example.error.invalid_email_format')),
        'INVALID_EMAIL'), (PermissionError(_(
        'api_video_conferences.label.access_denied_4')), 'ACCESS_DENIED'),
        (ConnectionError(_('error_handling_examples.error.network_error')),
        'NETWORK_ERROR'), (Exception(_(
        'error_handling_examples.label.payment_declined')), 'PAYMENT_DECLINED')
        ]
    for exception, expected_code in test_exceptions:
        print(f'\nTesting: {type(exception).__name__}')
        en_message = error_message_mapper.map_exception_to_message(exception,
            'en')
        print(f'EN: {en_message.message}')
        if en_message.suggested_actions:
            print(
                f"    Actions: {', '.join(en_message.suggested_actions[:2])}..."
                )
        es_message = error_message_mapper.map_exception_to_message(exception,
            'es')
        print(f'ES: {es_message.message}')
        if es_message.suggested_actions:
            print(
                f"    Acciones: {', '.join(es_message.suggested_actions[:2])}..."
                )


class UserProfileService:
    _('error_handling_examples.error.mock_user_profile_service_that')

    def __init__(self):
        self.call_count = 0
        self.cache = {}

    def get_profile(self, user_id: str) ->Dict[str, Any]:
        _('error_handling_examples.error.get_user_profile_might_fail')
        self.call_count += 1
        if self.call_count <= 2:
            raise ConnectionError(_(
                'error_handling_examples.message.profile_service_temporarily_un'
                ))
        profile = {'id': user_id, 'name': f'User {user_id}', 'avatar':
            f'https://example.com/avatars/{user_id}.jpg', 'preferences': {
            'theme': 'dark', 'language': 'en'}}
        self.cache[user_id] = profile
        return profile

    def get_cached_profile(self, user_id: str) ->Optional[Dict[str, Any]]:
        _('error_handling_examples.message.get_cached_profile_data')
        return self.cache.get(user_id)


def example_error_recovery():
    _('error_handling_examples.error.example_of_error_recovery_stra')
    print(_('error_handling_examples.error.error_recovery_example'))
    profile_service = UserProfileService()

    @with_recovery(cache_key=_(
        'error_handling_examples.message.user_profile_123'))
    def get_user_profile_with_cache(user_id):
        print(f'  Attempting to get profile for user {user_id}')
        return profile_service.get_profile(user_id)

    @with_fallback(fallback_value={'id': 'unknown', 'name': _(
        'error_handling_examples.label.guest_user')})
    def get_user_profile_with_default(user_id):
        print(f'  Attempting to get profile for user {user_id}')
        return profile_service.get_profile(user_id)

    def get_basic_profile(user_id):
        print(f'  Using basic profile fallback for user {user_id}')
        return {'id': user_id, 'name': f'User {user_id}', 'avatar':
            '/default-avatar.png', 'preferences': {'theme': 'light',
            'language': 'en'}}

    @with_fallback(fallback_function=get_basic_profile)
    def get_user_profile_with_function_fallback(user_id):
        print(f'  Attempting to get profile for user {user_id}')
        return profile_service.get_profile(user_id)
    print(_('error_handling_examples.message.testing_fallback_to_default_v'))
    try:
        profile = get_user_profile_with_default('123')
        print(f'Got profile: {profile}')
    except Exception as e:
        print(f'Recovery failed: {e}')
    print(_('error_handling_examples.message.testing_fallback_to_alternati'))
    try:
        profile = get_user_profile_with_function_fallback('456')
        print(f'Got profile: {profile}')
    except Exception as e:
        print(f'Recovery failed: {e}')
    profile_service.call_count = 0
    print(_('error_handling_examples.success.testing_cache_fallback_after'))
    try:
        profile = get_user_profile_with_cache('789')
        print(f'First call succeeded: {profile}')
    except Exception as e:
        print(f'First call failed: {e}')
    profile_service.call_count = 1
    try:
        profile = get_user_profile_with_cache('789')
        print(f'Second call with cache fallback: {profile}')
    except Exception as e:
        print(f'Cache fallback failed: {e}')


async def example_async_error_handling():
    _('error_handling_examples.error.example_of_async_error_handlin')
    print(_('error_handling_examples.error.async_error_handling_exam'))
    call_count = 0

    @retry(max_attempts=3, base_delay=0.5)
    async def async_api_call(endpoint: str):
        nonlocal call_count
        call_count += 1
        print(f'  Async API call #{call_count} to {endpoint}')
        await asyncio.sleep(0.1)
        if call_count <= 2:
            raise ConnectionError(f'API call failed (attempt #{call_count})')
        return {'endpoint': endpoint, 'data': 'success', 'attempt': call_count}
    try:
        result = await async_api_call('/api/data')
        print(f'Async call succeeded: {result}')
    except RetryExhaustedError as e:
        print(f'All async retries failed: {e}')


def example_flask_integration():
    _('error_handling_examples.error.example_of_integrating_error_h')
    print(_('error_handling_examples.message.flask_integration_example'))
    try:
        from flask import Flask, request, jsonify
        app = Flask(__name__)
        config_manager.load_from_dict({'enabled': True, 'middleware': {
            'include_stack_trace': False, 'log_request_data': True},
            'user_messages': {'default_locale': 'en'}})
        error_middleware = ErrorHandlingMiddleware(app, enable_monitoring=
            True, include_stack_trace=False)

        @app.route('/api/test-error')
        def test_error():
            _('error_handling_examples.error.endpoint_that_demonstrates_err')
            error_type = request.args.get('type', 'validation')
            if error_type == 'validation':
                raise ValueError(_(
                    'error_handling_examples.error.invalid_input_parameter'))
            elif error_type == 'auth':
                from ..exceptions import UnauthorizedException
                raise UnauthorizedException(_(
                    'core_decorators.validation.authentication_required'))
            elif error_type == 'not_found':
                from ..exceptions import NotFoundException
                raise NotFoundException(_(
                    'i18n_translation_service.label.resource_not_found'))
            else:
                raise Exception(_(
                    'error_handling_examples.error.unknown_error_type'))

        @app.route('/api/health')
        def health_check():
            _('api_ai_question_generation.label.health_check_endpoint')
            return jsonify({'status': 'healthy', 'error_stats':
                error_monitor.get_current_metrics()})
        print(_('error_handling_examples.error.flask_app_configured_with_erro')
            )
        print(_('error_handling_examples.label.example_endpoints'))
        print(_('error_handling_examples.error.get_api_test_error_type_val'))
        print(_('error_handling_examples.error.get_api_test_error_type_aut'))
        print(_('error_handling_examples.error.get_api_test_error_type_not'))
        print(_('error_handling_examples.message.get_api_health'))
        return app
    except ImportError:
        print(_('error_handling_examples.message.flask_not_available_skipping')
            )
        return None


def example_configuration_management():
    _('error_handling_examples.message.example_of_configuration_manag')
    print(_('error_handling_examples.message.configuration_management'))
    config_manager.load_default_config()
    custom_config = {'circuit_breaker': {'failure_threshold': 10,
        'recovery_timeout': 120}, 'retry': {'max_attempts': 5, 'base_delay':
        2.0}, 'monitoring': {'error_rate_threshold': 20.0},
        'custom_settings': {'feature_flags': {'advanced_recovery': True,
        'detailed_logging': True}}}
    config_manager.load_from_dict(custom_config)
    issues = config_manager.validate_config()
    if issues:
        print(f'Configuration issues found: {issues}')
    else:
        print(_('error_handling_examples.validation.configuration_is_valid'))
    current_config = config_manager.get_config()
    print(f'\nCurrent configuration:')
    print(
        f'Circuit Breaker failure threshold: {current_config.circuit_breaker.failure_threshold}'
        )
    print(f'Retry max attempts: {current_config.retry.max_attempts}')
    print(
        f'Monitoring error rate threshold: {current_config.monitoring.error_rate_threshold}'
        )
    config_json = config_manager.export_config('json')
    print(f'\nConfiguration exported (JSON): {len(config_json)} characters')


def run_all_examples():
    _('error_handling_examples.message.run_all_examples_in_sequence')
    print(_('error_handling_examples.error.running_error_handling_syste'))
    print('=' * 60)
    try:
        example_basic_error_handling()
        example_circuit_breaker()
        example_retry_mechanisms()
        example_error_monitoring()
        example_user_friendly_messages()
        example_error_recovery()
        example_configuration_management()
        print(_('error_handling_examples.message.running_async_example'))
        asyncio.run(example_async_error_handling())
        flask_app = example_flask_integration()
        print('\n' + '=' * 60)
        print(_('error_handling_examples.success.all_examples_completed_succe')
            )
        print(_('error_handling_examples.message.key_takeaways'))
        print(_(
            'error_handling_examples.message.1_use_decorators_for_common_p'))
        print(_(
            'error_handling_examples.message.2_configure_monitoring_and_al'))
        print(_('error_handling_examples.error.3_provide_user_friendly_loca'))
        print(_('error_handling_examples.error.4_implement_appropriate_recov'))
        print(_('error_handling_examples.error.5_use_configuration_managemen'))
    except Exception as e:
        print(f'\n❌ Example execution failed: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_examples()
