# BDC i18n Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying BDC's internationalization (i18n) features to production environments. The BDC application supports multiple languages with full RTL support, proper caching, and SEO optimization.

## Table of Contents

1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Translation File Management](#translation-file-management)
4. [Service Worker Configuration](#service-worker-configuration)
5. [CDN and Caching Strategy](#cdn-and-caching-strategy)
6. [SEO and Meta Tags](#seo-and-meta-tags)
7. [Performance Optimization](#performance-optimization)
8. [Monitoring and Analytics](#monitoring-and-analytics)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance and Updates](#maintenance-and-updates)

## Pre-deployment Checklist

### 1. Translation Completeness
- [ ] All translation files are complete and reviewed
- [ ] No missing translation keys in any supported language
- [ ] RTL languages (Arabic, Hebrew) have proper formatting
- [ ] Cultural considerations are addressed for each locale
- [ ] Date, time, and number formats are locale-appropriate

### 2. Technical Validation
- [ ] All translation files are valid JSON
- [ ] Translation keys follow consistent naming conventions
- [ ] i18n configuration is production-ready
- [ ] Service worker includes i18n caching strategies
- [ ] Bundle size impact is acceptable

### 3. Testing Requirements
- [ ] All supported languages have been tested
- [ ] RTL layout testing is complete
- [ ] Language switching works correctly
- [ ] Offline functionality is verified
- [ ] Performance benchmarks are met

## Environment Configuration

### 1. Production Environment Variables

```bash
# i18n Configuration
I18N_DEFAULT_LANGUAGE=en
I18N_SUPPORTED_LANGUAGES=en,tr,fr,es,ar,he,de,ru
I18N_FALLBACK_LANGUAGE=en
I18N_DEBUG=false

# CDN Configuration for translation files
I18N_CDN_URL=https://cdn.yourdomain.com/locales
I18N_CACHE_TTL=86400

# Performance Settings
I18N_LAZY_LOADING=true
I18N_BUNDLE_SPLITTING=true
```

### 2. Build Configuration

#### Vite Configuration (`vite.config.production.js`)

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate i18n bundle
          i18n: ['react-i18next', 'i18next', 'i18next-browser-languagedetector', 'i18next-http-backend'],
          // Separate translation files by language family
          'translations-western': [
            './src/i18n/locales/en.json',
            './src/i18n/locales/fr.json',
            './src/i18n/locales/es.json',
            './src/i18n/locales/de.json'
          ],
          'translations-eastern': [
            './src/i18n/locales/ar.json',
            './src/i18n/locales/he.json',
            './src/i18n/locales/ru.json',
            './src/i18n/locales/tr.json'
          ]
        }
      }
    }
  },
  define: {
    __I18N_SUPPORTED_LANGUAGES__: JSON.stringify(process.env.I18N_SUPPORTED_LANGUAGES?.split(',') || ['en']),
    __I18N_DEFAULT_LANGUAGE__: JSON.stringify(process.env.I18N_DEFAULT_LANGUAGE || 'en')
  }
});
```

## Translation File Management

### 1. File Structure

```
/public/locales/
├── en/
│   └── translation.json
├── tr/
│   └── translation.json
├── fr/
│   └── translation.json
├── es/
│   └── translation.json
├── ar/
│   └── translation.json
├── he/
│   └── translation.json
├── de/
│   └── translation.json
└── ru/
    └── translation.json
```

### 2. CDN Deployment Script

```bash
#!/bin/bash
# deploy-translations.sh

set -e

LOCALES_DIR="./public/locales"
CDN_BUCKET="your-cdn-bucket"
CDN_PREFIX="locales"

echo "Deploying translation files to CDN..."

# Validate all translation files
echo "Validating translation files..."
for file in $(find $LOCALES_DIR -name "*.json"); do
  if ! jq empty "$file" 2>/dev/null; then
    echo "ERROR: Invalid JSON in $file"
    exit 1
  fi
done

# Compress translation files
echo "Compressing translation files..."
find $LOCALES_DIR -name "*.json" -exec gzip -k {} \;

