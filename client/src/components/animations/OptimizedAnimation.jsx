import { motion, useMotionValue, useTransform } from 'framer-motion';
import { useInView } from 'react-intersection-observer';
import { useMemo } from 'react';
/**
 * Performance-optimized animation wrapper that only animates when in viewport
 * and uses GPU-accelerated transforms
 */
export const OptimizedAnimation = ({ 
  children, 
  variants, 
  threshold = 0.1,
  once = true,
  className,
  delay = 0,
  duration = 0.5,
  ...props 
}) => {
  const { ref, inView } = useInView({
    threshold,
    triggerOnce: once,
  });
  // Memoize animation variants for performance
  const animationVariants = useMemo(() => ({
    hidden: { 
      opacity: 0, 
      y: 20,
      transition: { duration: 0 }
    },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { 
        duration,
        delay,
        ease: 'easeOut'
      }
    }
  }), [delay, duration]);
  return (
    <motion.div
      ref={ref}
      initial="hidden"
      animate={inView ? "visible" : "hidden"}
      variants={variants || animationVariants}
      className={className}
      style={{ transform: 'translateZ(0)' }} // Force GPU acceleration
      {...props}
    >
      {children}
    </motion.div>
  );
};
/**
 * Optimized scroll-triggered animation
 */
export const ScrollAnimation = ({ children, className, offset = 100 }) => {
  const y = useMotionValue(0);
  const opacity = useTransform(y, [-offset, 0, offset], [0, 1, 0]);
  return (
    <motion.div
      className={className}
      style={{ opacity, y }}
    >
      {children}
    </motion.div>
  );
};
/**
 * Batch animation for multiple elements to reduce re-renders
 */
export const BatchAnimation = ({ children, staggerDelay = 0.1 }) => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: staggerDelay,
          },
        },
      }}
    >
      {children}
    </motion.div>
  );
};