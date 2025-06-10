// TODO: i18n - processed
import { motion } from 'framer-motion';
import { Table } from '@/components/ui/table';
import { listContainer, listItem } from '@/lib/animations';import { useTranslation } from "react-i18next";
export const AnimatedTable = ({ children, className, ...props }) => {const { t } = useTranslation();
  return (
    <motion.div
      variants={listContainer}
      initial="hidden"
      animate="visible">

      <Table className={className} {...props}>
        {children}
      </Table>
    </motion.div>);

};
export const AnimatedTableRow = ({ children, className, ...props }) => {const { t } = useTranslation();
  return (
    <motion.tr
      variants={listItem}
      className={className}
      {...props}>

      {children}
    </motion.tr>);

};