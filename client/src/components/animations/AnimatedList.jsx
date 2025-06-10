// TODO: i18n - processed
import { motion } from 'framer-motion';
import { listContainer, listItem } from '@/lib/animations';import { useTranslation } from "react-i18next";
export const AnimatedList = ({ children, className, ...props }) => {const { t } = useTranslation();
  return (
    <motion.ul
      variants={listContainer}
      initial="hidden"
      animate="visible"
      className={className}
      {...props}>

      {children}
    </motion.ul>);

};
export const AnimatedListItem = ({ children, className, ...props }) => {const { t } = useTranslation();
  return (
    <motion.li
      variants={listItem}
      className={className}
      {...props}>

      {children}
    </motion.li>);

};