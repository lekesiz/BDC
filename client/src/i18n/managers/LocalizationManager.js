// TODO: i18n - processed
/**
 * Localization Manager
 * Handles date, time, number, and currency formatting based on locale
 */

import { SUPPORTED_LANGUAGES, DATE_FORMATS, NUMBER_FORMATS } from '../constants';import { useTranslation } from "react-i18next";

class LocalizationManager {
  constructor() {
    this.formatters = new Map();
    this.currentLocale = 'en-US';
  }

  /**
   * Set current locale
   */
  setLocale(languageCode) {
    const language = SUPPORTED_LANGUAGES[languageCode];
    if (language) {
      this.currentLocale = language.locale;
      this.clearFormatters();
    }
  }

  /**
   * Get or create formatter
   */
  getFormatter(type, options = {}) {
    const key = `${type}:${JSON.stringify(options)}`;

    if (!this.formatters.has(key)) {
      let formatter;

      switch (type) {
        case 'dateTime':
          formatter = new Intl.DateTimeFormat(this.currentLocale, options);
          break;
        case 'number':
          formatter = new Intl.NumberFormat(this.currentLocale, options);
          break;
        case 'relativeTime':
          formatter = new Intl.RelativeTimeFormat(this.currentLocale, options);
          break;
        case 'list':
          formatter = new Intl.ListFormat(this.currentLocale, options);
          break;
        case 'plural':
          formatter = new Intl.PluralRules(this.currentLocale, options);
          break;
        default:
          throw new Error(`Unknown formatter type: ${type}`);
      }

      this.formatters.set(key, formatter);
    }

    return this.formatters.get(key);
  }

  /**
   * Clear all cached formatters
   */
  clearFormatters() {
    this.formatters.clear();
  }

  /**
   * Format date
   */
  formatDate(date, format = DATE_FORMATS.medium) {
    if (!date) return '';

    const dateObj = date instanceof Date ? date : new Date(date);

    if (isNaN(dateObj.getTime())) {
      console.error('Invalid date:', date);
      return '';
    }

    // Handle relative time format
    if (format === DATE_FORMATS.relative) {
      return this.formatRelativeTime(dateObj);
    }

    // Get format options based on format type
    const options = this.getDateFormatOptions(format);
    const formatter = this.getFormatter('dateTime', options);

    return formatter.format(dateObj);
  }

  /**
   * Get date format options
   */
  getDateFormatOptions(format) {
    switch (format) {
      case DATE_FORMATS.short:
        return {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        };
      case DATE_FORMATS.medium:
        return {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        };
      case DATE_FORMATS.long:
        return {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        };
      case DATE_FORMATS.full:
        return {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        };
      default:
        return format; // Allow custom options
    }
  }

  /**
   * Format time
   */
  formatTime(date, options = {}) {
    if (!date) return '';

    const dateObj = date instanceof Date ? date : new Date(date);

    if (isNaN(dateObj.getTime())) {
      console.error('Invalid date:', date);
      return '';
    }

    const defaultOptions = {
      hour: '2-digit',
      minute: '2-digit'
    };

    const formatter = this.getFormatter('dateTime', { ...defaultOptions, ...options });
    return formatter.format(dateObj);
  }

  /**
   * Format date and time
   */
  formatDateTime(date, dateFormat = DATE_FORMATS.medium, timeOptions = {}) {
    if (!date) return '';

    const dateObj = date instanceof Date ? date : new Date(date);

    if (isNaN(dateObj.getTime())) {
      console.error('Invalid date:', date);
      return '';
    }

    const dateOptions = this.getDateFormatOptions(dateFormat);
    const combinedOptions = {
      ...dateOptions,
      hour: '2-digit',
      minute: '2-digit',
      ...timeOptions
    };

    const formatter = this.getFormatter('dateTime', combinedOptions);
    return formatter.format(dateObj);
  }

