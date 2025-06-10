// TODO: i18n - processed
import React from 'react';
/**
 * Advanced caching utilities for API responses and data
 */
// Cache storage types
import { useTranslation } from "react-i18next";export const CacheType = {
  MEMORY: 'memory',
  LOCAL_STORAGE: 'localStorage',
  SESSION_STORAGE: 'sessionStorage',
  INDEXED_DB: 'indexedDB'
};
// Cache strategies
export const CacheStrategy = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  CACHE_ONLY: 'cache-only',
  NETWORK_ONLY: 'network-only',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};
/**
 * Memory cache implementation
 */
class MemoryCache {
  constructor(maxSize = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    if (this.isExpired(item)) {
      this.cache.delete(key);
      return null;
    }
    // Move to end (LRU)
    this.cache.delete(key);
    this.cache.set(key, item);
    return item.value;
  }
  set(key, value, ttl) {
    // Remove oldest if at capacity
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl
    });
  }
  delete(key) {
    return this.cache.delete(key);
  }
  clear() {
    this.cache.clear();
  }
  isExpired(item) {
    if (!item.ttl) return false;
    return Date.now() - item.timestamp > item.ttl;
  }
}
/**
 * Storage cache implementation (localStorage/sessionStorage)
 */
class StorageCache {
  constructor(storage, prefix = 'cache_') {
    this.storage = storage;
    this.prefix = prefix;
  }
  get(key) {
    try {
      const item = this.storage.getItem(this.prefix + key);
      if (!item) return null;
      const parsed = JSON.parse(item);
      if (this.isExpired(parsed)) {
        this.storage.removeItem(this.prefix + key);
        return null;
      }
      return parsed.value;
    } catch (error) {
      console.error('Cache get error:', error);
      return null;
    }
  }
  set(key, value, ttl) {
    const item = {
      value,
      timestamp: Date.now(),
      ttl
    };
    try {
      this.storage.setItem(this.prefix + key, JSON.stringify(item));
    } catch (error) {
      console.error('Cache set error:', error);
      // Handle quota exceeded
      if (error.name === 'QuotaExceededError') {
        this.clearExpired();
        // Retry once
        try {
          this.storage.setItem(this.prefix + key, JSON.stringify(item));
        } catch (retryError) {
          console.error('Cache set retry failed:', retryError);
        }
      }
    }
  }
  delete(key) {
    this.storage.removeItem(this.prefix + key);
  }
  clear() {
    const keys = Object.keys(this.storage);
    keys.forEach((key) => {
      if (key.startsWith(this.prefix)) {
        this.storage.removeItem(key);
      }
    });
  }
  clearExpired() {
    const keys = Object.keys(this.storage);
    keys.forEach((key) => {
      if (key.startsWith(this.prefix)) {
        try {
          const item = JSON.parse(this.storage.getItem(key));
          if (this.isExpired(item)) {
            this.storage.removeItem(key);
          }
        } catch (error) {
          // Invalid item, remove it
          this.storage.removeItem(key);
        }
      }
    });
  }
  isExpired(item) {
    if (!item.ttl) return false;
    return Date.now() - item.timestamp > item.ttl;
  }
}
/**
 * IndexedDB cache implementation
 */
class IndexedDBCache {
  constructor(dbName = 'AppCache', storeName = 'cache') {
    this.dbName = dbName;
    this.storeName = storeName;
    this.db = null;
    this.initPromise = this.init();
  }
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: 'key' });
        }
      };
    });
  }
  async get(key) {
    await this.initPromise;
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const request = store.get(key);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const item = request.result;
        if (!item) {
          resolve(null);
          return;
        }
        if (this.isExpired(item)) {
          this.delete(key);
          resolve(null);
          return;
        }
        resolve(item.value);
      };
    });
  }
  async set(key, value, ttl) {
    await this.initPromise;
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.put({
        key,
        value,
        timestamp: Date.now(),
        ttl
      });
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
  async delete(key) {
    await this.initPromise;
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.delete(key);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
  async clear() {
    await this.initPromise;
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const request = store.clear();
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
  isExpired(item) {
    if (!item.ttl) return false;
    return Date.now() - item.timestamp > item.ttl;
  }
}
/**
 * Unified cache manager
 */
export class CacheManager {
  constructor(options = {}) {
    const {
      type = CacheType.MEMORY,
      prefix = 'app_cache_',
      maxSize = 100,
      defaultTTL = 5 * 60 * 1000 // 5 minutes
    } = options;
    this.defaultTTL = defaultTTL;
    switch (type) {
      case CacheType.MEMORY:
        this.cache = new MemoryCache(maxSize);
        break;
      case CacheType.LOCAL_STORAGE:
        this.cache = new StorageCache(localStorage, prefix);
        break;
      case CacheType.SESSION_STORAGE:
        this.cache = new StorageCache(sessionStorage, prefix);
        break;
      case CacheType.INDEXED_DB:
        this.cache = new IndexedDBCache();
        break;
      default:
        this.cache = new MemoryCache(maxSize);
    }
  }
  async get(key, options = {}) {
    const {
      fallback = null,
      deserialize = JSON.parse
    } = options;
    try {
      const value = await this.cache.get(key);
      if (value === null) return fallback;
      return typeof value === 'string' && deserialize ? deserialize(value) : value;
    } catch (error) {
      console.error('Cache get error:', error);
      return fallback;
    }
  }
  async set(key, value, options = {}) {
    const {
      ttl = this.defaultTTL,
      serialize = JSON.stringify
    } = options;
    try {
      const serialized = serialize ? serialize(value) : value;
      await this.cache.set(key, serialized, ttl);
    } catch (error) {
      console.error('Cache set error:', error);
    }
  }
  async delete(key) {
    try {
      await this.cache.delete(key);
    } catch (error) {
      console.error('Cache delete error:', error);
    }
  }
  async clear() {
    try {
      await this.cache.clear();
    } catch (error) {
      console.error('Cache clear error:', error);
    }
  }
  // Cached function wrapper
  async cached(key, factory, options = {}) {
    const cached = await this.get(key);
    if (cached !== null) {
      return cached;
    }
    const value = await factory();
    await this.set(key, value, options);
    return value;
  }
  // Stale-while-revalidate implementation
  async staleWhileRevalidate(key, factory, options = {}) {
    const cached = await this.get(key);
    // Return stale data immediately
    if (cached !== null) {
      // Revalidate in background
      factory().then((value) => {
        this.set(key, value, options);
      }).catch((error) => {
        console.error('Revalidation error:', error);
      });
      return cached;
    }
    // No cache, fetch fresh
    const value = await factory();
    await this.set(key, value, options);
    return value;
  }
}
/**
 * React hook for caching
 */
export function useCache(cacheType = CacheType.MEMORY, options = {}) {
  const [cache] = React.useState(() => new CacheManager({ type: cacheType, ...options }));
  return cache;
}
// Export instances for common use cases
export const memoryCache = new CacheManager({ type: CacheType.MEMORY });
export const localCache = new CacheManager({ type: CacheType.LOCAL_STORAGE });
export const sessionCache = new CacheManager({ type: CacheType.SESSION_STORAGE });