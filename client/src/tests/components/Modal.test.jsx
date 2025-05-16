import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Modal from '../../components/common/Modal';

describe('Modal Component', () => {
  it('renders when isOpen is true', () => {
    render(
      <Modal isOpen={true} onClose={() => {}}>
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={() => {}}>
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.queryByText('Modal content')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} showCloseButton>
        <div>Modal content</div>
      </Modal>
    );
    
    fireEvent.click(screen.getByRole('button', { name: /close/i }));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when backdrop is clicked', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <div>Modal content</div>
      </Modal>
    );
    
    fireEvent.click(screen.getByTestId('modal-backdrop'));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('does not close on backdrop click when closeOnBackdropClick is false', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose} closeOnBackdropClick={false}>
        <div>Modal content</div>
      </Modal>
    );
    
    fireEvent.click(screen.getByTestId('modal-backdrop'));
    expect(handleClose).not.toHaveBeenCalled();
  });

  it('renders title when provided', () => {
    render(
      <Modal isOpen={true} onClose={() => {}} title="Test Title">
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders footer when provided', () => {
    render(
      <Modal 
        isOpen={true} 
        onClose={() => {}} 
        footer={<button>Save</button>}
      >
        <div>Modal content</div>
      </Modal>
    );
    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('applies correct size classes', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={() => {}} size="sm">
        <div>Small Modal</div>
      </Modal>
    );
    expect(screen.getByTestId('modal-content')).toHaveClass('max-w-sm');
    
    rerender(
      <Modal isOpen={true} onClose={() => {}} size="lg">
        <div>Large Modal</div>
      </Modal>
    );
    expect(screen.getByTestId('modal-content')).toHaveClass('max-w-3xl');
  });

  it('handles escape key press', () => {
    const handleClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={handleClose}>
        <div>Modal content</div>
      </Modal>
    );
    
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(handleClose).toHaveBeenCalledTimes(1);
  });
});