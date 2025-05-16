import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaUpload, FaFile, FaTimes, FaCheck, FaFolder, FaTag, FaUsers, FaLock, FaEye, FaInfoCircle } from 'react-icons/fa';
import { toast } from 'react-toastify';

const DocumentUploadPageV2 = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [files, setFiles] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    tags: [],
    visibility: 'private',
    permissions: {
      view: [],
      download: [],
      edit: []
    },
    folder: '',
    metadata: {
      author: '',
      version: '1.0',
      language: 'tr'
    }
  });
  const [categories] = useState([
    { id: 'training', name: 'Eğitim Materyalleri' },
    { id: 'assessment', name: 'Değerlendirme Dokümanları' },
    { id: 'reports', name: 'Raporlar' },
    { id: 'policy', name: 'Politikalar' },
    { id: 'templates', name: 'Şablonlar' },
    { id: 'other', name: 'Diğer' }
  ]);
  const [tagInput, setTagInput] = useState('');
  const [previewFile, setPreviewFile] = useState(null);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const newFiles = selectedFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0
    }));
    setFiles([...files, ...newFiles]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('border-blue-500');
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-500');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('border-blue-500');
    const droppedFiles = Array.from(e.dataTransfer.files);
    const newFiles = droppedFiles.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending',
      progress: 0
    }));
    setFiles([...files, ...newFiles]);
  };

  const removeFile = (fileId) => {
    setFiles(files.filter(f => f.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (fileType) => {
    if (fileType.includes('image')) return '🖼️';
    if (fileType.includes('pdf')) return '📄';
    if (fileType.includes('word') || fileType.includes('document')) return '📝';
    if (fileType.includes('sheet') || fileType.includes('excel')) return '📊';
    if (fileType.includes('presentation') || fileType.includes('powerpoint')) return '📊';
    if (fileType.includes('video')) return '🎥';
    if (fileType.includes('audio')) return '🎵';
    if (fileType.includes('zip') || fileType.includes('rar')) return '📦';
    return '📎';
  };

  const handleAddTag = (e) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      if (!formData.tags.includes(tagInput.trim())) {
        setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
      }
      setTagInput('');
    }
  };

  const removeTag = (tag) => {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) });
  };

  const uploadFiles = async () => {
    setLoading(true);
    const uploadPromises = files.map(async (fileItem) => {
      const data = new FormData();
      data.append('file', fileItem.file);
      data.append('title', formData.title || fileItem.name);
      data.append('description', formData.description);
      data.append('category', formData.category);
      data.append('tags', JSON.stringify(formData.tags));
      data.append('visibility', formData.visibility);
      data.append('permissions', JSON.stringify(formData.permissions));
      data.append('folder', formData.folder);
      data.append('metadata', JSON.stringify(formData.metadata));

      try {
        setFiles(prevFiles => prevFiles.map(f => 
          f.id === fileItem.id ? { ...f, status: 'uploading' } : f
        ));

        const response = await axios.post('/api/documents/upload', data, {
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(prev => ({ ...prev, [fileItem.id]: percentCompleted }));
            setFiles(prevFiles => prevFiles.map(f => 
              f.id === fileItem.id ? { ...f, progress: percentCompleted } : f
            ));
          }
        });

        setFiles(prevFiles => prevFiles.map(f => 
          f.id === fileItem.id ? { ...f, status: 'completed', documentId: response.data.id } : f
        ));

        return response.data;
      } catch (error) {
        setFiles(prevFiles => prevFiles.map(f => 
          f.id === fileItem.id ? { ...f, status: 'error', error: error.message } : f
        ));
        throw error;
      }
    });

    try {
      const results = await Promise.allSettled(uploadPromises);
      const successful = results.filter(r => r.status === 'fulfilled').length;
      const failed = results.filter(r => r.status === 'rejected').length;

      if (successful > 0) {
        toast.success(`${successful} dosya başarıyla yüklendi`);
      }
      if (failed > 0) {
        toast.error(`${failed} dosya yüklenemedi`);
      }

      if (successful > 0) {
        setTimeout(() => navigate('/documents'), 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      toast.error('Lütfen en az bir dosya seçin');
      return;
    }
    await uploadFiles();
  };

  const previewDocument = (fileItem) => {
    if (fileItem.file.type.includes('image')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewFile({
          name: fileItem.name,
          type: 'image',
          url: e.target.result
        });
      };
      reader.readAsDataURL(fileItem.file);
    } else if (fileItem.file.type === 'application/pdf') {
      const url = URL.createObjectURL(fileItem.file);
      setPreviewFile({
        name: fileItem.name,
        type: 'pdf',
        url
      });
    } else {
      setPreviewFile({
        name: fileItem.name,
        type: 'other',
        url: null
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/documents')}
            className="text-gray-600 hover:text-gray-800 mb-4"
          >
            ← Dokümanlara Geri Dön
          </button>
          <h1 className="text-2xl font-bold">Doküman Yükle</h1>
          <p className="text-gray-600">Yeni dokümanlar yükleyin ve kategorilendirin</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* File Upload Area */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Dosya Seçimi</h3>
            
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <FaUpload className="text-5xl text-gray-400 mx-auto mb-4" />
              <p className="text-lg mb-2">
                Dosyaları buraya sürükleyin veya tıklayarak seçin
              </p>
              <p className="text-sm text-gray-600">
                Desteklenen formatlar: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, JPG, PNG, ZIP
              </p>
              <p className="text-sm text-gray-600">
                Maksimum dosya boyutu: 100MB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.zip,.rar"
              />
            </div>

            {/* Selected Files */}
            {files.length > 0 && (
              <div className="mt-6">
                <h4 className="font-medium mb-3">Seçilen Dosyalar ({files.length})</h4>
                <div className="space-y-3">
                  {files.map((fileItem) => (
                    <div key={fileItem.id} className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center flex-1">
                          <span className="text-2xl mr-3">{getFileIcon(fileItem.type)}</span>
                          <div className="flex-1">
                            <p className="font-medium">{fileItem.name}</p>
                            <p className="text-sm text-gray-600">
                              {formatFileSize(fileItem.size)}
                            </p>
                          </div>
                          {fileItem.status === 'uploading' && (
                            <div className="w-32 mr-4">
                              <div className="bg-gray-200 rounded-full h-2">
                                <div
                                  className="bg-blue-500 h-2 rounded-full transition-all"
                                  style={{ width: `${fileItem.progress}%` }}
                                />
                              </div>
                              <p className="text-xs text-center mt-1">{fileItem.progress}%</p>
                            </div>
                          )}
                          {fileItem.status === 'completed' && (
                            <FaCheck className="text-green-500 mr-4" />
                          )}
                          {fileItem.status === 'error' && (
                            <span className="text-red-500 text-sm mr-4">Hata</span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            type="button"
                            onClick={() => previewDocument(fileItem)}
                            className="text-blue-500 hover:text-blue-600"
                          >
                            <FaEye />
                          </button>
                          <button
                            type="button"
                            onClick={() => removeFile(fileItem.id)}
                            className="text-red-500 hover:text-red-600"
                            disabled={fileItem.status === 'uploading'}
                          >
                            <FaTimes />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Document Details */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Doküman Detayları</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Başlık</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Doküman başlığı"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Kategori</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  <option value="">Kategori seçin</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2">Açıklama</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows="3"
                  placeholder="Doküman hakkında kısa açıklama"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  <FaFolder className="inline mr-1" />
                  Klasör
                </label>
                <input
                  type="text"
                  value={formData.folder}
                  onChange={(e) => setFormData({ ...formData, folder: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Klasör yolu (örn: /Eğitimler/2024)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  <FaLock className="inline mr-1" />
                  Görünürlük
                </label>
                <select
                  value={formData.visibility}
                  onChange={(e) => setFormData({ ...formData, visibility: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="private">Özel</option>
                  <option value="restricted">Kısıtlı</option>
                  <option value="public">Herkese Açık</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2">
                  <FaTag className="inline mr-1" />
                  Etiketler
                </label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {formData.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm flex items-center"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="ml-2 text-blue-500 hover:text-blue-700"
                      >
                        <FaTimes className="text-xs" />
                      </button>
                    </span>
                  ))}
                </div>
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleAddTag}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Etiket ekle (Enter ile onaylayın)"
                />
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Metadata</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Yazar</label>
                <input
                  type="text"
                  value={formData.metadata.author}
                  onChange={(e) => setFormData({
                    ...formData,
                    metadata: { ...formData.metadata, author: e.target.value }
                  })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Doküman yazarı"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Versiyon</label>
                <input
                  type="text"
                  value={formData.metadata.version}
                  onChange={(e) => setFormData({
                    ...formData,
                    metadata: { ...formData.metadata, version: e.target.value }
                  })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="1.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Dil</label>
                <select
                  value={formData.metadata.language}
                  onChange={(e) => setFormData({
                    ...formData,
                    metadata: { ...formData.metadata, language: e.target.value }
                  })}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="tr">Türkçe</option>
                  <option value="en">İngilizce</option>
                </select>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/documents')}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50"
            >
              İptal
            </button>
            <button
              type="submit"
              disabled={loading || files.length === 0}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? 'Yükleniyor...' : `${files.length} Dosyayı Yükle`}
            </button>
          </div>
        </form>
      </div>

      {/* Preview Modal */}
      {previewFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">{previewFile.name}</h3>
              <button
                onClick={() => setPreviewFile(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <FaTimes />
              </button>
            </div>
            <div className="p-4 overflow-auto max-h-[calc(90vh-8rem)]">
              {previewFile.type === 'image' && (
                <img
                  src={previewFile.url}
                  alt={previewFile.name}
                  className="max-w-full h-auto mx-auto"
                />
              )}
              {previewFile.type === 'pdf' && (
                <iframe
                  src={previewFile.url}
                  title={previewFile.name}
                  className="w-full h-[600px]"
                />
              )}
              {previewFile.type === 'other' && (
                <div className="text-center py-8">
                  <FaFile className="text-6xl text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Bu dosya türü önizlenemez</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUploadPageV2;