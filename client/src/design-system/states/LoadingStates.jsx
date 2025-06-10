// Loading States Components
import React from 'react';
import { motion } from 'framer-motion';
import { animations } from '../animations/animations';
import './states.css';

// Spinner Loading
export const Spinner = ({ size = 'md', color = 'primary', ...props }) => {
  const sizes = {
    sm: 16,
    md: 24,
    lg: 32,
    xl: 48
  };

  return (
    <motion.div
      className={`ds-spinner ds-spinner--${size} ds-spinner--${color}`}
      style={{ width: sizes[size], height: sizes[size] }}
      animate={animations.loading.spinner.animate}
      aria-label="Loading"
      role="status"
      {...props}
    >
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className="ds-spinner__track"
        />
        <path
          d="M12 2a10 10 0 0 1 10 10"
          stroke="currentColor"
          strokeWidth="3"
          strokeLinecap="round"
          className="ds-spinner__path"
        />
      </svg>
    </motion.div>
  );
};

// Dots Loading
export const LoadingDots = ({ size = 'md', color = 'primary', ...props }) => {
  const dotSizes = {
    sm: 4,
    md: 6,
    lg: 8,
    xl: 10
  };

  return (
    <div
      className={`ds-loading-dots ds-loading-dots--${size} ds-loading-dots--${color}`}
      role="status"
      aria-label="Loading"
      {...props}
    >
      {[0, 1, 2].map((index) => (
        <motion.span
          key={index}
          className="ds-loading-dots__dot"
          style={{
            width: dotSizes[size],
            height: dotSizes[size],
            animationDelay: `${index * 0.15}s`
          }}
          animate={animations.loading.dots.animate}
          transition={{
            ...animations.loading.dots.animate.transition,
            delay: index * 0.15
          }}
        />
      ))}
    </div>
  );
};

// Progress Bar Loading
export const ProgressBar = ({ 
  value = 0, 
  max = 100, 
  size = 'md', 
  color = 'primary',
  showLabel = true,
  animated = true,
  ...props 
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div
      className={`ds-progress ds-progress--${size} ds-progress--${color}`}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
      {...props}
    >
      {showLabel && (
        <div className="ds-progress__label">
          <span className="ds-progress__text">Loading</span>
          <span className="ds-progress__value">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="ds-progress__track">
        <motion.div
          className="ds-progress__fill"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{
            duration: animated ? 0.3 : 0,
            ease: 'easeOut'
          }}
        />
      </div>
    </div>
  );
};

// Skeleton Loading
export const Skeleton = ({ 
  variant = 'text',
  width,
  height,
  rounded = false,
  animated = true,
  className = '',
  ...props 
}) => {
  const variants = {
    text: 'ds-skeleton--text',
    title: 'ds-skeleton--title',
    button: 'ds-skeleton--button',
    avatar: 'ds-skeleton--avatar',
    image: 'ds-skeleton--image',
    card: 'ds-skeleton--card'
  };

  const style = {
    ...(width && { width }),
    ...(height && { height })
  };

  return (
    <div
      className={`ds-skeleton ${variants[variant]} ${rounded ? 'ds-skeleton--rounded' : ''} ${animated ? 'ds-skeleton--animated' : ''} ${className}`}
      style={style}
      aria-hidden="true"
      {...props}
    />
  );
};

// Loading Overlay
export const LoadingOverlay = ({ 
  visible = true,
  message = 'Loading...',
  spinner = true,
  blur = true,
  ...props 
}) => {
  if (!visible) return null;

  return (
    <motion.div
      className={`ds-loading-overlay ${blur ? 'ds-loading-overlay--blur' : ''}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      {...props}
    >
      <div className="ds-loading-overlay__content">
        {spinner && <Spinner size="lg" />}
        {message && (
          <p className="ds-loading-overlay__message">{message}</p>
        )}
      </div>
    </motion.div>
  );
};

// Button Loading State
export const ButtonLoading = ({ 
  loading = false,
  children,
  loadingText = 'Loading...',
  ...props 
}) => {
  return (
    <button
      className="ds-button ds-button--loading"
      disabled={loading}
      aria-busy={loading}
      {...props}
    >
      {loading ? (
        <>
          <Spinner size="sm" />
          <span>{loadingText}</span>
        </>
      ) : (
        children
      )}
    </button>
  );
};

// Shimmer Effect
export const Shimmer = ({ width = '100%', height = '100%', ...props }) => {
  return (
    <div
      className="ds-shimmer"
      style={{ width, height }}
      aria-hidden="true"
      {...props}
    >
      <div className="ds-shimmer__gradient" />
    </div>
  );
};

// Pulse Loading
export const PulseLoader = ({ count = 3, size = 'md', color = 'primary', ...props }) => {
  const sizes = {
    sm: 40,
    md: 60,
    lg: 80,
    xl: 100
  };

  return (
    <div
      className={`ds-pulse-loader ds-pulse-loader--${size} ds-pulse-loader--${color}`}
      role="status"
      aria-label="Loading"
      {...props}
    >
      {Array.from({ length: count }).map((_, index) => (
        <motion.div
          key={index}
          className="ds-pulse-loader__ring"
          style={{
            width: sizes[size],
            height: sizes[size],
            animationDelay: `${index * 0.2}s`
          }}
          animate={{
            scale: [1, 1.5],
            opacity: [1, 0]
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: index * 0.2
          }}
        />
      ))}
    </div>
  );
};

// Circular Progress
export const CircularProgress = ({ 
  value = 0,
  max = 100,
  size = 'md',
  strokeWidth = 4,
  color = 'primary',
  showLabel = true,
  ...props 
}) => {
  const sizes = {
    sm: 32,
    md: 48,
    lg: 64,
    xl: 96
  };

  const radius = (sizes[size] - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div
      className={`ds-circular-progress ds-circular-progress--${size} ds-circular-progress--${color}`}
      role="progressbar"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={max}
      {...props}
    >
      <svg width={sizes[size]} height={sizes[size]}>
        <circle
          className="ds-circular-progress__track"
          cx={sizes[size] / 2}
          cy={sizes[size] / 2}
          r={radius}
          strokeWidth={strokeWidth}
        />
        <motion.circle
          className="ds-circular-progress__fill"
          cx={sizes[size] / 2}
          cy={sizes[size] / 2}
          r={radius}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </svg>
      {showLabel && (
        <div className="ds-circular-progress__label">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};

// Export all loading states
export const LoadingStates = {
  Spinner,
  LoadingDots,
  ProgressBar,
  Skeleton,
  LoadingOverlay,
  ButtonLoading,
  Shimmer,
  PulseLoader,
  CircularProgress
};