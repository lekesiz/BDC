import React, { useState, useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';

/**
 * Optimized Image Component with lazy loading and progressive enhancement
 */
export const OptimizedImage = ({
  src,
  alt,
  className,
  width,
  height,
  priority = false,
  placeholder = 'blur',
  blurDataURL,
  onLoad,
  onError,
  sizes,
  srcSet,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef(null);

  // Use Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || !imgRef.current) {
      setIsInView(true);
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.01,
        rootMargin: '50px',
      }
    );

    observer.observe(imgRef.current);

    return () => {
      observer.disconnect();
    };
  }, [priority]);

  const handleLoad = (e) => {
    setIsLoaded(true);
    onLoad?.(e);
  };

  const handleError = (e) => {
    setHasError(true);
    onError?.(e);
  };

  // Generate blur placeholder if not provided
  const getPlaceholder = () => {
    if (placeholder === 'blur' && blurDataURL) {
      return blurDataURL;
    }
    // Default gray placeholder
    return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMSIgaGVpZ2h0PSIxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9IiNlNWU3ZWIiLz48L3N2Zz4=';
  };

  if (hasError) {
    return (
      <div
        className={cn(
          'bg-gray-200 flex items-center justify-center',
          className
        )}
        style={{ width, height }}
      >
        <svg
          className="w-8 h-8 text-gray-400"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    );
  }

  return (
    <div
      ref={imgRef}
      className={cn('relative overflow-hidden', className)}
      style={{ width, height }}
    >
      {/* Placeholder/Blur Background */}
      {placeholder === 'blur' && !isLoaded && (
        <img
          src={getPlaceholder()}
          alt=""
          className="absolute inset-0 w-full h-full object-cover filter blur-xl scale-110"
          aria-hidden="true"
        />
      )}

      {/* Main Image */}
      {isInView && (
        <img
          src={src}
          alt={alt}
          width={width}
          height={height}
          sizes={sizes}
          srcSet={srcSet}
          loading={priority ? 'eager' : 'lazy'}
          decoding="async"
          onLoad={handleLoad}
          onError={handleError}
          className={cn(
            'transition-opacity duration-300',
            isLoaded ? 'opacity-100' : 'opacity-0',
            className
          )}
          {...props}
        />
      )}

      {/* Loading Skeleton */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
    </div>
  );
};

/**
 * Picture component for responsive images with multiple formats
 */
export const OptimizedPicture = ({
  src,
  alt,
  className,
  width,
  height,
  priority = false,
  sizes,
  formats = ['webp', 'jpeg'],
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);

  // Generate source URLs for different formats
  const getSrcForFormat = (format) => {
    const lastDot = src.lastIndexOf('.');
    if (lastDot === -1) return src;
    return `${src.substring(0, lastDot)}.${format}`;
  };

  return (
    <picture className={className}>
      {/* WebP and other modern formats */}
      {formats.map((format) => (
        <source
          key={format}
          srcSet={getSrcForFormat(format)}
          type={`image/${format}`}
          sizes={sizes}
        />
      ))}

      {/* Fallback image */}
      <OptimizedImage
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        className={className}
        onLoad={() => setIsLoaded(true)}
        {...props}
      />
    </picture>
  );
};

/**
 * Background image component with lazy loading
 */
export const OptimizedBackgroundImage = ({
  src,
  className,
  children,
  overlay = false,
  overlayOpacity = 0.5,
  ...props
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      {
        threshold: 0.01,
        rootMargin: '50px',
      }
    );

    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!isInView) return;

    const img = new Image();
    img.src = src;
    img.onload = () => setIsLoaded(true);
  }, [isInView, src]);

  return (
    <div
      ref={containerRef}
      className={cn('relative', className)}
      {...props}
    >
      {/* Background image */}
      {isInView && (
        <div
          className={cn(
            'absolute inset-0 bg-cover bg-center transition-opacity duration-500',
            isLoaded ? 'opacity-100' : 'opacity-0'
          )}
          style={{ backgroundImage: `url(${src})` }}
        />
      )}

      {/* Overlay */}
      {overlay && (
        <div
          className="absolute inset-0 bg-black"
          style={{ opacity: overlayOpacity }}
        />
      )}

      {/* Loading placeholder */}
      {!isLoaded && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  );
};

/**
 * Avatar component with optimized loading
 */
export const OptimizedAvatar = ({
  src,
  alt,
  size = 'md',
  fallback,
  className,
  ...props
}) => {
  const [hasError, setHasError] = useState(false);

  const sizeClasses = {
    xs: 'w-6 h-6',
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  };

  const getFallbackContent = () => {
    if (fallback) return fallback;
    if (alt) {
      const initials = alt
        .split(' ')
        .map((word) => word[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
      return initials;
    }
    return '?';
  };

  if (hasError || !src) {
    return (
      <div
        className={cn(
          'rounded-full bg-gray-300 flex items-center justify-center text-gray-600 font-medium',
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {getFallbackContent()}
      </div>
    );
  }

  return (
    <OptimizedImage
      src={src}
      alt={alt}
      className={cn('rounded-full object-cover', sizeClasses[size], className)}
      onError={() => setHasError(true)}
      priority
      {...props}
    />
  );
};

/**
 * Image gallery with virtualization for large collections
 */
export const OptimizedImageGallery = ({
  images,
  columns = 3,
  gap = 4,
  className,
  onImageClick,
}) => {
  const [loadedImages, setLoadedImages] = useState(new Set());

  const handleImageLoad = (index) => {
    setLoadedImages((prev) => new Set(prev).add(index));
  };

  return (
    <div
      className={cn(
        'grid',
        `grid-cols-${columns}`,
        `gap-${gap}`,
        className
      )}
    >
      {images.map((image, index) => (
        <div
          key={image.id || index}
          className="relative aspect-square cursor-pointer group"
          onClick={() => onImageClick?.(image, index)}
        >
          <OptimizedImage
            src={image.src}
            alt={image.alt || `Image ${index + 1}`}
            className="w-full h-full object-cover rounded-lg group-hover:opacity-90 transition-opacity"
            onLoad={() => handleImageLoad(index)}
          />
          
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-200 rounded-lg" />
        </div>
      ))}
    </div>
  );
};

// Utility function to generate responsive image sizes
export const generateImageSizes = (maxWidth = 1200) => {
  const breakpoints = [640, 768, 1024, 1280, 1536];
  const sizes = breakpoints
    .filter((bp) => bp <= maxWidth)
    .map((bp) => `(max-width: ${bp}px) ${bp}px`)
    .join(', ');
  
  return `${sizes}, ${maxWidth}px`;
};

// Utility function to generate srcSet for responsive images
export const generateSrcSet = (baseUrl, widths = [320, 640, 960, 1280, 1920]) => {
  return widths
    .map((width) => {
      const url = baseUrl.includes('?')
        ? `${baseUrl}&w=${width}`
        : `${baseUrl}?w=${width}`;
      return `${url} ${width}w`;
    })
    .join(', ');
};