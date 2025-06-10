# BDC Internationalization (i18n) System

A comprehensive internationalization system for the BDC project supporting 10+ languages including RTL (Right-to-Left) languages like Arabic and Hebrew.

## Features

### 🌍 Multi-Language Support
- **10 Languages**: English, Spanish, French, German, Turkish, Arabic, Hebrew, Russian, Chinese, Japanese
- **RTL Support**: Full support for Arabic and Hebrew with automatic layout mirroring
- **Dynamic Language Switching**: Change languages on-the-fly without page reload
- **Language Detection**: Automatic detection based on user preferences, browser settings, or location

### 📝 Translation Management
- **Namespace Organization**: Translations organized by feature/domain
- **Dynamic Content Translation**: Translate database content in real-time
- **Translation Validation**: Ensure translation completeness and quality
- **Missing Translation Tracking**: Automatic detection and reporting of missing translations
- **Import/Export**: Support for JSON, CSV, XLIFF, and PO formats

### 🎨 Localization Features
- **Date/Time Formatting**: Locale-specific date and time formatting
- **Number Formatting**: Decimal, currency, and percentage formatting
- **Pluralization**: Language-specific plural rules
- **List Formatting**: Proper conjunction/disjunction formatting
- **File Size & Duration**: Human-readable formatting

### 🔄 RTL (Right-to-Left) Support
- **Automatic Layout Mirroring**: CSS properties automatically adjusted
- **Bidirectional Text**: Proper handling of mixed LTR/RTL content
- **RTL-Aware Components**: All UI components work seamlessly in RTL
- **Direction-Specific Styling**: Easy styling for both directions

## Usage

### Basic Setup

```jsx
import React from 'react';
import { LanguageProvider } from './i18n';
import App from './App';

function Root() {
  return (
    <LanguageProvider defaultLanguage="en">
      <App />
    </LanguageProvider>
  );
}
```

### Using Translations

```jsx
import { useTranslation } from '../i18n';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('common.welcome')}</h1>
      <p>{t('dashboard.overview')}</p>
    </div>
  );
}
```

### Language Switching

```jsx
import { useLanguage } from '../i18n';
import { SUPPORTED_LANGUAGES } from '../i18n/constants';

function LanguageSwitcher() {
  const { currentLanguage, changeLanguage, availableLanguages } = useLanguage();
  
  return (
    <select value={currentLanguage} onChange={(e) => changeLanguage(e.target.value)}>
      {availableLanguages.map(lang => (
        <option key={lang.code} value={lang.code}>
          {lang.flag} {lang.nativeName}
        </option>
      ))}
    </select>
  );
}
```

### Date/Time Formatting

```jsx
import { useLocalization } from '../i18n';

function DateDisplay({ date }) {
  const { formatDate, formatRelativeTime } = useLocalization();
  
  return (
    <div>
      <p>Date: {formatDate(date, 'long')}</p>
      <p>Relative: {formatRelativeTime(date)}</p>
    </div>
  );
}
```

### Number/Currency Formatting

```jsx
import { useLocalization } from '../i18n';

function PriceDisplay({ amount }) {
  const { formatCurrency, formatPercent } = useLocalization();
  
  return (
    <div>
      <p>Price: {formatCurrency(amount)}</p>
      <p>Discount: {formatPercent(0.15)}</p>
    </div>
  );
}
```

### RTL Support

```jsx
import { useRTL } from '../i18n';

function RTLAwareComponent() {
  const { isRTL, direction, getRTLStyle } = useRTL();
  
  return (
    <div 
      dir={direction}
      style={getRTLStyle({
        marginLeft: '20px',
        paddingRight: '10px',
        textAlign: 'left'
      })}
    >
      Content that adapts to RTL/LTR
    </div>
  );
}
```

### Dynamic Content Translation

```jsx
import { useDynamicTranslation } from '../i18n';

function EditableContent({ entityType, entityId }) {
  const {
    translations,
    updateTranslation,
    saveTranslations,
    translateField
  } = useDynamicTranslation(entityType, entityId, {
    fields: ['title', 'description'],
    autoSave: true
  });
  
  return (
    <div>
      <input
        value={translations.title?.[currentLanguage] || ''}
        onChange={(e) => updateTranslation('title', e.target.value)}
      />
      <button onClick={() => translateField('title', ['es', 'fr', 'ar'])}>
        Auto Translate
      </button>
    </div>
  );
}
```

### Translation Structure
Translations are organized in JSON files under `/src/i18n/locales/`:

```
src/i18n/
├── config.js          # i18n configuration
├── locales/
│   ├── en.json       # English translations
│   ├── tr.json       # Turkish translations
│   ├── fr.json       # French translations
│   └── es.json       # Spanish translations
```

### Translation Categories
- **common** - Common UI elements (save, cancel, delete, etc.)
- **navigation** - Navigation menu items
- **auth** - Authentication related texts
- **dashboard** - Dashboard specific texts
- **beneficiaries** - Beneficiary management texts
- **programs** - Program management texts
- **evaluations** - Evaluation/assessment texts
- **calendar** - Calendar related texts
- **documents** - Document management texts
- **reports** - Reporting texts
- **settings** - Settings page texts
- **profile** - User profile texts
- **errors** - Error messages
- **success** - Success messages
- **validation** - Form validation messages

