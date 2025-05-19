import { useState, useRef, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  ArrowLeft, 
  Upload, 
  File, 
  Folder, 
  X, 
  AlertCircle,
  Check,
  FileText,
  FileImage,
  FileArchive,
  FolderPlus
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';

/**
 * DocumentUploadPage allows users to upload new documents or new versions of existing documents
 */
const DocumentUploadPage = () => {
  const { id } = useParams(); // document id if updating an existing document
  const navigate = useNavigate();
  const { toast } = useToast();
  const fileInputRef = useRef(null);
  const [isLoading, setIsLoading] = useState(id ? true : false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [documentName, setDocumentName] = useState('');
  const [documentDescription, setDocumentDescription] = useState('');
  const [folders, setFolders] = useState([]);
  const [selectedFolderId, setSelectedFolderId] = useState(null);
  const [showFolderSelector, setShowFolderSelector] = useState(false);
  const [documentToUpdate, setDocumentToUpdate] = useState(null);
  
  const getIconForMimeType = (mimeType) => {
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

  // If updating an existing document, fetch its details
  useEffect(() => {
    const fetchDocumentDetails = async () => {
      if (!id) return;
      
      try {
        const response = await api.get(`/api/documents/${id}`);
        setDocumentToUpdate(response.data);
        setDocumentName(response.data.name);
        setDocumentDescription(response.data.description || '');
        setSelectedFolderId(response.data.folder_id);
      } catch (error) {
        console.error('Error fetching document details:', error);
        toast({
          title: 'Error',
          description: 'Failed to load document details',
          type: 'error',
        });
        navigate('/documents');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDocumentDetails();
  }, [id, navigate]); // Remove toast dependency to prevent infinite loop

  // Fetch available folders
  useEffect(() => {
    const fetchFolders = async () => {
      try {
        const response = await api.get('/api/folders');
        setFolders(response.data);
      } catch (error) {
        console.error('Error fetching folders:', error);
        toast({
          title: 'Error',
          description: 'Failed to load folders',
          type: 'error',
        });
      }
    };
    
    fetchFolders();
  }, []); // Remove toast dependency to prevent infinite loop

  // Handle file selection
  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    
    if (id && files.length > 1) {
      toast({
        title: 'Error',
        description: 'You can only upload one file when updating a document',
        type: 'error',
      });
      return;
    }
    
    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    const oversizedFiles = files.filter(file => file.size > maxSize);
    
    if (oversizedFiles.length > 0) {
      toast({
        title: 'Error',
        description: `Some files exceed the maximum size of 50MB: ${oversizedFiles.map(f => f.name).join(', ')}`,
        type: 'error',
      });
      
      // Filter out oversized files
      const validFiles = files.filter(file => file.size <= maxSize);
      setSelectedFiles(validFiles);
    } else {
      setSelectedFiles(files);
      
      // If uploading a single file and no name is set, use the file name
      if (files.length === 1 && (!documentName || documentName === '')) {
        // Remove file extension
        const nameWithoutExtension = files[0].name.replace(/\.[^/.]+$/, "");
        setDocumentName(nameWithoutExtension);
      }
    }
  };

  // Handle drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('border-primary');
  };
  
  const handleDragLeave = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-primary');
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-primary');
    
    const files = Array.from(e.dataTransfer.files);
    
    if (id && files.length > 1) {
      toast({
        title: 'Error',
        description: 'You can only upload one file when updating a document',
        type: 'error',
      });
      return;
    }
    
    // Validate file size (max 50MB)
    const maxSize = 50 * 1024 * 1024; // 50MB in bytes
    const oversizedFiles = files.filter(file => file.size > maxSize);
    
    if (oversizedFiles.length > 0) {
      toast({
        title: 'Error',
        description: `Some files exceed the maximum size of 50MB: ${oversizedFiles.map(f => f.name).join(', ')}`,
        type: 'error',
      });
      
      // Filter out oversized files
      const validFiles = files.filter(file => file.size <= maxSize);
      setSelectedFiles(validFiles);
    } else {
      setSelectedFiles(files);
      
      // If uploading a single file and no name is set, use the file name
      if (files.length === 1 && (!documentName || documentName === '')) {
        // Remove file extension
        const nameWithoutExtension = files[0].name.replace(/\.[^/.]+$/, "");
        setDocumentName(nameWithoutExtension);
      }
    }
  };

  // Remove file from selected files
  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  // Upload documents
  const uploadDocuments = async () => {
    if (selectedFiles.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one file to upload',
        type: 'error',
      });
      return;
    }
    
    if (!documentName.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a document name',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsUploading(true);
      
      if (id) {
        // Updating an existing document
        const formData = new FormData();
        formData.append('file', selectedFiles[0]);
        formData.append('name', documentName);
        formData.append('description', documentDescription);
        if (selectedFolderId) {
          formData.append('folder_id', selectedFolderId);
        }
        
        await api.put(`/api/documents/${id}`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percentCompleted);
          }
        });
        
        toast({
          title: 'Success',
          description: 'Document updated successfully',
          type: 'success',
        });
        
        navigate(`/documents/${id}`);
      } else {
        // Uploading new documents
        if (selectedFiles.length === 1) {
          // Single file upload
          const formData = new FormData();
          formData.append('file', selectedFiles[0]);
          formData.append('name', documentName);
          formData.append('description', documentDescription);
          if (selectedFolderId) {
            formData.append('folder_id', selectedFolderId);
          }
          
          const response = await api.post('/api/documents', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(percentCompleted);
            }
          });
          
          toast({
            title: 'Success',
            description: 'Document uploaded successfully',
            type: 'success',
          });
          
          navigate(`/documents/${response.data.id}`);
        } else {
          // Multiple files upload
          const formData = new FormData();
          
          selectedFiles.forEach(file => {
            formData.append('files', file);
          });
          
          if (selectedFolderId) {
            formData.append('folder_id', selectedFolderId);
          }
          
          await api.post('/api/documents/batch', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploadProgress(percentCompleted);
            }
          });
          
          toast({
            title: 'Success',
            description: `${selectedFiles.length} documents uploaded successfully`,
            type: 'success',
          });
          
          navigate('/documents');
        }
      }
    } catch (error) {
      console.error('Error uploading document(s):', error);
      toast({
        title: 'Error',
        description: 'Failed to upload document(s)',
        type: 'error',
      });
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  // Create a new folder
  const createNewFolder = async (folderName) => {
    if (!folderName.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a folder name',
        type: 'error',
      });
      return;
    }
    
    try {
      const response = await api.post('/api/folders', {
        name: folderName,
        parent_id: selectedFolderId
      });
      
      setFolders(prev => [...prev, response.data]);
      setSelectedFolderId(response.data.id);
      setShowFolderSelector(false);
      
      toast({
        title: 'Success',
        description: 'Folder created successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error creating folder:', error);
      toast({
        title: 'Error',
        description: 'Failed to create folder',
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

  return (
    <div className="container mx-auto py-6">
      {/* Header */}
      <div className="flex items-center mb-6">
        <button
          className="mr-4 p-2 rounded-full hover:bg-gray-100"
          onClick={() => navigate('/documents')}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        
        <h1 className="text-2xl font-bold">
          {id ? 'Update Document' : 'Upload Documents'}
        </h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left column: Upload area */}
        <div className="md:col-span-2">
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">
              {id ? 'Upload New Version' : 'Upload Files'}
            </h2>
            
            {id && documentToUpdate && (
              <div className="mb-6 bg-blue-50 p-4 rounded-lg">
                <div className="flex items-start">
                  <div className="mr-3 mt-1">
                    <AlertCircle className="w-5 h-5 text-blue-500" />
                  </div>
                  <div>
                    <h3 className="font-medium text-blue-700">Updating existing document</h3>
                    <p className="text-sm text-blue-600 mt-1">
                      You are uploading a new version of "{documentToUpdate.name}".
                      The original file will be preserved in the version history.
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            <div 
              className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 transition-colors"
              onClick={() => fileInputRef.current.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                multiple={!id} // Allow multiple files only when not updating an existing document
                className="hidden"
              />
              
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              
              <h3 className="text-lg font-medium text-gray-900 mb-1">
                {id ? 'Select a file to update' : 'Drag and drop files here'}
              </h3>
              
              <p className="text-gray-500 mb-3">
                {id ? 'or click to browse' : 'or click to browse your computer'}
              </p>
              
              <p className="text-xs text-gray-400">
                Maximum file size: 50MB
              </p>
            </div>
            
            {/* Selected files */}
            {selectedFiles.length > 0 && (
              <div className="mt-6">
                <h3 className="text-md font-medium mb-2">
                  Selected Files ({selectedFiles.length})
                </h3>
                
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center">
                        {getIconForMimeType(file.type)}
                        <div className="ml-3">
                          <div className="font-medium">{file.name}</div>
                          <div className="text-xs text-gray-500">
                            {(file.size / 1024).toFixed(2)} KB • {file.type || 'Unknown type'}
                          </div>
                        </div>
                      </div>
                      
                      <button
                        className="text-gray-500 hover:text-red-500"
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFile(index);
                        }}
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Upload progress */}
            {isUploading && (
              <div className="mt-6">
                <div className="text-sm font-medium text-gray-700 mb-1">
                  Uploading... {uploadProgress}%
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-primary h-2.5 rounded-full" 
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
              </div>
            )}
          </Card>
        </div>
        
        {/* Right column: Document details */}
        <div>
          <Card className="p-6">
            <h2 className="text-lg font-medium mb-4">Document Details</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Document Name{selectedFiles.length > 1 ? ' (applies to first file only)' : ''}
                </label>
                <Input
                  type="text"
                  value={documentName}
                  onChange={(e) => setDocumentName(e.target.value)}
                  placeholder="Enter document name"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description (Optional)
                </label>
                <textarea
                  value={documentDescription}
                  onChange={(e) => setDocumentDescription(e.target.value)}
                  placeholder="Enter document description"
                  className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  rows={3}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Folder (Optional)
                </label>
                
                {showFolderSelector ? (
                  <div className="border rounded-lg p-4">
                    <div className="mb-4">
                      <Input
                        type="text"
                        placeholder="New folder name..."
                        className="mb-2"
                        id="new_folder_name"
                      />
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setShowFolderSelector(false)}
                        >
                          Cancel
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => {
                            const input = document.getElementById('new_folder_name');
                            createNewFolder(input.value);
                          }}
                        >
                          Create
                        </Button>
                      </div>
                    </div>
                    
                    <div className="max-h-40 overflow-y-auto">
                      <div 
                        className={`p-2 rounded cursor-pointer ${selectedFolderId === null ? 'bg-primary-50 border border-primary' : 'hover:bg-gray-50'}`}
                        onClick={() => {
                          setSelectedFolderId(null);
                          setShowFolderSelector(false);
                        }}
                      >
                        <div className="flex items-center">
                          <Folder className="w-5 h-5 text-gray-400 mr-2" />
                          <span>Root folder</span>
                        </div>
                      </div>
                      
                      {folders.map(folder => (
                        <div 
                          key={folder.id}
                          className={`p-2 rounded cursor-pointer ${selectedFolderId === folder.id ? 'bg-primary-50 border border-primary' : 'hover:bg-gray-50'}`}
                          onClick={() => {
                            setSelectedFolderId(folder.id);
                            setShowFolderSelector(false);
                          }}
                        >
                          <div className="flex items-center">
                            <Folder className="w-5 h-5 text-gray-400 mr-2" />
                            <span>{folder.name}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div
                    className="flex items-center justify-between p-3 border rounded-lg cursor-pointer hover:border-primary"
                    onClick={() => setShowFolderSelector(true)}
                  >
                    <div className="flex items-center">
                      <Folder className="w-5 h-5 text-gray-400 mr-2" />
                      <span>
                        {selectedFolderId 
                          ? folders.find(f => f.id === selectedFolderId)?.name || 'Selected folder' 
                          : 'Root folder'}
                      </span>
                    </div>
                    <FolderPlus className="w-5 h-5 text-gray-400" />
                  </div>
                )}
              </div>
            </div>
            
            <div className="mt-6">
              <Button
                onClick={uploadDocuments}
                disabled={selectedFiles.length === 0 || isUploading || !documentName.trim()}
                className="w-full flex items-center justify-center"
              >
                {isUploading ? (
                  <>
                    <div className="animate-spin mr-2 h-4 w-4 border-2 border-gray-500 border-t-white rounded-full"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4 mr-2" />
                    {id ? 'Update Document' : 'Upload Document' + (selectedFiles.length > 1 ? 's' : '')}
                  </>
                )}
              </Button>
            </div>
          </Card>
          
          {!id && (
            <div className="mt-4 bg-blue-50 p-4 rounded-lg text-blue-800 text-sm">
              <div className="flex items-start">
                <Check className="w-5 h-5 text-blue-500 mr-2 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium mb-1">Multiple File Upload</p>
                  <p>
                    You can upload multiple files at once. Document details will be applied to the first file only.
                    Other files will use their original filenames.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentUploadPage;