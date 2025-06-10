# BDC I18n Migration Guide

This directory contains all the necessary files and scripts for migrating the BDC project to a fully internationalized (i18n) application.

## Overview

The migration includes:
1. **Translation Key Extraction**: Identifying all hardcoded strings in both frontend and backend
2. **Translation File Updates**: Adding missing keys to all language files
3. **Code Migration**: Replacing hardcoded strings with translation keys
4. **Backend I18n**: Adding i18n support for API responses
5. **Testing**: Verifying all translations work correctly

## Directory Structure

```
i18n-migration/
├── README.md                     # This file
├── scripts/
│   ├── extract-hardcoded-strings.js    # Extract strings from frontend
│   ├── extract-backend-strings.py      # Extract strings from backend
│   ├── migrate-frontend.js             # Replace frontend strings
│   ├── migrate-backend.py              # Replace backend strings
│   └── validate-translations.js        # Validate all translations
├── translations/
│   ├── missing-keys.json              # Identified missing keys
│   ├── frontend-strings.json          # Extracted frontend strings
│   └── backend-strings.json           # Extracted backend strings
└── reports/
    ├── migration-report.md            # Migration progress report
    └── coverage-report.json           # Translation coverage stats
```

## Migration Steps

### Step 1: Extract Hardcoded Strings
```bash
# Extract frontend strings
node scripts/extract-hardcoded-strings.js

# Extract backend strings
python scripts/extract-backend-strings.py
```

### Step 2: Update Translation Files
```bash
# Add missing keys to all language files
node scripts/update-translation-files.js
```

### Step 3: Migrate Code
```bash
# Migrate frontend components
node scripts/migrate-frontend.js

# Migrate backend code
python scripts/migrate-backend.py
```

### Step 4: Validate Translations
```bash
# Validate all translations
node scripts/validate-translations.js
```

## Language Support

Current languages:
- English (en) - Default
- Turkish (tr)
- Arabic (ar) - RTL
- Spanish (es)
- French (fr)
- German (de)
- Russian (ru)

## Best Practices

1. **Key Naming Convention**:
   - Use dot notation: `section.subsection.key`
   - Be descriptive: `beneficiaries.form.firstName` not `ben.f.fn`
   - Group related keys together

2. **Translation Context**:
   - Provide context for translators
   - Include placeholders: `Welcome, {{name}}!`
   - Handle plurals properly

3. **Component Migration**:
   - Import useTranslation hook
   - Replace hardcoded strings
   - Test with different languages

4. **Backend Migration**:
   - Use translation service
   - Return translation keys in API
   - Let frontend handle translation

## Common Issues

1. **Missing Translations**: Check `translations/missing-keys.json`
2. **RTL Layout**: Test Arabic translations thoroughly
3. **Date/Time Formats**: Use locale-specific formatting
4. **Number Formats**: Consider decimal separators

## Testing

Run the test suite after migration:
```bash
# Frontend tests
cd ../client && npm test

# Backend tests
cd ../server && pytest tests/
```

## Resources

- [Frontend I18n Guide](../client/src/i18n/README.md)
- [Backend I18n Guide](../server/I18N_IMPLEMENTATION_GUIDE.md)
- [Translation Management](../server/app/cli/i18n_commands.py)