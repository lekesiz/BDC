# BDC i18n Testing System

A comprehensive internationalization (i18n) testing system for the BDC application, covering frontend components, backend APIs, language switching, and RTL layout functionality.

## Overview

This testing system ensures that the BDC application properly supports multiple languages and cultural requirements including:

- **Multi-language support**: English, Spanish, French, German, Turkish, Arabic, Hebrew, Russian
- **RTL (Right-to-Left) layout**: Arabic, Hebrew
- **Cultural formatting**: Numbers, dates, currencies
- **Dynamic language switching**: Real-time language changes
- **API internationalization**: Localized error messages and responses
- **Accessibility**: Screen reader support in multiple languages

## Directory Structure

```
tests/i18n/
├── README.md                     # This file
├── utils.js                      # Frontend testing utilities
├── utils.py                      # Backend testing utilities
├── component-tests.jsx           # React component i18n tests
├── api-tests.py                  # Backend API i18n tests
├── language-switching-tests.js   # E2E language switching tests
├── rtl-layout-tests.js          # RTL layout and styling tests
├── jest.config.js               # Jest configuration for frontend tests
├── pytest.ini                   # Pytest configuration for backend tests
├── setup.js                     # Jest setup and global mocks
├── fixtures/                    # Test data and mock translations
│   ├── translations.json        # Complete translation fixtures
│   └── user-profile.json       # Mock user profile data
└── __mocks__/                   # Jest mocks
    └── fileMock.js              # Static asset mocks
```

## Supported Languages

### LTR (Left-to-Right) Languages
- **English** (en) - Default language
- **Spanish** (es) - European Spanish
- **French** (fr) - French
- **German** (de) - German
- **Turkish** (tr) - Turkish
- **Russian** (ru) - Russian

### RTL (Right-to-Left) Languages
- **Arabic** (ar) - Standard Arabic
- **Hebrew** (he) - Modern Hebrew

## Test Categories

### 1. Component Tests (`component-tests.jsx`)

Tests React components with different languages and scenarios:

- **Basic Translation Tests**: Verify components render correct translations
- **Pluralization Tests**: Test singular/plural forms in different languages
- **Form Validation Tests**: Ensure validation messages appear in correct language
- **RTL Layout Tests**: Verify components apply correct RTL styles
- **Language Switching Tests**: Test dynamic language changes
- **Edge Cases**: Handle missing translations and invalid data

**Example Test:**
```javascript
test('renders welcome component in Spanish', () => {
  render(
    <TestWrapper language="es">
      <WelcomeComponent name="Juan" />
    </TestWrapper>
  );

  expect(screen.getByText('Bienvenido')).toBeInTheDocument();
  expect(screen.getByText('Hola Juan')).toBeInTheDocument();
});
```

### 2. API Tests (`api-tests.py`)

Tests backend API endpoints with internationalization:

- **Response Localization**: API responses in different languages
- **Error Message Translation**: Localized error messages
- **Validation Messages**: Field validation in multiple languages
- **Content Negotiation**: Accept-Language header handling
- **RTL Response Markers**: Special markers for RTL languages

**Example Test:**
```python
def test_login_success_spanish(client):
    response = client.post('/api/auth/login', 
                         json={'email': 'valid@example.com', 'password': 'password'},
                         headers={'Accept-Language': 'es'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Inicio de sesión exitoso'
```

### 3. Language Switching Tests (`language-switching-tests.js`)

End-to-end tests for dynamic language switching:

- **Basic Language Switching**: Change languages through UI
- **Page Navigation**: Language persistence across pages
- **Form Interactions**: Forms update when language changes
- **Data Display**: Numbers, dates, currency formatting
- **User Preferences**: Save/load language preferences
- **Performance**: Memory management during rapid switching

**Example Test:**
```javascript
it('should switch from English to Spanish', () => {
  cy.get('[data-testid="language-selector"]').click();
  cy.get('[data-testid="language-option-es"]').click();
  
  cy.get('[data-testid="welcome-text"]').should('contain', 'Bienvenido');
  cy.get('html').should('have.attr', 'lang', 'es');
});
```

### 4. RTL Layout Tests (`rtl-layout-tests.js`)

Comprehensive tests for Right-to-Left layout support:

- **Basic RTL Layout**: HTML dir attribute, CSS direction
- **Text Alignment**: Proper alignment for RTL languages
- **Layout Components**: Sidebar, navigation, content positioning
- **Form Elements**: Input fields, labels, validation in RTL
- **Tables and Data**: Column order and alignment
- **Icons and Images**: Directional icon flipping
- **Mixed Content**: LTR content within RTL context
- **Responsive RTL**: Mobile and tablet RTL layouts

**Example Test:**
```javascript
it('should apply RTL layout for Arabic', () => {
  cy.get('[data-testid="language-selector"]').click();
  cy.get('[data-testid="language-option-ar"]').click();
  
  cy.get('html').should('have.attr', 'dir', 'rtl');
  cy.get('body').should('have.css', 'direction', 'rtl');
  cy.get('[data-testid="main-container"]')
    .should('have.css', 'text-align', 'right');
});
```

## Test Utilities

### Frontend Utilities (`utils.js`)

- `initTestI18n(language)`: Create test i18n instance
- `switchLanguage(i18n, language)`: Helper to switch languages
- `checkRTLStyles(element, language)`: Verify RTL styling
- `formatNumber(number, language)`: Locale-specific number formatting
- `formatCurrency(amount, language)`: Currency formatting
- `formatDate(date, language)`: Date formatting
- `mockLocalStorage()`: Mock localStorage for testing

