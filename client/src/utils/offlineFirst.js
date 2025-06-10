/**
 * Offline-First Architecture Utilities
 * Provides comprehensive offline-first data management and synchronization
 */

import { indexedDBManager } from '../services/indexeddb.service';
import { pwaService } from '../services/pwa.service';

/**
 * Offline-First Data Store
 * Manages data with offline-first principles
 */
export class OfflineFirstStore {
  constructor(storeName, options = {}) {
    this.storeName = storeName;
    this.options = {
      syncEndpoint: options.syncEndpoint || `/api/${storeName}`,
      idField: options.idField || 'id',
      timestampField: options.timestampField || 'lastModified',
      syncBatchSize: options.syncBatchSize || 10,
      conflictResolution: options.conflictResolution || 'server-wins',
      ...options
    };
    
    this.subscribers = new Set();
    this.syncInProgress = false;
    this.pendingOperations = new Map();
  }

  /**
   * Initialize the store
   */
  async init() {
    await indexedDBManager.init();
    
    // Setup sync when online
    if (navigator.onLine) {
      this.scheduleSync();
    }
    
    // Listen for online events
    window.addEventListener('online', () => {
      this.scheduleSync();
    });
    
    return this;
  }

  /**
   * Get all items from the store
   */
  async getAll(options = {}) {
    try {
      const items = await indexedDBManager.getAll(this.storeName, options);
      return this.transformItems(items);
    } catch (error) {
      console.error(`[OfflineFirst] Error getting all ${this.storeName}:`, error);
      return [];
    }
  }

  /**
   * Get a single item by ID
   */
  async get(id) {
    try {
      const item = await indexedDBManager.get(this.storeName, id);
      return this.transformItem(item);
    } catch (error) {
      console.error(`[OfflineFirst] Error getting ${this.storeName} ${id}:`, error);
      return null;
    }
  }

  /**
   * Create a new item
   */
  async create(data) {
    const item = this.prepareItem(data, 'create');
    
    try {
      // Store locally first
      await indexedDBManager.add(this.storeName, item);
      
      // Queue for sync
      await this.queueSync('create', item);
      
      // Notify subscribers
      this.notifySubscribers('create', item);
      
      // Try immediate sync if online
      if (navigator.onLine) {
        this.scheduleSync();
      }
      
      return item;
    } catch (error) {
      console.error(`[OfflineFirst] Error creating ${this.storeName}:`, error);
      throw error;
    }
  }

  /**
   * Update an existing item
   */
  async update(id, data) {
    const existing = await this.get(id);
    if (!existing) {
      throw new Error(`Item ${id} not found`);
    }

    const item = this.prepareItem({ ...existing, ...data }, 'update');
    
    try {
      // Store locally first
      await indexedDBManager.put(this.storeName, item);
      
      // Queue for sync
      await this.queueSync('update', item);
      
      // Notify subscribers
      this.notifySubscribers('update', item);
      
      // Try immediate sync if online
      if (navigator.onLine) {
        this.scheduleSync();
      }
      
      return item;
    } catch (error) {
      console.error(`[OfflineFirst] Error updating ${this.storeName} ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete an item
   */
  async delete(id) {
    try {
      const existing = await this.get(id);
      if (!existing) {
        throw new Error(`Item ${id} not found`);
      }

      // Mark as deleted locally
      const deletedItem = { ...existing, _deleted: true, _lastModified: Date.now() };
      await indexedDBManager.put(this.storeName, deletedItem);
      
      // Queue for sync
      await this.queueSync('delete', { [this.options.idField]: id });
      
      // Notify subscribers
      this.notifySubscribers('delete', { [this.options.idField]: id });
      
      // Try immediate sync if online
      if (navigator.onLine) {
        this.scheduleSync();
      }
      
      return true;
    } catch (error) {
      console.error(`[OfflineFirst] Error deleting ${this.storeName} ${id}:`, error);
      throw error;
    }
  }

  /**
   * Search items with query
   */
  async search(query) {
    try {
      const allItems = await this.getAll();
      
      return allItems.filter(item => {
        return Object.values(item).some(value => {
          if (typeof value === 'string') {
            return value.toLowerCase().includes(query.toLowerCase());
          }
          return false;
        });
      });
    } catch (error) {
      console.error(`[OfflineFirst] Error searching ${this.storeName}:`, error);
      return [];
    }
  }

  /**
   * Sync with server
   */
  async sync(force = false) {
    if (this.syncInProgress && !force) {
      console.log(`[OfflineFirst] Sync already in progress for ${this.storeName}`);
      return;
    }

    if (!navigator.onLine) {
      console.log(`[OfflineFirst] Offline, skipping sync for ${this.storeName}`);
      return;
    }

    this.syncInProgress = true;
    
    try {
      console.log(`[OfflineFirst] Starting sync for ${this.storeName}`);
      
      // First, pull changes from server
      await this.pullFromServer();
      
      // Then, push local changes to server
      await this.pushToServer();
      
      console.log(`[OfflineFirst] Sync completed for ${this.storeName}`);
      this.notifySubscribers('sync', { success: true });
      
    } catch (error) {
      console.error(`[OfflineFirst] Sync failed for ${this.storeName}:`, error);
      this.notifySubscribers('sync', { success: false, error });
      throw error;
    } finally {
      this.syncInProgress = false;
    }
  }

  /**
   * Pull changes from server
   */
  async pullFromServer() {
    try {
      const lastSync = await indexedDBManager.getSetting(`${this.storeName}_last_sync`, 0);
      const url = `${this.options.syncEndpoint}?since=${lastSync}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': await this.getAuthToken(),
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
      }

      const serverData = await response.json();
      
      if (serverData.items && serverData.items.length > 0) {
        console.log(`[OfflineFirst] Received ${serverData.items.length} updates from server`);
        
        for (const serverItem of serverData.items) {
          await this.mergeServerItem(serverItem);
        }
      }
      
      // Update last sync timestamp
      await indexedDBManager.setSetting(`${this.storeName}_last_sync`, Date.now());
      
    } catch (error) {
      console.error(`[OfflineFirst] Error pulling from server:`, error);
      throw error;
    }
  }

