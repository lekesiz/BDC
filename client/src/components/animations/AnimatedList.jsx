import { motion } from 'framer-motion';
import { listContainer, listItem } from '@/lib/animations';

export const AnimatedList = ({ children, className, ...props }) => {
  return (
    <motion.ul
      variants={listContainer}
      initial="hidden"
      animate="visible"
      className={className}
      {...props}
    >
      {children}
    </motion.ul>
  );
};

export const AnimatedListItem = ({ children, className, ...props }) => {
  return (
    <motion.li
      variants={listItem}
      className={className}
      {...props}
    >
      {children}
    </motion.li>
  );
};