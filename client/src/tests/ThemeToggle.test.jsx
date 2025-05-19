import { render, fireEvent } from '@testing-library/react'
import { vi, describe, it, expect } from 'vitest'
import ThemeToggle from '@/components/common/ThemeToggle'


describe('ThemeToggle', () => {
  it('toggles between light and dark', () => {
    const { getByRole } = render(<ThemeToggle />)
    const button = getByRole('button')
    // default to light
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    fireEvent.click(button)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    fireEvent.click(button)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
}) 