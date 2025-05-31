/**
 * Safe array helper functions to prevent undefined errors
 */

/**
 * Safely access array for mapping
 * @param {any} data - The data that should be an array
 * @param {any} defaultValue - Default value if data is not an array
 * @returns {Array} Always returns an array
 */
export const safeArray = (data, defaultValue = []) => {
  if (Array.isArray(data)) return data;
  if (data === null || data === undefined) return defaultValue;
  // If it's an object with items property (common in paginated responses)
  if (data && typeof data === 'object' && Array.isArray(data.items)) return data.items;
  // If it's an object with data property (common in API responses)
  if (data && typeof data === 'object' && Array.isArray(data.data)) return data.data;
  return defaultValue;
};

/**
 * Safely access nested array property
 * @param {Object} obj - The object containing the array
 * @param {string} path - Dot notation path to the array (e.g., 'data.items')
 * @param {any} defaultValue - Default value if path doesn't lead to an array
 * @returns {Array} Always returns an array
 */
export const safeArrayPath = (obj, path, defaultValue = []) => {
  if (!obj || typeof obj !== 'object') return defaultValue;
  
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return defaultValue;
    }
  }
  
  return safeArray(current, defaultValue);
};

/**
 * Check if a value is a non-empty array
 * @param {any} value - The value to check
 * @returns {boolean} True if value is a non-empty array
 */
export const isNonEmptyArray = (value) => {
  return Array.isArray(value) && value.length > 0;
};

/**
 * Safely find an item in an array
 * @param {any} data - The data that should be an array
 * @param {Function} predicate - The find predicate function
 * @param {any} defaultValue - Default value if not found
 * @returns {any} The found item or default value
 */
export const safeFind = (data, predicate, defaultValue = null) => {
  const array = safeArray(data);
  return array.find(predicate) || defaultValue;
};

/**
 * Safely filter an array
 * @param {any} data - The data that should be an array
 * @param {Function} predicate - The filter predicate function
 * @returns {Array} The filtered array
 */
export const safeFilter = (data, predicate) => {
  const array = safeArray(data);
  return array.filter(predicate);
};

/**
 * Get length of array safely
 * @param {any} data - The data that should be an array
 * @returns {number} The length of the array or 0
 */
export const safeLength = (data) => {
  const array = safeArray(data);
  return array.length;
};