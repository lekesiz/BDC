# BDC Performance Tuning Guide

This guide provides comprehensive performance optimization strategies for the BDC application.

## Table of Contents
- [Frontend Performance](#frontend-performance)
- [Backend Performance](#backend-performance)
- [Database Optimization](#database-optimization)
- [Caching Strategies](#caching-strategies)
- [Network Optimization](#network-optimization)
- [Monitoring and Profiling](#monitoring-and-profiling)
- [Performance Benchmarks](#performance-benchmarks)

## Frontend Performance

### 1. React Optimization

#### Code Splitting
```javascript
// Lazy load components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const BeneficiariesPage = lazy(() => import('./pages/beneficiaries/BeneficiariesPage'));

// Use Suspense with fallback
<Suspense fallback={<LoadingSpinner />}>
  <Dashboard />
</Suspense>
```

#### React.memo and useMemo
```javascript
// Memoize expensive computations
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// Memoize components
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{data}</div>;
}, (prevProps, nextProps) => {
  return prevProps.data === nextProps.data;
});
```

#### Virtual Scrolling
```javascript
// Use react-window for large lists
import { FixedSizeList } from 'react-window';

const BigList = ({ items }) => (
  <FixedSizeList
    height={600}
    itemCount={items.length}
    itemSize={50}
    width='100%'
  >
    {({ index, style }) => (
      <div style={style}>
        {items[index]}
      </div>
    )}
  </FixedSizeList>
);
```

### 2. Bundle Size Optimization

#### Tree Shaking
```javascript
// Import only what you need
import debounce from 'lodash/debounce'; // Good
// import _ from 'lodash'; // Bad

// Use production builds
NODE_ENV=production npm run build
```

#### Dynamic Imports
```javascript
// Load libraries on demand
const loadChart = async () => {
  const { Chart } = await import('chart.js');
  return new Chart(ctx, config);
};
```

### 3. Asset Optimization

#### Image Optimization
```javascript
// Use next-gen formats
<picture>
  <source srcSet="image.webp" type="image/webp" />
  <source srcSet="image.jpg" type="image/jpeg" />
  <img src="image.jpg" alt="Description" loading="lazy" />
</picture>

// Lazy load images
const LazyImage = ({ src, alt }) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const imgRef = useRef();
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => setIsIntersecting(entry.isIntersecting),
      { threshold: 0.1 }
    );
    
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    
    return () => observer.disconnect();
  }, []);
  
  return (
    <div ref={imgRef}>
      {isIntersecting && <img src={src} alt={alt} />}
    </div>
  );
};
```

### 4. Caching Strategy

#### Service Worker
```javascript
// public/service-worker.js
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).then((response) => {
        return caches.open('v1').then((cache) => {
          cache.put(event.request, response.clone());
          return response;
        });
      });
    })
  );
});
```

## Backend Performance

### 1. Flask Optimization

#### Request Processing
```python
# Use Flask-Compress for response compression
from flask_compress import Compress
compress = Compress(app)

# Enable response caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/data')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_data():
    return jsonify(expensive_operation())
```

#### Async Operations
```python
# Use threading for I/O bound operations
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

def async_operation():
    future = executor.submit(expensive_io_operation)
    return future.result()
```

### 2. Database Query Optimization

#### Indexing Strategy
```sql
-- Add indexes for frequent queries
CREATE INDEX idx_beneficiaries_status ON beneficiaries(status);
CREATE INDEX idx_beneficiaries_created_at ON beneficiaries(created_at);
CREATE INDEX idx_users_email ON users(email);

-- Composite indexes for complex queries
CREATE INDEX idx_appointments_user_date ON appointments(user_id, appointment_date);
```

#### Query Optimization
```python
# Use eager loading to avoid N+1 queries
beneficiaries = Beneficiary.query\
    .options(joinedload(Beneficiary.user))\
    .options(joinedload(Beneficiary.programs))\
    .all()

# Use pagination for large datasets
page = request.args.get('page', 1, type=int)
per_page = 20
beneficiaries = Beneficiary.query.paginate(
    page=page, 
    per_page=per_page, 
    error_out=False
)
```

#### Connection Pooling
```python
# Configure SQLAlchemy connection pool
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
app.config['SQLALCHEMY_POOL_PRE_PING'] = True
```

### 3. API Response Optimization

#### Response Compression
```python
# Enable gzip compression
from flask_compress import Compress
compress = Compress(app)
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml',
    'application/json', 'application/javascript'
]
```

#### Partial Response
```python
# Return only requested fields
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    fields = request.args.get('fields', '').split(',')
    user = User.query.get_or_404(user_id)
    
    if fields:
        return jsonify({
            field: getattr(user, field) 
            for field in fields 
            if hasattr(user, field)
        })
    
    return jsonify(user.to_dict())
```

## Database Optimization

### 1. PostgreSQL Configuration

```ini
# postgresql.conf optimizations
shared_buffers = 256MB              # 25% of system memory
effective_cache_size = 1GB          # 50-75% of system memory
work_mem = 4MB                      # Per operation memory
maintenance_work_mem = 64MB         # For maintenance operations

# Query planning
random_page_cost = 1.1              # For SSDs
effective_io_concurrency = 200      # For SSDs
```

### 2. Query Analysis

```sql
-- Enable query stats
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT 
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Analyze query execution
EXPLAIN ANALYZE SELECT * FROM beneficiaries WHERE status = 'active';
```

### 3. Maintenance

```sql
-- Regular maintenance
VACUUM ANALYZE beneficiaries;
REINDEX INDEX idx_beneficiaries_status;

-- Auto-vacuum configuration
ALTER TABLE beneficiaries SET (autovacuum_vacuum_scale_factor = 0.1);
```

## Caching Strategies

### 1. Multi-Level Caching

```python
# Application-level cache
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_permissions(user_id):
    return User.query.get(user_id).permissions

# Redis cache for distributed systems
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key):
    data = r.get(key)
    if data:
        return json.loads(data)
    
    # Fetch from database
    data = fetch_from_database()
    r.setex(key, 300, json.dumps(data))  # Cache for 5 minutes
    return data
```

### 2. Frontend Caching

```javascript
// Local storage cache
const cache = {
  set: (key, value, ttl = 3600) => {
    const item = {
      value,
      expiry: Date.now() + ttl * 1000
    };
    localStorage.setItem(key, JSON.stringify(item));
  },
  
  get: (key) => {
    const item = localStorage.getItem(key);
    if (!item) return null;
    
    const parsed = JSON.parse(item);
    if (Date.now() > parsed.expiry) {
      localStorage.removeItem(key);
      return null;
    }
    
    return parsed.value;
  }
};

// React Query for API caching
import { QueryClient } from 'react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});
```

## Network Optimization

### 1. HTTP/2 and CDN

```nginx
# Nginx configuration
server {
    listen 443 ssl http2;
    
    # Enable gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 256;
    
    # Browser caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 2. API Batching

```javascript
// Batch multiple API requests
const batchRequests = async (requests) => {
  const response = await fetch('/api/batch', {
    method: 'POST',
    body: JSON.stringify({ requests }),
    headers: { 'Content-Type': 'application/json' }
  });
  
  return response.json();
};

// Usage
const results = await batchRequests([
  { method: 'GET', url: '/api/users/1' },
  { method: 'GET', url: '/api/beneficiaries' },
  { method: 'POST', url: '/api/programs', body: programData }
]);
```

## Monitoring and Profiling

### 1. Performance Monitoring

```javascript
// Frontend monitoring
if ('performance' in window) {
  window.addEventListener('load', () => {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    const dnsTime = perfData.domainLookupEnd - perfData.domainLookupStart;
    const tcpTime = perfData.connectEnd - perfData.connectStart;
    
    // Send to analytics
    analytics.track('performance', {
      pageLoadTime,
      dnsTime,
      tcpTime
    });
  });
}

// React component profiling
import { Profiler } from 'react';

const onRender = (id, phase, actualDuration) => {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
};

<Profiler id="Dashboard" onRender={onRender}>
  <Dashboard />
</Profiler>
```

### 2. Backend Profiling

```python
# Flask profiling
from werkzeug.middleware.profiler import ProfilerMiddleware

app.wsgi_app = ProfilerMiddleware(app.wsgi_app, 
                                  restrictions=[30],
                                  profile_dir='./profile_results')

# Custom timing decorator
import time
from functools import wraps

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        logger.info(f'{func.__name__} took {end - start:.2f}s')
        return result
    return wrapper

@timeit
def expensive_operation():
    # Your code here
    pass
```

## Performance Benchmarks

### Target Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| First Contentful Paint | < 1.2s | - | ⚡ |
| Largest Contentful Paint | < 2.5s | - | ⚡ |
| Time to Interactive | < 3.8s | - | ⚡ |
| API Response Time (avg) | < 200ms | - | ⚡ |
| Database Query Time (avg) | < 50ms | - | ⚡ |

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:5000/api/beneficiaries

# Using k6
k6 run load-test.js
```

```javascript
// load-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function() {
  let response = http.get('http://localhost:5000/api/beneficiaries');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
}
```

## Best Practices

1. **Measure Before Optimizing**: Always profile and benchmark before making optimizations
2. **Set Performance Budgets**: Define limits for bundle sizes, load times, etc.
3. **Monitor Production**: Use tools like New Relic, Datadog, or custom monitoring
4. **Progressive Enhancement**: Start with a fast baseline and enhance gradually
5. **Regular Audits**: Run Lighthouse audits and fix issues regularly

## Tools and Resources

- **Frontend**: Chrome DevTools, React DevTools, Lighthouse, WebPageTest
- **Backend**: Flask-Profiler, py-spy, cProfile, New Relic
- **Database**: pgBadger, pg_stat_statements, EXPLAIN ANALYZE
- **Network**: Chrome Network tab, Wireshark, curl
- **Load Testing**: Apache Bench, k6, JMeter, Locust