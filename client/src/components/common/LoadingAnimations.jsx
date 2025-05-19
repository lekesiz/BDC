import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';

/**
 * Animated loading components using framer-motion
 */

// Pulsing dots loader
export const PulsingDots = ({ size = "md", color = "primary" }) => {
  const sizes = {
    sm: "h-2 w-2",
    md: "h-3 w-3",
    lg: "h-4 w-4"
  };
  
  const colors = {
    primary: "bg-primary",
    secondary: "bg-secondary",
    gray: "bg-gray-400"
  };
  
  const dotVariants = {
    initial: { scale: 0.8, opacity: 0.5 },
    animate: { scale: 1, opacity: 1 }
  };
  
  return (
    <div className="flex items-center space-x-2">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className={`${sizes[size]} ${colors[color]} rounded-full`}
          variants={dotVariants}
          initial="initial"
          animate="animate"
          transition={{
            duration: 0.6,
            repeat: Infinity,
            repeatType: "reverse",
            delay: index * 0.2
          }}
        />
      ))}
    </div>
  );
};

// Spinning circle loader
export const SpinningCircle = ({ size = "md", className = "" }) => {
  const sizes = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
    xl: "h-16 w-16"
  };
  
  return (
    <motion.div
      className={`${sizes[size]} border-2 border-gray-200 border-t-primary rounded-full ${className}`}
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }}
    />
  );
};

// Progress bar loader
export const ProgressBar = ({ progress = 0, className = "" }) => {
  return (
    <div className={`w-full bg-gray-200 rounded-full h-2 overflow-hidden ${className}`}>
      <motion.div
        className="h-full bg-primary"
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      />
    </div>
  );
};

// Skeleton pulse animation
export const SkeletonPulse = ({ className = "" }) => {
  return (
    <motion.div
      className={`bg-gray-200 rounded ${className}`}
      animate={{
        opacity: [1, 0.5, 1]
      }}
      transition={{
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    />
  );
};

// Content loading placeholder
export const ContentLoader = ({ lines = 3, className = "" }) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <SkeletonPulse
          key={index}
          className={`h-4 ${index === lines - 1 ? 'w-3/4' : 'w-full'}`}
        />
      ))}
    </div>
  );
};

// Card skeleton loader
export const CardSkeleton = ({ showAvatar = true, lines = 3 }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      {showAvatar && (
        <div className="flex items-center mb-4">
          <SkeletonPulse className="h-12 w-12 rounded-full mr-4" />
          <div className="flex-1">
            <SkeletonPulse className="h-4 w-32 mb-2" />
            <SkeletonPulse className="h-3 w-24" />
          </div>
        </div>
      )}
      <ContentLoader lines={lines} />
    </div>
  );
};

// Table skeleton loader
export const TableSkeleton = ({ rows = 5, columns = 4 }) => {
  return (
    <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
      <table className="min-w-full divide-y divide-gray-300">
        <thead className="bg-gray-50">
          <tr>
            {Array.from({ length: columns }).map((_, i) => (
              <th key={i} className="px-6 py-3">
                <SkeletonPulse className="h-4 w-full" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex} className="px-6 py-4">
                  <SkeletonPulse className="h-4 w-full" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Form skeleton loader
export const FormSkeleton = ({ fields = 4 }) => {
  return (
    <div className="space-y-6">
      {Array.from({ length: fields }).map((_, i) => (
        <div key={i}>
          <SkeletonPulse className="h-4 w-1/4 mb-2" />
          <SkeletonPulse className="h-10 w-full" />
        </div>
      ))}
      <div className="flex gap-4">
        <SkeletonPulse className="h-10 w-24" />
        <SkeletonPulse className="h-10 w-24" />
      </div>
    </div>
  );
};

// Page loading overlay
export const LoadingOverlay = ({ 
  visible = true, 
  message = "Loading...",
  fullScreen = false 
}) => {
  if (!visible) return null;
  
  const containerClass = fullScreen 
    ? "fixed inset-0 z-50" 
    : "absolute inset-0";
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`${containerClass} bg-white bg-opacity-75 flex items-center justify-center`}
    >
      <div className="text-center">
        <SpinningCircle size="lg" className="mx-auto mb-4" />
        <p className="text-gray-600">{message}</p>
      </div>
    </motion.div>
  );
};

// Button loading state
export const ButtonLoading = ({ 
  loading = false, 
  children, 
  loadingText = "Loading...",
  className = "",
  ...props 
}) => {
  return (
    <button
      disabled={loading}
      className={`relative ${loading ? 'cursor-not-allowed opacity-75' : ''} ${className}`}
      {...props}
    >
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 flex items-center justify-center bg-inherit"
        >
          <Loader2 className="h-4 w-4 animate-spin mr-2" />
          {loadingText}
        </motion.div>
      )}
      <span className={loading ? 'invisible' : ''}>{children}</span>
    </button>
  );
};

// Stagger children animation for lists
export const StaggerChildren = ({ children, className = "" }) => {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };
  
  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };
  
  return (
    <motion.div
      className={className}
      variants={container}
      initial="hidden"
      animate="show"
    >
      {React.Children.map(children, (child, index) => (
        <motion.div key={index} variants={item}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
};