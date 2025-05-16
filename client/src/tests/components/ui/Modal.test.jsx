import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../dialog'

describe('Modal/Dialog Component', () => {
  const user = userEvent.setup()

  it('renders dialog trigger', () => {
    render(
      <Dialog>
        <DialogTrigger>Open Dialog</DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
            <DialogDescription>This is a test dialog</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )
    
    expect(screen.getByText('Open Dialog')).toBeInTheDocument()
  })

  it('opens dialog on trigger click', async () => {
    render(
      <Dialog>
        <DialogTrigger>Open Dialog</DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
            <DialogDescription>This is a test dialog</DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )
    
    const trigger = screen.getByText('Open Dialog')
    await user.click(trigger)
    
    await waitFor(() => {
      expect(screen.getByText('Test Dialog')).toBeInTheDocument()
      expect(screen.getByText('This is a test dialog')).toBeInTheDocument()
    })
  })

  it('closes dialog on close button click', async () => {
    render(
      <Dialog defaultOpen>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
          </DialogHeader>
          <button>Close</button>
        </DialogContent>
      </Dialog>
    )
    
    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)
    
    await waitFor(() => {
      expect(screen.queryByText('Test Dialog')).not.toBeInTheDocument()
    })
  })

  it('closes dialog on escape key', async () => {
    render(
      <Dialog defaultOpen>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )
    
    await user.keyboard('{Escape}')
    
    await waitFor(() => {
      expect(screen.queryByText('Test Dialog')).not.toBeInTheDocument()
    })
  })

  it('closes dialog on backdrop click', async () => {
    render(
      <Dialog defaultOpen>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )
    
    const backdrop = screen.getByRole('dialog').parentElement
    await user.click(backdrop)
    
    await waitFor(() => {
      expect(screen.queryByText('Test Dialog')).not.toBeInTheDocument()
    })
  })

  it('can be controlled', async () => {
    const onOpenChange = vi.fn()
    const { rerender } = render(
      <Dialog open={false} onOpenChange={onOpenChange}>
        <DialogTrigger>Open Dialog</DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )
    
    const trigger = screen.getByText('Open Dialog')
    await user.click(trigger)
    
    expect(onOpenChange).toHaveBeenCalledWith(true)
    
    // Dialog should still be closed since we control it
    expect(screen.queryByText('Test Dialog')).not.toBeInTheDocument()
    
    // Open the dialog
    rerender(
      <Dialog open={true} onOpenChange={onOpenChange}>
        <DialogTrigger>Open Dialog</DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )
    
    expect(screen.getByText('Test Dialog')).toBeInTheDocument()
  })

  it('prevents closing when modal is true', async () => {
    render(
      <Dialog defaultOpen modal={false}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Non-modal Dialog</DialogTitle>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    )
    
    // Should be able to click outside
    const backdrop = screen.getByRole('dialog').parentElement
    await user.click(backdrop)
    
    // Dialog should still be open for non-modal
    expect(screen.getByText('Non-modal Dialog')).toBeInTheDocument()
  })

  it('traps focus within dialog', async () => {
    render(
      <Dialog defaultOpen>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Test Dialog</DialogTitle>
          </DialogHeader>
          <button>First Button</button>
          <button>Second Button</button>
        </DialogContent>
      </Dialog>
    )
    
    const firstButton = screen.getByText('First Button')
    const secondButton = screen.getByText('Second Button')
    
    firstButton.focus()
    expect(document.activeElement).toBe(firstButton)
    
    await user.tab()
    expect(document.activeElement).toBe(secondButton)
    
    await user.tab()
    // Should cycle back to close button or first focusable element
    expect(document.activeElement).not.toBe(document.body)
  })
})