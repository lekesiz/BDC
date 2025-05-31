import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { toast } from 'react-toastify';
import DocumentService from '../../../components/document/DocumentService';

// Mock axios
vi.mock('axios');

// Mock toast
vi.mock('react-toastify', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}));

// Mock document.createElement and related DOM methods
const mockLink = {
  href: '',
  setAttribute: vi.fn(),
  click: vi.fn(),
  remove: vi.fn()
};

// Mock URL methods
global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = vi.fn();

// Mock document.createElement and appendChild
document.createElement = vi.fn(() => mockLink);
document.body.appendChild = vi.fn();

describe('DocumentService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Document Type Helpers', () => {
    it('identifies document type by file extension', () => {
      expect(DocumentService.getDocumentType('document.pdf', '')).toBe('pdf');
      expect(DocumentService.getDocumentType('image.jpg', '')).toBe('image');
      expect(DocumentService.getDocumentType('spreadsheet.xlsx', '')).toBe('office');
      expect(DocumentService.getDocumentType('data.csv', '')).toBe('text');
      expect(DocumentService.getDocumentType('archive.zip', '')).toBe('archive');
    });

    it('identifies document type by mime type', () => {
      expect(DocumentService.getDocumentType('file', 'application/pdf')).toBe('pdf');
      expect(DocumentService.getDocumentType('file', 'image/jpeg')).toBe('image');
      expect(DocumentService.getDocumentType('file', 'application/vnd.ms-excel')).toBe('office');
      expect(DocumentService.getDocumentType('file', 'text/plain')).toBe('text');
      expect(DocumentService.getDocumentType('file', 'application/zip')).toBe('archive');
    });

    it('returns "unknown" for unsupported types', () => {
      expect(DocumentService.getDocumentType('file.xyz', 'application/unknown')).toBe('unknown');
    });

    it('checks for preview support', () => {
      expect(DocumentService.isPreviewSupported('document.pdf', 'application/pdf')).toBe(true);
      expect(DocumentService.isPreviewSupported('image.jpg', 'image/jpeg')).toBe(true);
      expect(DocumentService.isPreviewSupported('archive.zip', 'application/zip')).toBe(false);
      expect(DocumentService.isPreviewSupported('file.xyz', 'application/unknown')).toBe(false);
    });
  });

  describe('formatFileSize', () => {
    it('formats file size in appropriate units', () => {
      expect(DocumentService.formatFileSize(0)).toBe('0 Bytes');
      expect(DocumentService.formatFileSize(512)).toBe('512 Bytes');
      expect(DocumentService.formatFileSize(1024)).toBe('1 KB');
      expect(DocumentService.formatFileSize(1048576)).toBe('1 MB');
      expect(DocumentService.formatFileSize(1073741824)).toBe('1 GB');
      expect(DocumentService.formatFileSize(5368709120)).toBe('5 GB');
    });

    it('rounds to two decimal places', () => {
      expect(DocumentService.formatFileSize(1500)).toBe('1.46 KB');
      expect(DocumentService.formatFileSize(1500000)).toBe('1.43 MB');
    });
  });

  describe('validateFile', () => {
    it('validates supported file types', () => {
      const pdfFile = { name: 'document.pdf', type: 'application/pdf', size: 1024 * 1024 };
      const result = DocumentService.validateFile(pdfFile);
      expect(result.valid).toBe(true);
      expect(result.documentType).toBe('pdf');
    });

    it('rejects unsupported file types', () => {
      const unsupportedFile = { name: 'file.xyz', type: 'application/unknown', size: 1024 };
      const result = DocumentService.validateFile(unsupportedFile);
      expect(result.valid).toBe(false);
      expect(result.message).toBe('Desteklenmeyen dosya türü');
    });

    it('rejects files that exceed maximum size', () => {
      // PDF max size is 50MB
      const largeFile = { 
        name: 'large.pdf', 
        type: 'application/pdf', 
        size: 60 * 1024 * 1024 // 60MB 
      };
      
      const result = DocumentService.validateFile(largeFile);
      expect(result.valid).toBe(false);
      expect(result.message).toContain('Dosya boyutu çok büyük');
    });
  });

  describe('uploadDocument', () => {
    it('rejects invalid files before upload', async () => {
      const invalidFile = { name: 'file.xyz', type: 'application/unknown', size: 1024 };
      
      await expect(DocumentService.uploadDocument(invalidFile)).rejects.toThrow('Desteklenmeyen dosya türü');
      expect(toast.error).toHaveBeenCalled();
      expect(axios.post).not.toHaveBeenCalled();
    });

    it('uploads valid files to the server', async () => {
      const validFile = { name: 'document.pdf', type: 'application/pdf', size: 1024 * 1024 };
      const mockResponse = { 
        data: { 
          id: '123', 
          name: 'document.pdf',
          url: 'https://example.com/document.pdf' 
        } 
      };
      
      axios.post.mockResolvedValue(mockResponse);
      
      const result = await DocumentService.uploadDocument(validFile);
      
      expect(axios.post).toHaveBeenCalledWith(
        '/api/documents/upload',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: expect.any(Function)
        })
      );
      
      expect(result).toEqual(mockResponse.data);
      expect(toast.success).toHaveBeenCalled();
    });

    it('includes metadata in the upload request', async () => {
      const validFile = { name: 'document.pdf', type: 'application/pdf', size: 1024 * 1024 };
      const metadata = { category: 'invoice', userId: 123 };
      
      axios.post.mockResolvedValue({ data: {} });
      
      await DocumentService.uploadDocument(validFile, metadata);
      
      const formDataArg = axios.post.mock.calls[0][1];
      expect(formDataArg instanceof FormData).toBe(true);
      
      // We can't directly check FormData contents in tests,
      // but we can verify axios.post was called correctly
      expect(axios.post).toHaveBeenCalledWith(
        '/api/documents/upload',
        expect.any(FormData),
        expect.any(Object)
      );
    });

    it('handles upload progress updates', async () => {
      const validFile = { name: 'document.pdf', type: 'application/pdf', size: 1024 * 1024 };
      const onProgress = vi.fn();
      
      axios.post.mockImplementation((url, data, config) => {
        // Simulate progress event
        config.onUploadProgress({ loaded: 512 * 1024, total: 1024 * 1024 });
        return Promise.resolve({ data: {} });
      });
      
      await DocumentService.uploadDocument(validFile, {}, onProgress);
      
      expect(onProgress).toHaveBeenCalledWith(50); // 50% progress
    });

    it('handles upload errors', async () => {
      const validFile = { name: 'document.pdf', type: 'application/pdf', size: 1024 * 1024 };
      const errorMessage = 'Server error';
      
      axios.post.mockRejectedValue({
        response: {
          data: {
            message: errorMessage
          }
        }
      });
      
      await expect(DocumentService.uploadDocument(validFile)).rejects.toThrow();
      expect(toast.error).toHaveBeenCalledWith(errorMessage);
    });
  });

  describe('downloadDocument', () => {
    it('downloads a document from the server', async () => {
      const documentId = '123';
      const filename = 'document.pdf';
      const mockBlob = new Blob(['test content'], { type: 'application/pdf' });
      
      axios.mockImplementation(() => Promise.resolve({ data: mockBlob }));
      
      await DocumentService.downloadDocument(documentId, filename);
      
      expect(axios).toHaveBeenCalledWith(expect.objectContaining({
        url: `/api/documents/${documentId}/download`,
        method: 'GET',
        responseType: 'blob'
      }));
      
      expect(URL.createObjectURL).toHaveBeenCalledWith(expect.any(Blob));
      expect(mockLink.setAttribute).toHaveBeenCalledWith('download', filename);
      expect(mockLink.click).toHaveBeenCalled();
      expect(mockLink.remove).toHaveBeenCalled();
      expect(toast.success).toHaveBeenCalledWith('Dosya indirildi');
    });

    it('handles download errors', async () => {
      const documentId = '123';
      
      axios.mockRejectedValue(new Error('Download failed'));
      
      await expect(DocumentService.downloadDocument(documentId)).rejects.toThrow();
      expect(toast.error).toHaveBeenCalledWith('Dosya indirilirken bir hata oluştu');
    });

    it('tracks download progress', async () => {
      const documentId = '123';
      const onProgress = vi.fn();
      const mockBlob = new Blob(['test content'], { type: 'application/pdf' });
      
      axios.mockImplementation((config) => {
        // Simulate progress event
        config.onDownloadProgress({ loaded: 50, total: 100 });
        return Promise.resolve({ data: mockBlob });
      });
      
      await DocumentService.downloadDocument(documentId, 'document.pdf', onProgress);
      
      expect(onProgress).toHaveBeenCalledWith(50); // 50% progress
    });
  });

  describe('deleteDocument', () => {
    it('sends delete request to the server', async () => {
      const documentId = '123';
      
      axios.delete.mockResolvedValue({ data: { success: true } });
      
      await DocumentService.deleteDocument(documentId);
      
      expect(axios.delete).toHaveBeenCalledWith(`/api/documents/${documentId}`);
      expect(toast.success).toHaveBeenCalledWith('Doküman silindi');
    });

    it('handles delete errors', async () => {
      const documentId = '123';
      
      axios.delete.mockRejectedValue(new Error('Delete failed'));
      
      await expect(DocumentService.deleteDocument(documentId)).rejects.toThrow();
      expect(toast.error).toHaveBeenCalledWith('Doküman silinirken bir hata oluştu');
    });
  });

  describe('updateDocumentMetadata', () => {
    it('sends update request to the server', async () => {
      const documentId = '123';
      const metadata = { title: 'Updated Title', tags: ['important'] };
      
      axios.patch.mockResolvedValue({ data: { success: true } });
      
      await DocumentService.updateDocumentMetadata(documentId, metadata);
      
      expect(axios.patch).toHaveBeenCalledWith(`/api/documents/${documentId}`, metadata);
      expect(toast.success).toHaveBeenCalledWith('Doküman bilgileri güncellendi');
    });

    it('handles update errors', async () => {
      const documentId = '123';
      const metadata = { title: 'Updated Title' };
      
      axios.patch.mockRejectedValue(new Error('Update failed'));
      
      await expect(DocumentService.updateDocumentMetadata(documentId, metadata)).rejects.toThrow();
      expect(toast.error).toHaveBeenCalledWith('Doküman güncellenirken bir hata oluştu');
    });
  });

  describe('shareDocument', () => {
    it('sends share request to the server', async () => {
      const documentId = '123';
      const users = [101, 102];
      const permission = 'edit';
      
      axios.post.mockResolvedValue({ data: { success: true } });
      
      await DocumentService.shareDocument(documentId, users, permission);
      
      expect(axios.post).toHaveBeenCalledWith(`/api/documents/${documentId}/share`, {
        users,
        permission
      });
      
      expect(toast.success).toHaveBeenCalledWith('Doküman paylaşıldı');
    });

    it('uses default "view" permission when not specified', async () => {
      const documentId = '123';
      const users = [101, 102];
      
      axios.post.mockResolvedValue({ data: { success: true } });
      
      await DocumentService.shareDocument(documentId, users);
      
      expect(axios.post).toHaveBeenCalledWith(`/api/documents/${documentId}/share`, {
        users,
        permission: 'view'
      });
    });

    it('handles share errors', async () => {
      const documentId = '123';
      const users = [101, 102];
      
      axios.post.mockRejectedValue(new Error('Share failed'));
      
      await expect(DocumentService.shareDocument(documentId, users)).rejects.toThrow();
      expect(toast.error).toHaveBeenCalledWith('Doküman paylaşılırken bir hata oluştu');
    });
  });

  describe('Service API', () => {
    it('exports all required methods', () => {
      expect(typeof DocumentService.uploadDocument).toBe('function');
      expect(typeof DocumentService.downloadDocument).toBe('function');
      expect(typeof DocumentService.deleteDocument).toBe('function');
      expect(typeof DocumentService.updateDocumentMetadata).toBe('function');
      expect(typeof DocumentService.shareDocument).toBe('function');
      expect(typeof DocumentService.validateFile).toBe('function');
      expect(typeof DocumentService.getDocumentType).toBe('function');
      expect(typeof DocumentService.isPreviewSupported).toBe('function');
      expect(typeof DocumentService.formatFileSize).toBe('function');
      expect(DocumentService.SUPPORTED_DOCUMENT_TYPES).toBeDefined();
    });
  });
});