"""
Cross-Device Synchronization Coordinator

Manages synchronization across multiple devices for a user:
- Device registration and management
- Cross-device state coordination
- Device-specific conflict resolution
- Selective synchronization based on device capabilities
- Device presence and activity tracking
- Bandwidth-aware synchronization strategies
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Types of devices that can sync"""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    WEB = "web"
    API = "api"


class DeviceStatus(Enum):
    """Device status states"""
    ONLINE = "online"
    OFFLINE = "offline"
    SYNCING = "syncing"
    IDLE = "idle"
    SUSPENDED = "suspended"


class SyncPriority(Enum):
    """Synchronization priority levels"""
    IMMEDIATE = "immediate"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class DataCategory(Enum):
    """Categories of data for selective sync"""
    USER_PROFILE = "user_profile"
    DOCUMENTS = "documents"
    APPOINTMENTS = "appointments"
    SETTINGS = "settings"
    CACHE = "cache"
    TEMPORARY = "temporary"


@dataclass
class DeviceCapabilities:
    """Describes a device's synchronization capabilities"""
    storage_capacity: int = 0  # bytes
    bandwidth_limit: int = 0  # bytes/second, 0 = unlimited
    supports_real_time: bool = True
    supports_offline: bool = True
    supports_compression: bool = True
    supports_encryption: bool = True
    battery_optimized: bool = False
    sync_categories: List[DataCategory] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceInfo:
    """Information about a registered device"""
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    device_type: DeviceType = DeviceType.WEB
    device_name: str = ""
    platform: str = ""  # iOS, Android, Windows, etc.
    app_version: str = ""
    capabilities: DeviceCapabilities = field(default_factory=DeviceCapabilities)
    status: DeviceStatus = DeviceStatus.OFFLINE
    last_seen: float = field(default_factory=time.time)
    last_sync: Optional[float] = None
    sync_version: str = ""
    connection_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncOperation:
    """Represents a synchronization operation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_device_id: str = ""
    target_device_ids: List[str] = field(default_factory=list)
    data_category: DataCategory = DataCategory.DOCUMENTS
    operation_type: str = "update"  # create, update, delete, merge
    data: Dict[str, Any] = field(default_factory=dict)
    priority: SyncPriority = SyncPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    scheduled_at: Optional[float] = None
    completed_at: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncPolicy:
    """Defines synchronization policies for different scenarios"""
    name: str = ""
    device_types: List[DeviceType] = field(default_factory=list)
    data_categories: List[DataCategory] = field(default_factory=list)
    sync_frequency: int = 60  # seconds
    immediate_sync: bool = True
    offline_sync: bool = True
    compression_enabled: bool = True
    encryption_required: bool = False
    bandwidth_limit: Optional[int] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeviceSyncCoordinator:
    """
    Coordinates synchronization across multiple devices for users
    
    Features:
    - Device registration and capability management
    - Cross-device state coordination
    - Intelligent sync scheduling based on device capabilities
    - Conflict resolution with device-specific rules
    - Bandwidth-aware synchronization
    - Selective sync based on device type and data categories
    - Real-time sync notifications
    """
    
    def __init__(self, websocket_manager=None, offline_handler=None, 
                 conflict_resolver=None, event_store=None):
        self.websocket_manager = websocket_manager
        self.offline_handler = offline_handler
        self.conflict_resolver = conflict_resolver
        self.event_store = event_store
        
        # Device management
        self.devices: Dict[str, DeviceInfo] = {}
        self.user_devices: Dict[str, Set[str]] = {}  # user_id -> device_ids
        
        # Sync operations
        self.pending_operations: List[SyncOperation] = []
        self.completed_operations: List[SyncOperation] = []
        self.sync_policies: Dict[str, SyncPolicy] = {}
        
        # Real-time coordination
        self.device_listeners: Dict[str, List[Callable]] = {}  # device_id -> callbacks
        self.sync_channels: Dict[str, Set[str]] = {}  # channel -> device_ids
        
        # Background tasks
        self._sync_scheduler_task: Optional[asyncio.Task] = None
        self._device_monitor_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self.stats = {
            'devices_registered': 0,
            'sync_operations': 0,
            'conflicts_resolved': 0,
            'bandwidth_saved': 0,
            'sync_errors': 0
        }
        
        # Default sync policies
        self._create_default_policies()
        
    async def start(self):
        """Start the device sync coordinator"""
        logger.info("Starting device sync coordinator")
        self._running = True
        
        self._sync_scheduler_task = asyncio.create_task(self._sync_scheduler())
        self._device_monitor_task = asyncio.create_task(self._device_monitor())
        
    async def stop(self):
        """Stop the device sync coordinator"""
        logger.info("Stopping device sync coordinator")
        self._running = False
        
        if self._sync_scheduler_task:
            self._sync_scheduler_task.cancel()
        if self._device_monitor_task:
            self._device_monitor_task.cancel()
            
    async def register_device(self, 
                            user_id: str,
                            device_info: DeviceInfo) -> str:
        """Register a new device for synchronization"""
        
        device_info.user_id = user_id
        device_info.last_seen = time.time()
        
        # Store device info
        self.devices[device_info.device_id] = device_info
        
        # Update user devices mapping
        if user_id not in self.user_devices:
            self.user_devices[user_id] = set()
        self.user_devices[user_id].add(device_info.device_id)
        
        # Subscribe to relevant sync channels
        await self._subscribe_device_to_channels(device_info)
        
        self.stats['devices_registered'] += 1
        
        logger.info(f"Registered device {device_info.device_id} for user {user_id}")
        
        # Trigger initial sync
        await self._trigger_initial_sync(device_info)
        
        return device_info.device_id
        
    async def unregister_device(self, device_id: str):
        """Unregister a device"""
        
        device_info = self.devices.get(device_id)
        if not device_info:
            return
            
        # Remove from user devices
        user_id = device_info.user_id
        if user_id in self.user_devices:
            self.user_devices[user_id].discard(device_id)
            if not self.user_devices[user_id]:
                del self.user_devices[user_id]
                
        # Remove from sync channels
        await self._unsubscribe_device_from_channels(device_id)
        
        # Remove device
        del self.devices[device_id]
        
        logger.info(f"Unregistered device {device_id}")
        
    async def update_device_status(self, device_id: str, status: DeviceStatus):
        """Update device status"""
        
        device_info = self.devices.get(device_id)
        if not device_info:
            return
            
        old_status = device_info.status
        device_info.status = status
        device_info.last_seen = time.time()
        
        # Handle status changes
        if old_status != status:
            await self._handle_device_status_change(device_info, old_status, status)
            
    async def _handle_device_status_change(self, 
                                         device_info: DeviceInfo,
                                         old_status: DeviceStatus,
                                         new_status: DeviceStatus):
        """Handle device status changes"""
        
        if new_status == DeviceStatus.ONLINE and old_status == DeviceStatus.OFFLINE:
            # Device came online - trigger sync
            await self._trigger_device_sync(device_info.device_id)
            
        elif new_status == DeviceStatus.OFFLINE:
            # Device went offline - handle pending operations
            await self._handle_device_offline(device_info.device_id)
            
    async def sync_data(self,
                       source_device_id: str,
                       data_category: DataCategory,
                       operation_type: str,
                       data: Dict[str, Any],
                       target_device_ids: List[str] = None,
                       priority: SyncPriority = SyncPriority.NORMAL) -> str:
        """Synchronize data across devices"""
        
        source_device = self.devices.get(source_device_id)
        if not source_device:
            raise ValueError(f"Source device {source_device_id} not found")
            
        # Determine target devices if not specified
        if not target_device_ids:
            target_device_ids = list(self.user_devices.get(source_device.user_id, set()))
            target_device_ids = [did for did in target_device_ids if did != source_device_id]
            
        # Create sync operation
        sync_op = SyncOperation(
            source_device_id=source_device_id,
            target_device_ids=target_device_ids,
            data_category=data_category,
            operation_type=operation_type,
            data=data,
            priority=priority
        )
        
        # Apply sync policies
        await self._apply_sync_policies(sync_op)
        
        # Add to pending operations
        self.pending_operations.append(sync_op)
        
        self.stats['sync_operations'] += 1
        
        logger.info(f"Created sync operation {sync_op.id} from device {source_device_id}")
        
        return sync_op.id
        
    async def _apply_sync_policies(self, sync_op: SyncOperation):
        """Apply sync policies to a sync operation"""
        
        source_device = self.devices.get(sync_op.source_device_id)
        if not source_device:
            return
            
        # Find applicable policies
        applicable_policies = []
        for policy in self.sync_policies.values():
            if (not policy.device_types or source_device.device_type in policy.device_types) and \
               (not policy.data_categories or sync_op.data_category in policy.data_categories):
                applicable_policies.append(policy)
                
        # Apply most restrictive policies
        for policy in applicable_policies:
            if not policy.immediate_sync:
                sync_op.scheduled_at = time.time() + policy.sync_frequency
                
            if policy.bandwidth_limit and source_device.capabilities.bandwidth_limit:
                # Adjust for bandwidth limitations
                sync_op.metadata['bandwidth_limit'] = min(
                    policy.bandwidth_limit,
                    source_device.capabilities.bandwidth_limit
                )
                
    async def _sync_scheduler(self):
        """Background task to schedule and execute sync operations"""
        
        while self._running:
            try:
                current_time = time.time()
                
                # Process pending operations
                operations_to_process = []
                remaining_operations = []
                
                for sync_op in self.pending_operations:
                    if (sync_op.scheduled_at is None or 
                        sync_op.scheduled_at <= current_time):
                        operations_to_process.append(sync_op)
                    else:
                        remaining_operations.append(sync_op)
                        
                self.pending_operations = remaining_operations
                
                # Sort by priority
                operations_to_process.sort(
                    key=lambda op: op.priority.value if hasattr(op.priority, 'value') else 0
                )
                
                # Execute operations
                for sync_op in operations_to_process:
                    await self._execute_sync_operation(sync_op)
                    
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Sync scheduler error: {e}")
                await asyncio.sleep(5)
                
    async def _execute_sync_operation(self, sync_op: SyncOperation):
        """Execute a sync operation"""
        
        try:
            logger.info(f"Executing sync operation {sync_op.id}")
            
            # Filter target devices based on their status and capabilities
            valid_targets = await self._filter_valid_targets(sync_op)
            
            if not valid_targets:
                sync_op.error_message = "No valid target devices"
                sync_op.success = False
                self.completed_operations.append(sync_op)
                return
                
            # Execute sync for each target device
            success_count = 0
            
            for device_id in valid_targets:
                try:
                    await self._sync_to_device(sync_op, device_id)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync to device {device_id}: {e}")
                    
            # Mark operation as successful if at least one target succeeded
            sync_op.success = success_count > 0
            sync_op.completed_at = time.time()
            
            # Move to completed operations
            self.completed_operations.append(sync_op)
            
            logger.info(f"Completed sync operation {sync_op.id} "
                       f"(success: {success_count}/{len(valid_targets)})")
                       
        except Exception as e:
            logger.error(f"Error executing sync operation {sync_op.id}: {e}")
            
            # Handle retry logic
            if sync_op.retry_count < sync_op.max_retries:
                sync_op.retry_count += 1
                sync_op.scheduled_at = time.time() + (2 ** sync_op.retry_count)  # Exponential backoff
                self.pending_operations.append(sync_op)
            else:
                sync_op.success = False
                sync_op.error_message = str(e)
                sync_op.completed_at = time.time()
                self.completed_operations.append(sync_op)
                self.stats['sync_errors'] += 1
                
    async def _filter_valid_targets(self, sync_op: SyncOperation) -> List[str]:
        """Filter target devices based on their status and capabilities"""
        
        valid_targets = []
        
        for device_id in sync_op.target_device_ids:
            device_info = self.devices.get(device_id)
            if not device_info:
                continue
                
            # Check device status
            if device_info.status == DeviceStatus.OFFLINE:
                # Queue for offline sync if supported
                if device_info.capabilities.supports_offline:
                    if self.offline_handler:
                        await self.offline_handler.queue_operation(
                            operation_type="sync",
                            data={
                                'sync_operation': sync_op,
                                'target_device': device_id
                            }
                        )
                continue
                
            # Check data category support
            if (device_info.capabilities.sync_categories and 
                sync_op.data_category not in device_info.capabilities.sync_categories):
                continue
                
            # Check device capabilities
            if not self._check_device_capabilities(device_info, sync_op):
                continue
                
            valid_targets.append(device_id)
            
        return valid_targets
        
    def _check_device_capabilities(self, device_info: DeviceInfo, sync_op: SyncOperation) -> bool:
        """Check if device has required capabilities for sync operation"""
        
        # Check storage capacity
        data_size = self._estimate_data_size(sync_op.data)
        if (device_info.capabilities.storage_capacity > 0 and 
            data_size > device_info.capabilities.storage_capacity):
            return False
            
        # Check bandwidth requirements for large operations
        bandwidth_limit = sync_op.metadata.get('bandwidth_limit')
        if (bandwidth_limit and device_info.capabilities.bandwidth_limit > 0 and
            bandwidth_limit > device_info.capabilities.bandwidth_limit):
            return False
            
        return True
        
    def _estimate_data_size(self, data: Dict[str, Any]) -> int:
        """Estimate the size of data in bytes"""
        try:
            data_str = json.dumps(data, default=str)
            return len(data_str.encode())
        except:
            return 0
            
    async def _sync_to_device(self, sync_op: SyncOperation, device_id: str):
        """Sync data to a specific device"""
        
        device_info = self.devices.get(device_id)
        if not device_info:
            raise ValueError(f"Device {device_id} not found")
            
        # Prepare sync message
        sync_message = {
            'type': 'sync_data',
            'operation_id': sync_op.id,
            'data_category': sync_op.data_category.value,
            'operation_type': sync_op.operation_type,
            'data': sync_op.data,
            'source_device': sync_op.source_device_id,
            'timestamp': time.time()
        }
        
        # Apply compression if supported
        if device_info.capabilities.supports_compression:
            sync_message['compressed'] = True
            # In production, compress the data here
            
        # Apply encryption if required
        if device_info.capabilities.supports_encryption:
            sync_message['encrypted'] = True
            # In production, encrypt the data here
            
        # Send via WebSocket if device is connected
        if (self.websocket_manager and device_info.connection_id):
            try:
                await self.websocket_manager.send_to_device(
                    device_id, 
                    sync_message
                )
                
                # Update device sync timestamp
                device_info.last_sync = time.time()
                
            except Exception as e:
                logger.error(f"Failed to send sync message to device {device_id}: {e}")
                raise
                
        else:
            # Queue for offline delivery
            if self.offline_handler:
                await self.offline_handler.queue_operation(
                    operation_type="sync_delivery",
                    data={
                        'device_id': device_id,
                        'sync_message': sync_message
                    }
                )
                
    async def _device_monitor(self):
        """Monitor device health and connectivity"""
        
        while self._running:
            try:
                current_time = time.time()
                stale_threshold = 300  # 5 minutes
                
                for device_id, device_info in self.devices.items():
                    # Check for stale devices
                    if (current_time - device_info.last_seen > stale_threshold and
                        device_info.status != DeviceStatus.OFFLINE):
                        
                        await self.update_device_status(device_id, DeviceStatus.OFFLINE)
                        logger.info(f"Marked device {device_id} as offline (stale)")
                        
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Device monitor error: {e}")
                await asyncio.sleep(60)
                
    async def _subscribe_device_to_channels(self, device_info: DeviceInfo):
        """Subscribe device to relevant sync channels"""
        
        channels = [
            f"user:{device_info.user_id}",
            f"device_type:{device_info.device_type.value}"
        ]
        
        # Add data category channels
        for category in device_info.capabilities.sync_categories:
            channels.append(f"category:{category.value}")
            
        for channel in channels:
            if channel not in self.sync_channels:
                self.sync_channels[channel] = set()
            self.sync_channels[channel].add(device_info.device_id)
            
    async def _unsubscribe_device_from_channels(self, device_id: str):
        """Unsubscribe device from all sync channels"""
        
        for channel, device_ids in self.sync_channels.items():
            device_ids.discard(device_id)
            
    async def _trigger_initial_sync(self, device_info: DeviceInfo):
        """Trigger initial synchronization for a new device"""
        
        # Get other devices for the same user
        other_devices = self.user_devices.get(device_info.user_id, set()) - {device_info.device_id}
        
        if other_devices:
            # Find the most recently synced device to use as source
            source_device_id = max(
                other_devices,
                key=lambda did: self.devices.get(did, DeviceInfo()).last_sync or 0
            )
            
            # Create initial sync operations for each supported category
            for category in device_info.capabilities.sync_categories:
                await self.sync_data(
                    source_device_id=source_device_id,
                    data_category=category,
                    operation_type="initial_sync",
                    data={'full_sync': True},
                    target_device_ids=[device_info.device_id],
                    priority=SyncPriority.HIGH
                )
                
    async def _trigger_device_sync(self, device_id: str):
        """Trigger synchronization for a device that came online"""
        
        device_info = self.devices.get(device_id)
        if not device_info:
            return
            
        # Check for pending sync operations
        pending_for_device = [
            op for op in self.pending_operations
            if device_id in op.target_device_ids
        ]
        
        # Execute high priority operations immediately
        for sync_op in pending_for_device:
            if sync_op.priority == SyncPriority.IMMEDIATE:
                await self._execute_sync_operation(sync_op)
                self.pending_operations.remove(sync_op)
                
    async def _handle_device_offline(self, device_id: str):
        """Handle operations when a device goes offline"""
        
        # Update pending operations to handle offline state
        for sync_op in self.pending_operations:
            if device_id in sync_op.target_device_ids:
                # Queue for offline delivery
                if self.offline_handler:
                    await self.offline_handler.queue_operation(
                        operation_type="sync_offline",
                        data={
                            'sync_operation': sync_op,
                            'offline_device': device_id
                        }
                    )
                    
    def _create_default_policies(self):
        """Create default synchronization policies"""
        
        # Real-time policy for critical data
        self.sync_policies['realtime_critical'] = SyncPolicy(
            name="realtime_critical",
            data_categories=[
                DataCategory.USER_PROFILE,
                DataCategory.APPOINTMENTS
            ],
            sync_frequency=0,  # Immediate
            immediate_sync=True,
            compression_enabled=True,
            encryption_required=True
        )
        
        # Mobile-optimized policy
        self.sync_policies['mobile_optimized'] = SyncPolicy(
            name="mobile_optimized",
            device_types=[DeviceType.MOBILE],
            sync_frequency=300,  # 5 minutes
            immediate_sync=False,
            compression_enabled=True,
            bandwidth_limit=1024 * 1024,  # 1MB/s
            conditions={'battery_level': '>20%'}
        )
        
        # Background sync policy
        self.sync_policies['background'] = SyncPolicy(
            name="background",
            data_categories=[
                DataCategory.CACHE,
                DataCategory.TEMPORARY
            ],
            sync_frequency=3600,  # 1 hour
            immediate_sync=False,
            compression_enabled=True
        )
        
    def get_user_devices(self, user_id: str) -> List[DeviceInfo]:
        """Get all devices for a user"""
        device_ids = self.user_devices.get(user_id, set())
        return [self.devices[did] for did in device_ids if did in self.devices]
        
    def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """Get information about a specific device"""
        return self.devices.get(device_id)
        
    def get_sync_status(self, user_id: str = None, device_id: str = None) -> Dict[str, Any]:
        """Get synchronization status"""
        
        status = {
            'pending_operations': len(self.pending_operations),
            'completed_operations': len(self.completed_operations),
            'stats': self.stats.copy()
        }
        
        if user_id:
            user_devices = self.get_user_devices(user_id)
            status['devices'] = [
                {
                    'device_id': d.device_id,
                    'device_name': d.device_name,
                    'device_type': d.device_type.value,
                    'status': d.status.value,
                    'last_seen': d.last_seen,
                    'last_sync': d.last_sync
                }
                for d in user_devices
            ]
            
        if device_id:
            device_info = self.get_device_info(device_id)
            if device_info:
                status['device'] = {
                    'device_id': device_info.device_id,
                    'status': device_info.status.value,
                    'capabilities': device_info.capabilities,
                    'last_seen': device_info.last_seen,
                    'last_sync': device_info.last_sync
                }
                
        return status