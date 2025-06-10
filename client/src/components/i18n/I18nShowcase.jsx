// TODO: i18n - processed
/**
 * i18n Showcase Component
 * Demonstrates all internationalization features
 */

import React, { useState } from 'react';
import {
  useTranslation,
  useLanguage,
  useLocalization,
  useRTL,
  useDynamicTranslation,
  useTranslationValidation } from
'../../i18n';
import { SUPPORTED_LANGUAGES, DATE_FORMATS, NUMBER_FORMATS } from '../../i18n/constants';
import { Card, CardHeader, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Select } from '../ui/select';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import './I18nShowcase.css';import { useTranslation } from "react-i18next";

const I18nShowcase = () => {
  const { t, tc, tx, tf, exists } = useTranslation();
  const {
    currentLanguage,
    changeLanguage,
    availableLanguages,
    isRTL: isCurrentRTL,
    languageInfo
  } = useLanguage();
  const {
    formatDate,
    formatTime,
    formatDateTime,
    formatRelativeTime,
    formatNumber,
    formatCurrency,
    formatPercent,
    formatList,
    formatFileSize,
    formatDuration,
    parseNumber
  } = useLocalization();
  const {
    isRTL,
    direction,
    alignment,
    getRTLStyle,
    getRTLClassName,
    getIconPosition
  } = useRTL();

  // State
  const [selectedDate] = useState(new Date());
  const [testNumber] = useState(1234567.89);
  const [testCurrency] = useState(999.99);
  const [testPercent] = useState(0.856);
  const [testFileSize] = useState(1048576); // 1 MB
  const [testDuration] = useState(3661); // 1 hour, 1 minute, 1 second
  const [pluralCount, setPluralCount] = useState(1);
  const [dynamicContent, setDynamicContent] = useState('');

  // Dynamic translation for demo entity
  const {
    translations: dynamicTranslations,
    updateTranslation,
    saveTranslations,
    translateField,
    getTranslationStatus
  } = useDynamicTranslation('demo', 'showcase', {
    fields: ['title', 'description'],
    autoSave: false
  });

  // Translation validation
  const { validateLanguage, validationResults } = useTranslationValidation();

  // Handle language change
  const handleLanguageChange = async (newLanguage) => {
    await changeLanguage(newLanguage);
  };

  // Validate current language
  const handleValidateLanguage = async () => {
    const results = await validateLanguage(currentLanguage);
    console.log('Validation results:', results);
  };

  return (
    <div className={getRTLClassName('i18n-showcase', 'i18n-showcase-rtl')} dir={direction}>
      {/* Header */}
      <div className="showcase-header">
        <h1>{t('i18n.showcase.title', 'Internationalization Showcase')}</h1>
        <p>{t('i18n.showcase.description', 'Comprehensive demonstration of i18n features')}</p>
      </div>

      {/* Language Selector */}
      <Card className="language-selector-card">
        <CardHeader>
          <h2>{t('i18n.showcase.languageSelection', 'Language Selection')}</h2>
        </CardHeader>
        <CardContent>
          <div className="language-grid">
            {availableLanguages.map((lang) =>
            <Button
              key={lang.code}
              variant={currentLanguage === lang.code ? 'primary' : 'outline'}
              onClick={() => handleLanguageChange(lang.code)}
              className={getRTLClassName('language-button', 'language-button-rtl')}>

                <span className="flag">{lang.flag}</span>
                <span className="name">{lang.nativeName}</span>
                {lang.direction === 'rtl' &&
              <Badge variant="info" size="sm">RTL</Badge>
              }
              </Button>
            )}
          </div>
          
          <div className="language-info">
            <h3>{t('i18n.showcase.currentLanguageInfo', 'Current Language Information')}</h3>
            <dl>
              <dt>{t('i18n.showcase.code', 'Code')}:</dt>
              <dd>{languageInfo.code}</dd>
              
              <dt>{t('i18n.showcase.name', 'Name')}:</dt>
              <dd>{languageInfo.name}</dd>
              
              <dt>{t('i18n.showcase.direction', 'Direction')}:</dt>
              <dd>{languageInfo.direction}</dd>
              
              <dt>{t('i18n.showcase.locale', 'Locale')}:</dt>
              <dd>{languageInfo.locale}</dd>
              
              <dt>{t('i18n.showcase.dateFormat', 'Date Format')}:</dt>
              <dd>{languageInfo.date_format}</dd>
              
              <dt>{t('i18n.showcase.currency', 'Currency')}:</dt>
              <dd>{languageInfo.currency}</dd>
            </dl>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="translation" className="showcase-tabs">
        <TabsList>
          <TabsTrigger value="translation">
            {t('i18n.showcase.tabs.translation', 'Translation')}
          </TabsTrigger>
          <TabsTrigger value="formatting">
            {t('i18n.showcase.tabs.formatting', 'Formatting')}
          </TabsTrigger>
          <TabsTrigger value="rtl">
            {t('i18n.showcase.tabs.rtl', 'RTL Support')}
          </TabsTrigger>
          <TabsTrigger value="dynamic">
            {t('i18n.showcase.tabs.dynamic', 'Dynamic Content')}
          </TabsTrigger>
          <TabsTrigger value="validation">
            {t('i18n.showcase.tabs.validation', 'Validation')}
          </TabsTrigger>
        </TabsList>

        {/* Translation Features */}
        <TabsContent value="translation">
          <Card>
            <CardHeader>
              <h3>{t('i18n.showcase.translationFeatures', 'Translation Features')}</h3>
            </CardHeader>
            <CardContent>
              {/* Basic Translation */}
              <section>
                <h4>{t('i18n.showcase.basicTranslation', 'Basic Translation')}</h4>
                <p>{t('common.welcome')}</p>
                <p>{t('navigation.dashboard')}</p>
              </section>

              {/* Interpolation */}
              <section>
                <h4>{t('i18n.showcase.interpolation', 'Interpolation')}</h4>
                <p>{t('notifications.appointment.created', { date: formatDate(selectedDate) })}</p>
                <p>{t('notifications.program.progress', { percent: 75, program: 'Advanced Training' })}</p>
              </section>

              {/* Pluralization */}
              <section>
                <h4>{t('i18n.showcase.pluralization', 'Pluralization')}</h4>
                <div className="plural-demo">
                  <Input
                    type="number"
                    value={pluralCount}
                    onChange={(e) => setPluralCount(parseInt(e.target.value) || 0)}
                    min="0"
                    max="100" />

                  <p>{tc('i18n.showcase.items', pluralCount, { count: pluralCount })}</p>
                </div>
              </section>

              {/* Context */}
              <section>
                <h4>{t('i18n.showcase.context', 'Context-based Translation')}</h4>
                <p>{tx('common.save', 'button')}</p>
                <p>{tx('common.save', 'action')}</p>
              </section>

              {/* Fallback */}
              <section>
                <h4>{t('i18n.showcase.fallback', 'Fallback Translation')}</h4>
                <p>{tf('non.existent.key', 'This is a fallback value')}</p>
              </section>

              {/* Check Existence */}
              <section>
                <h4>{t('i18n.showcase.existence', 'Translation Existence Check')}</h4>
                <p>{t("components.commonwelcome_exists")}
                  {exists('common.welcome') ? '✓' : '✗'}
                </p>
                <p>
                  invalid.key exists: {exists('invalid.key') ? '✓' : '✗'}
                </p>
              </section>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Formatting Features */}
        <TabsContent value="formatting">
          <Card>
            <CardHeader>
              <h3>{t('i18n.showcase.formattingFeatures', 'Formatting Features')}</h3>
            </CardHeader>
            <CardContent>
              {/* Date Formatting */}
              <section>
                <h4>{t('i18n.showcase.dateFormatting', 'Date Formatting')}</h4>
                <dl>
                  <dt>{t('i18n.showcase.short', 'Short')}:</dt>
                  <dd>{formatDate(selectedDate, DATE_FORMATS.short)}</dd>
                  
                  <dt>{t('i18n.showcase.medium', 'Medium')}:</dt>
                  <dd>{formatDate(selectedDate, DATE_FORMATS.medium)}</dd>
                  
                  <dt>{t('i18n.showcase.long', 'Long')}:</dt>
                  <dd>{formatDate(selectedDate, DATE_FORMATS.long)}</dd>
                  
                  <dt>{t('i18n.showcase.full', 'Full')}:</dt>
                  <dd>{formatDate(selectedDate, DATE_FORMATS.full)}</dd>
                  
                  <dt>{t('i18n.showcase.relative', 'Relative')}:</dt>
                  <dd>{formatRelativeTime(new Date(Date.now() - 3600000))}</dd>
                </dl>
              </section>

              {/* Time Formatting */}
              <section>
                <h4>{t('i18n.showcase.timeFormatting', 'Time Formatting')}</h4>
                <p>{formatTime(selectedDate)}</p>
                <p>{formatDateTime(selectedDate)}</p>
              </section>

              {/* Number Formatting */}
              <section>
                <h4>{t('i18n.showcase.numberFormatting', 'Number Formatting')}</h4>
                <dl>
                  <dt>{t('i18n.showcase.decimal', 'Decimal')}:</dt>
                  <dd>{formatNumber(testNumber)}</dd>
                  
                  <dt>{t('i18n.showcase.percent', 'Percent')}:</dt>
                  <dd>{formatPercent(testPercent)}</dd>
                  
                  <dt>{t('i18n.showcase.currency', 'Currency')}:</dt>
                  <dd>{formatCurrency(testCurrency)}</dd>
                  
                  <dt>{t('i18n.showcase.fileSize', 'File Size')}:</dt>
                  <dd>{formatFileSize(testFileSize)}</dd>
                  
                  <dt>{t('i18n.showcase.duration', 'Duration')}:</dt>
                  <dd>{formatDuration(testDuration)}</dd>
                </dl>
              </section>

              {/* List Formatting */}
              <section>
                <h4>{t('i18n.showcase.listFormatting', 'List Formatting')}</h4>
                <p>{formatList(['Apple', 'Banana', 'Orange'])}</p>
                <p>{formatList(['Red', 'Green', 'Blue'], 'disjunction')}</p>
              </section>

              {/* Number Parsing */}
              <section>
                <h4>{t('i18n.showcase.numberParsing', 'Number Parsing')}</h4>
                <p>
                  {t('i18n.showcase.parseExample', 'Parse "1,234.56"')}: {parseNumber('1,234.56')}
                </p>
              </section>
            </CardContent>
          </Card>
        </TabsContent>

        {/* RTL Support */}
        <TabsContent value="rtl">
          <Card>
            <CardHeader>
              <h3>{t('i18n.showcase.rtlSupport', 'RTL Support Features')}</h3>
            </CardHeader>
            <CardContent>
              {/* RTL Info */}
              <section>
                <h4>{t('i18n.showcase.rtlInfo', 'RTL Information')}</h4>
                <dl>
                  <dt>{t('i18n.showcase.isRTL', 'Is RTL')}:</dt>
                  <dd>{isRTL ? '✓' : '✗'}</dd>
                  
                  <dt>{t('i18n.showcase.textDirection', 'Text Direction')}:</dt>
                  <dd>{direction}</dd>
                  
                  <dt>{t('i18n.showcase.alignment', 'Alignment')}:</dt>
                  <dd>{alignment}</dd>
                </dl>
              </section>

              {/* RTL Styling */}
              <section>
                <h4>{t('i18n.showcase.rtlStyling', 'RTL Styling')}</h4>
                <div
                  className="rtl-demo-box"
                  style={getRTLStyle({
                    marginLeft: '20px',
                    paddingRight: '10px',
                    borderLeft: '3px solid blue',
                    textAlign: 'left'
                  })}>

                  {t('i18n.showcase.rtlDemoText', 'This box adapts to RTL/LTR')}
                </div>
              </section>

              {/* Icon Position */}
              <section>
                <h4>{t('i18n.showcase.iconPosition', 'Icon Position')}</h4>
                <Button className={`icon-${getIconPosition()}`}>
                  <span className="icon">→</span>
                  {t('i18n.showcase.buttonWithIcon', 'Button with Icon')}
                </Button>
              </section>

              {/* Bidirectional Text */}
              <section>
                <h4>{t('i18n.showcase.bidirectionalText', 'Bidirectional Text')}</h4>
                <p className="bidi-text">
                  {t('i18n.showcase.mixedText', 'Phone: +1-234-567-8900 | البريد: example@email.com')}
                </p>
              </section>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Dynamic Translation */}
        <TabsContent value="dynamic">
          <Card>
            <CardHeader>
              <h3>{t('i18n.showcase.dynamicTranslation', 'Dynamic Content Translation')}</h3>
            </CardHeader>
            <CardContent>
              {/* Translation Editor */}
              <section>
                <h4>{t('i18n.showcase.translationEditor', 'Translation Editor')}</h4>
                <div className="translation-editor">
                  <div className="field-group">
                    <label>{t('i18n.showcase.title', 'Title')}</label>
                    <Input
                      value={dynamicTranslations.title?.[currentLanguage] || ''}
                      onChange={(e) => updateTranslation('title', e.target.value)}
                      placeholder={t('i18n.showcase.enterTranslation', 'Enter translation...')} />

                  </div>
                  
                  <div className="field-group">
                    <label>{t('i18n.showcase.description', 'Description')}</label>
                    <textarea
                      value={dynamicTranslations.description?.[currentLanguage] || ''}
                      onChange={(e) => updateTranslation('description', e.target.value)}
                      placeholder={t('i18n.showcase.enterTranslation', 'Enter translation...')}
                      rows="3" />

                  </div>
                  
                  <Button onClick={saveTranslations}>
                    {t('common.save')}
                  </Button>
                </div>
              </section>

              {/* Auto Translation */}
              <section>
                <h4>{t('i18n.showcase.autoTranslation', 'Auto Translation')}</h4>
                <Button
                  onClick={() => translateField('title', ['es', 'fr', 'ar'])}
                  variant="secondary">

                  {t('i18n.showcase.translateToAll', 'Translate to All Languages')}
                </Button>
              </section>

              {/* Translation Status */}
              <section>
                <h4>{t('i18n.showcase.translationStatus', 'Translation Status')}</h4>
                <div className="translation-status">
                  {JSON.stringify(getTranslationStatus(), null, 2)}
                </div>
              </section>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Validation */}
        <TabsContent value="validation">
          <Card>
            <CardHeader>
              <h3>{t('i18n.showcase.translationValidation', 'Translation Validation')}</h3>
            </CardHeader>
            <CardContent>
              <Button onClick={handleValidateLanguage}>
                {t('i18n.showcase.validateCurrentLanguage', 'Validate Current Language')}
              </Button>
              
              {validationResults[currentLanguage] &&
              <div className="validation-results">
                  <h4>{t('i18n.showcase.validationResults', 'Validation Results')}</h4>
                  <pre>{JSON.stringify(validationResults[currentLanguage], null, 2)}</pre>
                </div>
              }
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>);

};

export default I18nShowcase;