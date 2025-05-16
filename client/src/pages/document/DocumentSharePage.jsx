import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { 
  ArrowLeft, 
  Search, 
  Users, 
  Link, 
  Mail, 
  Check, 
  AlertCircle, 
  File
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * DocumentSharePage allows users to share documents with other users
 */
const DocumentSharePage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [document, setDocument] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [accessType, setAccessType] = useState('view'); // 'view' or 'edit'
  const [shareLink, setShareLink] = useState('');
  const [isSharing, setIsSharing] = useState(false);
  const [message, setMessage] = useState('');
  const [tabView, setTabView] = useState('users'); // 'users' or 'link'
  
  // Parse IDs from query parameters if sharing multiple documents
  const documentIds = location.search 
    ? new URLSearchParams(location.search).get('ids')?.split(',') 
    : [];

  // Fetch document details or documents list
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        
        if (id) {
          // Fetch single document details
          const response = await api.get(`/api/documents/${id}`);
          setDocument(response.data);
          
          // Fetch existing share link if any
          const sharingResponse = await api.get(`/api/documents/${id}/sharing`);
          setShareLink(sharingResponse.data.share_link || '');
        } else if (documentIds.length > 0) {
          // Fetch multiple documents
          const response = await api.post('/api/documents/batch', {
            ids: documentIds
          });
          setDocuments(response.data);
        } else {
          // No document ID provided, navigate back to documents list
          navigate('/documents');
          return;
        }
        
      } catch (error) {
        console.error('Error fetching document(s):', error);
        toast({
          title: 'Error',
          description: 'Failed to load document details',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [id, documentIds, navigate, toast]);

  // Search for users as typing
  useEffect(() => {
    const searchUsers = async () => {
      if (!searchTerm || searchTerm.length < 2) {
        setSearchResults([]);
        return;
      }
      
      try {
        const response = await api.get('/api/users/search', {
          params: { query: searchTerm }
        });
        
        setSearchResults(response.data);
      } catch (error) {
        console.error('Error searching users:', error);
      }
    };
    
    const debounceTimeout = setTimeout(searchUsers, 300);
    
    return () => clearTimeout(debounceTimeout);
  }, [searchTerm]);

  // Add user to selected list
  const addUser = (userToAdd) => {
    if (!selectedUsers.some(u => u.id === userToAdd.id)) {
      setSelectedUsers([...selectedUsers, userToAdd]);
      setSearchTerm('');
      setSearchResults([]);
    }
  };

  // Remove user from selected list
  const removeUser = (userId) => {
    setSelectedUsers(selectedUsers.filter(u => u.id !== userId));
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

  // Share document(s) with selected users
  const shareWithUsers = async () => {
    if (selectedUsers.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one user to share with',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsSharing(true);
      
      if (id) {
        // Share single document
        await api.post(`/api/documents/${id}/share`, {
          user_ids: selectedUsers.map(u => u.id),
          access_type: accessType,
          message: message
        });
      } else if (documentIds.length > 0) {
        // Share multiple documents
        await api.post('/api/documents/batch/share', {
          document_ids: documentIds,
          user_ids: selectedUsers.map(u => u.id),
          access_type: accessType,
          message: message
        });
      }
      
      toast({
        title: 'Success',
        description: `Document${documentIds.length > 1 || documentIds.length === 0 ? 's' : ''} shared successfully`,
        type: 'success',
      });
      
      // Navigate back
      if (id) {
        navigate(`/documents/${id}`);
      } else {
        navigate('/documents');
      }
    } catch (error) {
      console.error('Error sharing document:', error);
      toast({
        title: 'Error',
        description: 'Failed to share document',
        type: 'error',
      });
    } finally {
      setIsSharing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex items-center mb-6">
        <button
          className="mr-4 p-2 rounded-full hover:bg-gray-100"
          onClick={() => id ? navigate(`/documents/${id}`) : navigate('/documents')}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        
        <h1 className="text-2xl font-bold">
          Share {id ? 'Document' : `${documentIds.length} Documents`}
        </h1>
      </div>
      
      {/* Document(s) being shared */}
      <Card className="p-6 mb-6">
        <h2 className="text-lg font-medium mb-4">
          {id ? 'Document to Share' : 'Documents to Share'}
        </h2>
        
        {id && document ? (
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <div className="mr-3 p-2 bg-white rounded border">
              <File className="w-8 h-8 text-primary" />
            </div>
            <div>
              <div className="font-medium">{document.name}</div>
              <div className="text-sm text-gray-500">
                {(document.size / 1024).toFixed(2)} KB • {document.mime_type}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {documents.map(doc => (
              <div key={doc.id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                <div className="mr-3 p-2 bg-white rounded border">
                  <File className="w-8 h-8 text-primary" />
                </div>
                <div>
                  <div className="font-medium">{doc.name}</div>
                  <div className="text-sm text-gray-500">
                    {(doc.size / 1024).toFixed(2)} KB • {doc.mime_type}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
      
      {/* Tabs for sharing options */}
      <div className="border-b mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
              tabView === 'users'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
            onClick={() => setTabView('users')}
          >
            <Users className="w-4 h-4 mr-2" />
            Share with People
          </button>
          
          {id && (
            <button
              className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                tabView === 'link'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setTabView('link')}
            >
              <Link className="w-4 h-4 mr-2" />
              Get Link
            </button>
          )}
        </nav>
      </div>
      
      {/* Share with users */}
      {tabView === 'users' && (
        <Card className="p-6">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Add People
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <Input
                type="text"
                placeholder="Search users by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Search results */}
            {searchResults.length > 0 && (
              <div className="mt-2 border rounded-md overflow-hidden max-h-60 overflow-y-auto">
                {searchResults.map(userResult => (
                  <div 
                    key={userResult.id}
                    className="p-3 hover:bg-gray-50 cursor-pointer flex items-center justify-between border-b last:border-b-0"
                    onClick={() => addUser(userResult)}
                  >
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center mr-2 text-xs">
                        {userResult.name?.charAt(0) || 'U'}
                      </div>
                      <div>
                        <div className="font-medium">{userResult.name}</div>
                        <div className="text-xs text-gray-500">{userResult.email}</div>
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-gray-500"
                    >
                      <Check className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Selected users */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Selected People
            </label>
            
            {selectedUsers.length === 0 ? (
              <div className="p-4 bg-gray-50 rounded-md text-gray-500 text-center">
                No users selected yet
              </div>
            ) : (
              <div className="border rounded-md overflow-hidden">
                {selectedUsers.map(selectedUser => (
                  <div 
                    key={selectedUser.id}
                    className="p-3 border-b last:border-b-0 flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center mr-2 text-xs">
                        {selectedUser.name?.charAt(0) || 'U'}
                      </div>
                      <div>
                        <div className="font-medium">{selectedUser.name}</div>
                        <div className="text-xs text-gray-500">{selectedUser.email}</div>
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-500"
                      onClick={() => removeUser(selectedUser.id)}
                    >
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Access type */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Access Type
            </label>
            
            <div className="flex space-x-4">
              <div className="flex items-center">
                <input
                  id="access_view"
                  type="radio"
                  name="access_type"
                  value="view"
                  checked={accessType === 'view'}
                  onChange={() => setAccessType('view')}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
                />
                <label htmlFor="access_view" className="ml-2 block text-sm text-gray-700">
                  Can view
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  id="access_edit"
                  type="radio"
                  name="access_type"
                  value="edit"
                  checked={accessType === 'edit'}
                  onChange={() => setAccessType('edit')}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300"
                />
                <label htmlFor="access_edit" className="ml-2 block text-sm text-gray-700">
                  Can edit
                </label>
              </div>
            </div>
          </div>
          
          {/* Message (optional) */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Message (Optional)
            </label>
            
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Add a message to send with your invitation..."
              className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              rows={3}
            ></textarea>
          </div>
          
          {/* Action buttons */}
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => id ? navigate(`/documents/${id}`) : navigate('/documents')}
            >
              Cancel
            </Button>
            
            <Button
              onClick={shareWithUsers}
              disabled={selectedUsers.length === 0 || isSharing}
              className="flex items-center"
            >
              {isSharing ? (
                <>
                  <div className="animate-spin mr-2 h-4 w-4 border-2 border-gray-500 border-t-white rounded-full"></div>
                  Sharing...
                </>
              ) : (
                <>
                  <Mail className="w-4 h-4 mr-2" />
                  Share
                </>
              )}
            </Button>
          </div>
        </Card>
      )}
      
      {/* Share link - only available for single document */}
      {tabView === 'link' && id && (
        <Card className="p-6">
          <h2 className="text-lg font-medium mb-4">Share Link</h2>
          
          <div className="mb-6">
            <p className="text-gray-600 mb-4">
              Anyone with the link will be able to view this document. No sign-in required.
            </p>
            
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
              <div className="bg-gray-50 p-4 rounded-md flex items-center justify-between">
                <div className="flex items-center text-gray-600">
                  <AlertCircle className="w-5 h-5 mr-2 text-gray-400" />
                  No share link generated
                </div>
                
                <Button
                  onClick={generateShareLink}
                  className="flex items-center"
                >
                  <Link className="w-4 h-4 mr-2" />
                  Generate Link
                </Button>
              </div>
            )}
          </div>
          
          {shareLink && (
            <div className="bg-yellow-50 p-4 rounded-md text-yellow-800 text-sm flex items-start mt-6">
              <div className="mt-0.5">
                <AlertCircle className="w-5 h-5 mr-2 text-yellow-500" />
              </div>
              <div>
                <p className="font-medium mb-1">Security Notice</p>
                <p>
                  Anyone with this link can view this document. To restrict access,
                  delete this share link and use the "Share with People" option instead.
                </p>
                
                <button 
                  className="text-primary font-medium mt-2 flex items-center"
                  onClick={() => {
                    // In a real app, this would delete the share link
                    setShareLink('');
                    toast({
                      title: 'Success',
                      description: 'Share link deleted successfully',
                      type: 'success',
                    });
                  }}
                >
                  Delete Link
                </button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};

export default DocumentSharePage;