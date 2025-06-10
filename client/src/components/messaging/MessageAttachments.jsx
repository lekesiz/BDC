// TODO: i18n - processed
import React, { useState } from 'react';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { X, Upload, File, Image, FileText, Download, Eye } from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import LoadingSpinner from '../ui/LoadingSpinner';import { useTranslation } from "react-i18next";
const MessageAttachments = ({ onAttachmentsChange, existingAttachments = [] }) => {const { t } = useTranslation();
  const [attachments, setAttachments] = useState(existingAttachments);
  const [uploading, setUploading] = useState(false);
  const { toast } = useToast();
  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    // Check file size (max 10MB)
    const MAX_SIZE = 10 * 1024 * 1024; // 10MB
    const oversizedFiles = files.filter((file) => file.size > MAX_SIZE);
    if (oversizedFiles.length > 0) {
      toast({
        title: "File too large",
        description: `Maximum file size is 10MB. ${oversizedFiles.length} file(s) exceeded this limit.`,
        variant: "destructive"
      });
      return;
    }
    setUploading(true);
    try {
      // Simulate file upload
      await new Promise((resolve) => setTimeout(resolve, 1000));
      const newAttachments = files.map((file) => ({
        id: Date.now() + Math.random(),
        name: file.name,
        size: formatFileSize(file.size),
        type: file.type,
        url: URL.createObjectURL(file),
        uploadedAt: new Date().toISOString()
      }));
      const updatedAttachments = [...attachments, ...newAttachments];
      setAttachments(updatedAttachments);
      if (onAttachmentsChange) {
        onAttachmentsChange(updatedAttachments);
      }
      toast({
        title: "Files uploaded",
        description: `${files.length} file(s) uploaded successfully.`
      });
    } catch (error) {
      toast({
        title: "Upload failed",
        description: "Failed to upload files. Please try again.",
        variant: "destructive"
      });
    } finally {
      setUploading(false);
    }
  };
  const handleRemoveAttachment = (id) => {
    const updatedAttachments = attachments.filter((att) => att.id !== id);
    setAttachments(updatedAttachments);
    if (onAttachmentsChange) {
      onAttachmentsChange(updatedAttachments);
    }
  };
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  const getFileIcon = (type) => {
    if (type.startsWith('image/')) return <Image className="h-4 w-4" />;
    if (type.includes('pdf')) return <FileText className="h-4 w-4" />;
    return <File className="h-4 w-4" />;
  };
  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="file-upload">{t("components.attachments")}</Label>
        <div className="mt-2">
          <Input
            id="file-upload"
            type="file"
            multiple
            onChange={handleFileSelect}
            disabled={uploading}
            className="hidden"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.gif" />

          <label
            htmlFor="file-upload"
            className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">

            {uploading ?
            <>
                <LoadingSpinner size="sm" className="mr-2" />{t("components.uploading")}

            </> :

            <>
                <Upload className="h-4 w-4 mr-2" />{t("components.choose_files")}

            </>
            }
          </label>
          <p className="text-sm text-gray-500 mt-1">{t("components.supported_formats_pdf_doc_docx_xls_xlsx_png_jpg_gi")}

          </p>
        </div>
      </div>
      {attachments.length > 0 &&
      <div className="space-y-2">
          <Label>{t("components.attached_files_")}{attachments.length})</Label>
          <div className="space-y-2">
            {attachments.map((attachment) =>
          <Card key={attachment.id} className="p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getFileIcon(attachment.type)}
                    <div>
                      <p className="text-sm font-medium">{attachment.name}</p>
                      <p className="text-xs text-gray-500">{attachment.size}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => window.open(attachment.url, '_blank')}>

                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    const a = document.createElement('a');
                    a.href = attachment.url;
                    a.download = attachment.name;
                    a.click();
                  }}>

                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleRemoveAttachment(attachment.id)}
                  className="text-red-600 hover:text-red-700">

                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
          )}
          </div>
        </div>
      }
    </div>);

};
export default MessageAttachments;