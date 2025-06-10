// TODO: i18n - processed
/**
 * Image optimization utilities
 */
import React, { useState, useEffect } from 'react';
/**
 * Image formats and quality settings
 */import { useTranslation } from "react-i18next";
export const imageFormats = {
  webp: {
    quality: 0.85,
    supported: typeof window !== 'undefined' &&
    window.document.createElement('canvas').toDataURL('image/webp').indexOf('data:image/webp') === 0
  },
  avif: {
    quality: 0.85,
    supported: false // Need to detect AVIF support properly
  },
  jpeg: {
    quality: 0.85,
    supported: true
  },
  png: {
    quality: 0.95,
    supported: true
  }
};
/**
 * Responsive image sizes
 */
export const imageSizes = {
  thumbnail: { width: 150, height: 150 },
  small: { width: 320, height: 240 },
  medium: { width: 640, height: 480 },
  large: { width: 1024, height: 768 },
  xlarge: { width: 1920, height: 1080 },
  xxlarge: { width: 2560, height: 1440 }
};
/**
 * Image optimization utilities
 */
export const imageOptimizationUtils = {
  /**
   * Generate srcset for responsive images
   */
  generateSrcSet: (basePath, extension = 'jpg', sizes = ['small', 'medium', 'large']) => {
    return sizes.
    map((size) => {
      const dimensions = imageSizes[size];
      return `${basePath}-${dimensions.width}x${dimensions.height}.${extension} ${dimensions.width}w`;
    }).
    join(', ');
  },
  /**
   * Generate picture element with multiple formats
   */
  generatePictureElement: (basePath, alt, sizes = ['small', 'medium', 'large']) => {
    const formats = ['avif', 'webp', 'jpg'];
    return {
      sources: formats.slice(0, -1).map((format) => ({
        type: `image/${format}`,
        srcSet: imageOptimizationUtils.generateSrcSet(basePath, format, sizes)
      })),
      img: {
        src: `${basePath}-${imageSizes.medium.width}x${imageSizes.medium.height}.jpg`,
        srcSet: imageOptimizationUtils.generateSrcSet(basePath, 'jpg', sizes),
        alt
      }
    };
  },
  /**
   * Calculate optimal image dimensions
   */
  calculateDimensions: (originalWidth, originalHeight, maxWidth, maxHeight) => {
    const aspectRatio = originalWidth / originalHeight;
    let width = originalWidth;
    let height = originalHeight;
    if (width > maxWidth) {
      width = maxWidth;
      height = width / aspectRatio;
    }
    if (height > maxHeight) {
      height = maxHeight;
      width = height * aspectRatio;
    }
    return {
      width: Math.round(width),
      height: Math.round(height)
    };
  },
  /**
   * Convert image to different format
   */
  convertImageFormat: async (file, targetFormat = 'webp', quality = 0.85) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement('canvas');
          canvas.width = img.width;
          canvas.height = img.height;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0);
          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(new File([blob], file.name.replace(/\.[^/.]+$/, `.${targetFormat}`), {
                  type: `image/${targetFormat}`
                }));
              } else {
                reject(new Error(`Failed to convert to ${targetFormat}`));
              }
            },
            `image/${targetFormat}`,
            quality
          );
        };
        img.onerror = () => reject(new Error('Failed to load image'));
        img.src = e.target.result;
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  },
  /**
   * Resize image
   */
  resizeImage: async (file, maxWidth, maxHeight, quality = 0.85) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const dimensions = imageOptimizationUtils.calculateDimensions(
            img.width,
            img.height,
            maxWidth,
            maxHeight
          );
          const canvas = document.createElement('canvas');
          canvas.width = dimensions.width;
          canvas.height = dimensions.height;
          const ctx = canvas.getContext('2d');
          // Use better image scaling algorithm
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = 'high';
          ctx.drawImage(img, 0, 0, dimensions.width, dimensions.height);
          canvas.toBlob(
            (blob) => {
              if (blob) {
                resolve(new File([blob], file.name, { type: file.type }));
              } else {
                reject(new Error('Failed to resize image'));
              }
            },
            file.type,
            quality
          );
        };
        img.onerror = () => reject(new Error('Failed to load image'));
        img.src = e.target.result;
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsDataURL(file);
    });
  },
  /**
   * Optimize image for web
   */
  optimizeForWeb: async (file, options = {}) => {
    const {
      maxWidth = 1920,
      maxHeight = 1080,
      targetFormat = 'webp',
      quality = 0.85,
      generateSizes = true
    } = options;
    try {
      // Resize if needed
      let optimizedFile = file;
      const img = new Image();
      const imageUrl = URL.createObjectURL(file);
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = imageUrl;
      });
      if (img.width > maxWidth || img.height > maxHeight) {
        optimizedFile = await imageOptimizationUtils.resizeImage(
          file,
          maxWidth,
          maxHeight,
          quality
        );
      }
      // Convert format if needed
      if (file.type !== `image/${targetFormat}` && imageFormats[targetFormat].supported) {
        optimizedFile = await imageOptimizationUtils.convertImageFormat(
          optimizedFile,
          targetFormat,
          quality
        );
      }
      // Generate multiple sizes if requested
      if (generateSizes) {
        const sizes = await imageOptimizationUtils.generateResponsiveSizes(
          optimizedFile,
          ['thumbnail', 'small', 'medium', 'large']
        );
        return { original: optimizedFile, sizes };
      }
      URL.revokeObjectURL(imageUrl);
      return optimizedFile;
    } catch (error) {
      console.error('Image optimization failed:', error);
      return file; // Return original file if optimization fails
    }
  },
  /**
   * Generate responsive image sizes
   */
  generateResponsiveSizes: async (file, sizeNames = ['small', 'medium', 'large']) => {
    const sizes = {};
    for (const sizeName of sizeNames) {
      const size = imageSizes[sizeName];
      if (size) {
        try {
          sizes[sizeName] = await imageOptimizationUtils.resizeImage(
            file,
            size.width,
            size.height
          );
        } catch (error) {
          console.error(`Failed to generate ${sizeName} size:`, error);
        }
      }
    }
    return sizes;
  },
  /**
   * Extract image metadata
   */
  extractMetadata: async (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          resolve({
            width: img.width,
            height: img.height,
            aspectRatio: img.width / img.height,
            size: file.size,
            type: file.type,
            name: file.name
          });
        };
        img.onerror = () => resolve(null);
        img.src = e.target.result;
      };
      reader.onerror = () => resolve(null);
      reader.readAsDataURL(file);
    });
  }
};
/**
 * Optimized image component
 */
