// TODO: i18n - processed
import { motion } from 'framer-motion';
import { pageTransition } from '@/lib/animations';import { useTranslation } from "react-i18next";
export const AnimatedPage = ({ children, className, ...props }) => {const { t } = useTranslation();
  return (
    <motion.div
      variants={pageTransition}
      initial="initial"
      animate="animate"
      exit="exit"
      className={className}
      {...props}>

      {children}
    </motion.div>);

};