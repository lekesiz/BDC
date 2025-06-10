// TODO: i18n - processed
import { useTranslation } from "react-i18next"; /**
 * Input Sanitization and Validation Service
 * Protects against XSS, injection attacks, and data validation issues
 */
class InputSanitizer {
  constructor() {
    // XSS patterns to detect and remove
    this.xssPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
    /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,
    /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi,
    /<link\b[^>]*>/gi,
    /<meta\b[^>]*>/gi,
    /<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi,
    /javascript:/gi,
    /vbscript:/gi,
    /onload\s*=/gi,
    /onerror\s*=/gi,
    /onclick\s*=/gi,
    /onmouseover\s*=/gi,
    /onfocus\s*=/gi,
    /onblur\s*=/gi,
    /onchange\s*=/gi,
    /onsubmit\s*=/gi,
    /expression\s*\(/gi,
    /url\s*\(/gi,
    /@import/gi,
    /binding\s*:/gi,
    /document\.cookie/gi,
    /document\.write/gi,
    /eval\s*\(/gi,
    /setTimeout\s*\(/gi,
    /setInterval\s*\(/gi];

    // SQL injection patterns
    this.sqlPatterns = [
    /('|(\\')|(;)|(\||(\*)|(%)|(\-\-)|(\+)|(\,)|(\<)|(\>)|(\{)|(\})|(\[)|(\])|(\()|(\))|(\&)|(\#))/gi,
    /(\b(ALTER|CREATE|DELETE|DROP|EXEC(UTE){0,1}|INSERT( +INTO){0,1}|MERGE|SELECT|UPDATE|UNION( +ALL){0,1})\b)/gi,
    /(\/\*(\*(?!\/)|[^*])*\*\/)/gi,
    /(\b(AND|OR)\b.*(=|>|<|\!|<>|><))/gi,
    /(\b(GRANT|REVOKE)\b)/gi,
    /(\b(GROUP\s+BY|ORDER\s+BY|HAVING)\b)/gi];

    // Command injection patterns
    this.commandPatterns = [
    /[;&|`$(){}[\]]/g,
    /\b(cat|ls|pwd|whoami|id|uname|ps|kill|rm|mv|cp|chmod|chown|grep|awk|sed|sort|uniq|wc|head|tail|more|less)\b/gi,
    /(\\|\/)(bin|etc|usr|var|tmp|home)/gi,
    /(\.\.|\.\/|~\/)/gi];

    // Allowed HTML tags for rich text content
    this.allowedTags = [
    'p', 'br', 'strong', 'em', 'u', 'b', 'i',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'a', 'img', 'table', 'thead', 'tbody', 'tr', 'th', 'td'];

    // Allowed attributes for HTML tags
    this.allowedAttributes = {
      'a': ['href', 'title', 'target'],
      'img': ['src', 'alt', 'width', 'height', 'title'],
      'table': ['class'],
      'tr': ['class'],
      'td': ['class', 'colspan', 'rowspan'],
      'th': ['class', 'colspan', 'rowspan'],
      '*': ['class', 'id']
    };
  }
  /**
   * Sanitize input text to prevent XSS and injection attacks
   */
  sanitize(input, options = {}) {
    if (typeof input !== 'string') {
      return input;
    }
    const config = {
      allowHTML: false,
      allowedTags: this.allowedTags,
      allowedAttributes: this.allowedAttributes,
      maxLength: 10000,
      trimWhitespace: true,
      removeNullBytes: true,
      ...options
    };
    let sanitized = input;
    // Remove null bytes
    if (config.removeNullBytes) {
      sanitized = sanitized.replace(/\x00/g, '');
    }
    // Trim whitespace
    if (config.trimWhitespace) {
      sanitized = sanitized.trim();
    }
    // Length validation
    if (config.maxLength && sanitized.length > config.maxLength) {
      sanitized = sanitized.substring(0, config.maxLength);
    }
    // Handle HTML content
    if (config.allowHTML) {
      sanitized = this.sanitizeHTML(sanitized, config);
    } else {
      // HTML encode all content
      sanitized = this.htmlEncode(sanitized);
    }
    // Remove XSS patterns
    sanitized = this.removeXSSPatterns(sanitized);
    // Remove SQL injection patterns
    if (config.preventSQL !== false) {
      sanitized = this.removeSQLPatterns(sanitized);
    }
    // Remove command injection patterns
    if (config.preventCommand !== false) {
      sanitized = this.removeCommandPatterns(sanitized);
    }
    return sanitized;
  }
  /**
   * HTML encode special characters
   */
  htmlEncode(str) {
    return str.
    replace(/&/g, '&amp;').
    replace(/</g, '&lt;').
    replace(/>/g, '&gt;').
    replace(/"/g, '&quot;').
    replace(/'/g, '&#x27;').
    replace(/\//g, '&#x2F;');
  }
  /**
   * HTML decode special characters
   */
  htmlDecode(str) {
    return str.
    replace(/&amp;/g, '&').
    replace(/&lt;/g, '<').
    replace(/&gt;/g, '>').
    replace(/&quot;/g, '"').
    replace(/&#x27;/g, "'").
    replace(/&#x2F;/g, '/');
  }
  /**
   * Sanitize HTML content while preserving allowed tags
   */
  sanitizeHTML(html, config) {
    // Create a temporary DOM element
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    // Recursively clean the DOM
    this.cleanElement(tempDiv, config);
    return tempDiv.innerHTML;
  }
  /**
   * Clean DOM element recursively
   */
  cleanElement(element, config) {
    const children = Array.from(element.children);
    children.forEach((child) => {
      const tagName = child.tagName.toLowerCase();
      // Remove disallowed tags
      if (!config.allowedTags.includes(tagName)) {
        child.remove();
        return;
      }
      // Clean attributes
      this.cleanAttributes(child, config.allowedAttributes);
      // Recursively clean children
      this.cleanElement(child, config);
    });
  }
  /**
   * Clean element attributes
   */
  cleanAttributes(element, allowedAttrs) {
    const tagName = element.tagName.toLowerCase();
    const allowedForTag = allowedAttrs[tagName] || [];
    const allowedForAll = allowedAttrs['*'] || [];
    const allowedList = [...allowedForTag, ...allowedForAll];
    // Get all attributes
    const attributes = Array.from(element.attributes);
    attributes.forEach((attr) => {
      const attrName = attr.name.toLowerCase();
      // Remove disallowed attributes
      if (!allowedList.includes(attrName)) {
        element.removeAttribute(attr.name);
        return;
      }
      // Validate attribute values
      const attrValue = attr.value;
      // Check for JavaScript in attribute values
      if (this.containsJavaScript(attrValue)) {
        element.removeAttribute(attr.name);
        return;
      }
      // Validate specific attributes
      if (attrName === 'href' || attrName === 'src') {
        if (!this.isValidURL(attrValue)) {
          element.removeAttribute(attr.name);
        }
      }
    });
  }
  /**
   * Check if text contains JavaScript
   */
  containsJavaScript(text) {
    const jsPatterns = [
    /javascript:/gi,
    /vbscript:/gi,
    /on\w+\s*=/gi,
    /expression\s*\(/gi,
    /url\s*\(/gi,
    /eval\s*\(/gi];

    return jsPatterns.some((pattern) => pattern.test(text));
  }
  /**
   * Validate URL safety
   */
  isValidURL(url) {
    try {
      const parsed = new URL(url, window.location.origin);
      // Only allow http, https, and mailto protocols
      const allowedProtocols = ['http:', 'https:', 'mailto:'];
      return allowedProtocols.includes(parsed.protocol);
    } catch {
      // Relative URLs are okay
      return !url.includes(':');
    }
  }
  /**
   * Remove XSS patterns
   */
  removeXSSPatterns(text) {
    let cleaned = text;
    this.xssPatterns.forEach((pattern) => {
      cleaned = cleaned.replace(pattern, '');
    });
    return cleaned;
  }
  /**
   * Remove SQL injection patterns
   */
  removeSQLPatterns(text) {
    let cleaned = text;
    this.sqlPatterns.forEach((pattern) => {
      cleaned = cleaned.replace(pattern, '');
    });
    return cleaned;
  }
  /**
   * Remove command injection patterns
   */
  removeCommandPatterns(text) {
    let cleaned = text;
    this.commandPatterns.forEach((pattern) => {
      cleaned = cleaned.replace(pattern, '');
    });
    return cleaned;
  }
  /**
   * Validate input against rules
   */
  validate(input, rules = []) {
    const errors = [];
    rules.forEach((rule) => {
      switch (rule.type) {
        case 'required':
          if (!input || input.toString().trim() === '') {
            errors.push(rule.message || 'This field is required');
          }
          break;
        case 'minLength':
          if (input && input.toString().length < rule.value) {
            errors.push(rule.message || `Minimum length is ${rule.value}`);
          }
          break;
        case 'maxLength':
          if (input && input.toString().length > rule.value) {
            errors.push(rule.message || `Maximum length is ${rule.value}`);
          }
          break;
        case 'pattern':
          if (input && !rule.value.test(input.toString())) {
            errors.push(rule.message || 'Invalid format');
          }
          break;
        case 'email':
          const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (input && !emailPattern.test(input.toString())) {
            errors.push(rule.message || 'Invalid email format');
          }
          break;
        case 'url':
          if (input && !this.isValidURL(input.toString())) {
            errors.push(rule.message || 'Invalid URL format');
          }
          break;
        case 'noXSS':
          if (input && this.detectXSS(input.toString()).isXSS) {
            errors.push(rule.message || 'Contains potentially malicious content');
          }
          break;
        case 'noSQL':
          if (input && this.detectSQL(input.toString()).isSQL) {
            errors.push(rule.message || 'Contains potentially malicious SQL');
          }
          break;
      }
    });
    return {
      isValid: errors.length === 0,
      errors
    };
  }
  /**
   * Detect XSS patterns in text
   */
  detectXSS(text) {
    for (const pattern of this.xssPatterns) {
      if (pattern.test(text)) {
        return {
          isXSS: true,
          pattern: pattern.toString()
        };
      }
    }
    return { isXSS: false };
  }
  /**
   * Detect SQL injection patterns in text
   */
  detectSQL(text) {
    for (const pattern of this.sqlPatterns) {
      if (pattern.test(text)) {
        return {
          isSQL: true,
          pattern: pattern.toString()
        };
      }
    }
    return { isSQL: false };
  }
  /**
   * Sanitize file name
   */
  sanitizeFileName(fileName) {
    if (typeof fileName !== 'string') {
      return 'file';
    }
    return fileName.
    replace(/[^a-zA-Z0-9._-]/g, '_').
    replace(/_{2,}/g, '_').
    replace(/^[._-]+|[._-]+$/g, '').
    substring(0, 255);
  }
  /**
   * Validate and sanitize form data
   */
  sanitizeFormData(formData, rules = {}) {
    const sanitized = {};
    const errors = {};
    Object.keys(formData).forEach((key) => {
      const value = formData[key];
      const fieldRules = rules[key] || [];
      // Sanitize value
      if (typeof value === 'string') {
        sanitized[key] = this.sanitize(value, fieldRules.sanitizeOptions);
      } else {
        sanitized[key] = value;
      }
      // Validate value
      const validation = this.validate(sanitized[key], fieldRules.validation || []);
      if (!validation.isValid) {
        errors[key] = validation.errors;
      }
    });
    return {
      data: sanitized,
      errors,
      isValid: Object.keys(errors).length === 0
    };
  }
}
export default new InputSanitizer();