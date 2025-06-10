// TODO: i18n - processed
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { buttonHover } from '@/lib/animations';import { useTranslation } from "react-i18next";
export const AnimatedButton = ({
  children,
  className,
  onClick,
  disabled,
  ...props
}) => {const { t } = useTranslation();
  return (
    <motion.div
      whileHover={!disabled ? buttonHover.whileHover : undefined}
      whileTap={!disabled ? buttonHover.whileTap : undefined}
      transition={buttonHover.transition}>

      <Button
        className={className}
        onClick={onClick}
        disabled={disabled}
        {...props}>

        {children}
      </Button>
    </motion.div>);

};