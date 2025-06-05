# BDC Multi-Language Support Implementation Guide

## Overview

This document describes the comprehensive internationalization (i18n) system implemented for the BDC application, supporting 7 languages with advanced features including AI-powered translations, RTL support, and professional translation workflows.

## Supported Languages

| Language | Code | Native Name | Direction | Region | Status |
|----------|------|-------------|-----------|---------|---------|
| English | `en` | English | LTR | en-US | ✅ Default |
| Turkish | `tr` | Türkçe | LTR | tr-TR | ✅ Active |
| Arabic | `ar` | العربية | RTL | ar-SA | ✅ Active |
| Spanish | `es` | Español | LTR | es-ES | ✅ Active |
| French | `fr` | Français | LTR | fr-FR | ✅ Active |
| German | `de` | Deutsch | LTR | de-DE | ✅ Active |
| Russian | `ru` | Русский | LTR | ru-RU | ✅ Active |

## Architecture

### Core Components

1. **Language Detection Service** (`app/services/i18n/language_detection_service.py`)
   - Browser language detection
   - Content-based language detection
   - Geolocation-based detection
   - User preference integration

2. **Translation Service** (`app/services/i18n/translation_service.py`)
   - UI text translations
   - Fallback language support
   - Translation file management
   - Translation coverage analysis

3. **Locale Service** (`app/services/i18n/locale_service.py`)
   - Date/time formatting
   - Number formatting
   - Currency formatting
   - Calendar localization

4. **Content Translation Service** (`app/services/i18n/content_translation_service.py`)
   - AI-powered content translation
   - Translation memory management
   - Quality scoring
   - Professional translation workflows

5. **I18n Manager** (`app/services/i18n/i18n_manager.py`)
   - Comprehensive i18n orchestration
   - Analytics and reporting
   - Bulk operations
   - System management

### Database Schema

#### Languages Table
Stores supported language configurations:
```sql
CREATE TABLE languages (
    id INTEGER PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    native_name VARCHAR(100) NOT NULL,
    direction VARCHAR(3) DEFAULT 'ltr',
    region VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    flag_icon VARCHAR(255),
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### Multilingual Content Table
Stores translated content for all entities:
```sql
CREATE TABLE multilingual_content (
    id INTEGER PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(255) NOT NULL,
    field_name VARCHAR(100) NOT NULL,
    language_code VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(20) DEFAULT 'text',
    is_original BOOLEAN DEFAULT FALSE,
    translation_status VARCHAR(20) DEFAULT 'draft',
    translation_method VARCHAR(20),
    quality_score FLOAT,
    version INTEGER DEFAULT 1,
    is_current BOOLEAN DEFAULT TRUE,
    -- User tracking fields
    created_by INTEGER,
    updated_by INTEGER,
    translated_by INTEGER,
    reviewed_by INTEGER,
    -- Timestamps
    created_at DATETIME,
    updated_at DATETIME,
    translated_at DATETIME,
    reviewed_at DATETIME,
    published_at DATETIME
);
```

#### User Language Preferences Table
Stores user-specific language settings:
```sql
CREATE TABLE user_language_preferences (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    primary_language VARCHAR(10) NOT NULL DEFAULT 'en',
    secondary_languages TEXT, -- JSON array
    enable_auto_detection BOOLEAN DEFAULT TRUE,
    detect_from_browser BOOLEAN DEFAULT TRUE,
    detect_from_content BOOLEAN DEFAULT FALSE,
    detect_from_location BOOLEAN DEFAULT FALSE,
    fallback_language VARCHAR(10) DEFAULT 'en',
    show_original_content BOOLEAN DEFAULT FALSE,
    auto_translate_content BOOLEAN DEFAULT TRUE,
    -- Translation preferences
    translation_specialties TEXT, -- JSON array
    available_for_translation BOOLEAN DEFAULT FALSE,
    translation_language_pairs TEXT, -- JSON array
    created_at DATETIME,
    updated_at DATETIME
);
```

### API Endpoints

Base URL: `/api/i18n`

#### Language Management
- `GET /languages` - Get all active languages
- `POST /languages` - Create new language (admin only)
- `PUT /languages/{code}` - Update language (admin only)

#### Language Detection
- `POST /detect-language` - Detect best language for user
- `GET /language-info/{code}` - Get comprehensive language info

#### Translation
- `POST /translate` - Translate text using AI
- `GET /translations/{key}` - Get specific translation
- `GET /translations` - Get translation dictionary

#### Content Management
- `POST /content` - Create multilingual content
- `GET /content/{type}/{id}` - Get multilingual content
- `PUT /content/{id}` - Update content

#### User Preferences
- `GET /preferences` - Get user language preferences
- `PUT /preferences` - Update user preferences

#### Locale & Formatting
- `POST /locale/{code}/format` - Format data according to locale

#### Analytics & Management
- `GET /stats` - Get translation statistics
- `POST /bulk-translate` - Bulk translate content
- `GET /export/{code}` - Export language data
- `POST /import/{code}` - Import language data

### Middleware Components

#### I18n Middleware (`app/middleware/i18n_middleware.py`)
- Automatic language detection
- Request/response language headers
- Session language persistence
- Template globals for i18n

#### Content Localization Middleware
- Automatic response content localization
- JSON response translation
- Configurable field translation

#### RTL Support Middleware
- Right-to-left language support
- Automatic HTML direction attributes
- CSS class injection for RTL layouts

## Usage Guide

### Setting Up I18n

1. **Initialize the database:**
```bash
# Run migration
flask db upgrade

