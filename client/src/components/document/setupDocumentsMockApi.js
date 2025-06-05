import {
  fetchDocuments,
  fetchDocument,
  fetchFolder,
  fetchDocumentVersions,
  fetchDocumentComments,
  addDocumentComment,
  fetchDocumentSharing,
  generateShareLink,
  shareDocument,
  shareMultipleDocuments,
  updateDocument,
  deleteDocument,
  uploadDocument,
  createFolder,
  searchUsers,
  fetchMultipleDocuments
} from './mockDocumentsData';
// This function sets up mock API handlers for document endpoints
export const setupDocumentsMockApi = (api, originalGet, originalPost, originalPut, originalDelete) => {
  // Override GET requests for document endpoints
  api.get = function(url, config) {
    // List documents in root or specific folder
    const documentsMatch = url.match(/\/api\/documents$/);
    if (documentsMatch) {
      const urlObj = new URL(url, window.location.origin);
      const folderId = urlObj.searchParams.get('folder_id');
      return Promise.resolve(fetchDocuments(folderId));
    }
    // Document versions
    const versionsMatch = url.match(/\/api\/documents\/(\d+)\/versions$/);
    if (versionsMatch) {
      return Promise.resolve(fetchDocumentVersions(versionsMatch[1]));
    }
    // Document comments
    const commentsMatch = url.match(/\/api\/documents\/(\d+)\/comments$/);
    if (commentsMatch) {
      return Promise.resolve(fetchDocumentComments(commentsMatch[1]));
    }
    // Document sharing info
    const sharingMatch = url.match(/\/api\/documents\/(\d+)\/sharing$/);
    if (sharingMatch) {
      return Promise.resolve(fetchDocumentSharing(sharingMatch[1]));
    }
    // Download document (return empty blob)
    const downloadMatch = url.match(/\/api\/documents\/(\d+)\/download$/);
    if (downloadMatch) {
      return Promise.resolve({
        status: 200,
        data: new Blob(['Mock document content'], { type: 'application/octet-stream' }),
      });
    }
    // Download specific version (return empty blob)
    const versionDownloadMatch = url.match(/\/api\/documents\/(\d+)\/versions\/(\d+)\/download$/);
    if (versionDownloadMatch) {
      return Promise.resolve({
        status: 200,
        data: new Blob(['Mock version content'], { type: 'application/octet-stream' }),
      });
    }
    // Search users
    const searchUsersMatch = url.match(/\/api\/users\/search/);
    if (searchUsersMatch) {
      const urlObj = new URL(url, window.location.origin);
      const query = urlObj.searchParams.get('query');
      return Promise.resolve(searchUsers(query));
    }
    // Get folders list
    if (url === '/api/folders') {
      return Promise.resolve({
        status: 200,
        data: []
      });
    }
    // Get folder details
    const folderMatch = url.match(/\/api\/folders\/(\d+)$/);
    if (folderMatch) {
      return Promise.resolve(fetchFolder(folderMatch[1]));
    }
    // Get document details
    const documentMatch = url.match(/\/api\/documents\/(\d+)$/);
    if (documentMatch) {
      return Promise.resolve(fetchDocument(documentMatch[1]));
    }
    // Fallback to original implementation
    return originalGet.call(api, url, config);
  };
  // Override POST requests for document endpoints
  api.post = function(url, data, config) {
    // Create document comment
    const commentMatch = url.match(/\/api\/documents\/(\d+)\/comments$/);
    if (commentMatch) {
      return Promise.resolve(addDocumentComment(commentMatch[1], data));
    }
    // Generate share link
    const shareLinkMatch = url.match(/\/api\/documents\/(\d+)\/share-link$/);
    if (shareLinkMatch) {
      return Promise.resolve(generateShareLink(shareLinkMatch[1]));
    }
    // Share document with users
    const shareMatch = url.match(/\/api\/documents\/(\d+)\/share$/);
    if (shareMatch) {
      return Promise.resolve(shareDocument(shareMatch[1], data));
    }
    // Share multiple documents
    if (url === '/api/documents/batch/share') {
      return Promise.resolve(shareMultipleDocuments(data));
    }
    // Get multiple documents by IDs
    if (url === '/api/documents/batch') {
      return Promise.resolve(fetchMultipleDocuments(data.ids));
    }
    // Create new document
    if (url === '/api/documents') {
      return Promise.resolve(uploadDocument(data));
    }
    // Create new folder
    if (url === '/api/folders') {
      return Promise.resolve(createFolder(data));
    }
    // Fallback to original implementation
    return originalPost.call(api, url, data, config);
  };
  // Override PUT requests for document endpoints
  api.put = function(url, data, config) {
    // Update document
    const documentMatch = url.match(/\/api\/documents\/(\d+)$/);
    if (documentMatch) {
      return Promise.resolve(updateDocument(documentMatch[1], data));
    }
    // Fallback to original implementation
    return originalPut.call(api, url, data, config);
  };
  // Override DELETE requests for document endpoints
  api.delete = function(url, config) {
    // Delete document
    const documentMatch = url.match(/\/api\/documents\/(\d+)$/);
    if (documentMatch) {
      return Promise.resolve(deleteDocument(documentMatch[1]));
    }
    // Fallback to original implementation
    return originalDelete.call(api, url, config);
  };
};