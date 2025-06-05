# API Versioning Strategy

## Current Status
- Both `/api/` and `/api/v2/` endpoints are active
- No clear deprecation strategy
- Duplicate endpoint implementations

## Recommended Strategy

### 1. Version Structure
```
/api/v1/  - Current stable API (rename from /api/)
/api/v2/  - New features and breaking changes
```

### 2. Migration Plan

#### Phase 1: Setup (Immediate)
```python
# In app/__init__.py
API_VERSION_1 = '/api/v1'
API_VERSION_2 = '/api/v2'
API_LATEST = API_VERSION_2  # Point to latest stable
```

#### Phase 2: Redirect (1 month)
```python
# Redirect /api/ to /api/v1/
@app.route('/api/<path:path>')
def redirect_to_v1(path):
    return redirect(f'/api/v1/{path}', code=301)
```

#### Phase 3: Deprecation Headers
```python
# Add deprecation headers to v1 endpoints
@app.after_request
def add_deprecation_header(response):
    if request.path.startswith('/api/v1/'):
        response.headers['X-API-Deprecation-Date'] = '2025-06-01'
        response.headers['X-API-Deprecation-Info'] = 'Please migrate to /api/v2/'
    return response
```

### 3. Implementation

#### Create Version Manager
```python
# app/api/version_manager.py
class APIVersionManager:
    def __init__(self):
        self.versions = {
            'v1': {
                'status': 'deprecated',
                'deprecation_date': '2025-06-01',
                'endpoints': []
            },
            'v2': {
                'status': 'stable',
                'endpoints': []
            }
        }
    
    def register_endpoint(self, version, endpoint):
        self.versions[version]['endpoints'].append(endpoint)
    
    def get_active_versions(self):
        return [v for v, info in self.versions.items() 
                if info['status'] != 'retired']
```

#### Update Blueprint Registration
```python
# app/api/__init__.py
from flask import Blueprint

# Version 1 (Current API)
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Version 2 (New API)
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Register blueprints
def register_api_blueprints(app):
    app.register_blueprint(api_v1)
    app.register_blueprint(api_v2)
```

### 4. Documentation

#### API Version Documentation
```yaml
# openapi_spec.yaml
openapi: 3.0.0
servers:
  - url: /api/v1
    description: Stable API (Deprecated - EOL 2025-06-01)
  - url: /api/v2
    description: Current API Version
```

### 5. Client Migration Guide

#### For Frontend
```javascript
// config/api.js
const API_VERSION = process.env.REACT_APP_API_VERSION || 'v2';
const API_BASE_URL = `/api/${API_VERSION}`;

// Gradual migration
const endpoints = {
  // Migrated to v2
  auth: `${API_BASE_URL}/auth`,
  users: `${API_BASE_URL}/users`,
  
  // Still on v1 (to be migrated)
  legacy: '/api/v1/legacy'
};
```

### 6. Timeline

- **Week 1**: Implement version manager and redirects
- **Week 2**: Add deprecation headers and notifications
- **Month 1-3**: Client migration period
- **Month 4**: Remove v1 endpoints

### 7. Best Practices

1. **No Breaking Changes in Minor Versions**
   - v2.0 → v2.1: Only additions, no breaking changes
   - v2.x → v3.0: Breaking changes allowed

2. **Version in Headers**
   ```
   X-API-Version: 2.0
   Accept: application/vnd.bdc.v2+json
   ```

3. **Clear Error Messages**
   ```json
   {
     "error": "Endpoint deprecated",
     "message": "This v1 endpoint is deprecated. Use /api/v2/users instead",
     "migration_guide": "https://docs.bdc.com/api/migration"
   }
   ```

### 8. Monitoring

Track usage of deprecated endpoints:
```python
# app/utils/metrics.py
def track_api_usage(version, endpoint):
    # Log to monitoring service
    current_app.logger.info(f"API Usage: {version} - {endpoint}")
    # Send to metrics collector
    metrics.increment(f'api.{version}.{endpoint}')
```

## Action Items
1. ✅ Create this strategy document
2. ⬜ Implement version manager
3. ⬜ Setup redirects from /api/ to /api/v1/
4. ⬜ Add deprecation headers
5. ⬜ Update documentation
6. ⬜ Notify clients about migration
7. ⬜ Monitor v1 usage
8. ⬜ Complete migration by June 2025