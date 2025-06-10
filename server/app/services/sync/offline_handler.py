"""
Offline/Online State Handler

Manages offline/online state transitions and queues operations when offline:
- Network state detection and monitoring
- Operation queuing during offline periods
- Automatic retry with exponential backoff
- Conflict detection and resolution preparation
- Data consistency maintenance during network interruptions
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timedelta
import pickle
import os

logger = logging.getLogger(__name__)


class NetworkState(Enum):
    """Network connectivity states"""
    ONLINE = "online"
    OFFLINE = "offline"
    RECONNECTING = "reconnecting"
    DEGRADED = "degraded"  # Poor connection


class OperationType(Enum):
    """Types of operations that can be queued"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"
    CUSTOM = "custom"


class OperationPriority(Enum):
    """Priority levels for queued operations"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class QueuedOperation:
    """Represents an operation queued for execution when online"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: OperationType = OperationType.SYNC
    priority: OperationPriority = OperationPriority.MEDIUM
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    retry_count: int = 0
    max_retries: int = 5
    next_retry: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None


@dataclass
class NetworkStatus:
    """Current network status information"""
    state: NetworkState = NetworkState.OFFLINE
    last_online: Optional[float] = None
    last_offline: Optional[float] = None
    connectivity_score: float = 0.0  # 0.0 = offline, 1.0 = perfect
    latency: Optional[float] = None
    bandwidth_estimate: Optional[float] = None


