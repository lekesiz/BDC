import React from 'react';
import { cn } from '@/lib/utils';
/**
 * Avatar component for displaying user profile images
 * Falls back to initials when image fails to load
 * 
 * @param {object} props - Component props
 * @param {string} props.src - Image source URL
 * @param {string} props.alt - Alt text for the image
 * @param {string} props.initials - Initials to display as fallback
 * @param {string} props.size - Size variant: sm, md, lg, xl
 * @param {string} props.shape - Shape variant: circle, square
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Avatar content (used for custom fallback)
 * @returns {JSX.Element} Avatar component
 */
const Avatar = ({ 
  src, 
  alt = "", 
  initials, 
  size = "md", 
  shape = "circle", 
  className,
  ...props 
}) => {
  const [imageError, setImageError] = React.useState(false);
  const sizeClasses = {
    sm: "h-8 w-8 text-xs",
    md: "h-10 w-10 text-sm",
    lg: "h-12 w-12 text-base",
    xl: "h-16 w-16 text-lg"
  };
  const shapeClasses = {
    circle: "rounded-full",
    square: "rounded-md"
  };
  const handleError = () => {
    setImageError(true);
  };
  return (
    <div 
      className={cn(
        "relative inline-flex items-center justify-center overflow-hidden bg-muted",
        sizeClasses[size],
        shapeClasses[shape],
        className
      )}
      {...props}
    >
      {src && !imageError ? (
        <img
          src={src}
          alt={alt}
          className="h-full w-full object-cover"
          onError={handleError}
        />
      ) : (
        <span className="font-medium text-muted-foreground">
          {initials || alt.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)}
        </span>
      )}
    </div>
  );
};
/**
 * Avatar group component to display multiple avatars with overlap
 * 
 * @param {object} props - Component props
 * @param {number} props.max - Maximum number of avatars to display before showing a counter
 * @param {string} props.className - Additional CSS classes
 * @param {React.ReactNode} props.children - Avatar components
 * @returns {JSX.Element} AvatarGroup component
 */
const AvatarGroup = ({ 
  max = 3, 
  className, 
  children, 
  ...props 
}) => {
  const childrenArray = React.Children.toArray(children);
  const showCount = max > 0 && childrenArray.length > max;
  const visibleAvatars = showCount ? childrenArray.slice(0, max) : childrenArray;
  const remainingAvatars = showCount ? childrenArray.length - max : 0;
  return (
    <div 
      className={cn("flex -space-x-2", className)} 
      {...props}
    >
      {visibleAvatars.map((child, index) => (
        <div key={index} className="relative inline-block border-2 border-background">
          {child}
        </div>
      ))}
      {showCount && (
        <div 
          className={cn(
            "relative inline-flex h-10 w-10 items-center justify-center rounded-full bg-muted text-sm font-medium border-2 border-background",
          )}
        >
          +{remainingAvatars}
        </div>
      )}
    </div>
  );
};
export { Avatar, AvatarGroup };