export const OptimizedImage = ({
  src,
  alt,
  width,
  height,
  sizes,
  loading = 'lazy',
  placeholder,
  className,
  style,
  onLoad,
  onError
}) => {const { t } = useTranslation();
  const [currentSrc, setCurrentSrc] = useState(placeholder || src);
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  useEffect(() => {
    const img = new Image();
    img.onload = () => {
      setCurrentSrc(src);
      setIsLoaded(true);
      onLoad && onLoad();
    };
    img.onerror = () => {
      setHasError(true);
      onError && onError();
    };
    img.src = src;
  }, [src, onLoad, onError]);
  const imgProps = {
    src: currentSrc,
    alt,
    width,
    height,
    sizes: sizes || '(max-width: 768px) 100vw, 50vw',
    loading,
    className,
    style: {
      ...style,
      filter: isLoaded ? 'none' : 'blur(10px)',
      transition: 'filter 0.3s ease-in-out'
    }
  };
  if (hasError) {
    return (
      <div
        className={className}
        style={{
          ...style,
          width,
          height,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: '#f0f0f0',
          color: '#666'
        }}>{t("components.failed_to_load_image")}


      </div>);

  }
  // Use picture element for better format support
  const formats = ['avif', 'webp'];
  const basePath = src.replace(/\.[^/.]+$/, '');
  const extension = src.split('.').pop();
  return (
    <picture>
      {formats.map((format) =>
      imageFormats[format].supported &&
      <source
        key={format}
        type={`image/${format}`}
        srcSet={`${basePath}.${format}`} />


      )}
      <img {...imgProps} />
    </picture>);

};
/**
 * Image upload optimizer
 */
