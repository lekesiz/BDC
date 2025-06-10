# Real-Time Data Synchronization System

A comprehensive real-time data synchronization system for the BDC project that provides seamless data consistency across multiple clients and devices.

## Features

### Core Components

1. **WebSocket Connection Manager** (`websocket_manager.py`)
   - Real-time bidirectional communication
   - Connection pooling and load balancing
   - Authentication and session management
   - Heartbeat monitoring and automatic reconnection
   - Message routing and broadcasting

2. **Offline/Online State Handler** (`offline_handler.py`)
   - Network state detection and monitoring
   - Operation queuing during offline periods
   - Automatic retry with exponential backoff
   - Conflict detection preparation
   - Persistent storage of queued operations

3. **Conflict Resolution System** (`conflict_resolver.py`)
   - Multiple resolution strategies (Last Write Wins, Three-way Merge, etc.)
   - Custom business rule-based resolution
   - Operational Transform for text editing
   - User-driven conflict resolution with fallback strategies
   - Conflict history and analytics

4. **Data Versioning and Merging** (`version_manager.py`)
   - Version creation and management
   - Change tracking with detailed metadata
   - Branch management for complex scenarios
   - Automatic and manual merge operations
   - Compression for storage efficiency

5. **Event Sourcing System** (`event_sourcing.py`)
   - Immutable event logging
   - Event replay and reconstruction capabilities
   - Snapshot management for performance
   - Audit trail generation and querying
   - Event projections and aggregations

6. **Cross-Device Synchronization** (`device_sync.py`)
   - Device registration and capability management
   - Intelligent sync scheduling
   - Bandwidth-aware synchronization
   - Selective sync based on device type and data categories
   - Real-time sync notifications

7. **Main Sync Service** (`sync_service.py`)
   - Orchestrates all synchronization components
   - Unified interface for sync operations
   - Performance monitoring and optimization
   - Extensible plugin architecture
   - Request/response handling

8. **Configuration Management** (`config.py`)
   - Centralized configuration for all components
   - Environment-based configuration loading
   - Runtime configuration updates
   - Validation and defaults

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Sync Service                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   WebSocket     │  │   Offline       │  │   Device     │ │
│  │   Manager       │  │   Handler       │  │   Sync       │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Conflict      │  │   Version       │  │   Event      │ │
│  │   Resolver      │  │   Manager       │  │   Sourcing   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Basic Setup

```python
from app.services.sync import SyncService, SyncConfig

# Create configuration
config = SyncConfig()
config.jwt_secret = "your-jwt-secret"
config.websocket.heartbeat_interval = 30

# Initialize sync service
sync_service = SyncService(config)

# Start the service
await sync_service.start()
```

### Processing Sync Requests

```python
from app.services.sync import SyncRequest, SyncPriority

# Create a sync request
request = SyncRequest(
    entity_type="Document",
    entity_id="doc-123",
    operation="update",
    data={"title": "Updated Document", "content": "New content"},
    user_id="user-456",
    device_id="device-789",
    priority=SyncPriority.HIGH
)

# Process the request
response = await sync_service.process_sync_request(request)

if response.success:
    print(f"Sync successful: {response.version_id}")
else:
    print(f"Sync failed: {response.error_message}")
```

### Device Registration

```python
from app.services.sync import DeviceInfo, DeviceType, DeviceCapabilities, DataCategory

# Create device info
device_info = DeviceInfo(
    device_type=DeviceType.MOBILE,
    device_name="User's iPhone",
    platform="iOS",
    app_version="1.0.0",
    capabilities=DeviceCapabilities(
        storage_capacity=1024*1024*1024,  # 1GB
        bandwidth_limit=1024*1024,       # 1MB/s
        supports_real_time=True,
        supports_offline=True,
        sync_categories=[DataCategory.DOCUMENTS, DataCategory.SETTINGS]
    )
)

# Register device
device_id = await sync_service.register_device("user-456", device_info)
```

### WebSocket Integration

```python
# Handle WebSocket connections
async def handle_websocket(websocket, path):
    await sync_service.websocket_manager.handle_connection(websocket, path)

# Start WebSocket server
import websockets
start_server = websockets.serve(handle_websocket, "localhost", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
```

## Configuration

### Environment Variables

```bash
export BDC_SYNC_JWT_SECRET="your-jwt-secret"
export BDC_SYNC_WS_HEARTBEAT_INTERVAL=30
export BDC_SYNC_OFFLINE_STORAGE_PATH="/var/lib/bdc/sync"
export BDC_SYNC_LOG_LEVEL="INFO"
export BDC_SYNC_ENABLE_COMPRESSION=true
```

### Configuration File (sync_config.yaml)

```yaml
websocket:
  heartbeat_interval: 30
  max_connections: 10000
  compression_enabled: true

offline:
  storage_path: "/var/lib/bdc/sync"
  max_queue_size: 10000
  connectivity_check_interval: 5

security:
  jwt_secret: "your-jwt-secret"
  require_authentication: true

monitoring:
  log_level: "INFO"
  enable_metrics: true
```

