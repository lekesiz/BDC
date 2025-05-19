import { motion } from 'framer-motion';
import { Checkbox } from '@/components/ui/checkbox';

export const AnimatedCheckbox = ({ 
  checked,
  onChange,
  label,
  className,
  ...props 
}) => {
  return (
    <motion.label 
      className={`flex items-center cursor-pointer ${className || ''}`}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      <motion.div
        animate={{
          scale: checked ? [1, 1.2, 1] : 1,
        }}
        transition={{ duration: 0.2 }}
      >
        <Checkbox
          checked={checked}
          onChange={onChange}
          {...props}
        />
      </motion.div>
      
      {label && (
        <motion.span 
          className="ml-2 select-none"
          animate={{
            color: checked ? '#3b82f6' : '#374151',
          }}
        >
          {label}
        </motion.span>
      )}
    </motion.label>
  );
};