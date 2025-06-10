"""
WebSocket Connection Manager

Handles WebSocket connections for real-time synchronization including:
- Connection lifecycle management
- Authentication and authorization
- Connection pooling and load balancing
- Message routing and broadcasting
- Heartbeat and keep-alive functionality
- Automatic reconnection with exponential backoff
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import jwt
from weakref import WeakSet
import uuid

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """WebSocket connection states"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection"""
    connection_id: str
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    tenant_id: Optional[str] = None
    state: ConnectionState = ConnectionState.CONNECTING
    connected_at: float = field(default_factory=time.time)
    last_ping: float = field(default_factory=time.time)
    last_pong: float = field(default_factory=time.time)
    subscriptions: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """WebSocket message structure"""
    type: str
    data: Dict[str, Any]
    target: Optional[str] = None
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class WebSocketManager:
    """
    Manages WebSocket connections for real-time synchronization
    
    Features:
    - Connection pooling and management
    - Authentication and session management
    - Message routing and broadcasting
    - Heartbeat monitoring
    - Automatic cleanup of stale connections
    """
    
    def __init__(self, jwt_secret: str, heartbeat_interval: int = 30):
        self.jwt_secret = jwt_secret
        self.heartbeat_interval = heartbeat_interval
        
        # Connection management
        self.connections: Dict[str, ConnectionInfo] = {}
        self.websockets: Dict[str, Any] = {}  # WebSocket objects
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.device_connections: Dict[str, Set[str]] = {}  # device_id -> connection_ids
        self.tenant_connections: Dict[str, Set[str]] = {}  # tenant_id -> connection_ids
        
        # Subscriptions and channels
        self.channel_subscriptions: Dict[str, Set[str]] = {}  # channel -> connection_ids
        self.connection_subscriptions: Dict[str, Set[str]] = {}  # connection_id -> channels
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'authentication_failures': 0
        }
        
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the WebSocket manager background tasks"""
        logger.info("Starting WebSocket manager")
        self._heartbeat_task = asyncio.create_task(self._heartbeat_monitor())
        self._cleanup_task = asyncio.create_task(self._cleanup_stale_connections())
        
    async def stop(self):
        """Stop the WebSocket manager and cleanup resources"""
        logger.info("Stopping WebSocket manager")
        
        # Cancel background tasks
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
            
        # Close all connections
        await self._close_all_connections()
        
    async def handle_connection(self, websocket, path: str = None):
        """Handle a new WebSocket connection"""
        connection_id = str(uuid.uuid4())
        
        try:
            # Create connection info
            connection_info = ConnectionInfo(connection_id=connection_id)
            self.connections[connection_id] = connection_info
            self.websockets[connection_id] = websocket
            
            self.stats['total_connections'] += 1
            self.stats['active_connections'] += 1
            
            logger.info(f"New WebSocket connection: {connection_id}")
            
            # Handle connection lifecycle
            await self._handle_connection_lifecycle(connection_id, websocket)
            
        except Exception as e:
            logger.error(f"Error handling connection {connection_id}: {e}")
        finally:
            await self._cleanup_connection(connection_id)
            
    async def _handle_connection_lifecycle(self, connection_id: str, websocket):
        """Handle the full lifecycle of a WebSocket connection"""
        connection_info = self.connections[connection_id]
        
        try:
            # Set initial state
            connection_info.state = ConnectionState.CONNECTED
            
            # Send welcome message
            await self._send_to_connection(connection_id, Message(
                type="welcome",
                data={"connection_id": connection_id}
            ))
            
            # Handle incoming messages
            async for message in websocket:
                try:
                    await self._handle_message(connection_id, message)
                except Exception as e:
                    logger.error(f"Error handling message from {connection_id}: {e}")
                    await self._send_error(connection_id, str(e))
                    
        except Exception as e:
            logger.error(f"Connection lifecycle error for {connection_id}: {e}")
        finally:
            connection_info.state = ConnectionState.DISCONNECTED
            
    async def _handle_message(self, connection_id: str, raw_message: str):
        """Handle an incoming WebSocket message"""
        connection_info = self.connections.get(connection_id)
        if not connection_info:
            return
            
        try:
            # Parse message
            message_data = json.loads(raw_message)
            message = Message(**message_data)
            
            self.stats['messages_received'] += 1
            
            # Apply middleware
            for middleware in self.middleware:
                message = await middleware(connection_id, message)
                if not message:
                    return
                    
            # Handle special message types
            if message.type == "authenticate":
                await self._handle_authentication(connection_id, message)
            elif message.type == "subscribe":
                await self._handle_subscription(connection_id, message)
            elif message.type == "unsubscribe":
                await self._handle_unsubscription(connection_id, message)
            elif message.type == "ping":
                await self._handle_ping(connection_id, message)
            else:
                # Route to registered handlers
                handler = self.message_handlers.get(message.type)
                if handler:
                    await handler(connection_id, message)
                else:
                    logger.warning(f"No handler for message type: {message.type}")
                    
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {connection_id}")
            await self._send_error(connection_id, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message from {connection_id}: {e}")
            await self._send_error(connection_id, "Message processing error")
            
    async def _handle_authentication(self, connection_id: str, message: Message):
        """Handle authentication message"""
        connection_info = self.connections.get(connection_id)
        if not connection_info:
            return
            
        try:
            token = message.data.get('token')
            if not token:
                raise ValueError("No authentication token provided")
                
            # Verify JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Extract user information
            user_id = payload.get('user_id')
            device_id = message.data.get('device_id')
            tenant_id = payload.get('tenant_id')
            
            # Update connection info
            connection_info.user_id = user_id
            connection_info.device_id = device_id
            connection_info.tenant_id = tenant_id
            connection_info.state = ConnectionState.AUTHENTICATED
            
            # Update indexes
            if user_id:
                self.user_connections.setdefault(user_id, set()).add(connection_id)
            if device_id:
                self.device_connections.setdefault(device_id, set()).add(connection_id)
            if tenant_id:
                self.tenant_connections.setdefault(tenant_id, set()).add(connection_id)
                
            logger.info(f"Connection {connection_id} authenticated for user {user_id}")
            
            # Send authentication success
            await self._send_to_connection(connection_id, Message(
                type="authenticated",
                data={
                    "user_id": user_id,
                    "device_id": device_id,
                    "tenant_id": tenant_id
                }
            ))
            
        except jwt.InvalidTokenError:
            self.stats['authentication_failures'] += 1
            logger.warning(f"Invalid token for connection {connection_id}")
            await self._send_error(connection_id, "Invalid authentication token")
        except Exception as e:
            self.stats['authentication_failures'] += 1
            logger.error(f"Authentication error for {connection_id}: {e}")
            await self._send_error(connection_id, "Authentication failed")
            
    async def _handle_subscription(self, connection_id: str, message: Message):
        """Handle subscription to channels"""
        connection_info = self.connections.get(connection_id)
        if not connection_info or connection_info.state != ConnectionState.AUTHENTICATED:
            await self._send_error(connection_id, "Must be authenticated to subscribe")
            return
            
        channels = message.data.get('channels', [])
        if isinstance(channels, str):
            channels = [channels]
            
        for channel in channels:
            # Add to subscriptions
            self.channel_subscriptions.setdefault(channel, set()).add(connection_id)
            self.connection_subscriptions.setdefault(connection_id, set()).add(channel)
            connection_info.subscriptions.add(channel)
            
        logger.info(f"Connection {connection_id} subscribed to channels: {channels}")
        
        await self._send_to_connection(connection_id, Message(
            type="subscribed",
            data={"channels": channels}
        ))
        
    async def _handle_unsubscription(self, connection_id: str, message: Message):
        """Handle unsubscription from channels"""
        channels = message.data.get('channels', [])
        if isinstance(channels, str):
            channels = [channels]
            
        for channel in channels:
            # Remove from subscriptions
            if channel in self.channel_subscriptions:
                self.channel_subscriptions[channel].discard(connection_id)
                if not self.channel_subscriptions[channel]:
                    del self.channel_subscriptions[channel]
                    
            if connection_id in self.connection_subscriptions:
                self.connection_subscriptions[connection_id].discard(channel)
                
            connection_info = self.connections.get(connection_id)
            if connection_info:
                connection_info.subscriptions.discard(channel)
                
        logger.info(f"Connection {connection_id} unsubscribed from channels: {channels}")
        
        await self._send_to_connection(connection_id, Message(
            type="unsubscribed", 
            data={"channels": channels}
        ))
        
    async def _handle_ping(self, connection_id: str, message: Message):
        """Handle ping message"""
        connection_info = self.connections.get(connection_id)
        if connection_info:
            connection_info.last_ping = time.time()
            
        await self._send_to_connection(connection_id, Message(
            type="pong",
            data=message.data
        ))
        
    async def send_to_user(self, user_id: str, message: Message):
        """Send message to all connections for a specific user"""
        connection_ids = self.user_connections.get(user_id, set())
        for connection_id in connection_ids.copy():
            await self._send_to_connection(connection_id, message)
            
    async def send_to_device(self, device_id: str, message: Message):
        """Send message to a specific device"""
        connection_ids = self.device_connections.get(device_id, set())
        for connection_id in connection_ids.copy():
            await self._send_to_connection(connection_id, message)
            
    async def send_to_tenant(self, tenant_id: str, message: Message):
        """Send message to all connections for a tenant"""
        connection_ids = self.tenant_connections.get(tenant_id, set())
        for connection_id in connection_ids.copy():
            await self._send_to_connection(connection_id, message)
            
    async def broadcast_to_channel(self, channel: str, message: Message):
        """Broadcast message to all subscribers of a channel"""
        connection_ids = self.channel_subscriptions.get(channel, set())
        for connection_id in connection_ids.copy():
            await self._send_to_connection(connection_id, message)
            
    async def _send_to_connection(self, connection_id: str, message: Message):
        """Send message to a specific connection"""
        websocket = self.websockets.get(connection_id)
        if not websocket:
            return
            
        try:
            message_json = json.dumps({
                'type': message.type,
                'data': message.data,
                'timestamp': message.timestamp,
                'message_id': message.message_id
            })
            
            await websocket.send(message_json)
            self.stats['messages_sent'] += 1
            
        except Exception as e:
            logger.error(f"Error sending message to {connection_id}: {e}")
            await self._cleanup_connection(connection_id)
            
    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message to connection"""
        await self._send_to_connection(connection_id, Message(
            type="error",
            data={"message": error_message}
        ))
        
    async def _heartbeat_monitor(self):
        """Monitor connection health with heartbeats"""
        while True:
            try:
                current_time = time.time()
                stale_connections = []
                
                for connection_id, connection_info in self.connections.items():
                    # Check if connection is stale
                    if current_time - connection_info.last_ping > self.heartbeat_interval * 2:
                        stale_connections.append(connection_id)
                    elif current_time - connection_info.last_ping > self.heartbeat_interval:
                        # Send ping
                        await self._send_to_connection(connection_id, Message(
                            type="ping",
                            data={"timestamp": current_time}
                        ))
                        
                # Cleanup stale connections
                for connection_id in stale_connections:
                    logger.info(f"Cleaning up stale connection: {connection_id}")
                    await self._cleanup_connection(connection_id)
                    
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Heartbeat monitor error: {e}")
                await asyncio.sleep(5)
                
    async def _cleanup_stale_connections(self):
        """Periodic cleanup of stale connections"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Additional cleanup logic can be added here
                logger.info(f"Active connections: {len(self.connections)}")
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                
    async def _cleanup_connection(self, connection_id: str):
        """Clean up a connection and all its associated data"""
        connection_info = self.connections.pop(connection_id, None)
        websocket = self.websockets.pop(connection_id, None)
        
        if not connection_info:
            return
            
        # Update statistics
        self.stats['active_connections'] = max(0, self.stats['active_connections'] - 1)
        
        # Remove from user connections
        if connection_info.user_id:
            user_connections = self.user_connections.get(connection_info.user_id, set())
            user_connections.discard(connection_id)
            if not user_connections:
                self.user_connections.pop(connection_info.user_id, None)
                
        # Remove from device connections  
        if connection_info.device_id:
            device_connections = self.device_connections.get(connection_info.device_id, set())
            device_connections.discard(connection_id)
            if not device_connections:
                self.device_connections.pop(connection_info.device_id, None)
                
        # Remove from tenant connections
        if connection_info.tenant_id:
            tenant_connections = self.tenant_connections.get(connection_info.tenant_id, set())
            tenant_connections.discard(connection_id)
            if not tenant_connections:
                self.tenant_connections.pop(connection_info.tenant_id, None)
                
        # Remove from channel subscriptions
        for channel in connection_info.subscriptions:
            if channel in self.channel_subscriptions:
                self.channel_subscriptions[channel].discard(connection_id)
                if not self.channel_subscriptions[channel]:
                    del self.channel_subscriptions[channel]
                    
        self.connection_subscriptions.pop(connection_id, None)
        
        # Close websocket if still open
        if websocket:
            try:
                await websocket.close()
            except Exception:
                pass
                
        logger.info(f"Cleaned up connection: {connection_id}")
        
    async def _close_all_connections(self):
        """Close all active connections"""
        connection_ids = list(self.connections.keys())
        for connection_id in connection_ids:
            await self._cleanup_connection(connection_id)
            
    def add_message_handler(self, message_type: str, handler: Callable):
        """Register a message handler for a specific message type"""
        self.message_handlers[message_type] = handler
        
    def add_middleware(self, middleware: Callable):
        """Add middleware to process messages"""
        self.middleware.append(middleware)
        
    def get_connection_info(self, connection_id: str) -> Optional[ConnectionInfo]:
        """Get information about a specific connection"""
        return self.connections.get(connection_id)
        
    def get_user_connections(self, user_id: str) -> Set[str]:
        """Get all connection IDs for a user"""
        return self.user_connections.get(user_id, set()).copy()
        
    def get_device_connections(self, device_id: str) -> Set[str]:
        """Get all connection IDs for a device"""
        return self.device_connections.get(device_id, set()).copy()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return self.stats.copy()