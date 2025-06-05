// Secure credential storage utility for integration credentials
// In production, these should be stored server-side with proper encryption
class SecureStorage {
  constructor() {
    this.storageKey = 'bdc_integrations_secure';
    this.encryptionKey = this.getOrCreateEncryptionKey();
  }
  // Generate or retrieve encryption key (in production, this should come from server)
  getOrCreateEncryptionKey() {
    let key = localStorage.getItem('bdc_enc_key');
    if (!key) {
      key = this.generateKey();
      localStorage.setItem('bdc_enc_key', key);
    }
    return key;
  }
  // Simple key generation (replace with proper crypto in production)
  generateKey() {
    return Array.from({ length: 32 }, () => 
      Math.floor(Math.random() * 256).toString(16).padStart(2, '0')
    ).join('');
  }
  // Simple XOR encryption (replace with AES in production)
  encrypt(text, key) {
    if (!text) return '';
    let encrypted = '';
    for (let i = 0; i < text.length; i++) {
      const charCode = text.charCodeAt(i) ^ key.charCodeAt(i % key.length);
      encrypted += String.fromCharCode(charCode);
    }
    return btoa(encrypted); // Base64 encode
  }
  // Simple XOR decryption
  decrypt(encrypted, key) {
    if (!encrypted) return '';
    try {
      const text = atob(encrypted); // Base64 decode
      let decrypted = '';
      for (let i = 0; i < text.length; i++) {
        const charCode = text.charCodeAt(i) ^ key.charCodeAt(i % key.length);
        decrypted += String.fromCharCode(charCode);
      }
      return decrypted;
    } catch (error) {
      console.error('Decryption failed:', error);
      return '';
    }
  }
  // Store credentials securely
  storeCredentials(integrationId, credentials) {
    try {
      const storage = this.getStorage();
      // Encrypt sensitive fields
      const encryptedCredentials = {};
      for (const [key, value] of Object.entries(credentials)) {
        if (this.isSensitiveField(key)) {
          encryptedCredentials[key] = {
            encrypted: true,
            value: this.encrypt(value, this.encryptionKey)
          };
        } else {
          encryptedCredentials[key] = {
            encrypted: false,
            value: value
          };
        }
      }
      storage[integrationId] = {
        credentials: encryptedCredentials,
        timestamp: new Date().toISOString()
      };
      this.saveStorage(storage);
      return true;
    } catch (error) {
      console.error('Failed to store credentials:', error);
      return false;
    }
  }
  // Retrieve credentials
  getCredentials(integrationId) {
    try {
      const storage = this.getStorage();
      const data = storage[integrationId];
      if (!data) return null;
      // Decrypt sensitive fields
      const decryptedCredentials = {};
      for (const [key, field] of Object.entries(data.credentials)) {
        if (field.encrypted) {
          decryptedCredentials[key] = this.decrypt(field.value, this.encryptionKey);
        } else {
          decryptedCredentials[key] = field.value;
        }
      }
      return decryptedCredentials;
    } catch (error) {
      console.error('Failed to retrieve credentials:', error);
      return null;
    }
  }
  // Remove credentials
  removeCredentials(integrationId) {
    try {
      const storage = this.getStorage();
      delete storage[integrationId];
      this.saveStorage(storage);
      return true;
    } catch (error) {
      console.error('Failed to remove credentials:', error);
      return false;
    }
  }
  // Check if field is sensitive
  isSensitiveField(fieldName) {
    const sensitiveFields = [
      'apiKey',
      'apiSecret',
      'secretKey',
      'clientSecret',
      'authToken',
      'accessToken',
      'refreshToken',
      'password',
      'privateKey',
      'webhookSecret',
      'signingSecret'
    ];
    return sensitiveFields.some(field => 
      fieldName.toLowerCase().includes(field.toLowerCase())
    );
  }
  // Get storage object
  getStorage() {
    try {
      const stored = localStorage.getItem(this.storageKey);
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  }
  // Save storage object
  saveStorage(storage) {
    localStorage.setItem(this.storageKey, JSON.stringify(storage));
  }
  // Clear all stored credentials
  clearAll() {
    localStorage.removeItem(this.storageKey);
  }
  // Export credentials (for backup)
  exportCredentials() {
    const storage = this.getStorage();
    const exported = {};
    for (const [integrationId, data] of Object.entries(storage)) {
      exported[integrationId] = {
        timestamp: data.timestamp,
        // Don't include actual credentials in export
        hasCredentials: true
      };
    }
    return exported;
  }
  // Validate credentials format
  validateCredentials(credentials) {
    if (!credentials || typeof credentials !== 'object') {
      return { valid: false, error: 'Invalid credentials format' };
    }
    // Check for empty values in required fields
    for (const [key, value] of Object.entries(credentials)) {
      if (value === '' || value === null || value === undefined) {
        return { valid: false, error: `Missing value for ${key}` };
      }
    }
    return { valid: true };
  }
  // Get credential age
  getCredentialAge(integrationId) {
    const storage = this.getStorage();
    const data = storage[integrationId];
    if (!data || !data.timestamp) return null;
    const age = Date.now() - new Date(data.timestamp).getTime();
    return {
      days: Math.floor(age / (1000 * 60 * 60 * 24)),
      hours: Math.floor((age % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
      isExpired: age > 90 * 24 * 60 * 60 * 1000 // 90 days
    };
  }
}
// Singleton instance
const secureStorage = new SecureStorage();
// Rate limiting for API calls
class RateLimiter {
  constructor() {
    this.limits = new Map();
  }
  // Check if request is allowed
  checkLimit(integrationId, limit = 100, window = 60000) {
    const now = Date.now();
    const key = `${integrationId}_${Math.floor(now / window)}`;
    const current = this.limits.get(key) || 0;
    if (current >= limit) {
      return {
        allowed: false,
        remaining: 0,
        resetTime: Math.ceil(now / window) * window
      };
    }
    this.limits.set(key, current + 1);
    // Clean old entries
    this.cleanup(now - window * 2);
    return {
      allowed: true,
      remaining: limit - current - 1,
      resetTime: Math.ceil(now / window) * window
    };
  }
  // Clean up old entries
  cleanup(before) {
    for (const [key, _] of this.limits) {
      const timestamp = parseInt(key.split('_')[1]) * 60000;
      if (timestamp < before) {
        this.limits.delete(key);
      }
    }
  }
  // Get current usage
  getUsage(integrationId, window = 60000) {
    const now = Date.now();
    const key = `${integrationId}_${Math.floor(now / window)}`;
    return this.limits.get(key) || 0;
  }
}
// Retry logic for failed requests
class RetryManager {
  constructor() {
    this.retryQueues = new Map();
  }
  // Add request to retry queue
  addToRetryQueue(integrationId, request, options = {}) {
    const {
      maxRetries = 3,
      retryDelay = 1000,
      backoffMultiplier = 2
    } = options;
    if (!this.retryQueues.has(integrationId)) {
      this.retryQueues.set(integrationId, []);
    }
    const queue = this.retryQueues.get(integrationId);
    queue.push({
      request,
      attempts: 0,
      maxRetries,
      retryDelay,
      backoffMultiplier,
      createdAt: Date.now()
    });
  }
  // Process retry queue
  async processRetryQueue(integrationId, executeFn) {
    const queue = this.retryQueues.get(integrationId);
    if (!queue || queue.length === 0) return;
    const processed = [];
    const failed = [];
    for (const item of queue) {
      if (item.attempts >= item.maxRetries) {
        failed.push(item);
        continue;
      }
      try {
        await new Promise(resolve => 
          setTimeout(resolve, item.retryDelay * Math.pow(item.backoffMultiplier, item.attempts))
        );
        await executeFn(item.request);
        processed.push(item);
      } catch (error) {
        item.attempts++;
        item.lastError = error;
        if (item.attempts >= item.maxRetries) {
          failed.push(item);
        }
      }
    }
    // Remove processed items
    const remaining = queue.filter(item => 
      !processed.includes(item) && !failed.includes(item)
    );
    this.retryQueues.set(integrationId, remaining);
    return { processed: processed.length, failed: failed.length };
  }
  // Get retry queue status
  getQueueStatus(integrationId) {
    const queue = this.retryQueues.get(integrationId) || [];
    return {
      pending: queue.length,
      oldest: queue.length > 0 ? new Date(queue[0].createdAt) : null
    };
  }
  // Clear retry queue
  clearQueue(integrationId) {
    this.retryQueues.delete(integrationId);
  }
}
// Export utilities
export {
  secureStorage,
  RateLimiter,
  RetryManager
};