"""
Main Synchronization Service

Orchestrates all synchronization components and provides a unified interface:
- Coordinates WebSocket connections, offline handling, conflict resolution
- Manages data versioning and event sourcing
- Provides high-level sync operations
- Handles service lifecycle and configuration
- Monitors sync health and performance
- Exposes APIs for external integration
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .websocket_manager import WebSocketManager, Message
from .offline_handler import OfflineHandler, OperationType, OperationPriority
from .conflict_resolver import ConflictResolver, ResolutionStrategy
from .version_manager import VersionManager, ChangeType
from .event_sourcing import EventStore, EventSourcingService, Event, EventType
from .device_sync import DeviceSyncCoordinator, DeviceInfo, DataCategory, SyncPriority
from .config import SyncConfig

logger = logging.getLogger(__name__)


class SyncServiceState(Enum):
    """Synchronization service states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class SyncRequest:
    """Represents a synchronization request"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""
    entity_id: str = ""
    operation: str = "sync"  # sync, create, update, delete
    data: Dict[str, Any] = field(default_factory=dict)
    user_id: str = ""
    device_id: str = ""
    tenant_id: str = ""
    priority: SyncPriority = SyncPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class SyncResponse:
    """Response to a synchronization request"""
    request_id: str = ""
    success: bool = False
    result_data: Optional[Dict[str, Any]] = None
    conflicts: List[str] = field(default_factory=list)
    version_id: Optional[str] = None
    event_id: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class SyncService:
    """
    Main synchronization service that orchestrates all sync components
    
    Features:
    - Unified interface for all sync operations
    - Automatic conflict detection and resolution
    - Real-time and offline synchronization
    - Cross-device coordination
    - Event sourcing and audit trails
    - Performance monitoring and optimization
    - Extensible plugin architecture
    """
    
    def __init__(self, config: SyncConfig = None):
        self.config = config or SyncConfig()
        self.state = SyncServiceState.INITIALIZING
        
        # Core components
        self.websocket_manager: Optional[WebSocketManager] = None
        self.offline_handler: Optional[OfflineHandler] = None
        self.conflict_resolver: Optional[ConflictResolver] = None
        self.version_manager: Optional[VersionManager] = None
        self.event_store: Optional[EventStore] = None
        self.event_service: Optional[EventSourcingService] = None
        self.device_coordinator: Optional[DeviceSyncCoordinator] = None
        
        # Request handling
        self.request_handlers: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        
        # Performance monitoring
        self.metrics = {
            'requests_processed': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'events_logged': 0,
            'avg_response_time': 0.0,
            'active_connections': 0,
            'sync_errors': 0
        }
        
        # Background tasks
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._metrics_collector_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize all sync service components"""
        try:
            self.state = SyncServiceState.INITIALIZING
            logger.info("Initializing synchronization service")
            
            # Initialize core components
            await self._initialize_core_components()
            
            # Setup component integrations
            await self._setup_integrations()
            
            # Register default handlers
            await self._register_default_handlers()
            
            # Setup middleware
            await self._setup_middleware()
            
            self.state = SyncServiceState.RUNNING
            logger.info("Synchronization service initialized successfully")
            
        except Exception as e:
            self.state = SyncServiceState.ERROR
            logger.error(f"Failed to initialize sync service: {e}")
            raise
            
    async def _initialize_core_components(self):
        """Initialize all core synchronization components"""
        
        # WebSocket Manager
        self.websocket_manager = WebSocketManager(
            jwt_secret=self.config.jwt_secret,
            heartbeat_interval=self.config.heartbeat_interval
        )
        
        # Offline Handler
        self.offline_handler = OfflineHandler(
            storage_path=self.config.offline_storage_path,
            max_queue_size=self.config.max_queue_size,
            connectivity_check_interval=self.config.connectivity_check_interval
        )
        
        # Conflict Resolver
        self.conflict_resolver = ConflictResolver()
        
        # Version Manager
        self.version_manager = VersionManager(
            enable_compression=self.config.enable_compression
        )
        
        # Event Store and Service
        self.event_store = EventStore(
            enable_compression=self.config.enable_compression
        )
        self.event_service = EventSourcingService(self.event_store)
        
        # Device Sync Coordinator
        self.device_coordinator = DeviceSyncCoordinator(
            websocket_manager=self.websocket_manager,
            offline_handler=self.offline_handler,
            conflict_resolver=self.conflict_resolver,
            event_store=self.event_store
        )
        
    async def _setup_integrations(self):
        """Setup integrations between components"""
        
        # Setup offline handler operation handlers
        self.offline_handler.add_operation_handler(
            OperationType.SYNC,
            self._handle_offline_sync_operation
        )
        
        # Setup conflict resolution custom rules
        self.conflict_resolver.add_custom_rule(
            "User",
            self._resolve_user_conflicts
        )
        self.conflict_resolver.add_custom_rule(
            "Document", 
            self._resolve_document_conflicts
        )
        
        # Setup version manager change listeners
        self.version_manager.add_change_listener(self._on_version_change)
        
        # Setup WebSocket message handlers
        self.websocket_manager.add_message_handler("sync_request", self._handle_websocket_sync)
        self.websocket_manager.add_message_handler("conflict_resolution", self._handle_conflict_resolution)
        
    async def _register_default_handlers(self):
        """Register default request handlers"""
        
        self.request_handlers.update({
            'sync': self._handle_sync_request,
            'create': self._handle_create_request,
            'update': self._handle_update_request,
            'delete': self._handle_delete_request,
            'get_version': self._handle_get_version_request,
            'get_history': self._handle_get_history_request,
            'resolve_conflict': self._handle_resolve_conflict_request
        })
        
    async def _setup_middleware(self):
        """Setup request processing middleware"""
        
        # Add validation middleware
        self.middleware.append(self._validate_request_middleware)
        
        # Add authentication middleware
        self.middleware.append(self._auth_middleware)
        
        # Add rate limiting middleware
        self.middleware.append(self._rate_limit_middleware)
        
        # Add metrics middleware
        self.middleware.append(self._metrics_middleware)
        
    async def start(self):
        """Start the synchronization service"""
        try:
            if self.state != SyncServiceState.RUNNING:
                await self.initialize()
                
            logger.info("Starting synchronization service components")
            
            # Start all components
            if self.websocket_manager:
                await self.websocket_manager.start()
                
            if self.offline_handler:
                await self.offline_handler.start()
                
            if self.event_service:
                await self.event_service.start()
                
            if self.device_coordinator:
                await self.device_coordinator.start()
                
            # Start background tasks
            self._health_monitor_task = asyncio.create_task(self._health_monitor())
            self._metrics_collector_task = asyncio.create_task(self._metrics_collector())
            
            logger.info("Synchronization service started successfully")
            
        except Exception as e:
            self.state = SyncServiceState.ERROR
            logger.error(f"Failed to start sync service: {e}")
            raise
            
    async def stop(self):
        """Stop the synchronization service"""
        try:
            self.state = SyncServiceState.STOPPING
            logger.info("Stopping synchronization service")
            
            # Cancel background tasks
            if self._health_monitor_task:
                self._health_monitor_task.cancel()
            if self._metrics_collector_task:
                self._metrics_collector_task.cancel()
                
            # Stop all components
            if self.device_coordinator:
                await self.device_coordinator.stop()
                
            if self.event_service:
                await self.event_service.stop()
                
            if self.offline_handler:
                await self.offline_handler.stop()
                
            if self.websocket_manager:
                await self.websocket_manager.stop()
                
            self.state = SyncServiceState.STOPPED
            logger.info("Synchronization service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping sync service: {e}")
            self.state = SyncServiceState.ERROR
            
    async def process_sync_request(self, request: SyncRequest) -> SyncResponse:
        """Process a synchronization request"""
        
        start_time = time.time()
        response = SyncResponse(request_id=request.id)
        
        try:
            # Apply middleware
            for middleware in self.middleware:
                request = await middleware(request)
                if not request:
                    response.success = False
                    response.error_message = "Request blocked by middleware"
                    return response
                    
            # Route to appropriate handler
            handler = self.request_handlers.get(request.operation)
            if not handler:
                response.success = False
                response.error_message = f"No handler for operation: {request.operation}"
                return response
                
            # Execute handler
            result = await handler(request)
            
            # Update response
            response.success = True
            response.result_data = result.get('data')
            response.version_id = result.get('version_id')
            response.event_id = result.get('event_id')
            response.conflicts = result.get('conflicts', [])
            response.warnings = result.get('warnings', [])
            response.metadata = result.get('metadata', {})
            
            # Update metrics
            self.metrics['requests_successful'] += 1
            
        except Exception as e:
            logger.error(f"Error processing sync request {request.id}: {e}")
            response.success = False
            response.error_message = str(e)
            self.metrics['requests_failed'] += 1
            
        finally:
            # Update metrics
            self.metrics['requests_processed'] += 1
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)
            
        return response
        
    async def _handle_sync_request(self, request: SyncRequest) -> Dict[str, Any]:
        """Handle a general sync request"""
        
        # Get current version
        current_version = await self.version_manager.get_latest_version(
            request.entity_type, 
            request.entity_id
        )
        
        # Create new version
        new_version = await self.version_manager.create_version(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            data=request.data,
            parent_versions=[current_version.id] if current_version else [],
            author=request.user_id,
            device_id=request.device_id
        )
        
        # Log event
        event = Event(
            event_type=EventType.DATA_UPDATED,
            aggregate_type=request.entity_type,
            aggregate_id=request.entity_id,
            event_data=request.data,
            user_id=request.user_id,
            device_id=request.device_id,
            tenant_id=request.tenant_id
        )
        
        await self.event_service.publish_event(event)
        
        # Sync to other devices
        if self.device_coordinator:
            await self.device_coordinator.sync_data(
                source_device_id=request.device_id,
                data_category=DataCategory.DOCUMENTS,  # Default category
                operation_type="update",
                data=request.data,
                priority=request.priority
            )
            
        return {
            'data': new_version.data,
            'version_id': new_version.id,
            'event_id': event.id,
            'metadata': {'operation': 'sync'}
        }
        
    async def _handle_create_request(self, request: SyncRequest) -> Dict[str, Any]:
        """Handle a create request"""
        
        # Create initial version
        version = await self.version_manager.create_version(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            data=request.data,
            author=request.user_id,
            device_id=request.device_id
        )
        
        # Log creation event
        event = Event(
            event_type=EventType.DATA_CREATED,
            aggregate_type=request.entity_type,
            aggregate_id=request.entity_id,
            event_data=request.data,
            user_id=request.user_id,
            device_id=request.device_id,
            tenant_id=request.tenant_id
        )
        
        await self.event_service.publish_event(event)
        
        # Sync to other devices
        if self.device_coordinator:
            await self.device_coordinator.sync_data(
                source_device_id=request.device_id,
                data_category=DataCategory.DOCUMENTS,
                operation_type="create",
                data=request.data,
                priority=request.priority
            )
            
        return {
            'data': version.data,
            'version_id': version.id,
            'event_id': event.id,
            'metadata': {'operation': 'create'}
        }
        
    async def _handle_update_request(self, request: SyncRequest) -> Dict[str, Any]:
        """Handle an update request with conflict detection"""
        
        # Get current version
        current_version = await self.version_manager.get_latest_version(
            request.entity_type,
            request.entity_id
        )
        
        if not current_version:
            raise ValueError(f"Entity {request.entity_type}:{request.entity_id} not found")
            
        # Check for conflicts
        conflicts = await self.conflict_resolver.detect_conflicts(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            local_data=request.data,
            remote_data=current_version.data,
            local_version=None,  # Would need version info from request
            remote_version=None   # Would need to create version info
        )
        
        result_data = request.data
        
        # Resolve conflicts if any
        if conflicts:
            self.metrics['conflicts_detected'] += len(conflicts)
            
            resolution_results = await self.conflict_resolver.resolve_conflicts(
                conflicts,
                strategy=ResolutionStrategy.THREE_WAY_MERGE
            )
            
            if all(r.success for r in resolution_results):
                result_data = resolution_results[0].merged_data
                self.metrics['conflicts_resolved'] += len(conflicts)
            else:
                return {
                    'conflicts': [c.id for c in conflicts],
                    'warnings': ['Conflicts require manual resolution']
                }
                
        # Create new version
        version = await self.version_manager.create_version(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            data=result_data,
            parent_versions=[current_version.id],
            author=request.user_id,
            device_id=request.device_id
        )
        
        # Log update event
        event = Event(
            event_type=EventType.DATA_UPDATED,
            aggregate_type=request.entity_type,
            aggregate_id=request.entity_id,
            event_data=result_data,
            user_id=request.user_id,
            device_id=request.device_id,
            tenant_id=request.tenant_id
        )
        
        await self.event_service.publish_event(event)
        
        # Sync to other devices
        if self.device_coordinator:
            await self.device_coordinator.sync_data(
                source_device_id=request.device_id,
                data_category=DataCategory.DOCUMENTS,
                operation_type="update",
                data=result_data,
                priority=request.priority
            )
            
        return {
            'data': version.data,
            'version_id': version.id,
            'event_id': event.id,
            'conflicts': [c.id for c in conflicts] if conflicts else [],
            'metadata': {'operation': 'update'}
        }
        
    async def _handle_delete_request(self, request: SyncRequest) -> Dict[str, Any]:
        """Handle a delete request"""
        
        # Mark as deleted in new version
        delete_data = {'_deleted': True, '_deleted_at': time.time()}
        
        version = await self.version_manager.create_version(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            data=delete_data,
            author=request.user_id,
            device_id=request.device_id
        )
        
        # Log deletion event
        event = Event(
            event_type=EventType.DATA_DELETED,
            aggregate_type=request.entity_type,
            aggregate_id=request.entity_id,
            event_data=delete_data,
            user_id=request.user_id,
            device_id=request.device_id,
            tenant_id=request.tenant_id
        )
        
        await self.event_service.publish_event(event)
        
        # Sync deletion to other devices
        if self.device_coordinator:
            await self.device_coordinator.sync_data(
                source_device_id=request.device_id,
                data_category=DataCategory.DOCUMENTS,
                operation_type="delete",
                data=delete_data,
                priority=request.priority
            )
            
        return {
            'data': version.data,
            'version_id': version.id,
            'event_id': event.id,
            'metadata': {'operation': 'delete'}
        }
        
    async def _handle_get_version_request(self, request: SyncRequest) -> Dict[str, Any]:
        """Handle get version request"""
        
        version_id = request.metadata.get('version_id')
        if version_id:
            version = await self.version_manager.get_version(version_id)
        else:
            version = await self.version_manager.get_latest_version(
                request.entity_type,
                request.entity_id
            )
            
        if not version:
            raise ValueError("Version not found")
            
        return {
            'data': version.data,
            'version_id': version.id,
            'metadata': {
                'operation': 'get_version',
                'timestamp': version.timestamp,
                'author': version.author
            }
        }
        
    async def _handle_get_history_request(self, request: SyncRequest) -> Dict[str, Any]:
        """Handle get history request"""
        
        limit = request.metadata.get('limit', 50)
        
        versions = await self.version_manager.get_version_history(
            request.entity_type,
            request.entity_id,
            limit=limit
        )
        
        history = [
            {
                'version_id': v.id,
                'timestamp': v.timestamp,
                'author': v.author,
                'device_id': v.device_id,
                'checksum': v.checksum
            }
            for v in versions
        ]
        
        return {
            'data': {'history': history},
            'metadata': {'operation': 'get_history', 'count': len(history)}
        }
        
    async def _handle_resolve_conflict_request(self, request: SyncRequest) -> Dict[str, Any]:
        """Handle manual conflict resolution"""
        
        conflict_id = request.metadata.get('conflict_id')
        resolution_strategy = request.metadata.get('strategy', 'three_way_merge')
        
        # This would need to be implemented based on stored conflicts
        # For now, return a placeholder
        
        return {
            'data': {'resolved': True},
            'metadata': {
                'operation': 'resolve_conflict',
                'conflict_id': conflict_id,
                'strategy': resolution_strategy
            }
        }
        
    # Middleware functions
    async def _validate_request_middleware(self, request: SyncRequest) -> Optional[SyncRequest]:
        """Validate request format and required fields"""
        
        if not request.entity_type or not request.entity_id:
            raise ValueError("entity_type and entity_id are required")
            
        if not request.user_id:
            raise ValueError("user_id is required")
            
        return request
        
    async def _auth_middleware(self, request: SyncRequest) -> Optional[SyncRequest]:
        """Authenticate and authorize request"""
        
        # Placeholder for authentication logic
        # In production, verify JWT token, check permissions, etc.
        
        return request
        
    async def _rate_limit_middleware(self, request: SyncRequest) -> Optional[SyncRequest]:
        """Apply rate limiting"""
        
        # Placeholder for rate limiting logic
        # In production, implement proper rate limiting per user/device
        
        return request
        
    async def _metrics_middleware(self, request: SyncRequest) -> Optional[SyncRequest]:
        """Collect metrics for request"""
        
        # Update metrics
        self.metrics['requests_processed'] += 1
        
        return request
        
    # Component event handlers
    async def _handle_offline_sync_operation(self, operation):
        """Handle offline sync operations"""
        
        # Convert offline operation to sync request
        sync_request = SyncRequest(
            entity_type=operation.data.get('entity_type', ''),
            entity_id=operation.data.get('entity_id', ''),
            operation=operation.data.get('operation', 'sync'),
            data=operation.data.get('data', {}),
            user_id=operation.data.get('user_id', ''),
            device_id=operation.data.get('device_id', '')
        )
        
        # Process the request
        response = await self.process_sync_request(sync_request)
        
        return response.success
        
    async def _resolve_user_conflicts(self, conflict, context):
        """Custom conflict resolution for User entities"""
        
        # Implement user-specific conflict resolution logic
        # For example, profile updates might merge non-conflicting fields
        
        return {
            'success': True,
            'merged_data': context.get('version_data', {}).get(conflict.conflicting_versions[0].version, {}),
            'metadata': {'custom_rule': 'user_merge'}
        }
        
    async def _resolve_document_conflicts(self, conflict, context):
        """Custom conflict resolution for Document entities"""
        
        # Implement document-specific conflict resolution logic
        # For example, might preserve the version with more content
        
        return {
            'success': True,
            'merged_data': context.get('version_data', {}).get(conflict.conflicting_versions[0].version, {}),
            'metadata': {'custom_rule': 'document_merge'}
        }
        
    async def _on_version_change(self, event_type: str, data):
        """Handle version manager events"""
        
        if event_type == 'version_created':
            version = data
            logger.debug(f"Version created: {version.id} for {version.entity_type}:{version.entity_id}")
            
    async def _handle_websocket_sync(self, connection_id: str, message: Message):
        """Handle sync requests from WebSocket connections"""
        
        try:
            # Convert WebSocket message to sync request
            sync_request = SyncRequest(
                entity_type=message.data.get('entity_type'),
                entity_id=message.data.get('entity_id'),
                operation=message.data.get('operation', 'sync'),
                data=message.data.get('data', {}),
                user_id=message.data.get('user_id'),
                device_id=message.data.get('device_id')
            )
            
            # Process the request
            response = await self.process_sync_request(sync_request)
            
            # Send response back via WebSocket
            response_message = Message(
                type="sync_response",
                data={
                    'request_id': sync_request.id,
                    'success': response.success,
                    'result': response.result_data,
                    'version_id': response.version_id,
                    'conflicts': response.conflicts,
                    'error': response.error_message
                }
            )
            
            await self.websocket_manager._send_to_connection(connection_id, response_message)
            
        except Exception as e:
            logger.error(f"Error handling WebSocket sync request: {e}")
            
    async def _handle_conflict_resolution(self, connection_id: str, message: Message):
        """Handle conflict resolution from WebSocket"""
        
        # Placeholder for conflict resolution handling
        pass
        
    # Background tasks
    async def _health_monitor(self):
        """Monitor service health"""
        
        while self.state == SyncServiceState.RUNNING:
            try:
                # Check component health
                health_status = {
                    'websocket_manager': self.websocket_manager is not None,
                    'offline_handler': self.offline_handler is not None,
                    'conflict_resolver': self.conflict_resolver is not None,
                    'version_manager': self.version_manager is not None,
                    'event_service': self.event_service is not None,
                    'device_coordinator': self.device_coordinator is not None
                }
                
                # Log unhealthy components
                unhealthy = [name for name, healthy in health_status.items() if not healthy]
                if unhealthy:
                    logger.warning(f"Unhealthy components: {unhealthy}")
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(30)
                
    async def _metrics_collector(self):
        """Collect and update metrics"""
        
        while self.state == SyncServiceState.RUNNING:
            try:
                # Update connection metrics
                if self.websocket_manager:
                    self.metrics['active_connections'] = len(self.websocket_manager.connections)
                    
                # Log metrics periodically
                logger.info(f"Sync metrics: {self.metrics}")
                
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"Metrics collector error: {e}")
                await asyncio.sleep(60)
                
    def _update_avg_response_time(self, new_time: float):
        """Update average response time using exponential moving average"""
        alpha = 0.1  # Smoothing factor
        if self.metrics['avg_response_time'] == 0:
            self.metrics['avg_response_time'] = new_time
        else:
            self.metrics['avg_response_time'] = (
                alpha * new_time + (1 - alpha) * self.metrics['avg_response_time']
            )
            
    # Public API methods
    async def register_device(self, user_id: str, device_info: DeviceInfo) -> str:
        """Register a device for synchronization"""
        if self.device_coordinator:
            return await self.device_coordinator.register_device(user_id, device_info)
        raise RuntimeError("Device coordinator not available")
        
    async def unregister_device(self, device_id: str):
        """Unregister a device"""
        if self.device_coordinator:
            await self.device_coordinator.unregister_device(device_id)
        else:
            raise RuntimeError("Device coordinator not available")
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics"""
        return self.metrics.copy()
        
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            'state': self.state.value,
            'metrics': self.get_metrics(),
            'components': {
                'websocket_manager': self.websocket_manager is not None,
                'offline_handler': self.offline_handler is not None,
                'conflict_resolver': self.conflict_resolver is not None,
                'version_manager': self.version_manager is not None,
                'event_service': self.event_service is not None,
                'device_coordinator': self.device_coordinator is not None
            }
        }
        
    def add_request_handler(self, operation: str, handler: Callable):
        """Add a custom request handler"""
        self.request_handlers[operation] = handler
        
    def add_middleware(self, middleware: Callable):
        """Add custom middleware"""
        self.middleware.append(middleware)