### Adding New Translations

1. Add the new key to all language files:
```json
// en.json
{
  "mySection": {
    "myNewKey": "My new text"
  }
}

// tr.json
{
  "mySection": {
    "myNewKey": "Yeni metnim"
  }
}
```

2. Use in your component:
```jsx
const { t } = useTranslation();
return <p>{t('mySection.myNewKey')}</p>;
```

## API Reference

### Hooks

#### `useTranslation(namespace?)`
- `t(key, options?)`: Translate a key
- `tc(key, count, options?)`: Translate with count (pluralization)
- `tx(key, context, options?)`: Translate with context
- `tf(key, fallback, options?)`: Translate with fallback
- `exists(key)`: Check if translation exists

#### `useLanguage()`
- `currentLanguage`: Current language code
- `changeLanguage(code)`: Change language
- `availableLanguages`: List of available languages
- `isRTL`: Whether current language is RTL
- `languageInfo`: Current language configuration

#### `useLocalization()`
- `formatDate(date, format?)`: Format date
- `formatTime(time, options?)`: Format time
- `formatNumber(number, format?, options?)`: Format number
- `formatCurrency(amount, currency?, options?)`: Format currency
- `formatRelativeTime(date, base?)`: Format relative time
- `formatList(items, type?, style?)`: Format list

#### `useRTL()`
- `isRTL`: Whether RTL is active
- `direction`: 'rtl' or 'ltr'
- `getRTLStyle(styles)`: Convert styles for RTL
- `getRTLClassName(ltr, rtl)`: Get appropriate class name

## Adding a New Language

1. Create translation file: `client/src/i18n/locales/[lang].json`
2. Add language configuration to `constants.js`:

```javascript
export const SUPPORTED_LANGUAGES = {
  // ... existing languages
  pt: {
    code: 'pt',
    name: 'Portuguese',
    nativeName: 'Português',
    direction: 'ltr',
    locale: 'pt-PT',
    flag: '🇵🇹',
    dateFormat: 'DD/MM/YYYY',
    currency: 'EUR'
  }
};
```

3. Add server-side translations: `server/app/locales/[lang].json`
4. Update language configuration in server: `server/app/i18n/config.py`

## Best Practices

### 1. Key Naming Convention
- Use dot notation: `section.subsection.key`
- Be descriptive: `beneficiaries.list.searchPlaceholder`
- Group by feature/domain

### 2. Placeholder Usage
```javascript
t('notifications.appointment.created', { date: '2024-01-15' })
// "Appointment scheduled for 2024-01-15"
```

### 3. Pluralization
```javascript
tc('items.count', count, { count })
// In translation file:
{
  "items": {
    "count": {
      "zero": "No items",
      "one": "1 item",
      "other": "{{count}} items"
    }
  }
}
```

### 4. Context-Based Translation
```javascript
tx('save', 'button') // "Save"
tx('save', 'action') // "Save changes"
```

### 5. RTL Considerations
- Use logical properties: `margin-inline-start` instead of `margin-left`
- Test UI in both directions
- Handle bidirectional text properly

## Server-Side i18n

### API Usage

```python
from app.i18n import i18n_manager

# Get current language
language = i18n_manager.get_current_language()

# Translate
message = i18n_manager.translate('api.errors.not_found', language)

# Format date
formatted_date = i18n_manager.format_date(datetime.now(), 'long', language)

# Save content translation
i18n_manager.save_content_translation(
    entity_type='program',
    entity_id='123',
    field_name='description',
    content='Translated content',
    language_code='es'
)
```

### Email Templates

```python
subject = i18n_manager.translate('email.subjects.welcome', user_language)
body = render_template(f'email/welcome_{user_language}.html', **context)
```

## Testing

### Unit Tests
```javascript
import { renderWithI18n } from '../test-utils';

test('displays translated content', () => {
  const { getByText } = renderWithI18n(<MyComponent />, { language: 'es' });
  expect(getByText('Bienvenido')).toBeInTheDocument();
});
```

### Translation Validation
```javascript
import { useTranslationValidation } from '../i18n';

const { validateAllLanguages } = useTranslationValidation();
const results = await validateAllLanguages();
console.log(results);
```

## Troubleshooting

### Missing Translations
- Check browser console for missing key warnings
- Use translation validation tool
- Enable missing translation tracking

### RTL Layout Issues
- Ensure `dir` attribute is set on root element
- Use RTL-aware CSS properties
- Test with browser RTL simulation

### Performance
- Enable translation caching
- Lazy load language resources
- Use namespace splitting for large apps

## Resources

- [i18next Documentation](https://www.i18next.com/)
- [Babel Locale Data](http://babel.pocoo.org/)
- [CLDR Unicode Data](http://cldr.unicode.org/)
- [RTL Styling Guide](https://rtlstyling.com/)