// TODO: i18n - processed
/**
 * i18n Utility Functions
 * Helper functions for internationalization
 */

import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE } from '../constants';

/**
 * Detect user's preferred language
 */import { useTranslation } from "react-i18next";
export const detectUserLanguage = async () => {
  // Check browser language
  const browserLang = navigator.language || navigator.userLanguage;
  const primaryLang = browserLang.split('-')[0];

  // Check if browser language is supported
  if (SUPPORTED_LANGUAGES[primaryLang]) {
    return primaryLang;
  }

  // Check for full locale match
  const fullLocaleMatch = Object.values(SUPPORTED_LANGUAGES).find(
    (lang) => lang.locale === browserLang
  );

  if (fullLocaleMatch) {
    return fullLocaleMatch.code;
  }

  // Try to detect from timezone
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const countryLanguageMap = {
    'Europe/Paris': 'fr',
    'Europe/Madrid': 'es',
    'Europe/Berlin': 'de',
    'Europe/Moscow': 'ru',
    'Asia/Istanbul': 'tr',
    'Asia/Jerusalem': 'he',
    'Asia/Riyadh': 'ar',
    'Asia/Shanghai': 'zh',
    'Asia/Tokyo': 'ja'
  };

  for (const [tz, lang] of Object.entries(countryLanguageMap)) {
    if (timezone.includes(tz.split('/')[0])) {
      return lang;
    }
  }

  // Default fallback
  return DEFAULT_LANGUAGE;
};

/**
 * Load language resources dynamically
 */
export const loadLanguageResources = async (language) => {
  try {
    // Dynamic import of language resources
    const module = await import(`../locales/${language}.json`);
    return module.default;
  } catch (error) {
    console.error(`Failed to load language resources for ${language}:`, error);
    // Fallback to English
    if (language !== DEFAULT_LANGUAGE) {
      const fallbackModule = await import(`../locales/${DEFAULT_LANGUAGE}.json`);
      return fallbackModule.default;
    }
    throw error;
  }
};

/**
 * Format language display name
 */
export const formatLanguageName = (code, displayIn = 'native') => {
  const language = SUPPORTED_LANGUAGES[code];
  if (!language) return code;

  switch (displayIn) {
    case 'native':
      return language.nativeName;
    case 'english':
      return language.name;
    case 'both':
      return `${language.nativeName} (${language.name})`;
    case 'withFlag':
      return `${language.flag} ${language.nativeName}`;
    default:
      return language.nativeName;
  }
};

/**
 * Get language direction for CSS
 */
export const getLanguageDirection = (code) => {
  return SUPPORTED_LANGUAGES[code]?.direction || 'ltr';
};

/**
 * Check if language is RTL
 */
export const isRTLLanguage = (code) => {
  return getLanguageDirection(code) === 'rtl';
};

/**
 * Get opposite direction
 */
export const getOppositeDirection = (direction) => {
  return direction === 'ltr' ? 'rtl' : 'ltr';
};

/**
 * Convert LTR styles to RTL
 */
export const convertToRTL = (styles) => {
  if (!styles || typeof styles !== 'object') return styles;

  const rtlStyles = { ...styles };
  const conversions = {
    left: 'right',
    right: 'left',
    marginLeft: 'marginRight',
    marginRight: 'marginLeft',
    paddingLeft: 'paddingRight',
    paddingRight: 'paddingLeft',
    borderLeft: 'borderRight',
    borderRight: 'borderLeft',
    borderLeftWidth: 'borderRightWidth',
    borderRightWidth: 'borderLeftWidth',
    borderLeftColor: 'borderRightColor',
    borderRightColor: 'borderLeftColor',
    borderLeftStyle: 'borderRightStyle',
    borderRightStyle: 'borderLeftStyle',
    borderTopLeftRadius: 'borderTopRightRadius',
    borderTopRightRadius: 'borderTopLeftRadius',
    borderBottomLeftRadius: 'borderBottomRightRadius',
    borderBottomRightRadius: 'borderBottomLeftRadius'
  };

  for (const [ltrProp, rtlProp] of Object.entries(conversions)) {
    if (ltrProp in rtlStyles) {
      const temp = rtlStyles[ltrProp];
      rtlStyles[rtlProp] = rtlStyles[rtlProp] || temp;
      rtlStyles[ltrProp] = rtlStyles[rtlProp];
      rtlStyles[rtlProp] = temp;
    }
  }

  // Handle text alignment
  if ('textAlign' in rtlStyles) {
    if (rtlStyles.textAlign === 'left') {
      rtlStyles.textAlign = 'right';
    } else if (rtlStyles.textAlign === 'right') {
      rtlStyles.textAlign = 'left';
    }
  }

  // Handle transform
  if ('transform' in rtlStyles && rtlStyles.transform.includes('translateX')) {
    rtlStyles.transform = rtlStyles.transform.replace(
      /translateX\(([-\d.]+)([a-z%]*)\)/g,
      (match, value, unit) => `translateX(${-parseFloat(value)}${unit})`
    );
  }

  return rtlStyles;
};

/**
 * Parse accept-language header
 */
