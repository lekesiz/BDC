"""
Event Sourcing System for Audit Trails

Implements event sourcing pattern for comprehensive audit trails:
- Event store with immutable event logging
- Event replay and reconstruction capabilities
- Snapshot management for performance
- Event streaming and subscription
- Audit trail generation and querying
- Event projection and aggregation
"""

import json
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable, Set, Type, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import hashlib
import pickle
import gzip

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can be stored"""
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_MERGED = "data_merged"
    USER_ACTION = "user_action"
    SYSTEM_ACTION = "system_action"
    SYNC_ACTION = "sync_action"
    CONFLICT_RESOLVED = "conflict_resolved"
    VERSION_CREATED = "version_created"
    BRANCH_CREATED = "branch_created"
    PERMISSION_CHANGED = "permission_changed"


class EventStatus(Enum):
    """Status of an event"""
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"
    REPLAYING = "replaying"


@dataclass
class Event:
    """Represents an immutable event in the system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.USER_ACTION
    aggregate_type: str = ""  # e.g., "User", "Document", "Appointment"
    aggregate_id: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    version: int = 1
    correlation_id: str = ""
    causation_id: str = ""
    user_id: str = ""
    device_id: str = ""
    tenant_id: str = ""
    checksum: str = ""
    status: EventStatus = EventStatus.PENDING
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
            
    def _calculate_checksum(self) -> str:
        """Calculate checksum for event integrity"""
        event_str = json.dumps({
            'id': self.id,
            'event_type': self.event_type.value,
            'aggregate_type': self.aggregate_type,
            'aggregate_id': self.aggregate_id,
            'event_data': self.event_data,
            'timestamp': self.timestamp,
            'version': self.version
        }, sort_keys=True, default=str)
        return hashlib.sha256(event_str.encode()).hexdigest()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type.value,
            'aggregate_type': self.aggregate_type,
            'aggregate_id': self.aggregate_id,
            'event_data': self.event_data,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'version': self.version,
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'tenant_id': self.tenant_id,
            'checksum': self.checksum,
            'status': self.status.value
        }


