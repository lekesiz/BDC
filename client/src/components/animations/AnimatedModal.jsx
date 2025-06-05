import { motion, AnimatePresence } from 'framer-motion';
import { modalOverlay, modalContent } from '@/lib/animations';
export const AnimatedModal = ({ 
  isOpen, 
  onClose,
  children, 
  className,
  overlayClassName
}) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className={`fixed inset-0 bg-black bg-opacity-25 z-40 ${overlayClassName || ''}`}
            variants={modalOverlay}
            initial="initial"
            animate="animate"
            exit="exit"
            onClick={onClose}
          />
          <motion.div
            className={`fixed inset-0 z-50 flex items-center justify-center p-4 ${className || ''}`}
            variants={modalContent}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <div onClick={(e) => e.stopPropagation()}>
              {children}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};