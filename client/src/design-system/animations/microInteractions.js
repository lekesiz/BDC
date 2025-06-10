// TODO: i18n - processed
import { useTranslation } from "react-i18next"; // Micro-interactions for enhanced user experience
export const microInteractions = {
  // Button interactions
  button: {
    tap: {
      scale: 0.95,
      transition: { duration: 0.1 }
    },
    hover: {
      scale: 1.02,
      transition: { duration: 0.2 }
    },
    success: {
      animate: {
        scale: [1, 0.9, 1.1, 1],
        rotate: [0, 0, 360, 360],
        transition: { duration: 0.5 }
      }
    }
  },

  // Form interactions
  form: {
    fieldFocus: {
      scale: 1.02,
      borderColor: 'var(--color-interactive-focus)',
      transition: { duration: 0.2 }
    },
    fieldError: {
      x: [-5, 5, -5, 5, 0],
      borderColor: 'var(--color-semantic-error)',
      transition: { duration: 0.4 }
    },
    fieldSuccess: {
      borderColor: 'var(--color-semantic-success)',
      transition: { duration: 0.3 }
    }
  },

  // Toggle/Switch interactions
  toggle: {
    on: {
      x: 20,
      backgroundColor: 'var(--color-semantic-success)',
      transition: { duration: 0.2 }
    },
    off: {
      x: 0,
      backgroundColor: 'var(--color-neutral-400)',
      transition: { duration: 0.2 }
    }
  },

  // Card interactions
  card: {
    hover: {
      y: -2,
      boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
      transition: { duration: 0.3 }
    },
    tap: {
      scale: 0.98,
      transition: { duration: 0.1 }
    }
  },

  // Icon interactions
  icon: {
    rotate: {
      rotate: 360,
      transition: { duration: 0.4 }
    },
    bounce: {
      y: [-2, 2, -2, 0],
      transition: { duration: 0.3 }
    },
    pulse: {
      scale: [1, 1.2, 1],
      transition: { duration: 0.3 }
    }
  },

  // Notification interactions
  notification: {
    enter: {
      x: [100, 0],
      opacity: [0, 1],
      transition: { duration: 0.3, ease: 'easeOut' }
    },
    exit: {
      x: [0, 100],
      opacity: [1, 0],
      transition: { duration: 0.2, ease: 'easeIn' }
    },
    attention: {
      scale: [1, 1.05, 1],
      transition: { duration: 0.2, repeat: 2 }
    }
  },

  // Loading states
  loading: {
    skeleton: {
      backgroundColor: ['#f0f0f0', '#e0e0e0', '#f0f0f0'],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: 'linear'
      }
    },
    spinner: {
      rotate: [0, 360],
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: 'linear'
      }
    },
    dots: {
      scale: [0.8, 1, 0.8],
      opacity: [0.5, 1, 0.5],
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: 'easeInOut',
        times: [0, 0.5, 1],
        delay: 0.2
      }
    }
  },

  // Tooltip interactions
  tooltip: {
    show: {
      opacity: [0, 1],
      y: [-5, 0],
      transition: { duration: 0.2 }
    },
    hide: {
      opacity: [1, 0],
      y: [0, -5],
      transition: { duration: 0.15 }
    }
  },

  // Dropdown interactions
  dropdown: {
    open: {
      opacity: [0, 1],
      y: [-10, 0],
      transition: { duration: 0.2 }
    },
    close: {
      opacity: [1, 0],
      y: [0, -10],
      transition: { duration: 0.15 }
    }
  },

  // Tab interactions
  tab: {
    active: {
      borderBottom: '2px solid var(--color-brand-primary)',
      color: 'var(--color-brand-primary)',
      transition: { duration: 0.2 }
    },
    inactive: {
      borderBottom: '2px solid transparent',
      color: 'var(--color-text-secondary)',
      transition: { duration: 0.2 }
    }
  },

  // Progress interactions
  progress: {
    fill: {
      scaleX: [0, 1],
      transformOrigin: 'left',
      transition: { duration: 0.5, ease: 'easeOut' }
    },
    pulse: {
      opacity: [0.6, 1, 0.6],
      transition: {
        duration: 1,
        repeat: Infinity,
        ease: 'easeInOut'
      }
    }
  },

  // Feedback interactions
  feedback: {
    success: {
      scale: [0, 1.2, 1],
      opacity: [0, 1],
      transition: { duration: 0.4 }
    },
    error: {
      scale: [0, 1.1, 1],
      rotate: [0, -10, 10, -10, 0],
      opacity: [0, 1],
      transition: { duration: 0.5 }
    },
    warning: {
      scale: [0, 1.1, 1],
      opacity: [0, 1],
      transition: { duration: 0.4 }
    }
  }
};

// Gesture configurations
export const gestures = {
  drag: {
    dragElastic: 0.2,
    dragConstraints: { left: 0, right: 0, top: 0, bottom: 0 },
    dragTransition: { bounceStiffness: 600, bounceDamping: 20 }
  },

  swipe: {
    swipePower: (offset, velocity) => {
      return Math.abs(offset) * velocity;
    },
    swipeConfidenceThreshold: 10000,
    swipeVelocityThreshold: 500
  },

  pinch: {
    scale: { min: 0.5, max: 2 },
    transition: { type: 'spring', stiffness: 300 }
  }
};