  /**
   * Format relative time
   */
  formatRelativeTime(date, baseDate = new Date()) {
    if (!date) return '';

    const dateObj = date instanceof Date ? date : new Date(date);
    const baseDateObj = baseDate instanceof Date ? baseDate : new Date(baseDate);

    if (isNaN(dateObj.getTime()) || isNaN(baseDateObj.getTime())) {
      console.error('Invalid date:', date, baseDate);
      return '';
    }

    const formatter = this.getFormatter('relativeTime', { numeric: 'auto' });

    // Calculate difference in various units
    const diffMs = dateObj - baseDateObj;
    const diffSecs = Math.round(diffMs / 1000);
    const diffMins = Math.round(diffSecs / 60);
    const diffHours = Math.round(diffMins / 60);
    const diffDays = Math.round(diffHours / 24);
    const diffWeeks = Math.round(diffDays / 7);
    const diffMonths = Math.round(diffDays / 30);
    const diffYears = Math.round(diffDays / 365);

    // Choose appropriate unit
    if (Math.abs(diffSecs) < 60) {
      return formatter.format(diffSecs, 'second');
    } else if (Math.abs(diffMins) < 60) {
      return formatter.format(diffMins, 'minute');
    } else if (Math.abs(diffHours) < 24) {
      return formatter.format(diffHours, 'hour');
    } else if (Math.abs(diffDays) < 7) {
      return formatter.format(diffDays, 'day');
    } else if (Math.abs(diffWeeks) < 4) {
      return formatter.format(diffWeeks, 'week');
    } else if (Math.abs(diffMonths) < 12) {
      return formatter.format(diffMonths, 'month');
    } else {
      return formatter.format(diffYears, 'year');
    }
  }

  /**
   * Format number
   */
  formatNumber(number, format = NUMBER_FORMATS.decimal, options = {}) {
    if (number === null || number === undefined) return '';

    const numValue = typeof number === 'string' ? parseFloat(number) : number;

    if (isNaN(numValue)) {
      console.error('Invalid number:', number);
      return '';
    }

    let formatOptions = { ...options };

    switch (format) {
      case NUMBER_FORMATS.decimal:
        // Use default options
        break;
      case NUMBER_FORMATS.percent:
        formatOptions = {
          style: 'percent',
          minimumFractionDigits: 0,
          maximumFractionDigits: 2,
          ...options
        };
        break;
      case NUMBER_FORMATS.scientific:
        formatOptions = {
          notation: 'scientific',
          ...options
        };
        break;
      default:
        // Allow custom format
        break;
    }

    const formatter = this.getFormatter('number', formatOptions);
    return formatter.format(numValue);
  }

  /**
   * Format currency
   */
  formatCurrency(amount, currency = null, options = {}) {
    if (amount === null || amount === undefined) return '';

    const numValue = typeof amount === 'string' ? parseFloat(amount) : amount;

    if (isNaN(numValue)) {
      console.error('Invalid amount:', amount);
      return '';
    }

    // Get currency from current language if not provided
    if (!currency) {
      const languageCode = this.currentLocale.split('-')[0];
      const language = Object.values(SUPPORTED_LANGUAGES).find(
        (lang) => lang.locale === this.currentLocale
      );
      currency = language?.currency || 'USD';
    }

    const formatOptions = {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
      ...options
    };

    const formatter = this.getFormatter('number', formatOptions);
    return formatter.format(numValue);
  }

  /**
   * Format list
   */
  formatList(items, type = 'conjunction', style = 'long') {
    if (!Array.isArray(items) || items.length === 0) return '';

    const formatter = this.getFormatter('list', { type, style });
    return formatter.format(items);
  }

  /**
   * Get plural form
   */
  getPluralForm(count, options = {}) {
    const formatter = this.getFormatter('plural', options);
    return formatter.select(count);
  }

  /**
   * Format file size
   */
  formatFileSize(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const size = parseFloat((bytes / Math.pow(k, i)).toFixed(dm));

    return `${this.formatNumber(size)} ${sizes[i]}`;
  }