# Initialize languages
flask i18n init-languages
```

2. **Register middleware in app factory:**
```python
from app.middleware.i18n_middleware import (
    i18n_middleware, content_localization_middleware, rtl_support_middleware
)

def create_app():
    app = Flask(__name__)
    
    # Initialize i18n middleware
    i18n_middleware.init_app(app)
    content_localization_middleware.init_app(app)
    rtl_support_middleware.init_app(app)
    
    return app
```

### Frontend Integration

#### Language Detection
```javascript
// Automatic language detection
fetch('/api/i18n/detect-language', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        accept_language: navigator.language,
        country_code: getUserCountry(),
        content: getCurrentPageContent()
    })
})
.then(response => response.json())
.then(data => {
    const detectedLang = data.data.detected_language;
    setApplicationLanguage(detectedLang);
});
```

#### Getting Translations
```javascript
// Get translation dictionary
async function loadTranslations(language) {
    const response = await fetch(`/api/i18n/translations?language=${language}`);
    const data = await response.json();
    return data.data.translations;
}

// Get specific translation
async function translate(key, language = 'en') {
    const response = await fetch(`/api/i18n/translations/${key}?language=${language}`);
    const data = await response.json();
    return data.data.text;
}
```

#### User Preferences
```javascript
// Update user language preferences
async function updateLanguagePreferences(preferences) {
    const response = await fetch('/api/i18n/preferences', {
        method: 'PUT',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(preferences)
    });
    return response.json();
}
```

#### RTL Support
```css
/* CSS for RTL support */
.rtl {
    direction: rtl;
    text-align: right;
}

.rtl .sidebar {
    right: 0;
    left: auto;
}

.rtl .button-group {
    flex-direction: row-reverse;
}
```

### Backend Usage

#### Creating Multilingual Content
```python
from app.services.i18n.i18n_manager import I18nManager

i18n_manager = I18nManager()

# Create content in multiple languages
content_data = {
    'en': 'Welcome to our program',
    'tr': 'Programımıza hoş geldiniz',
    'ar': 'مرحباً بكم في برنامجنا'
}

i18n_manager.create_multilingual_content(
    entity_type='program',
    entity_id='123',
    field_name='title',
    content_data=content_data,
    user_id=current_user.id
)
```

#### AI Translation
```python
from app.services.i18n.content_translation_service import (
    ContentTranslationService, TranslationRequest
)

translation_service = ContentTranslationService()

# Translate content using AI
request = TranslationRequest(
    content="Hello, welcome to our application!",
    source_language='en',
    target_language='ar',
    content_type='text',
    context='application_welcome'
)

result = translation_service.translate_content(request, user_id=user.id)
print(f"Translated: {result.translated_content}")
print(f"Confidence: {result.confidence}")
```

#### Getting Localized Content
```python
# Get content in user's language
def get_program_content(program_id, user_language):
    content = i18n_manager.get_multilingual_content(
        entity_type='program',
        entity_id=program_id,
        language_code=user_language
    )
    
    # Fallback to English if translation not available
    if not content and user_language != 'en':
        content = i18n_manager.get_multilingual_content(
            entity_type='program',
            entity_id=program_id,
            language_code='en'
        )
    
    return content
```

### CLI Management

#### Available Commands
```bash
# Initialize languages
flask i18n init-languages

# Check translation coverage
flask i18n check-translations

# Export language data
flask i18n export-language -l ar -o arabic_export.json

# Import language data
flask i18n import-language -f translations.json -l es

# Translate specific entity
flask i18n translate-entity -t program -i 123 -s en -l "tr,ar,es"

# View analytics
flask i18n analytics

# Clean up old translations
flask i18n cleanup -d 90

