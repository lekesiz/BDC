import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { motion } from 'framer-motion';
const ThemeToggle = ({ className }) => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
  return (
    <motion.button
      onClick={toggleTheme}
      className={`relative p-2 rounded-lg transition-colors ${
        isDark 
          ? 'bg-gray-800 hover:bg-gray-700 text-yellow-400' 
          : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
      } ${className || ''}`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      title={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <motion.div
        initial={false}
        animate={{
          rotate: isDark ? 180 : 0,
        }}
        transition={{ duration: 0.3 }}
      >
        {isDark ? (
          <Moon className="w-5 h-5" />
        ) : (
          <Sun className="w-5 h-5" />
        )}
      </motion.div>
    </motion.button>
  );
};
export default ThemeToggle;