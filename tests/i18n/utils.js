/**
 * i18n Testing Utilities
 * Comprehensive utilities for testing internationalization features
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { SUPPORTED_LANGUAGES, RTL_LANGUAGES } from '../../client/src/i18n/constants';

/**
 * Initialize test i18n instance with mock translations
 */
export const initTestI18n = (initialLanguage = 'en') => {
  const testI18n = i18n.createInstance();
  
  testI18n
    .use(initReactI18next)
    .init({
      lng: initialLanguage,
      fallbackLng: 'en',
      ns: ['translation'],
      defaultNS: 'translation',
      resources: getMockTranslations(),
      interpolation: {
        escapeValue: false
      },
      react: {
        useSuspense: false
      }
    });
    
  return testI18n;
};

/**
 * Get mock translations for testing
 */
export const getMockTranslations = () => ({
  en: {
    translation: {
      common: {
        welcome: 'Welcome',
        hello: 'Hello {{name}}',
        items_count_one: '{{count}} item',
        items_count_other: '{{count}} items',
        save: 'Save',
        cancel: 'Cancel',
        delete: 'Delete',
        edit: 'Edit',
        loading: 'Loading...',
        error: 'Error',
        success: 'Success'
      },
      auth: {
        login: 'Login',
        logout: 'Logout',
        email: 'Email',
        password: 'Password',
        forgot_password: 'Forgot Password?',
        register: 'Register',
        login_success: 'Login successful',
        login_failed: 'Invalid credentials'
      },
      validation: {
        required: '{{field}} is required',
        email_invalid: 'Invalid email format',
        password_weak: 'Password must be at least 8 characters',
        field_too_short: '{{field}} must be at least {{min}} characters',
        field_too_long: '{{field}} must not exceed {{max}} characters'
      },
      dashboard: {
        title: 'Dashboard',
        welcome_back: 'Welcome back, {{name}}!',
        statistics: 'Statistics',
        recent_activity: 'Recent Activity'
      },
      rtl_test: {
        text_alignment: 'This text should align properly',
        mixed_content: 'English text with עברית mixed',
        number_format: 'Number: {{number}}'
      }
    }
  },
  es: {
    translation: {
      common: {
        welcome: 'Bienvenido',
        hello: 'Hola {{name}}',
        items_count_one: '{{count}} artículo',
        items_count_other: '{{count}} artículos',
        save: 'Guardar',
        cancel: 'Cancelar',
        delete: 'Eliminar',
        edit: 'Editar',
        loading: 'Cargando...',
        error: 'Error',
        success: 'Éxito'
      },
      auth: {
        login: 'Iniciar sesión',
        logout: 'Cerrar sesión',
        email: 'Correo electrónico',
        password: 'Contraseña',
        forgot_password: '¿Olvidaste tu contraseña?',
        register: 'Registrarse',
        login_success: 'Inicio de sesión exitoso',
        login_failed: 'Credenciales inválidas'
      },
      validation: {
        required: '{{field}} es requerido',
        email_invalid: 'Formato de correo inválido',
        password_weak: 'La contraseña debe tener al menos 8 caracteres',
        field_too_short: '{{field}} debe tener al menos {{min}} caracteres',
        field_too_long: '{{field}} no debe exceder {{max}} caracteres'
      },
      dashboard: {
        title: 'Tablero',
        welcome_back: '¡Bienvenido de nuevo, {{name}}!',
        statistics: 'Estadísticas',
        recent_activity: 'Actividad Reciente'
      }
    }
  },
  ar: {
    translation: {
      common: {
        welcome: 'مرحبا',
        hello: 'مرحبا {{name}}',
        items_count_zero: 'لا توجد عناصر',
        items_count_one: 'عنصر واحد',
        items_count_two: 'عنصران',
        items_count_few: '{{count}} عناصر',
        items_count_many: '{{count}} عنصراً',
        items_count_other: '{{count}} عنصر',
        save: 'حفظ',
        cancel: 'إلغاء',
        delete: 'حذف',
        edit: 'تعديل',
        loading: 'جاري التحميل...',
        error: 'خطأ',
        success: 'نجاح'
      },
      auth: {
        login: 'تسجيل الدخول',
        logout: 'تسجيل الخروج',
        email: 'البريد الإلكتروني',
        password: 'كلمة المرور',
        forgot_password: 'نسيت كلمة المرور؟',
        register: 'تسجيل',
        login_success: 'تم تسجيل الدخول بنجاح',
        login_failed: 'بيانات الاعتماد غير صحيحة'
      },
      rtl_test: {
        text_alignment: 'يجب أن يتم محاذاة هذا النص بشكل صحيح',
        mixed_content: 'نص عربي مع English مختلط',
        number_format: 'الرقم: {{number}}'
      }
    }
  },
  he: {
    translation: {
      common: {
        welcome: 'ברוך הבא',
        hello: 'שלום {{name}}',
        items_count_one: 'פריט אחד',
        items_count_two: 'שני פריטים',
        items_count_many: '{{count}} פריטים',
        items_count_other: '{{count}} פריטים',
        save: 'שמור',
        cancel: 'ביטול',
        delete: 'מחק',
        edit: 'ערוך',
        loading: 'טוען...',
        error: 'שגיאה',
        success: 'הצלחה'
      },
      rtl_test: {
        text_alignment: 'הטקסט הזה צריך להיות מיושר נכון',
        mixed_content: 'טקסט עברי עם English מעורב',
        number_format: 'מספר: {{number}}'
      }
    }
  },
  fr: {
    translation: {
      common: {
        welcome: 'Bienvenue',
        hello: 'Bonjour {{name}}',
        items_count_one: '{{count}} élément',
        items_count_other: '{{count}} éléments',
        save: 'Enregistrer',
        cancel: 'Annuler',
        delete: 'Supprimer',
        edit: 'Modifier'
      }
    }
  },
  de: {
    translation: {
      common: {
        welcome: 'Willkommen',
        hello: 'Hallo {{name}}',
        items_count_one: '{{count}} Artikel',
        items_count_other: '{{count}} Artikel',
        save: 'Speichern',
        cancel: 'Abbrechen',
        delete: 'Löschen',
        edit: 'Bearbeiten'
      }
    }
  }
});

