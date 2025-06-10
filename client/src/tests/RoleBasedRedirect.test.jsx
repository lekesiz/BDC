// TODO: i18n - processed
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import RoleBasedRedirect from '@/components/common/RoleBasedRedirect';
// Mock the DashboardPage component
vi.mock('@/pages/dashboard/DashboardPage', () => ({
  default: () => <div data-testid="dashboard">Dashboard</div>
}));
// Mock the useAuth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn()
}));
import { useAuth } from '@/hooks/useAuth';import { useTranslation } from "react-i18next";
describe('RoleBasedRedirect', () => {
  it('redirects students to /portal', () => {
    // Set up the mock to return student role
    useAuth.mockReturnValue({ user: { role: 'student' }, isLoading: false });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<RoleBasedRedirect />} />
          <Route path="/portal" element={<div data-testid="portal">Portal</div>} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByTestId('portal')).toBeInTheDocument();
  });
  it('shows dashboard for admin/trainer', () => {
    useAuth.mockReturnValue({ user: { role: 'admin' }, isLoading: false });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<RoleBasedRedirect />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByTestId('dashboard')).toBeInTheDocument();
  });
  it('shows loading state', () => {
    useAuth.mockReturnValue({ user: null, isLoading: true });
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<RoleBasedRedirect />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});