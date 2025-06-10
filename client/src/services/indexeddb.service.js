/**
 * Advanced IndexedDB Manager for PWA Offline Data Storage
 * Provides comprehensive data management, synchronization, and offline-first capabilities
 */

class IndexedDBManager {
  constructor() {
    this.dbName = 'BDC_PWA_Database';
    this.version = 3;
    this.db = null;
    this.isInitialized = false;
    this.syncQueue = new Map();
    this.observers = new Map();
    this.compressionEnabled = true;
    
    // Store schemas for different object stores
    this.storeSchemas = {
      beneficiaries: {
        keyPath: 'id',
        autoIncrement: false,
        indexes: [
          { name: 'status', keyPath: 'status', unique: false },
          { name: 'lastModified', keyPath: 'lastModified', unique: false },
          { name: 'syncStatus', keyPath: 'syncStatus', unique: false }
        ]
      },
      evaluations: {
        keyPath: 'id',
        autoIncrement: false,
        indexes: [
          { name: 'beneficiaryId', keyPath: 'beneficiaryId', unique: false },
          { name: 'status', keyPath: 'status', unique: false },
          { name: 'createdAt', keyPath: 'createdAt', unique: false },
          { name: 'syncStatus', keyPath: 'syncStatus', unique: false }
        ]
      },
      documents: {
        keyPath: 'id',
        autoIncrement: false,
        indexes: [
          { name: 'type', keyPath: 'type', unique: false },
          { name: 'category', keyPath: 'category', unique: false },
          { name: 'uploadedAt', keyPath: 'uploadedAt', unique: false },
          { name: 'syncStatus', keyPath: 'syncStatus', unique: false }
        ]
      },
      calendar: {
        keyPath: 'id',
        autoIncrement: false,
        indexes: [
          { name: 'date', keyPath: 'date', unique: false },
          { name: 'type', keyPath: 'type', unique: false },
          { name: 'participantId', keyPath: 'participantId', unique: false },
          { name: 'syncStatus', keyPath: 'syncStatus', unique: false }
        ]
      },
      syncQueue: {
        keyPath: 'id',
        autoIncrement: true,
        indexes: [
          { name: 'operation', keyPath: 'operation', unique: false },
          { name: 'store', keyPath: 'store', unique: false },
          { name: 'timestamp', keyPath: 'timestamp', unique: false },
          { name: 'priority', keyPath: 'priority', unique: false },
          { name: 'retryCount', keyPath: 'retryCount', unique: false }
        ]
      },
      settings: {
        keyPath: 'key',
        autoIncrement: false,
        indexes: [
          { name: 'category', keyPath: 'category', unique: false },
          { name: 'lastModified', keyPath: 'lastModified', unique: false }
        ]
      },
      cache: {
        keyPath: 'url',
        autoIncrement: false,
        indexes: [
          { name: 'timestamp', keyPath: 'timestamp', unique: false },
          { name: 'type', keyPath: 'type', unique: false },
          { name: 'size', keyPath: 'size', unique: false },
          { name: 'expiry', keyPath: 'expiry', unique: false }
        ]
      },
      performance: {
        keyPath: 'id',
        autoIncrement: true,
        indexes: [
          { name: 'metric', keyPath: 'metric', unique: false },
          { name: 'timestamp', keyPath: 'timestamp', unique: false },
          { name: 'category', keyPath: 'category', unique: false }
        ]
      }
    };
  }

  /**
   * Initialize the IndexedDB database
   */
  async init() {
    if (this.isInitialized) {
      return this.db;
    }

    try {
      this.db = await this.openDatabase();
      this.isInitialized = true;
      await this.setupPeriodicCleanup();
      console.log('[IndexedDB] Database initialized successfully');
      return this.db;
    } catch (error) {
      console.error('[IndexedDB] Failed to initialize:', error);
      throw error;
    }
  }

