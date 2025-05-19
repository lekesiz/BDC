import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { buttonHover } from '@/lib/animations';

export const AnimatedButton = ({ 
  children, 
  className, 
  onClick,
  disabled,
  ...props 
}) => {
  return (
    <motion.div
      whileHover={!disabled ? buttonHover.whileHover : undefined}
      whileTap={!disabled ? buttonHover.whileTap : undefined}
      transition={buttonHover.transition}
    >
      <Button 
        className={className} 
        onClick={onClick}
        disabled={disabled}
        {...props}
      >
        {children}
      </Button>
    </motion.div>
  );
};