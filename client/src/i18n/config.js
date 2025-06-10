import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';
import { SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE, INTERPOLATION_OPTIONS } from './constants';

// Import translation files
import enTranslations from './locales/en.json';
import trTranslations from './locales/tr.json';
import frTranslations from './locales/fr.json';
import esTranslations from './locales/es.json';
import arTranslations from './locales/ar.json';
import heTranslations from './locales/he.json';
import deTranslations from './locales/de.json';
import ruTranslations from './locales/ru.json';
const resources = {
  en: { translation: enTranslations },
  tr: { translation: trTranslations },
  fr: { translation: frTranslations },
  es: { translation: esTranslations },
  ar: { translation: arTranslations },
  he: { translation: heTranslations },
  de: { translation: deTranslations },
  ru: { translation: ruTranslations }
};

// Custom language detector
const customLanguageDetector = {
  name: 'customDetector',
  lookup() {
    // Check localStorage first
    const savedLanguage = localStorage.getItem('bdc_user_language');
    if (savedLanguage && SUPPORTED_LANGUAGES[savedLanguage]) {
      return savedLanguage;
    }
    
    // Check browser language
    const browserLang = navigator.language || navigator.userLanguage;
    const primaryLang = browserLang.split('-')[0];
    
    if (SUPPORTED_LANGUAGES[primaryLang]) {
      return primaryLang;
    }
    
    // Default fallback
    return DEFAULT_LANGUAGE;
  },
  cacheUserLanguage(lng) {
    localStorage.setItem('bdc_user_language', lng);
  }
};
// Language detector instance
const detector = new LanguageDetector();
detector.addDetector(customLanguageDetector);

i18n
  .use(detector)
  .use(Backend)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: DEFAULT_LANGUAGE,
    debug: process.env.NODE_ENV === 'development',
    
    // Namespaces
    ns: ['translation'],
    defaultNS: 'translation',
    
    // Interpolation settings
    interpolation: INTERPOLATION_OPTIONS,
    
    // Detection settings
    detection: {
      order: ['customDetector', 'localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
      lookupLocalStorage: 'bdc_user_language',
      checkWhitelist: true
    },
    
    // React specific options
    react: {
      useSuspense: false,
      bindI18n: 'languageChanged loaded',
      bindI18nStore: 'added removed',
      transEmptyNodeValue: '',
      transSupportBasicHtmlNodes: true,
      transKeepBasicHtmlNodesFor: ['br', 'strong', 'i', 'p']
    },
    
    // Backend options (for dynamic loading)
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
      addPath: '/locales/add/{{lng}}/{{ns}}',
      allowMultiLoading: false,
      crossDomain: false
    },
    
    // Supported languages whitelist
    supportedLngs: Object.keys(SUPPORTED_LANGUAGES),
    
    // Load languages on demand
    load: 'languageOnly',
    
    // Preload languages
    preload: [DEFAULT_LANGUAGE],
    
    // Clean code
    cleanCode: true,
    
    // Non-explicit whitelist
    nonExplicitSupportedLngs: false,
    
    // Missing key handler
    saveMissing: process.env.NODE_ENV === 'development',
    saveMissingTo: 'current',
    missingKeyHandler: (lngs, ns, key, fallbackValue) => {
      if (process.env.NODE_ENV === 'development') {
        console.warn(`Missing translation: ${key} for languages: ${lngs.join(', ')}`);
      }
    },
    
    // Post process
    postProcess: ['sprintf'],
    
    // Return objects
    returnObjects: true,
    returnedObjectHandler: (key, value, options) => {
      // Handle returned objects
      return value;
    },
    
    // Context
    context: true,
    contextSeparator: '_',
    
    // Plural
    pluralSeparator: '_',
    
    // Key separator
    keySeparator: '.',
    
    // Namespace separator
    nsSeparator: ':',
    
    // Allow deep keys
    allowObjectInHTMLChildren: false
  });

// Language change handler
i18n.on('languageChanged', (lng) => {
  // Update document attributes
  document.documentElement.lang = lng;
  document.documentElement.dir = SUPPORTED_LANGUAGES[lng]?.direction || 'ltr';
  
  // Update meta tags
  const metaLang = document.querySelector('meta[http-equiv="content-language"]');
  if (metaLang) {
    metaLang.content = lng;
  }
});

// Initialize language on load
i18n.on('initialized', () => {
  const currentLang = i18n.language;
  document.documentElement.lang = currentLang;
  document.documentElement.dir = SUPPORTED_LANGUAGES[currentLang]?.direction || 'ltr';
});
export default i18n;