// TODO: i18n - processed
/**
 * Translation Manager
 * Handles dynamic translation loading, caching, and management
 */

import i18n from '../config';
import { SUPPORTED_LANGUAGES, TRANSLATION_NAMESPACES } from '../constants';
import api from '../../lib/api';import { useTranslation } from "react-i18next";

class TranslationManager {
  constructor() {
    this.cache = new Map();
    this.pendingRequests = new Map();
    this.listeners = new Set();
    this.missingTranslations = new Map();
  }

  /**
   * Load translations for a specific language and namespace
   */
  async loadTranslations(language, namespace = 'common') {
    const cacheKey = `${language}:${namespace}`;

    // Return cached translations if available
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Return pending request if already loading
    if (this.pendingRequests.has(cacheKey)) {
      return this.pendingRequests.get(cacheKey);
    }

    // Create loading promise
    const loadPromise = this._fetchTranslations(language, namespace);
    this.pendingRequests.set(cacheKey, loadPromise);

    try {
      const translations = await loadPromise;
      this.cache.set(cacheKey, translations);
      this.pendingRequests.delete(cacheKey);

      // Add translations to i18n
      i18n.addResourceBundle(language, namespace, translations, true, true);

      return translations;
    } catch (error) {
      this.pendingRequests.delete(cacheKey);
      throw error;
    }
  }

  /**
   * Fetch translations from server or local files
   */
  async _fetchTranslations(language, namespace) {
    try {
      // Try to fetch from server first
      const response = await api.get(`/i18n/translations/${language}/${namespace}`);
      return response.data;
    } catch (error) {
      // Fallback to local translations
      try {
        const translations = await import(`../locales/${language}.json`);
        return translations.default[namespace] || {};
      } catch (importError) {
        console.error(`Failed to load translations for ${language}:${namespace}`, importError);
        return {};
      }
    }
  }

  /**
   * Load all translations for a language
   */
  async loadLanguage(language) {
    if (!SUPPORTED_LANGUAGES[language]) {
      throw new Error(`Language ${language} is not supported`);
    }

    const namespacePromises = TRANSLATION_NAMESPACES.map((namespace) =>
    this.loadTranslations(language, namespace)
    );

    await Promise.all(namespacePromises);
    this.notifyListeners('languageLoaded', { language });
  }

  /**
   * Preload translations for multiple languages
   */
  async preloadLanguages(languages = []) {
    const preloadPromises = languages.map((language) => this.loadLanguage(language));
    await Promise.all(preloadPromises);
  }

  /**
   * Clear translation cache
   */
  clearCache(language = null, namespace = null) {
    if (language && namespace) {
      this.cache.delete(`${language}:${namespace}`);
    } else if (language) {
      // Clear all namespaces for a language
      for (const key of this.cache.keys()) {
        if (key.startsWith(`${language}:`)) {
          this.cache.delete(key);
        }
      }
    } else {
      // Clear entire cache
      this.cache.clear();
    }
  }

  /**
   * Get translation with fallback
   */
  getTranslation(key, language, namespace = 'common', fallback = null) {
    const translation = i18n.t(`${namespace}:${key}`, { lng: language });

    if (translation === `${namespace}:${key}`) {
      // Translation not found, track it
      this.trackMissingTranslation(key, language, namespace);
      return fallback || key;
    }

    return translation;
  }

  /**
   * Track missing translations
   */
  trackMissingTranslation(key, language, namespace) {
    const missingKey = `${language}:${namespace}:${key}`;

    if (!this.missingTranslations.has(missingKey)) {
      this.missingTranslations.set(missingKey, {
        key,
        language,
        namespace,
        count: 1,
        firstSeen: new Date(),
        lastSeen: new Date()
      });
    } else {
      const entry = this.missingTranslations.get(missingKey);
      entry.count++;
      entry.lastSeen = new Date();
    }
  }

  /**
   * Get missing translations report
   */
  getMissingTranslationsReport() {
    const report = {
      total: this.missingTranslations.size,
      byLanguage: {},
      byNamespace: {},
      entries: []
    };

    for (const [key, entry] of this.missingTranslations) {
      // Group by language
      if (!report.byLanguage[entry.language]) {
        report.byLanguage[entry.language] = [];
      }
      report.byLanguage[entry.language].push(entry);

      // Group by namespace
      if (!report.byNamespace[entry.namespace]) {
        report.byNamespace[entry.namespace] = [];
      }
      report.byNamespace[entry.namespace].push(entry);

      // Add to entries
      report.entries.push(entry);
    }

    // Sort entries by count
    report.entries.sort((a, b) => b.count - a.count);

    return report;
  }

