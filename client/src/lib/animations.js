/**
 * Centralized animation configurations for consistent animations throughout the app
 */
// Framer Motion animation variants with GPU acceleration
export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: 0.3 }
};
export const fadeInUp = {
  initial: { opacity: 0, y: 20, transform: 'translateZ(0)' },
  animate: { opacity: 1, y: 0, transform: 'translateZ(0)' },
  exit: { opacity: 0, y: 20 },
  transition: { duration: 0.3, ease: 'easeOut' }
};
export const fadeInDown = {
  initial: { opacity: 0, y: -20, transform: 'translateZ(0)' },
  animate: { opacity: 1, y: 0, transform: 'translateZ(0)' },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3, ease: 'easeOut' }
};
export const fadeInLeft = {
  initial: { opacity: 0, x: -20, transform: 'translateZ(0)' },
  animate: { opacity: 1, x: 0, transform: 'translateZ(0)' },
  exit: { opacity: 0, x: -20 },
  transition: { duration: 0.3, ease: 'easeOut' }
};
export const fadeInRight = {
  initial: { opacity: 0, x: 20, transform: 'translateZ(0)' },
  animate: { opacity: 1, x: 0, transform: 'translateZ(0)' },
  exit: { opacity: 0, x: 20 },
  transition: { duration: 0.3, ease: 'easeOut' }
};
export const scaleIn = {
  initial: { opacity: 0, scale: 0.9, transform: 'translateZ(0)' },
  animate: { opacity: 1, scale: 1, transform: 'translateZ(0)' },
  exit: { opacity: 0, scale: 0.9 },
  transition: { duration: 0.3, ease: 'easeOut' }
};
export const slideLeft = {
  initial: { x: '100%' },
  animate: { x: 0 },
  exit: { x: '100%' }
};
export const slideRight = {
  initial: { x: '-100%' },
  animate: { x: 0 },
  exit: { x: '-100%' }
};
export const slideUp = {
  initial: { y: '100%' },
  animate: { y: 0 },
  exit: { y: '100%' }
};
export const slideDown = {
  initial: { y: '-100%' },
  animate: { y: 0 },
  exit: { y: '-100%' }
};
// Stagger children animations
export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
};
export const staggerItem = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 }
};
// Page transition variants
export const pageTransition = {
  initial: { opacity: 0, y: 20 },
  animate: { 
    opacity: 1, 
    y: 0,
    transition: {
      duration: 0.3,
      ease: 'easeOut'
    }
  },
  exit: { 
    opacity: 0, 
    y: -20,
    transition: {
      duration: 0.2,
      ease: 'easeIn'
    }
  }
};
// Modal animations
export const modalOverlay = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 }
};
export const modalContent = {
  initial: { opacity: 0, scale: 0.95, y: 20 },
  animate: { 
    opacity: 1, 
    scale: 1, 
    y: 0,
    transition: {
      type: 'spring',
      damping: 25,
      stiffness: 300
    }
  },
  exit: { 
    opacity: 0, 
    scale: 0.95, 
    y: 20,
    transition: {
      duration: 0.2
    }
  }
};
// List animations
export const listContainer = {
  hidden: { opacity: 1 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.1,
      staggerChildren: 0.05
    }
  }
};
export const listItem = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      damping: 25,
      stiffness: 300
    }
  }
};
// Skeleton loading animation
export const shimmer = {
  initial: { x: '-100%' },
  animate: {
    x: '100%',
    transition: {
      repeat: Infinity,
      duration: 1.5,
      ease: 'linear'
    }
  }
};
// Button hover animations
export const buttonHover = {
  whileHover: { scale: 1.02 },
  whileTap: { scale: 0.98 },
  transition: {
    type: 'spring',
    stiffness: 400,
    damping: 17
  }
};
// Card hover animations
export const cardHover = {
  whileHover: { 
    y: -4,
    boxShadow: '0 10px 20px rgba(0, 0, 0, 0.1)'
  },
  transition: {
    type: 'spring',
    stiffness: 400,
    damping: 25
  }
};
// Navigation menu animations
export const menuItemVariants = {
  initial: { opacity: 0, x: -20 },
  animate: (i) => ({
    opacity: 1,
    x: 0,
    transition: {
      delay: i * 0.05,
      type: 'spring',
      stiffness: 300,
      damping: 24
    }
  })
};
// Toast notification animations
export const toastAnimation = {
  initial: { opacity: 0, y: 50, scale: 0.9 },
  animate: { 
    opacity: 1, 
    y: 0, 
    scale: 1,
    transition: {
      type: 'spring',
      damping: 20,
      stiffness: 300
    }
  },
  exit: { 
    opacity: 0, 
    y: 20, 
    scale: 0.9,
    transition: {
      duration: 0.2
    }
  }
};
// Floating action animations
export const floatingAnimation = {
  animate: {
    y: [0, -10, 0],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
};
// Pulse animation for notifications
export const pulseAnimation = {
  animate: {
    scale: [1, 1.1, 1],
    opacity: [1, 0.8, 1],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
};
// Rotation animation
export const rotateAnimation = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear'
    }
  }
};
// Custom easing functions
export const easings = {
  easeInQuad: [0.55, 0.085, 0.68, 0.53],
  easeOutQuad: [0.25, 0.46, 0.45, 0.94],
  easeInOutQuad: [0.455, 0.03, 0.515, 0.955],
  easeInCubic: [0.55, 0.055, 0.675, 0.19],
  easeOutCubic: [0.215, 0.61, 0.355, 1],
  easeInOutCubic: [0.645, 0.045, 0.355, 1],
  easeInQuart: [0.895, 0.03, 0.685, 0.22],
  easeOutQuart: [0.165, 0.84, 0.44, 1],
  easeInOutQuart: [0.77, 0, 0.175, 1],
  easeInQuint: [0.755, 0.05, 0.855, 0.06],
  easeOutQuint: [0.23, 1, 0.32, 1],
  easeInOutQuint: [0.86, 0, 0.07, 1],
  easeInExpo: [0.95, 0.05, 0.795, 0.035],
  easeOutExpo: [0.19, 1, 0.22, 1],
  easeInOutExpo: [1, 0, 0, 1],
  easeInCirc: [0.6, 0.04, 0.98, 0.335],
  easeOutCirc: [0.075, 0.82, 0.165, 1],
  easeInOutCirc: [0.785, 0.135, 0.15, 0.86]
};
// CSS transition classes for non-Framer Motion components
export const transitionClasses = {
  ease: 'transition-all duration-300 ease-in-out',
  easeIn: 'transition-all duration-300 ease-in',
  easeOut: 'transition-all duration-300 ease-out',
  fast: 'transition-all duration-150',
  slow: 'transition-all duration-500',
  bounce: 'transition-all duration-300 ease-bounce',
  colors: 'transition-colors duration-200',
  transform: 'transition-transform duration-300',
  opacity: 'transition-opacity duration-300'
};
export default {
  fadeIn,
  fadeInUp,
  fadeInDown,
  fadeInLeft,
  fadeInRight,
  scaleIn,
  slideLeft,
  slideRight,
  slideUp,
  slideDown,
  staggerContainer,
  staggerItem,
  pageTransition,
  modalOverlay,
  modalContent,
  listContainer,
  listItem,
  shimmer,
  buttonHover,
  cardHover,
  menuItemVariants,
  toastAnimation,
  floatingAnimation,
  pulseAnimation,
  rotateAnimation,
  easings,
  transitionClasses
};