### Backend Utilities (`utils.py`)

- `create_test_app()`: Create Flask test app with i18n
- `test_api_response_translation()`: Test API endpoints with locales
- `mock_user_with_language(language)`: Create mock user with language preference
- `check_translation_completeness()`: Verify translation coverage
- `TranslationTestCase`: Base class for translation tests

## Running Tests

### Frontend Tests (Jest)

```bash
# Run all i18n component tests
npm test -- tests/i18n/component-tests.jsx

# Run with coverage
npm test -- tests/i18n/component-tests.jsx --coverage

# Watch mode
npm test -- tests/i18n/component-tests.jsx --watch
```

### Backend Tests (Pytest)

```bash
# Run all i18n API tests
pytest tests/i18n/api-tests.py -v

# Run with coverage
pytest tests/i18n/api-tests.py --cov=server/app/i18n

# Run specific test class
pytest tests/i18n/api-tests.py::TestI18nAPIEndpoints -v
```

### E2E Tests (Cypress)

```bash
# Run language switching tests
npx cypress run --spec "tests/i18n/language-switching-tests.js"

# Run RTL layout tests
npx cypress run --spec "tests/i18n/rtl-layout-tests.js"

# Run in headed mode
npx cypress open
```

## Test Configuration

### Jest Configuration (`jest.config.js`)
- Specialized configuration for i18n component tests
- Custom module mapping for i18n files
- Coverage thresholds for translation files
- Mock setup for i18next and browser APIs

### Pytest Configuration (`pytest.ini`)
- Backend i18n test configuration
- Coverage settings for i18n modules
- Test markers for different test types
- Warning filters for clean output

## Mock Data

### Translation Fixtures (`fixtures/translations.json`)
Complete mock translations for all supported languages including:
- Common UI elements
- Authentication messages
- Validation errors
- Navigation items
- Dashboard content
- Success/error messages

### User Profile Fixture (`fixtures/user-profile.json`)
Mock user data with language preferences for testing user-specific i18n features.

## Best Practices

### 1. Translation Key Testing
- Always test that translation keys exist
- Verify interpolation works correctly
- Test pluralization rules for each language
- Handle missing translations gracefully

### 2. RTL Testing
- Test layout with both RTL and LTR languages
- Verify text alignment and direction
- Check icon and image positioning
- Test mixed content scenarios

### 3. Cultural Formatting
- Test number formatting per locale
- Verify date formatting conventions
- Check currency display
- Test sorting and ordering

### 4. Performance Testing
- Test rapid language switching
- Verify memory usage during language changes
- Check lazy loading of translations
- Monitor bundle size impact

### 5. Accessibility Testing
- Test screen reader compatibility
- Verify keyboard navigation in RTL
- Check ARIA attributes in different languages
- Test high contrast mode with RTL

## Common Patterns

### Testing Component Translation
```javascript
test('component shows correct translation', () => {
  const { rerender } = render(
    <TestWrapper language="en">
      <MyComponent />
    </TestWrapper>
  );
  expect(screen.getByText('English Text')).toBeInTheDocument();

  rerender(
    <TestWrapper language="es">
      <MyComponent />
    </TestWrapper>
  );
  expect(screen.getByText('Spanish Text')).toBeInTheDocument();
});
```

### Testing API Response Localization
```python
@pytest.mark.parametrize("language", ["en", "es", "fr", "ar"])
def test_api_response_localized(client, language):
    response = client.get('/api/endpoint', 
                         headers={'Accept-Language': language})
    
    data = response.get_json()
    assert data['_locale'] == language
    assert 'message' in data
```

### Testing RTL Layout
```javascript
test('applies RTL styles correctly', () => {
  render(
    <TestWrapper language="ar">
      <RTLComponent />
    </TestWrapper>
  );
  
  const element = screen.getByTestId('component');
  expect(element).toHaveDirection('rtl');
  expect(element).toHaveStyle('text-align: right');
});
```

## Troubleshooting

### Common Issues

1. **Missing Translations**: Check translation keys exist in all language files
2. **RTL Layout Issues**: Verify CSS direction and text-align properties
3. **API Locale Issues**: Ensure Accept-Language header is properly set
4. **Test Flakiness**: Use proper async/await for language switching

### Debug Tips

1. Use `cy.debug()` in Cypress tests to inspect element state
2. Add `console.log(i18n.language)` to verify language state
3. Check browser dev tools for CSS direction properties
4. Use React Dev Tools i18next plugin for debugging

## Contributing

When adding new i18n tests:

1. Follow existing test patterns and structure
2. Add tests for both LTR and RTL languages
3. Include edge cases and error scenarios
4. Update this README with new test categories
5. Ensure tests are deterministic and don't rely on external state

## Coverage Goals

- **Component Tests**: 90%+ coverage of i18n-related components
- **API Tests**: 85%+ coverage of i18n API endpoints
- **E2E Tests**: Cover all major user workflows with language switching
- **RTL Tests**: Complete coverage of layout components in RTL mode

## Related Documentation

- [BDC i18n Implementation Guide](../../client/src/i18n/README.md)
- [Backend i18n Setup](../../server/app/i18n/README.md)
- [Translation Management](../../i18n-migration/README.md)
- [Accessibility Guidelines](../../docs/accessibility.md)