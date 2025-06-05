import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  Star, 
  Trash, 
  Edit, 
  File, 
  Clock, 
  User, 
  Eye, 
  FileText,
  FileImage,
  FileArchive,
  Link,
  MessageSquare,
  History
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { formatDistanceToNow, format } from 'date-fns';
import { tr } from 'date-fns/locale';
/**
 * DocumentDetailPage displays detailed information about a document
 */
const DocumentDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [document, setDocument] = useState(null);
  const [documentVersions, setDocumentVersions] = useState([]);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [tabView, setTabView] = useState('details'); // 'details', 'versions', 'comments', 'sharing'
  const [shareLink, setShareLink] = useState('');
  const [sharedUsers, setSharedUsers] = useState([]);
  const getIconForMimeType = (mimeType) => {
    if (mimeType.startsWith('image/')) {
      return <FileImage className="w-12 h-12 text-blue-500" />;
    } else if (mimeType === 'application/pdf') {
      return <FileText className="w-12 h-12 text-red-500" />;
    } else if (mimeType.includes('zip') || mimeType.includes('compressed')) {
      return <FileArchive className="w-12 h-12 text-yellow-500" />;
    } else if (mimeType.includes('text/') || mimeType.includes('document')) {
      return <FileText className="w-12 h-12 text-green-500" />;
    } else {
      return <File className="w-12 h-12 text-gray-500" />;
    }
  };
  // Fetch document details
  useEffect(() => {
    const fetchDocumentDetails = async () => {
      try {
        setIsLoading(true);
        // Fetch document details
        const documentResponse = await api.get(`/api/documents/${id}`);
        setDocument(documentResponse.data);
        // Fetch document versions
        const versionsResponse = await api.get(`/api/documents/${id}/versions`);
        setDocumentVersions(versionsResponse.data);
        // Fetch document comments
        const commentsResponse = await api.get(`/api/documents/${id}/comments`);
        setComments(commentsResponse.data);
        // Fetch document sharing information
        const sharingResponse = await api.get(`/api/documents/${id}/sharing`);
        setShareLink(sharingResponse.data.share_link || '');
        setSharedUsers(sharingResponse.data.shared_users || []);
      } catch (error) {
        console.error('Error fetching document details:', error);
        toast({
          title: 'Error',
          description: 'Failed to load document details',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchDocumentDetails();
  }, [id]); // Remove toast dependency to prevent infinite loop
  // Toggle document star
  const toggleStar = async () => {
    if (!document) return;
    try {
      const updatedDocument = { ...document, is_starred: !document.is_starred };
      await api.put(`/api/documents/${id}`, {
        is_starred: updatedDocument.is_starred
      });
      setDocument(updatedDocument);
      toast({
        title: 'Success',
        description: updatedDocument.is_starred 
          ? 'Document added to favorites' 
          : 'Document removed from favorites',
        type: 'success',
      });
    } catch (error) {
      console.error('Error updating document:', error);
      toast({
        title: 'Error',
        description: 'Failed to update document',
        type: 'error',
      });
    }
  };
  // Download document
  const downloadDocument = async () => {
    try {
      if (!document) return;
      const response = await api.get(`/api/documents/${id}/download`, {
        responseType: 'blob'
      });
      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.name);
      document.body.appendChild(link);
      link.click();
      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading document:', error);
      toast({
        title: 'Error',
        description: 'Failed to download document',
        type: 'error',
      });
    }
  };
  // Delete document
  const deleteDocument = async () => {
    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }
    try {
      await api.delete(`/api/documents/${id}`);
      toast({
        title: 'Success',
        description: 'Document successfully deleted',
        type: 'success',
      });
      // Navigate back to documents list
      navigate('/documents');
    } catch (error) {
      console.error('Error deleting document:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete document',
        type: 'error',
      });
    }
  };
  // Add new comment
  const addComment = async () => {
    if (!newComment.trim()) return;
    try {
      const response = await api.post(`/api/documents/${id}/comments`, {
        content: newComment
      });
      setComments(prev => [response.data, ...prev]);
      setNewComment('');
      toast({
        title: 'Success',
        description: 'Comment added successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error adding comment:', error);
      toast({
        title: 'Error',
        description: 'Failed to add comment',
        type: 'error',
      });
    }
  };
  // Generate share link
  const generateShareLink = async () => {
    try {
      const response = await api.post(`/api/documents/${id}/share-link`);
      setShareLink(response.data.share_link);
      toast({
        title: 'Success',
        description: 'Share link generated successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error generating share link:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate share link',
        type: 'error',
      });
    }
  };
  // Copy share link to clipboard
  const copyShareLink = () => {
    if (!shareLink) return;
    navigator.clipboard.writeText(shareLink);
    toast({
      title: 'Success',
      description: 'Share link copied to clipboard',
      type: 'success',
    });
  };
  // Download specific version
  const downloadVersion = async (versionId) => {
    try {
      const response = await api.get(`/api/documents/${id}/versions/${versionId}/download`, {
        responseType: 'blob'
      });
      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${document.name} (Version ${versionId})`);
      document.body.appendChild(link);
      link.click();
      // Clean up
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading version:', error);
      toast({
        title: 'Error',
        description: 'Failed to download version',
        type: 'error',
      });
    }
  };
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }
  if (!document) {
    return (
      <div className="container mx-auto py-12 text-center">
        <File className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Document Not Found</h1>
        <p className="text-gray-600 mb-6">The document you're looking for doesn't exist or you don't have permission to view it.</p>
        <Button onClick={() => navigate('/documents')}>
          Back to Documents
        </Button>
      </div>
    );
  }
  return (
    <div className="container mx-auto py-6">
      {/* Header with actions */}
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center">
          <button
            className="mr-4 p-2 rounded-full hover:bg-gray-100"
            onClick={() => navigate('/documents')}
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">{document.name}</h1>
            <p className="text-gray-500">
              {(document.size / 1024).toFixed(2)} KB • Last modified {
                formatDistanceToNow(new Date(document.updated_at), {
                  addSuffix: true,
                  locale: tr
                })
              }
            </p>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={toggleStar}
            className="flex items-center"
          >
            <Star className={`w-4 h-4 mr-1 ${document.is_starred ? 'fill-yellow-500 text-yellow-500' : ''}`} />
            {document.is_starred ? 'Starred' : 'Star'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={downloadDocument}
            className="flex items-center"
          >
            <Download className="w-4 h-4 mr-1" />
            Download
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setTabView('sharing')}
            className="flex items-center"
          >
            <Share2 className="w-4 h-4 mr-1" />
            Share
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate(`/documents/${id}/edit`)}
            className="flex items-center"
          >
            <Edit className="w-4 h-4 mr-1" />
            Edit
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={deleteDocument}
            className="flex items-center text-red-500 hover:bg-red-50"
          >
            <Trash className="w-4 h-4 mr-1" />
            Delete
          </Button>
        </div>
      </div>
      {/* Tabs navigation */}
      <div className="border-b mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              tabView === 'details'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setTabView('details')}
          >
            <Eye className="w-4 h-4 mr-2" />
            Details
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              tabView === 'versions'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setTabView('versions')}
          >
            <History className="w-4 h-4 mr-2" />
            Versions ({documentVersions.length})
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              tabView === 'comments'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setTabView('comments')}
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Comments ({comments.length})
          </button>
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              tabView === 'sharing'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setTabView('sharing')}
          >
            <Share2 className="w-4 h-4 mr-2" />
            Sharing
          </button>
        </nav>
      </div>
      {/* Content based on selected tab */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left column: Document preview/details */}
        <div className="md:col-span-2">
          {tabView === 'details' && (
            <Card className="p-6">
              <div className="flex justify-center items-center border rounded-lg p-8 mb-6 bg-gray-50">
                {document.mime_type.startsWith('image/') ? (
                  <img 
                    src={`/api/documents/${id}/preview`} 
                    alt={document.name}
                    className="max-w-full max-h-[400px] object-contain"
                  />
                ) : (
                  <div className="text-center">
                    {getIconForMimeType(document.mime_type)}
                    <div className="mt-4 text-lg font-medium">{document.name}</div>
                    <div className="text-sm text-gray-500 mt-1">{document.mime_type}</div>
                  </div>
                )}
              </div>
              <h2 className="text-lg font-medium mb-4">Document Details</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3">
                <div>
                  <div className="text-sm font-medium text-gray-500">Name</div>
                  <div>{document.name}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Type</div>
                  <div>{document.mime_type}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Size</div>
                  <div>{(document.size / 1024).toFixed(2)} KB</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Location</div>
                  <div>{document.folder_name || 'Root folder'}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Created</div>
                  <div>
                    {format(new Date(document.created_at), 'PP', { locale: tr })}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Last Modified</div>
                  <div>
                    {format(new Date(document.updated_at), 'PP', { locale: tr })}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Owner</div>
                  <div className="flex items-center">
                    <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center mr-2 text-xs">
                      {document.owner_name?.charAt(0) || 'U'}
                    </div>
                    {document.owner_name || 'You'}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Shared with</div>
                  <div>{sharedUsers.length} people</div>
                </div>
                {document.description && (
                  <div className="col-span-2">
                    <div className="text-sm font-medium text-gray-500">Description</div>
                    <div>{document.description}</div>
                  </div>
                )}
              </div>
            </Card>
          )}
          {tabView === 'versions' && (
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Document Versions</h2>
              {documentVersions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <History className="w-12 h-12 mx-auto text-gray-300 mb-2" />
                  <p>No previous versions found</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {documentVersions.map((version, index) => (
                    <div 
                      key={version.id} 
                      className={`border rounded-lg p-4 ${
                        index === 0 ? 'border-primary bg-primary-50' : ''
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-medium">
                            {index === 0 ? 'Current Version' : `Version ${documentVersions.length - index}`}
                          </div>
                          <div className="text-sm text-gray-500">
                            {formatDistanceToNow(new Date(version.created_at), {
                              addSuffix: true,
                              locale: tr
                            })}
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => downloadVersion(version.id)}
                            className="flex items-center"
                          >
                            <Download className="w-4 h-4 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                      <div className="mt-2 text-sm">
                        <div className="flex items-center text-gray-600">
                          <User className="w-4 h-4 mr-1" />
                          <span>
                            {version.user_name || 'You'} {version.change_type || 'uploaded this file'}
                          </span>
                        </div>
                        {version.size && (
                          <div className="flex items-center text-gray-600 mt-1">
                            <File className="w-4 h-4 mr-1" />
                            <span>{(version.size / 1024).toFixed(2)} KB</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}
          {tabView === 'comments' && (
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Comments</h2>
              <div className="mb-6">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment..."
                  className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  rows={3}
                ></textarea>
                <div className="flex justify-end mt-2">
                  <Button 
                    onClick={addComment}
                    disabled={!newComment.trim()}
                  >
                    Comment
                  </Button>
                </div>
              </div>
              {comments.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <MessageSquare className="w-12 h-12 mx-auto text-gray-300 mb-2" />
                  <p>No comments yet</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {comments.map((comment) => (
                    <div key={comment.id} className="border rounded-lg p-4">
                      <div className="flex items-start mb-2">
                        <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center mr-2 text-xs">
                          {comment.user_name?.charAt(0) || 'U'}
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between items-center">
                            <div className="font-medium">
                              {comment.user_name || 'You'}
                            </div>
                            <div className="text-xs text-gray-500">
                              {formatDistanceToNow(new Date(comment.created_at), {
                                addSuffix: true,
                                locale: tr
                              })}
                            </div>
                          </div>
                          <div className="mt-1">
                            {comment.content}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}
          {tabView === 'sharing' && (
            <Card className="p-6">
              <h2 className="text-lg font-medium mb-4">Sharing</h2>
              {/* Share link section */}
              <div className="mb-6">
                <h3 className="text-md font-medium mb-2">Share Link</h3>
                {shareLink ? (
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={shareLink}
                      readOnly
                      className="flex-1 p-2 border rounded-md bg-gray-50"
                    />
                    <Button
                      variant="outline"
                      onClick={copyShareLink}
                    >
                      Copy
                    </Button>
                  </div>
                ) : (
                  <div className="text-gray-600 mb-2">
                    No share link generated. Create one to share this document with anyone.
                  </div>
                )}
                <div className="mt-2">
                  <Button
                    variant={shareLink ? 'outline' : 'default'}
                    onClick={generateShareLink}
                    className="flex items-center"
                  >
                    <Link className="w-4 h-4 mr-1" />
                    {shareLink ? 'Regenerate Link' : 'Generate Share Link'}
                  </Button>
                </div>
              </div>
              {/* Shared with users section */}
              <div>
                <h3 className="text-md font-medium mb-2">Shared With</h3>
                <div className="border rounded-lg overflow-hidden">
                  {sharedUsers.length === 0 ? (
                    <div className="text-center py-6 text-gray-500">
                      <Users className="w-8 h-8 mx-auto text-gray-300 mb-2" />
                      <p>Not shared with anyone</p>
                    </div>
                  ) : (
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">User</th>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Access</th>
                          <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Shared On</th>
                          <th className="px-4 py-2 text-right text-sm font-medium text-gray-500">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {sharedUsers.map((user) => (
                          <tr key={user.id}>
                            <td className="px-4 py-3">
                              <div className="flex items-center">
                                <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center mr-2 text-xs">
                                  {user.name?.charAt(0) || 'U'}
                                </div>
                                <div>
                                  <div className="font-medium">{user.name}</div>
                                  <div className="text-xs text-gray-500">{user.email}</div>
                                </div>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-sm">
                              {user.access_type === 'edit' ? 'Can edit' : 'Can view'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-500">
                              {format(new Date(user.shared_at), 'PP', { locale: tr })}
                            </td>
                            <td className="px-4 py-3 text-right">
                              <Button
                                variant="ghost"
                                size="sm"
                                className="text-red-500"
                              >
                                <Trash className="w-4 h-4" />
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
                <div className="mt-4">
                  <Button
                    onClick={() => navigate(`/documents/${id}/share`)}
                    className="flex items-center"
                  >
                    <Share2 className="w-4 h-4 mr-1" />
                    Share with People
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
        {/* Right column: Activity feed */}
        <div>
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Activity</h2>
            <div className="space-y-6">
              {/* Create new document event */}
              <div className="flex">
                <div className="mr-4">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <File className="w-4 h-4 text-blue-600" />
                  </div>
                </div>
                <div>
                  <div className="font-medium">Document created</div>
                  <div className="text-sm text-gray-500">
                    {format(new Date(document.created_at), 'PP', { locale: tr })}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {document.owner_name || 'You'} created this document
                  </div>
                </div>
              </div>
              {/* Add version updates */}
              {documentVersions.length > 1 && documentVersions.slice(1).map((version, index) => (
                <div className="flex" key={`activity-${version.id}`}>
                  <div className="mr-4">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Edit className="w-4 h-4 text-green-600" />
                    </div>
                  </div>
                  <div>
                    <div className="font-medium">Document updated</div>
                    <div className="text-sm text-gray-500">
                      {format(new Date(version.created_at), 'PP', { locale: tr })}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {version.user_name || 'You'} updated this document
                    </div>
                  </div>
                </div>
              ))}
              {/* Add recent comments */}
              {comments.slice(0, 3).map((comment) => (
                <div className="flex" key={`activity-comment-${comment.id}`}>
                  <div className="mr-4">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <MessageSquare className="w-4 h-4 text-purple-600" />
                    </div>
                  </div>
                  <div>
                    <div className="font-medium">New comment</div>
                    <div className="text-sm text-gray-500">
                      {format(new Date(comment.created_at), 'PP', { locale: tr })}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {comment.user_name || 'You'} commented: "{comment.content.substring(0, 50)}
                      {comment.content.length > 50 ? '...' : ''}"
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
export default DocumentDetailPage;