  /**
   * Push local changes to server
   */
  async pushToServer() {
    try {
      const pendingItems = await this.getPendingSync();
      
      if (pendingItems.length === 0) {
        console.log(`[OfflineFirst] No pending items to sync for ${this.storeName}`);
        return;
      }

      console.log(`[OfflineFirst] Pushing ${pendingItems.length} items to server`);
      
      // Process in batches
      for (let i = 0; i < pendingItems.length; i += this.options.syncBatchSize) {
        const batch = pendingItems.slice(i, i + this.options.syncBatchSize);
        await this.syncBatch(batch);
      }
      
    } catch (error) {
      console.error(`[OfflineFirst] Error pushing to server:`, error);
      throw error;
    }
  }

  /**
   * Sync a batch of items
   */
  async syncBatch(batch) {
    const operations = {
      create: [],
      update: [],
      delete: []
    };

    // Group by operation type
    for (const item of batch) {
      const operation = item._operation || 'update';
      operations[operation].push(item);
    }

    // Process each operation type
    for (const [operation, items] of Object.entries(operations)) {
      if (items.length === 0) continue;
      
      try {
        await this.syncOperation(operation, items);
      } catch (error) {
        console.error(`[OfflineFirst] Error syncing ${operation} operation:`, error);
        // Continue with other operations
      }
    }
  }

  /**
   * Sync a specific operation
   */
  async syncOperation(operation, items) {
    const endpoint = this.getOperationEndpoint(operation);
    const method = this.getOperationMethod(operation);
    
    for (const item of items) {
      try {
        const url = operation === 'delete' ? 
          `${endpoint}/${item[this.options.idField]}` : 
          endpoint;
          
        const body = operation === 'delete' ? 
          undefined : 
          JSON.stringify(this.prepareForServer(item));

        const response = await fetch(url, {
          method,
          headers: {
            'Authorization': await this.getAuthToken(),
            'Content-Type': 'application/json'
          },
          body
        });

        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();
        
        // Update local item with server response
        if (operation !== 'delete') {
          await this.updateAfterSync(item, result);
        } else {
          await indexedDBManager.delete(this.storeName, item[this.options.idField]);
        }
        
        // Remove from sync queue
        await this.removeSyncItem(item);
        
        console.log(`[OfflineFirst] Successfully synced ${operation} for ${item[this.options.idField]}`);
        
      } catch (error) {
        console.error(`[OfflineFirst] Error syncing item ${item[this.options.idField]}:`, error);
        
        // Increment retry count
        await this.incrementRetryCount(item);
      }
    }
  }

