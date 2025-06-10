// TODO: i18n - processed
/**
 * useLocalization Hook
 * Access localization functions for dates, numbers, and currency
 */

import { useCallback, useEffect, useMemo } from 'react';
import { useLanguage } from './useLanguage';
import localizationManager from '../managers/LocalizationManager';
import { DATE_FORMATS, NUMBER_FORMATS } from '../constants';import { useTranslation } from "react-i18next";

const useLocalization = () => {
  const { currentLanguage, getLocale } = useLanguage();

  // Update localization manager when language changes
  useEffect(() => {
    localizationManager.setLocale(currentLanguage);
  }, [currentLanguage]);

  // Date formatting
  const formatDate = useCallback((date, format = DATE_FORMATS.medium) => {
    return localizationManager.formatDate(date, format);
  }, []);

  const formatTime = useCallback((date, options = {}) => {
    return localizationManager.formatTime(date, options);
  }, []);

  const formatDateTime = useCallback((date, dateFormat = DATE_FORMATS.medium, timeOptions = {}) => {
    return localizationManager.formatDateTime(date, dateFormat, timeOptions);
  }, []);

  const formatRelativeTime = useCallback((date, baseDate = new Date()) => {
    return localizationManager.formatRelativeTime(date, baseDate);
  }, []);

  // Number formatting
  const formatNumber = useCallback((number, format = NUMBER_FORMATS.decimal, options = {}) => {
    return localizationManager.formatNumber(number, format, options);
  }, []);

  const formatCurrency = useCallback((amount, currency = null, options = {}) => {
    return localizationManager.formatCurrency(amount, currency, options);
  }, []);

  const formatPercent = useCallback((value, options = {}) => {
    return localizationManager.formatNumber(value, NUMBER_FORMATS.percent, options);
  }, []);

  // List formatting
  const formatList = useCallback((items, type = 'conjunction', style = 'long') => {
    return localizationManager.formatList(items, type, style);
  }, []);

  // Plural forms
  const getPluralForm = useCallback((count, options = {}) => {
    return localizationManager.getPluralForm(count, options);
  }, []);

  // File size formatting
  const formatFileSize = useCallback((bytes, decimals = 2) => {
    return localizationManager.formatFileSize(bytes, decimals);
  }, []);

  // Duration formatting
  const formatDuration = useCallback((seconds, options = {}) => {
    return localizationManager.formatDuration(seconds, options);
  }, []);

  // Phone number formatting
  const formatPhoneNumber = useCallback((phoneNumber, countryCode = 'US') => {
    return localizationManager.formatPhoneNumber(phoneNumber, countryCode);
  }, []);

  // Parse localized number
  const parseNumber = useCallback((localizedNumber) => {
    return localizationManager.parseNumber(localizedNumber);
  }, []);

  // Get calendar information
  const getCalendarInfo = useCallback(() => {
    return localizationManager.getCalendarInfo();
  }, []);

  // Date range formatting
  const formatDateRange = useCallback((startDate, endDate, format = DATE_FORMATS.medium) => {
    const start = formatDate(startDate, format);
    const end = formatDate(endDate, format);

    // If same day, show time range
    if (new Date(startDate).toDateString() === new Date(endDate).toDateString()) {
      return `${start} ${formatTime(startDate)} - ${formatTime(endDate)}`;
    }

    return `${start} - ${end}`;
  }, [formatDate, formatTime]);

  // Smart date formatting (today, yesterday, etc.)
  const formatSmartDate = useCallback((date) => {
    const dateObj = date instanceof Date ? date : new Date(date);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (dateObj.toDateString() === today.toDateString()) {
      return `Today, ${formatTime(dateObj)}`;
    } else if (dateObj.toDateString() === yesterday.toDateString()) {
      return `Yesterday, ${formatTime(dateObj)}`;
    } else if (Math.abs(today - dateObj) < 7 * 24 * 60 * 60 * 1000) {
      return formatRelativeTime(dateObj);
    } else {
      return formatDate(dateObj);
    }
  }, [formatDate, formatTime, formatRelativeTime]);

  // Format with locale-specific separators
  const formatWithSeparators = useCallback((value, separator = 'auto') => {
    if (separator === 'auto') {
      return formatNumber(value);
    }

    const parts = value.toString().split('.');
    const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, separator);
    return parts.length > 1 ? `${integerPart}.${parts[1]}` : integerPart;
  }, [formatNumber]);

  // Currency with symbol position
  const formatCurrencyWithPosition = useCallback((amount, currency = null) => {
    const formatted = formatCurrency(amount, currency);
    const locale = getLocale();

    // Some locales put currency symbol after the number
    const symbolAfter = ['fr-FR', 'de-DE', 'es-ES'].includes(locale);

    if (symbolAfter && formatted.match(/^[^0-9]*[0-9]/)) {
      // Move symbol to end if needed
      const match = formatted.match(/^([^0-9]+)(.+)$/);
      if (match) {
        return `${match[2]} ${match[1].trim()}`;
      }
    }

    return formatted;
  }, [formatCurrency, getLocale]);

  // Memoized return value
  const memoizedReturn = useMemo(() => ({
    // Date/Time formatting
    formatDate,
    formatTime,
    formatDateTime,
    formatRelativeTime,
    formatDateRange,
    formatSmartDate,

    // Number formatting
    formatNumber,
    formatCurrency,
    formatPercent,
    formatWithSeparators,
    formatCurrencyWithPosition,

    // Other formatting
    formatList,
    formatFileSize,
    formatDuration,
    formatPhoneNumber,

    // Parsing
    parseNumber,

    // Utilities
    getPluralForm,
    getCalendarInfo,

    // Constants
    DATE_FORMATS,
    NUMBER_FORMATS,

    // Current locale
    locale: getLocale()
  }), [
  formatDate,
  formatTime,
  formatDateTime,
  formatRelativeTime,
  formatDateRange,
  formatSmartDate,
  formatNumber,
  formatCurrency,
  formatPercent,
  formatWithSeparators,
  formatCurrencyWithPosition,
  formatList,
  formatFileSize,
  formatDuration,
  formatPhoneNumber,
  parseNumber,
  getPluralForm,
  getCalendarInfo,
  getLocale]
  );

  return memoizedReturn;
};

export default useLocalization;