// TODO: i18n - processed
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useIntersectionObserver } from 'react-intersection-observer';
import { cn } from '@/lib/utils';
import { useMobile } from '../components/MobileProvider';

/**
 * MobileImageOptimizer - Comprehensive image optimization for mobile devices
 * Features responsive images, lazy loading, progressive enhancement, and format detection
 */import { useTranslation } from "react-i18next";
export const MobileImageOptimizer = ({
  src,
  alt,
  className,
  sizes = '100vw',
  priority = false,
  placeholder = 'blur',
  blurDataURL,
  quality = 75,
  formats = ['webp', 'jpg'],
  breakpoints = {
    sm: 640,
    md: 768,
    lg: 1024,
    xl: 1280
  },
  aspectRatio,
  objectFit = 'cover',
  loading = 'lazy',
  fade = true,
  onLoad,
  onError,
  ...props
}) => {const { t } = useTranslation();
  const {
    networkStatus,
    performance,
    screenSize,
    shouldReduceAnimations
  } = useMobile();

  const [imageState, setImageState] = useState({
    loaded: false,
    error: false,
    currentSrc: null
  });

  const [shouldLoadHiRes, setShouldLoadHiRes] = useState(false);
  const imgRef = useRef(null);
  const lowResRef = useRef(null);

  // Intersection observer for lazy loading
  const { ref: intersectionRef, inView } = useIntersectionObserver({
    threshold: 0.1,
    rootMargin: '50px',
    triggerOnce: true,
    skip: priority
  });

  // Determine optimal image quality based on device and network
  const getOptimalQuality = useCallback(() => {
    if (networkStatus.saveData || networkStatus.effectiveType === 'slow-2g') {
      return Math.min(quality * 0.6, 40);
    }
    if (networkStatus.effectiveType === '2g') {
      return Math.min(quality * 0.7, 50);
    }
    if (performance.isSlowDevice) {
      return Math.min(quality * 0.8, 60);
    }
    return quality;
  }, [networkStatus, performance, quality]);

  // Generate responsive image sources
  const generateSrcSet = useCallback((baseSrc, format = 'jpg') => {
    const optimalQuality = getOptimalQuality();
    const devicePixelRatio = window.devicePixelRatio || 1;

    return Object.entries(breakpoints).
    map(([name, width]) => {
      // Adjust width for device pixel ratio but cap at 2x for performance
      const targetWidth = Math.round(width * Math.min(devicePixelRatio, 2));
      return `${generateImageUrl(baseSrc, targetWidth, optimalQuality, format)} ${width}w`;
    }).
    join(', ');
  }, [breakpoints, getOptimalQuality]);

  // Generate optimized image URL
  const generateImageUrl = useCallback((baseSrc, width, quality, format) => {
    // This would integrate with your image optimization service
    // For now, we'll return the original src with query parameters
    const url = new URL(baseSrc, window.location.origin);
    url.searchParams.set('w', width);
    url.searchParams.set('q', quality);
    url.searchParams.set('f', format);
    return url.toString();
  }, []);

  // Check if browser supports format
  const supportsFormat = useCallback((format) => {
    if (format === 'webp') {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }
    if (format === 'avif') {
      const canvas = document.createElement('canvas');
      canvas.width = 1;
      canvas.height = 1;
      return canvas.toDataURL('image/avif').indexOf('data:image/avif') === 0;
    }
    return true;
  }, []);

  // Get best supported format
  const getBestFormat = useCallback(() => {
    for (const format of formats) {
      if (supportsFormat(format)) {
        return format;
      }
    }
    return 'jpg';
  }, [formats, supportsFormat]);

  // Generate low resolution placeholder
  const generateLowResPlaceholder = useCallback((baseSrc) => {
    return generateImageUrl(baseSrc, 40, 10, 'jpg');
  }, [generateImageUrl]);

  // Handle image load
  const handleImageLoad = useCallback((event) => {
    setImageState((prev) => ({ ...prev, loaded: true }));
    onLoad?.(event);
  }, [onLoad]);

  // Handle image error
  const handleImageError = useCallback((event) => {
    setImageState((prev) => ({ ...prev, error: true }));
    onError?.(event);
  }, [onError]);

  // Load high resolution image when appropriate
  useEffect(() => {
    if (inView || priority) {
      // Delay high-res loading on slow connections
      const delay = networkStatus.effectiveType === 'slow-2g' ? 2000 :
      networkStatus.effectiveType === '2g' ? 1000 : 0;

      setTimeout(() => {
        setShouldLoadHiRes(true);
      }, delay);
    }
  }, [inView, priority, networkStatus.effectiveType]);

  // Preload critical images
  useEffect(() => {
    if (priority && src) {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'image';
      link.href = src;
      document.head.appendChild(link);

      return () => {
        document.head.removeChild(link);
      };
    }
  }, [priority, src]);

  const bestFormat = getBestFormat();
  const lowResSrc = generateLowResPlaceholder(src);
  const srcSet = generateSrcSet(src, bestFormat);

  return (
    <div
      ref={intersectionRef}
      className={cn(
        'relative overflow-hidden',
        aspectRatio && `aspect-${aspectRatio}`,
        className
      )}
      {...props}>

      {/* Low resolution placeholder */}
      {placeholder === 'blur' && (shouldLoadHiRes || priority) &&
      <img
        ref={lowResRef}
        src={blurDataURL || lowResSrc}
        alt=""
        className={cn(
          'absolute inset-0 w-full h-full object-cover filter blur-sm scale-110',
          'transition-opacity duration-500',
          imageState.loaded ? 'opacity-0' : 'opacity-100'
        )}
        style={{ objectFit }}
        aria-hidden="true" />

      }

      {/* Color placeholder */}
      {placeholder === 'empty' && !imageState.loaded &&
      <div
        className="absolute inset-0 bg-muted animate-pulse"
        aria-hidden="true" />

      }

      {/* Main image */}
      {(shouldLoadHiRes || priority) &&
      <picture>
          {/* WebP source */}
          {supportsFormat('webp') &&
        <source
          srcSet={generateSrcSet(src, 'webp')}
          sizes={sizes}
          type="image/webp" />

        }
          
          {/* AVIF source */}
          {supportsFormat('avif') &&
        <source
          srcSet={generateSrcSet(src, 'avif')}
          sizes={sizes}
          type="image/avif" />

        }
          
          {/* Fallback */}
          <img
          ref={imgRef}
          src={src}
          srcSet={srcSet}
          sizes={sizes}
          alt={alt}
          loading={priority ? 'eager' : loading}
          onLoad={handleImageLoad}
          onError={handleImageError}
          className={cn(
            'w-full h-full object-cover',
            fade && !shouldReduceAnimations && 'transition-opacity duration-500',
            imageState.loaded ? 'opacity-100' : 'opacity-0',
            imageState.error && 'hidden'
          )}
          style={{ objectFit }} />

        </picture>
      }

      {/* Error fallback */}
      {imageState.error &&
      <div className="absolute inset-0 flex items-center justify-center bg-muted text-muted-foreground">
          <div className="text-center">
            <div className="text-2xl mb-2">📷</div>
            <div className="text-sm">{t("components.failed_to_load_image")}</div>
          </div>
        </div>
      }

      {/* Loading indicator */}
      {!imageState.loaded && !imageState.error && (shouldLoadHiRes || priority) &&
      <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <div className={cn(
          'w-8 h-8 border-2 border-primary border-t-transparent rounded-full',
          !shouldReduceAnimations && 'animate-spin'
        )} />
        </div>
      }
    </div>);

};

