// TODO: i18n - processed
import React, { useState } from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogClose,
  DialogFooter } from
'../../../components/ui/dialog';import { useTranslation } from "react-i18next";
describe('Modal/Dialog Component', () => {
  it('renders a simple dialog when open', () => {
    render(
      <Dialog open={true}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
            <DialogDescription>This is a test dialog</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    );
    expect(screen.getByText('Test Dialog')).toBeInTheDocument();
    expect(screen.getByText('This is a test dialog')).toBeInTheDocument();
  });
  it('does not render when closed', () => {
    render(
      <Dialog open={false}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Hidden Dialog</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    );
    expect(screen.queryByText('Hidden Dialog')).not.toBeInTheDocument();
  });
  it('renders with footer', () => {
    render(
      <Dialog open={true}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Dialog with Footer</DialogTitle>
          </DialogHeader>
          <DialogFooter>
            <button>Cancel</button>
            <button>Save</button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
  });
  it('triggers onOpenChange when close button clicked', () => {
    const onOpenChange = vi.fn();
    render(
      <Dialog open={true} onOpenChange={onOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Closable Dialog</DialogTitle>
          </DialogHeader>
          <DialogClose />
        </DialogContent>
      </Dialog>
    );
    // Find and click the close button
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
  it('can be controlled externally', () => {
    const ControlledDialog = () => {const { t } = useTranslation();
      const [open, setOpen] = useState(false);
      return (
        <>
          <button onClick={() => setOpen(true)}>{t("components.open_dialog")}</button>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Controlled Dialog</DialogTitle>
              </DialogHeader>
            </DialogContent>
          </Dialog>
        </>);

    };
    render(<ControlledDialog />);
    // Initially closed
    expect(screen.queryByText('Controlled Dialog')).not.toBeInTheDocument();
    // Open dialog
    fireEvent.click(screen.getByText('Open Dialog'));
    // Should now be visible
    expect(screen.getByText('Controlled Dialog')).toBeInTheDocument();
  });
});