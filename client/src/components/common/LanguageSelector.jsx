import React, { useState, useRef, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, Check } from 'lucide-react';
import { SUPPORTED_LANGUAGES } from '../../i18n/constants';

/**
 * Enhanced Language Selector Component
 * Provides UI for changing application language with better UX
 */
const LanguageSelector = ({ 
  className = '', 
  showFlag = true, 
  showNativeName = true,
  dropdownPosition = 'bottom-right',
  mobile = false 
}) => {
  const { i18n, t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  
  const languages = Object.entries(SUPPORTED_LANGUAGES).map(([code, info]) => ({
    code,
    ...info,
    active: i18n.language === code
  }));
  
  const currentLanguage = languages.find(lang => lang.code === i18n.language);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLanguageChange = async (langCode) => {
    try {
      await i18n.changeLanguage(langCode);
      
      // Store user preference
      localStorage.setItem('bdc_user_language', langCode);
      
      // Update document attributes
      document.documentElement.lang = langCode;
      document.documentElement.dir = SUPPORTED_LANGUAGES[langCode]?.direction || 'ltr';
      
      // Emit custom event for other components
      window.dispatchEvent(new CustomEvent('languageChanged', {
        detail: { language: langCode, languageInfo: SUPPORTED_LANGUAGES[langCode] }
      }));
      
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to change language:', error);
    }
  };

  const getDropdownClasses = () => {
    const positions = {
      'bottom-right': 'right-0 mt-2',
      'bottom-left': 'left-0 mt-2',
      'top-right': 'right-0 bottom-full mb-2',
      'top-left': 'left-0 bottom-full mb-2'
    };
    return positions[dropdownPosition] || positions['bottom-right'];
  };

  const getFlagEmoji = (langCode) => {
    const flags = {
      en: '🇺🇸',
      tr: '🇹🇷',
      ar: '🇸🇦',
      es: '🇪🇸',
      fr: '🇫🇷',
      de: '🇩🇪',
      ru: '🇷🇺',
      he: '🇮🇱'
    };
    return flags[langCode] || '🌐';
  };

  if (mobile) {
    return (
      <div className="border-t border-gray-200 dark:border-gray-700 pt-2">
        <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-2">
          {t('common.language', 'Language')}
        </div>
        <select
          value={i18n.language}
          onChange={(e) => handleLanguageChange(e.target.value)}
          className="w-full p-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        >
          {languages.map((lang) => (
            <option key={lang.code} value={lang.code}>
              {getFlagEmoji(lang.code)} {lang.nativeName}
            </option>
          ))}
        </select>
      </div>
    );
  }

  return (
    <div className={`relative inline-block text-left ${className}`} ref={dropdownRef}>
      <button
        type="button"
        className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 transition-colors rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="true"
        aria-expanded={isOpen}
        aria-label={t('common.select_language', 'Select language')}
      >
        <Globe className="w-4 h-4" />
        {showFlag && (
          <span className="text-lg">{getFlagEmoji(currentLanguage?.code)}</span>
        )}
        <span className="hidden md:inline-block">
          {showNativeName ? currentLanguage?.nativeName : currentLanguage?.code.toUpperCase()}
        </span>
      </button>

      {isOpen && (
        <div 
          className={`absolute z-50 w-64 mt-2 origin-top-right bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 ${getDropdownClasses()}`}
          role="menu"
          aria-orientation="vertical"
          aria-labelledby="language-menu"
        >
          <div className="py-1" role="none">
            <div className="px-4 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 border-b border-gray-100 dark:border-gray-700">
              {t('common.select_language', 'Select Language')}
            </div>
            {languages.map((lang) => (
              <button
                key={lang.code}
                className={`
                  flex items-center w-full px-4 py-3 text-sm text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors
                  ${lang.active ? 'text-blue-600 dark:text-blue-400 font-medium bg-blue-50 dark:bg-blue-900/20' : 'text-gray-700 dark:text-gray-300'}
                  ${lang.direction === 'rtl' ? 'flex-row-reverse text-right' : 'text-left'}
                `}
                role="menuitem"
                onClick={() => handleLanguageChange(lang.code)}
                dir={lang.direction}
                disabled={lang.active}
              >
                {showFlag && (
                  <span className={`text-lg ${lang.direction === 'rtl' ? 'ml-3' : 'mr-3'}`}>
                    {getFlagEmoji(lang.code)}
                  </span>
                )}
                <div className="flex-1">
                  <div className="font-medium">
                    {showNativeName ? lang.nativeName : lang.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {lang.name !== lang.nativeName ? lang.name : ''}
                  </div>
                </div>
                {lang.active && (
                  <Check className={`w-4 h-4 text-blue-600 dark:text-blue-400 ${lang.direction === 'rtl' ? 'mr-2' : 'ml-2'}`} />
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default LanguageSelector;