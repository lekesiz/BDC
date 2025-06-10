// TODO: i18n - processed
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
/**
 * Combines multiple class names using clsx and tailwind-merge
 * This allows for conditional and dynamic class names that are properly merged
 * with tailwind classes
 * 
 * @param  {...any} inputs - Class names to be combined
 * @returns {string} - Merged class names
 */import { useTranslation } from "react-i18next";
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
/**
 * Format a date string into a human-readable format
 * 
 * @param {string} dateString - ISO date string to format
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} - Formatted date string
 */
export function formatDate(dateString, options = {}) {
  if (!dateString) return '';
  const date = new Date(dateString);
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options
  };
  return new Intl.DateTimeFormat('en-US', defaultOptions).format(date);
}
/**
 * Format a date with time
 * 
 * @param {string} dateString - ISO date string to format
 * @returns {string} - Formatted date string with time
 */
export function formatDateTime(dateString) {
  return formatDate(dateString, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
/**
 * Truncate a string to a specified length and add an ellipsis
 * 
 * @param {string} str - String to truncate
 * @param {number} length - Maximum length before truncation
 * @returns {string} - Truncated string
 */
export function truncate(str, length = 50) {
  if (!str) return '';
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
}
/**
 * Capitalize the first letter of a string
 * 
 * @param {string} str - String to capitalize
 * @returns {string} - Capitalized string
 */
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}
/**
 * Format a snake_case or kebab-case string to Title Case
 * 
 * @param {string} str - String to format
 * @returns {string} - Formatted string
 */
export function formatTitle(str) {
  if (!str) return '';
  // Replace underscores and hyphens with spaces
  const words = str.replace(/[_-]/g, ' ').split(' ');
  // Capitalize each word
  const capitalizedWords = words.map((word) => capitalize(word));
  return capitalizedWords.join(' ');
}
/**
 * Get initials from a name (first letter of first and last name)
 * 
 * @param {string} name - Full name
 * @returns {string} - Initials
 */
export function getInitials(name) {
  if (!name) return '';
  const names = name.split(' ');
  if (names.length === 1) return names[0].charAt(0).toUpperCase();
  return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
}
/**
 * Parse JWT token to get payload data
 * 
 * @param {string} token - JWT token
 * @returns {object|null} - Parsed token payload or null if invalid
 */
export function parseJwt(token) {
  if (!token) return null;
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64).
      split('').
      map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).
      join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
}
/**
 * Format bytes to human readable format
 * 
 * @param {number} bytes - Number of bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted string
 */
export function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
/**
 * Check if a JWT token is expired
 * 
 * @param {string} token - JWT token
 * @returns {boolean} - True if token is expired or invalid
 */
export function isTokenExpired(token) {
  const payload = parseJwt(token);
  if (!payload || !payload.exp) return true;
  const currentTime = Date.now() / 1000;
  return payload.exp < currentTime;
}
/**
 * Convert bytes to a human-readable size format
 * 
 * @param {number} bytes - Size in bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted size string
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
/**
 * Deep clone an object
 * 
 * @param {object} obj - Object to clone
 * @returns {object} - Cloned object
 */
export function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
}
/**
 * Generate a random ID string
 * 
 * @param {number} length - Length of the ID
 * @returns {string} - Random ID
 */
export function generateId(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}