export const ImageUploadOptimizer = ({
  onUpload,
  maxWidth = 1920,
  maxHeight = 1080,
  maxFileSize = 5 * 1024 * 1024, // 5MB
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp'],
  quality = 0.85,
  targetFormat = 'webp'
}) => {const { t } = useTranslation();
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = React.useRef(null);
  const handleFile = async (file) => {
    // Validate file type
    if (!acceptedFormats.includes(file.type)) {
      console.error('Invalid file type');
      return;
    }
    // Validate file size
    if (file.size > maxFileSize) {
      console.error('File size exceeds limit');
      return;
    }
    try {
      const optimizedFile = await imageOptimizationUtils.optimizeForWeb(file, {
        maxWidth,
        maxHeight,
        targetFormat,
        quality
      });
      const metadata = await imageOptimizationUtils.extractMetadata(optimizedFile);
      onUpload(optimizedFile, metadata);
    } catch (error) {
      console.error('Failed to optimize image:', error);
      onUpload(file); // Upload original if optimization fails
    }
  };
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    files.forEach(handleFile);
  };
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    files.forEach(handleFile);
  };
  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      style={{
        border: `2px dashed ${isDragging ? '#0066cc' : '#ccc'}`,
        borderRadius: '8px',
        padding: '20px',
        textAlign: 'center',
        cursor: 'pointer',
        transition: 'border-color 0.3s ease'
      }}
      onClick={() => fileInputRef.current?.click()}>

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={acceptedFormats.join(',')}
        onChange={handleFileSelect}
        style={{ display: 'none' }} />

      <p>
        {isDragging ? 'Drop images here' : 'Drag & drop images or click to upload'}
      </p>
      <p style={{ fontSize: '14px', color: '#666', marginTop: '10px' }}>{t("utils.max_size")}
        {maxFileSize / (1024 * 1024)}{t("utils.mb_formats")}
        {acceptedFormats.map((f) => f.split('/')[1]).join(', ')}
      </p>
    </div>);

};
/**
 * Image performance monitor
 */
export const imagePerformanceMonitor = {
  metrics: {
    imagesLoaded: 0,
    imagesFailed: 0,
    totalLoadTime: 0,
    totalSize: 0,
    formatBreakdown: {}
  },
  trackImageLoad: (src, loadTime, size, format) => {
    imagePerformanceMonitor.metrics.imagesLoaded++;
    imagePerformanceMonitor.metrics.totalLoadTime += loadTime;
    imagePerformanceMonitor.metrics.totalSize += size;
    if (!imagePerformanceMonitor.metrics.formatBreakdown[format]) {
      imagePerformanceMonitor.metrics.formatBreakdown[format] = 0;
    }
    imagePerformanceMonitor.metrics.formatBreakdown[format]++;
  },
  trackImageError: (src) => {
    imagePerformanceMonitor.metrics.imagesFailed++;
  },
  getMetrics: () => imagePerformanceMonitor.metrics,
  getAverageLoadTime: () => {
    const { imagesLoaded, totalLoadTime } = imagePerformanceMonitor.metrics;
    return imagesLoaded > 0 ? totalLoadTime / imagesLoaded : 0;
  },
  getAverageSize: () => {
    const { imagesLoaded, totalSize } = imagePerformanceMonitor.metrics;
    return imagesLoaded > 0 ? totalSize / imagesLoaded : 0;
  },
  reset: () => {
    imagePerformanceMonitor.metrics = {
      imagesLoaded: 0,
      imagesFailed: 0,
      totalLoadTime: 0,
      totalSize: 0,
      formatBreakdown: {}
    };
  }
};
export default {
  imageFormats,
  imageSizes,
  imageOptimizationUtils,
  OptimizedImage,
  ImageUploadOptimizer,
  imagePerformanceMonitor
};