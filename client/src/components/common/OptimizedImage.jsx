import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
/**
 * Optimized image component with lazy loading and progressive enhancement
 */
export const OptimizedImage = ({
  src,
  alt,
  width,
  height,
  className = '',
  objectFit = 'cover',
  placeholder = 'blur',
  blurDataUrl,
  priority = false,
  onLoad,
  onError,
  srcSet,
  sizes,
  loading = 'lazy',
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [error, setError] = useState(false);
  const imgRef = useRef(null);
  const observerRef = useRef(null);
  // Generate blur placeholder if not provided
  const defaultBlurDataUrl = `data:image/svg+xml;base64,${btoa(
    `<svg width="${width || 100}" height="${height || 100}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f3f4f6"/>
    </svg>`
  )}`;
  const placeholderSrc = blurDataUrl || defaultBlurDataUrl;
  useEffect(() => {
    if (priority || loading === 'eager') {
      setIsInView(true);
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(entry.isIntersecting);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0,
        rootMargin: '50px'
      }
    );
    observerRef.current = observer;
    if (imgRef.current) {
      observer.observe(imgRef.current);
    }
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [priority, loading]);
  const handleLoad = (e) => {
    setIsLoaded(true);
    if (onLoad) onLoad(e);
  };
  const handleError = (e) => {
    setError(true);
    if (onError) onError(e);
  };
  const style = {
    objectFit,
    width: width || '100%',
    height: height || 'auto'
  };
  return (
    <div 
      ref={imgRef}
      className={`relative overflow-hidden ${className}`}
      style={{ width: width || '100%', height: height || 'auto' }}
    >
      {/* Placeholder/Blur Background */}
      {placeholder === 'blur' && !isLoaded && (
        <img
          src={placeholderSrc}
          alt=""
          className="absolute inset-0 w-full h-full"
          style={style}
          aria-hidden="true"
        />
      )}
      {/* Skeleton Placeholder */}
      {placeholder === 'skeleton' && !isLoaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
      {/* Main Image */}
      {isInView && !error && (
        <motion.img
          src={src}
          alt={alt}
          width={width}
          height={height}
          className={className}
          style={style}
          srcSet={srcSet}
          sizes={sizes}
          onLoad={handleLoad}
          onError={handleError}
          initial={{ opacity: 0 }}
          animate={{ opacity: isLoaded ? 1 : 0 }}
          transition={{ duration: 0.3 }}
          {...props}
        />
      )}
      {/* Error State */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <svg
              className="w-12 h-12 mx-auto text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p className="mt-2 text-sm text-gray-600">Failed to load image</p>
          </div>
        </div>
      )}
    </div>
  );
};
/**
 * Picture component for responsive images
 */
export const ResponsivePicture = ({
  sources = [],
  fallbackSrc,
  alt,
  className,
  ...props
}) => {
  return (
    <picture>
      {sources.map((source, index) => (
        <source
          key={index}
          srcSet={source.srcSet}
          media={source.media}
          type={source.type}
        />
      ))}
      <OptimizedImage
        src={fallbackSrc}
        alt={alt}
        className={className}
        {...props}
      />
    </picture>
  );
};
/**
 * Background image component with optimization
 */
export const OptimizedBackgroundImage = ({
  src,
  className = '',
  children,
  overlay = false,
  overlayColor = 'rgba(0, 0, 0, 0.5)',
  minHeight = '400px',
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  useEffect(() => {
    const img = new Image();
    img.src = src;
    img.onload = () => setIsLoaded(true);
  }, [src]);
  return (
    <div
      className={`relative ${className}`}
      style={{
        minHeight,
        backgroundImage: isLoaded ? `url(${src})` : 'none',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundColor: isLoaded ? 'transparent' : '#f3f4f6'
      }}
      {...props}
    >
      {!isLoaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
      {overlay && (
        <div
          className="absolute inset-0"
          style={{ backgroundColor: overlayColor }}
        />
      )}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
};
/**
 * Image gallery with lazy loading
 */
export const OptimizedImageGallery = ({
  images = [],
  columns = 3,
  gap = 16,
  ...imageProps
}) => {
  return (
    <div
      className="grid"
      style={{
        gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))`,
        gap: `${gap}px`
      }}
    >
      {images.map((image, index) => (
        <OptimizedImage
          key={index}
          src={image.src}
          alt={image.alt || `Image ${index + 1}`}
          priority={index < columns} // First row gets priority
          {...imageProps}
          {...image}
        />
      ))}
    </div>
  );
};
/**
 * Avatar component with optimization
 */
export const OptimizedAvatar = ({
  src,
  alt,
  size = 'md',
  fallback,
  className = '',
  ...props
}) => {
  const sizes = {
    xs: 24,
    sm: 32,
    md: 40,
    lg: 48,
    xl: 64
  };
  const dimension = sizes[size] || sizes.md;
  return (
    <OptimizedImage
      src={src}
      alt={alt}
      width={dimension}
      height={dimension}
      className={`rounded-full ${className}`}
      fallback={fallback}
      {...props}
    />
  );
};