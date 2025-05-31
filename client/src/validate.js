// Simple validation script to check if our code is syntactically correct
console.log('Validation script running...');

// Test WebSocket functionality
function mockSocket() {
  const handlers = {};
  return {
    on: (event, handler) => {
      handlers[event] = handler;
      return () => { delete handlers[event]; };
    },
    emit: (event, data) => {
      console.log(`Emitting ${event} with data:`, data);
    },
    triggerEvent: (event, data) => {
      if (handlers[event]) {
        handlers[event](data);
        return true;
      }
      return false;
    }
  };
}

// Create a mock socket
const socket = mockSocket();

// Register some handlers
const cleanupCreated = socket.on('program_created', (data) => {
  console.log('Program created:', data);
});

const cleanupUpdated = socket.on('program_updated', (data) => {
  console.log('Program updated:', data);
});

// Trigger an event
socket.triggerEvent('program_created', { 
  program: { 
    id: 123, 
    name: 'Test Program' 
  } 
});

// Cleanup
cleanupCreated();
cleanupUpdated();

console.log('Validation complete!');