class OfflineHandler:
    """
    Handles offline/online state transitions and operation queuing
    
    Features:
    - Network state monitoring and detection
    - Operation queuing with priority and dependency management
    - Automatic retry with exponential backoff
    - Persistent storage of queued operations
    - Conflict detection preparation
    - Bandwidth-aware operation scheduling
    """
    
    def __init__(self, 
                 storage_path: str = "/tmp/bdc_offline_queue",
                 max_queue_size: int = 10000,
                 connectivity_check_interval: int = 5,
                 retry_base_delay: float = 1.0,
                 retry_max_delay: float = 300.0):
        
        self.storage_path = storage_path
        self.max_queue_size = max_queue_size
        self.connectivity_check_interval = connectivity_check_interval
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        
        # State management
        self.network_status = NetworkStatus()
        self.operation_queue: List[QueuedOperation] = []
        self.processing_queue: Set[str] = set()  # Operations currently being processed
        self.completed_operations: Set[str] = set()
        self.failed_operations: Set[str] = set()
        
        # Event handlers
        self.state_change_handlers: List[Callable] = []
        self.operation_handlers: Dict[OperationType, Callable] = {}
        self.retry_handlers: Dict[str, Callable] = {}
        
        # Background tasks
        self._connectivity_task: Optional[asyncio.Task] = None
        self._queue_processor_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'operations_queued': 0,
            'operations_completed': 0,
            'operations_failed': 0,
            'network_transitions': 0,
            'total_offline_time': 0.0,
            'current_offline_start': None
        }
        
        # Create storage directory
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
    async def start(self):
        """Start the offline handler background tasks"""
        logger.info("Starting offline handler")
        
        # Load persisted queue
        await self._load_queue()
        
        # Start background tasks
        self._connectivity_task = asyncio.create_task(self._monitor_connectivity())
        self._queue_processor_task = asyncio.create_task(self._process_queue())
        self._cleanup_task = asyncio.create_task(self._cleanup_completed_operations())
        
    async def stop(self):
        """Stop the offline handler and save state"""
        logger.info("Stopping offline handler")
        
        # Cancel background tasks
        if self._connectivity_task:
            self._connectivity_task.cancel()
        if self._queue_processor_task:
            self._queue_processor_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
            
        # Save queue state
        await self._save_queue()
        
    async def queue_operation(self, 
                            operation_type: OperationType,
                            data: Dict[str, Any],
                            priority: OperationPriority = OperationPriority.MEDIUM,
                            dependencies: List[str] = None,
                            callback: Callable = None,
                            error_callback: Callable = None,
                            metadata: Dict[str, Any] = None) -> str:
        """Queue an operation for execution when online"""
        
        if len(self.operation_queue) >= self.max_queue_size:
            raise ValueError("Operation queue is full")
            
        operation = QueuedOperation(
            type=operation_type,
            priority=priority,
            data=data,
            dependencies=dependencies or [],
            callback=callback,
            error_callback=error_callback,
            metadata=metadata or {}
        )
        
        # Add to queue in priority order
        self._insert_operation_by_priority(operation)
        
        self.stats['operations_queued'] += 1
        logger.info(f"Queued operation {operation.id} of type {operation_type}")
        
        # Save queue state
        await self._save_queue()
        
        return operation.id
        
    def _insert_operation_by_priority(self, operation: QueuedOperation):
        """Insert operation into queue maintaining priority order"""
        inserted = False
        for i, existing_op in enumerate(self.operation_queue):
            if operation.priority.value > existing_op.priority.value:
                self.operation_queue.insert(i, operation)
                inserted = True
                break
                
        if not inserted:
            self.operation_queue.append(operation)
            
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a queued operation"""
        for i, operation in enumerate(self.operation_queue):
            if operation.id == operation_id:
                self.operation_queue.pop(i)
                logger.info(f"Cancelled operation {operation_id}")
                await self._save_queue()
                return True
        return False
        
    async def get_operation_status(self, operation_id: str) -> Optional[str]:
        """Get the current status of an operation"""
        if operation_id in self.processing_queue:
            return "processing"
        elif operation_id in self.completed_operations:
            return "completed"
        elif operation_id in self.failed_operations:
            return "failed"
        elif any(op.id == operation_id for op in self.operation_queue):
            return "queued"
        return None
        
    async def set_network_state(self, state: NetworkState, 
                              connectivity_score: float = None,
                              latency: float = None,
                              bandwidth_estimate: float = None):
        """Manually set network state (useful for testing or manual control)"""
        old_state = self.network_status.state
        
        # Update network status
        self.network_status.state = state
        if connectivity_score is not None:
            self.network_status.connectivity_score = connectivity_score
        if latency is not None:
            self.network_status.latency = latency
        if bandwidth_estimate is not None:
            self.network_status.bandwidth_estimate = bandwidth_estimate
            
        # Update timestamps
        current_time = time.time()
        if state == NetworkState.ONLINE and old_state != NetworkState.ONLINE:
            self.network_status.last_online = current_time
            if self.stats['current_offline_start']:
                self.stats['total_offline_time'] += current_time - self.stats['current_offline_start']
                self.stats['current_offline_start'] = None
        elif state == NetworkState.OFFLINE and old_state != NetworkState.OFFLINE:
            self.network_status.last_offline = current_time
            self.stats['current_offline_start'] = current_time
            
        # Track state transitions
        if old_state != state:
            self.stats['network_transitions'] += 1
            logger.info(f"Network state changed from {old_state} to {state}")
            
            # Notify handlers
            for handler in self.state_change_handlers:
                try:
                    await handler(old_state, state, self.network_status)
                except Exception as e:
                    logger.error(f"Error in state change handler: {e}")
                    
    async def _monitor_connectivity(self):
        """Monitor network connectivity status"""
        while True:
            try:
                # Check connectivity (simplified - in production, use more sophisticated checks)
                connectivity_score = await self._check_connectivity()
                
                # Determine network state based on connectivity score
                if connectivity_score >= 0.8:
                    new_state = NetworkState.ONLINE
                elif connectivity_score >= 0.3:
                    new_state = NetworkState.DEGRADED
                elif self.network_status.state == NetworkState.OFFLINE:
                    # Try to reconnect
                    new_state = NetworkState.RECONNECTING
                else:
                    new_state = NetworkState.OFFLINE
                    
                await self.set_network_state(new_state, connectivity_score)
                
                await asyncio.sleep(self.connectivity_check_interval)
                
            except Exception as e:
                logger.error(f"Connectivity monitoring error: {e}")
                await asyncio.sleep(self.connectivity_check_interval)
                
    async def _check_connectivity(self) -> float:
        """Check network connectivity and return a score (0.0 to 1.0)"""
        try:
            # Simplified connectivity check
            # In production, implement more sophisticated checks:
            # - Multiple endpoint testing
            # - Latency measurements
            # - Bandwidth testing
            # - DNS resolution checks
            
            import aiohttp
            
            start_time = time.time()
            timeout = aiohttp.ClientTimeout(total=5)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get('https://httpbin.org/status/200') as response:
                    if response.status == 200:
                        latency = time.time() - start_time
                        self.network_status.latency = latency
                        
                        # Calculate score based on latency
                        if latency < 0.1:
                            return 1.0
                        elif latency < 0.5:
                            return 0.9
                        elif latency < 1.0:
                            return 0.7
                        elif latency < 2.0:
                            return 0.5
                        else:
                            return 0.3
                            
        except Exception:
            pass
            
        return 0.0  # Offline
        
    async def _process_queue(self):
        """Process queued operations when online"""
        while True:
            try:
                if (self.network_status.state in [NetworkState.ONLINE, NetworkState.DEGRADED] and 
                    self.operation_queue):
                    
                    # Get next operation to process
                    operation = await self._get_next_operation()
                    
                    if operation:
                        await self._execute_operation(operation)
                        
                await asyncio.sleep(1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(5)
                
    async def _get_next_operation(self) -> Optional[QueuedOperation]:
        """Get the next operation to execute from the queue"""
        current_time = time.time()
        
        for i, operation in enumerate(self.operation_queue):
            # Skip if already processing
            if operation.id in self.processing_queue:
                continue
                
            # Check if it's time to retry
            if operation.next_retry and current_time < operation.next_retry:
                continue
                
            # Check dependencies
            if await self._check_dependencies(operation):
                # Remove from queue and return
                return self.operation_queue.pop(i)
                
        return None
        
    async def _check_dependencies(self, operation: QueuedOperation) -> bool:
        """Check if all dependencies for an operation are satisfied"""
        for dep_id in operation.dependencies:
            if dep_id not in self.completed_operations:
                return False
        return True
        
    async def _execute_operation(self, operation: QueuedOperation):
        """Execute a queued operation"""
        self.processing_queue.add(operation.id)
        
        try:
            logger.info(f"Executing operation {operation.id} of type {operation.type}")
            
            # Get handler for operation type
            handler = self.operation_handlers.get(operation.type)
            if not handler:
                raise ValueError(f"No handler for operation type {operation.type}")
                
            # Execute the operation
            result = await handler(operation)
            
            # Mark as completed
            self.completed_operations.add(operation.id)
            self.stats['operations_completed'] += 1
            
            # Call success callback
            if operation.callback:
                try:
                    await operation.callback(operation, result)
                except Exception as e:
                    logger.error(f"Error in operation callback: {e}")
                    
            logger.info(f"Successfully executed operation {operation.id}")
            
        except Exception as e:
            logger.error(f"Failed to execute operation {operation.id}: {e}")
            
            # Handle retry logic
            if operation.retry_count < operation.max_retries:
                await self._schedule_retry(operation, e)
            else:
                # Mark as failed
                self.failed_operations.add(operation.id)
                self.stats['operations_failed'] += 1
                
                # Call error callback
                if operation.error_callback:
                    try:
                        await operation.error_callback(operation, e)
                    except Exception as callback_error:
                        logger.error(f"Error in operation error callback: {callback_error}")
                        
        finally:
            self.processing_queue.discard(operation.id)
            await self._save_queue()
            
    async def _schedule_retry(self, operation: QueuedOperation, error: Exception):
        """Schedule an operation for retry with exponential backoff"""
        operation.retry_count += 1
        
        # Calculate next retry time with exponential backoff
        delay = min(
            self.retry_base_delay * (2 ** operation.retry_count),
            self.retry_max_delay
        )
        
        operation.next_retry = time.time() + delay
        
        # Add back to queue
        self._insert_operation_by_priority(operation)
        
        logger.info(f"Scheduled retry {operation.retry_count}/{operation.max_retries} "
                   f"for operation {operation.id} in {delay:.2f} seconds")
                   
    async def _cleanup_completed_operations(self):
        """Periodic cleanup of completed operations"""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                # Keep only recent completed operations (last 24 hours)
                cutoff_time = time.time() - 86400
                
                # This is simplified - in production, you might want more sophisticated cleanup
                logger.info(f"Completed operations: {len(self.completed_operations)}")
                logger.info(f"Failed operations: {len(self.failed_operations)}")
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                
    async def _save_queue(self):
        """Save the current queue state to persistent storage"""
        try:
            # Prepare data for serialization (exclude non-serializable callbacks)
            queue_data = []
            for op in self.operation_queue:
                op_data = {
                    'id': op.id,
                    'type': op.type.value,
                    'priority': op.priority.value,
                    'data': op.data,
                    'metadata': op.metadata,
                    'created_at': op.created_at,
                    'retry_count': op.retry_count,
                    'max_retries': op.max_retries,
                    'next_retry': op.next_retry,
                    'dependencies': op.dependencies
                }
                queue_data.append(op_data)
                
            save_data = {
                'queue': queue_data,
                'stats': self.stats,
                'network_status': {
                    'state': self.network_status.state.value,
                    'last_online': self.network_status.last_online,
                    'last_offline': self.network_status.last_offline,
                    'connectivity_score': self.network_status.connectivity_score
                }
            }
            
            with open(self.storage_path, 'wb') as f:
                pickle.dump(save_data, f)
                
        except Exception as e:
            logger.error(f"Error saving queue: {e}")
            
    async def _load_queue(self):
        """Load queue state from persistent storage"""
        try:
            if not os.path.exists(self.storage_path):
                return
                
            with open(self.storage_path, 'rb') as f:
                save_data = pickle.load(f)
                
            # Restore queue
            self.operation_queue = []
            for op_data in save_data.get('queue', []):
                operation = QueuedOperation(
                    id=op_data['id'],
                    type=OperationType(op_data['type']),
                    priority=OperationPriority(op_data['priority']),
                    data=op_data['data'],
                    metadata=op_data['metadata'],
                    created_at=op_data['created_at'],
                    retry_count=op_data['retry_count'],
                    max_retries=op_data['max_retries'],
                    next_retry=op_data['next_retry'],
                    dependencies=op_data['dependencies']
                )
                self.operation_queue.append(operation)
                
            # Restore stats
            if 'stats' in save_data:
                self.stats.update(save_data['stats'])
                
            # Restore network status
            if 'network_status' in save_data:
                ns_data = save_data['network_status']
                self.network_status.state = NetworkState(ns_data['state'])
                self.network_status.last_online = ns_data.get('last_online')
                self.network_status.last_offline = ns_data.get('last_offline')
                self.network_status.connectivity_score = ns_data.get('connectivity_score', 0.0)
                
            logger.info(f"Loaded {len(self.operation_queue)} operations from storage")
            
        except Exception as e:
            logger.error(f"Error loading queue: {e}")
            
    def add_state_change_handler(self, handler: Callable):
        """Add a handler for network state changes"""
        self.state_change_handlers.append(handler)
        
    def add_operation_handler(self, operation_type: OperationType, handler: Callable):
        """Add a handler for a specific operation type"""
        self.operation_handlers[operation_type] = handler
        
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status and statistics"""
        return {
            'network_state': self.network_status.state.value,
            'connectivity_score': self.network_status.connectivity_score,
            'queue_size': len(self.operation_queue),
            'processing_count': len(self.processing_queue),
            'completed_count': len(self.completed_operations),
            'failed_count': len(self.failed_operations),
            'stats': self.stats.copy()
        }
        
    def is_online(self) -> bool:
        """Check if currently online"""
        return self.network_status.state in [NetworkState.ONLINE, NetworkState.DEGRADED]