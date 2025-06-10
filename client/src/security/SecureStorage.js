// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Secure Storage Service
 * Provides encrypted local storage with security features
 */
class SecureStorage {
  constructor() {
    this.encryptionKey = null;
    this.initialized = false;
    this.storagePrefix = 'bdc_secure_';
    this.sessionTimeout = 30 * 60 * 1000; // 30 minutes
    this.maxRetries = 3;
    this.init();
  }
  /**
   * Initialize secure storage
   */
  async init() {
    try {
      // Generate or retrieve encryption key
      await this.initializeEncryption();
      // Setup session monitoring
      this.setupSessionMonitoring();
      // Cleanup expired items
      this.cleanupExpiredItems();
      this.initialized = true;
    } catch (error) {
      console.error('SecureStorage initialization failed:', error);
    }
  }
  /**
   * Initialize encryption for storage
   */
  async initializeEncryption() {
    // Check if Web Crypto API is available
    if (!window.crypto || !window.crypto.subtle) {
      console.warn('Web Crypto API not available, using base64 encoding instead');
      this.encryptionKey = 'fallback_key';
      return;
    }
    try {
      // Try to get existing key from session storage
      const existingKey = sessionStorage.getItem('sec_key');
      if (existingKey) {
        this.encryptionKey = await this.importKey(existingKey);
      } else {
        // Generate new encryption key
        this.encryptionKey = await window.crypto.subtle.generateKey(
          {
            name: 'AES-GCM',
            length: 256
          },
          true,
          ['encrypt', 'decrypt']
        );
        // Store key in session storage (only for current session)
        const exportedKey = await window.crypto.subtle.exportKey('raw', this.encryptionKey);
        const keyArray = Array.from(new Uint8Array(exportedKey));
        sessionStorage.setItem('sec_key', JSON.stringify(keyArray));
      }
    } catch (error) {
      console.error('Encryption initialization failed:', error);
      this.encryptionKey = 'fallback_key';
    }
  }
  /**
   * Import encryption key from stored data
   */
  async importKey(keyData) {
    try {
      const keyArray = new Uint8Array(JSON.parse(keyData));
      return await window.crypto.subtle.importKey(
        'raw',
        keyArray,
        {
          name: 'AES-GCM',
          length: 256
        },
        true,
        ['encrypt', 'decrypt']
      );
    } catch (error) {
      throw new Error('Failed to import encryption key');
    }
  }
  /**
   * Encrypt data using Web Crypto API
   */
  async encrypt(data) {
    if (!this.encryptionKey || this.encryptionKey === 'fallback_key') {
      // Fallback to base64 encoding
      return btoa(JSON.stringify(data));
    }
    try {
      const encoder = new TextEncoder();
      const encodedData = encoder.encode(JSON.stringify(data));
      const iv = window.crypto.getRandomValues(new Uint8Array(12));
      const encryptedData = await window.crypto.subtle.encrypt(
        {
          name: 'AES-GCM',
          iv: iv
        },
        this.encryptionKey,
        encodedData
      );
      // Combine IV and encrypted data
      const combined = new Uint8Array(iv.length + encryptedData.byteLength);
      combined.set(iv);
      combined.set(new Uint8Array(encryptedData), iv.length);
      // Convert to base64 for storage
      return btoa(String.fromCharCode(...combined));
    } catch (error) {
      console.error('Encryption failed:', error);
      // Fallback to base64 encoding
      return btoa(JSON.stringify(data));
    }
  }
  /**
   * Decrypt data using Web Crypto API
   */
  async decrypt(encryptedData) {
    if (!this.encryptionKey || this.encryptionKey === 'fallback_key') {
      // Fallback from base64 encoding
      try {
        return JSON.parse(atob(encryptedData));
      } catch (error) {
        throw new Error('Failed to decrypt data');
      }
    }
    try {
      // Convert from base64
      const combined = new Uint8Array(
        atob(encryptedData).
        split('').
        map((char) => char.charCodeAt(0))
      );
      // Extract IV and encrypted data
      const iv = combined.slice(0, 12);
      const encrypted = combined.slice(12);
      const decryptedData = await window.crypto.subtle.decrypt(
        {
          name: 'AES-GCM',
          iv: iv
        },
        this.encryptionKey,
        encrypted
      );
      const decoder = new TextDecoder();
      const decodedData = decoder.decode(decryptedData);
      return JSON.parse(decodedData);
    } catch (error) {
      console.error('Decryption failed:', error);
      // Try fallback decryption
      try {
        return JSON.parse(atob(encryptedData));
      } catch (fallbackError) {
        throw new Error('Failed to decrypt data');
      }
    }
  }
  /**
   * Store data securely
   */
  async setItem(key, value, options = {}) {
    if (!this.initialized) {
      await this.init();
    }
    const config = {
      encrypt: true,
      expiry: null,
      sensitive: false,
      ...options
    };
    try {
      const storageKey = this.storagePrefix + key;
      const storageData = {
        value: value,
        timestamp: Date.now(),
        expiry: config.expiry ? Date.now() + config.expiry : null,
        sensitive: config.sensitive,
        checksum: this.generateChecksum(value)
      };
      let dataToStore;
      if (config.encrypt) {
        dataToStore = await this.encrypt(storageData);
      } else {
        dataToStore = JSON.stringify(storageData);
      }
      // Choose storage type based on sensitivity
      const storage = config.sensitive ? sessionStorage : localStorage;
      storage.setItem(storageKey, dataToStore);
      return true;
    } catch (error) {
      console.error('SecureStorage setItem failed:', error);
      return false;
    }
  }
  /**
   * Retrieve data securely
   */
  async getItem(key, options = {}) {
    if (!this.initialized) {
      await this.init();
    }
    const config = {
      decrypt: true,
      checkIntegrity: true,
      ...options
    };
    try {
      const storageKey = this.storagePrefix + key;
      // Try both storage types
      let storedData = localStorage.getItem(storageKey) ||
      sessionStorage.getItem(storageKey);
      if (!storedData) {
        return null;
      }
      let parsedData;
      if (config.decrypt) {
        parsedData = await this.decrypt(storedData);
      } else {
        parsedData = JSON.parse(storedData);
      }
      // Check expiry
      if (parsedData.expiry && Date.now() > parsedData.expiry) {
        this.removeItem(key);
        return null;
      }
      // Check data integrity
      if (config.checkIntegrity) {
        const expectedChecksum = this.generateChecksum(parsedData.value);
        if (parsedData.checksum !== expectedChecksum) {
          console.warn('Data integrity check failed for key:', key);
          this.removeItem(key);
          return null;
        }
      }
      return parsedData.value;
    } catch (error) {
      console.error('SecureStorage getItem failed:', error);
      // Clean up corrupted data
      this.removeItem(key);
      return null;
    }
  }
  /**
   * Remove item from storage
   */
  removeItem(key) {
    const storageKey = this.storagePrefix + key;
    localStorage.removeItem(storageKey);
    sessionStorage.removeItem(storageKey);
  }
  /**
   * Clear all secure storage items
   */
  clear() {
    // Clear localStorage items
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.storagePrefix)) {
        localStorage.removeItem(key);
      }
    }
    // Clear sessionStorage items
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const key = sessionStorage.key(i);
      if (key && key.startsWith(this.storagePrefix)) {
        sessionStorage.removeItem(key);
      }
    }
  }
  /**
   * Generate checksum for data integrity
   */
  generateChecksum(data) {
    const str = JSON.stringify(data);
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString();
  }
  /**
   * Setup session monitoring for security
   */
  setupSessionMonitoring() {
    // Monitor for storage events (cross-tab security)
    window.addEventListener('storage', (event) => {
      if (event.key && event.key.startsWith(this.storagePrefix)) {
        this.handleStorageEvent(event);
      }
    });
    // Monitor for page visibility changes
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        this.handlePageHidden();
      }
    });
    // Monitor for beforeunload
    window.addEventListener('beforeunload', () => {
      this.handlePageUnload();
    });
  }
  /**
   * Handle storage events for security monitoring
   */
  handleStorageEvent(event) {
    // Log potential security event
    console.warn('External storage modification detected:', event.key);
    // Could trigger security alert or re-authentication
    if (event.key.includes('auth') || event.key.includes('token')) {
      // Critical security data modified externally
      this.triggerSecurityAlert('External modification of authentication data');
    }
  }
  /**
   * Handle page hidden event
   */
  handlePageHidden() {
    // Clear sensitive session data when page is hidden
    const sensitiveKeys = this.getSensitiveKeys();
    sensitiveKeys.forEach((key) => {
      if (key.includes('temp') || key.includes('sensitive')) {
        this.removeItem(key.replace(this.storagePrefix, ''));
      }
    });
  }
  /**
   * Handle page unload event
   */
  handlePageUnload() {
    // Clear all session storage on page unload
    sessionStorage.clear();
  }
  /**
   * Get list of sensitive storage keys
   */
  getSensitiveKeys() {
    const keys = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      if (key && key.startsWith(this.storagePrefix)) {
        keys.push(key);
      }
    }
    return keys;
  }
  /**
   * Cleanup expired items
   */
  cleanupExpiredItems() {
    const now = Date.now();
    // Check localStorage
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.storagePrefix)) {
        try {
          const data = JSON.parse(localStorage.getItem(key));
          if (data.expiry && now > data.expiry) {
            localStorage.removeItem(key);
          }
        } catch (error) {
          // Remove corrupted data
          localStorage.removeItem(key);
        }
      }
    }
    // Check sessionStorage
    for (let i = sessionStorage.length - 1; i >= 0; i--) {
      const key = sessionStorage.key(i);
      if (key && key.startsWith(this.storagePrefix)) {
        try {
          const data = JSON.parse(sessionStorage.getItem(key));
          if (data.expiry && now > data.expiry) {
            sessionStorage.removeItem(key);
          }
        } catch (error) {
          // Remove corrupted data
          sessionStorage.removeItem(key);
        }
      }
    }
  }
  /**
   * Trigger security alert
   */
  triggerSecurityAlert(message) {
    // Dispatch custom security event
    const event = new CustomEvent('securityAlert', {
      detail: {
        type: 'storage_security',
        message: message,
        timestamp: Date.now()
      }
    });
    window.dispatchEvent(event);
  }
  /**
   * Check if storage is available and secure
   */
  isSecure() {
    try {
      // Check if storage is available
      const test = 'security_test';
      localStorage.setItem(test, test);
      localStorage.removeItem(test);
      // Check if HTTPS is being used
      const isHTTPS = window.location.protocol === 'https:';
      // Check if encryption is available
      const hasEncryption = this.encryptionKey && this.encryptionKey !== 'fallback_key';
      return {
        available: true,
        https: isHTTPS,
        encrypted: hasEncryption,
        secure: isHTTPS && hasEncryption
      };
    } catch (error) {
      return {
        available: false,
        https: false,
        encrypted: false,
        secure: false,
        error: error.message
      };
    }
  }
  /**
   * Get storage usage statistics
   */
  getStorageInfo() {
    const info = {
      localStorage: {
        used: 0,
        items: 0
      },
      sessionStorage: {
        used: 0,
        items: 0
      }
    };
    // Calculate localStorage usage
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.storagePrefix)) {
        const value = localStorage.getItem(key);
        info.localStorage.used += key.length + (value ? value.length : 0);
        info.localStorage.items++;
      }
    }
    // Calculate sessionStorage usage
    for (let i = 0; i < sessionStorage.length; i++) {
      const key = sessionStorage.key(i);
      if (key && key.startsWith(this.storagePrefix)) {
        const value = sessionStorage.getItem(key);
        info.sessionStorage.used += key.length + (value ? value.length : 0);
        info.sessionStorage.items++;
      }
    }
    return info;
  }
}
export default new SecureStorage();