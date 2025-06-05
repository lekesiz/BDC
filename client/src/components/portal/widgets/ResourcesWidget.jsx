import { useNavigate } from 'react-router-dom';
import { 
  FileText, 
  FileCode, 
  FileImage, 
  FileVideo, 
  Package, 
  Download, 
  Folder,
  Search,
  Loader
} from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useState } from 'react';
/**
 * Displays recent and recommended resources for the student
 */
const ResourcesWidget = ({ data, isLoading, error }) => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  // Get icon based on file type
  const getFileIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <FileText className="h-5 w-5 text-red-500" />;
      case 'doc':
      case 'docx':
        return <FileText className="h-5 w-5 text-blue-500" />;
      case 'ppt':
      case 'pptx':
        return <FileText className="h-5 w-5 text-orange-500" />;
      case 'xls':
      case 'xlsx':
        return <FileText className="h-5 w-5 text-green-500" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <FileImage className="h-5 w-5 text-purple-500" />;
      case 'mp4':
      case 'webm':
      case 'avi':
        return <FileVideo className="h-5 w-5 text-indigo-500" />;
      case 'js':
      case 'jsx':
      case 'html':
      case 'css':
      case 'ts':
      case 'tsx':
        return <FileCode className="h-5 w-5 text-yellow-500" />;
      case 'zip':
      case 'rar':
        return <Package className="h-5 w-5 text-gray-500" />;
      default:
        return <FileText className="h-5 w-5 text-gray-500" />;
    }
  };
  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
    else return (bytes / 1073741824).toFixed(1) + ' GB';
  };
  // Filter resources based on search term
  const getFilteredResources = () => {
    if (!data?.resources) return [];
    const resources = data.resources;
    if (!searchTerm.trim()) {
      return resources.slice(0, 5); // Return the first 5 resources if no search term
    }
    const term = searchTerm.toLowerCase();
    return resources
      .filter(resource => (
        resource.name.toLowerCase().includes(term) || 
        resource.description.toLowerCase().includes(term) ||
        resource.category.toLowerCase().includes(term) ||
        resource.moduleName.toLowerCase().includes(term) ||
        resource.fileType.toLowerCase().includes(term)
      ))
      .slice(0, 5); // Limit to 5 results
  };
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">Learning Resources</h2>
        </div>
        <div className="flex justify-center items-center p-12">
          <Loader className="h-8 w-8 text-primary animate-spin" />
        </div>
      </Card>
    );
  }
  if (error) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">Learning Resources</h2>
        </div>
        <div className="p-6 text-center text-red-500">
          Failed to load resources
        </div>
      </Card>
    );
  }
  const filteredResources = getFilteredResources();
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex justify-between items-center border-b">
        <h2 className="text-lg font-medium">Learning Resources</h2>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/portal/resources')}
        >
          Browse All
        </Button>
      </div>
      <div className="p-4">
        <div className="relative mb-4">
          <Input
            type="text"
            placeholder="Search resources..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>
        {filteredResources.length > 0 ? (
          <div className="divide-y">
            {filteredResources.map(resource => (
              <div key={resource.id} className="py-3 px-1 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className="p-2 mr-3">
                      {getFileIcon(resource.fileType)}
                    </div>
                    <div>
                      <h4 className="font-medium text-sm">{resource.name}</h4>
                      <div className="flex items-center text-xs text-gray-500 mt-0.5">
                        <span className="bg-gray-100 px-1.5 py-0.5 rounded mr-2">
                          {resource.fileType.toUpperCase()}
                        </span>
                        <span>{formatFileSize(resource.fileSize)}</span>
                        <span className="mx-1.5">•</span>
                        <span>{resource.moduleName}</span>
                      </div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0"
                    onClick={() => navigate('/portal/resources')}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6">
            <Folder className="h-12 w-12 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">
              {searchTerm.trim() 
                ? 'No resources match your search'
                : 'No resources available'
              }
            </p>
          </div>
        )}
      </div>
      <div className="bg-gray-50 p-4 text-center border-t">
        <Button
          variant="link"
          onClick={() => navigate('/portal/resources')}
        >
          Browse All Resources
        </Button>
      </div>
    </Card>
  );
};
export default ResourcesWidget;