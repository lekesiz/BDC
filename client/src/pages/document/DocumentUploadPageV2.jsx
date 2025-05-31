import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaFolder, FaTag, FaLock, FaInfoCircle } from 'react-icons/fa';
import { toast } from 'react-toastify';
import { DocumentUploader, DocumentViewer } from '../../components/document';

const DocumentUploadPageV2 = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
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

  const handleUploadComplete = (documents, errors) => {
    setUploadedDocuments(documents);
    setUploadComplete(true);
    setLoading(false);
    
    if (documents.length > 0) {
      toast.success(`${documents.length} dosya başarıyla yüklendi`);
      setTimeout(() => navigate('/documents'), 2000);
    }
    
    if (errors.length > 0) {
      toast.error(`${errors.length} dosya yüklenemedi`);
    }
  };
  
  const handleUploadError = (errorMessages) => {
    errorMessages.forEach(msg => toast.error(msg));
    setLoading(false);
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

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
  };
  
  const getUploadMetadata = () => {
    return {
      title: formData.title,
      description: formData.description,
      category: formData.category,
      tags: JSON.stringify(formData.tags),
      visibility: formData.visibility,
      permissions: JSON.stringify(formData.permissions),
      folder: formData.folder,
      metadata: JSON.stringify(formData.metadata)
    };
  };
  
  const handlePreviewDocument = (document) => {
    setPreviewFile(document);
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
            
            <DocumentUploader
              onUploadComplete={handleUploadComplete}
              onUploadError={handleUploadError}
              metadata={getUploadMetadata()}
              maxFileSize={100 * 1024 * 1024} // 100MB
              allowMultiple={true}
              maxFiles={10}
              acceptedFileTypes={['pdf', 'office', 'image', 'text', 'archive']}
              onPreview={handlePreviewDocument}
            />
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
              disabled={loading || uploadComplete}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? 'Yükleniyor...' : uploadComplete ? 'Yükleme Tamamlandı' : 'Dosyaları Yükle'}
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
                ✕
              </button>
            </div>
            <div className="p-4 overflow-auto max-h-[calc(90vh-8rem)]">
              <DocumentViewer 
                document={previewFile}
                height="600px"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentUploadPageV2;