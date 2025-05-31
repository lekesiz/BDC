import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Download, Eye, Printer, Share2, ZoomIn, ZoomOut, RotateCw, FileText, Image, FileSpreadsheet, File } from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import LoadingSpinner from '../ui/LoadingSpinner';

const DocumentViewer = ({ document, onClose }) => {
  const [loading, setLoading] = useState(true);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const { toast } = useToast();

  useEffect(() => {
    // Simulate document loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, [document]);

  const handleDownload = () => {
    toast({
      title: "Download Started",
      description: `Downloading ${document?.name || 'document'}...`,
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const handleShare = () => {
    toast({
      title: "Share Document",
      description: "Share functionality will be implemented soon.",
    });
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev + 10, 200));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev - 10, 50));
  };

  const handleRotate = () => {
    setRotation(prev => (prev + 90) % 360);
  };

  const getFileIcon = (type) => {
    switch (type) {
      case 'pdf':
      case 'doc':
      case 'docx':
        return <FileText className="h-5 w-5" />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <Image className="h-5 w-5" />;
      case 'xls':
      case 'xlsx':
      case 'csv':
        return <FileSpreadsheet className="h-5 w-5" />;
      default:
        return <File className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <Card className="flex-1">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getFileIcon(document?.type)}
              <CardTitle>{document?.name || 'Document Viewer'}</CardTitle>
              <Badge variant="outline">
                {document?.type?.toUpperCase() || 'FILE'}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomOut}
                disabled={zoom <= 50}
              >
                <ZoomOut className="h-4 w-4" />
              </Button>
              <span className="text-sm font-medium px-2">{zoom}%</span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomIn}
                disabled={zoom >= 200}
              >
                <ZoomIn className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRotate}
              >
                <RotateCw className="h-4 w-4" />
              </Button>
              <div className="h-6 w-px bg-border mx-2" />
              <Button
                variant="outline"
                size="sm"
                onClick={handleShare}
              >
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handlePrint}
              >
                <Printer className="h-4 w-4 mr-2" />
                Print
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={handleDownload}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="preview" className="w-full">
            <TabsList>
              <TabsTrigger value="preview">
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </TabsTrigger>
              <TabsTrigger value="details">Details</TabsTrigger>
              <TabsTrigger value="versions">Versions</TabsTrigger>
              <TabsTrigger value="activity">Activity</TabsTrigger>
            </TabsList>
            
            <TabsContent value="preview" className="mt-4">
              <div 
                className="border rounded-lg p-8 bg-gray-50 min-h-[600px] flex items-center justify-center"
                style={{
                  transform: `scale(${zoom / 100}) rotate(${rotation}deg)`,
                  transition: 'transform 0.3s ease'
                }}
              >
                {document?.type === 'pdf' ? (
                  <div className="text-center">
                    <FileText className="h-24 w-24 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">PDF Preview</p>
                    <p className="text-sm text-gray-500 mt-2">
                      {document?.name}
                    </p>
                  </div>
                ) : document?.type?.startsWith('image') ? (
                  <div className="text-center">
                    <Image className="h-24 w-24 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Image Preview</p>
                    <p className="text-sm text-gray-500 mt-2">
                      {document?.name}
                    </p>
                  </div>
                ) : (
                  <div className="text-center">
                    <File className="h-24 w-24 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Document Preview</p>
                    <p className="text-sm text-gray-500 mt-2">
                      {document?.name}
                    </p>
                    <p className="text-xs text-gray-400 mt-4">
                      Preview not available for this file type
                    </p>
                  </div>
                )}
              </div>
            </TabsContent>
            
            <TabsContent value="details" className="mt-4">
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700">File Information</h4>
                  <div className="mt-2 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Name:</span>
                      <span>{document?.name || 'Untitled'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Type:</span>
                      <span>{document?.type || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Size:</span>
                      <span>{document?.size || '0 KB'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Created:</span>
                      <span>{document?.created_at || 'Unknown'}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Modified:</span>
                      <span>{document?.updated_at || 'Unknown'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="versions" className="mt-4">
              <div className="text-center py-8">
                <p className="text-gray-500">No previous versions available</p>
              </div>
            </TabsContent>
            
            <TabsContent value="activity" className="mt-4">
              <div className="text-center py-8">
                <p className="text-gray-500">No activity to show</p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default DocumentViewer;