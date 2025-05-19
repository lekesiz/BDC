import { useState, useEffect } from 'react';
import { 
  FileText, 
  FileCode, 
  FileImage, 
  FileVideo, 
  Package, 
  Download, 
  Search, 
  Filter, 
  Folder, 
  BookOpen, 
  Loader 
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';

/**
 * PortalResourcesPage provides access to learning materials and resources
 * for beneficiary students
 */
const PortalResourcesPage = () => {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(true);
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Fetch resources data
  useEffect(() => {
    const fetchResources = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/resources');
        const resourceData = response.data;
        
        // Handle different response structures
        const resourcesList = resourceData.resources || resourceData.documents || resourceData.data || [];
        const categoriesList = resourceData.categories || [];
        
        setResources(resourcesList);
        setFilteredResources(resourcesList);
        setCategories(categoriesList);
      } catch (error) {
        console.error('Error fetching resources:', error);
        toast({
          title: 'Error',
          description: 'Failed to load resources',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchResources();
  }, []); // Remove toast dependency to prevent infinite loop
  
  // Filter resources based on category and search term
  useEffect(() => {
    if (!Array.isArray(resources)) {
      setFilteredResources([]);
      return;
    }
    
    let result = resources;
    
    // Filter by category
    if (selectedCategory !== 'all') {
      result = result.filter(resource => resource.category === selectedCategory);
    }
    
    // Filter by search term
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      result = result.filter(resource => 
        (resource.name && resource.name.toLowerCase().includes(search)) || 
        (resource.description && resource.description.toLowerCase().includes(search))
      );
    }
    
    setFilteredResources(result);
  }, [selectedCategory, searchTerm, resources]);
  
  // Get icon based on file type
  const getFileIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-6 w-6 text-red-500" />;
      case 'doc':
      case 'docx':
        return <FileText className="h-6 w-6 text-blue-500" />;
      case 'ppt':
      case 'pptx':
        return <FileText className="h-6 w-6 text-orange-500" />;
      case 'xls':
      case 'xlsx':
        return <FileText className="h-6 w-6 text-green-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <FileImage className="h-6 w-6 text-purple-500" />;
      case 'mp4':
      case 'webm':
      case 'avi':
        return <FileVideo className="h-6 w-6 text-indigo-500" />;
      case 'js':
      case 'jsx':
      case 'html':
      case 'css':
      case 'ts':
      case 'tsx':
        return <FileCode className="h-6 w-6 text-yellow-500" />;
      case 'zip':
      case 'rar':
        return <Package className="h-6 w-6 text-gray-500" />;
      default:
        return <FileText className="h-6 w-6 text-gray-500" />;
    }
  };
  
  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
    else return (bytes / 1073741824).toFixed(1) + ' GB';
  };
  
  // Handle resource download
  const handleDownload = async (resourceId) => {
    try {
      // In a real implementation, this would trigger a file download
      await api.get(`/api/portal/resources/${resourceId}/download`);
      
      toast({
        title: 'Success',
        description: 'Resource downloaded successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error downloading resource:', error);
      toast({
        title: 'Error',
        description: 'Failed to download resource',
        type: 'error',
      });
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-6">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">Learning Resources</h1>
        <p className="text-gray-600">
          Access all learning materials, reference guides, and supplementary resources for your program
        </p>
      </div>
      
      {/* Search and filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Input
            type="text"
            placeholder="Search resources..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>
        
        <div className="flex space-x-2">
          <Button
            variant={selectedCategory === 'all' ? 'default' : 'outline'}
            onClick={() => setSelectedCategory('all')}
          >
            All
          </Button>
          
          {categories.map(category => (
            <Button
              key={category.id}
              variant={selectedCategory === category.name ? 'default' : 'outline'}
              onClick={() => setSelectedCategory(category.name)}
            >
              {category.name}
            </Button>
          ))}
        </div>
      </div>
      
      {/* Categories grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
        {categories.map(category => (
          <Card 
            key={category.id}
            className={`p-4 cursor-pointer transition-colors hover:bg-gray-50 ${
              selectedCategory === category.name ? 'ring-2 ring-primary' : ''
            }`}
            onClick={() => setSelectedCategory(category.name)}
          >
            <div className="flex items-center">
              <div className={`p-3 rounded-lg mr-3 ${category.colorClass}`}>
                {category.icon === 'Folder' && <Folder className="h-5 w-5 text-white" />}
                {category.icon === 'BookOpen' && <BookOpen className="h-5 w-5 text-white" />}
                {category.icon === 'FileCode' && <FileCode className="h-5 w-5 text-white" />}
                {category.icon === 'FileText' && <FileText className="h-5 w-5 text-white" />}
              </div>
              <div>
                <h3 className="font-medium">{category.name}</h3>
                <p className="text-sm text-gray-500">{category.count} resources</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
      
      {/* Resources list */}
      {filteredResources.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-1">No resources found</h3>
          <p className="text-gray-500">
            Try adjusting your search or filter to find what you're looking for
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Resource groups by module */}
          {Object.entries(
            filteredResources.reduce((acc, resource) => {
              if (!acc[resource.moduleName]) {
                acc[resource.moduleName] = [];
              }
              acc[resource.moduleName].push(resource);
              return acc;
            }, {})
          ).map(([moduleName, moduleResources]) => (
            <div key={moduleName} className="mb-8">
              <h2 className="text-lg font-medium mb-4">{moduleName}</h2>
              <Card className="overflow-hidden">
                <div className="divide-y">
                  {moduleResources.map(resource => (
                    <div key={resource.id} className="p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="p-2 mr-4">
                            {getFileIcon(resource.fileType)}
                          </div>
                          <div>
                            <h3 className="font-medium">{resource.name}</h3>
                            <p className="text-sm text-gray-500 mb-1">{resource.description}</p>
                            <div className="flex items-center text-xs text-gray-500">
                              <span className="bg-gray-100 px-2 py-0.5 rounded mr-2">
                                {resource.fileType.toUpperCase()}
                              </span>
                              <span>{formatFileSize(resource.fileSize)}</span>
                              {resource.uploadDate && (
                                <span className="ml-2">
                                  Added {new Date(resource.uploadDate).toLocaleDateString()}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline"
                          className="ml-4"
                          onClick={() => handleDownload(resource.id)}
                        >
                          <Download className="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PortalResourcesPage;