# Upload to CDN with appropriate headers
echo "Uploading to CDN..."
aws s3 sync $LOCALES_DIR s3://$CDN_BUCKET/$CDN_PREFIX \
  --cache-control "public, max-age=86400" \
  --content-encoding gzip \
  --content-type "application/json" \
  --metadata-directive REPLACE

echo "Translation files deployed successfully!"
```

### 3. Translation File Optimization

```javascript
// optimize-translations.js
const fs = require('fs');
const path = require('path');

function optimizeTranslationFile(filePath) {
  const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  
  // Remove comments and metadata
  const optimized = Object.keys(content)
    .filter(key => !key.startsWith('_'))
    .reduce((acc, key) => {
      acc[key] = content[key];
      return acc;
    }, {});
  
  // Write minified version
  fs.writeFileSync(filePath, JSON.stringify(optimized));
  console.log(`Optimized: ${filePath}`);
}

// Optimize all translation files
const localesDir = './public/locales';
fs.readdirSync(localesDir).forEach(lang => {
  const filePath = path.join(localesDir, lang, 'translation.json');
  if (fs.existsSync(filePath)) {
    optimizeTranslationFile(filePath);
  }
});
```

## Service Worker Configuration

### 1. Production Service Worker Updates

```javascript
// Additional configuration for production
const I18N_CACHE_VERSION = 'v1.2.0';
const I18N_CACHE_NAME = `bdc-i18n-${I18N_CACHE_VERSION}`;

// Pre-cache critical languages on install
const CRITICAL_LANGUAGES = ['en', 'tr']; // Add your most common languages

// Enhanced i18n caching strategy
async function precacheI18nAssets() {
  const cache = await caches.open(I18N_CACHE_NAME);
  const urls = CRITICAL_LANGUAGES.map(lang => `/locales/${lang}/translation.json`);
  
  try {
    await cache.addAll(urls);
    console.log('[SW] Pre-cached critical i18n assets');
  } catch (error) {
    console.error('[SW] Failed to pre-cache i18n assets:', error);
  }
}

// Call during install
self.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      // ... existing caching
      precacheI18nAssets()
    ])
  );
});
```

## CDN and Caching Strategy

### 1. CDN Configuration

#### CloudFront Configuration (AWS)

```json
{
  "Origins": [
    {
      "DomainName": "your-app-domain.com",
      "Id": "bdc-app",
      "CustomOriginConfig": {
        "HTTPPort": 443,
        "OriginProtocolPolicy": "https-only"
      }
    }
  ],
  "CacheBehaviors": [
    {
      "PathPattern": "/locales/*",
      "TargetOriginId": "bdc-app",
      "ViewerProtocolPolicy": "redirect-to-https",
      "CachePolicyId": "custom-i18n-cache-policy",
      "TTL": {
        "DefaultTTL": 86400,
        "MaxTTL": 31536000
      },
      "Compress": true
    }
  ]
}
```

### 2. Cache Headers Configuration

#### Nginx Configuration

```nginx
location /locales/ {
    # Enable gzip compression
    gzip on;
    gzip_types application/json;
    
    # Cache headers
    expires 1d;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding, Accept-Language";
    
    # CORS headers for CDN
    add_header Access-Control-Allow-Origin "*";
    add_header Access-Control-Allow-Methods "GET, OPTIONS";
    add_header Access-Control-Allow-Headers "Content-Type, Accept-Language";
    
    # Security headers
    add_header X-Content-Type-Options "nosniff";
    
    try_files $uri $uri/ =404;
}
```

## SEO and Meta Tags

### 1. Dynamic Meta Tags

```javascript
// utils/seo.js
export function updateMetaTags(language, route) {
  const langInfo = SUPPORTED_LANGUAGES[language];
  
  // Update HTML lang attribute
  document.documentElement.lang = language;
  document.documentElement.dir = langInfo.direction;
  
  // Update meta tags
  updateMetaTag('http-equiv="content-language"', language);
  updateMetaTag('name="language"', language);
  updateMetaTag('property="og:locale"', langInfo.locale);
  
  // Add alternate language links
  addAlternateLanguageLinks(route);
}

