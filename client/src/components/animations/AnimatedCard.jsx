import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { cardHover, fadeInUp } from '@/lib/animations';
import { useTheme } from '@/contexts/ThemeContext';
export const AnimatedCard = ({ 
  children, 
  className, 
  variants = fadeInUp,
  hoverEffect = true,
  ...props 
}) => {
  const { isDark } = useTheme();
  const combinedVariants = hoverEffect 
    ? { ...variants, ...cardHover }
    : variants;
  // Dark mode hover effects
  const darkHoverVariants = {
    ...combinedVariants,
    whileHover: hoverEffect ? {
      ...combinedVariants.whileHover,
      boxShadow: isDark ? '0 10px 20px rgba(255, 255, 255, 0.05)' : '0 10px 20px rgba(0, 0, 0, 0.1)'
    } : undefined
  };
  return (
    <motion.div
      variants={darkHoverVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      whileHover={hoverEffect ? darkHoverVariants.whileHover : undefined}
      transition={combinedVariants.transition}
    >
      <Card className={`${isDark ? 'dark:bg-gray-800 dark:border-gray-700' : ''} ${className || ''}`} {...props}>
        {children}
      </Card>
    </motion.div>
  );
};