  /**
   * Open the IndexedDB database with proper schema setup
   */
  openDatabase() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.version);

      request.onerror = () => {
        reject(new Error(`Failed to open database: ${request.error?.message}`));
      };

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        const transaction = event.target.transaction;

        // Create object stores based on schemas
        Object.entries(this.storeSchemas).forEach(([storeName, schema]) => {
          try {
            let store;
            
            if (db.objectStoreNames.contains(storeName)) {
              store = transaction.objectStore(storeName);
            } else {
              store = db.createObjectStore(storeName, {
                keyPath: schema.keyPath,
                autoIncrement: schema.autoIncrement
              });
            }

            // Create indexes
            schema.indexes.forEach(index => {
              if (!store.indexNames.contains(index.name)) {
                store.createIndex(index.name, index.keyPath, { unique: index.unique });
              }
            });

            console.log(`[IndexedDB] Object store '${storeName}' configured`);
          } catch (error) {
            console.error(`[IndexedDB] Error configuring store '${storeName}':`, error);
          }
        });
      };

      request.onblocked = () => {
        console.warn('[IndexedDB] Database upgrade blocked. Close other tabs.');
      };
    });
  }

  /**
   * Generic method to add data to any store
   */
  async add(storeName, data, options = {}) {
    await this.ensureInitialized();

    const enrichedData = this.enrichData(data, options);
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.add(enrichedData);

      request.onsuccess = () => {
        this.notifyObservers(storeName, 'add', enrichedData);
        resolve(request.result);
      };

      request.onerror = () => {
        reject(new Error(`Failed to add to ${storeName}: ${request.error?.message}`));
      };
    });
  }

  /**
   * Generic method to update data in any store
   */
  async put(storeName, data, options = {}) {
    await this.ensureInitialized();

    const enrichedData = this.enrichData(data, options);
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(enrichedData);

      request.onsuccess = () => {
        this.notifyObservers(storeName, 'put', enrichedData);
        resolve(request.result);
      };

      request.onerror = () => {
        reject(new Error(`Failed to update ${storeName}: ${request.error?.message}`));
      };
    });
  }

  /**
   * Generic method to get data from any store
   */
  async get(storeName, key) {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onsuccess = () => {
        const data = request.result;
        resolve(data ? this.deenrichData(data) : null);
      };

      request.onerror = () => {
        reject(new Error(`Failed to get from ${storeName}: ${request.error?.message}`));
      };
    });
  }

  /**
   * Get all records from a store with optional filtering
   */
  async getAll(storeName, options = {}) {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      
      let request;
      
      if (options.index && options.value) {
        const index = store.index(options.index);
        request = options.range ? 
          index.getAll(options.range) : 
          index.getAll(options.value);
      } else {
        request = store.getAll();
      }

      request.onsuccess = () => {
        let results = request.result.map(item => this.deenrichData(item));
        
        // Apply filters
        if (options.filter) {
          results = results.filter(options.filter);
        }
        
        // Apply sorting
        if (options.sort) {
          results.sort(options.sort);
        }
        
        // Apply pagination
        if (options.limit) {
          const start = options.offset || 0;
          results = results.slice(start, start + options.limit);
        }
        
        resolve(results);
      };

      request.onerror = () => {
        reject(new Error(`Failed to get all from ${storeName}: ${request.error?.message}`));
      };
    });
  }

  /**
   * Delete a record from a store
   */
  async delete(storeName, key) {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onsuccess = () => {
        this.notifyObservers(storeName, 'delete', { key });
        resolve(true);
      };

      request.onerror = () => {
        reject(new Error(`Failed to delete from ${storeName}: ${request.error?.message}`));
      };
    });
  }

  /**
   * Clear all records from a store
   */
  async clear(storeName) {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();

      request.onsuccess = () => {
        this.notifyObservers(storeName, 'clear', {});
        resolve(true);
      };

      request.onerror = () => {
        reject(new Error(`Failed to clear ${storeName}: ${request.error?.message}`));
      };
    });
  }

  /**
   * Count records in a store
   */
  async count(storeName, query = null) {
    await this.ensureInitialized();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = query ? store.count(query) : store.count();

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        reject(new Error(`Failed to count ${storeName}: ${request.error?.message}`));
      };
    });
  }

  /**
   * Advanced query with multiple conditions
   */
  async query(storeName, conditions = {}) {
    await this.ensureInitialized();

    const results = await this.getAll(storeName);
    
    return results.filter(item => {
      return Object.entries(conditions).every(([key, value]) => {
        if (typeof value === 'function') {
          return value(item[key]);
        }
        return item[key] === value;
      });
    });
  }

  /**
   * Batch operations for better performance
   */
  async batch(operations) {
    await this.ensureInitialized();

    const stores = [...new Set(operations.map(op => op.store))];
    
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(stores, 'readwrite');
      const results = [];
      let completed = 0;

      transaction.oncomplete = () => {
        resolve(results);
      };

      transaction.onerror = () => {
        reject(new Error(`Batch operation failed: ${transaction.error?.message}`));
      };

      operations.forEach((operation, index) => {
        const store = transaction.objectStore(operation.store);
        let request;

        switch (operation.type) {
          case 'add':
            request = store.add(this.enrichData(operation.data));
            break;
          case 'put':
            request = store.put(this.enrichData(operation.data));
            break;
          case 'delete':
            request = store.delete(operation.key);
            break;
          default:
            throw new Error(`Unknown operation type: ${operation.type}`);
        }

        request.onsuccess = () => {
          results[index] = request.result;
          completed++;
        };

        request.onerror = () => {
          results[index] = { error: request.error?.message };
          completed++;
        };
      });
    });
  }

  /**
   * Sync queue management
   */
  async addToSyncQueue(operation, store, data, options = {}) {
    const syncItem = {
      operation,
      store,
      data,
      timestamp: Date.now(),
      priority: options.priority || 'normal',
      retryCount: 0,
      maxRetries: options.maxRetries || 3,
      metadata: options.metadata || {}
    };

    await this.add('syncQueue', syncItem);
    return syncItem;
  }

  async getSyncQueue(filters = {}) {
    const options = {
      sort: (a, b) => {
        // Priority: high > normal > low
        const priorityOrder = { high: 3, normal: 2, low: 1 };
        const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
        
        if (priorityDiff !== 0) return priorityDiff;
        
        // Then by timestamp (older first)
        return a.timestamp - b.timestamp;
      }
    };

    if (filters.store) {
      options.filter = item => item.store === filters.store;
    }

    return this.getAll('syncQueue', options);
  }

  async removeSyncItem(id) {
    return this.delete('syncQueue', id);
  }

  async updateSyncItemRetry(id) {
    const item = await this.get('syncQueue', id);
    if (item) {
      item.retryCount++;
      item.lastRetry = Date.now();
      await this.put('syncQueue', item);
    }
    return item;
  }

  /**
   * Data enrichment and compression
   */
  enrichData(data, options = {}) {
    const enriched = {
      ...data,
      _lastModified: Date.now(),
      _syncStatus: options.syncStatus || 'pending',
      _version: options.version || 1
    };

    if (this.compressionEnabled && options.compress) {
      enriched._compressed = true;
      enriched._originalSize = JSON.stringify(data).length;
      // Note: In a real implementation, you'd use a compression library
      enriched.data = data; // Placeholder for compressed data
    }

    return enriched;
  }

  deenrichData(data) {
    if (!data) return data;

    const { _lastModified, _syncStatus, _version, _compressed, _originalSize, ...cleanData } = data;
    
    if (_compressed) {
      // Note: In a real implementation, you'd decompress here
      return cleanData.data;
    }
    
    return cleanData;
  }

  /**
   * Performance monitoring
   */
  async recordPerformanceMetric(metric, value, category = 'general') {
    const perfData = {
      metric,
      value,
      category,
      timestamp: Date.now(),
      userAgent: navigator.userAgent,
      metadata: {
        url: window.location.href,
        connectionType: navigator.connection?.effectiveType || 'unknown'
      }
    };

    await this.add('performance', perfData);
  }

  async getPerformanceMetrics(metric = null, timeRange = 24 * 60 * 60 * 1000) {
    const cutoff = Date.now() - timeRange;
    
    const options = {
      filter: item => item.timestamp > cutoff,
      sort: (a, b) => b.timestamp - a.timestamp
    };

    if (metric) {
      options.filter = item => item.timestamp > cutoff && item.metric === metric;
    }

    return this.getAll('performance', options);
  }

  /**
   * Cache management
   */
  async cacheResponse(url, response, type = 'api', ttl = 24 * 60 * 60 * 1000) {
    const cacheData = {
      url,
      response: await response.clone().text(),
      type,
      timestamp: Date.now(),
      expiry: Date.now() + ttl,
      size: response.headers.get('content-length') || 0,
      headers: Object.fromEntries(response.headers.entries())
    };

    await this.put('cache', cacheData);
    return cacheData;
  }

  async getCachedResponse(url) {
    const cached = await this.get('cache', url);
    
    if (!cached) return null;
    
    if (cached.expiry < Date.now()) {
      await this.delete('cache', url);
      return null;
    }

    return new Response(cached.response, {
      status: 200,
      headers: cached.headers
    });
  }

  async clearExpiredCache() {
    const expired = await this.query('cache', {
      expiry: (expiry) => expiry < Date.now()
    });

    const deletePromises = expired.map(item => this.delete('cache', item.url));
    await Promise.all(deletePromises);
    
    return expired.length;
  }

  /**
   * Settings management
   */
  async getSetting(key, defaultValue = null) {
    const setting = await this.get('settings', key);
    return setting ? setting.value : defaultValue;
  }

  async setSetting(key, value, category = 'general') {
    const setting = {
      key,
      value,
      category,
      lastModified: Date.now()
    };

    await this.put('settings', setting);
    return setting;
  }

  /**
   * Observer pattern for real-time updates
   */
  observe(storeName, callback) {
    if (!this.observers.has(storeName)) {
      this.observers.set(storeName, new Set());
    }
    
    this.observers.get(storeName).add(callback);
    
    // Return unsubscribe function
    return () => {
      this.observers.get(storeName)?.delete(callback);
    };
  }

  notifyObservers(storeName, operation, data) {
    const storeObservers = this.observers.get(storeName);
    if (storeObservers) {
      storeObservers.forEach(callback => {
        try {
          callback({ operation, data, store: storeName });
        } catch (error) {
          console.error('[IndexedDB] Observer error:', error);
        }
      });
    }
  }

  /**
   * Database maintenance and cleanup
   */
  async setupPeriodicCleanup() {
    // Clean up every hour
    setInterval(async () => {
      try {
        await this.performMaintenance();
      } catch (error) {
        console.error('[IndexedDB] Maintenance error:', error);
      }
    }, 60 * 60 * 1000);
  }

  async performMaintenance() {
    console.log('[IndexedDB] Starting maintenance...');
    
    // Clear expired cache
    const expiredCount = await this.clearExpiredCache();
    
    // Clean old performance metrics (keep last 7 days)
    const weekAgo = Date.now() - (7 * 24 * 60 * 60 * 1000);
    const oldMetrics = await this.query('performance', {
      timestamp: (ts) => ts < weekAgo
    });
    
    for (const metric of oldMetrics) {
      await this.delete('performance', metric.id);
    }
    
    // Clean failed sync items (older than 24 hours with max retries)
    const dayAgo = Date.now() - (24 * 60 * 60 * 1000);
    const failedSyncs = await this.query('syncQueue', {
      timestamp: (ts) => ts < dayAgo,
      retryCount: (count) => count >= 3
    });
    
    for (const sync of failedSyncs) {
      await this.delete('syncQueue', sync.id);
    }
    
    console.log(`[IndexedDB] Maintenance completed: ${expiredCount} expired cache, ${oldMetrics.length} old metrics, ${failedSyncs.length} failed syncs cleaned`);
  }

  /**
   * Database statistics
   */
  async getStatistics() {
    const stats = {};
    
    for (const storeName of Object.keys(this.storeSchemas)) {
      try {
        stats[storeName] = await this.count(storeName);
      } catch (error) {
        stats[storeName] = 0;
      }
    }
    
    // Calculate total storage estimate
    if ('storage' in navigator && 'estimate' in navigator.storage) {
      try {
        const estimate = await navigator.storage.estimate();
        stats.storage = {
          used: estimate.usage,
          quota: estimate.quota,
          percentage: estimate.quota > 0 ? Math.round((estimate.usage / estimate.quota) * 100) : 0
        };
      } catch (error) {
        stats.storage = { error: error.message };
      }
    }
    
    return stats;
  }

  /**
   * Export and import functionality
   */
  async exportData(stores = null) {
    const storesToExport = stores || Object.keys(this.storeSchemas);
    const exported = {
      version: this.version,
      timestamp: Date.now(),
      data: {}
    };

    for (const storeName of storesToExport) {
      try {
        exported.data[storeName] = await this.getAll(storeName);
      } catch (error) {
        console.error(`Failed to export ${storeName}:`, error);
        exported.data[storeName] = [];
      }
    }

    return exported;
  }

  async importData(importedData, options = {}) {
    const { overwrite = false, stores = null } = options;
    const storesToImport = stores || Object.keys(importedData.data || {});
    const results = {};

    for (const storeName of storesToImport) {
      try {
        if (overwrite) {
          await this.clear(storeName);
        }

        const items = importedData.data[storeName] || [];
        const operations = items.map(item => ({
          type: 'put',
          store: storeName,
          data: item
        }));

        await this.batch(operations);
        results[storeName] = { success: true, count: items.length };
      } catch (error) {
        console.error(`Failed to import ${storeName}:`, error);
        results[storeName] = { success: false, error: error.message };
      }
    }

    return results;
  }

  /**
   * Utility methods
   */
  async ensureInitialized() {
    if (!this.isInitialized) {
      await this.init();
    }
  }

  async close() {
    if (this.db) {
      this.db.close();
      this.db = null;
      this.isInitialized = false;
    }
  }

  async deleteDatabase() {
    await this.close();
    
    return new Promise((resolve, reject) => {
      const deleteRequest = indexedDB.deleteDatabase(this.dbName);
      
      deleteRequest.onsuccess = () => resolve(true);
      deleteRequest.onerror = () => reject(deleteRequest.error);
      deleteRequest.onblocked = () => {
        console.warn('[IndexedDB] Delete blocked. Close other tabs.');
      };
    });
  }
}

// Export singleton instance
export const indexedDBManager = new IndexedDBManager();
export default indexedDBManager;