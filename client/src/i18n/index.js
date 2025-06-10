// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Internationalization (i18n) Module
 * Comprehensive language support system for the BDC project
 */

export { default } from './config';
export { default as LanguageProvider } from './providers/LanguageProvider';
export { default as TranslationManager } from './managers/TranslationManager';
export { default as LocalizationManager } from './managers/LocalizationManager';
export { default as RTLProvider } from './providers/RTLProvider';
export { useTranslation, useLanguage, useLocalization, useRTL } from './hooks';
export * from './utils';
export * from './constants';