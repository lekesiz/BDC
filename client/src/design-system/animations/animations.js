// TODO: i18n - processed
// Core Animation Library
import { transitions } from '../tokens/transitions';import { useTranslation } from "react-i18next";

export const animations = {
  // Entrance animations
  entrance: {
    fadeIn: {
      initial: { opacity: 0 },
      animate: { opacity: 1 },
      exit: { opacity: 0 },
      transition: { duration: 0.3, ease: transitions.easing.easeOut }
    },
    slideInUp: {
      initial: { opacity: 0, y: 20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: 20 },
      transition: { duration: 0.3, ease: transitions.easing.easeOutCubic }
    },
    slideInDown: {
      initial: { opacity: 0, y: -20 },
      animate: { opacity: 1, y: 0 },
      exit: { opacity: 0, y: -20 },
      transition: { duration: 0.3, ease: transitions.easing.easeOutCubic }
    },
    slideInLeft: {
      initial: { opacity: 0, x: -20 },
      animate: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: -20 },
      transition: { duration: 0.3, ease: transitions.easing.easeOutCubic }
    },
    slideInRight: {
      initial: { opacity: 0, x: 20 },
      animate: { opacity: 1, x: 0 },
      exit: { opacity: 0, x: 20 },
      transition: { duration: 0.3, ease: transitions.easing.easeOutCubic }
    },
    scaleIn: {
      initial: { opacity: 0, scale: 0.9 },
      animate: { opacity: 1, scale: 1 },
      exit: { opacity: 0, scale: 0.9 },
      transition: { duration: 0.3, ease: transitions.easing.easeOutCubic }
    },
    rotateIn: {
      initial: { opacity: 0, rotate: -10 },
      animate: { opacity: 1, rotate: 0 },
      exit: { opacity: 0, rotate: 10 },
      transition: { duration: 0.4, ease: transitions.easing.spring }
    }
  },

  // Attention seekers
  attention: {
    pulse: {
      animate: {
        scale: [1, 1.05, 1],
        transition: {
          duration: 1,
          repeat: Infinity,
          ease: transitions.easing.easeInOut
        }
      }
    },
    shake: {
      animate: {
        x: [-10, 10, -10, 10, 0],
        transition: {
          duration: 0.5,
          ease: transitions.easing.linear
        }
      }
    },
    bounce: {
      animate: {
        y: [0, -20, 0],
        transition: {
          duration: 0.6,
          repeat: Infinity,
          ease: transitions.easing.easeInOut
        }
      }
    },
    wiggle: {
      animate: {
        rotate: [-3, 3, -3, 3, 0],
        transition: {
          duration: 0.4,
          ease: transitions.easing.easeInOut
        }
      }
    },
    rubberBand: {
      animate: {
        scaleX: [1, 1.25, 0.75, 1.15, 0.95, 1],
        scaleY: [1, 0.75, 1.25, 0.85, 1.05, 1],
        transition: {
          duration: 1,
          ease: transitions.easing.easeInOut
        }
      }
    }
  },

  // Loading animations
  loading: {
    spinner: {
      animate: {
        rotate: 360,
        transition: {
          duration: 1,
          repeat: Infinity,
          ease: transitions.easing.linear
        }
      }
    },
    dots: {
      animate: {
        opacity: [0.3, 1, 0.3],
        transition: {
          duration: 1.5,
          repeat: Infinity,
          ease: transitions.easing.easeInOut
        }
      }
    },
    bars: {
      animate: {
        scaleY: [0.5, 1, 0.5],
        transition: {
          duration: 1.2,
          repeat: Infinity,
          ease: transitions.easing.easeInOut
        }
      }
    },
    ripple: {
      animate: {
        scale: [0, 1],
        opacity: [1, 0],
        transition: {
          duration: 1,
          repeat: Infinity,
          ease: transitions.easing.easeOut
        }
      }
    }
  },

  // Hover effects
  hover: {
    lift: {
      whileHover: {
        y: -4,
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.15)',
        transition: { duration: 0.2 }
      }
    },
    grow: {
      whileHover: {
        scale: 1.05,
        transition: { duration: 0.2 }
      }
    },
    shrink: {
      whileHover: {
        scale: 0.95,
        transition: { duration: 0.2 }
      }
    },
    glow: {
      whileHover: {
        boxShadow: '0 0 20px rgba(24, 144, 255, 0.5)',
        transition: { duration: 0.2 }
      }
    },
    rotate: {
      whileHover: {
        rotate: 5,
        transition: { duration: 0.2 }
      }
    }
  },

  // Tap/Click effects
  tap: {
    scale: {
      whileTap: {
        scale: 0.95,
        transition: { duration: 0.1 }
      }
    },
    press: {
      whileTap: {
        scale: 0.98,
        y: 1,
        transition: { duration: 0.1 }
      }
    }
  },

  // Complex animations
  complex: {
    morphing: {
      initial: { borderRadius: '4px' },
      animate: { borderRadius: '50%' },
      transition: { duration: 0.5, ease: transitions.easing.easeInOut }
    },
    staggerChildren: {
      animate: {
        transition: {
          staggerChildren: 0.1,
          delayChildren: 0.3
        }
      }
    },
    parallax: {
      animate: (scrollY) => ({
        y: scrollY * 0.5,
        transition: { type: 'spring', stiffness: 100 }
      })
    }
  },

  // Skeleton loading
  skeleton: {
    shimmer: {
      animate: {
        backgroundPosition: ['200% 0', '-200% 0'],
        transition: {
          duration: 1.5,
          repeat: Infinity,
          ease: transitions.easing.linear
        }
      }
    }
  }
};

// Animation variants for common use cases
export const animationVariants = {
  // Container variants for stagger effects
  container: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.3,
        staggerChildren: 0.1
      }
    }
  },

  // Item variants for stagger effects
  item: {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.3,
        ease: transitions.easing.easeOut
      }
    }
  },

  // Page transition variants
  page: {
    initial: { opacity: 0, x: -20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 20 },
    transition: { duration: 0.3 }
  }
};