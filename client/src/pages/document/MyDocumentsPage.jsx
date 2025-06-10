// TODO: i18n - processed
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Download, Eye, Calendar, FolderOpen, Upload } from 'lucide-react';
import api from '@/lib/api';
import { API_ENDPOINTS } from '@/lib/constants';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast';
import { formatDate, formatBytes } from '@/lib/utils';
/**
 * MyDocumentsPage displays documents for student users
 */import { useTranslation } from "react-i18next";
const MyDocumentsPage = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [documents, setDocuments] = useState([]);
  const [folders, setFolders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedFolder, setSelectedFolder] = useState(null);
  // Fetch student's documents
  useEffect(() => {
    const fetchMyDocuments = async () => {
      try {
        setIsLoading(true);
        // Fetch documents
        const docsResponse = await api.get(API_ENDPOINTS.DOCUMENTS.BASE, {
          params: {
            folder_id: selectedFolder,
            my_documents: true // This flag ensures we only get documents accessible to the student
          }
        });
        setDocuments(docsResponse.data.items || []);
        // Fetch folders if not already loaded
        if (!selectedFolder && folders.length === 0) {
          const foldersResponse = await api.get(API_ENDPOINTS.DOCUMENTS.FOLDERS || '/api/folders');
          setFolders(foldersResponse.data || []);
        }
      } catch (error) {
        console.error('Error fetching documents:', error);
        toast({
          title: 'Error',
          description: 'Failed to load your documents',
          type: 'error'
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchMyDocuments();
  }, [selectedFolder]); // Remove toast dependency to prevent infinite loop
  // View document
  const handleViewDocument = (document) => {
    navigate(`/documents/${document.id}`);
  };
  // Download document
  const handleDownloadDocument = async (document) => {
    try {
      const response = await api.get(`${API_ENDPOINTS.DOCUMENTS.BASE}/${document.id}/download`, {
        responseType: 'blob'
      });
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast({
        title: 'Success',
        description: 'Document downloaded successfully',
        type: 'success'
      });
    } catch (error) {
      console.error('Error downloading document:', error);
      toast({
        title: 'Error',
        description: 'Failed to download document',
        type: 'error'
      });
    }
  };
  // Get document type icon
  const getDocumentIcon = (type) => {
    // You can customize this based on actual file types
    return <FileText className="h-10 w-10 text-blue-500" />;
  };
  // Get document type color
  const getTypeColor = (type) => {
    switch (type?.toLowerCase()) {
      case 'pdf':
        return 'error';
      case 'doc':
      case 'docx':
        return 'primary';
      case 'xls':
      case 'xlsx':
        return 'success';
      case 'ppt':
      case 'pptx':
        return 'warning';
      default:
        return 'secondary';
    }
  };
  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
        </div>
      </div>);

  }
  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{t("pages.my_documents")}</h1>
        <p className="text-gray-600 mt-1">{t("pages.access_your_study_materials_and_documents")}</p>
      </div>
      {/* Folders */}
      {folders.length > 0 &&
      <div className="mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-3">{t("pages.folders")}</h2>
          <div className="flex flex-wrap gap-3">
            <Button
            variant={selectedFolder === null ? 'primary' : 'outline'}
            onClick={() => setSelectedFolder(null)}>

              <FolderOpen className="h-4 w-4 mr-2" />{t("pages.all_documents")}

          </Button>
            {folders.map((folder) =>
          <Button
            key={folder.id}
            variant={selectedFolder === folder.id ? 'primary' : 'outline'}
            onClick={() => setSelectedFolder(folder.id)}>

                <FolderOpen className="h-4 w-4 mr-2" />
                {folder.name}
              </Button>
          )}
          </div>
        </div>
      }
      {/* Documents */}
      {documents.length === 0 ?
      <Card className="p-8 text-center">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t("pages.no_documents")}</h3>
          <p className="text-gray-500">{t("pages.no_documents_have_been_shared_with_you_yet")}</p>
        </Card> :

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {documents.map((document) =>
        <Card key={document.id} className="hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start space-x-3">
                    {getDocumentIcon(document.type)}
                    <div>
                      <h3 className="font-medium text-gray-900">
                        {document.name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {formatBytes(document.size || 0)}
                      </p>
                    </div>
                  </div>
                  <Badge color={getTypeColor(document.type)}>
                    {document.type?.toUpperCase() || 'FILE'}
                  </Badge>
                </div>
                {document.description &&
            <p className="text-gray-600 text-sm mb-4">
                    {document.description}
                  </p>
            }
                <div className="space-y-2 text-sm text-gray-500">
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    <span>{t("components.uploaded")}{formatDate(document.created_at)}</span>
                  </div>
                  {document.uploaded_by_name &&
              <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      <span>{t("pages.by")}{document.uploaded_by_name}</span>
                    </div>
              }
                </div>
                <div className="mt-6 flex gap-2">
                  <Button
                onClick={() => handleViewDocument(document)}
                variant="outline"
                size="sm"
                className="flex-1">

                    <Eye className="h-4 w-4 mr-1" />{t("mobile.view")}

              </Button>
                  <Button
                onClick={() => handleDownloadDocument(document)}
                variant="primary"
                size="sm"
                className="flex-1">

                    <Download className="h-4 w-4 mr-1" />{t("pages.download")}

              </Button>
                </div>
              </div>
            </Card>
        )}
        </div>
      }
    </div>);

};
export default MyDocumentsPage;