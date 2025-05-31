// Mock of framer-motion for tests

// Create a simple mock component that just renders children
const createMockComponent = (name) => {
  const component = ({ children, ...props }) => {
    if (typeof children === 'function') {
      return children(props);
    }
    return children || null;
  };
  component.displayName = name;
  return component;
};

// Mock motion function
export const motion = new Proxy(
  {},
  {
    get: (_, prop) => {
      return createMockComponent(`motion.${String(prop)}`);
    }
  }
);

// Mock animation helpers
export const AnimatePresence = createMockComponent('AnimatePresence');
export const useAnimation = () => ({
  start: () => Promise.resolve(),
  stop: () => {},
  set: () => {}
});
export const useMotionValue = (initial) => ({
  get: () => initial,
  set: () => {},
  onChange: () => () => {}
});
export const useTransform = () => ({
  get: () => 0,
  set: () => {}
});
export const useCycle = (...args) => {
  const [first] = args;
  return [first, () => {}];
};

// Mock variants
export const fadeInUp = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 }
};

// Default export for when the whole package is imported
export default {
  motion,
  AnimatePresence,
  useAnimation,
  useMotionValue,
  useTransform,
  useCycle,
  fadeInUp
};