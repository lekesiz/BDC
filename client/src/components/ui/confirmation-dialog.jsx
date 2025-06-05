import { AlertCircle, X } from 'lucide-react';
import { Modal, ModalHeader, ModalBody, ModalFooter } from './modal';
import { Button } from './button';
/**
 * ConfirmationDialog component for showing confirmations with cancel/confirm options
 * 
 * @param {object} props - Component props
 * @param {boolean} props.isOpen - Whether the dialog is open
 * @param {function} props.onClose - Function to close the dialog
 * @param {function} props.onConfirm - Function to call when confirmed
 * @param {string} props.title - Dialog title
 * @param {string} props.description - Dialog description
 * @param {string} props.confirmText - Text for the confirm button
 * @param {string} props.cancelText - Text for the cancel button
 * @param {boolean} props.isDanger - Whether this is a dangerous action (changes styling)
 * @returns {JSX.Element} ConfirmationDialog component
 */
const ConfirmationDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  isDanger = false,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm">
      <div className="flex items-start justify-between">
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        <button
          type="button"
          className="text-gray-400 hover:text-gray-500"
          onClick={onClose}
        >
          <X className="h-5 w-5" />
        </button>
      </div>
      <ModalBody className="pt-2 pb-4">
        {isDanger && (
          <div className="flex items-center text-amber-500 mb-2">
            <AlertCircle className="h-5 w-5 mr-2" />
            <span className="font-medium">Warning</span>
          </div>
        )}
        <p className="text-sm text-gray-500">{description}</p>
      </ModalBody>
      <ModalFooter>
        <Button variant="outline" onClick={onClose}>
          {cancelText}
        </Button>
        <Button
          variant={isDanger ? 'destructive' : 'default'}
          onClick={() => {
            onConfirm();
            onClose();
          }}
        >
          {confirmText}
        </Button>
      </ModalFooter>
    </Modal>
  );
};
export default ConfirmationDialog;