## Advanced Features

### Custom Conflict Resolution

```python
async def custom_document_resolver(conflict, context):
    """Custom resolver for document conflicts"""
    
    # Implement custom business logic
    if conflict.entity_type == "Document":
        # Merge based on document type
        return {
            'success': True,
            'merged_data': merge_documents(context['version_data']),
            'metadata': {'strategy': 'document_merge'}
        }
    
    return {'success': False}

# Register custom resolver
sync_service.conflict_resolver.add_custom_rule("Document", custom_document_resolver)
```

### Event Handling

```python
async def document_event_handler(event):
    """Handle document-related events"""
    if event.event_type == EventType.DATA_UPDATED:
        print(f"Document {event.aggregate_id} was updated")
        # Trigger additional processing

# Subscribe to events
sync_service.event_service.subscribe_to_aggregate("Document", document_event_handler)
```

### Custom Middleware

```python
async def audit_middleware(request):
    """Log all sync requests for auditing"""
    logger.info(f"Sync request: {request.operation} on {request.entity_type}:{request.entity_id}")
    return request

# Add middleware
sync_service.add_middleware(audit_middleware)
```

## Performance Monitoring

```python
# Get service metrics
metrics = sync_service.get_metrics()
print(f"Requests processed: {metrics['requests_processed']}")
print(f"Average response time: {metrics['avg_response_time']:.2f}s")
print(f"Active connections: {metrics['active_connections']}")

# Get detailed status
status = sync_service.get_status()
print(f"Service state: {status['state']}")
print(f"Component health: {status['components']}")
```

## Testing

### Unit Tests

```python
import pytest
from app.services.sync import SyncService, SyncConfig

@pytest.fixture
async def sync_service():
    config = SyncConfig.create_test_config()
    service = SyncService(config)
    await service.start()
    yield service
    await service.stop()

async def test_sync_request(sync_service):
    request = SyncRequest(
        entity_type="TestEntity",
        entity_id="test-123",
        operation="create",
        data={"name": "Test"},
        user_id="user-123",
        device_id="device-123"
    )
    
    response = await sync_service.process_sync_request(request)
    assert response.success
    assert response.version_id is not None
```

### Integration Tests

```python
async def test_websocket_sync():
    # Test WebSocket-based synchronization
    async with websockets.connect("ws://localhost:8765") as websocket:
        # Send authentication
        await websocket.send(json.dumps({
            "type": "authenticate",
            "token": "valid-jwt-token"
        }))
        
        # Send sync request
        await websocket.send(json.dumps({
            "type": "sync_request",
            "entity_type": "Document",
            "entity_id": "doc-123",
            "operation": "update",
            "data": {"title": "Updated via WebSocket"}
        }))
        
        # Receive response
        response = await websocket.recv()
        assert json.loads(response)["success"]
```

## Deployment

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
EXPOSE 8765

CMD ["python", "-m", "app.services.sync.main"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: bdc-sync-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: bdc-sync-service
  template:
    metadata:
      labels:
        app: bdc-sync-service
    spec:
      containers:
      - name: sync-service
        image: bdc/sync-service:latest
        ports:
        - containerPort: 8765
        env:
        - name: BDC_SYNC_JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: sync-secrets
              key: jwt-secret
```

## Security Considerations

1. **Authentication**: All WebSocket connections require JWT authentication
2. **Rate Limiting**: Built-in rate limiting to prevent abuse
3. **Data Encryption**: Optional encryption for sensitive data
4. **Audit Logging**: Complete audit trail of all sync operations
5. **Input Validation**: Comprehensive validation of all inputs
6. **CORS**: Configurable CORS settings for web clients

## Performance Optimization

1. **Connection Pooling**: Efficient WebSocket connection management
2. **Data Compression**: Optional compression for large payloads
3. **Batching**: Batch processing of multiple operations
4. **Caching**: Intelligent caching of frequently accessed data
5. **Indexing**: Optimized indexing for fast queries
6. **Horizontal Scaling**: Support for multiple service instances

## Troubleshooting

### Common Issues

1. **Connection Drops**: Check network stability and heartbeat settings
2. **Conflict Resolution Failures**: Review conflict resolution strategies
3. **High Memory Usage**: Enable compression and adjust cache settings
4. **Slow Sync Performance**: Check bandwidth limits and batch sizes

### Logging

Enable debug logging for detailed troubleshooting:

```python
import logging
logging.getLogger('app.services.sync').setLevel(logging.DEBUG)
```

### Health Checks

```python
# Check service health
status = sync_service.get_status()
if status['state'] != 'running':
    print("Service is not running properly")
    
# Check component health
for component, healthy in status['components'].items():
    if not healthy:
        print(f"Component {component} is unhealthy")
```

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure all components integrate properly with the main sync service

## License

This synchronization system is part of the BDC project and follows the project's licensing terms.