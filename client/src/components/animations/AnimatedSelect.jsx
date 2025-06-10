// TODO: i18n - processed
import { motion } from 'framer-motion';
import { Select } from '@/components/ui/select';
import { useState } from 'react';import { useTranslation } from "react-i18next";
export const AnimatedSelect = ({
  error,
  className,
  onFocus,
  onBlur,
  children,
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
    <motion.div
      animate={{
        scale: isFocused ? 1.01 : 1
      }}
      transition={{ duration: 0.2 }}>

      <Select
        className={`${error ? 'border-red-500' : ''} ${className || ''}`}
        onFocus={handleFocus}
        onBlur={handleBlur}
        {...props}>

        {children}
      </Select>
      {error &&
      <motion.div
        initial={{ opacity: 0, y: -5 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.15 }}
        className="text-red-500 text-xs mt-1">

          {error}
        </motion.div>
      }
    </motion.div>);

};