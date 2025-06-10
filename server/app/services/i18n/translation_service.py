_('i18n_translation_service.message.translation_service_for_multi')
import json
import logging
import os
from typing import Dict, Optional, Any, List
from pathlib import Path
from dataclasses import dataclass
from app.utils.cache import cache_manager
from app.services.i18n.language_detection_service import LanguageDetectionService
from flask_babel import _, lazy_gettext as _l
logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    _('i18n_translation_service.message.translation_result_with_metada')
    text: str
    language: str
    source: str
    confidence: float = 1.0


class TranslationService:
    _('i18n_translation_service.message.service_for_handling_translati')

    def __init__(self):
        _('i18n_translation_service.label.initialize_translation_service')
        self.language_service = LanguageDetectionService()
        self.translations_cache = {}
        self.translations_dir = Path(__file__).parent.parent.parent / 'locales'
        self.cache_timeout = 3600
        self.translations_dir.mkdir(exist_ok=True)
        self._load_all_translations()

    def _load_all_translations(self):
        _('i18n_translation_service.message.load_all_translation_files_int')
        try:
            for language_code in self.language_service.SUPPORTED_LANGUAGES.keys(
                ):
                self._load_translation_file(language_code)
        except Exception as e:
            logger.error(f'Error loading translations: {e}')

    def _load_translation_file(self, language_code: str) ->Dict[str, Any]:
        _('i18n_translation_service.message.load_translation_file')
        try:
            file_path = self.translations_dir / f'{language_code}.json'
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    self.translations_cache[language_code] = translations
                    return translations
            else:
                self._create_default_translation_file(language_code)
                return self.translations_cache.get(language_code, {})
        except Exception as e:
            logger.error(
                f'Error loading translation file for {language_code}: {e}')
            return {}

    def _create_default_translation_file(self, language_code: str):
        _('i18n_translation_service.message.create_default_transl')
        try:
            default_translations = self._get_default_translations(language_code
                )
            file_path = self.translations_dir / f'{language_code}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_translations, f, ensure_ascii=False, indent=2
                    )
            self.translations_cache[language_code] = default_translations
            logger.info(f'Created default translation file for {language_code}'
                )
        except Exception as e:
            logger.error(
                f'Error creating default translation file for {language_code}: {e}'
                )

    def _get_default_translations(self, language_code: str) ->Dict[str, Any]:
        _('i18n_translation_service.message.get_default_translati')
        base_translations = {'common': {'save': _(
            'i18n_translation_service.label.save'), 'cancel': _(
            'i18n_translation_service.label.cancel'), 'delete': 'Delete',
            'edit': _('i18n_translation_service.label.edit'), 'create': _(
            'i18n_translation_service.label.create'), 'update': 'Update',
            'search': _('i18n_translation_service.label.search'), 'filter':
            _('i18n_translation_service.label.filter'), 'loading': _(
            'i18n_translation_service.label.loading'), 'error': _(
            'i18n_translation_service.error.error_1'), 'success': _(
            'i18n_translation_service.success.success'), 'warning': _(
            'i18n_translation_service.label.warning'), 'info': _(
            'i18n_translation_service.validation.information_2'), 'confirm':
            _('i18n_translation_service.label.confirm'), 'yes': _(
            'i18n_translation_service.label.yes'), 'no': 'No', 'ok': 'OK',
            'submit': _('i18n_translation_service.label.submit'), 'reset':
            _('i18n_translation_service.label.reset'), 'close': _(
            'i18n_translation_service.label.close'), 'back': _(
            'i18n_translation_service.label.back'), 'next': _(
            'i18n_translation_service.label.next'), 'previous': _(
            'i18n_translation_service.label.previous'), 'home': _(
            'i18n_translation_service.label.home'), 'dashboard': _(
            'i18n_translation_service.label.dashboard_1'), 'profile': _(
            'i18n_translation_service.label.profile'), 'settings': _(
            'i18n_translation_service.label.settings'), 'logout': _(
            'i18n_translation_service.label.logout'), 'login': _(
            'i18n_translation_service.label.login'), 'register': _(
            'i18n_translation_service.label.register')}, 'auth': {'email':
            _('i18n_translation_service.label.email'), 'password': _(
            'i18n_translation_service.label.password'), 'confirm_password':
            _('i18n_translation_service.label.confirm_password'),
            'remember_me': _('i18n_translation_service.label.remember_me'),
            'forgot_password': _(
            'i18n_translation_service.label.forgot_password'),
            'reset_password': _(
            'i18n_translation_service.label.reset_password'),
            'login_success': _(
            'i18n_translation_service.success.login_successful'),
            'login_failed': _('i18n_translation_service.error.login_failed'
            ), 'logout_success': _(
            'i18n_translation_service.success.logout_successful'),
            'registration_success': _(
            'i18n_translation_service.success.registration_successful'),
            'invalid_credentials': _(
            'i18n_translation_service.error.invalid_credentials'),
            'password_reset_sent': _(
            'i18n_translation_service.message.password_reset_email_sent'),
            'password_updated': 'Password updated successfully'},
            'navigation': {'beneficiaries': _(
            'i18n_translation_service.label.beneficiaries'), 'programs': _(
            'i18n_translation_service.label.programs'), 'appointments': _(
            'i18n_translation_service.label.appointments'), 'documents': _(
            'i18n_translation_service.label.documents'), 'reports': _(
            'i18n_translation_service.label.reports'), 'calendar': _(
            'i18n_translation_service.label.calendar'), 'messages': _(
            'i18n_translation_service.label.messages'), 'notifications': _(
            'i18n_translation_service.label.notifications'), 'analytics': _
            ('i18n_translation_service.label.analytics'), 'administration':
            _('i18n_translation_service.label.administration'), 'users': _(
            'i18n_translation_service.label.users'), 'tenants': _(
            'i18n_translation_service.label.tenants')}, 'forms': {
            'first_name': _('i18n_translation_service.label.first_name'),
            'last_name': _('i18n_translation_service.label.last_name'),
            'phone': _('i18n_translation_service.label.phone'), 'address':
            _('i18n_translation_service.label.address'), 'city': _(
            'i18n_translation_service.label.city'), 'state': _(
            'i18n_translation_service.label.state'), 'country': _(
            'i18n_translation_service.label.country'), 'zip_code': _(
            'i18n_translation_service.label.zip_code'), 'organization': _(
            'i18n_translation_service.label.organization'), 'bio': _(
            'i18n_translation_service.label.biography'), 'date_of_birth': _
            ('i18n_translation_service.label.date_of_birth'), 'gender': _(
            'i18n_translation_service.label.gender'), 'emergency_contact':
            _('i18n_translation_service.label.emergency_contact'), 'notes':
            _('i18n_translation_service.label.notes'), 'description': _(
            'i18n_translation_service.label.description'), 'title': _(
            'i18n_translation_service.label.title'), 'start_date': _(
            'i18n_translation_service.label.start_date'), 'end_date': _(
            'i18n_translation_service.label.end_date'), 'status': _(
            'i18n_translation_service.label.status')}, 'messages': {
            'no_data': _('i18n_translation_service.label.no_data_available'
            ), 'no_results': _(
            'i18n_translation_service.label.no_results_found'),
            'data_saved': _(
            'i18n_translation_service.success.data_saved_successfully'),
            'data_deleted': 'Data deleted successfully', 'operation_failed':
            _('i18n_translation_service.error.operation_failed'),
            'permission_denied': _(
            'i18n_translation_service.label.permission_denied'),
            'invalid_input': _(
            'i18n_translation_service.error.invalid_input'),
            'required_field': _(
            'i18n_translation_service.validation.this_field_is_required'),
            'invalid_email': _(
            'i18n_translation_service.error.invalid_email_address'),
            'password_too_short': _(
            'i18n_translation_service.message.password_is_too_short'),
            'passwords_dont_match': _(
            'i18n_translation_service.label.passwords_don_t_match'),
            'file_uploaded': _(
            'i18n_translation_service.success.file_uploaded_successfully'),
            'file_too_large': _(
            'i18n_translation_service.message.file_is_too_large'),
            'invalid_file_type': _(
            'i18n_translation_service.error.invalid_file_type')}, 'errors':
            {'network_error': _(
            'i18n_translation_service.error.network_error_occurred'),
            'server_error': _(
            'i18n_translation_service.error.server_error_occurred'),
            'not_found': _(
            'i18n_translation_service.label.resource_not_found'),
            'unauthorized': _(
            'i18n_translation_service.label.unauthorized_access'),
            'forbidden': _(
            'i18n_translation_service.label.access_forbidden'),
            'validation_error': _(
            'i18n_translation_service.error.validation_error'), 'timeout':
            _('i18n_translation_service.label.request_timeout'),
            'unknown_error': _(
            'i18n_translation_service.error.unknown_error_occurred')},
            'date_time': {'today': _('i18n_translation_service.label.today'
            ), 'yesterday': _('i18n_translation_service.label.yesterday'),
            'tomorrow': _('i18n_translation_service.label.tomorrow'),
            'this_week': _('i18n_translation_service.label.this_week'),
            'last_week': _('i18n_translation_service.label.last_week'),
            'next_week': _('i18n_translation_service.label.next_week'),
            'this_month': _('i18n_translation_service.label.this_month'),
            'last_month': _('i18n_translation_service.label.last_month'),
            'next_month': _('i18n_translation_service.label.next_month'),
            'this_year': _('i18n_translation_service.label.this_year'),
            'morning': _('i18n_translation_service.label.morning'),
            'afternoon': _('i18n_translation_service.label.afternoon'),
            'evening': _('i18n_translation_service.label.evening'), 'night':
            _('i18n_translation_service.label.night')}}
        translations_map = {'tr': {'common': {'save': _(
            'i18n_translation_service.label.kaydet'), 'cancel': _(
            'i18n_translation_service.label.ptal'), 'delete': _(
            'i18n_translation_service.label.sil'), 'edit': _(
            'i18n_translation_service.label.d_zenle'), 'create': _(
            'i18n_translation_service.label.olu_tur'), 'update': _(
            'i18n_translation_service.label.g_ncelle'), 'search': _(
            'i18n_translation_service.label.ara'), 'filter': _(
            'i18n_translation_service.label.filtrele'), 'loading': _(
            'i18n_translation_service.label.y_kleniyor'), 'error': _(
            'i18n_translation_service.label.hata'), 'success': _(
            'i18n_translation_service.label.ba_ar_l'), 'warning': _(
            'i18n_translation_service.label.uyar'), 'info': _(
            'i18n_translation_service.label.bilgi'), 'confirm': _(
            'i18n_translation_service.label.onayla'), 'yes': _(
            'i18n_translation_service.label.evet'), 'no': _(
            'i18n_translation_service.label.hay_r'), 'ok': _(
            'i18n_translation_service.label.tamam'), 'submit': _(
            'i18n_translation_service.label.g_nder'), 'reset': _(
            'i18n_translation_service.label.s_f_rla'), 'close': _(
            'i18n_translation_service.label.kapat'), 'back': _(
            'i18n_translation_service.label.geri'), 'next': _(
            'i18n_translation_service.label.leri'), 'previous': _(
            'i18n_translation_service.label.nceki'), 'home': _(
            'i18n_translation_service.label.ana_sayfa'), 'dashboard': _(
            'i18n_translation_service.label.kontrol_paneli'), 'profile': _(
            'i18n_translation_service.label.profil_2'), 'settings': _(
            'i18n_translation_service.label.ayarlar'), 'logout': _(
            'i18n_translation_service.label.k'), 'login': _(
            'i18n_translation_service.label.giri'), 'register': _(
            'i18n_translation_service.label.kay_t_ol')}, 'auth': {'email':
            _('i18n_translation_service.label.e_posta'), 'password': _(
            'i18n_translation_service.label.ifre'), 'confirm_password': _(
            'i18n_translation_service.label.ifreyi_onayla'), 'remember_me':
            _('i18n_translation_service.label.beni_hat_rla'),
            'forgot_password': _(
            'i18n_translation_service.label.ifremi_unuttum'),
            'reset_password': _(
            'i18n_translation_service.label.ifreyi_s_f_rla'),
            'login_success': _(
            'i18n_translation_service.label.giri_ba_ar_l'), 'login_failed':
            _('i18n_translation_service.label.giri_ba_ar_s_z'),
            'logout_success': _('i18n_translation_service.label.k_ba_ar_l'),
            'registration_success': _(
            'i18n_translation_service.label.kay_t_ba_ar_l'),
            'invalid_credentials': _(
            'i18n_translation_service.label.ge_ersiz_kimlik_bilgileri'),
            'password_reset_sent': _(
            'i18n_translation_service.message.ifre_s_f_rlama_e_postas_g_nd'
            ), 'password_updated': _(
            'i18n_translation_service.label.ifre_ba_ar_yla_g_ncellendi')}},
            'ar': {'common': {'save': _('i18n_translation_service.message.'
            ), 'cancel': _('i18n_translation_service.message._1'), 'delete':
            _('i18n_translation_service.message._2'), 'edit': _(
            'i18n_translation_service.message._3'), 'create': _(
            'i18n_translation_service.message._4'), 'update': _(
            'i18n_translation_service.message._5'), 'search': _(
            'i18n_translation_service.message._6'), 'filter': _(
            'i18n_translation_service.message._7'), 'loading': _(
            'i18n_translation_service.message._8'), 'error': _(
            'i18n_translation_service.message._9'), 'success': _(
            'i18n_translation_service.message._10'), 'warning': _(
            'i18n_translation_service.message._11'), 'info': _(
            'i18n_translation_service.message._12'), 'confirm': _(
            'i18n_translation_service.message._13'), 'yes': _(
            'i18n_translation_service.message._14'), 'no': 'لا', 'ok': _(
            'i18n_translation_service.message._15'), 'submit': _(
            'i18n_translation_service.message._16'), 'reset': _(
            'i18n_translation_service.message._17'), 'close': _(
            'i18n_translation_service.message._18'), 'back': _(
            'i18n_translation_service.message._19'), 'next': _(
            'i18n_translation_service.message._20'), 'previous': _(
            'i18n_translation_service.message._21'), 'home': _(
            'i18n_translation_service.message._22'), 'dashboard': _(
            'i18n_translation_service.message._23'), 'profile': _(
            'i18n_translation_service.message._24'), 'settings': _(
            'i18n_translation_service.message._25'), 'logout': _(
            'i18n_translation_service.message._26'), 'login': _(
            'i18n_translation_service.message._27'), 'register': _(
            'i18n_translation_service.message._28')}}, 'es': {'common': {
            'save': _('i18n_translation_service.label.guardar'), 'cancel':
            _('i18n_translation_service.label.cancelar'), 'delete': _(
            'i18n_translation_service.label.eliminar'), 'edit': _(
            'i18n_translation_service.label.editar'), 'create': _(
            'i18n_translation_service.label.crear'), 'update': _(
            'i18n_translation_service.label.actualizar'), 'search': _(
            'i18n_translation_service.label.buscar'), 'filter': _(
            'i18n_translation_service.label.filtrar'), 'loading': _(
            'i18n_translation_service.label.cargando'), 'error': _(
            'i18n_translation_service.error.error_1'), 'success': _(
            'i18n_translation_service.label.xito'), 'warning': _(
            'i18n_translation_service.label.advertencia'), 'info': _(
            'i18n_translation_service.label.informaci_n'), 'confirm': _(
            'i18n_translation_service.label.confirmar'), 'yes': 'Sí', 'no':
            'No', 'ok': 'OK', 'submit': _(
            'i18n_translation_service.label.enviar'), 'reset': _(
            'i18n_translation_service.label.restablecer'), 'close': _(
            'i18n_translation_service.label.cerrar'), 'back': _(
            'i18n_translation_service.label.atr_s'), 'next': _(
            'i18n_translation_service.label.siguiente'), 'previous': _(
            'i18n_translation_service.label.anterior'), 'home': _(
            'i18n_translation_service.label.inicio'), 'dashboard': _(
            'i18n_translation_service.label.panel'), 'profile': _(
            'i18n_translation_service.label.perfil'), 'settings': _(
            'i18n_translation_service.label.configuraci_n'), 'logout': _(
            'i18n_translation_service.label.cerrar_sesi_n'), 'login': _(
            'i18n_translation_service.label.iniciar_sesi_n'), 'register': _
            ('i18n_translation_service.label.registrarse')}}, 'fr': {
            'common': {'save': _(
            'i18n_translation_service.label.enregistrer'), 'cancel': _(
            'i18n_translation_service.label.annuler'), 'delete': _(
            'i18n_translation_service.label.supprimer'), 'edit': _(
            'i18n_translation_service.label.modifier'), 'create': _(
            'i18n_translation_service.label.cr_er'), 'update': _(
            'i18n_translation_service.label.mettre_jour'), 'search': _(
            'i18n_translation_service.label.rechercher'), 'filter': _(
            'i18n_translation_service.label.filtrer'), 'loading': _(
            'i18n_translation_service.label.chargement'), 'error': _(
            'i18n_translation_service.label.erreur'), 'success': _(
            'i18n_translation_service.label.succ_s'), 'warning': _(
            'i18n_translation_service.label.avertissement'), 'info': _(
            'i18n_translation_service.validation.information_2'), 'confirm':
            _('i18n_translation_service.label.confirmer'), 'yes': _(
            'i18n_translation_service.label.oui'), 'no': _(
            'i18n_translation_service.label.non'), 'ok': 'OK', 'submit': _(
            'i18n_translation_service.label.soumettre'), 'reset': _(
            'i18n_translation_service.label.r_initialiser'), 'close': _(
            'i18n_translation_service.label.fermer'), 'back': _(
            'i18n_translation_service.label.retour'), 'next': _(
            'i18n_translation_service.label.suivant'), 'previous': _(
            'i18n_translation_service.label.pr_c_dent'), 'home': _(
            'i18n_translation_service.label.accueil'), 'dashboard': _(
            'i18n_translation_service.label.tableau_de_bord'), 'profile': _
            ('i18n_translation_service.label.profil_2'), 'settings': _(
            'i18n_translation_service.label.param_tres'), 'logout': _(
            'i18n_translation_service.label.d_connexion'), 'login': _(
            'i18n_translation_service.label.connexion'), 'register': _(
            'i18n_translation_service.label.s_inscrire')}}, 'de': {'common':
            {'save': _('i18n_translation_service.label.speichern'),
            'cancel': _('i18n_translation_service.label.abbrechen'),
            'delete': _('i18n_translation_service.label.l_schen'), 'edit':
            _('i18n_translation_service.label.bearbeiten'), 'create': _(
            'i18n_translation_service.label.erstellen'), 'update': _(
            'i18n_translation_service.label.aktualisieren'), 'search': _(
            'i18n_translation_service.label.suchen'), 'filter': _(
            'i18n_translation_service.label.filtern'), 'loading': _(
            'i18n_translation_service.label.laden'), 'error': _(
            'i18n_translation_service.label.fehler'), 'success': _(
            'i18n_translation_service.label.erfolg'), 'warning': _(
            'i18n_translation_service.label.warnung'), 'info': _(
            'i18n_translation_service.validation.information_2'), 'confirm':
            _('i18n_translation_service.label.best_tigen'), 'yes': 'Ja',
            'no': _('i18n_translation_service.label.nein'), 'ok': 'OK',
            'submit': _('i18n_translation_service.label.senden'), 'reset':
            _('i18n_translation_service.label.zur_cksetzen'), 'close': _(
            'i18n_translation_service.label.schlie_en'), 'back': _(
            'i18n_translation_service.label.zur_ck'), 'next': _(
            'i18n_translation_service.label.weiter'), 'previous': _(
            'i18n_translation_service.label.vorherige'), 'home': _(
            'i18n_translation_service.label.startseite'), 'dashboard': _(
            'i18n_translation_service.label.dashboard_1'), 'profile': _(
            'i18n_translation_service.label.profil_2'), 'settings': _(
            'i18n_translation_service.label.einstellungen'), 'logout': _(
            'i18n_translation_service.label.abmelden'), 'login': _(
            'i18n_translation_service.label.anmelden'), 'register': _(
            'i18n_translation_service.label.registrieren')}}, 'ru': {
            'common': {'save': _('i18n_translation_service.label.'),
            'cancel': _('i18n_translation_service.label._1'), 'delete': _(
            'i18n_translation_service.label._2'), 'edit': _(
            'i18n_translation_service.label._3'), 'create': _(
            'i18n_translation_service.label._4'), 'update': _(
            'i18n_translation_service.label._5'), 'search': _(
            'i18n_translation_service.label._6'), 'filter': _(
            'i18n_translation_service.label._7'), 'loading': _(
            'i18n_translation_service.label._8'), 'error': _(
            'i18n_translation_service.label._9'), 'success': _(
            'i18n_translation_service.label._10'), 'warning': _(
            'i18n_translation_service.label._11'), 'info': _(
            'i18n_translation_service.label._12'), 'confirm': _(
            'i18n_translation_service.label._13'), 'yes': 'Да', 'no': _(
            'i18n_translation_service.label._14'), 'ok': 'ОК', 'submit': _(
            'i18n_translation_service.label._15'), 'reset': _(
            'i18n_translation_service.label._16'), 'close': _(
            'i18n_translation_service.label._17'), 'back': _(
            'i18n_translation_service.label._18'), 'next': _(
            'i18n_translation_service.label._19'), 'previous': _(
            'i18n_translation_service.label._20'), 'home': _(
            'i18n_translation_service.label._21'), 'dashboard': _(
            'i18n_translation_service.label._22'), 'profile': _(
            'i18n_translation_service.label._23'), 'settings': _(
            'i18n_translation_service.label._24'), 'logout': _(
            'i18n_translation_service.label._25'), 'login': _(
            'i18n_translation_service.label._26'), 'register': _(
            'i18n_translation_service.label._27')}}}
        if language_code in translations_map:
            result = base_translations.copy()
            for section, translations in translations_map[language_code].items(
                ):
                if section in result:
                    result[section].update(translations)
                else:
                    result[section] = translations
            return result
        return base_translations

    @cache_manager.memoize(timeout=3600)
    def translate(self, key: str, language: str, **kwargs) ->TranslationResult:
        _('i18n_translation_service.validation.translate_a_key_to_th')
        try:
            language = self.language_service.normalize_language_code(language)
            if language not in self.translations_cache:
                self._load_translation_file(language)
            translations = self.translations_cache.get(language, {})
            value = translations
            for key_part in key.split('.'):
                if isinstance(value, dict) and key_part in value:
                    value = value[key_part]
                else:
                    value = None
                    break
            if value and isinstance(value, str):
                try:
                    formatted_text = value.format(**kwargs
                        ) if kwargs else value
                    return TranslationResult(text=formatted_text, language=
                        language, source='file', confidence=1.0)
                except (KeyError, ValueError) as e:
                    logger.warning(f'Error formatting translation {key}: {e}')
                    return TranslationResult(text=value, language=language,
                        source='file', confidence=0.8)
            fallback_language = self.language_service.get_fallback_language(
                language)
            if fallback_language != language:
                fallback_result = self.translate(key, fallback_language, **
                    kwargs)
                if fallback_result.text != key:
                    return TranslationResult(text=fallback_result.text,
                        language=fallback_language, source='fallback',
                        confidence=0.6)
            return TranslationResult(text=key, language=language, source=
                'fallback', confidence=0.1)
        except Exception as e:
            logger.error(f'Error translating key {key} to {language}: {e}')
            return TranslationResult(text=key, language=language, source=
                'fallback', confidence=0.0)

    def get_translation_dict(self, language: str, section: Optional[str]=None
        ) ->Dict[str, Any]:
        _('i18n_translation_service.message.get_translation_dicti')
        try:
            language = self.language_service.normalize_language_code(language)
            if language not in self.translations_cache:
                self._load_translation_file(language)
            translations = self.translations_cache.get(language, {})
            if section:
                return translations.get(section, {})
            return translations
        except Exception as e:
            logger.error(f'Error getting translation dict for {language}: {e}')
            return {}

    def update_translation(self, key: str, language: str, value: str,
        save_to_file: bool=True):
        """
        Update a translation value.
        
        Args:
            key: Translation key
            language: Language code
            value: New translation value
            save_to_file: Whether to save to file immediately
        """
        try:
            language = self.language_service.normalize_language_code(language)
            if language not in self.translations_cache:
                self._load_translation_file(language)
            translations = self.translations_cache[language]
            key_parts = key.split('.')
            current = translations
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[key_parts[-1]] = value
            if save_to_file:
                self._save_translation_file(language)
            cache_key = f'translate_{key}_{language}'
            cache_manager.delete(cache_key)
        except Exception as e:
            logger.error(
                f'Error updating translation {key} for {language}: {e}')

    def _save_translation_file(self, language: str):
        _('i18n_translation_service.message.save_translation_file')
        try:
            file_path = self.translations_dir / f'{language}.json'
            translations = self.translations_cache.get(language, {})
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f'Error saving translation file for {language}: {e}')

    def bulk_update_translations(self, updates: Dict[str, Dict[str, str]],
        save_to_file: bool=True):
        """
        Bulk update translations for multiple languages.
        
        Args:
            updates: Dictionary of {language: {key: value}}
            save_to_file: Whether to save to files
        """
        try:
            for language, translations in updates.items():
                for key, value in translations.items():
                    self.update_translation(key, language, value,
                        save_to_file=False)
                if save_to_file:
                    self._save_translation_file(language)
        except Exception as e:
            logger.error(f'Error in bulk update translations: {e}')

    def get_missing_translations(self, target_language: str,
        reference_language: str='en') ->List[str]:
        _('i18n_translation_service.message.get_list_of_missing_t')
        try:
            ref_translations = self.get_translation_dict(reference_language)
            target_translations = self.get_translation_dict(target_language)
            missing_keys = []

            def check_nested_keys(ref_dict, target_dict, prefix=''):
                for key, value in ref_dict.items():
                    full_key = f'{prefix}.{key}' if prefix else key
                    if isinstance(value, dict):
                        target_section = target_dict.get(key, {})
                        check_nested_keys(value, target_section, full_key)
                    elif key not in target_dict or not target_dict[key]:
                        missing_keys.append(full_key)
            check_nested_keys(ref_translations, target_translations)
            return missing_keys
        except Exception as e:
            logger.error(f'Error getting missing translations: {e}')
            return []

    def get_translation_coverage(self, language: str, reference_language:
        str='en') ->float:
        _('i18n_translation_service.message.get_translation_cover')
        try:
            missing = self.get_missing_translations(language,
                reference_language)
            ref_translations = self.get_translation_dict(reference_language)

            def count_keys(d):
                count = 0
                for value in d.values():
                    if isinstance(value, dict):
                        count += count_keys(value)
                    else:
                        count += 1
                return count
            total_keys = count_keys(ref_translations)
            if total_keys == 0:
                return 1.0
            return max(0.0, (total_keys - len(missing)) / total_keys)
        except Exception as e:
            logger.error(f'Error calculating translation coverage: {e}')
            return 0.0
