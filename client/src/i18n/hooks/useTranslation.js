/**
 * Enhanced useTranslation hook for BDC application
 * Provides translation functionality with additional utilities
 */

import { useTranslation as useI18nTranslation } from 'react-i18next';
import { useCallback, useMemo } from 'react';
import {
  formatNumber,
  formatCurrency,
  formatDate,
  formatTime,
  formatDateTime,
  formatRelativeTime,
  formatList,
  getTextAlign,
  getDirectionalProperty,
  isRTL as checkIsRTL
} from '../utils/translationHelpers';

/**
 * Enhanced translation hook with utilities
 * @param {string} [namespace] - Optional namespace
 * @returns {Object} Translation functions and utilities
 */
export const useTranslation = (namespace) => {
  const { t, i18n, ready } = useI18nTranslation(namespace);

  // Memoize language info
  const languageInfo = useMemo(() => ({
    language: i18n.language,
    isRTL: checkIsRTL(),
    direction: i18n.dir(),
  }), [i18n.language]);

  // Enhanced translation function with fallback
  const translate = useCallback((key, options = {}) => {
    const { fallback, ...translationOptions } = options;
    const translation = t(key, translationOptions);
    
    // Return fallback if translation is the same as key (not found)
    if (fallback && translation === key) {
      return fallback;
    }
    
    return translation;
  }, [t]);

  // Change language with side effects
  const changeLanguage = useCallback(async (lng) => {
    await i18n.changeLanguage(lng);
    // Update localStorage
    localStorage.setItem('bdc_user_language', lng);
    // Update document attributes
    document.documentElement.lang = lng;
    document.documentElement.dir = i18n.dir(lng);
  }, [i18n]);

  // Get available languages
  const getLanguages = useCallback(() => {
    const supportedLngs = i18n.options.supportedLngs || [];
    return supportedLngs
      .filter(lng => lng !== 'cimode')
      .map(lng => ({
        code: lng,
        name: t(`languages.${lng}`, { lng, defaultValue: lng }),
        nativeName: getNativeLanguageName(lng),
        direction: i18n.dir(lng),
        active: lng === i18n.language
      }));
  }, [i18n, t]);

  // Format utilities bound to current language
  const format = useMemo(() => ({
    number: (value, options) => formatNumber(value, options),
    currency: (value, currency, options) => formatCurrency(value, currency, options),
    date: (date, options) => formatDate(date, options),
    time: (time, options) => formatTime(time, options),
    dateTime: (dateTime, options) => formatDateTime(dateTime, options),
    relativeTime: (date, baseDate) => formatRelativeTime(date, baseDate),
    list: (items, options) => formatList(items, options),
  }), []);

  // Style utilities for RTL support
  const style = useMemo(() => ({
    textAlign: (start, end) => getTextAlign(start, end),
    margin: (value, direction = 'horizontal') => {
      if (direction === 'horizontal') {
        return {
          marginLeft: languageInfo.isRTL ? 0 : value,
          marginRight: languageInfo.isRTL ? value : 0,
        };
      }
      return { margin: value };
    },
    padding: (value, direction = 'horizontal') => {
      if (direction === 'horizontal') {
        return {
          paddingLeft: languageInfo.isRTL ? 0 : value,
          paddingRight: languageInfo.isRTL ? value : 0,
        };
      }
      return { padding: value };
    },
    direction: (start, end) => languageInfo.isRTL ? end : start,
  }), [languageInfo.isRTL]);

  // Validation message helpers
  const validation = useMemo(() => ({
    required: (field) => t('form.validation.required', { field }),
    minLength: (field, min) => t('form.validation.minLength', { field, min }),
    maxLength: (field, max) => t('form.validation.maxLength', { field, max }),
    email: () => t('form.validation.email'),
    number: () => t('form.validation.number'),
    phone: () => t('form.validation.phone'),
    url: () => t('form.validation.url'),
    date: () => t('form.validation.date'),
    pattern: (pattern) => t('form.validation.pattern', { pattern }),
    min: (min) => t('form.validation.min', { min }),
    max: (max) => t('form.validation.max', { max }),
  }), [t]);

  // Common UI text helpers
  const ui = useMemo(() => ({
    // Buttons
    save: () => t('common.save'),
    cancel: () => t('common.cancel'),
    delete: () => t('common.delete'),
    edit: () => t('common.edit'),
    add: () => t('common.add'),
    update: () => t('common.update'),
    submit: () => t('common.submit'),
    close: () => t('common.close'),
    back: () => t('common.back'),
    next: () => t('common.next'),
    
    // Messages
    loading: () => t('common.loading'),
    noData: () => t('common.noData'),
    error: (message) => message || t('common.error'),
    success: (message) => message || t('common.success'),
    confirm: (message) => message || t('messages.confirm.general'),
    
    // Pagination
    page: (current, total) => t('pagination.page', { current, total }),
    showing: (start, end, total) => t('pagination.showing', { start, end, total }),
    
    // Search
    search: () => t('common.search'),
    searchPlaceholder: () => t('placeholders.search'),
    noResults: (query) => t('search.noResults', { query }),
  }), [t]);

  return {
    // Core translation function
    t: translate,
    
    // Language management
    i18n,
    ready,
    language: languageInfo.language,
    isRTL: languageInfo.isRTL,
    direction: languageInfo.direction,
    changeLanguage,
    getLanguages,
    
    // Formatting utilities
    format,
    
    // Style utilities
    style,
    
    // Validation helpers
    validation,
    
    // Common UI text
    ui,
  };
};

// Helper function to get native language names
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

export default useTranslation;