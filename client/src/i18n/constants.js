// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * i18n Constants
 * Language configuration and supported features
 */

export const SUPPORTED_LANGUAGES = {
  en: {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    direction: 'ltr',
    locale: 'en-US',
    flag: '🇺🇸',
    dateFormat: 'MM/DD/YYYY',
    currency: 'USD',
    numberFormat: {
      decimal: '.',
      thousand: ',',
      precision: 2
    }
  },
  es: {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    direction: 'ltr',
    locale: 'es-ES',
    flag: '🇪🇸',
    dateFormat: 'DD/MM/YYYY',
    currency: 'EUR',
    numberFormat: {
      decimal: ',',
      thousand: '.',
      precision: 2
    }
  },
  fr: {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    direction: 'ltr',
    locale: 'fr-FR',
    flag: '🇫🇷',
    dateFormat: 'DD/MM/YYYY',
    currency: 'EUR',
    numberFormat: {
      decimal: ',',
      thousand: ' ',
      precision: 2
    }
  },
  tr: {
    code: 'tr',
    name: 'Turkish',
    nativeName: 'Türkçe',
    direction: 'ltr',
    locale: 'tr-TR',
    flag: '🇹🇷',
    dateFormat: 'DD.MM.YYYY',
    currency: 'TRY',
    numberFormat: {
      decimal: ',',
      thousand: '.',
      precision: 2
    }
  },
  ar: {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    direction: 'rtl',
    locale: 'ar-SA',
    flag: '🇸🇦',
    dateFormat: 'DD/MM/YYYY',
    currency: 'SAR',
    numberFormat: {
      decimal: '.',
      thousand: ',',
      precision: 2
    }
  },
  he: {
    code: 'he',
    name: 'Hebrew',
    nativeName: 'עברית',
    direction: 'rtl',
    locale: 'he-IL',
    flag: '🇮🇱',
    dateFormat: 'DD/MM/YYYY',
    currency: 'ILS',
    numberFormat: {
      decimal: '.',
      thousand: ',',
      precision: 2
    }
  },
  de: {
    code: 'de',
    name: 'German',
    nativeName: 'Deutsch',
    direction: 'ltr',
    locale: 'de-DE',
    flag: '🇩🇪',
    dateFormat: 'DD.MM.YYYY',
    currency: 'EUR',
    numberFormat: {
      decimal: ',',
      thousand: '.',
      precision: 2
    }
  },
  ru: {
    code: 'ru',
    name: 'Russian',
    nativeName: 'Русский',
    direction: 'ltr',
    locale: 'ru-RU',
    flag: '🇷🇺',
    dateFormat: 'DD.MM.YYYY',
    currency: 'RUB',
    numberFormat: {
      decimal: ',',
      thousand: ' ',
      precision: 2
    }
  },
  zh: {
    code: 'zh',
    name: 'Chinese',
    nativeName: '中文',
    direction: 'ltr',
    locale: 'zh-CN',
    flag: '🇨🇳',
    dateFormat: 'YYYY/MM/DD',
    currency: 'CNY',
    numberFormat: {
      decimal: '.',
      thousand: ',',
      precision: 2
    }
  },
  ja: {
    code: 'ja',
    name: 'Japanese',
    nativeName: '日本語',
    direction: 'ltr',
    locale: 'ja-JP',
    flag: '🇯🇵',
    dateFormat: 'YYYY/MM/DD',
    currency: 'JPY',
    numberFormat: {
      decimal: '.',
      thousand: ',',
      precision: 0
    }
  }
};

export const RTL_LANGUAGES = ['ar', 'he'];

export const DEFAULT_LANGUAGE = 'en';

export const LANGUAGE_STORAGE_KEY = 'bdc_user_language';

export const TRANSLATION_NAMESPACES = [
'common',
'navigation',
'auth',
'dashboard',
'beneficiaries',
'programs',
'evaluations',
'calendar',
'documents',
'reports',
'settings',
'profile',
'errors',
'success',
'validation',
'portal',
'admin',
'analytics',
'notifications',
'messaging',
'integration'];


export const DATE_FORMATS = {
  short: 'short',
  medium: 'medium',
  long: 'long',
  full: 'full',
  relative: 'relative'
};

export const NUMBER_FORMATS = {
  decimal: 'decimal',
  currency: 'currency',
  percent: 'percent',
  scientific: 'scientific'
};

export const PLURALIZATION_RULES = {
  en: {
    zero: 'zero',
    one: 'one',
    other: 'other'
  },
  ar: {
    zero: 'zero',
    one: 'one',
    two: 'two',
    few: 'few',
    many: 'many',
    other: 'other'
  },
  ru: {
    one: 'one',
    few: 'few',
    many: 'many',
    other: 'other'
  },
  fr: {
    one: 'one',
    other: 'other'
  },
  es: {
    one: 'one',
    other: 'other'
  },
  de: {
    one: 'one',
    other: 'other'
  },
  tr: {
    one: 'one',
    other: 'other'
  },
  he: {
    one: 'one',
    two: 'two',
    many: 'many',
    other: 'other'
  },
  zh: {
    other: 'other'
  },
  ja: {
    other: 'other'
  }
};

export const INTERPOLATION_OPTIONS = {
  escapeValue: false,
  formatSeparator: ',',
  keySeparator: '.',
  nsSeparator: ':',
  prefix: '{{',
  suffix: '}}',
  unescapePrefix: '-',
  unescapeSuffix: '',
  nestingPrefix: '$t(',
  nestingSuffix: ')',
  nestingOptionsSeparator: ',',
  maxReplaces: 1000
};