// TODO: i18n - processed
/**
 * Language Provider Component
 * Manages language state and provides language context to the application
 */

import React, { createContext, useState, useEffect, useCallback, useMemo } from 'react';
import i18n from '../config';
import {
  SUPPORTED_LANGUAGES,
  DEFAULT_LANGUAGE,
  LANGUAGE_STORAGE_KEY,
  RTL_LANGUAGES } from
'../constants';
import { detectUserLanguage, loadLanguageResources } from '../utils';
import RTLProvider from './RTLProvider';import { useTranslation } from "react-i18next";

export const LanguageContext = createContext({
  currentLanguage: DEFAULT_LANGUAGE,
  languages: SUPPORTED_LANGUAGES,
  changeLanguage: () => {},
  isRTL: false,
  isLoading: false,
  error: null
});

const LanguageProvider = ({ children, defaultLanguage = DEFAULT_LANGUAGE }) => {const { t } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState(defaultLanguage);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [languageResources, setLanguageResources] = useState({});

  // Initialize language on mount
  useEffect(() => {
    const initializeLanguage = async () => {
      try {
        setIsLoading(true);

        // Try to get saved language from storage
        const savedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY);

        // Detect user language if no saved preference
        const detectedLanguage = savedLanguage || (await detectUserLanguage());
        const languageToUse = SUPPORTED_LANGUAGES[detectedLanguage] ?
        detectedLanguage :
        defaultLanguage;

        // Load language resources
        await loadLanguageResources(languageToUse);

        // Set language in i18n
        await i18n.changeLanguage(languageToUse);

        setCurrentLanguage(languageToUse);
        localStorage.setItem(LANGUAGE_STORAGE_KEY, languageToUse);

        // Set document direction
        document.documentElement.dir = SUPPORTED_LANGUAGES[languageToUse].direction;
        document.documentElement.lang = languageToUse;

      } catch (err) {
        console.error('Error initializing language:', err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    initializeLanguage();
  }, [defaultLanguage]);

  // Change language handler
  const changeLanguage = useCallback(async (newLanguage) => {
    if (!SUPPORTED_LANGUAGES[newLanguage]) {
      console.error(`Language ${newLanguage} is not supported`);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Load new language resources if not already loaded
      if (!languageResources[newLanguage]) {
        await loadLanguageResources(newLanguage);
      }

      // Change language in i18n
      await i18n.changeLanguage(newLanguage);

      setCurrentLanguage(newLanguage);
      localStorage.setItem(LANGUAGE_STORAGE_KEY, newLanguage);

      // Update document direction and lang
      document.documentElement.dir = SUPPORTED_LANGUAGES[newLanguage].direction;
      document.documentElement.lang = newLanguage;

      // Emit language change event
      window.dispatchEvent(new CustomEvent('languageChanged', {
        detail: { language: newLanguage }
      }));

    } catch (err) {
      console.error('Error changing language:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [languageResources]);

  // Check if current language is RTL
  const isRTL = useMemo(() => {
    return RTL_LANGUAGES.includes(currentLanguage);
  }, [currentLanguage]);

  // Context value
  const contextValue = useMemo(() => ({
    currentLanguage,
    languages: SUPPORTED_LANGUAGES,
    changeLanguage,
    isRTL,
    isLoading,
    error,
    languageInfo: SUPPORTED_LANGUAGES[currentLanguage] || SUPPORTED_LANGUAGES[DEFAULT_LANGUAGE]
  }), [currentLanguage, changeLanguage, isRTL, isLoading, error]);

  return (
    <LanguageContext.Provider value={contextValue}>
      <RTLProvider isRTL={isRTL}>
        {children}
      </RTLProvider>
    </LanguageContext.Provider>);

};

export default LanguageProvider;