function addAlternateLanguageLinks(route) {
  // Remove existing alternate links
  document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(link => {
    link.remove();
  });
  
  // Add new alternate links
  Object.entries(SUPPORTED_LANGUAGES).forEach(([code, info]) => {
    const link = document.createElement('link');
    link.rel = 'alternate';
    link.hreflang = code;
    link.href = `${window.location.origin}/${code}${route}`;
    document.head.appendChild(link);
  });
  
  // Add x-default
  const defaultLink = document.createElement('link');
  defaultLink.rel = 'alternate';
  defaultLink.hreflang = 'x-default';
  defaultLink.href = `${window.location.origin}${route}`;
  document.head.appendChild(defaultLink);
}
```

### 2. Sitemap Generation

```javascript
// scripts/generate-sitemap.js
const fs = require('fs');
const { SUPPORTED_LANGUAGES } = require('../src/i18n/constants');

const routes = [
  '/',
  '/login',
  '/register',
  '/dashboard',
  '/beneficiaries',
  '/programs',
  '/evaluations',
  '/calendar',
  '/reports'
];

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
${routes.map(route => `
  <url>
    <loc>https://yourdomain.com${route}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
    ${Object.keys(SUPPORTED_LANGUAGES).map(lang => `
    <xhtml:link rel="alternate" hreflang="${lang}" href="https://yourdomain.com/${lang}${route}"/>
    `).join('')}
    <xhtml:link rel="alternate" hreflang="x-default" href="https://yourdomain.com${route}"/>
  </url>
`).join('')}
</urlset>`;

fs.writeFileSync('./public/sitemap.xml', sitemap);
console.log('Sitemap generated successfully!');
```

## Performance Optimization

### 1. Bundle Analysis

```bash
# Analyze bundle size impact
npm run build
npx vite-bundle-analyzer dist

# Check i18n bundle size
du -sh dist/assets/*i18n*
```

### 2. Lazy Loading Implementation

```javascript
// Enhanced lazy loading for translations
class I18nLazyLoader {
  constructor() {
    this.loadedLanguages = new Set(['en']); // Always load default
    this.loadingPromises = new Map();
  }
  
  async loadLanguage(language) {
    if (this.loadedLanguages.has(language)) {
      return Promise.resolve();
    }
    
    if (this.loadingPromises.has(language)) {
      return this.loadingPromises.get(language);
    }
    
    const loadPromise = this.fetchAndCacheLanguage(language);
    this.loadingPromises.set(language, loadPromise);
    
    try {
      await loadPromise;
      this.loadedLanguages.add(language);
      this.loadingPromises.delete(language);
    } catch (error) {
      this.loadingPromises.delete(language);
      throw error;
    }
  }
  
  async fetchAndCacheLanguage(language) {
    const response = await fetch(`/locales/${language}/translation.json`);
    
    if (!response.ok) {
      throw new Error(`Failed to load language: ${language}`);
    }
    
    const translations = await response.json();
    await i18n.addResourceBundle(language, 'translation', translations);
    
    // Cache in service worker
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'CACHE_I18N',
        payload: { language, url: response.url }
      });
    }
  }
}
```

### 3. Performance Monitoring

```javascript
// Performance monitoring for i18n
class I18nPerformanceMonitor {
  constructor() {
    this.metrics = {};
  }
  
  startTimer(operation, language) {
    const key = `${operation}_${language}`;
    this.metrics[key] = { start: performance.now() };
  }
  
  endTimer(operation, language) {
    const key = `${operation}_${language}`;
    if (this.metrics[key]) {
      const duration = performance.now() - this.metrics[key].start;
      this.metrics[key].duration = duration;
      
      // Send to analytics
      if (window.gtag) {
        window.gtag('event', 'i18n_performance', {
          event_category: 'i18n',
          event_label: `${operation}_${language}`,
          value: Math.round(duration)
        });
      }
    }
  }
  
  reportLanguageSwitch(fromLang, toLang, duration) {
    if (window.gtag) {
      window.gtag('event', 'language_switch', {
        event_category: 'i18n',
        event_label: `${fromLang}_to_${toLang}`,
        value: Math.round(duration)
      });
    }
  }
}
```

