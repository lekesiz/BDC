# I18n Migration Quick Start Guide

## Prerequisites

1. **Node.js** (v14 or higher)
2. **Python** (v3.8 or higher)
3. **npm** or **yarn**

## Setup

1. Navigate to the migration directory:
```bash
cd /Users/mikail/Desktop/BDC/i18n-migration
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Step-by-Step Migration

### 1. Extract Hardcoded Strings

Extract all hardcoded strings from the codebase:

```bash
# Extract from frontend (React/JSX files)
npm run extract:frontend

# Extract from backend (Python files)
npm run extract:backend

# Or extract from both
npm run extract:all
```

This will create:
- `translations/frontend-strings.json` - Frontend hardcoded strings
- `translations/backend-strings.json` - Backend hardcoded strings

### 2. Update Translation Files

Add missing keys to all language files:

```bash
npm run update:translations
```

This will:
- Add missing keys to all language JSON files
- Generate `translations/missing-keys.json` report
- Create `reports/coverage-report.json`

### 3. Review and Translate

Before migrating code, review the generated keys:
1. Check `translations/missing-keys.json`
2. Review suggested translation keys
3. Optionally modify keys in the extraction results
4. Translate placeholder entries in language files

### 4. Migrate Code (Dry Run)

First, do a dry run to see what changes will be made:

```bash
# Dry run for frontend
npm run migrate:frontend:dry

# Dry run for backend
npm run migrate:backend:dry
```

Review the reports in `reports/` directory.

### 5. Migrate Code (Actual)

When ready, perform the actual migration:

```bash
# Migrate frontend components
npm run migrate:frontend

# Migrate backend code
npm run migrate:backend

# Or migrate both
npm run migrate:all
```

### 6. Validate Implementation

Check that everything is properly migrated:

```bash
npm run validate
```

This will generate `reports/validation-report.json` with:
- Missing translation keys
- Unused translation keys
- Remaining hardcoded strings
- Translation consistency issues

## Complete Migration

Run the entire migration process:

```bash
# Dry run first
npm run migration:dry-run

# Then actual migration
npm run migration:complete
```

## Manual Tasks After Migration

1. **Review Modified Files**
   - Check git diff for all changes
   - Ensure imports are correct
   - Verify component functionality

2. **Translate Content**
   - Replace placeholder translations `[LANG] text`
   - Use professional translators for accuracy
   - Review context for each translation

3. **Test Thoroughly**
   - Test with each language
   - Check RTL layout (Arabic)
   - Verify API response translations
   - Test edge cases

4. **Update Tests**
   - Mock translation functions in tests
   - Update snapshot tests
   - Add i18n-specific tests

## Common Issues

### Issue: "Module not found" errors
**Solution**: Run `npm install` in the migration directory

### Issue: Python import errors
**Solution**: Install requirements: `pip install -r requirements.txt`

### Issue: Parser errors on JSX files
**Solution**: The parser is configured for modern JavaScript. Check for syntax errors in the source files.

### Issue: Translation key conflicts
**Solution**: Review and manually adjust keys in the extraction results before migrating

## Tips

1. **Start Small**: Test on a few files first
2. **Use Version Control**: Commit before migration
3. **Review Changes**: Check each modified file
4. **Test Incrementally**: Test after each phase
5. **Document Issues**: Keep notes on any problems

## Support

For issues or questions:
1. Check the main [README.md](README.md)
2. Review error messages in reports
3. Check script source code for options
4. Consult the [I18N Implementation Guide](../server/I18N_IMPLEMENTATION_GUIDE.md)