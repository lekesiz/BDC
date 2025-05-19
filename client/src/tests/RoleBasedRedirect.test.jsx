import { render } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import RoleBasedRedirect from '@/components/common/RoleBasedRedirect'

vi.mock('@/hooks/useAuth', () => {
  return {
    useAuth: () => ({ user: { role: 'student' }, isLoading: false }),
  }
})

describe('RoleBasedRedirect', () => {
  it('redirects students to /portal', () => {
    const { container } = render(
      <MemoryRouter initialEntries={["/"]}>
        <RoleBasedRedirect />
      </MemoryRouter>
    )
    // Navigate renders <a href="/portal"> fallback in test DOM
    expect(container.innerHTML).toContain('/portal')
  })
}) 