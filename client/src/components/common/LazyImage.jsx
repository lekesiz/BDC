import React, { useState, useEffect, useRef } from 'react';
import { useInView } from 'react-intersection-observer';
const LazyImage = ({ 
  src, 
  alt, 
  className = '', 
  placeholder = '/api/placeholder/400/300',
  threshold = 0.1,
  rootMargin = '50px',
  onLoad,
  onError,
  ...props 
}) => {
  const [imageSrc, setImageSrc] = useState(placeholder);
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);
  const { ref, inView } = useInView({
    threshold,
    rootMargin,
    triggerOnce: true
  });
  useEffect(() => {
    if (inView && src) {
      const img = new Image();
      img.src = src;
      img.onload = () => {
        setImageSrc(src);
        setImageLoading(false);
        onLoad?.();
      };
      img.onerror = () => {
        setImageError(true);
        setImageLoading(false);
        onError?.();
      };
    }
  }, [inView, src, onLoad, onError]);
  return (
    <div ref={ref} className={`relative ${className}`}>
      {imageLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded" />
      )}
      {imageError ? (
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center rounded">
          <span className="text-gray-400">Failed to load image</span>
        </div>
      ) : (
        <img
          src={imageSrc}
          alt={alt}
          className={`${className} ${imageLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
          {...props}
        />
      )}
    </div>
  );
};
export default React.memo(LazyImage);