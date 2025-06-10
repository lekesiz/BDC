// TODO: i18n - processed
// Animation Hook
import { useEffect, useState } from 'react';
import { useDesignSystem } from '../DesignSystemProvider';
import { animations } from '../animations/animations';
import { microInteractions } from '../animations/microInteractions';import { useTranslation } from "react-i18next";

export const useAnimation = (animationName, options = {}) => {
  const { config } = useDesignSystem();
  const [animationConfig, setAnimationConfig] = useState({});

  useEffect(() => {
    if (config.reducedMotion) {
      // Return minimal or no animation for reduced motion
      setAnimationConfig({
        initial: false,
        animate: false,
        exit: false,
        transition: { duration: 0 }
      });
    } else {
      // Get animation from library
      const animationPath = animationName.split('.');
      let animation = animations;

      for (const path of animationPath) {
        animation = animation[path];
        if (!animation) break;
      }

      if (!animation) {
        // Try micro interactions
        animation = microInteractions[animationName];
      }

      if (animation) {
        setAnimationConfig({
          ...animation,
          ...options
        });
      }
    }
  }, [animationName, config.reducedMotion, options]);

  return animationConfig;
};

// Gesture hook
export const useGesture = (gestureName, handlers = {}) => {
  const { config } = useDesignSystem();

  if (config.reducedMotion) {
    return {}; // No gestures in reduced motion
  }

  const gestureHandlers = {
    swipe: {
      onPan: handlers.onSwipe,
      onPanEnd: handlers.onSwipeEnd
    },
    drag: {
      drag: true,
      onDrag: handlers.onDrag,
      onDragEnd: handlers.onDragEnd,
      dragElastic: 0.2,
      dragConstraints: handlers.constraints
    },
    hover: {
      onHoverStart: handlers.onHoverStart,
      onHoverEnd: handlers.onHoverEnd
    },
    tap: {
      onTap: handlers.onTap,
      onTapStart: handlers.onTapStart,
      onTapCancel: handlers.onTapCancel
    }
  };

  return gestureHandlers[gestureName] || {};
};