  /**
   * Merge server item with local data
   */
  async mergeServerItem(serverItem) {
    const localItem = await this.get(serverItem[this.options.idField]);
    
    if (!localItem) {
      // New item from server
      await indexedDBManager.put(this.storeName, this.transformServerItem(serverItem));
      this.notifySubscribers('create', serverItem);
      return;
    }

    // Check for conflicts
    const conflict = this.detectConflict(localItem, serverItem);
    
    if (conflict) {
      const resolved = await this.resolveConflict(localItem, serverItem);
      await indexedDBManager.put(this.storeName, resolved);
      this.notifySubscribers('update', resolved);
    } else if (serverItem[this.options.timestampField] > localItem[this.options.timestampField]) {
      // Server is newer, update local
      await indexedDBManager.put(this.storeName, this.transformServerItem(serverItem));
      this.notifySubscribers('update', serverItem);
    }
  }

  /**
   * Detect conflicts between local and server items
   */
  detectConflict(localItem, serverItem) {
    // If local item has pending changes and server item is newer
    return localItem._syncStatus === 'pending' && 
           serverItem[this.options.timestampField] > localItem._originalTimestamp;
  }

  /**
   * Resolve conflicts based on strategy
   */
  async resolveConflict(localItem, serverItem) {
    switch (this.options.conflictResolution) {
      case 'server-wins':
        return this.transformServerItem(serverItem);
        
      case 'client-wins':
        return localItem;
        
      case 'merge':
        return this.mergeItems(localItem, serverItem);
        
      case 'manual':
        return await this.handleManualConflict(localItem, serverItem);
        
      default:
        return this.transformServerItem(serverItem);
    }
  }

  /**
   * Merge two items
   */
  mergeItems(localItem, serverItem) {
    // Simple merge strategy - could be more sophisticated
    return {
      ...serverItem,
      ...localItem,
      [this.options.timestampField]: Math.max(
        localItem[this.options.timestampField] || 0,
        serverItem[this.options.timestampField] || 0
      )
    };
  }

  /**
   * Handle manual conflict resolution
   */
  async handleManualConflict(localItem, serverItem) {
    // Emit conflict event for manual resolution
    this.notifySubscribers('conflict', { local: localItem, server: serverItem });
    
    // For now, default to server wins
    return this.transformServerItem(serverItem);
  }

  /**
   * Prepare item for storage
   */
  prepareItem(data, operation = 'update') {
    const now = Date.now();
    
    return {
      ...data,
      [this.options.timestampField]: now,
      _lastModified: now,
      _syncStatus: 'pending',
      _operation: operation,
      _originalTimestamp: data[this.options.timestampField] || now
    };
  }

  /**
   * Transform item for client use (remove internal fields)
   */
  transformItem(item) {
    if (!item) return null;
    
    const { _lastModified, _syncStatus, _operation, _originalTimestamp, _deleted, ...cleanItem } = item;
    
    // Don't return deleted items
    if (_deleted) return null;
    
    return cleanItem;
  }

  /**
   * Transform items array
   */
  transformItems(items) {
    return items
      .map(item => this.transformItem(item))
      .filter(item => item !== null);
  }

  /**
   * Transform server item for local storage
   */
  transformServerItem(serverItem) {
    return {
      ...serverItem,
      _lastModified: Date.now(),
      _syncStatus: 'synced',
      _originalTimestamp: serverItem[this.options.timestampField]
    };
  }

  /**
   * Prepare item for server
   */
  prepareForServer(item) {
    const { _lastModified, _syncStatus, _operation, _originalTimestamp, ...serverItem } = item;
    return serverItem;
  }

  /**
   * Queue item for sync
   */
  async queueSync(operation, item) {
    await indexedDBManager.addToSyncQueue(
      operation,
      this.storeName,
      item,
      { priority: this.getSyncPriority(operation) }
    );
  }

  /**
   * Get items pending sync
   */
  async getPendingSync() {
    const syncQueue = await indexedDBManager.getSyncQueue({ store: this.storeName });
    return syncQueue.map(item => item.data);
  }

  /**
   * Remove item from sync queue
   */
  async removeSyncItem(item) {
    const syncQueue = await indexedDBManager.getSyncQueue({ store: this.storeName });
    const queueItem = syncQueue.find(q => 
      q.data[this.options.idField] === item[this.options.idField]
    );
    
    if (queueItem) {
      await indexedDBManager.removeSyncItem(queueItem.id);
    }
  }

