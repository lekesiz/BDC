import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  File, 
  Upload, 
  FolderPlus, 
  Search, 
  Filter, 
  Clock, 
  Grid, 
  List as ListIcon,
  Star, 
  Share2, 
  MoreHorizontal, 
  Trash, 
  Download,
  Edit,
  Users,
  FileText,
  FileImage,
  FileArchive,
  Lock
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';
/**
 * DocumentsPage displays a list of documents and provides document management functionality
 */
const DocumentsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user, hasRole } = useAuth();
  // Document management permissions based on user role
  const canUploadDocuments = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  const canCreateFolders = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  const canDeleteDocuments = hasRole(['super_admin', 'tenant_admin']);
  const canEditDocuments = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  const canShareDocuments = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  const canDownloadDocuments = true; // All authenticated users can download
  // Show access restricted message for students
  if (user?.role === 'student') {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="p-8 text-center max-w-md">
          <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Limited Access</h2>
          <p className="text-gray-600 mb-4">
            Document management is restricted for your role. You can only view assigned documents.
          </p>
          <p className="text-sm text-gray-500">
            Current role: <Badge variant="secondary">{user?.role}</Badge>
          </p>
          <Button 
            onClick={() => navigate('/portal')} 
            className="mt-4"
            variant="outline"
          >
            Go to Student Portal
          </Button>
        </Card>
      </div>
    );
  }
  const [isLoading, setIsLoading] = useState(true);
  const [documents, setDocuments] = useState([]);
  const [filteredDocuments, setFilteredDocuments] = useState([]);
  const [view, setView] = useState('grid'); // 'grid' or 'list'
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    type: 'all',
    owner: 'all',
    folder: 'all',
    starred: false
  });
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showNewFolderModal, setShowNewFolderModal] = useState(false);
  const [activeFolderId, setActiveFolderId] = useState(null);
  const [folders, setFolders] = useState([]);
  const [breadcrumbs, setBreadcrumbs] = useState([
    { id: null, name: 'All Documents' }
  ]);
  const getIconForMimeType = (mimeType) => {
    if (!mimeType) return <FileText className="w-8 h-8 text-gray-500" />;
    if (mimeType.startsWith('image/')) {
      return <FileImage className="w-8 h-8 text-blue-500" />;
    } else if (mimeType === 'application/pdf') {
      return <FileText className="w-8 h-8 text-red-500" />;
    } else if (mimeType.includes('zip') || mimeType.includes('compressed')) {
      return <FileArchive className="w-8 h-8 text-yellow-500" />;
    } else if (mimeType.includes('text/') || mimeType.includes('document')) {
      return <FileText className="w-8 h-8 text-green-500" />;
    } else {
      return <File className="w-8 h-8 text-gray-500" />;
    }
  };
  // Fetch documents and folders
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        setIsLoading(true);
        // Call API to get documents for the current folder
        const response = await api.get('/api/documents', {
          params: { folder_id: activeFolderId }
        });
        setDocuments(response.data.documents);
        setFilteredDocuments(response.data.documents);
        setFolders(response.data.folders || []);
        // Update breadcrumbs if a folder is selected
        if (activeFolderId) {
          const folderResponse = await api.get(`/api/folders/${activeFolderId}`);
          const folder = folderResponse.data;
          setBreadcrumbs([
            { id: null, name: 'All Documents' },
            ...(folder.path || []).map(p => ({ id: p.id, name: p.name })),
            { id: folder.id, name: folder.name }
          ]);
        } else {
          setBreadcrumbs([
            { id: null, name: 'All Documents' }
          ]);
        }
      } catch (error) {
        console.error('Error fetching documents:', error);
        toast({
          title: 'Error',
          description: 'Failed to load documents',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchDocuments();
  }, [activeFolderId]); // Remove toast dependency to prevent infinite loop
  // Filter documents based on search term and filters
  useEffect(() => {
    let filtered = [...documents];
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(
        doc => doc.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    // Apply type filter
    if (filters.type !== 'all') {
      filtered = filtered.filter(
        doc => doc.mime_type.includes(filters.type)
      );
    }
    // Apply owner filter
    if (filters.owner !== 'all') {
      filtered = filtered.filter(
        doc => doc.owner_id === parseInt(filters.owner)
      );
    }
    // Apply starred filter
    if (filters.starred) {
      filtered = filtered.filter(doc => doc.is_starred);
    }
    setFilteredDocuments(filtered);
  }, [documents, searchTerm, filters]);
  // Toggle document selection
  const toggleDocumentSelection = (docId) => {
    setSelectedDocuments(prev => {
      if (prev.includes(docId)) {
        return prev.filter(id => id !== docId);
      } else {
        return [...prev, docId];
      }
    });
  };
  // Select all documents
  const selectAllDocuments = () => {
    if (selectedDocuments.length === filteredDocuments.length) {
      setSelectedDocuments([]);
    } else {
      setSelectedDocuments(filteredDocuments.map(doc => doc.id));
    }
  };
  // Navigate to document details
  const navigateToDocument = (documentId) => {
    navigate(`/documents/${documentId}`);
  };
  // Toggle star on document
  const toggleStarDocument = async (documentId, event) => {
    event.stopPropagation();
    try {
      const docToUpdate = documents.find(doc => doc.id === documentId);
      if (!docToUpdate) return;
      const updatedDoc = { ...docToUpdate, is_starred: !docToUpdate.is_starred };
      await api.put(`/api/documents/${documentId}`, {
        is_starred: updatedDoc.is_starred
      });
      setDocuments(prev => 
        prev.map(doc => doc.id === documentId ? updatedDoc : doc)
      );
      toast({
        title: 'Success',
        description: updatedDoc.is_starred 
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
  // Delete document
  const deleteDocument = async (documentId, event) => {
    event.stopPropagation();
    // Check deletion permissions
    if (!canDeleteDocuments) {
      toast({
        title: 'Access Denied',
        description: 'You do not have permission to delete documents',
        type: 'error',
      });
      return;
    }
    // Additional check: users can only delete their own documents unless they're admins
    const document = documents.find(doc => doc.id === documentId);
    if (document && document.owner_id !== user.id && !hasRole(['super_admin', 'tenant_admin'])) {
      toast({
        title: 'Access Denied',
        description: 'You can only delete your own documents',
        type: 'error',
      });
      return;
    }
    // Confirm deletion
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }
    try {
      await api.delete(`/api/documents/${documentId}`);
      setDocuments(prev => 
        prev.filter(doc => doc.id !== documentId)
      );
      setSelectedDocuments(prev => 
        prev.filter(id => id !== documentId)
      );
      toast({
        title: 'Success',
        description: 'Document successfully deleted',
        type: 'success',
      });
    } catch (error) {
      console.error('Error deleting document:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete document',
        type: 'error',
      });
    }
  };
  // Shared selected documents
  const shareSelectedDocuments = async () => {
    // Check sharing permissions
    if (!canShareDocuments) {
      toast({
        title: 'Access Denied',
        description: 'You do not have permission to share documents',
        type: 'error',
      });
      return;
    }
    // Navigate to share page with selected document IDs
    navigate(`/documents/share?ids=${selectedDocuments.join(',')}`);
  };
  // Delete selected documents
  const deleteSelectedDocuments = async () => {
    // Check deletion permissions
    if (!canDeleteDocuments) {
      toast({
        title: 'Access Denied',
        description: 'You do not have permission to delete documents',
        type: 'error',
      });
      return;
    }
    // Additional check: filter out documents user doesn't own unless they're admin
    const allowedDocuments = selectedDocuments.filter(docId => {
      const document = documents.find(doc => doc.id === docId);
      return document && (document.owner_id === user.id || hasRole(['super_admin', 'tenant_admin']));
    });
    if (allowedDocuments.length !== selectedDocuments.length) {
      toast({
        title: 'Warning',
        description: 'Some documents were skipped - you can only delete your own documents',
        type: 'warning',
      });
    }
    if (allowedDocuments.length === 0) {
      toast({
        title: 'Access Denied',
        description: 'You cannot delete any of the selected documents',
        type: 'error',
      });
      return;
    }
    // Confirm deletion
    if (!window.confirm(`Are you sure you want to delete ${allowedDocuments.length} documents?`)) {
      return;
    }
    try {
      await Promise.all(
        allowedDocuments.map(id => api.delete(`/api/documents/${id}`))
      );
      setDocuments(prev => 
        prev.filter(doc => !allowedDocuments.includes(doc.id))
      );
      setSelectedDocuments([]);
      toast({
        title: 'Success',
        description: `${allowedDocuments.length} documents successfully deleted`,
        type: 'success',
      });
    } catch (error) {
      console.error('Error deleting documents:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete selected documents',
        type: 'error',
      });
    }
  };
  // Download document
  const downloadDocument = async (documentId, event) => {
    event.stopPropagation();
    try {
      const document = documents.find(doc => doc.id === documentId);
      if (!document) return;
      const response = await api.get(`/api/documents/${documentId}/download`, {
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
  // Navigate to edit document page
  const editDocument = (documentId, event) => {
    event.stopPropagation();
    // Check edit permissions
    if (!canEditDocuments) {
      toast({
        title: 'Access Denied',
        description: 'You do not have permission to edit documents',
        type: 'error',
      });
      return;
    }
    // Additional check: users can only edit their own documents unless they're admins
    const document = documents.find(doc => doc.id === documentId);
    if (document && document.owner_id !== user.id && !hasRole(['super_admin', 'tenant_admin'])) {
      toast({
        title: 'Access Denied',
        description: 'You can only edit your own documents',
        type: 'error',
      });
      return;
    }
    navigate(`/documents/${documentId}/edit`);
  };
  // Navigate to folder
  const navigateToFolder = (folderId) => {
    setActiveFolderId(folderId);
  };
  // Handle breadcrumb navigation
  const handleBreadcrumbClick = (folderId) => {
    setActiveFolderId(folderId);
  };
  // Handle filter changes
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };
  // Render grid view
  const renderGridView = () => {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {/* Folders first */}
        {folders.map((folder) => (
          <Card 
            key={`folder-${folder.id}`}
            className="p-4 cursor-pointer hover:border-primary transition-colors"
            onClick={() => navigateToFolder(folder.id)}
          >
            <div className="flex items-center space-x-3">
              <div className="bg-gray-100 p-3 rounded-lg">
                <FolderPlus className="w-8 h-8 text-yellow-500" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-gray-900 truncate">
                  {folder.name}
                </h3>
                <p className="text-xs text-gray-500">
                  {folder.document_count || 0} document(s)
                </p>
              </div>
            </div>
          </Card>
        ))}
        {/* Then documents */}
        {filteredDocuments.map((document) => (
          <Card 
            key={`doc-${document.id}`}
            className={`p-4 cursor-pointer hover:border-primary transition-colors ${
              selectedDocuments.includes(document.id) ? 'bg-primary-50 border-primary' : ''
            }`}
            onClick={() => navigateToDocument(document.id)}
          >
            <div className="flex justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="bg-gray-100 p-3 rounded-lg">
                  {getIconForMimeType(document.mime_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-gray-900 truncate">
                    {document.name}
                  </h3>
                  <p className="text-xs text-gray-500">
                    {(document.size / 1024).toFixed(2)} KB • {
                      document.updated_at && !isNaN(new Date(document.updated_at).getTime())
                        ? formatDistanceToNow(new Date(document.updated_at), {
                            addSuffix: true,
                            locale: tr
                          })
                        : 'recently'
                    }
                  </p>
                </div>
              </div>
              <div>
                <input
                  type="checkbox"
                  checked={selectedDocuments.includes(document.id)}
                  onChange={(e) => {
                    e.stopPropagation();
                    toggleDocumentSelection(document.id);
                  }}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
              </div>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex space-x-2">
                <button 
                  className="text-gray-500 hover:text-yellow-500"
                  onClick={(e) => toggleStarDocument(document.id, e)}
                >
                  <Star className={`w-4 h-4 ${document.is_starred ? 'fill-yellow-500 text-yellow-500' : ''}`} />
                </button>
                <button 
                  className="text-gray-500 hover:text-blue-500"
                  onClick={(e) => downloadDocument(document.id, e)}
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
              <div className="flex space-x-2">
                {(canEditDocuments && (document.owner_id === user.id || hasRole(['super_admin', 'tenant_admin']))) && (
                  <button 
                    className="text-gray-500 hover:text-green-500"
                    onClick={(e) => editDocument(document.id, e)}
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                )}
                {(canDeleteDocuments && (document.owner_id === user.id || hasRole(['super_admin', 'tenant_admin']))) && (
                  <button 
                    className="text-gray-500 hover:text-red-500"
                    onClick={(e) => deleteDocument(document.id, e)}
                  >
                    <Trash className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>
          </Card>
        ))}
        {filteredDocuments.length === 0 && folders.length === 0 && !isLoading && (
          <div className="col-span-full py-8 text-center text-gray-500">
            <File className="w-12 h-12 mx-auto text-gray-300 mb-2" />
            <h3 className="text-lg font-medium">No documents found</h3>
            <p>Upload documents or create a new folder to get started.</p>
          </div>
        )}
      </div>
    );
  };
  // Render list view
  const renderListView = () => {
    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="text-left border-b">
              <th className="px-4 py-3 font-medium">
                <input
                  type="checkbox"
                  checked={selectedDocuments.length > 0 && selectedDocuments.length === filteredDocuments.length}
                  onChange={selectAllDocuments}
                  className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                />
              </th>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Size</th>
              <th className="px-4 py-3 font-medium">Owner</th>
              <th className="px-4 py-3 font-medium">Modified</th>
              <th className="px-4 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {/* Folders first */}
            {folders.map((folder) => (
              <tr 
                key={`folder-${folder.id}`} 
                className="border-b hover:bg-gray-50 cursor-pointer"
                onClick={() => navigateToFolder(folder.id)}
              >
                <td className="px-4 py-3">
                  {/* Folders don't get selected */}
                  <div className="w-4"></div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center">
                    <FolderPlus className="w-5 h-5 text-yellow-500 mr-2" />
                    <span className="font-medium">{folder.name}</span>
                  </div>
                </td>
                <td className="px-4 py-3">—</td>
                <td className="px-4 py-3">
                  {folder.owner_name || 'You'}
                </td>
                <td className="px-4 py-3 text-gray-500 text-sm">
                  {folder.updated_at && !isNaN(new Date(folder.updated_at).getTime())
                    ? formatDistanceToNow(new Date(folder.updated_at), {
                        addSuffix: true,
                        locale: tr
                      })
                    : '—'
                  }
                </td>
                <td className="px-4 py-3">
                  {/* Folder actions go here if needed */}
                </td>
              </tr>
            ))}
            {/* Then documents */}
            {filteredDocuments.map((document) => (
              <tr 
                key={`doc-${document.id}`} 
                className={`border-b hover:bg-gray-50 cursor-pointer ${
                  selectedDocuments.includes(document.id) ? 'bg-primary-50' : ''
                }`}
                onClick={() => navigateToDocument(document.id)}
              >
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedDocuments.includes(document.id)}
                    onChange={(e) => {
                      e.stopPropagation();
                      toggleDocumentSelection(document.id);
                    }}
                    className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  />
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center">
                    {getIconForMimeType(document.mime_type)}
                    <div className="ml-2">
                      <div className="font-medium">{document.name}</div>
                      <div className="text-xs text-gray-500">
                        {document.mime_type}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm">
                  {(document.size / 1024).toFixed(2)} KB
                </td>
                <td className="px-4 py-3">
                  {document.owner_name || 'You'}
                </td>
                <td className="px-4 py-3 text-gray-500 text-sm">
                  {document.updated_at && !isNaN(new Date(document.updated_at).getTime())
                    ? formatDistanceToNow(new Date(document.updated_at), {
                        addSuffix: true,
                        locale: tr
                      })
                    : 'recently'
                  }
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex justify-end space-x-2">
                    <button 
                      className="text-gray-500 hover:text-yellow-500"
                      onClick={(e) => toggleStarDocument(document.id, e)}
                    >
                      <Star className={`w-4 h-4 ${document.is_starred ? 'fill-yellow-500 text-yellow-500' : ''}`} />
                    </button>
                    {canDownloadDocuments && (
                      <button 
                        className="text-gray-500 hover:text-blue-500"
                        onClick={(e) => downloadDocument(document.id, e)}
                      >
                        <Download className="w-4 h-4" />
                      </button>
                    )}
                    {(canEditDocuments && (document.owner_id === user.id || hasRole(['super_admin', 'tenant_admin']))) && (
                      <button 
                        className="text-gray-500 hover:text-green-500"
                        onClick={(e) => editDocument(document.id, e)}
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                    )}
                    {(canDeleteDocuments && (document.owner_id === user.id || hasRole(['super_admin', 'tenant_admin']))) && (
                      <button 
                        className="text-gray-500 hover:text-red-500"
                        onClick={(e) => deleteDocument(document.id, e)}
                      >
                        <Trash className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredDocuments.length === 0 && folders.length === 0 && !isLoading && (
          <div className="py-8 text-center text-gray-500">
            <File className="w-12 h-12 mx-auto text-gray-300 mb-2" />
            <h3 className="text-lg font-medium">No documents found</h3>
            <p>Upload documents or create a new folder to get started.</p>
          </div>
        )}
      </div>
    );
  };
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Documents</h1>
        <div className="flex space-x-2">
          {canUploadDocuments && (
            <Button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center"
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload
            </Button>
          )}
          {canCreateFolders && (
            <Button
              variant="outline"
              onClick={() => setShowNewFolderModal(true)}
              className="flex items-center"
            >
              <FolderPlus className="w-4 h-4 mr-2" />
              New Folder
            </Button>
          )}
        </div>
      </div>
      <div className="bg-white shadow-sm mb-6 p-4 rounded-lg border">
        <div className="flex items-center mb-2 overflow-x-auto whitespace-nowrap pb-2">
          {breadcrumbs.map((crumb, index) => (
            <div key={index} className="flex items-center">
              {index > 0 && <span className="mx-2 text-gray-400">/</span>}
              <button
                className={`text-sm ${
                  index === breadcrumbs.length - 1
                    ? 'font-medium text-gray-900'
                    : 'text-gray-600 hover:text-primary'
                }`}
                onClick={() => handleBreadcrumbClick(crumb.id)}
              >
                {crumb.name}
              </button>
            </div>
          ))}
        </div>
        <div className="flex flex-col md:flex-row justify-between space-y-4 md:space-y-0">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <Input
              type="text"
              placeholder="Search documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex space-x-2">
            <div>
              <select
                value={filters.type}
                onChange={(e) => handleFilterChange('type', e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary text-sm"
              >
                <option value="all">All Types</option>
                <option value="image">Images</option>
                <option value="pdf">PDFs</option>
                <option value="document">Documents</option>
                <option value="spreadsheet">Spreadsheets</option>
              </select>
            </div>
            <div>
              <select
                value={filters.owner}
                onChange={(e) => handleFilterChange('owner', e.target.value)}
                className="rounded-md border-gray-300 shadow-sm focus:border-primary focus:ring-primary text-sm"
              >
                <option value="all">All Owners</option>
                <option value={user?.id}>My Documents</option>
              </select>
            </div>
            <div className="flex items-center space-x-2">
              <input
                id="starred_filter"
                type="checkbox"
                checked={filters.starred}
                onChange={(e) => handleFilterChange('starred', e.target.checked)}
                className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
              />
              <label htmlFor="starred_filter" className="text-sm">
                Starred
              </label>
            </div>
            <div className="flex border border-gray-300 rounded-md overflow-hidden">
              <Button
                variant={view === 'grid' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setView('grid')}
                className="rounded-none border-0"
              >
                <Grid className="w-4 h-4" />
              </Button>
              <Button
                variant={view === 'list' ? 'default' : 'ghost'}
                size="sm"
                onClick={() => setView('list')}
                className="rounded-none border-0"
              >
                <ListIcon className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
      {/* Selected documents actions */}
      {selectedDocuments.length > 0 && (
        <div className="bg-primary-50 p-3 rounded-lg shadow mb-4 flex items-center justify-between">
          <div>
            <span className="font-medium mr-2">{selectedDocuments.length} document(s) selected</span>
            <button
              className="text-primary text-sm underline"
              onClick={() => setSelectedDocuments([])}
            >
              Clear selection
            </button>
          </div>
          <div className="flex space-x-2">
            {canShareDocuments && (
              <Button
                variant="outline"
                size="sm"
                onClick={shareSelectedDocuments}
                className="flex items-center"
              >
                <Share2 className="w-4 h-4 mr-1" />
                Share
              </Button>
            )}
            {canDeleteDocuments && (
              <Button
                variant="outline"
                size="sm"
                onClick={deleteSelectedDocuments}
                className="flex items-center text-red-500"
              >
                <Trash className="w-4 h-4 mr-1" />
                Delete
              </Button>
            )}
          </div>
        </div>
      )}
      {/* Document list */}
      <Card className="p-6">
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : (
          <>
            {view === 'grid' ? renderGridView() : renderListView()}
          </>
        )}
      </Card>
      {/* Upload Document Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" onClick={() => setShowUploadModal(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Upload Document
                </h3>
                <div className="mt-2">
                  <Button
                    variant="primary"
                    onClick={() => {
                      navigate('/documents/upload');
                      setShowUploadModal(false);
                    }}
                    className="w-full"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Choose Files to Upload
                  </Button>
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  variant="ghost"
                  onClick={() => setShowUploadModal(false)}
                  className="mt-3 w-full sm:mt-0 sm:ml-3 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* New Folder Modal */}
      {showNewFolderModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" onClick={() => setShowNewFolderModal(false)}>
              <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
                  Create New Folder
                </h3>
                <div className="mt-2">
                  <Input
                    type="text"
                    placeholder="Folder name"
                    id="folderName"
                    className="w-full"
                  />
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <Button
                  variant="primary"
                  onClick={async () => {
                    const folderName = document.getElementById('folderName').value;
                    if (folderName.trim()) {
                      try {
                        await api.post('/api/folders', {
                          name: folderName,
                          parent_id: activeFolderId
                        });
                        toast({
                          title: 'Success',
                          description: 'Folder created successfully',
                          type: 'success',
                        });
                        setShowNewFolderModal(false);
                        // Refresh the document list
                        const response = await api.get('/api/documents', {
                          params: { folder_id: activeFolderId }
                        });
                        setDocuments(response.data.documents);
                        setFolders(response.data.folders || []);
                      } catch (error) {
                        toast({
                          title: 'Error',
                          description: 'Failed to create folder',
                          type: 'error',
                        });
                      }
                    }
                  }}
                  className="w-full sm:w-auto"
                >
                  Create Folder
                </Button>
                <Button
                  variant="ghost"
                  onClick={() => setShowNewFolderModal(false)}
                  className="mt-3 w-full sm:mt-0 sm:mr-3 sm:w-auto"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default DocumentsPage;