# BDC Performance Optimization System

## Overview

This comprehensive performance optimization system provides advanced performance monitoring, optimization, and testing capabilities for the BDC application. It includes both backend and frontend optimizations with real-time monitoring and intelligent caching strategies.

## Features

### 🚀 Core Performance Optimizer
- **Multi-level optimization**: Basic, Moderate, and Aggressive optimization levels
- **Intelligent caching**: Redis, memory, and distributed caching with adaptive strategies
- **Automatic optimization**: Self-tuning based on performance metrics
- **Real-time monitoring**: Performance tracking with alerting and reporting

### 🗄️ Database Optimization
- **Query optimization**: Automatic query analysis and optimization suggestions
- **Index management**: Intelligent index creation and maintenance
- **Connection pooling**: Optimized database connections with monitoring
- **Slow query detection**: Automatic identification and optimization of slow queries

### 🔄 Caching Strategies
- **Multi-level caching**: L1 (memory), L2 (Redis), L3 (database) caching
- **Cache warming**: Intelligent preloading of frequently accessed data
- **Compression**: Automatic compression for large cached values
- **Invalidation**: Smart cache invalidation with tag-based strategies

### 🌐 API Response Optimization
- **Response compression**: Gzip, Brotli, and adaptive compression
- **Pagination optimization**: Cursor-based and keyset pagination
- **ETags and conditional requests**: Efficient caching with validation
- **Response streaming**: Large dataset streaming with chunked encoding

### 📊 Performance Monitoring
- **Real-time metrics**: CPU, memory, response times, and custom metrics
- **Web Vitals**: LCP, FID, CLS, and other Core Web Vitals tracking
- **Profiling**: Code-level performance analysis with hotspot detection
- **Alerting**: Configurable alerts for performance thresholds

### 🖼️ Asset Optimization
- **Image optimization**: Automatic format conversion (WebP, AVIF) and compression
- **Responsive images**: Multi-resolution image generation for different devices
- **CDN integration**: Multi-provider CDN support with intelligent routing
- **Lazy loading**: Intelligent asset loading based on viewport

### 🧪 Load Testing & Benchmarking
- **Load testing**: Realistic user simulation with various load patterns
- **Stress testing**: Determine breaking points and scaling limits
- **Benchmarking**: Performance comparison across versions and configurations
- **Reporting**: Comprehensive performance reports with recommendations

## Installation & Setup

### Backend Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Initialize the performance optimizer**:
```python
from app.performance import PerformanceOptimizer
from app.performance.config import PerformanceConfig

# Initialize with configuration
config = PerformanceConfig()
optimizer = PerformanceOptimizer(config)

# Initialize with Flask app
optimizer.init_app(app)
```

3. **Configure Redis (optional but recommended)**:
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
redis-server

# Configure in your app
REDIS_URL=redis://localhost:6379/0
```

### Frontend Setup

1. **Install the performance module**:
```javascript
import PerformanceOptimizer from './src/performance/PerformanceOptimizer';

// Initialize with configuration
const optimizer = new PerformanceOptimizer({
  optimization: {
    level: 'moderate',
    enableLazyLoading: true,
    enableImageOptimization: true
  }
});

// Initialize the optimizer
await optimizer.init();
```

2. **Optimize components**:
```javascript
import { optimizeComponent } from './src/performance';

// Optimize a React component
const OptimizedComponent = optimizeComponent(MyComponent, {
  lazy: true,
  memo: true,
  errorBoundary: true
});
```

## Configuration

### Environment-based Configuration

The system automatically adapts based on the environment:

- **Development**: Basic optimizations, detailed logging, no rate limiting
- **Staging**: Moderate optimizations, load testing enabled
- **Production**: Aggressive optimizations, full monitoring, security enabled

### Custom Configuration

Create a `performance_config.yaml` file:

```yaml
optimization_level: moderate
enable_debug_mode: false

database:
  enable_query_optimization: true
  slow_query_threshold: 1.0
  connection_pool_size: 20