/**
 * OptimizedAvatar - Specialized component for avatar images
 */
export const OptimizedAvatar = ({
  src,
  alt,
  size = 40,
  fallback,
  className,
  ...props
}) => {const { t } = useTranslation();
  const [imageError, setImageError] = useState(false);

  const handleError = () => {
    setImageError(true);
  };

  if (imageError || !src) {
    return (
      <div
        className={cn(
          'flex items-center justify-center bg-muted text-muted-foreground rounded-full',
          className
        )}
        style={{ width: size, height: size }}
        {...props}>

        {fallback || alt?.charAt(0)?.toUpperCase() || '?'}
      </div>);

  }

  return (
    <MobileImageOptimizer
      src={src}
      alt={alt}
      className={cn('rounded-full', className)}
      style={{ width: size, height: size }}
      aspectRatio="square"
      priority={size <= 60} // Prioritize small avatars
      quality={80}
      onError={handleError}
      {...props} />);


};

/**
 * ResponsiveImage - Simple responsive image wrapper
 */
export const ResponsiveImage = ({
  src,
  alt,
  className,
  containerClassName,
  ...props
}) => {const { t } = useTranslation();
  return (
    <div className={cn('relative', containerClassName)}>
      <MobileImageOptimizer
        src={src}
        alt={alt}
        className={cn('w-full h-auto', className)}
        {...props} />

    </div>);

};

/**
 * ImageGallery - Optimized image gallery with lazy loading
 */
export const ImageGallery = ({
  images,
  columns = { sm: 2, md: 3, lg: 4 },
  gap = 4,
  aspectRatio = 'square',
  onClick,
  className,
  ...props
}) => {const { t } = useTranslation();
  const { isMobile, isTablet } = useMobile();

  const getColumns = () => {
    if (isMobile) return columns.sm || 2;
    if (isTablet) return columns.md || 3;
    return columns.lg || 4;
  };

  return (
    <div
      className={cn(
        'grid gap-4',
        `grid-cols-${getColumns()}`,
        className
      )}
      style={{ gap: `${gap * 4}px` }}
      {...props}>

      {images.map((image, index) =>
      <div
        key={image.id || index}
        className="cursor-pointer hover:opacity-80 transition-opacity"
        onClick={() => onClick?.(image, index)}>

          <MobileImageOptimizer
          src={image.src}
          alt={image.alt || `Image ${index + 1}`}
          aspectRatio={aspectRatio}
          className="w-full rounded-lg"
          priority={index < getColumns() * 2} // Prioritize first two rows
          quality={70} />

        </div>
      )}
    </div>);

};

/**
 * useImagePreloader - Hook for preloading images
 */
export const useImagePreloader = () => {
  const [preloadedImages, setPreloadedImages] = useState(new Set());

  const preloadImage = useCallback((src) => {
    if (preloadedImages.has(src)) return Promise.resolve();

    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        setPreloadedImages((prev) => new Set([...prev, src]));
        resolve();
      };
      img.onerror = reject;
      img.src = src;
    });
  }, [preloadedImages]);

  const preloadImages = useCallback(async (srcs) => {
    try {
      await Promise.all(srcs.map(preloadImage));
    } catch (error) {
      console.warn('Some images failed to preload:', error);
    }
  }, [preloadImage]);

  return { preloadImage, preloadImages, preloadedImages };
};

export default MobileImageOptimizer;