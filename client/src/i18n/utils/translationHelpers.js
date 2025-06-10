/**
 * Translation helper utilities for BDC i18n implementation
 */

import i18n from '../config';

/**
 * Get nested translation value
 * @param {string} key - Translation key (dot notation)
 * @param {Object} options - Translation options
 * @returns {string} Translated string
 */
export const t = (key, options = {}) => {
  return i18n.t(key, options);
};

/**
 * Check if translation exists
 * @param {string} key - Translation key
 * @param {string} [lng] - Language code (optional)
 * @returns {boolean} True if translation exists
 */
export const hasTranslation = (key, lng) => {
  return i18n.exists(key, { lng });
};

/**
 * Get current language
 * @returns {string} Current language code
 */
export const getCurrentLanguage = () => {
  return i18n.language;
};

/**
 * Change language
 * @param {string} lng - Language code
 * @returns {Promise} Promise that resolves when language is changed
 */
export const changeLanguage = async (lng) => {
  await i18n.changeLanguage(lng);
  // Update localStorage
  localStorage.setItem('bdc_user_language', lng);
  // Update document attributes
  document.documentElement.lang = lng;
  const direction = i18n.dir(lng);
  document.documentElement.dir = direction;
  return lng;
};

/**
 * Get language direction
 * @param {string} [lng] - Language code (optional)
 * @returns {string} 'ltr' or 'rtl'
 */
export const getLanguageDirection = (lng) => {
  return i18n.dir(lng || i18n.language);
};

/**
 * Format number according to current locale
 * @param {number} value - Number to format
 * @param {Object} options - Intl.NumberFormat options
 * @returns {string} Formatted number
 */
export const formatNumber = (value, options = {}) => {
  const locale = i18n.language;
  return new Intl.NumberFormat(locale, options).format(value);
};

/**
 * Format currency according to current locale
 * @param {number} value - Amount to format
 * @param {string} currency - Currency code (e.g., 'USD', 'EUR')
 * @param {Object} options - Additional Intl.NumberFormat options
 * @returns {string} Formatted currency
 */
export const formatCurrency = (value, currency = 'USD', options = {}) => {
  const locale = i18n.language;
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    ...options
  }).format(value);
};

/**
 * Format date according to current locale
 * @param {Date|string|number} date - Date to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date
 */
export const formatDate = (date, options = {}) => {
  const locale = i18n.language;
  const dateObj = date instanceof Date ? date : new Date(date);
  return new Intl.DateTimeFormat(locale, options).format(dateObj);
};

/**
 * Format time according to current locale
 * @param {Date|string|number} time - Time to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted time
 */
export const formatTime = (time, options = {}) => {
  return formatDate(time, {
    hour: 'numeric',
    minute: 'numeric',
    ...options
  });
};

/**
 * Format date and time according to current locale
 * @param {Date|string|number} dateTime - Date and time to format
 * @param {Object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date and time
 */
export const formatDateTime = (dateTime, options = {}) => {
  return formatDate(dateTime, {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    ...options
  });
};

/**
 * Format relative time (e.g., "2 hours ago", "in 3 days")
 * @param {Date|string|number} date - Date to compare
 * @param {Date} [baseDate] - Base date (defaults to now)
 * @returns {string} Relative time string
 */
export const formatRelativeTime = (date, baseDate = new Date()) => {
  const dateObj = date instanceof Date ? date : new Date(date);
  const diffInMs = dateObj.getTime() - baseDate.getTime();
  const diffInSeconds = Math.round(diffInMs / 1000);
  const diffInMinutes = Math.round(diffInSeconds / 60);
  const diffInHours = Math.round(diffInMinutes / 60);
  const diffInDays = Math.round(diffInHours / 24);
  const diffInWeeks = Math.round(diffInDays / 7);
  const diffInMonths = Math.round(diffInDays / 30);
  const diffInYears = Math.round(diffInDays / 365);

  const isFuture = diffInMs > 0;
  const abs = Math.abs;

  if (abs(diffInSeconds) < 60) {
    return t('dateTime.relative.justNow');
  } else if (abs(diffInMinutes) < 60) {
    const key = isFuture ? 'dateTime.relative.inMinutes' : 'dateTime.relative.minutesAgo';
    return t(key, { count: abs(diffInMinutes) });
  } else if (abs(diffInHours) < 24) {
    const key = isFuture ? 'dateTime.relative.inHours' : 'dateTime.relative.hoursAgo';
    return t(key, { count: abs(diffInHours) });
  } else if (abs(diffInDays) < 7) {
    const key = isFuture ? 'dateTime.relative.inDays' : 'dateTime.relative.daysAgo';
    return t(key, { count: abs(diffInDays) });
  } else if (abs(diffInWeeks) < 4) {
    const key = isFuture ? 'dateTime.relative.inWeeks' : 'dateTime.relative.weeksAgo';
    return t(key, { count: abs(diffInWeeks) });
  } else if (abs(diffInMonths) < 12) {
    const key = isFuture ? 'dateTime.relative.inMonths' : 'dateTime.relative.monthsAgo';
    return t(key, { count: abs(diffInMonths) });
  } else {
    const key = isFuture ? 'dateTime.relative.inYears' : 'dateTime.relative.yearsAgo';
    return t(key, { count: abs(diffInYears) });
  }
};