  /**
   * Format duration
   */
  formatDuration(seconds, options = {}) {
    const {
      format = 'long', // 'short', 'long', 'narrow'
      units = ['hour', 'minute', 'second']
    } = options;

    const parts = [];
    let remainingSeconds = Math.abs(seconds);

    const unitValues = {
      year: 365 * 24 * 60 * 60,
      month: 30 * 24 * 60 * 60,
      week: 7 * 24 * 60 * 60,
      day: 24 * 60 * 60,
      hour: 60 * 60,
      minute: 60,
      second: 1
    };

    for (const unit of units) {
      if (unitValues[unit] && remainingSeconds >= unitValues[unit]) {
        const value = Math.floor(remainingSeconds / unitValues[unit]);
        remainingSeconds %= unitValues[unit];

        if (value > 0) {
          const formatter = this.getFormatter('relativeTime', {
            numeric: 'always',
            style: format
          });

          // Format without the relative part
          const formatted = formatter.format(value, unit).replace(/^in |ago$/, '').trim();
          parts.push(formatted);
        }
      }
    }

    return parts.join(', ') || '0 seconds';
  }

  /**
   * Format phone number
   */
  formatPhoneNumber(phoneNumber, countryCode = 'US') {
    // Simple formatter - can be enhanced with libphonenumber-js
    const cleaned = phoneNumber.replace(/\D/g, '');

    if (countryCode === 'US' && cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    }

    return phoneNumber;
  }

  /**
   * Parse localized number
   */
  parseNumber(localizedNumber) {
    if (!localizedNumber) return NaN;

    // Get number format info for current locale
    const formatter = this.getFormatter('number');
    const parts = formatter.formatToParts(1234.5);

    let decimal = '.';
    let group = ',';

    for (const part of parts) {
      if (part.type === 'decimal') decimal = part.value;
      if (part.type === 'group') group = part.value;
    }

    // Remove grouping separators and replace decimal separator
    const normalized = localizedNumber.
    replace(new RegExp(`\\${group}`, 'g'), '').
    replace(new RegExp(`\\${decimal}`), '.');

    return parseFloat(normalized);
  }

  /**
   * Get calendar info
   */
  getCalendarInfo() {
    const now = new Date();
    const formatter = this.getFormatter('dateTime', { weekday: 'long' });

    // Get weekday names
    const weekdays = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(2024, 0, i + 7); // January 7-13, 2024 (Sunday-Saturday)
      weekdays.push(formatter.format(date));
    }

    // Get month names
    const monthFormatter = this.getFormatter('dateTime', { month: 'long' });
    const months = [];
    for (let i = 0; i < 12; i++) {
      const date = new Date(2024, i, 1);
      months.push(monthFormatter.format(date));
    }

    return {
      weekdays,
      months,
      firstDayOfWeek: this.getFirstDayOfWeek(),
      weekendDays: this.getWeekendDays()
    };
  }

  /**
   * Get first day of week for locale
   */
  getFirstDayOfWeek() {
    // This is a simplified version - in production, use a proper locale data library
    const locale = this.currentLocale.split('-')[1];
    const sundayFirst = ['US', 'CA', 'JP', 'KR', 'TW', 'HK', 'MO', 'PH'];

    return sundayFirst.includes(locale) ? 0 : 1; // 0 = Sunday, 1 = Monday
  }

  /**
   * Get weekend days for locale
   */
  getWeekendDays() {
    // Simplified version
    const locale = this.currentLocale.split('-')[1];
    const fridaySaturday = ['AE', 'BH', 'DZ', 'EG', 'IQ', 'JO', 'KW', 'LY', 'OM', 'QA', 'SA', 'SD', 'SY', 'YE'];

    if (fridaySaturday.includes(locale)) {
      return [5, 6]; // Friday, Saturday
    }

    return [0, 6]; // Sunday, Saturday
  }
}

// Create singleton instance
const localizationManager = new LocalizationManager();

export default localizationManager;