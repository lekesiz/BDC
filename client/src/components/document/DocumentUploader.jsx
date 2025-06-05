import React, { useState, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useDropzone } from 'react-dropzone';
import { FaUpload, FaFilePdf, FaFileImage, FaFileAlt, FaFileArchive, FaFile, FaTimes, FaCheck } from 'react-icons/fa';
import DocumentService from './DocumentService';
/**
 * DocumentUploader - Component for uploading documents with drag and drop
 */
const DocumentUploader = ({
  onUploadComplete,
  onUploadError,
  acceptedFileTypes = null,
  maxFileSize = 50 * 1024 * 1024, // 50MB default
  maxFiles = 5,
  allowMultiple = true,
  className = '',
  showPreview = true,
  metadata = {},
  disableDefaultToast = false
}) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [uploadStatus, setUploadStatus] = useState({});
  const uploadTimersRef = useRef({});
  // Create accept object for react-dropzone
  const getAcceptedTypes = () => {
    if (!acceptedFileTypes) return undefined;
    // Convert array of file extensions to object for dropzone
    if (Array.isArray(acceptedFileTypes)) {
      return acceptedFileTypes.reduce((acc, ext) => {
        const type = DocumentService.SUPPORTED_DOCUMENT_TYPES[ext]?.mimeTypes || [];
        type.forEach(mime => {
          acc[mime] = [];
        });
        return acc;
      }, {});
    }
    // Direct mime type definitions
    return acceptedFileTypes;
  };
  // File drop handler
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    // Handle rejected files first
    if (rejectedFiles.length > 0) {
      const errorMessages = rejectedFiles.map(({ file, errors }) => {
        const errorMsg = errors.map(e => e.message).join(', ');
        return `${file.name}: ${errorMsg}`;
      });
      if (onUploadError) {
        onUploadError(errorMessages);
      }
    }
    // Process accepted files
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: `${file.name}-${file.size}-${Date.now()}`,
      progress: 0,
      status: 'pending',
      error: null
    }));
    // Add to existing files, ensuring we don't exceed maxFiles
    setFiles(prevFiles => {
      const combinedFiles = [...prevFiles, ...newFiles];
      return combinedFiles.slice(0, maxFiles);
    });
  }, [maxFiles, onUploadError]);
  // Set up react-dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: getAcceptedTypes(),
    maxSize: maxFileSize,
    multiple: allowMultiple,
    disabled: uploading
  });
  // Handle file removal before upload
  const removeFile = (fileId) => {
    setFiles(prevFiles => prevFiles.filter(file => file.id !== fileId));
  };
  // Get file icon based on type
  const getFileIcon = (file) => {
    const fileType = file.type;
    if (fileType.includes('pdf')) {
      return <FaFilePdf className="text-red-500" />;
    } else if (fileType.includes('image')) {
      return <FaFileImage className="text-blue-500" />;
    } else if (fileType.includes('text')) {
      return <FaFileAlt className="text-yellow-500" />;
    } else if (fileType.includes('zip') || fileType.includes('rar') || fileType.includes('gz')) {
      return <FaFileArchive className="text-purple-500" />;
    } else {
      return <FaFile className="text-gray-500" />;
    }
  };
  // Handle upload progress updates
  const updateProgress = (fileId, progress) => {
    setUploadProgress(prev => ({
      ...prev,
      [fileId]: progress
    }));
    // Simulate progress even if server doesn't send updates
    if (progress > 0 && progress < 100) {
      clearTimeout(uploadTimersRef.current[fileId]);
      uploadTimersRef.current[fileId] = setTimeout(() => {
        updateProgress(fileId, Math.min(progress + 5, 95));
      }, 500);
    }
  };
  // Update status for a file
  const updateStatus = (fileId, status, error = null) => {
    setUploadStatus(prev => ({
      ...prev,
      [fileId]: { status, error }
    }));
  };
  // Handle form submission and upload
  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    const uploadPromises = files.map(async (fileObj) => {
      const { file, id } = fileObj;
      // Skip already uploaded files
      if (uploadStatus[id]?.status === 'success') {
        return { id, success: true, data: null };
      }
      // Reset progress
      updateProgress(id, 0);
      updateStatus(id, 'uploading');
      try {
        const data = await DocumentService.uploadDocument(
          file, 
          metadata,
          (progress) => updateProgress(id, progress)
        );
        updateProgress(id, 100);
        updateStatus(id, 'success');
        clearTimeout(uploadTimersRef.current[id]);
        return { id, success: true, data };
      } catch (error) {
        updateStatus(id, 'error', error.message || 'Upload failed');
        clearTimeout(uploadTimersRef.current[id]);
        return { id, success: false, error };
      }
    });
    try {
      const results = await Promise.all(uploadPromises);
      const successfulUploads = results.filter(r => r.success).map(r => r.data);
      const failedUploads = results.filter(r => !r.success);
      // Call the complete callback with results
      if (onUploadComplete) {
        onUploadComplete(successfulUploads, failedUploads);
      }
    } catch (error) {
      if (onUploadError) {
        onUploadError([error.message || 'An unexpected error occurred during upload']);
      }
    } finally {
      setUploading(false);
    }
  };
  // File preview renderer
  const renderFilePreview = (fileObj) => {
    const { file, id } = fileObj;
    const progress = uploadProgress[id] || 0;
    const status = uploadStatus[id]?.status || 'pending';
    const error = uploadStatus[id]?.error;
    return (
      <div 
        key={id} 
        className="flex items-center justify-between p-3 bg-white rounded-lg shadow-sm border mb-2"
        data-cy="file-item"
      >
        <div className="flex items-center mr-3">
          {getFileIcon(file)}
          <div className="ml-3">
            <p className="text-sm font-medium truncate max-w-xs">{file.name}</p>
            <p className="text-xs text-gray-500">
              {DocumentService.formatFileSize(file.size)}
            </p>
            {error && <p className="text-xs text-red-500">{error}</p>}
          </div>
        </div>
        <div className="flex items-center">
          {status === 'pending' && (
            <button
              onClick={() => removeFile(id)}
              className="text-gray-500 hover:text-red-500 p-1"
              data-cy="remove-file"
            >
              <FaTimes />
            </button>
          )}
          {status === 'uploading' && (
            <div className="w-24 bg-gray-200 h-2 rounded-full overflow-hidden">
              <div 
                className="bg-blue-500 h-full" 
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          )}
          {status === 'success' && (
            <FaCheck className="text-green-500" />
          )}
          {status === 'error' && (
            <FaTimes className="text-red-500" />
          )}
        </div>
      </div>
    );
  };
  return (
    <div className={`document-uploader ${className}`} data-cy="document-uploader">
      {/* Dropzone area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition duration-200 
          ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:bg-gray-50'} 
          ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
        data-cy="dropzone"
      >
        <input {...getInputProps()} data-cy="file-input" />
        <FaUpload className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm font-medium text-gray-900">
          {isDragActive ? 'Dosyaları buraya bırakın' : 'Dosyaları seçmek için tıklayın veya sürükleyin'}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          {acceptedFileTypes 
            ? `Desteklenen dosya türleri: ${Object.keys(DocumentService.SUPPORTED_DOCUMENT_TYPES).join(', ')}`
            : 'Tüm dosya türleri desteklenir'}
        </p>
        <p className="text-xs text-gray-500">
          Maksimum dosya boyutu: {DocumentService.formatFileSize(maxFileSize)}
        </p>
        {allowMultiple && (
          <p className="text-xs text-gray-500">
            Maksimum dosya sayısı: {maxFiles}
          </p>
        )}
      </div>
      {/* File list */}
      {showPreview && files.length > 0 && (
        <div className="mt-4" data-cy="file-list">
          <h3 className="text-sm font-medium mb-2">Yüklenecek Dosyalar ({files.length})</h3>
          <div className="space-y-2">
            {files.map(fileObj => renderFilePreview(fileObj))}
          </div>
        </div>
      )}
      {/* Upload button */}
      {files.length > 0 && (
        <button
          onClick={handleUpload}
          disabled={uploading}
          className={`mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
            ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          data-cy="upload-button"
        >
          {uploading ? 'Yükleniyor...' : 'Dosyaları Yükle'}
        </button>
      )}
    </div>
  );
};
DocumentUploader.propTypes = {
  /** Callback function when upload is complete */
  onUploadComplete: PropTypes.func,
  /** Callback function when upload errors occur */
  onUploadError: PropTypes.func,
  /** Accepted file types (array of extensions or dropzone accept object) */
  acceptedFileTypes: PropTypes.oneOfType([
    PropTypes.object,
    PropTypes.arrayOf(PropTypes.string)
  ]),
  /** Maximum file size in bytes */
  maxFileSize: PropTypes.number,
  /** Maximum number of files that can be uploaded */
  maxFiles: PropTypes.number,
  /** Allow multiple files to be selected */
  allowMultiple: PropTypes.bool,
  /** Additional CSS classes */
  className: PropTypes.string,
  /** Show file preview list */
  showPreview: PropTypes.bool,
  /** Additional metadata to include with upload */
  metadata: PropTypes.object,
  /** Disable default toast notifications */
  disableDefaultToast: PropTypes.bool
};
export default DocumentUploader;