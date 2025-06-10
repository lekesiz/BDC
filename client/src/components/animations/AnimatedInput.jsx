// TODO: i18n - processed
import { motion, AnimatePresence } from 'framer-motion';
import { Input } from '@/components/ui/input';
import { useState } from 'react';import { useTranslation } from "react-i18next";
export const AnimatedInput = ({
  error,
  className,
  onFocus,
  onBlur,
  ...props
}) => {const { t } = useTranslation();
  const [isFocused, setIsFocused] = useState(false);
  const handleFocus = (e) => {
    setIsFocused(true);
    onFocus?.(e);
  };
  const handleBlur = (e) => {
    setIsFocused(false);
    onBlur?.(e);
  };
  return (
    <div className="relative">
      <motion.div
        animate={{
          scale: isFocused ? 1.01 : 1
        }}
        transition={{ duration: 0.2 }}>

        <Input
          className={`${error ? 'border-red-500' : ''} ${className || ''}`}
          onFocus={handleFocus}
          onBlur={handleBlur}
          {...props} />

      </motion.div>
      <AnimatePresence>
        {error &&
        <motion.div
          initial={{ opacity: 0, y: -5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          transition={{ duration: 0.15 }}
          className="absolute text-red-500 text-xs mt-1">

            {error}
          </motion.div>
        }
      </AnimatePresence>
    </div>);

};