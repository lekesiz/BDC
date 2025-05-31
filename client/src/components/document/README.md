# Document Management Components

This directory contains components for document management in the BDC application. These components provide a comprehensive solution for viewing, uploading, and sharing documents.

## Components Overview

### DocumentViewer

A versatile document viewer component that supports multiple file types including PDFs, images, and text files.

```jsx
import { DocumentViewer } from '../components/document';

<DocumentViewer 
  document={documentObject} 
  height="600px"
  showToolbar={true}
  initialZoom={100}
  onDownload={handleDownload}
/>
```

**Props:**
- `document` (Object, required): Document object with properties:
  - `id`: Document ID
  - `name`: Document name
  - `url`: Document URL
  - `type`: Document type ('pdf', 'image', 'txt', etc.)
  - `page_count`: Number of pages (for PDFs)
  - `size_formatted`: Formatted size string
- `height` (String): Height of the viewer (default: '500px')
- `width` (String): Width of the viewer (default: '100%')
- `showToolbar` (Boolean): Whether to show the toolbar (default: true)
- `initialZoom` (Number): Initial zoom level (default: 100)
- `onDownload` (Function): Callback when download button is clicked
- `className` (String): Additional CSS classes

### DocumentUploader

A drag-and-drop file uploader component with validation and progress tracking.

```jsx
import { DocumentUploader } from '../components/document';

<DocumentUploader
  onUploadComplete={handleUploadComplete}
  onUploadError={handleUploadError}
  acceptedFileTypes={['pdf', 'image']}
  maxFileSize={10 * 1024 * 1024}
  maxFiles={5}
  allowMultiple={true}
  metadata={{ categoryId: 123, userId: 456 }}
/>
```

**Props:**
- `onUploadComplete` (Function): Callback when upload completes successfully
- `onUploadError` (Function): Callback when upload fails
- `acceptedFileTypes` (Array|Object): File types to accept (array of extensions or dropzone accept object)
- `maxFileSize` (Number): Maximum file size in bytes (default: 50MB)
- `maxFiles` (Number): Maximum number of files to upload (default: 5)
- `allowMultiple` (Boolean): Allow multiple file selection (default: true)
- `showPreview` (Boolean): Show file preview list (default: true)
- `metadata` (Object): Additional metadata to include with upload
- `className` (String): Additional CSS classes
- `disableDefaultToast` (Boolean): Disable default toast notifications

### DocumentShare

A component for sharing documents with other users and generating public links.

```jsx
import { DocumentShare } from '../components/document';

<DocumentShare
  documentId="123"
  initialShares={existingShares}
  onShareComplete={handleShareComplete}
  onClose={handleClose}
/>
```

**Props:**
- `documentId` (String|Number, required): ID of the document to share
- `initialShares` (Array): Initial shares to display
- `onShareComplete` (Function): Callback when sharing is complete
- `onClose` (Function): Callback when close button is clicked
- `className` (String): Additional CSS classes

### DocumentService

A service module with functions for document operations.

```jsx
import DocumentService from '../components/document/DocumentService';

// Upload a document
const uploadResult = await DocumentService.uploadDocument(
  file,
  { categoryId: 123 },
  (progress) => console.log(`Upload progress: ${progress}%`)
);

// Download a document
await DocumentService.downloadDocument(documentId, filename);

// Share a document
await DocumentService.shareDocument(documentId, [userId1, userId2], 'edit');

// Delete a document
await DocumentService.deleteDocument(documentId);
```

**API:**
- `uploadDocument(file, metadata, onProgress)`: Upload a document
- `downloadDocument(documentId, filename, onProgress)`: Download a document
- `deleteDocument(documentId)`: Delete a document
- `updateDocumentMetadata(documentId, metadata)`: Update document metadata
- `shareDocument(documentId, users, permission)`: Share a document with users
- `validateFile(file)`: Validate a file before upload
- `getDocumentType(filename, mimeType)`: Get document type from filename/MIME type
- `isPreviewSupported(filename, mimeType)`: Check if preview is supported
- `formatFileSize(bytes)`: Format bytes to human-readable size
- `SUPPORTED_DOCUMENT_TYPES`: Object with supported document types info

## Usage Examples

### Displaying a Document

```jsx
import React, { useState, useEffect } from 'react';
import { DocumentViewer } from '../components/document';
import axios from 'axios';

const DocumentViewPage = ({ documentId }) => {
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`/api/documents/${documentId}`);
        setDocument(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load document');
      } finally {
        setLoading(false);
      }
    };

    fetchDocument();
  }, [documentId]);

  if (loading) return <div>Loading document...</div>;
  if (error) return <div>{error}</div>;
  if (!document) return <div>Document not found</div>;

  return (
    <div className="document-page">
      <h1>{document.name}</h1>
      <DocumentViewer 
        document={document}
        height="600px"
        onDownload={() => console.log('Download clicked')}
      />
    </div>
  );
};

export default DocumentViewPage;
```

### Uploading Documents

```jsx
import React from 'react';
import { DocumentUploader } from '../components/document';
import { toast } from 'react-toastify';

const DocumentUploadPage = () => {
  const handleUploadComplete = (documents) => {
    toast.success(`Successfully uploaded ${documents.length} document(s)`);
    // Navigate or update UI...
  };

  const handleUploadError = (errors) => {
    toast.error(`Upload failed: ${errors.join(', ')}`);
  };

  return (
    <div className="upload-page">
      <h1>Upload Documents</h1>
      <p>Drag and drop files below or click to select files.</p>

      <DocumentUploader
        onUploadComplete={handleUploadComplete}
        onUploadError={handleUploadError}
        acceptedFileTypes={['pdf', 'image', 'office']}
        maxFileSize={20 * 1024 * 1024} // 20MB
        maxFiles={10}
        metadata={{ categoryId: 123 }}
      />
    </div>
  );
};

export default DocumentUploadPage;
```

### Sharing Documents

```jsx
import React, { useState } from 'react';
import { DocumentShare } from '../components/document';

const DocumentSharingModal = ({ documentId, onClose }) => {
  const handleShareComplete = (shares) => {
    console.log(`Document shared with ${shares.length} users`);
    // Update UI or parent component...
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Share Document</h2>
        <DocumentShare
          documentId={documentId}
          onShareComplete={handleShareComplete}
          onClose={onClose}
        />
      </div>
    </div>
  );
};

export default DocumentSharingModal;
```

## Testing

All components have comprehensive test coverage. You can run the tests with:

```bash
npm test -- components/document
```

## Customization

These components use Tailwind CSS for styling and can be customized by:

1. Passing additional CSS classes via the `className` prop
2. Overriding Tailwind styles using the theme configuration
3. Creating component wrappers with custom styles

## API Integration

The DocumentService module interacts with the following API endpoints:

- `POST /api/documents/upload`: Upload a document
- `GET /api/documents/{id}`: Get document details
- `GET /api/documents/{id}/download`: Download a document
- `DELETE /api/documents/{id}`: Delete a document
- `PATCH /api/documents/{id}`: Update document metadata
- `POST /api/documents/{id}/share`: Share a document
- `GET /api/documents/{id}/shares`: Get document shares
- `DELETE /api/documents/shares/{id}`: Remove a share
- `POST /api/documents/{id}/public-link`: Create public link
- `DELETE /api/documents/{id}/public-link`: Remove public link
- `GET /api/users/search`: Search users for sharing

Any changes to these API endpoints will require corresponding updates to the DocumentService module.