  /**
   * Submit missing translations to server
   */
  async submitMissingTranslations() {
    if (this.missingTranslations.size === 0) {
      return { message: 'No missing translations to submit' };
    }

    try {
      const report = this.getMissingTranslationsReport();
      const response = await api.post('/i18n/missing-translations', report);

      // Clear submitted translations
      this.missingTranslations.clear();

      return response.data;
    } catch (error) {
      console.error('Failed to submit missing translations:', error);
      throw error;
    }
  }

  /**
   * Update translation dynamically
   */
  updateTranslation(language, namespace, key, value) {
    // Update in i18n instance
    i18n.addResource(language, namespace, key, value);

    // Update cache
    const cacheKey = `${language}:${namespace}`;
    if (this.cache.has(cacheKey)) {
      const translations = this.cache.get(cacheKey);
      this._setNestedValue(translations, key, value);
    }

    // Notify listeners
    this.notifyListeners('translationUpdated', { language, namespace, key, value });
  }

  /**
   * Batch update translations
   */
  batchUpdateTranslations(updates) {
    for (const update of updates) {
      this.updateTranslation(
        update.language,
        update.namespace,
        update.key,
        update.value
      );
    }
  }

  /**
   * Set nested value in object
   */
  _setNestedValue(obj, path, value) {
    const keys = path.split('.');
    let current = obj;

    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) {
        current[keys[i]] = {};
      }
      current = current[keys[i]];
    }

    current[keys[keys.length - 1]] = value;
  }

  /**
   * Add event listener
   */
  addEventListener(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Notify listeners
   */
  notifyListeners(event, data) {
    for (const listener of this.listeners) {
      try {
        listener(event, data);
      } catch (error) {
        console.error('Error in translation manager listener:', error);
      }
    }
  }

  /**
   * Export translations for a language
   */
  async exportTranslations(language) {
    const translations = {};

    for (const namespace of TRANSLATION_NAMESPACES) {
      const cacheKey = `${language}:${namespace}`;
      if (this.cache.has(cacheKey)) {
        translations[namespace] = this.cache.get(cacheKey);
      } else {
        translations[namespace] = await this.loadTranslations(language, namespace);
      }
    }

    return translations;
  }

  /**
   * Import translations
   */
  async importTranslations(language, translations) {
    for (const [namespace, namespaceTranslations] of Object.entries(translations)) {
      // Update cache
      this.cache.set(`${language}:${namespace}`, namespaceTranslations);

      // Update i18n
      i18n.addResourceBundle(language, namespace, namespaceTranslations, true, true);
    }

    this.notifyListeners('translationsImported', { language });
  }

  /**
   * Validate translations
   */
  validateTranslations(language, referenceLanguage = 'en') {
    const issues = [];

    for (const namespace of TRANSLATION_NAMESPACES) {
      const targetTranslations = this.cache.get(`${language}:${namespace}`) || {};
      const referenceTranslations = this.cache.get(`${referenceLanguage}:${namespace}`) || {};

      // Check for missing keys
      const missingKeys = this._findMissingKeys(referenceTranslations, targetTranslations);
      if (missingKeys.length > 0) {
        issues.push({
          type: 'missing',
          namespace,
          keys: missingKeys
        });
      }

      // Check for extra keys
      const extraKeys = this._findMissingKeys(targetTranslations, referenceTranslations);
      if (extraKeys.length > 0) {
        issues.push({
          type: 'extra',
          namespace,
          keys: extraKeys
        });
      }

      // Check for empty translations
      const emptyKeys = this._findEmptyValues(targetTranslations);
      if (emptyKeys.length > 0) {
        issues.push({
          type: 'empty',
          namespace,
          keys: emptyKeys
        });
      }
    }

    return {
      language,
      referenceLanguage,
      valid: issues.length === 0,
      issues
    };
  }

  /**
   * Find missing keys between two objects
   */
  _findMissingKeys(reference, target, prefix = '') {
    const missing = [];

    for (const key in reference) {
      const fullKey = prefix ? `${prefix}.${key}` : key;

      if (!(key in target)) {
        missing.push(fullKey);
      } else if (typeof reference[key] === 'object' && reference[key] !== null) {
        const nestedMissing = this._findMissingKeys(
          reference[key],
          target[key] || {},
          fullKey
        );
        missing.push(...nestedMissing);
      }
    }

    return missing;
  }

  /**
   * Find empty values in translations
   */
  _findEmptyValues(translations, prefix = '') {
    const empty = [];

    for (const key in translations) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      const value = translations[key];

      if (typeof value === 'string' && value.trim() === '') {
        empty.push(fullKey);
      } else if (typeof value === 'object' && value !== null) {
        const nestedEmpty = this._findEmptyValues(value, fullKey);
        empty.push(...nestedEmpty);
      }
    }

    return empty;
  }
}

// Create singleton instance
const translationManager = new TranslationManager();

export default translationManager;