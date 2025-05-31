# WebSocket Integration in BDC

This document describes the real-time WebSocket functionality implemented in the BDC application.

## Architecture Overview

The BDC application uses Socket.IO to provide real-time updates and notifications across clients:

- **Backend**: Socket.IO server integrated with Flask (see `server/app/socketio_events.py`)
- **Frontend**: Socket.IO client managed through React context (see `client/src/contexts/SocketContext.jsx`)

## Connection Management

The `SocketContext` handles WebSocket connection management automatically:

- Connects when a user authenticates
- Reconnects on connection loss
- Provides authentication via JWT token
- Cleans up on component unmount

## Using WebSockets in Components

To use WebSockets in your components:

```jsx
import { useSocket } from '@/contexts/SocketContext';

function MyComponent() {
  const { connected, on, off, emit, joinRoom, leaveRoom } = useSocket();

  // Listen for events
  useEffect(() => {
    // The `on` function returns a cleanup function that will be called when the component unmounts
    const cleanup = on('program_updated', (data) => {
      console.log('Program updated:', data.program);
      // Update local state here
    });
    
    // Always return the cleanup function
    return cleanup;
  }, [on]);
  
  // Emit events
  const handleAction = () => {
    emit('update_program', { id: 123, name: 'Updated Program' });
  };
  
  return (
    <div>
      <p>Status: {connected ? 'Connected' : 'Disconnected'}</p>
      <button onClick={handleAction}>Update Program</button>
    </div>
  );
}
```

## Supported Events

### Program Events
- `program_created`: Emitted when a new program is created
- `program_updated`: Emitted when a program is updated
- `program_deleted`: Emitted when a program is deleted

### User Events
- `user_joined`: Emitted when a user connects
- `user_left`: Emitted when a user disconnects

### Notification Events
- `notification`: General notifications
- `message`: Direct messages between users

## Testing WebSocket Functionality

Testing WebSocket functionality requires mocking the Socket.IO client. We use Vitest for testing:

```jsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

describe('WebSocket Tests', () => {
  // Create a mock socket
  const mockSocket = {
    connected: true,
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn()
  };
  
  // Store handlers
  const savedHandlers = {};
  
  // Mock the on method to save handlers
  mockSocket.on.mockImplementation((event, handler) => {
    savedHandlers[event] = handler;
    return () => {}; // Return cleanup function
  });
  
  it('handles program_created events', async () => {
    // Register a mock handler
    const handler = vi.fn();
    mockSocket.on('program_created', handler);
    
    // Simulate receiving an event
    const newProgram = { id: 123, name: 'Test Program' };
    savedHandlers.program_created({ program: newProgram });
    
    // Verify the handler was called with the correct data
    expect(handler).toHaveBeenCalledWith({ program: newProgram });
  });
});
```

## Implementation Notes

1. **Reconnection Strategy**: Socket.IO is configured with automatic reconnection with exponential backoff.

2. **Authentication**: JWT tokens are sent with the initial connection to authenticate the user.

3. **Room Management**: Users join specific rooms based on their permissions and roles:
   - `user_{id}`: Personal notifications
   - `tenant_{id}`: Organization-specific updates
   - `global`: System-wide announcements

4. **Error Handling**: Connection errors are displayed to users with appropriate recovery options.

5. **Performance Considerations**: 
   - Keep payloads small to minimize bandwidth usage
   - Use fine-grained events to prevent unnecessary updates
   - Implement throttling for high-frequency events

## Troubleshooting

If you encounter WebSocket issues:

1. **Check Network**: Ensure WebSocket connections aren't blocked by firewalls
2. **Inspect Browser Console**: Look for connection errors
3. **Verify Token**: JWT token may be expired
4. **Check CORS**: Cross-origin requests may be blocked
5. **Test with Simple Client**: Use a WebSocket test client to verify server functionality