@dataclass
class Snapshot:
    """Represents a snapshot of aggregate state at a point in time"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    aggregate_type: str = ""
    aggregate_id: str = ""
    aggregate_state: Dict[str, Any] = field(default_factory=dict)
    version: int = 0
    timestamp: float = field(default_factory=time.time)
    event_id: str = ""  # Last event that was applied to create this snapshot
    compressed_data: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventProjection:
    """Represents a projection of events for read models"""
    name: str = ""
    aggregate_types: List[str] = field(default_factory=list)
    event_types: List[EventType] = field(default_factory=list)
    last_processed_event: str = ""
    last_processed_timestamp: float = 0.0
    projection_data: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class EventHandler(ABC):
    """Abstract base class for event handlers"""
    
    @abstractmethod
    async def handle(self, event: Event) -> bool:
        """Handle an event and return success status"""
        pass
        
    @abstractmethod
    def can_handle(self, event: Event) -> bool:
        """Check if this handler can process the given event"""
        pass


class EventStore:
    """
    Event store for immutable event logging and retrieval
    
    Features:
    - Immutable event storage
    - Event integrity verification
    - Event querying and filtering
    - Snapshot management
    - Event compression for storage efficiency
    """
    
    def __init__(self, storage_backend=None, enable_compression=True):
        self.storage_backend = storage_backend
        self.enable_compression = enable_compression
        
        # In-memory storage (would be replaced with persistent storage in production)
        self.events: Dict[str, Event] = {}
        self.aggregate_events: Dict[str, Dict[str, List[str]]] = {}  # aggregate_type -> aggregate_id -> event_ids
        self.snapshots: Dict[str, Dict[str, Snapshot]] = {}  # aggregate_type -> aggregate_id -> snapshot
        
        # Indexing for fast queries
        self.event_type_index: Dict[EventType, List[str]] = {}
        self.timestamp_index: List[Tuple[float, str]] = []  # (timestamp, event_id)
        self.user_events: Dict[str, List[str]] = {}
        
        # Statistics
        self.stats = {
            'events_stored': 0,
            'snapshots_created': 0,
            'storage_size_bytes': 0,
            'compression_ratio': 0.0,
            'integrity_violations': 0
        }
        
    async def append_event(self, event: Event) -> bool:
        """Append an event to the store"""
        
        try:
            # Verify event integrity
            if not self._verify_event_integrity(event):
                self.stats['integrity_violations'] += 1
                logger.error(f"Event integrity verification failed for event {event.id}")
                return False
                
            # Store event
            self.events[event.id] = event
            
            # Update indexes
            self._update_indexes(event)
            
            # Update statistics
            self.stats['events_stored'] += 1
            self._update_storage_stats()
            
            # Save to storage backend if available
            if self.storage_backend:
                await self.storage_backend.save_event(event)
                
            logger.debug(f"Appended event {event.id} to store")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to append event {event.id}: {e}")
            return False
            
    def _verify_event_integrity(self, event: Event) -> bool:
        """Verify event integrity using checksum"""
        expected_checksum = event._calculate_checksum()
        return event.checksum == expected_checksum
        
    def _update_indexes(self, event: Event):
        """Update various indexes for fast querying"""
        
        # Aggregate events index
        if event.aggregate_type not in self.aggregate_events:
            self.aggregate_events[event.aggregate_type] = {}
        if event.aggregate_id not in self.aggregate_events[event.aggregate_type]:
            self.aggregate_events[event.aggregate_type][event.aggregate_id] = []
            
        self.aggregate_events[event.aggregate_type][event.aggregate_id].append(event.id)
        
        # Event type index
        if event.event_type not in self.event_type_index:
            self.event_type_index[event.event_type] = []
        self.event_type_index[event.event_type].append(event.id)
        
        # Timestamp index (keep sorted)
        self.timestamp_index.append((event.timestamp, event.id))
        self.timestamp_index.sort(key=lambda x: x[0])
        
        # User events index
        if event.user_id:
            if event.user_id not in self.user_events:
                self.user_events[event.user_id] = []
            self.user_events[event.user_id].append(event.id)
            
    async def get_events(self,
                        aggregate_type: str = None,
                        aggregate_id: str = None,
                        event_types: List[EventType] = None,
                        from_timestamp: float = None,
                        to_timestamp: float = None,
                        from_version: int = None,
                        limit: int = None,
                        order: str = "asc") -> List[Event]:
        """Get events based on various filters"""
        
        event_ids = set()
        
        # Filter by aggregate
        if aggregate_type and aggregate_id:
            if (aggregate_type in self.aggregate_events and 
                aggregate_id in self.aggregate_events[aggregate_type]):
                event_ids = set(self.aggregate_events[aggregate_type][aggregate_id])
            else:
                return []
        elif aggregate_type:
            if aggregate_type in self.aggregate_events:
                for aggregate_id in self.aggregate_events[aggregate_type]:
                    event_ids.update(self.aggregate_events[aggregate_type][aggregate_id])
            else:
                return []
        else:
            # Get all events
            event_ids = set(self.events.keys())
            
        # Filter by event types
        if event_types:
            type_event_ids = set()
            for event_type in event_types:
                if event_type in self.event_type_index:
                    type_event_ids.update(self.event_type_index[event_type])
            event_ids = event_ids.intersection(type_event_ids)
            
        # Get event objects and apply additional filters
        events = []
        for event_id in event_ids:
            event = self.events.get(event_id)
            if not event:
                continue
                
            # Apply timestamp filters
            if from_timestamp and event.timestamp < from_timestamp:
                continue
            if to_timestamp and event.timestamp > to_timestamp:
                continue
                
            # Apply version filter
            if from_version and event.version < from_version:
                continue
                
            events.append(event)
            
        # Sort events
        if order == "desc":
            events.sort(key=lambda e: e.timestamp, reverse=True)
        else:
            events.sort(key=lambda e: e.timestamp)
            
        # Apply limit
        if limit:
            events = events[:limit]
            
        return events
        
    async def get_aggregate_events(self, aggregate_type: str, aggregate_id: str) -> List[Event]:
        """Get all events for a specific aggregate"""
        return await self.get_events(aggregate_type=aggregate_type, aggregate_id=aggregate_id)
        
    async def create_snapshot(self, 
                            aggregate_type: str,
                            aggregate_id: str,
                            aggregate_state: Dict[str, Any],
                            version: int,
                            last_event_id: str) -> Snapshot:
        """Create a snapshot of aggregate state"""
        
        snapshot = Snapshot(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            aggregate_state=aggregate_state,
            version=version,
            event_id=last_event_id
        )
        
        # Compress snapshot data if enabled
        if self.enable_compression:
            snapshot.compressed_data = self._compress_snapshot(aggregate_state)
            
        # Store snapshot
        if aggregate_type not in self.snapshots:
            self.snapshots[aggregate_type] = {}
        self.snapshots[aggregate_type][aggregate_id] = snapshot
        
        self.stats['snapshots_created'] += 1
        
        # Save to storage backend if available
        if self.storage_backend:
            await self.storage_backend.save_snapshot(snapshot)
            
        logger.info(f"Created snapshot for {aggregate_type}:{aggregate_id} at version {version}")
        
        return snapshot
        
    async def get_snapshot(self, aggregate_type: str, aggregate_id: str) -> Optional[Snapshot]:
        """Get the latest snapshot for an aggregate"""
        
        if (aggregate_type in self.snapshots and 
            aggregate_id in self.snapshots[aggregate_type]):
            return self.snapshots[aggregate_type][aggregate_id]
            
        # Try to load from storage backend
        if self.storage_backend:
            snapshot = await self.storage_backend.load_snapshot(aggregate_type, aggregate_id)
            if snapshot:
                if aggregate_type not in self.snapshots:
                    self.snapshots[aggregate_type] = {}
                self.snapshots[aggregate_type][aggregate_id] = snapshot
                return snapshot
                
        return None
        
    def _compress_snapshot(self, data: Dict[str, Any]) -> bytes:
        """Compress snapshot data"""
        data_bytes = pickle.dumps(data)
        compressed = gzip.compress(data_bytes)
        
        # Update compression ratio
        if len(data_bytes) > 0:
            self.stats['compression_ratio'] = len(compressed) / len(data_bytes)
            
        return compressed
        
    def _decompress_snapshot(self, compressed_data: bytes) -> Dict[str, Any]:
        """Decompress snapshot data"""
        data_bytes = gzip.decompress(compressed_data)
        return pickle.loads(data_bytes)
        
    def _update_storage_stats(self):
        """Update storage statistics"""
        total_size = 0
        
        # Calculate size of events
        for event in self.events.values():
            event_str = json.dumps(event.to_dict(), default=str)
            total_size += len(event_str.encode())
            
        # Calculate size of snapshots
        for aggregate_type in self.snapshots:
            for snapshot in self.snapshots[aggregate_type].values():
                if snapshot.compressed_data:
                    total_size += len(snapshot.compressed_data)
                else:
                    snapshot_str = json.dumps(snapshot.aggregate_state, default=str)
                    total_size += len(snapshot_str.encode())
                    
        self.stats['storage_size_bytes'] = total_size
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get event store statistics"""
        return self.stats.copy()