/**
 * Test helper to switch languages
 */
export const switchLanguage = async (i18nInstance, language) => {
  await i18nInstance.changeLanguage(language);
  return new Promise(resolve => {
    i18nInstance.on('languageChanged', () => {
      resolve();
    });
  });
};

/**
 * Check if a language is RTL
 */
export const isRTL = (language) => {
  return RTL_LANGUAGES.includes(language);
};

/**
 * Get direction for a language
 */
export const getDirection = (language) => {
  return isRTL(language) ? 'rtl' : 'ltr';
};

/**
 * Format number according to locale
 */
export const formatNumber = (number, language) => {
  const locale = SUPPORTED_LANGUAGES[language]?.locale || 'en-US';
  return new Intl.NumberFormat(locale).format(number);
};

/**
 * Format currency according to locale
 */
export const formatCurrency = (amount, language) => {
  const langConfig = SUPPORTED_LANGUAGES[language];
  const locale = langConfig?.locale || 'en-US';
  const currency = langConfig?.currency || 'USD';
  
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency
  }).format(amount);
};

/**
 * Format date according to locale
 */
export const formatDate = (date, language) => {
  const locale = SUPPORTED_LANGUAGES[language]?.locale || 'en-US';
  return new Intl.DateTimeFormat(locale).format(new Date(date));
};

/**
 * Check if all required translations exist
 */