## Monitoring and Analytics

### 1. Language Usage Analytics

```javascript
// Track language usage
function trackLanguageUsage() {
  const currentLanguage = i18n.language;
  const detectedLanguage = navigator.language.split('-')[0];
  const userAgent = navigator.userAgent;
  
  // Send analytics data
  if (window.gtag) {
    window.gtag('event', 'language_detected', {
      event_category: 'i18n',
      custom_map: {
        custom_parameter_1: 'current_language',
        custom_parameter_2: 'detected_language',
        custom_parameter_3: 'user_agent'
      },
      current_language: currentLanguage,
      detected_language: detectedLanguage,
      user_agent: userAgent
    });
  }
}

// Track language preferences
function trackLanguagePreference(language, source) {
  if (window.gtag) {
    window.gtag('event', 'language_preference', {
      event_category: 'i18n',
      event_label: language,
      value: 1,
      custom_parameter: source // 'auto_detect', 'user_select', 'stored'
    });
  }
}
```

### 2. Error Monitoring

```javascript
// i18n error tracking
function setupI18nErrorMonitoring() {
  // Missing translation key tracking
  i18n.on('missingKey', (lngs, namespace, key, res) => {
    console.warn(`Missing translation: ${key} for languages: ${lngs.join(', ')}`);
    
    if (window.Sentry) {
      window.Sentry.captureMessage('Missing translation key', {
        tags: {
          component: 'i18n',
          languages: lngs.join(','),
          namespace,
          key
        }
      });
    }
  });
  
  // Language loading failure tracking
  i18n.on('failedLoading', (lng, ns, msg) => {
    console.error(`Failed to load language resource: ${lng}/${ns}`, msg);
    
    if (window.Sentry) {
      window.Sentry.captureException(new Error(`Failed to load ${lng}/${ns}: ${msg}`), {
        tags: {
          component: 'i18n',
          language: lng,
          namespace: ns
        }
      });
    }
  });
}
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Translation Files Not Loading

**Problem**: Translation files return 404 errors in production.

**Solution**:
```bash
# Check file paths in build output
ls -la dist/locales/

# Verify CDN configuration
curl -I https://your-cdn.com/locales/en/translation.json

# Check service worker cache
# Open DevTools > Application > Storage > Cache Storage
```

#### 2. RTL Layout Issues

**Problem**: RTL languages don't display correctly.

**Solution**:
```css
/* Add to your CSS build process */
[dir="rtl"] .your-component {
  text-align: right;
  direction: rtl;
}

/* Use CSS logical properties where possible */
.margin-start {
  margin-inline-start: 1rem;
}
```

#### 3. Performance Issues

**Problem**: Language switching is slow.

**Solution**:
```javascript
// Implement progressive loading
const criticalKeys = ['common', 'navigation', 'auth'];
const nonCriticalKeys = ['reports', 'analytics'];

// Load critical keys first
await i18n.loadNamespaces(criticalKeys);
// Load non-critical keys in background
setTimeout(() => i18n.loadNamespaces(nonCriticalKeys), 1000);
```

### 4. Debugging Tools

```javascript
// i18n debugging utilities
window.i18nDebug = {
  // List all loaded languages
  getLoadedLanguages: () => Object.keys(i18n.store.data),
  
  // Check missing keys
  getMissingKeys: (language) => {
    const missing = [];
    // Implementation to scan for missing keys
    return missing;
  },
  
  // Get translation statistics
  getStats: () => ({
    currentLanguage: i18n.language,
    loadedLanguages: Object.keys(i18n.store.data),
    totalKeys: Object.keys(i18n.store.data[i18n.language]?.translation || {}).length,
    cacheSize: 'Check DevTools > Application > Cache Storage'
  })
};
```

## Maintenance and Updates

### 1. Translation Update Process

```bash
#!/bin/bash
# update-translations.sh