class EventSourcingService:
    """
    Event sourcing service that coordinates event handling and projections
    
    Features:
    - Event publishing and handling
    - Aggregate reconstruction from events
    - Event replay capabilities
    - Projection management
    - Event streaming and subscriptions
    """
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        
        # Event handlers
        self.event_handlers: Dict[EventType, List[EventHandler]] = {}
        self.aggregate_handlers: Dict[str, List[EventHandler]] = {}
        
        # Projections
        self.projections: Dict[str, EventProjection] = {}
        self.projection_handlers: Dict[str, Callable] = {}
        
        # Subscriptions
        self.event_subscribers: Dict[EventType, List[Callable]] = {}
        self.aggregate_subscribers: Dict[str, List[Callable]] = {}
        
        # Background tasks
        self._projection_task: Optional[asyncio.Task] = None
        self._running = False
        
    async def start(self):
        """Start the event sourcing service"""
        logger.info("Starting event sourcing service")
        self._running = True
        self._projection_task = asyncio.create_task(self._process_projections())
        
    async def stop(self):
        """Stop the event sourcing service"""
        logger.info("Stopping event sourcing service")
        self._running = False
        
        if self._projection_task:
            self._projection_task.cancel()
            
    async def publish_event(self, event: Event) -> bool:
        """Publish an event to the store and notify handlers"""
        
        # Store the event
        success = await self.event_store.append_event(event)
        if not success:
            return False
            
        # Update event status
        event.status = EventStatus.PROCESSED
        
        # Notify event handlers
        await self._notify_event_handlers(event)
        
        # Notify subscribers
        await self._notify_subscribers(event)
        
        return True
        
    async def _notify_event_handlers(self, event: Event):
        """Notify registered event handlers"""
        
        # Event type handlers
        handlers = self.event_handlers.get(event.event_type, [])
        
        # Aggregate type handlers
        if event.aggregate_type in self.aggregate_handlers:
            handlers.extend(self.aggregate_handlers[event.aggregate_type])
            
        for handler in handlers:
            try:
                if handler.can_handle(event):
                    await handler.handle(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
                
    async def _notify_subscribers(self, event: Event):
        """Notify event subscribers"""
        
        # Event type subscribers
        subscribers = self.event_subscribers.get(event.event_type, [])
        
        # Aggregate type subscribers
        if event.aggregate_type in self.aggregate_subscribers:
            subscribers.extend(self.aggregate_subscribers[event.aggregate_type])
            
        for subscriber in subscribers:
            try:
                await subscriber(event)
            except Exception as e:
                logger.error(f"Event subscriber error: {e}")
                
    async def reconstruct_aggregate(self, 
                                  aggregate_type: str,
                                  aggregate_id: str,
                                  to_version: int = None) -> Dict[str, Any]:
        """Reconstruct aggregate state from events"""
        
        # Try to get a snapshot first
        snapshot = await self.event_store.get_snapshot(aggregate_type, aggregate_id)
        
        if snapshot:
            # Start from snapshot
            state = snapshot.aggregate_state.copy()
            from_version = snapshot.version + 1
        else:
            # Start from empty state
            state = {}
            from_version = 1
            
        # Get events since snapshot
        events = await self.event_store.get_events(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            from_version=from_version,
            order="asc"
        )
        
        # Apply events to reconstruct state
        for event in events:
            if to_version and event.version > to_version:
                break
                
            state = await self._apply_event_to_state(state, event)
            
        return state
        
    async def _apply_event_to_state(self, state: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Apply an event to aggregate state"""
        
        # This is a simplified implementation
        # In practice, you'd have specific logic for each event type
        
        if event.event_type == EventType.DATA_CREATED:
            state.update(event.event_data)
        elif event.event_type == EventType.DATA_UPDATED:
            # Apply updates from event data
            for key, value in event.event_data.items():
                if key != '_metadata':
                    state[key] = value
        elif event.event_type == EventType.DATA_DELETED:
            # Mark as deleted or remove fields
            deleted_fields = event.event_data.get('deleted_fields', [])
            for field in deleted_fields:
                state.pop(field, None)
                
        # Update metadata
        state['_last_event_id'] = event.id
        state['_version'] = event.version
        state['_last_modified'] = event.timestamp
        
        return state
        
    async def replay_events(self,
                          aggregate_type: str = None,
                          aggregate_id: str = None,
                          from_timestamp: float = None,
                          to_timestamp: float = None,
                          event_handler: Callable = None) -> int:
        """Replay events with optional filtering"""
        
        events = await self.event_store.get_events(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            order="asc"
        )
        
        replayed_count = 0
        
        for event in events:
            # Mark as replaying
            event.status = EventStatus.REPLAYING
            
            try:
                if event_handler:
                    await event_handler(event)
                else:
                    # Use default handlers
                    await self._notify_event_handlers(event)
                    
                replayed_count += 1
                
            except Exception as e:
                logger.error(f"Error replaying event {event.id}: {e}")
                event.status = EventStatus.FAILED
                
        logger.info(f"Replayed {replayed_count} events")
        return replayed_count
        
    async def create_projection(self,
                              name: str,
                              aggregate_types: List[str] = None,
                              event_types: List[EventType] = None,
                              handler: Callable = None) -> EventProjection:
        """Create a new event projection"""
        
        projection = EventProjection(
            name=name,
            aggregate_types=aggregate_types or [],
            event_types=event_types or []
        )
        
        self.projections[name] = projection
        
        if handler:
            self.projection_handlers[name] = handler
            
        logger.info(f"Created projection: {name}")
        
        return projection
        
    async def _process_projections(self):
        """Background task to process projections"""
        
        while self._running:
            try:
                for projection_name, projection in self.projections.items():
                    if not projection.is_active:
                        continue
                        
                    # Get new events for this projection
                    events = await self._get_projection_events(projection)
                    
                    if events:
                        # Process events
                        handler = self.projection_handlers.get(projection_name)
                        if handler:
                            try:
                                await handler(projection, events)
                                
                                # Update projection metadata
                                if events:
                                    last_event = events[-1]
                                    projection.last_processed_event = last_event.id
                                    projection.last_processed_timestamp = last_event.timestamp
                                    
                            except Exception as e:
                                logger.error(f"Projection handler error for {projection_name}: {e}")
                                
                await asyncio.sleep(1)  # Process projections every second
                
            except Exception as e:
                logger.error(f"Projection processing error: {e}")
                await asyncio.sleep(5)
                
    async def _get_projection_events(self, projection: EventProjection) -> List[Event]:
        """Get new events for a projection"""
        
        # Get events since last processed
        events = await self.event_store.get_events(
            event_types=projection.event_types if projection.event_types else None,
            from_timestamp=projection.last_processed_timestamp,
            order="asc"
        )
        
        # Filter by aggregate types if specified
        if projection.aggregate_types:
            events = [e for e in events if e.aggregate_type in projection.aggregate_types]
            
        # Exclude already processed events
        events = [e for e in events if e.id != projection.last_processed_event]
        
        return events
        
    def add_event_handler(self, event_type: EventType, handler: EventHandler):
        """Add an event handler for a specific event type"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        
    def add_aggregate_handler(self, aggregate_type: str, handler: EventHandler):
        """Add an event handler for a specific aggregate type"""
        if aggregate_type not in self.aggregate_handlers:
            self.aggregate_handlers[aggregate_type] = []
        self.aggregate_handlers[aggregate_type].append(handler)
        
    def subscribe_to_events(self, event_type: EventType, callback: Callable):
        """Subscribe to events of a specific type"""
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        self.event_subscribers[event_type].append(callback)
        
    def subscribe_to_aggregate(self, aggregate_type: str, callback: Callable):
        """Subscribe to events for a specific aggregate type"""
        if aggregate_type not in self.aggregate_subscribers:
            self.aggregate_subscribers[aggregate_type] = []
        self.aggregate_subscribers[aggregate_type].append(callback)
        
    async def get_audit_trail(self,
                            aggregate_type: str = None,
                            aggregate_id: str = None,
                            user_id: str = None,
                            from_timestamp: float = None,
                            to_timestamp: float = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail for analysis and compliance"""
        
        events = await self.event_store.get_events(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            limit=limit,
            order="desc"
        )
        
        # Filter by user if specified
        if user_id:
            events = [e for e in events if e.user_id == user_id]
            
        # Convert to audit trail format
        audit_trail = []
        for event in events:
            audit_entry = {
                'event_id': event.id,
                'timestamp': event.timestamp,
                'event_type': event.event_type.value,
                'aggregate_type': event.aggregate_type,
                'aggregate_id': event.aggregate_id,
                'user_id': event.user_id,
                'device_id': event.device_id,
                'changes': event.event_data,
                'metadata': event.metadata
            }
            audit_trail.append(audit_entry)
            
        return audit_trail