/**
 * Get plural form
 * @param {string} key - Translation key
 * @param {number} count - Count for pluralization
 * @param {Object} options - Additional options
 * @returns {string} Pluralized translation
 */
export const plural = (key, count, options = {}) => {
  return t(key, { count, ...options });
};

/**
 * Get all available languages
 * @returns {Array} Array of language objects
 */
export const getAvailableLanguages = () => {
  const languages = i18n.options.supportedLngs || [];
  return languages
    .filter(lng => lng !== 'cimode') // Filter out test language
    .map(lng => ({
      code: lng,
      name: t(`languages.${lng}`, { lng, defaultValue: lng }),
      nativeName: getNativeLanguageName(lng),
      direction: getLanguageDirection(lng)
    }));
};

/**
 * Get native language name
 * @param {string} lng - Language code
 * @returns {string} Native language name
 */
const getNativeLanguageName = (lng) => {
  const nativeNames = {
    en: 'English',
    tr: 'Türkçe',
    ar: 'العربية',
    es: 'Español',
    fr: 'Français',
    de: 'Deutsch',
    ru: 'Русский',
    he: 'עברית'
  };
  return nativeNames[lng] || lng;
};

/**
 * Interpolate translation with variables
 * @param {string} key - Translation key
 * @param {Object} variables - Variables to interpolate
 * @returns {string} Interpolated translation
 */
export const interpolate = (key, variables = {}) => {
  return t(key, variables);
};

/**
 * Get translation with fallback
 * @param {string} key - Translation key
 * @param {string} fallback - Fallback text
 * @param {Object} options - Translation options
 * @returns {string} Translation or fallback
 */
export const tWithFallback = (key, fallback, options = {}) => {
  return hasTranslation(key) ? t(key, options) : fallback;
};

/**
 * Get namespaced translation helper
 * @param {string} namespace - Namespace prefix
 * @returns {Function} Translation function with namespace
 */
export const getNamespacedT = (namespace) => {
  return (key, options) => t(`${namespace}.${key}`, options);
};

/**
 * Format list according to current locale
 * @param {Array} items - List items
 * @param {Object} options - Intl.ListFormat options
 * @returns {string} Formatted list
 */
export const formatList = (items, options = {}) => {
  const locale = i18n.language;
  
  // Fallback for browsers that don't support Intl.ListFormat
  if (!Intl.ListFormat) {
    return items.join(', ');
  }
  
  return new Intl.ListFormat(locale, {
    style: 'long',
    type: 'conjunction',
    ...options
  }).format(items);
};

/**
 * Get date format pattern for current locale
 * @param {string} format - Format type ('short', 'medium', 'long', 'full')
 * @returns {string} Date format pattern
 */
export const getDateFormatPattern = (format = 'medium') => {
  return t(`dateTime.formats.${format}`, { defaultValue: 'MM/DD/YYYY' });
};

/**
 * Check if current language is RTL
 * @returns {boolean} True if RTL
 */
export const isRTL = () => {
  return getLanguageDirection() === 'rtl';
};

/**
 * Get text alignment based on language direction
 * @param {string} [start='left'] - Start alignment
 * @param {string} [end='right'] - End alignment
 * @returns {string} Appropriate alignment
 */
export const getTextAlign = (start = 'left', end = 'right') => {
  return isRTL() ? end : start;
};

/**
 * Get margin/padding direction based on language
 * @param {string} property - CSS property (e.g., 'margin', 'padding')
 * @param {string} [start='Left'] - Start direction
 * @param {string} [end='Right'] - End direction
 * @returns {string} CSS property with direction
 */
export const getDirectionalProperty = (property, start = 'Left', end = 'Right') => {
  const direction = isRTL() ? end : start;
  return `${property}${direction}`;
};

/**
 * Export translation utilities as default
 */
export default {
  t,
  hasTranslation,
  getCurrentLanguage,
  changeLanguage,
  getLanguageDirection,
  formatNumber,
  formatCurrency,
  formatDate,
  formatTime,
  formatDateTime,
  formatRelativeTime,
  plural,
  getAvailableLanguages,
  interpolate,
  tWithFallback,
  getNamespacedT,
  formatList,
  getDateFormatPattern,
  isRTL,
  getTextAlign,
  getDirectionalProperty
};