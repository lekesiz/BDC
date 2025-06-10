"""
Real-time Data Synchronization System for BDC Project

This module provides comprehensive real-time data synchronization capabilities including:
- WebSocket connection management
- Offline/online state handling  
- Conflict resolution algorithms
- Data versioning and merging
- Event sourcing for audit trails
- Cross-device synchronization

The synchronization system is designed to handle distributed data consistency
across multiple clients and devices while maintaining data integrity and
providing seamless user experience during network interruptions.
"""

from .websocket_manager import WebSocketManager, Message, ConnectionState, ConnectionInfo
from .offline_handler import OfflineHandler, OperationType, OperationPriority, NetworkState
from .conflict_resolver import ConflictResolver, ConflictType, ResolutionStrategy, ConflictResolution
from .version_manager import VersionManager, ChangeType, MergeType, Version, Branch
from .event_sourcing import EventStore, EventSourcingService, Event, EventType, Snapshot
from .device_sync import DeviceSyncCoordinator, DeviceInfo, DeviceType, DataCategory, SyncPriority
from .sync_service import SyncService, SyncRequest, SyncResponse, SyncServiceState
from .config import SyncConfig, LogLevel, CompressionType, EncryptionType
from .exceptions import (
    SyncException, ConnectionException, AuthenticationException, 
    ConflictResolutionException, VersionException, EventException,
    DeviceSyncException, OfflineException, ConfigurationException,
    StorageException, ValidationException, RateLimitException, TimeoutException
)
from .utils import (
    generate_id, current_timestamp, calculate_checksum, 
    compress_data, decompress_data, deep_merge, deep_diff,
    retry_with_backoff, CircularBuffer, RateLimiter
)

__all__ = [
    # Core Components
    'WebSocketManager', 'OfflineHandler', 'ConflictResolver',
    'VersionManager', 'EventStore', 'EventSourcingService',
    'DeviceSyncCoordinator', 'SyncService', 'SyncConfig',
    
    # WebSocket Types
    'Message', 'ConnectionState', 'ConnectionInfo',
    
    # Offline Types
    'OperationType', 'OperationPriority', 'NetworkState',
    
    # Conflict Types
    'ConflictType', 'ResolutionStrategy', 'ConflictResolution',
    
    # Version Types
    'ChangeType', 'MergeType', 'Version', 'Branch',
    
    # Event Types
    'Event', 'EventType', 'Snapshot',
    
    # Device Sync Types
    'DeviceInfo', 'DeviceType', 'DataCategory', 'SyncPriority',
    
    # Service Types
    'SyncRequest', 'SyncResponse', 'SyncServiceState',
    
    # Config Types
    'LogLevel', 'CompressionType', 'EncryptionType',
    
    # Exceptions
    'SyncException', 'ConnectionException', 'AuthenticationException',
    'ConflictResolutionException', 'VersionException', 'EventException',
    'DeviceSyncException', 'OfflineException', 'ConfigurationException',
    'StorageException', 'ValidationException', 'RateLimitException', 
    'TimeoutException',
    
    # Utilities
    'generate_id', 'current_timestamp', 'calculate_checksum',
    'compress_data', 'decompress_data', 'deep_merge', 'deep_diff',
    'retry_with_backoff', 'CircularBuffer', 'RateLimiter'
]

__version__ = '1.0.0'