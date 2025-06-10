// TODO: i18n - processed
/**
 * useLanguage Hook
 * Access language context and management functions
 */

import { useContext, useCallback, useMemo } from 'react';
import { LanguageContext } from '../providers/LanguageProvider';
import { SUPPORTED_LANGUAGES } from '../constants';import { useTranslation } from "react-i18next";

const useLanguage = () => {
  const context = useContext(LanguageContext);

  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }

  const {
    currentLanguage,
    languages,
    changeLanguage,
    isRTL,
    isLoading,
    error,
    languageInfo
  } = context;

  // Get language by code
  const getLanguage = useCallback((code) => {
    return SUPPORTED_LANGUAGES[code] || null;
  }, []);

  // Get native language name
  const getNativeName = useCallback((code = currentLanguage) => {
    return SUPPORTED_LANGUAGES[code]?.nativeName || code;
  }, [currentLanguage]);

  // Get language flag
  const getFlag = useCallback((code = currentLanguage) => {
    return SUPPORTED_LANGUAGES[code]?.flag || '';
  }, [currentLanguage]);

  // Check if language is supported
  const isSupported = useCallback((code) => {
    return code in SUPPORTED_LANGUAGES;
  }, []);

  // Get available languages as array
  const availableLanguages = useMemo(() => {
    return Object.values(SUPPORTED_LANGUAGES).map((lang) => ({
      code: lang.code,
      name: lang.name,
      nativeName: lang.nativeName,
      flag: lang.flag,
      direction: lang.direction
    }));
  }, []);

  // Get language direction
  const getDirection = useCallback((code = currentLanguage) => {
    return SUPPORTED_LANGUAGES[code]?.direction || 'ltr';
  }, [currentLanguage]);

  // Get locale
  const getLocale = useCallback((code = currentLanguage) => {
    return SUPPORTED_LANGUAGES[code]?.locale || 'en-US';
  }, [currentLanguage]);

  // Check if current language matches
  const isCurrentLanguage = useCallback((code) => {
    return currentLanguage === code;
  }, [currentLanguage]);

  // Get language-specific date format
  const getDateFormat = useCallback((code = currentLanguage) => {
    return SUPPORTED_LANGUAGES[code]?.dateFormat || 'MM/DD/YYYY';
  }, [currentLanguage]);

  // Get language-specific currency
  const getCurrency = useCallback((code = currentLanguage) => {
    return SUPPORTED_LANGUAGES[code]?.currency || 'USD';
  }, [currentLanguage]);

  // Get number format settings
  const getNumberFormat = useCallback((code = currentLanguage) => {
    return SUPPORTED_LANGUAGES[code]?.numberFormat || {
      decimal: '.',
      thousand: ',',
      precision: 2
    };
  }, [currentLanguage]);

  // Language switcher helper
  const switchToLanguage = useCallback(async (code) => {
    if (!isSupported(code)) {
      console.error(`Language ${code} is not supported`);
      return false;
    }

    try {
      await changeLanguage(code);
      return true;
    } catch (error) {
      console.error('Failed to switch language:', error);
      return false;
    }
  }, [changeLanguage, isSupported]);

  // Get next/previous language (for language cycling)
  const getNextLanguage = useCallback(() => {
    const codes = Object.keys(SUPPORTED_LANGUAGES);
    const currentIndex = codes.indexOf(currentLanguage);
    const nextIndex = (currentIndex + 1) % codes.length;
    return codes[nextIndex];
  }, [currentLanguage]);

  const getPreviousLanguage = useCallback(() => {
    const codes = Object.keys(SUPPORTED_LANGUAGES);
    const currentIndex = codes.indexOf(currentLanguage);
    const prevIndex = (currentIndex - 1 + codes.length) % codes.length;
    return codes[prevIndex];
  }, [currentLanguage]);

  // Cycle through languages
  const cycleLanguage = useCallback(async (direction = 'next') => {
    const nextLang = direction === 'next' ? getNextLanguage() : getPreviousLanguage();
    await switchToLanguage(nextLang);
  }, [getNextLanguage, getPreviousLanguage, switchToLanguage]);

  return {
    // Current state
    currentLanguage,
    languageInfo,
    isRTL,
    isLoading,
    error,

    // Language data
    languages,
    availableLanguages,

    // Language functions
    changeLanguage,
    switchToLanguage,
    cycleLanguage,

    // Helper functions
    getLanguage,
    getNativeName,
    getFlag,
    isSupported,
    getDirection,
    getLocale,
    isCurrentLanguage,
    getDateFormat,
    getCurrency,
    getNumberFormat,
    getNextLanguage,
    getPreviousLanguage
  };
};

export default useLanguage;