# BDC Client Internationalization (i18n) Guide

## Overview
The BDC client application supports multiple languages including English, Turkish (Türkçe), French (Français), and Spanish (Español).

## Available Languages
- **English** (en) - Default
- **Turkish** (tr) - Türkçe
- **French** (fr) - Français  
- **Spanish** (es) - Español

## Usage

### Basic Usage with Hook
```jsx
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('common.welcome')}</h1>
      <button>{t('common.save')}</button>
    </div>
  );
}
```

### Using Custom Hook
```jsx
import { useTranslations } from '@/hooks/useTranslations';

function MyComponent() {
  const { common, navigation } = useTranslations();
  
  return (
    <div>
      <h1>{common.welcome()}</h1>
      <nav>
        <a href="/dashboard">{navigation.dashboard()}</a>
        <a href="/beneficiaries">{navigation.beneficiaries()}</a>
      </nav>
    </div>
  );
}
```

### Changing Language
The language can be changed in two ways:

1. **Using the Language Selector in Header** - Click the globe icon in the header
2. **Using the Settings Page** - Go to Settings > Preferences > Display Language

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

### Interpolation
For dynamic values:
```jsx
// Translation file
{
  "validation": {
    "minLength": "Must be at least {{min}} characters"
  }
}

// Usage
t('validation.minLength', { min: 8 })
```

### Language Persistence
The selected language is automatically saved to localStorage and will be remembered on page reload.

### Testing Different Languages
You can quickly test different languages by:
1. Opening the browser console
2. Running: `localStorage.setItem('i18nextLng', 'tr')` (or 'en', 'fr', 'es')
3. Refreshing the page

## Turkish Translation Notes
The Turkish translations include:
- Proper Turkish grammar and spelling
- Context-appropriate translations (not literal)
- Technical terms that are commonly used in Turkish IT contexts
- Formal language suitable for a professional application