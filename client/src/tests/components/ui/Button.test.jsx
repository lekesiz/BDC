import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../button'

describe('Button Component', () => {
  const user = userEvent.setup()

  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: /Click me/i })).toBeInTheDocument()
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    const button = screen.getByRole('button', { name: /Click me/i })
    await user.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('can be disabled', () => {
    render(<Button disabled>Disabled</Button>)
    
    const button = screen.getByRole('button', { name: /Disabled/i })
    expect(button).toBeDisabled()
  })

  it('applies variant styles', () => {
    render(
      <>
        <Button variant="default">Default</Button>
        <Button variant="destructive">Destructive</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="ghost">Ghost</Button>
        <Button variant="link">Link</Button>
      </>
    )
    
    expect(screen.getByRole('button', { name: /Default/i })).toHaveClass('bg-primary')
    expect(screen.getByRole('button', { name: /Destructive/i })).toHaveClass('bg-destructive')
    expect(screen.getByRole('button', { name: /Outline/i })).toHaveClass('border')
    expect(screen.getByRole('button', { name: /Secondary/i })).toHaveClass('bg-secondary')
    expect(screen.getByRole('button', { name: /Ghost/i })).toHaveClass('hover:bg-accent')
    expect(screen.getByRole('button', { name: /Link/i })).toHaveClass('underline-offset-4')
  })

  it('applies size styles', () => {
    render(
      <>
        <Button size="default">Default</Button>
        <Button size="sm">Small</Button>
        <Button size="lg">Large</Button>
        <Button size="icon">Icon</Button>
      </>
    )
    
    expect(screen.getByRole('button', { name: /Default/i })).toHaveClass('h-10 px-4 py-2')
    expect(screen.getByRole('button', { name: /Small/i })).toHaveClass('h-9 px-3')
    expect(screen.getByRole('button', { name: /Large/i })).toHaveClass('h-11 px-8')
    expect(screen.getByRole('button', { name: /Icon/i })).toHaveClass('h-10 w-10')
  })

  it('supports as child', () => {
    render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    )
    
    const link = screen.getByRole('link', { name: /Link Button/i })
    expect(link).toHaveAttribute('href', '/test')
  })

  it('forwards ref correctly', () => {
    const ref = vi.fn()
    render(<Button ref={ref}>Button</Button>)
    
    expect(ref).toHaveBeenCalled()
  })

  it('applies custom className', () => {
    render(<Button className="custom-class">Custom</Button>)
    
    const button = screen.getByRole('button', { name: /Custom/i })
    expect(button).toHaveClass('custom-class')
  })

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>)
    
    const button = screen.getByRole('button', { name: /Loading/i })
    expect(button).toBeDisabled()
    expect(button.querySelector('.animate-spin')).toBeInTheDocument()
  })
})