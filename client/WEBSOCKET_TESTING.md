# WebSocket Testing in BDC

This document outlines the implementation and testing of WebSocket functionality in the BDC application.

## Implementation

We've implemented comprehensive WebSocket testing using Vitest and Jest's mocking capabilities. The tests are located in:

- `/src/test/websocket/basic.test.js`: Basic test setup verification
- `/src/test/websocket/socket.test.jsx`: Socket utility testing
- `/src/test/websocket/ProgramWebSocket.test.jsx`: Program-specific WebSocket functionality

## Testing Approach

Our approach to testing WebSockets follows these principles:

1. **Mock the Socket.IO client**: Create a mock implementation of the Socket.IO functionality to avoid actual network connections.
2. **Track event handlers**: Store registered event handlers to simulate real-time events.
3. **Test event emission**: Verify that components emit the correct events.
4. **Test event reception**: Simulate receiving events and verify component reactions.
5. **Test connection state**: Verify that components respond to connection state changes.

## Example Test Pattern

```jsx
// Mock socket implementation
const mockSocket = {
  connected: true,
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn()
};

// Store for event handlers
const savedHandlers = {};

// Mock the 'on' method to save handlers
mockSocket.on.mockImplementation((event, handler) => {
  savedHandlers[event] = handler;
  return () => {}; // Return cleanup function
});

// Test receiving an event
it('handles program_created event', () => {
  // Register handler
  const handler = vi.fn();
  mockSocket.on('program_created', handler);
  
  // Simulate event
  const program = { id: 123, name: 'Test Program' };
  savedHandlers.program_created({ program });
  
  // Verify handler called
  expect(handler).toHaveBeenCalledWith({ program });
});

// Test emitting an event
it('emits create_program event', () => {
  // Set up component
  render(<CreateProgramButton socket={mockSocket} />);
  
  // Trigger action
  fireEvent.click(screen.getByText('Create Program'));
  
  // Verify event emitted
  expect(mockSocket.emit).toHaveBeenCalledWith(
    'create_program',
    expect.objectContaining({ name: 'New Program' })
  );
});
```

## Resolved Issues

During implementation, we encountered and resolved several issues:

1. **Path alias resolution**: Updated the Vitest configuration to properly resolve path aliases like `@/components`.
2. **Vitest version incompatibility**: Downgraded from Vitest 3.1.3 to 0.34.6 to fix syntax parsing issues.
3. **JSX parsing errors**: Fixed errors with the JSX parser in test files.
4. **Mock implementation**: Ensured proper cleanup of handlers between tests.

## Best Practices

When writing WebSocket tests:

1. **Always clean up handlers** between tests to prevent test contamination.
2. **Keep mocks simple** but comprehensive enough to simulate real behavior.
3. **Test both directions** of communication (emitting and receiving).
4. **Verify state changes** caused by WebSocket events.
5. **Use waitFor** for asynchronous updates to the UI.

## Running Tests

To run WebSocket tests specifically:

```bash
npm run test -- websocket
```

To run all tests:

```bash
npm run test
```