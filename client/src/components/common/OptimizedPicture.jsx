import React from 'react';
import LazyImage from './LazyImage';
const OptimizedPicture = ({
  src,
  alt,
  className = '',
  sizes = '100vw',
  formats = ['webp', 'avif'],
  widths = [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
  quality = 85,
  loading = 'lazy',
  priority = false,
  placeholder,
  onLoad,
  onError,
  ...props
}) => {
  // If priority is true, use native loading instead of LazyImage
  if (priority) {
    return (
      <picture>
        {formats.map(format => (
          <source
            key={format}
            type={`image/${format}`}
            srcSet={widths.map(w => 
              `${src}?w=${w}&fm=${format}&q=${quality} ${w}w`
            ).join(', ')}
            sizes={sizes}
          />
        ))}
        <img
          src={`${src}?w=${widths[widths.length - 1]}&q=${quality}`}
          alt={alt}
          className={className}
          loading="eager"
          decoding="async"
          onLoad={onLoad}
          onError={onError}
          {...props}
        />
      </picture>
    );
  }
  // For non-priority images, use LazyImage
  return (
    <picture>
      {formats.map(format => (
        <source
          key={format}
          type={`image/${format}`}
          srcSet={widths.map(w => 
            `${src}?w=${w}&fm=${format}&q=${quality} ${w}w`
          ).join(', ')}
          sizes={sizes}
        />
      ))}
      <LazyImage
        src={`${src}?w=${widths[widths.length - 1]}&q=${quality}`}
        alt={alt}
        className={className}
        placeholder={placeholder}
        onLoad={onLoad}
        onError={onError}
        {...props}
      />
    </picture>
  );
};
export default React.memo(OptimizedPicture);