cache:
  enable_redis: true
  redis_url: "redis://localhost:6379/0"
  default_ttl: 3600
  enable_compression: true

api:
  enable_response_compression: true
  compression_level: 6
  enable_pagination_optimization: true
  default_page_size: 25

monitoring:
  enable_performance_monitoring: true
  monitoring_interval: 30
  alert_thresholds:
    response_time_ms: 1000
    error_rate_percent: 5

assets:
  enable_image_optimization: true
  image_quality_jpeg: 85
  enable_responsive_images: true
  responsive_breakpoints: [320, 480, 768, 1024, 1920]
```

## Usage Examples

### Database Optimization

```python
from app.performance.database import QueryOptimizer, IndexManager

# Initialize optimizers
query_optimizer = QueryOptimizer(db)
index_manager = IndexManager(db)

# Optimize a query
optimized_query = query_optimizer.optimize(
    "SELECT * FROM users WHERE email = %s",
    {"email": "user@example.com"}
)

# Suggest indexes
index_suggestions = index_manager.suggest_indexes()
for suggestion in index_suggestions:
    print(f"Suggested index: {suggestion.table_name}({', '.join(suggestion.columns)})")
```

### Caching

```python
from app.performance.caching import CacheManager

# Initialize cache manager
cache = CacheManager(app)

# Cache a function result
@cache.cache_function(ttl=3600, tags=['user_data'])
def get_user_profile(user_id):
    return db.session.query(User).filter_by(id=user_id).first()

# Manual caching
cache.set('user_profile_123', user_data, ttl=3600)
cached_data = cache.get('user_profile_123')

# Cache invalidation by tags
cache.invalidate_by_tags(['user_data'])
```

### API Response Optimization

```python
from app.performance.api import ResponseOptimizer, PaginationOptimizer

# Initialize optimizers
response_optimizer = ResponseOptimizer()
pagination_optimizer = PaginationOptimizer()

# Optimize API response
@app.route('/api/users')
def get_users():
    query = User.query
    
    # Apply pagination
    result = pagination_optimizer.paginate_query(
        query, 
        page=request.args.get('page', 1),
        per_page=25,
        pagination_type=PaginationType.CURSOR
    )
    
    # Create optimized response
    return response_optimizer.optimize_json_response(result)
```

### Image Optimization

```python
from app.performance.assets import ImageOptimizer

# Initialize image optimizer
image_optimizer = ImageOptimizer()

# Optimize a single image
result = image_optimizer.optimize_image(
    'path/to/image.jpg',
    target_format=ImageFormat.WEBP,
    optimization_level=OptimizationLevel.MODERATE
)

print(f"Optimized: {result.original_size} -> {result.optimized_size} bytes")
print(f"Compression ratio: {result.compression_ratio:.2%}")

# Generate responsive images
variants = image_optimizer.generate_responsive_image(
    'path/to/image.jpg',
    breakpoints=[480, 768, 1024, 1920]
)
```

### Load Testing

```python
from app.performance.testing import LoadTester, LoadTestConfig

# Configure load test
config = LoadTestConfig(
    base_url="http://localhost:5000",
    endpoints=["/api/users", "/api/posts"],
    concurrent_users=50,
    duration_seconds=300,
    pattern=LoadPattern.RAMP_UP
)

# Run load test
load_tester = LoadTester(config)
result = await load_tester.run_load_test("API Performance Test")

print(f"Total requests: {result.total_requests}")
print(f"Average response time: {result.avg_response_time:.2f}ms")
print(f"Requests per second: {result.requests_per_second:.2f}")
print(f"Error rate: {result.failed_requests / result.total_requests:.2%}")
```

### Performance Monitoring

```python
from app.performance.monitoring import PerformanceMonitor

# Initialize monitor
monitor = PerformanceMonitor()
await monitor.init()

# Record custom metrics
monitor.record_metrics({
    'custom_operation_time': 150.5,
    'cache_hit_rate': 85.2,
    'active_users': 1250
})

# Get performance summary
summary = monitor.getSummary()
print(f"Performance score: {summary['performanceScore']}/100")