  /**
   * Update item after successful sync
   */
  async updateAfterSync(localItem, serverResult) {
    const updated = {
      ...localItem,
      ...serverResult,
      _syncStatus: 'synced',
      _lastModified: Date.now()
    };
    
    delete updated._operation;
    delete updated._originalTimestamp;
    
    await indexedDBManager.put(this.storeName, updated);
  }

  /**
   * Increment retry count for failed sync
   */
  async incrementRetryCount(item) {
    await indexedDBManager.updateSyncItemRetry(item[this.options.idField]);
  }

  /**
   * Get operation endpoint
   */
  getOperationEndpoint(operation) {
    return this.options.syncEndpoint;
  }

  /**
   * Get HTTP method for operation
   */
  getOperationMethod(operation) {
    switch (operation) {
      case 'create': return 'POST';
      case 'update': return 'PUT';
      case 'delete': return 'DELETE';
      default: return 'PUT';
    }
  }

  /**
   * Get sync priority for operation
   */
  getSyncPriority(operation) {
    switch (operation) {
      case 'delete': return 'high';
      case 'create': return 'normal';
      case 'update': return 'normal';
      default: return 'low';
    }
  }

  /**
   * Get auth token for API requests
   */
  async getAuthToken() {
    const token = localStorage.getItem('authToken');
    return token ? `Bearer ${token}` : '';
  }

  /**
   * Schedule sync
   */
  scheduleSync() {
    if (this.syncTimeout) {
      clearTimeout(this.syncTimeout);
    }
    
    this.syncTimeout = setTimeout(() => {
      this.sync().catch(error => {
        console.error(`[OfflineFirst] Scheduled sync failed:`, error);
      });
    }, 1000); // Wait 1 second before syncing
  }

  /**
   * Subscribe to store changes
   */
  subscribe(callback) {
    this.subscribers.add(callback);
    
    return () => {
      this.subscribers.delete(callback);
    };
  }

  /**
   * Notify subscribers of changes
   */
  notifySubscribers(operation, data) {
    this.subscribers.forEach(callback => {
      try {
        callback({ operation, data, store: this.storeName });
      } catch (error) {
        console.error('[OfflineFirst] Subscriber error:', error);
      }
    });
  }

  /**
   * Get store statistics
   */
  async getStats() {
    const total = await indexedDBManager.count(this.storeName);
    const pending = await this.getPendingSync();
    
    return {
      total,
      pending: pending.length,
      synced: total - pending.length,
      lastSync: await indexedDBManager.getSetting(`${this.storeName}_last_sync`, null)
    };
  }

  /**
   * Clear all data
   */
  async clear() {
    await indexedDBManager.clear(this.storeName);
    this.notifySubscribers('clear', {});
  }

  /**
   * Export data
   */
  async export() {
    const items = await indexedDBManager.getAll(this.storeName);
    return {
      storeName: this.storeName,
      items,
      timestamp: Date.now()
    };
  }

  /**
   * Import data
   */
  async import(data, options = {}) {
    const { overwrite = false } = options;
    
    if (overwrite) {
      await this.clear();
    }
    
    for (const item of data.items || []) {
      try {
        await indexedDBManager.put(this.storeName, item);
      } catch (error) {
        console.error(`[OfflineFirst] Error importing item:`, error);
      }
    }
    
    this.notifySubscribers('import', { count: data.items?.length || 0 });
  }
}

/**
 * Offline-First Manager
 * Manages multiple stores with unified interface
 */
export class OfflineFirstManager {
  constructor() {
    this.stores = new Map();
    this.globalSubscribers = new Set();
  }

  /**
   * Register a store
   */
  registerStore(name, options = {}) {
    const store = new OfflineFirstStore(name, options);
    this.stores.set(name, store);
    
    // Subscribe to store changes for global notifications
    store.subscribe((event) => {
      this.notifyGlobalSubscribers({ ...event, store: name });
    });
    
    return store;
  }

  /**
   * Get a store
   */
  getStore(name) {
    return this.stores.get(name);
  }

  /**
   * Initialize all stores
   */
  async init() {
    const initPromises = Array.from(this.stores.values()).map(store => store.init());
    await Promise.all(initPromises);
  }

