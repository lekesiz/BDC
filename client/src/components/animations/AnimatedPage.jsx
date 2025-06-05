import { motion } from 'framer-motion';
import { pageTransition } from '@/lib/animations';
export const AnimatedPage = ({ children, className, ...props }) => {
  return (
    <motion.div
      variants={pageTransition}
      initial="initial"
      animate="animate"
      exit="exit"
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
};