// TODO: i18n - processed
/**
 * useDynamicTranslation Hook
 * Handle dynamic content translation and real-time updates
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useLanguage } from './useLanguage';
import translationManager from '../managers/TranslationManager';
import api from '../../lib/api';import { useTranslation } from "react-i18next";

const useDynamicTranslation = (entityType, entityId, options = {}) => {
  const { currentLanguage } = useLanguage();
  const [translations, setTranslations] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDirty, setIsDirty] = useState(false);
  const pendingUpdates = useRef(new Map());
  const saveTimeoutRef = useRef(null);

  const {
    autoSave = true,
    autoSaveDelay = 2000,
    fields = [],
    onSave,
    onError
  } = options;

  // Load translations for entity
  useEffect(() => {
    if (!entityType || !entityId) return;

    const loadTranslations = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await api.get(`/i18n/content/${entityType}/${entityId}`, {
          params: { language: currentLanguage }
        });

        setTranslations(response.data.translations || {});
      } catch (err) {
        console.error('Failed to load translations:', err);
        setError(err.message);
        onError?.(err);
      } finally {
        setIsLoading(false);
      }
    };

    loadTranslations();
  }, [entityType, entityId, currentLanguage, onError]);

  // Get translation for a field
  const getTranslation = useCallback((fieldName, fallback = '') => {
    return translations[fieldName]?.[currentLanguage] || fallback;
  }, [translations, currentLanguage]);

  // Update translation for a field
  const updateTranslation = useCallback((fieldName, value) => {
    // Update local state
    setTranslations((prev) => ({
      ...prev,
      [fieldName]: {
        ...prev[fieldName],
        [currentLanguage]: value
      }
    }));

    // Track pending update
    pendingUpdates.current.set(`${fieldName}:${currentLanguage}`, {
      fieldName,
      language: currentLanguage,
      value
    });

    setIsDirty(true);

    // Auto-save if enabled
    if (autoSave) {
      clearTimeout(saveTimeoutRef.current);
      saveTimeoutRef.current = setTimeout(() => {
        saveTranslations();
      }, autoSaveDelay);
    }
  }, [currentLanguage, autoSave, autoSaveDelay]);

  // Batch update translations
  const batchUpdateTranslations = useCallback((updates) => {
    const newTranslations = { ...translations };

    for (const { fieldName, language, value } of updates) {
      if (!newTranslations[fieldName]) {
        newTranslations[fieldName] = {};
      }
      newTranslations[fieldName][language] = value;

      pendingUpdates.current.set(`${fieldName}:${language}`, {
        fieldName,
        language,
        value
      });
    }

    setTranslations(newTranslations);
    setIsDirty(true);

    if (autoSave) {
      clearTimeout(saveTimeoutRef.current);
      saveTimeoutRef.current = setTimeout(() => {
        saveTranslations();
      }, autoSaveDelay);
    }
  }, [translations, autoSave, autoSaveDelay]);

  // Save translations to server
  const saveTranslations = useCallback(async () => {
    if (pendingUpdates.current.size === 0) return;

    const updates = Array.from(pendingUpdates.current.values());
    pendingUpdates.current.clear();

    try {
      const response = await api.post(`/i18n/content/${entityType}/${entityId}`, {
        translations: updates
      });

      setIsDirty(false);
      onSave?.(response.data);

      return response.data;
    } catch (err) {
      console.error('Failed to save translations:', err);

      // Re-add updates to pending
      for (const update of updates) {
        pendingUpdates.current.set(`${update.fieldName}:${update.language}`, update);
      }

      setError(err.message);
      onError?.(err);
      throw err;
    }
  }, [entityType, entityId, onSave, onError]);

  // Delete translation for a field
  const deleteTranslation = useCallback((fieldName, language = currentLanguage) => {
    setTranslations((prev) => {
      const updated = { ...prev };
      if (updated[fieldName]) {
        delete updated[fieldName][language];
        if (Object.keys(updated[fieldName]).length === 0) {
          delete updated[fieldName];
        }
      }
      return updated;
    });

    pendingUpdates.current.set(`${fieldName}:${language}`, {
      fieldName,
      language,
      value: null,
      deleted: true
    });

    setIsDirty(true);

    if (autoSave) {
      clearTimeout(saveTimeoutRef.current);
      saveTimeoutRef.current = setTimeout(() => {
        saveTranslations();
      }, autoSaveDelay);
    }
  }, [currentLanguage, autoSave, autoSaveDelay]);

  // Translate field using AI
  const translateField = useCallback(async (fieldName, targetLanguages = [], sourceLanguage = 'en') => {
    try {
      const sourceText = translations[fieldName]?.[sourceLanguage];
      if (!sourceText) {
        throw new Error(`No source text found for field ${fieldName} in language ${sourceLanguage}`);
      }

      const response = await api.post('/i18n/translate', {
        text: sourceText,
        sourceLanguage,
        targetLanguages,
        context: {
          entityType,
          entityId,
          fieldName
        }
      });

      // Update translations with AI results
      const updates = response.data.translations.map(({ language, text }) => ({
        fieldName,
        language,
        value: text
      }));

      batchUpdateTranslations(updates);

      return response.data;
    } catch (err) {
      console.error('Failed to translate field:', err);
      setError(err.message);
      onError?.(err);
      throw err;
    }
  }, [translations, entityType, entityId, batchUpdateTranslations, onError]);

  // Translate all fields
  const translateAllFields = useCallback(async (targetLanguages = [], sourceLanguage = 'en') => {
    const results = [];

    for (const fieldName of fields) {
      try {
        const result = await translateField(fieldName, targetLanguages, sourceLanguage);
        results.push({ fieldName, success: true, result });
      } catch (err) {
        results.push({ fieldName, success: false, error: err.message });
      }
    }

    return results;
  }, [fields, translateField]);

  // Get translation status for all fields
  const getTranslationStatus = useCallback(() => {
    const status = {
      total: fields.length,
      translated: {},
      missing: {},
      coverage: {}
    };

    const languages = new Set();

    // Collect all languages
    for (const fieldTranslations of Object.values(translations)) {
      Object.keys(fieldTranslations).forEach((lang) => languages.add(lang));
    }

    // Check each language
    for (const language of languages) {
      status.translated[language] = 0;
      status.missing[language] = [];

      for (const field of fields) {
        if (translations[field]?.[language]) {
          status.translated[language]++;
        } else {
          status.missing[language].push(field);
        }
      }

      status.coverage[language] = status.total > 0 ?
      status.translated[language] / status.total * 100 :
      0;
    }

    return status;
  }, [fields, translations]);

  // Import translations from file
  const importTranslations = useCallback(async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('entityType', entityType);
      formData.append('entityId', entityId);

      const response = await api.post('/i18n/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setTranslations(response.data.translations);
      return response.data;
    } catch (err) {
      console.error('Failed to import translations:', err);
      setError(err.message);
      onError?.(err);
      throw err;
    }
  }, [entityType, entityId, onError]);

  // Export translations to file
  const exportTranslations = useCallback(async (format = 'json') => {
    try {
      const response = await api.get(`/i18n/export/${entityType}/${entityId}`, {
        params: { format },
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `translations_${entityType}_${entityId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return true;
    } catch (err) {
      console.error('Failed to export translations:', err);
      setError(err.message);
      onError?.(err);
      throw err;
    }
  }, [entityType, entityId, onError]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      clearTimeout(saveTimeoutRef.current);
      if (isDirty && autoSave) {
        saveTranslations();
      }
    };
  }, [isDirty, autoSave, saveTranslations]);

  return {
    translations,
    isLoading,
    error,
    isDirty,
    currentLanguage,

    // CRUD operations
    getTranslation,
    updateTranslation,
    batchUpdateTranslations,
    deleteTranslation,
    saveTranslations,

    // Translation operations
    translateField,
    translateAllFields,

    // Import/Export
    importTranslations,
    exportTranslations,

    // Status
    getTranslationStatus
  };
};

export default useDynamicTranslation;