  /**
   * Sync all stores
   */
  async syncAll() {
    const syncPromises = Array.from(this.stores.values()).map(store => store.sync());
    const results = await Promise.allSettled(syncPromises);
    
    const failed = results.filter(result => result.status === 'rejected');
    if (failed.length > 0) {
      console.error(`[OfflineFirst] ${failed.length} stores failed to sync`);
    }
    
    return results;
  }

  /**
   * Get statistics for all stores
   */
  async getAllStats() {
    const stats = {};
    
    for (const [name, store] of this.stores) {
      try {
        stats[name] = await store.getStats();
      } catch (error) {
        stats[name] = { error: error.message };
      }
    }
    
    return stats;
  }

  /**
   * Subscribe to global changes
   */
  subscribe(callback) {
    this.globalSubscribers.add(callback);
    
    return () => {
      this.globalSubscribers.delete(callback);
    };
  }

  /**
   * Notify global subscribers
   */
  notifyGlobalSubscribers(event) {
    this.globalSubscribers.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('[OfflineFirst] Global subscriber error:', error);
      }
    });
  }

  /**
   * Clear all stores
   */
  async clearAll() {
    const clearPromises = Array.from(this.stores.values()).map(store => store.clear());
    await Promise.all(clearPromises);
  }

  /**
   * Export all data
   */
  async exportAll() {
    const exports = {};
    
    for (const [name, store] of this.stores) {
      try {
        exports[name] = await store.export();
      } catch (error) {
        exports[name] = { error: error.message };
      }
    }
    
    return {
      timestamp: Date.now(),
      stores: exports
    };
  }

  /**
   * Import all data
   */
  async importAll(data, options = {}) {
    const results = {};
    
    for (const [name, storeData] of Object.entries(data.stores || {})) {
      const store = this.getStore(name);
      if (store) {
        try {
          await store.import(storeData, options);
          results[name] = { success: true };
        } catch (error) {
          results[name] = { success: false, error: error.message };
        }
      }
    }
    
    return results;
  }
}

// Create and export default manager instance
export const offlineFirstManager = new OfflineFirstManager();

// Helper hook for React components
export function useOfflineFirst(storeName, options = {}) {
  const [store, setStore] = React.useState(null);
  const [data, setData] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [syncing, setSyncing] = React.useState(false);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    let mounted = true;
    let unsubscribe;

    async function initStore() {
      try {
        let storeInstance = offlineFirstManager.getStore(storeName);
        
        if (!storeInstance) {
          storeInstance = offlineFirstManager.registerStore(storeName, options);
          await storeInstance.init();
        }
        
        if (!mounted) return;

        setStore(storeInstance);
        
        // Load initial data
        const items = await storeInstance.getAll();
        if (mounted) {
          setData(items);
          setLoading(false);
        }
        
        // Subscribe to changes
        unsubscribe = storeInstance.subscribe((event) => {
          if (!mounted) return;
          
          if (event.operation === 'sync') {
            setSyncing(false);
            if (!event.data.success) {
              setError(event.data.error);
            }
          } else {
            // Reload data on changes
            storeInstance.getAll().then(items => {
              if (mounted) setData(items);
            });
          }
        });
        
      } catch (err) {
        if (mounted) {
          setError(err);
          setLoading(false);
        }
      }
    }

    initStore();

    return () => {
      mounted = false;
      if (unsubscribe) unsubscribe();
    };
  }, [storeName]);

  const create = React.useCallback(async (data) => {
    if (!store) throw new Error('Store not initialized');
    setSyncing(true);
    setError(null);
    return store.create(data);
  }, [store]);

  const update = React.useCallback(async (id, data) => {
    if (!store) throw new Error('Store not initialized');
    setSyncing(true);
    setError(null);
    return store.update(id, data);
  }, [store]);

  const remove = React.useCallback(async (id) => {
    if (!store) throw new Error('Store not initialized');
    setSyncing(true);
    setError(null);
    return store.delete(id);
  }, [store]);

  const sync = React.useCallback(async () => {
    if (!store) throw new Error('Store not initialized');
    setSyncing(true);
    setError(null);
    return store.sync();
  }, [store]);

  return {
    data,
    loading,
    syncing,
    error,
    create,
    update,
    remove,
    sync,
    store
  };
}

export default OfflineFirstManager;