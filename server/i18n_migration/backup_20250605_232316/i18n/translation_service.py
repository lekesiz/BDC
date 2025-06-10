"""Translation service for multi-language support."""

import json
import logging
import os
from typing import Dict, Optional, Any, List
from pathlib import Path
from dataclasses import dataclass
from app.utils.cache import cache_manager
from app.services.i18n.language_detection_service import LanguageDetectionService

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Translation result with metadata."""
    text: str
    language: str
    source: str  # 'file', 'ai', 'fallback'
    confidence: float = 1.0


class TranslationService:
    """Service for handling translations and localization."""
    
    def __init__(self):
        """Initialize translation service."""
        self.language_service = LanguageDetectionService()
        self.translations_cache = {}
        self.translations_dir = Path(__file__).parent.parent.parent / 'locales'
        self.cache_timeout = 3600  # 1 hour
        
        # Ensure translations directory exists
        self.translations_dir.mkdir(exist_ok=True)
        
        # Load all translation files on init
        self._load_all_translations()
    
    def _load_all_translations(self):
        """Load all translation files into memory."""
        try:
            for language_code in self.language_service.SUPPORTED_LANGUAGES.keys():
                self._load_translation_file(language_code)
        except Exception as e:
            logger.error(f"Error loading translations: {e}")
    
    def _load_translation_file(self, language_code: str) -> Dict[str, Any]:
        """
        Load translation file for a specific language.
        
        Args:
            language_code: Language code
            
        Returns:
            Translation dictionary
        """
        try:
            file_path = self.translations_dir / f'{language_code}.json'
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations = json.load(f)
                    self.translations_cache[language_code] = translations
                    return translations
            else:
                # Create default translation file if it doesn't exist
                self._create_default_translation_file(language_code)
                return self.translations_cache.get(language_code, {})
                
        except Exception as e:
            logger.error(f"Error loading translation file for {language_code}: {e}")
            return {}
    
    def _create_default_translation_file(self, language_code: str):
        """
        Create default translation file for a language.
        
        Args:
            language_code: Language code
        """
        try:
            default_translations = self._get_default_translations(language_code)
            
            file_path = self.translations_dir / f'{language_code}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_translations, f, ensure_ascii=False, indent=2)
            
            self.translations_cache[language_code] = default_translations
            logger.info(f"Created default translation file for {language_code}")
            
        except Exception as e:
            logger.error(f"Error creating default translation file for {language_code}: {e}")
    
    def _get_default_translations(self, language_code: str) -> Dict[str, Any]:
        """
        Get default translations for a language.
        
        Args:
            language_code: Language code
            
        Returns:
            Default translations dictionary
        """
        # Base translations structure
        base_translations = {
            "common": {
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "create": "Create",
                "update": "Update",
                "search": "Search",
                "filter": "Filter",
                "loading": "Loading...",
                "error": "Error",
                "success": "Success",
                "warning": "Warning",
                "info": "Information",
                "confirm": "Confirm",
                "yes": "Yes",
                "no": "No",
                "ok": "OK",
                "submit": "Submit",
                "reset": "Reset",
                "close": "Close",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "home": "Home",
                "dashboard": "Dashboard",
                "profile": "Profile",
                "settings": "Settings",
                "logout": "Logout",
                "login": "Login",
                "register": "Register"
            },
            "auth": {
                "email": "Email",
                "password": "Password",
                "confirm_password": "Confirm Password",
                "remember_me": "Remember Me",
                "forgot_password": "Forgot Password?",
                "reset_password": "Reset Password",
                "login_success": "Login successful",
                "login_failed": "Login failed",
                "logout_success": "Logout successful",
                "registration_success": "Registration successful",
                "invalid_credentials": "Invalid credentials",
                "password_reset_sent": "Password reset email sent",
                "password_updated": "Password updated successfully"
            },
            "navigation": {
                "beneficiaries": "Beneficiaries",
                "programs": "Programs",
                "appointments": "Appointments",
                "documents": "Documents",
                "reports": "Reports",
                "calendar": "Calendar",
                "messages": "Messages",
                "notifications": "Notifications",
                "analytics": "Analytics",
                "administration": "Administration",
                "users": "Users",
                "tenants": "Tenants"
            },
            "forms": {
                "first_name": "First Name",
                "last_name": "Last Name",
                "phone": "Phone",
                "address": "Address",
                "city": "City",
                "state": "State",
                "country": "Country",
                "zip_code": "ZIP Code",
                "organization": "Organization",
                "bio": "Biography",
                "date_of_birth": "Date of Birth",
                "gender": "Gender",
                "emergency_contact": "Emergency Contact",
                "notes": "Notes",
                "description": "Description",
                "title": "Title",
                "start_date": "Start Date",
                "end_date": "End Date",
                "status": "Status"
            },
            "messages": {
                "no_data": "No data available",
                "no_results": "No results found",
                "data_saved": "Data saved successfully",
                "data_deleted": "Data deleted successfully",
                "operation_failed": "Operation failed",
                "permission_denied": "Permission denied",
                "invalid_input": "Invalid input",
                "required_field": "This field is required",
                "invalid_email": "Invalid email address",
                "password_too_short": "Password is too short",
                "passwords_dont_match": "Passwords don't match",
                "file_uploaded": "File uploaded successfully",
                "file_too_large": "File is too large",
                "invalid_file_type": "Invalid file type"
            },
            "errors": {
                "network_error": "Network error occurred",
                "server_error": "Server error occurred",
                "not_found": "Resource not found",
                "unauthorized": "Unauthorized access",
                "forbidden": "Access forbidden",
                "validation_error": "Validation error",
                "timeout": "Request timeout",
                "unknown_error": "Unknown error occurred"
            },
            "date_time": {
                "today": "Today",
                "yesterday": "Yesterday",
                "tomorrow": "Tomorrow",
                "this_week": "This Week",
                "last_week": "Last Week",
                "next_week": "Next Week",
                "this_month": "This Month",
                "last_month": "Last Month",
                "next_month": "Next Month",
                "this_year": "This Year",
                "morning": "Morning",
                "afternoon": "Afternoon",
                "evening": "Evening",
                "night": "Night"
            }
        }
        
        # Language-specific translations
        translations_map = {
            'tr': {
                "common": {
                    "save": "Kaydet",
                    "cancel": "İptal",
                    "delete": "Sil",
                    "edit": "Düzenle",
                    "create": "Oluştur",
                    "update": "Güncelle",
                    "search": "Ara",
                    "filter": "Filtrele",
                    "loading": "Yükleniyor...",
                    "error": "Hata",
                    "success": "Başarılı",
                    "warning": "Uyarı",
                    "info": "Bilgi",
                    "confirm": "Onayla",
                    "yes": "Evet",
                    "no": "Hayır",
                    "ok": "Tamam",
                    "submit": "Gönder",
                    "reset": "Sıfırla",
                    "close": "Kapat",
                    "back": "Geri",
                    "next": "İleri",
                    "previous": "Önceki",
                    "home": "Ana Sayfa",
                    "dashboard": "Kontrol Paneli",
                    "profile": "Profil",
                    "settings": "Ayarlar",
                    "logout": "Çıkış",
                    "login": "Giriş",
                    "register": "Kayıt Ol"
                },
                "auth": {
                    "email": "E-posta",
                    "password": "Şifre",
                    "confirm_password": "Şifreyi Onayla",
                    "remember_me": "Beni Hatırla",
                    "forgot_password": "Şifremi Unuttum",
                    "reset_password": "Şifreyi Sıfırla",
                    "login_success": "Giriş başarılı",
                    "login_failed": "Giriş başarısız",
                    "logout_success": "Çıkış başarılı",
                    "registration_success": "Kayıt başarılı",
                    "invalid_credentials": "Geçersiz kimlik bilgileri",
                    "password_reset_sent": "Şifre sıfırlama e-postası gönderildi",
                    "password_updated": "Şifre başarıyla güncellendi"
                }
            },
            'ar': {
                "common": {
                    "save": "حفظ",
                    "cancel": "إلغاء",
                    "delete": "حذف",
                    "edit": "تحرير",
                    "create": "إنشاء",
                    "update": "تحديث",
                    "search": "بحث",
                    "filter": "تصفية",
                    "loading": "جاري التحميل...",
                    "error": "خطأ",
                    "success": "نجح",
                    "warning": "تحذير",
                    "info": "معلومات",
                    "confirm": "تأكيد",
                    "yes": "نعم",
                    "no": "لا",
                    "ok": "موافق",
                    "submit": "إرسال",
                    "reset": "إعادة تعيين",
                    "close": "إغلاق",
                    "back": "العودة",
                    "next": "التالي",
                    "previous": "السابق",
                    "home": "الرئيسية",
                    "dashboard": "لوحة التحكم",
                    "profile": "الملف الشخصي",
                    "settings": "الإعدادات",
                    "logout": "تسجيل الخروج",
                    "login": "تسجيل الدخول",
                    "register": "التسجيل"
                }
            },
            'es': {
                "common": {
                    "save": "Guardar",
                    "cancel": "Cancelar",
                    "delete": "Eliminar",
                    "edit": "Editar",
                    "create": "Crear",
                    "update": "Actualizar",
                    "search": "Buscar",
                    "filter": "Filtrar",
                    "loading": "Cargando...",
                    "error": "Error",
                    "success": "Éxito",
                    "warning": "Advertencia",
                    "info": "Información",
                    "confirm": "Confirmar",
                    "yes": "Sí",
                    "no": "No",
                    "ok": "OK",
                    "submit": "Enviar",
                    "reset": "Restablecer",
                    "close": "Cerrar",
                    "back": "Atrás",
                    "next": "Siguiente",
                    "previous": "Anterior",
                    "home": "Inicio",
                    "dashboard": "Panel",
                    "profile": "Perfil",
                    "settings": "Configuración",
                    "logout": "Cerrar Sesión",
                    "login": "Iniciar Sesión",
                    "register": "Registrarse"
                }
            },
            'fr': {
                "common": {
                    "save": "Enregistrer",
                    "cancel": "Annuler",
                    "delete": "Supprimer",
                    "edit": "Modifier",
                    "create": "Créer",
                    "update": "Mettre à jour",
                    "search": "Rechercher",
                    "filter": "Filtrer",
                    "loading": "Chargement...",
                    "error": "Erreur",
                    "success": "Succès",
                    "warning": "Avertissement",
                    "info": "Information",
                    "confirm": "Confirmer",
                    "yes": "Oui",
                    "no": "Non",
                    "ok": "OK",
                    "submit": "Soumettre",
                    "reset": "Réinitialiser",
                    "close": "Fermer",
                    "back": "Retour",
                    "next": "Suivant",
                    "previous": "Précédent",
                    "home": "Accueil",
                    "dashboard": "Tableau de bord",
                    "profile": "Profil",
                    "settings": "Paramètres",
                    "logout": "Déconnexion",
                    "login": "Connexion",
                    "register": "S'inscrire"
                }
            },
            'de': {
                "common": {
                    "save": "Speichern",
                    "cancel": "Abbrechen",
                    "delete": "Löschen",
                    "edit": "Bearbeiten",
                    "create": "Erstellen",
                    "update": "Aktualisieren",
                    "search": "Suchen",
                    "filter": "Filtern",
                    "loading": "Laden...",
                    "error": "Fehler",
                    "success": "Erfolg",
                    "warning": "Warnung",
                    "info": "Information",
                    "confirm": "Bestätigen",
                    "yes": "Ja",
                    "no": "Nein",
                    "ok": "OK",
                    "submit": "Senden",
                    "reset": "Zurücksetzen",
                    "close": "Schließen",
                    "back": "Zurück",
                    "next": "Weiter",
                    "previous": "Vorherige",
                    "home": "Startseite",
                    "dashboard": "Dashboard",
                    "profile": "Profil",
                    "settings": "Einstellungen",
                    "logout": "Abmelden",
                    "login": "Anmelden",
                    "register": "Registrieren"
                }
            },
            'ru': {
                "common": {
                    "save": "Сохранить",
                    "cancel": "Отменить",
                    "delete": "Удалить",
                    "edit": "Редактировать",
                    "create": "Создать",
                    "update": "Обновить",
                    "search": "Поиск",
                    "filter": "Фильтр",
                    "loading": "Загрузка...",
                    "error": "Ошибка",
                    "success": "Успех",
                    "warning": "Предупреждение",
                    "info": "Информация",
                    "confirm": "Подтвердить",
                    "yes": "Да",
                    "no": "Нет",
                    "ok": "ОК",
                    "submit": "Отправить",
                    "reset": "Сбросить",
                    "close": "Закрыть",
                    "back": "Назад",
                    "next": "Далее",
                    "previous": "Предыдущий",
                    "home": "Главная",
                    "dashboard": "Панель управления",
                    "profile": "Профиль",
                    "settings": "Настройки",
                    "logout": "Выйти",
                    "login": "Войти",
                    "register": "Регистрация"
                }
            }
        }
        
        # Merge language-specific translations with base
        if language_code in translations_map:
            result = base_translations.copy()
            for section, translations in translations_map[language_code].items():
                if section in result:
                    result[section].update(translations)
                else:
                    result[section] = translations
            return result
        
        return base_translations
    
    @cache_manager.memoize(timeout=3600)
    def translate(self, key: str, language: str, **kwargs) -> TranslationResult:
        """
        Translate a key to the specified language.
        
        Args:
            key: Translation key (e.g., 'common.save', 'auth.login')
            language: Target language code
            **kwargs: Variables for string formatting
            
        Returns:
            Translation result
        """
        try:
            # Normalize language
            language = self.language_service.normalize_language_code(language)
            
            # Get translation from cache or load
            if language not in self.translations_cache:
                self._load_translation_file(language)
            
            translations = self.translations_cache.get(language, {})
            
            # Navigate nested key
            value = translations
            for key_part in key.split('.'):
                if isinstance(value, dict) and key_part in value:
                    value = value[key_part]
                else:
                    value = None
                    break
            
            # If translation found, format and return
            if value and isinstance(value, str):
                try:
                    formatted_text = value.format(**kwargs) if kwargs else value
                    return TranslationResult(
                        text=formatted_text,
                        language=language,
                        source='file',
                        confidence=1.0
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error formatting translation {key}: {e}")
                    return TranslationResult(
                        text=value,
                        language=language,
                        source='file',
                        confidence=0.8
                    )
            
            # Try fallback language
            fallback_language = self.language_service.get_fallback_language(language)
            if fallback_language != language:
                fallback_result = self.translate(key, fallback_language, **kwargs)
                if fallback_result.text != key:
                    return TranslationResult(
                        text=fallback_result.text,
                        language=fallback_language,
                        source='fallback',
                        confidence=0.6
                    )
            
            # Return key as fallback
            return TranslationResult(
                text=key,
                language=language,
                source='fallback',
                confidence=0.1
            )
            
        except Exception as e:
            logger.error(f"Error translating key {key} to {language}: {e}")
            return TranslationResult(
                text=key,
                language=language,
                source='fallback',
                confidence=0.0
            )
    
    def get_translation_dict(self, language: str, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Get translation dictionary for a language and optional section.
        
        Args:
            language: Language code
            section: Optional section to filter
            
        Returns:
            Translation dictionary
        """
        try:
            language = self.language_service.normalize_language_code(language)
            
            if language not in self.translations_cache:
                self._load_translation_file(language)
            
            translations = self.translations_cache.get(language, {})
            
            if section:
                return translations.get(section, {})
            
            return translations
            
        except Exception as e:
            logger.error(f"Error getting translation dict for {language}: {e}")
            return {}
    
    def update_translation(self, key: str, language: str, value: str, save_to_file: bool = True):
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
            
            # Navigate and update nested key
            translations = self.translations_cache[language]
            key_parts = key.split('.')
            
            current = translations
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[key_parts[-1]] = value
            
            # Save to file if requested
            if save_to_file:
                self._save_translation_file(language)
            
            # Clear cache
            cache_key = f"translate_{key}_{language}"
            cache_manager.delete(cache_key)
            
        except Exception as e:
            logger.error(f"Error updating translation {key} for {language}: {e}")
    
    def _save_translation_file(self, language: str):
        """
        Save translation file to disk.
        
        Args:
            language: Language code
        """
        try:
            file_path = self.translations_dir / f'{language}.json'
            translations = self.translations_cache.get(language, {})
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving translation file for {language}: {e}")
    
    def bulk_update_translations(self, updates: Dict[str, Dict[str, str]], save_to_file: bool = True):
        """
        Bulk update translations for multiple languages.
        
        Args:
            updates: Dictionary of {language: {key: value}}
            save_to_file: Whether to save to files
        """
        try:
            for language, translations in updates.items():
                for key, value in translations.items():
                    self.update_translation(key, language, value, save_to_file=False)
                
                if save_to_file:
                    self._save_translation_file(language)
            
        except Exception as e:
            logger.error(f"Error in bulk update translations: {e}")
    
    def get_missing_translations(self, target_language: str, reference_language: str = 'en') -> List[str]:
        """
        Get list of missing translation keys for a target language.
        
        Args:
            target_language: Language to check
            reference_language: Reference language to compare against
            
        Returns:
            List of missing translation keys
        """
        try:
            ref_translations = self.get_translation_dict(reference_language)
            target_translations = self.get_translation_dict(target_language)
            
            missing_keys = []
            
            def check_nested_keys(ref_dict, target_dict, prefix=''):
                for key, value in ref_dict.items():
                    full_key = f"{prefix}.{key}" if prefix else key
                    
                    if isinstance(value, dict):
                        target_section = target_dict.get(key, {})
                        check_nested_keys(value, target_section, full_key)
                    else:
                        if key not in target_dict or not target_dict[key]:
                            missing_keys.append(full_key)
            
            check_nested_keys(ref_translations, target_translations)
            return missing_keys
            
        except Exception as e:
            logger.error(f"Error getting missing translations: {e}")
            return []
    
    def get_translation_coverage(self, language: str, reference_language: str = 'en') -> float:
        """
        Get translation coverage percentage for a language.
        
        Args:
            language: Language to check
            reference_language: Reference language
            
        Returns:
            Coverage percentage (0.0 to 1.0)
        """
        try:
            missing = self.get_missing_translations(language, reference_language)
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
            logger.error(f"Error calculating translation coverage: {e}")
            return 0.0