export const checkTranslationKeys = (translations, requiredKeys) => {
  const missingKeys = [];
  
  const checkKeys = (obj, keys, path = '') => {
    keys.forEach(key => {
      const fullPath = path ? `${path}.${key}` : key;
      if (typeof key === 'object') {
        const [nestedKey, nestedKeys] = Object.entries(key)[0];
        if (obj[nestedKey]) {
          checkKeys(obj[nestedKey], nestedKeys, fullPath);
        } else {
          missingKeys.push(`${fullPath}.${nestedKey}`);
        }
      } else {
        if (!obj[key]) {
          missingKeys.push(fullPath);
        }
      }
    });
  };
  
  Object.entries(translations).forEach(([lang, data]) => {
    checkKeys(data.translation, requiredKeys, lang);
  });
  
  return missingKeys;
};

/**
 * Mock translation function for testing
 */
export const mockT = (key, options = {}) => {
  // Simple mock that returns key with options
  if (Object.keys(options).length > 0) {
    let result = key;
    Object.entries(options).forEach(([k, v]) => {
      result = result.replace(`{{${k}}}`, v);
    });
    return result;
  }
  return key;
};

/**
 * Test helper to check RTL styles
 */
export const checkRTLStyles = (element, language) => {
  const isRTLLang = isRTL(language);
  const computedStyle = window.getComputedStyle(element);
  
  return {
    direction: computedStyle.direction === (isRTLLang ? 'rtl' : 'ltr'),
    textAlign: isRTLLang ? 
      ['right', 'start'].includes(computedStyle.textAlign) :
      ['left', 'start'].includes(computedStyle.textAlign),
    marginRight: isRTLLang ? computedStyle.marginLeft : computedStyle.marginRight,
    marginLeft: isRTLLang ? computedStyle.marginRight : computedStyle.marginLeft,
    paddingRight: isRTLLang ? computedStyle.paddingLeft : computedStyle.paddingRight,
    paddingLeft: isRTLLang ? computedStyle.paddingRight : computedStyle.paddingLeft
  };
};

/**
 * Generate test cases for all supported languages
 */
export const generateLanguageTestCases = (testFn) => {
  return Object.keys(SUPPORTED_LANGUAGES).map(lang => ({
    language: lang,
    testFn: () => testFn(lang)
  }));
};

/**
 * Wait for translation to be loaded
 */
export const waitForTranslation = (key, timeout = 5000) => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const checkTranslation = () => {
      if (i18n.exists(key)) {
        resolve(i18n.t(key));
      } else if (Date.now() - startTime > timeout) {
        reject(new Error(`Translation key "${key}" not found after ${timeout}ms`));
      } else {
        setTimeout(checkTranslation, 100);
      }
    };
    
    checkTranslation();
  });
};

/**
 * Mock localStorage for testing
 */
export const mockLocalStorage = () => {
  const storage = {};
  
  return {
    getItem: (key) => storage[key] || null,
    setItem: (key, value) => { storage[key] = value; },
    removeItem: (key) => { delete storage[key]; },
    clear: () => { Object.keys(storage).forEach(key => delete storage[key]); },
    get length() { return Object.keys(storage).length; },
    key: (index) => Object.keys(storage)[index] || null
  };
};

/**
 * Test interpolation with various data types
 */
export const testInterpolation = (i18nInstance, key, variables) => {
  return i18nInstance.t(key, variables);
};

/**
 * Test pluralization rules
 */
export const testPluralization = (i18nInstance, key, count) => {
  return i18nInstance.t(key, { count });
};

/**
 * Check if translation exists
 */
export const hasTranslation = (i18nInstance, key, language) => {
  const currentLang = i18nInstance.language;
  i18nInstance.changeLanguage(language);
  const exists = i18nInstance.exists(key);
  i18nInstance.changeLanguage(currentLang);
  return exists;
};

export default {
  initTestI18n,
  getMockTranslations,
  switchLanguage,
  isRTL,
  getDirection,
  formatNumber,
  formatCurrency,
  formatDate,
  checkTranslationKeys,
  mockT,
  checkRTLStyles,
  generateLanguageTestCases,
  waitForTranslation,
  mockLocalStorage,
  testInterpolation,
  testPluralization,
  hasTranslation
};