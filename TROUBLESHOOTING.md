# BDC Troubleshooting Guide

This guide provides solutions to common issues encountered in the BDC application.

## Table of Contents
- [Common Issues](#common-issues)
- [Frontend Issues](#frontend-issues)
- [Backend Issues](#backend-issues)
- [Database Issues](#database-issues)
- [Authentication Issues](#authentication-issues)
- [Deployment Issues](#deployment-issues)
- [Performance Issues](#performance-issues)
- [Debugging Tips](#debugging-tips)

## Common Issues

### Application Won't Start

#### Frontend
```bash
# Check for missing dependencies
npm install

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Check for port conflicts
lsof -i :3000
kill -9 <PID>

# Start with verbose logging
npm start -- --verbose
```

#### Backend
```bash
# Check Python environment
python --version  # Should be 3.8+

# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Check for port conflicts
lsof -i :5000
kill -9 <PID>

# Start with debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### CORS Issues

**Symptoms**: "Cross-Origin Request Blocked" errors in browser console

**Solution**:
```python
# server/app/__init__.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Frontend Issues

### React Component Not Rendering

**Common causes**:
1. Import path issues
2. Case sensitivity problems
3. Missing exports

**Solutions**:
```javascript
// Check import paths
import Component from './components/Component'; // Relative path
import Component from '@/components/Component'; // Absolute path

// Check component export
export default Component;  // Default export
export { Component };      // Named export

// Debug rendering
console.log('Component props:', props);
console.log('Component state:', state);
```

### State Not Updating

**Issue**: Component doesn't re-render after state change

**Solutions**:
```javascript
// Ensure immutable updates
// Bad
state.items.push(newItem);
setState(state);

// Good
setState({
  items: [...state.items, newItem]
});

// Use functional updates for dependent state
setState(prevState => ({
  count: prevState.count + 1
}));

// Force re-render (last resort)
const [, forceUpdate] = useReducer(x => x + 1, 0);
forceUpdate();
```

### API Calls Failing

**Debugging steps**:
```javascript
// Add comprehensive error handling
try {
  const response = await api.get('/endpoint');
  console.log('Response:', response);
} catch (error) {
  console.error('API Error:', error);
  console.error('Status:', error.response?.status);
  console.error('Data:', error.response?.data);
  console.error('Headers:', error.response?.headers);
}

// Check authentication token
const token = localStorage.getItem('token');
console.log('Token exists:', !!token);
console.log('Token:', token);

// Verify API URL
console.log('API Base URL:', process.env.REACT_APP_API_URL);
```

## Backend Issues

### Database Connection Errors

**Error**: "SQLALCHEMY_DATABASE_URI not set"

**Solution**:
```python
# Check environment variables
import os
print("Database URI:", os.getenv('DATABASE_URL'))

# .env file
DATABASE_URL=postgresql://user:pass@localhost/bdc_db

# Fallback configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.getenv('DATABASE_URL') or 
    'sqlite:///app.db'
)
```

### Import Errors

**Error**: "ModuleNotFoundError"

**Solutions**:
```python
# Add project root to Python path
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Check virtual environment
which python  # Should show venv path

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Flask App Context Issues

**Error**: "Working outside of application context"

**Solution**:
```python
# For scripts/tests
from app import app

with app.app_context():
    # Your code here
    user = User.query.first()

# For background tasks
from flask import current_app

def background_task():
    with current_app.app_context():
        # Your code here
        pass
```

## Database Issues

### Migration Errors

**Issue**: "Target database is not up to date"

**Solution**:
```bash
# Check current revision
flask db current

# Upgrade to latest
flask db upgrade

# If errors persist, stamp the database
flask db stamp head

# Reset migrations (caution!)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Query Performance Issues

**Debugging**:
```python
# Enable SQL logging
app.config['SQLALCHEMY_ECHO'] = True

# Profile queries
from flask_sqlalchemy import get_debug_queries

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= 0.5:
            app.logger.warning(
                'SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' %
                (query.statement, query.parameters, query.duration, query.context)
            )
    return response

# Optimize queries
# Bad - N+1 problem
users = User.query.all()
for user in users:
    print(user.profile.bio)  # Triggers query for each user

# Good - Eager loading
users = User.query.options(joinedload(User.profile)).all()
```

## Authentication Issues

### JWT Token Issues

**Problem**: "Invalid token" or "Token expired"

**Solutions**:
```javascript
// Frontend - Token refresh
const refreshToken = async () => {
  try {
    const response = await api.post('/auth/refresh', {
      refresh_token: localStorage.getItem('refresh_token')
    });
    
    localStorage.setItem('token', response.data.access_token);
    return response.data.access_token;
  } catch (error) {
    // Redirect to login
    window.location.href = '/login';
  }
};

// Add request interceptor
api.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for 401s
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const newToken = await refreshToken();
      error.config.headers.Authorization = `Bearer ${newToken}`;
      return api(error.config);
    }
    return Promise.reject(error);
  }
);
```

### Password Reset Issues

**Problem**: Reset emails not sending

**Solutions**:
```python
# Check SMTP configuration
print("MAIL_SERVER:", app.config.get('MAIL_SERVER'))
print("MAIL_PORT:", app.config.get('MAIL_PORT'))
print("MAIL_USERNAME:", app.config.get('MAIL_USERNAME'))

# Test email sending
from flask_mail import Mail, Message

mail = Mail(app)

def test_email():
    try:
        msg = Message(
            'Test Email',
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=['test@example.com']
        )
        msg.body = 'This is a test email'
        mail.send(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Email error: {e}")
```

## Deployment Issues

### Docker Container Issues

**Problem**: Container won't start

**Solutions**:
```bash
# Check logs
docker logs <container_name>

# Debug container
docker run -it <image_name> /bin/sh

# Check environment variables
docker exec <container_name> env

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Nginx Configuration Issues

**Problem**: 502 Bad Gateway

**Solutions**:
```nginx
# Check upstream server
upstream app {
    server localhost:5000;  # Ensure Flask is running on this port
}

# Increase timeouts
location / {
    proxy_pass http://app;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    proxy_send_timeout 300s;
}

# Check Nginx error logs
tail -f /var/log/nginx/error.log
```

### SSL/HTTPS Issues

**Problem**: SSL certificate errors

**Solutions**:
```bash
# Check certificate validity
openssl s_client -connect yourdomain.com:443

# Renew Let's Encrypt certificate
certbot renew

# Check certificate configuration
nginx -t
```

## Performance Issues

### Slow Page Loads

**Debugging**:
```javascript
// Frontend performance
console.time('Component Render');
// Component code
console.timeEnd('Component Render');

// Check bundle size
npm run build
ls -la build/static/js/

// Profile React components
const ProfiledComponent = React.Profiler(
  'ComponentName',
  (id, phase, actualDuration) => {
    console.log(`${id} (${phase}) took ${actualDuration}ms`);
  }
);
```

### Memory Leaks

**Frontend**:
```javascript
// Clean up subscriptions
useEffect(() => {
  const subscription = dataSource.subscribe();
  
  return () => {
    subscription.unsubscribe();
  };
}, []);

// Clear timers
useEffect(() => {
  const timer = setTimeout(() => {}, 1000);
  
  return () => {
    clearTimeout(timer);
  };
}, []);
```

**Backend**:
```python
# Monitor memory usage
import psutil
import os

process = psutil.Process(os.getpid())
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB")

# Use generators for large datasets
def get_large_dataset():
    for i in range(1000000):
        yield process_item(i)  # Instead of loading all at once
```

## Debugging Tips

### Enable Debug Mode

**Frontend**:
```javascript
// Add to .env.development
REACT_APP_DEBUG=true

// In code
if (process.env.REACT_APP_DEBUG === 'true') {
  console.log('Debug info:', data);
}
```

**Backend**:
```python
# Enable Flask debug mode
app.config['DEBUG'] = True

# Add debug toolbar
from flask_debugtoolbar import DebugToolbarExtension
toolbar = DebugToolbarExtension(app)

# Custom debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Browser DevTools

```javascript
// Debugging React components
// Install React Developer Tools extension

// Check component props/state
$r.props
$r.state

// Profile performance
performance.mark('myTask:start');
// Code to profile
performance.mark('myTask:end');
performance.measure('myTask', 'myTask:start', 'myTask:end');
```

### Network Debugging

```bash
# Monitor API calls
curl -v http://localhost:5000/api/users

# Check headers
curl -I http://localhost:5000/api/users

# Test with authentication
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/users
```

### Database Debugging

```sql
-- Check active connections
SELECT pid, usename, application_name, state 
FROM pg_stat_activity;

-- Kill stuck queries
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle in transaction' 
AND query_start < current_timestamp - interval '10 minutes';

-- Check table sizes
SELECT 
    schemaname AS table_schema,
    tablename AS table_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Getting Help

If you can't resolve an issue:

1. Check existing [GitHub Issues](https://github.com/your-org/bdc/issues)
2. Search error messages in documentation
3. Create a detailed bug report with:
   - Error messages/screenshots
   - Steps to reproduce
   - Environment details
   - Relevant logs

Remember to sanitize any sensitive information before sharing logs or screenshots!