export const parseAcceptLanguage = (acceptLanguageHeader) => {
  if (!acceptLanguageHeader) return [];

  // Parse the header and sort by quality value
  const languages = acceptLanguageHeader.
  split(',').
  map((lang) => {
    const [code, q = 'q=1.0'] = lang.trim().split(';');
    const quality = parseFloat(q.replace('q=', ''));
    return { code: code.toLowerCase(), quality };
  }).
  sort((a, b) => b.quality - a.quality).
  map(({ code }) => code);

  // Find supported languages
  const supportedLanguages = languages.
  map((code) => {
    // Try exact match
    if (SUPPORTED_LANGUAGES[code]) return code;

    // Try primary language (before hyphen)
    const primary = code.split('-')[0];
    if (SUPPORTED_LANGUAGES[primary]) return primary;

    return null;
  }).
  filter(Boolean);

  return supportedLanguages;
};

/**
 * Get text direction for mixed content
 */
export const getTextDirection = (text) => {
  if (!text) return 'ltr';

  // Check for RTL characters
  const rtlChars = /[\u0591-\u07FF\u200F\u202B\u202E\uFB1D-\uFDFD\uFE70-\uFEFC]/;
  const ltrChars = /[A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02B8\u0300-\u0590\u0800-\u1FFF\u2C00-\uFB1C\uFDFE-\uFE6F\uFEFD-\uFFFF]/;

  const rtlCount = (text.match(rtlChars) || []).length;
  const ltrCount = (text.match(ltrChars) || []).length;

  return rtlCount > ltrCount ? 'rtl' : 'ltr';
};

/**
 * Format number according to language
 */
export const formatNumberByLanguage = (number, language) => {
  const locale = SUPPORTED_LANGUAGES[language]?.locale || 'en-US';
  return new Intl.NumberFormat(locale).format(number);
};

/**
 * Format date according to language
 */
export const formatDateByLanguage = (date, language, options = {}) => {
  const locale = SUPPORTED_LANGUAGES[language]?.locale || 'en-US';
  return new Intl.DateTimeFormat(locale, options).format(new Date(date));
};

/**
 * Get plural rules for language
 */
export const getPluralRules = (language) => {
  const locale = SUPPORTED_LANGUAGES[language]?.locale || 'en-US';
  return new Intl.PluralRules(locale);
};

/**
 * Select plural form
 */
export const selectPluralForm = (count, forms, language) => {
  const pluralRules = getPluralRules(language);
  const rule = pluralRules.select(count);
  return forms[rule] || forms.other || forms[Object.keys(forms)[0]];
};

/**
 * Interpolate translation string
 */
export const interpolate = (template, values = {}) => {
  return template.replace(/{{([^}]+)}}/g, (match, key) => {
    const keys = key.trim().split('.');
    let value = values;

    for (const k of keys) {
      value = value?.[k];
    }

    return value !== undefined ? value : match;
  });
};

/**
 * Deep merge translation objects
 */
export const mergeTranslations = (target, source) => {
  const result = { ...target };

  for (const key in source) {
    if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
      result[key] = mergeTranslations(result[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }

  return result;
};

/**
 * Extract translation keys from component
 */
export const extractTranslationKeys = (componentString) => {
  const patterns = [
  /t\(['"`]([^'"`]+)['"`]/g,
  /i18n\.t\(['"`]([^'"`]+)['"`]/g,
  /translation:\s*['"`]([^'"`]+)['"`]/g];


  const keys = new Set();

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(componentString)) !== null) {
      keys.add(match[1]);
    }
  }

  return Array.from(keys);
};

/**
 * Generate translation key from text
 */
export const generateTranslationKey = (text, namespace = 'common') => {
  const key = text.
  toLowerCase().
  replace(/[^a-z0-9\s]/g, '').
  replace(/\s+/g, '_').
  substring(0, 50);

  return `${namespace}.${key}`;
};

/**
 * Check if translation key exists
 */
export const translationExists = (key, translations) => {
  const keys = key.split('.');
  let current = translations;

  for (const k of keys) {
    if (!current || !(k in current)) {
      return false;
    }
    current = current[k];
  }

  return true;
};

/**
 * Get nested translation value
 */
export const getNestedTranslation = (translations, key, fallback = null) => {
  const keys = key.split('.');
  let current = translations;

  for (const k of keys) {
    if (!current || !(k in current)) {
      return fallback;
    }
    current = current[k];
  }

  return current;
};

/**
 * Flatten translations object
 */
export const flattenTranslations = (translations, prefix = '') => {
  const flattened = {};

  for (const key in translations) {
    const fullKey = prefix ? `${prefix}.${key}` : key;

    if (typeof translations[key] === 'object' && translations[key] !== null) {
      Object.assign(flattened, flattenTranslations(translations[key], fullKey));
    } else {
      flattened[fullKey] = translations[key];
    }
  }

  return flattened;
};

/**
 * Unflatten translations object
 */
export const unflattenTranslations = (flattened) => {
  const result = {};

  for (const key in flattened) {
    const keys = key.split('.');
    let current = result;

    for (let i = 0; i < keys.length - 1; i++) {
      if (!(keys[i] in current)) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }

    current[keys[keys.length - 1]] = flattened[key];
  }

  return result;
};