# 1. Pull latest translations from translation service
echo "Pulling latest translations..."
curl -H "Authorization: Bearer $TRANSLATION_API_KEY" \
     "https://api.translation-service.com/projects/bdc/export" \
     -o translations.zip

# 2. Extract and validate
unzip translations.zip -d temp/
for file in temp/locales/*/*.json; do
  if ! jq empty "$file"; then
    echo "Invalid JSON: $file"
    exit 1
  fi
done

# 3. Update local files
rsync -av temp/locales/ ./public/locales/

# 4. Run tests
npm run test:i18n

# 5. Deploy if tests pass
if [ $? -eq 0 ]; then
  ./deploy-translations.sh
  echo "Translations updated successfully!"
else
  echo "Translation tests failed. Deployment aborted."
  exit 1
fi
```

### 2. Version Management

```javascript
// Translation version tracking
const TRANSLATION_VERSION = '2024.01.15';

// Add version to translation files
{
  "_meta": {
    "version": "2024.01.15",
    "lastUpdated": "2024-01-15T10:30:00Z",
    "translator": "Professional Translation Service",
    "reviewedBy": "Language Team Lead"
  },
  "common": {
    "loading": "Loading...",
    // ... rest of translations
  }
}
```

### 3. Automated Testing

```javascript
// Automated i18n tests
describe('i18n Production Tests', () => {
  test('all translation files are valid JSON', async () => {
    const languages = ['en', 'tr', 'fr', 'es', 'ar', 'he', 'de', 'ru'];
    
    for (const lang of languages) {
      const response = await fetch(`/locales/${lang}/translation.json`);
      expect(response.ok).toBe(true);
      
      const json = await response.json();
      expect(json).toBeDefined();
      expect(typeof json).toBe('object');
    }
  });
  
  test('all languages have required keys', async () => {
    const requiredKeys = ['common.loading', 'navigation.home', 'auth.login'];
    const languages = Object.keys(SUPPORTED_LANGUAGES);
    
    for (const lang of languages) {
      for (const key of requiredKeys) {
        const translation = await i18n.getFixedT(lang)(key);
        expect(translation).not.toBe(key); // Should not return the key itself
      }
    }
  });
});
```

## Production Deployment Checklist

### Final Pre-deployment Verification

- [ ] All translation files validated and optimized
- [ ] Service worker updated with i18n caching
- [ ] CDN configuration deployed and tested
- [ ] Performance benchmarks verified
- [ ] SEO meta tags implemented
- [ ] Analytics tracking configured
- [ ] Error monitoring setup
- [ ] Fallback mechanisms tested
- [ ] Browser compatibility verified
- [ ] Accessibility compliance checked
- [ ] Security headers configured
- [ ] Backup and rollback procedures documented

### Post-deployment Monitoring

1. **Real User Monitoring (RUM)**
   - Language switching performance
   - Translation loading times
   - Error rates by language

2. **Analytics Tracking**
   - Language usage patterns
   - Geographic distribution
   - User preference trends

3. **Health Checks**
   - Translation file availability
   - CDN performance
   - Cache hit rates

4. **User Feedback**
   - Translation quality reports
   - Cultural appropriateness feedback
   - Usability issues

## Support and Documentation

### Internal Team Resources

- **Translation Management**: Contact translation team for updates
- **Technical Issues**: Escalate to frontend development team
- **Performance Issues**: Monitor via APM tools and CloudWatch
- **User Reports**: Track via customer support system

### External Resources

- [react-i18next Documentation](https://react.i18next.com/)
- [i18next Best Practices](https://www.i18next.com/overview/getting-started)
- [Web Internationalization Guidelines](https://www.w3.org/International/)
- [CDN Best Practices for i18n](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)

---

**Last Updated**: January 2024  
**Version**: 1.0  
**Review Schedule**: Quarterly  
**Owner**: Frontend Development Team