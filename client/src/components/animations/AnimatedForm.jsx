import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';

export const AnimatedForm = ({ children, className, onSubmit, ...props }) => {
  return (
    <motion.form
      variants={fadeInUp}
      initial="initial"
      animate="animate"
      exit="exit"
      className={className}
      onSubmit={onSubmit}
      {...props}
    >
      {children}
    </motion.form>
  );
};

export const AnimatedFormField = ({ children, className, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const AnimatedFormError = ({ children, className, ...props }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className={`text-red-500 text-sm ${className || ''}`}
      {...props}
    >
      {children}
    </motion.div>
  );
};