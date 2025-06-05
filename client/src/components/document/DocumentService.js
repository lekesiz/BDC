/**
 * DocumentService - Handles document operations (upload, download, processing)
 */
import axios from 'axios';
import { toast } from 'react-toastify';
/**
 * Supported document types and their corresponding mime types
 */
export const SUPPORTED_DOCUMENT_TYPES = {
  // PDF documents
  pdf: {
    mimeTypes: ['application/pdf'],
    maxSize: 50 * 1024 * 1024, // 50MB
    preview: true,
    extensions: ['.pdf']
  },
  // Images
  image: {
    mimeTypes: [
      'image/jpeg', 
      'image/png', 
      'image/gif', 
      'image/svg+xml', 
      'image/webp'
    ],
    maxSize: 20 * 1024 * 1024, // 20MB
    preview: true,
    extensions: ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']
  },
  // Microsoft Office documents
  office: {
    mimeTypes: [
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    ],
    maxSize: 25 * 1024 * 1024, // 25MB
    preview: true,
    extensions: ['.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
  },
  // Text files
  text: {
    mimeTypes: ['text/plain', 'text/csv', 'text/html', 'text/css', 'text/javascript'],
    maxSize: 10 * 1024 * 1024, // 10MB
    preview: true,
    extensions: ['.txt', '.csv', '.html', '.css', '.js']
  },
  // Archives
  archive: {
    mimeTypes: [
      'application/zip', 
      'application/x-rar-compressed', 
      'application/x-7z-compressed',
      'application/gzip'
    ],
    maxSize: 100 * 1024 * 1024, // 100MB
    preview: false,
    extensions: ['.zip', '.rar', '.7z', '.gz', '.tar.gz']
  }
};
/**
 * Gets the document type based on the file extension or mime type
 * @param {string} filename - The file name
 * @param {string} mimeType - The file mime type
 * @returns {string} The document type or 'unknown'
 */
export const getDocumentType = (filename, mimeType) => {
  const extension = '.' + filename.split('.').pop().toLowerCase();
  // Check by extension first
  for (const [type, info] of Object.entries(SUPPORTED_DOCUMENT_TYPES)) {
    if (info.extensions.includes(extension)) {
      return type;
    }
  }
  // Then check by mime type
  for (const [type, info] of Object.entries(SUPPORTED_DOCUMENT_TYPES)) {
    if (info.mimeTypes.includes(mimeType)) {
      return type;
    }
  }
  return 'unknown';
};
/**
 * Checks if file is supported for preview
 * @param {string} filename - The file name
 * @param {string} mimeType - The file mime type
 * @returns {boolean} Whether the file is supported for preview
 */
export const isPreviewSupported = (filename, mimeType) => {
  const documentType = getDocumentType(filename, mimeType);
  return documentType !== 'unknown' && 
         SUPPORTED_DOCUMENT_TYPES[documentType]?.preview === true;
};
/**
 * Formats bytes to human-readable size
 * @param {number} bytes - The size in bytes
 * @returns {string} Formatted size string
 */
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};
/**
 * Validates file before upload
 * @param {File} file - The file to validate
 * @returns {Object} Validation result {valid, message}
 */
export const validateFile = (file) => {
  const documentType = getDocumentType(file.name, file.type);
  if (documentType === 'unknown') {
    return {
      valid: false,
      message: 'Desteklenmeyen dosya türü'
    };
  }
  const typeInfo = SUPPORTED_DOCUMENT_TYPES[documentType];
  if (file.size > typeInfo.maxSize) {
    return {
      valid: false,
      message: `Dosya boyutu çok büyük. Maksimum boyut: ${formatFileSize(typeInfo.maxSize)}`
    };
  }
  return {
    valid: true,
    message: 'Dosya geçerli',
    documentType
  };
};
/**
 * Uploads a document to the server
 * @param {File} file - The file to upload
 * @param {Object} metadata - Additional metadata for the document
 * @param {Function} onProgress - Progress callback function
 * @returns {Promise<Object>} Upload result
 */
export const uploadDocument = async (file, metadata = {}, onProgress = null) => {
  // Validate file first
  const validation = validateFile(file);
  if (!validation.valid) {
    toast.error(validation.message);
    return Promise.reject(new Error(validation.message));
  }
  // Create form data
  const formData = new FormData();
  formData.append('file', file);
  // Add metadata
  Object.entries(metadata).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      formData.append(key, value);
    }
  });
  try {
    const response = await axios.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (event) => {
        if (onProgress) {
          const percentCompleted = Math.round((event.loaded * 100) / event.total);
          onProgress(percentCompleted);
        }
      }
    });
    toast.success('Dosya başarıyla yüklendi');
    return response.data;
  } catch (error) {
    const errorMessage = error.response?.data?.message || 'Dosya yüklenirken bir hata oluştu';
    toast.error(errorMessage);
    throw error;
  }
};
/**
 * Downloads a document
 * @param {string|number} documentId - The document ID to download
 * @param {string} filename - The filename for the downloaded file
 * @param {Function} onProgress - Progress callback function
 * @returns {Promise<void>}
 */
export const downloadDocument = async (documentId, filename = null, onProgress = null) => {
  try {
    const response = await axios({
      url: `/api/documents/${documentId}/download`,
      method: 'GET',
      responseType: 'blob',
      onDownloadProgress: (progressEvent) => {
        if (onProgress) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      }
    });
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename || `document-${documentId}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    toast.success('Dosya indirildi');
  } catch (error) {
    toast.error('Dosya indirilirken bir hata oluştu');
    throw error;
  }
};
/**
 * Deletes a document
 * @param {string|number} documentId - The document ID to delete
 * @returns {Promise<Object>} Delete result
 */
export const deleteDocument = async (documentId) => {
  try {
    const response = await axios.delete(`/api/documents/${documentId}`);
    toast.success('Doküman silindi');
    return response.data;
  } catch (error) {
    toast.error('Doküman silinirken bir hata oluştu');
    throw error;
  }
};
/**
 * Updates document metadata
 * @param {string|number} documentId - The document ID
 * @param {Object} metadata - The metadata to update
 * @returns {Promise<Object>} Update result
 */
export const updateDocumentMetadata = async (documentId, metadata) => {
  try {
    const response = await axios.patch(`/api/documents/${documentId}`, metadata);
    toast.success('Doküman bilgileri güncellendi');
    return response.data;
  } catch (error) {
    toast.error('Doküman güncellenirken bir hata oluştu');
    throw error;
  }
};
/**
 * Shares a document with other users
 * @param {string|number} documentId - The document ID
 * @param {Array} users - Array of user IDs to share with
 * @param {string} permission - Permission level ('view', 'edit', etc.)
 * @returns {Promise<Object>} Share result
 */
export const shareDocument = async (documentId, users, permission = 'view') => {
  try {
    const response = await axios.post(`/api/documents/${documentId}/share`, {
      users,
      permission
    });
    toast.success('Doküman paylaşıldı');
    return response.data;
  } catch (error) {
    toast.error('Doküman paylaşılırken bir hata oluştu');
    throw error;
  }
};
export default {
  uploadDocument,
  downloadDocument,
  deleteDocument,
  updateDocumentMetadata,
  shareDocument,
  validateFile,
  getDocumentType,
  isPreviewSupported,
  formatFileSize,
  SUPPORTED_DOCUMENT_TYPES
};