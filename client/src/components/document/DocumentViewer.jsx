import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { FaDownload, FaExpand, FaCompress, FaPrint, FaSearch, FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import { toast } from 'react-toastify';
/**
 * DocumentViewer - Reusable component for viewing different types of documents
 * 
 * Supports:
 * - PDF files with pagination
 * - Images with zoom
 * - Office documents via Google Docs Viewer
 * - Text files
 * - Fallback for unsupported file types
 */
const DocumentViewer = ({
  document,
  onDownload,
  showToolbar = true,
  initialZoom = 100,
  height = '800px',
  className = '',
}) => {
  const viewerRef = useRef(null);
  const [fullscreen, setFullscreen] = useState(false);
  const [zoom, setZoom] = useState(initialZoom);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(document?.page_count || 1);
  const [isLoading, setIsLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [isTextFile, setIsTextFile] = useState(false);
  const [textContent, setTextContent] = useState('');
  useEffect(() => {
    // Reset state when document changes
    setCurrentPage(1);
    setZoom(initialZoom);
    setIsLoading(true);
    setTotalPages(document?.page_count || 1);
    // Check if it's a text file
    if (document?.type === 'txt' || document?.mime_type === 'text/plain') {
      setIsTextFile(true);
      fetchTextContent();
    } else {
      setIsTextFile(false);
    }
    // Set up PDF.js if it's a PDF document
    if (document?.type === 'pdf') {
      initPdfViewer();
    }
  }, [document?.id]);
  // Function to fetch text content for text files
  const fetchTextContent = async () => {
    if (!document?.url) return;
    try {
      const response = await fetch(document.url);
      const text = await response.text();
      setTextContent(text);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching text content:', error);
      toast.error('Metin içeriği yüklenemedi');
      setIsLoading(false);
    }
  };
  // Initialize PDF.js viewer if needed
  const initPdfViewer = () => {
    // In a real implementation, this would initialize PDF.js
    // For now, we'll just simulate loading
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };
  const handleZoom = (direction) => {
    if (direction === 'in' && zoom < 200) {
      setZoom(prev => prev + 25);
    } else if (direction === 'out' && zoom > 50) {
      setZoom(prev => prev - 25);
    } else if (direction === 'reset') {
      setZoom(100);
    }
  };
  const handleDownload = () => {
    if (onDownload) {
      onDownload();
    } else if (document?.url) {
      // Default download behavior
      const link = document.createElement('a');
      link.href = document.url;
      link.setAttribute('download', document.name || 'document');
      document.body.appendChild(link);
      link.click();
      link.remove();
    }
  };
  const toggleFullscreen = () => {
    if (!fullscreen) {
      viewerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
    setFullscreen(!fullscreen);
  };
  const handlePrint = () => {
    window.print();
  };
  const navigatePage = (direction) => {
    if (direction === 'next' && currentPage < totalPages) {
      setCurrentPage(prev => prev + 1);
    } else if (direction === 'prev' && currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  };
  const handleSearch = (e) => {
    e.preventDefault();
    // In a real implementation, this would use PDF.js search functionality
    // or highlight text in the document
    toast.info(`Aranan: ${searchText}`);
  };
  // Handle document loading error
  const handleError = () => {
    setIsLoading(false);
    toast.error('Doküman yüklenemedi');
  };
  // Render the appropriate viewer based on file type
  const renderContent = () => {
    if (!document || !document.url) {
      return (
        <div className="flex flex-col items-center justify-center h-full">
          <p className="text-gray-500">Doküman bulunamadı</p>
        </div>
      );
    }
    if (isLoading) {
      return (
        <div className="flex flex-col items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
          <p className="text-gray-500">Doküman yükleniyor...</p>
        </div>
      );
    }
    switch (document.type) {
      case 'pdf':
        return (
          <div className="relative">
            <iframe
              src={`${document.url}#page=${currentPage}`}
              className="w-full border-0"
              style={{ 
                height,
                transform: `scale(${zoom / 100})`, 
                transformOrigin: 'top left' 
              }}
              title={document.name || 'PDF Document'}
              onError={handleError}
              data-cy="document-pdf-viewer"
            />
            {totalPages > 1 && (
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white shadow-lg rounded-lg px-4 py-2 flex items-center space-x-4">
                <button
                  onClick={() => navigatePage('prev')}
                  disabled={currentPage === 1}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                  aria-label="Previous page"
                  data-cy="previous-page-button"
                >
                  <FaChevronLeft />
                </button>
                <span>
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => navigatePage('next')}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
                  aria-label="Next page"
                  data-cy="next-page-button"
                >
                  <FaChevronRight />
                </button>
              </div>
            )}
          </div>
        );
      case 'image':
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
      case 'svg':
        return (
          <div className="flex justify-center overflow-auto" style={{ height }}>
            <img
              src={document.url}
              alt={document.name || 'Image'}
              className="max-h-full"
              style={{ transform: `scale(${zoom / 100})` }}
              onError={handleError}
              data-cy="document-image-viewer"
            />
          </div>
        );
      case 'txt':
        return (
          <div 
            className="p-4 bg-white rounded shadow overflow-auto"
            style={{ height, fontSize: `${zoom / 100}rem` }}
            data-cy="document-text-viewer"
          >
            {textContent.split('\n').map((line, index) => (
              <div key={index} className="whitespace-pre-wrap">
                {line || ' '}
              </div>
            ))}
          </div>
        );
      case 'doc':
      case 'docx':
      case 'xls':
      case 'xlsx':
      case 'ppt':
      case 'pptx':
        return (
          <iframe
            src={`https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(document.url)}`}
            className="w-full border-0"
            style={{ height }}
            title={document.name || 'Office Document'}
            onError={handleError}
            data-cy="document-office-viewer"
          />
        );
      case 'html':
        return (
          <iframe
            src={document.url}
            className="w-full border-0"
            style={{ height }}
            title={document.name || 'HTML Document'}
            sandbox="allow-same-origin allow-scripts"
            onError={handleError}
            data-cy="document-html-viewer"
          />
        );
      default:
        // Fallback for unsupported file types
        return (
          <div className="flex flex-col items-center justify-center h-full p-8">
            <div className="text-center py-16">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-xl mb-4">Bu dosya türü önizlenemez</p>
              <p className="text-gray-600 mb-6">
                {document.mime_type || document.type} formatındaki dosyalar için önizleme kullanılamıyor.
              </p>
              <button
                onClick={handleDownload}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 inline-flex items-center"
                data-cy="download-button"
              >
                <FaDownload className="mr-2" />
                Dosyayı İndir
              </button>
            </div>
          </div>
        );
    }
  };
  return (
    <div 
      ref={viewerRef}
      className={`document-viewer ${className} border rounded-lg overflow-hidden bg-gray-50 ${fullscreen ? 'fixed inset-0 z-50' : ''}`}
      data-cy="document-viewer"
    >
      {/* Toolbar */}
      {showToolbar && (
        <div className="bg-white border-b p-2 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <button
                onClick={() => handleZoom('out')}
                className="p-1.5 rounded-md hover:bg-gray-100"
                aria-label="Zoom out"
                title="Küçült"
                data-cy="zoom-out-button"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </button>
              <span className="text-sm min-w-[50px] text-center">{zoom}%</span>
              <button
                onClick={() => handleZoom('in')}
                className="p-1.5 rounded-md hover:bg-gray-100"
                aria-label="Zoom in"
                title="Büyüt"
                data-cy="zoom-in-button"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </button>
              <button
                onClick={() => handleZoom('reset')}
                className="text-xs p-1.5 rounded-md hover:bg-gray-100"
                aria-label="Reset zoom"
                title="Sıfırla"
                data-cy="zoom-reset-button"
              >
                100%
              </button>
            </div>
            {document?.type === 'pdf' && (
              <div className="flex items-center ml-4">
                <button
                  onClick={() => navigatePage('prev')}
                  disabled={currentPage === 1}
                  className="p-1.5 rounded-md hover:bg-gray-100 disabled:opacity-50"
                  aria-label="Previous page"
                  title="Önceki sayfa"
                  data-cy="toolbar-prev-page"
                >
                  <FaChevronLeft />
                </button>
                <span className="text-sm mx-2">
                  {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => navigatePage('next')}
                  disabled={currentPage === totalPages}
                  className="p-1.5 rounded-md hover:bg-gray-100 disabled:opacity-50"
                  aria-label="Next page"
                  title="Sonraki sayfa"
                  data-cy="toolbar-next-page"
                >
                  <FaChevronRight />
                </button>
              </div>
            )}
            {(document?.type === 'pdf' || isTextFile) && (
              <form onSubmit={handleSearch} className="ml-4 flex items-center">
                <input
                  type="text"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  placeholder="Ara..."
                  className="border rounded-l-md px-2 py-1 text-sm w-32"
                  data-cy="search-input"
                />
                <button
                  type="submit"
                  className="bg-blue-500 text-white p-1 rounded-r-md hover:bg-blue-600"
                  aria-label="Search document"
                  title="Ara"
                  data-cy="search-button"
                >
                  <FaSearch />
                </button>
              </form>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownload}
              className="p-1.5 rounded-md hover:bg-gray-100"
              aria-label="Download document"
              title="İndir"
              data-cy="toolbar-download"
            >
              <FaDownload />
            </button>
            <button
              onClick={handlePrint}
              className="p-1.5 rounded-md hover:bg-gray-100"
              aria-label="Print document"
              title="Yazdır"
              data-cy="toolbar-print"
            >
              <FaPrint />
            </button>
            <button
              onClick={toggleFullscreen}
              className="p-1.5 rounded-md hover:bg-gray-100"
              aria-label={fullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
              title={fullscreen ? 'Tam ekrandan çık' : 'Tam ekran'}
              data-cy="toolbar-fullscreen"
            >
              {fullscreen ? <FaCompress /> : <FaExpand />}
            </button>
          </div>
        </div>
      )}
      {/* Document Content */}
      <div className="document-content">
        {renderContent()}
      </div>
    </div>
  );
};
DocumentViewer.propTypes = {
  /** Document object with url, type, name, page_count properties */
  document: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    url: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    name: PropTypes.string,
    page_count: PropTypes.number,
    mime_type: PropTypes.string
  }).isRequired,
  /** Custom download handler function */
  onDownload: PropTypes.func,
  /** Show or hide the toolbar */
  showToolbar: PropTypes.bool,
  /** Initial zoom level (percentage) */
  initialZoom: PropTypes.number,
  /** Height of the viewer */
  height: PropTypes.string,
  /** Additional CSS classes */
  className: PropTypes.string
};
export default DocumentViewer;