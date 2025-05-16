import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaArrowLeft, FaDownload, FaShare, FaEdit, FaTrash, FaStar, FaComment, FaExpand, FaCompress, FaTag, FaEye, FaClock, FaPrint, FaBookmark } from 'react-icons/fa';
import { toast } from 'react-toastify';

const DocumentViewerPageV2 = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState(null);
  const [fullscreen, setFullscreen] = useState(false);
  const [zoom, setZoom] = useState(100);
  const [showSidebar, setShowSidebar] = useState(true);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [rating, setRating] = useState(0);
  const [bookmarked, setBookmarked] = useState(false);
  const [versions, setVersions] = useState([]);
  const [viewCount, setViewCount] = useState(0);
  const [relatedDocs, setRelatedDocs] = useState([]);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    fetchDocument();
    fetchComments();
    fetchVersions();
    fetchRelatedDocs();
    trackView();
  }, [id]);

  const fetchDocument = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/documents/${id}`);
      setDocument(response.data);
      setRating(response.data.user_rating || 0);
      setBookmarked(response.data.is_bookmarked || false);
      if (response.data.type === 'pdf') {
        setTotalPages(response.data.page_count || 1);
      }
    } catch (error) {
      toast.error('Doküman yüklenemedi');
      navigate('/documents');
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}/comments`);
      setComments(response.data);
    } catch (error) {
      console.error('Yorumlar yüklenemedi:', error);
    }
  };

  const fetchVersions = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}/versions`);
      setVersions(response.data);
    } catch (error) {
      console.error('Versiyonlar yüklenemedi:', error);
    }
  };

  const fetchRelatedDocs = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}/related`);
      setRelatedDocs(response.data);
    } catch (error) {
      console.error('İlgili dokümanlar yüklenemedi:', error);
    }
  };

  const trackView = async () => {
    try {
      const response = await axios.post(`/api/documents/${id}/view`);
      setViewCount(response.data.view_count);
    } catch (error) {
      console.error('Görüntüleme kaydedilemedi:', error);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios({
        url: `/api/documents/${id}/download`,
        method: 'GET',
        responseType: 'blob',
        onDownloadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setDownloadProgress(percentCompleted);
        }
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', document.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Doküman indirildi');
    } catch (error) {
      toast.error('İndirme başarısız');
    } finally {
      setDownloadProgress(0);
    }
  };

  const handleShare = () => {
    navigate(`/documents/${id}/share`);
  };

  const handleEdit = () => {
    navigate(`/documents/${id}/edit`);
  };

  const handleDelete = async () => {
    if (window.confirm('Bu dokümanı silmek istediğinizden emin misiniz?')) {
      try {
        await axios.delete(`/api/documents/${id}`);
        toast.success('Doküman silindi');
        navigate('/documents');
      } catch (error) {
        toast.error('Silme işlemi başarısız');
      }
    }
  };

  const handleRating = async (value) => {
    try {
      await axios.post(`/api/documents/${id}/rate`, { rating: value });
      setRating(value);
      toast.success('Değerlendirmeniz kaydedildi');
    } catch (error) {
      toast.error('Değerlendirme başarısız');
    }
  };

  const handleBookmark = async () => {
    try {
      await axios.post(`/api/documents/${id}/bookmark`);
      setBookmarked(!bookmarked);
      toast.success(bookmarked ? 'Yer imi kaldırıldı' : 'Yer imine eklendi');
    } catch (error) {
      toast.error('İşlem başarısız');
    }
  };

  const handleComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      const response = await axios.post(`/api/documents/${id}/comments`, { 
        content: newComment 
      });
      setComments([...comments, response.data]);
      setNewComment('');
      toast.success('Yorum eklendi');
    } catch (error) {
      toast.error('Yorum eklenemedi');
    }
  };

  const toggleFullscreen = () => {
    if (!fullscreen) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setFullscreen(!fullscreen);
  };

  const handleZoom = (direction) => {
    if (direction === 'in' && zoom < 200) {
      setZoom(zoom + 25);
    } else if (direction === 'out' && zoom > 50) {
      setZoom(zoom - 25);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const navigatePage = (direction) => {
    if (direction === 'next' && currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    } else if (direction === 'prev' && currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const renderDocumentContent = () => {
    if (!document) return null;

    switch (document.type) {
      case 'pdf':
        return (
          <div className="relative">
            <iframe
              src={`${document.url}#page=${currentPage}`}
              className="w-full h-[800px] border-0"
              style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top left' }}
              title={document.name}
            />
            {totalPages > 1 && (
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white shadow-lg rounded-lg px-4 py-2 flex items-center space-x-4">
                <button
                  onClick={() => navigatePage('prev')}
                  disabled={currentPage === 1}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                >
                  ← Önceki
                </button>
                <span>
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => navigatePage('next')}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                >
                  Sonraki →
                </button>
              </div>
            )}
          </div>
        );
      
      case 'image':
        return (
          <img
            src={document.url}
            alt={document.name}
            className="max-w-full h-auto mx-auto"
            style={{ transform: `scale(${zoom / 100})` }}
          />
        );
      
      case 'document':
      case 'docx':
      case 'doc':
        return (
          <iframe
            src={`https://docs.google.com/viewer?url=${encodeURIComponent(document.url)}&embedded=true`}
            className="w-full h-[800px] border-0"
            title={document.name}
          />
        );
      
      default:
        return (
          <div className="text-center py-16">
            <FaEye className="text-6xl text-gray-400 mx-auto mb-4" />
            <p className="text-xl mb-4">Bu dosya türü önizlenemez</p>
            <button
              onClick={handleDownload}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              Dosyayı İndir
            </button>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gray-50 ${fullscreen ? 'fixed inset-0 z-50' : ''}`}>
      <div className="flex h-screen">
        {/* Sidebar */}
        {showSidebar && !fullscreen && (
          <div className="w-80 bg-white shadow-lg overflow-y-auto">
            <div className="p-6">
              <button
                onClick={() => navigate('/documents')}
                className="flex items-center text-gray-600 hover:text-gray-800 mb-4"
              >
                <FaArrowLeft className="mr-2" />
                Dokümanlara Dön
              </button>

              <h1 className="text-xl font-bold mb-2">{document?.name}</h1>
              
              <div className="flex items-center text-sm text-gray-600 mb-4">
                <FaEye className="mr-1" />
                {viewCount} görüntüleme
                <FaClock className="ml-4 mr-1" />
                {new Date(document?.created_at).toLocaleDateString('tr-TR')}
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-2 mb-6">
                <button
                  onClick={handleDownload}
                  className="flex items-center px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                  disabled={downloadProgress > 0}
                >
                  <FaDownload className="mr-1" />
                  {downloadProgress > 0 ? `${downloadProgress}%` : 'İndir'}
                </button>
                <button
                  onClick={handleShare}
                  className="flex items-center px-3 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  <FaShare className="mr-1" />
                  Paylaş
                </button>
                <button
                  onClick={handlePrint}
                  className="flex items-center px-3 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
                >
                  <FaPrint className="mr-1" />
                  Yazdır
                </button>
                {document?.can_edit && (
                  <button
                    onClick={handleEdit}
                    className="flex items-center px-3 py-2 bg-yellow-500 text-white rounded hover:bg-yellow-600"
                  >
                    <FaEdit className="mr-1" />
                    Düzenle
                  </button>
                )}
                {document?.can_delete && (
                  <button
                    onClick={handleDelete}
                    className="flex items-center px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                  >
                    <FaTrash className="mr-1" />
                    Sil
                  </button>
                )}
              </div>

              {/* Rating */}
              <div className="mb-6">
                <p className="text-sm font-medium mb-2">Değerlendirme</p>
                <div className="flex items-center space-x-1">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      onClick={() => handleRating(star)}
                      className={`text-2xl ${star <= rating ? 'text-yellow-500' : 'text-gray-300'} hover:text-yellow-500`}
                    >
                      <FaStar />
                    </button>
                  ))}
                  <button
                    onClick={handleBookmark}
                    className={`ml-4 text-2xl ${bookmarked ? 'text-blue-500' : 'text-gray-300'} hover:text-blue-500`}
                  >
                    <FaBookmark />
                  </button>
                </div>
              </div>

              {/* Document Info */}
              <div className="mb-6">
                <h3 className="font-medium mb-2">Doküman Bilgileri</h3>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Kategori:</strong> {document?.category_name}
                </p>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Boyut:</strong> {document?.size_formatted}
                </p>
                <p className="text-sm text-gray-600 mb-1">
                  <strong>Yükleyen:</strong> {document?.uploader_name}
                </p>
                {document?.tags?.length > 0 && (
                  <div className="mt-2">
                    <strong className="text-sm">Etiketler:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {document.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs"
                        >
                          <FaTag className="inline mr-1" />
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Description */}
              {document?.description && (
                <div className="mb-6">
                  <h3 className="font-medium mb-2">Açıklama</h3>
                  <p className="text-sm text-gray-600">{document.description}</p>
                </div>
              )}

              {/* Versions */}
              {versions.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-medium mb-2">Versiyonlar</h3>
                  <div className="space-y-2">
                    {versions.map((version) => (
                      <div
                        key={version.id}
                        className={`p-2 rounded cursor-pointer ${
                          version.id === document.id
                            ? 'bg-blue-50 border border-blue-200'
                            : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                        onClick={() => navigate(`/documents/${version.id}`)}
                      >
                        <p className="text-sm font-medium">v{version.version}</p>
                        <p className="text-xs text-gray-600">
                          {new Date(version.created_at).toLocaleDateString('tr-TR')}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Comments */}
              <div>
                <h3 className="font-medium mb-2">
                  <FaComment className="inline mr-1" />
                  Yorumlar ({comments.length})
                </h3>
                <form onSubmit={handleComment} className="mb-4">
                  <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg resize-none"
                    rows="3"
                    placeholder="Yorumunuzu yazın..."
                  />
                  <button
                    type="submit"
                    className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                  >
                    Yorum Ekle
                  </button>
                </form>
                <div className="space-y-3">
                  {comments.map((comment) => (
                    <div key={comment.id} className="bg-gray-50 rounded-lg p-3">
                      <div className="flex justify-between items-start mb-1">
                        <p className="font-medium text-sm">{comment.author_name}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(comment.created_at).toLocaleDateString('tr-TR')}
                        </p>
                      </div>
                      <p className="text-sm text-gray-700">{comment.content}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          {/* Toolbar */}
          <div className="bg-white shadow-sm border-b px-6 py-3 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="text-gray-600 hover:text-gray-800"
              >
                {showSidebar ? '⟨' : '⟩'}
              </button>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleZoom('out')}
                  className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200"
                >
                  -
                </button>
                <span className="min-w-[60px] text-center">{zoom}%</span>
                <button
                  onClick={() => handleZoom('in')}
                  className="px-3 py-1 bg-gray-100 rounded hover:bg-gray-200"
                >
                  +
                </button>
              </div>
            </div>
            <button
              onClick={toggleFullscreen}
              className="text-gray-600 hover:text-gray-800"
            >
              {fullscreen ? <FaCompress /> : <FaExpand />}
            </button>
          </div>

          {/* Document Viewer */}
          <div className="h-full overflow-auto bg-gray-100 p-4">
            {renderDocumentContent()}
          </div>
        </div>

        {/* Related Documents */}
        {!fullscreen && relatedDocs.length > 0 && (
          <div className="w-64 bg-white shadow-lg p-4 overflow-y-auto">
            <h3 className="font-medium mb-3">İlgili Dokümanlar</h3>
            <div className="space-y-3">
              {relatedDocs.map((doc) => (
                <div
                  key={doc.id}
                  className="cursor-pointer p-2 rounded hover:bg-gray-50"
                  onClick={() => navigate(`/documents/${doc.id}`)}
                >
                  <p className="text-sm font-medium truncate">{doc.name}</p>
                  <p className="text-xs text-gray-600">{doc.category_name}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentViewerPageV2;