# Generate performance report
report = monitor.generate_performance_report()
```

## Performance Monitoring Dashboard

### Web Vitals Tracking

The system automatically tracks Core Web Vitals:

- **LCP (Largest Contentful Paint)**: < 2.5s (Good)
- **FID (First Input Delay)**: < 100ms (Good)
- **CLS (Cumulative Layout Shift)**: < 0.1 (Good)

### Custom Metrics

Track application-specific metrics:

```javascript
// Record custom performance metrics
performanceOptimizer.recordMetric('database_query_time', 45.2);
performanceOptimizer.recordMetric('api_response_size', 1024);
performanceOptimizer.recordMetric('user_action_completion_time', 250);
```

### Alerting

Configure alerts for performance thresholds:

```python
# Add custom alert rules
monitor.add_alert_rule(
    name='slow_api_response',
    metric_name='avg_response_time',
    threshold=1000,  # 1 second
    comparison='gt',
    level=AlertLevel.WARNING
)
```

## Best Practices

### 1. Database Optimization
- **Use indexes wisely**: Don't over-index; focus on frequently queried columns
- **Optimize queries**: Use EXPLAIN to understand query execution plans
- **Connection pooling**: Configure appropriate pool sizes for your workload
- **Monitor slow queries**: Set appropriate thresholds for your application

### 2. Caching Strategy
- **Cache at multiple levels**: Use L1 (memory), L2 (Redis), and L3 (database) caching
- **Set appropriate TTLs**: Balance between performance and data freshness
- **Use cache tags**: Enable efficient cache invalidation
- **Monitor cache hit rates**: Aim for >80% hit rates

### 3. API Performance
- **Use pagination**: Implement cursor-based pagination for large datasets
- **Enable compression**: Use Gzip or Brotli for API responses
- **Implement ETags**: Reduce bandwidth with conditional requests
- **Rate limiting**: Protect against abuse and ensure fair usage

### 4. Asset Optimization
- **Optimize images**: Use modern formats (WebP, AVIF) when supported
- **Implement responsive images**: Serve appropriate sizes for different devices
- **Use CDN**: Distribute assets globally for better performance
- **Enable lazy loading**: Load assets only when needed

### 5. Monitoring & Alerting
- **Set realistic thresholds**: Base alerts on actual user impact
- **Monitor trends**: Look for gradual performance degradation
- **Regular reporting**: Generate and review performance reports
- **Proactive optimization**: Address issues before they impact users

## Troubleshooting

### Common Issues

1. **High memory usage**:
   - Check cache sizes and TTLs
   - Monitor for memory leaks
   - Optimize image processing

2. **Slow database queries**:
   - Review query optimization suggestions
   - Check index usage
   - Monitor connection pool health

3. **Low cache hit rates**:
   - Review cache key strategies
   - Check TTL settings
   - Monitor cache eviction patterns

4. **High response times**:
   - Check for slow endpoints
   - Review compression settings
   - Monitor system resources

### Performance Debugging

Enable debug mode for detailed logging:

```python
config = PerformanceConfig({
    'enable_debug_mode': True,
    'monitoring': {
        'monitoring_interval': 5  # More frequent monitoring
    }
})
```

### Health Checks

The system provides built-in health checks:

```bash
# Check system health
curl http://localhost:5000/health/performance

# Get performance metrics
curl http://localhost:5000/api/performance/metrics

# Get optimization recommendations
curl http://localhost:5000/api/performance/recommendations
```

## Contributing

To contribute to the performance optimization system:

1. **Fork the repository**
2. **Create a feature branch**
3. **Add tests for new functionality**
4. **Ensure performance benchmarks pass**
5. **Submit a pull request**

### Testing

Run the performance test suite:

```bash
# Backend tests
python -m pytest app/performance/tests/

# Frontend tests
npm run test:performance

# Load tests
python -m pytest app/performance/tests/test_load_testing.py

# Benchmarks
python scripts/run_benchmarks.py
```

## License

This performance optimization system is part of the BDC project and follows the same licensing terms.