# Validate i18n setup
flask i18n validate
```

#### Translation File Management
```bash
# Update specific translation
flask i18n update-translation -t tr -k "common.save" -v "Kaydet"

# Check missing translations
flask i18n check-translations -l tr
```

## Advanced Features

### AI-Powered Translation

The system includes OpenAI GPT integration for automatic content translation:

```python
# Configure AI translation
AI_TRANSLATION_CONFIG = {
    'model': 'gpt-3.5-turbo',
    'max_length': 5000,
    'confidence_threshold': 0.8,
    'temperature': 0.3
}
```

### Translation Memory

Automatic translation memory for consistent translations:
- Exact match detection
- Fuzzy matching
- Usage statistics
- Quality scoring

### Professional Translation Workflow

Support for human translation workflows:
- Translation projects
- Translator assignments
- Review processes
- Quality control
- Approval workflows

### RTL Language Support

Complete right-to-left language support:
- Automatic text direction detection
- HTML `dir` attribute injection
- CSS class application
- Layout mirroring

### Locale-Specific Formatting

Comprehensive locale support:
- Date/time formatting
- Number formatting
- Currency formatting
- Calendar localization
- Cultural preferences

## Performance Considerations

### Caching Strategy
- Translation cache (1 hour TTL)
- Language detection cache
- Locale data cache
- Translation memory cache

### Database Optimization
- Optimized indexes for multilingual content
- Efficient queries for language fallbacks
- Content versioning for large translations

### Frontend Optimization
- Lazy loading of translation files
- Local storage for user preferences
- Progressive enhancement for RTL

## Security Considerations

### Input Validation
- XSS prevention in translations
- Content sanitization
- Language code validation

### Access Control
- Role-based translation management
- User preference isolation
- Admin-only language configuration

### Data Protection
- Translation audit logging
- Version control for content
- Backup and recovery procedures

## Testing

### Unit Tests
```python
# Test language detection
def test_language_detection():
    service = LanguageDetectionService()
    result = service.detect_from_browser('en-US,en;q=0.9,tr;q=0.8')
    assert result.language == 'en'

# Test translation service
def test_translation():
    service = TranslationService()
    result = service.translate('common.save', 'tr')
    assert result.text == 'Kaydet'
```

### Integration Tests
```python
# Test API endpoints
def test_language_preferences_api(client, auth_headers):
    response = client.get('/api/i18n/preferences', headers=auth_headers)
    assert response.status_code == 200
    assert 'primary_language' in response.json['data']
```

## Deployment

### Environment Variables
```bash
# OpenAI for translations
OPENAI_API_KEY=your_openai_key

# Redis for caching
REDIS_URL=redis://localhost:6379

# Language detection
DEFAULT_LANGUAGE=en
ENABLE_AUTO_DETECTION=true
```

### Production Setup
1. Run database migrations
2. Initialize languages
3. Configure caching
4. Set up translation workflows
5. Monitor translation quality

## Monitoring and Analytics

### Key Metrics
- Translation coverage per language
- Translation quality scores
- User language preferences
- API usage statistics
- Error rates

### Alerting
- Missing translations
- Low quality scores
- High error rates
- Performance issues

## Troubleshooting

### Common Issues

1. **Missing Translations**
   ```bash
   flask i18n check-translations -l tr
   ```

2. **RTL Layout Issues**
   - Check CSS RTL classes
   - Verify text direction attributes
   - Test layout components

3. **Performance Issues**
   - Monitor cache hit rates
   - Check database query performance
   - Optimize translation loading

4. **AI Translation Errors**
   - Verify OpenAI API key
   - Check request limits
   - Monitor confidence scores

## Future Enhancements

### Planned Features
- Machine learning translation quality prediction
- Automatic translation workflow optimization
- Advanced translation memory matching
- Integration with professional translation services
- Real-time collaboration on translations
- Advanced analytics and reporting

### Scalability Improvements
- Distributed translation caching
- Microservice architecture
- Edge-based language detection
- CDN integration for static translations

## Contributing

### Adding New Languages
1. Add language to `LanguageDetectionService.SUPPORTED_LANGUAGES`
2. Create translation file in `app/locales/{code}.json`
3. Add language patterns for content detection
4. Update locale mappings
5. Run `flask i18n init-languages`

### Translation Guidelines
- Use clear, concise language
- Maintain consistency across similar terms
- Consider cultural context
- Test with native speakers
- Follow accessibility guidelines

## Support

For technical support or questions about the i18n system:
- Check the troubleshooting section
- Run validation: `flask i18n validate`
- Review logs in `app/logs/`
- Contact the development team

---

**Last Updated:** 2024-01-01
**Version:** 1.0.0
**Status:** Production Ready