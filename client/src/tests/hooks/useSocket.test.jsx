// TODO: i18n - processed
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useSocket } from '@/contexts/SocketContext';
// Mock socket.io-client
import { useTranslation } from "react-i18next";const mockSocket = {
  on: vi.fn(),
  off: vi.fn(),
  emit: vi.fn(),
  disconnect: vi.fn(),
  connected: true
};
vi.mock('socket.io-client', () => ({
  default: vi.fn(() => mockSocket)
}));
// Mock auth context
const mockAuth = {
  user: { id: 1, email: 'test@example.com' },
  isAuthenticated: true
};
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => mockAuth
}));
// Create wrapper component for SocketProvider
const createWrapper = () => {
  const { SocketProvider } = require('@/contexts/SocketContext');
  return ({ children }) =>
  <SocketProvider>
      {children}
    </SocketProvider>;

};
describe('useSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('provides socket connection status', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    expect(result.current.connected).toBeDefined();
  });
  it('provides emit function', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    expect(typeof result.current.emit).toBe('function');
  });
  it('emits events when connected', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    act(() => {
      result.current.emit('test_event', { data: 'test' });
    });
    expect(mockSocket.emit).toHaveBeenCalledWith('test_event', { data: 'test' });
  });
  it('provides on function for event listeners', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    const handler = vi.fn();
    act(() => {
      result.current.on('test_event', handler);
    });
    expect(mockSocket.on).toHaveBeenCalledWith('test_event', handler);
  });
  it('provides off function for removing listeners', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    const handler = vi.fn();
    act(() => {
      result.current.off('test_event', handler);
    });
    expect(mockSocket.off).toHaveBeenCalledWith('test_event', handler);
  });
  it('provides joinRoom function', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    act(() => {
      result.current.joinRoom('test_room');
    });
    expect(mockSocket.emit).toHaveBeenCalledWith('join_room', { room: 'test_room' });
  });
  it('provides leaveRoom function', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    act(() => {
      result.current.leaveRoom('test_room');
    });
    expect(mockSocket.emit).toHaveBeenCalledWith('leave_room', { room: 'test_room' });
  });
  it('provides sendMessage function', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    const callback = vi.fn();
    act(() => {
      result.current.sendMessage('test_room', 'Hello world', callback);
    });
    expect(mockSocket.emit).toHaveBeenCalledWith(
      'send_message',
      { room: 'test_room', message: 'Hello world' },
      callback
    );
  });
  it('provides markAsRead function', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    act(() => {
      result.current.markAsRead([1, 2, 3]);
    });
    expect(mockSocket.emit).toHaveBeenCalledWith('mark_as_read', { message_ids: [1, 2, 3] });
  });
  it('tracks online users', () => {
    const wrapper = createWrapper();
    const { result } = renderHook(() => useSocket(), { wrapper });
    expect(result.current.onlineUsers).toBeDefined();
    expect(Array.isArray(result.current.onlineUsers)).toBe(true);
  });
  it('handles connection events', () => {
    const wrapper = createWrapper();
    renderHook(() => useSocket(), { wrapper });
    // Verify that connection event handlers are set up
    expect(mockSocket.on).toHaveBeenCalledWith('connect', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('disconnect', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('connect_error', expect.any(Function));
  });
  it('handles notification events', () => {
    const wrapper = createWrapper();
    renderHook(() => useSocket(), { wrapper });
    // Verify that notification event handlers are set up
    expect(mockSocket.on).toHaveBeenCalledWith('notification', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('user_joined', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('user_left', expect.any(Function));
    expect(mockSocket.on).toHaveBeenCalledWith('message', expect.any(Function));
  });
  it('disconnects when user logs out', () => {
    // Mock auth with no user
    const mockAuthNoUser = {
      user: null,
      isAuthenticated: false
    };
    vi.mocked(require('@/hooks/useAuth').useAuth).mockReturnValue(mockAuthNoUser);
    const wrapper = createWrapper();
    renderHook(() => useSocket(), { wrapper });
    expect(mockSocket.disconnect).toHaveBeenCalled();
  });
});