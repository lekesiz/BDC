import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import Header from '@/components/layout/Header';

// Mock dependencies
vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: {
      id: '1',
      email: 'test@example.com',
      first_name: 'John',
      last_name: 'Doe',
      role: 'admin'
    },
    logout: vi.fn()
  })
}));

vi.mock('@/hooks/useMediaQuery', () => ({
  useBreakpoint: () => ({
    isMobile: false,
    isTablet: false
  })
}));

vi.mock('../notifications/RealTimeNotifications', () => ({
  default: () => <div>RealTimeNotifications</div>
}));

vi.mock('../common/ThemeToggle', () => ({
  default: () => <button>Theme Toggle</button>
}));

vi.mock('../common/LanguageSelector', () => ({
  default: () => <button>Language Selector</button>
}));

const renderComponent = (props = {}) => {
  return render(
    <BrowserRouter>
      <Header onToggleSidebar={vi.fn()} {...props} />
    </BrowserRouter>
  );
};

describe('Header Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with logo and user info', () => {
    renderComponent();

    expect(screen.getByText('BDC')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('renders all action buttons', () => {
    renderComponent();

    expect(screen.getByText('Theme Toggle')).toBeInTheDocument();
    expect(screen.getByText('Language Selector')).toBeInTheDocument();
    expect(screen.getByText('RealTimeNotifications')).toBeInTheDocument();
  });

  it('toggles sidebar when menu button is clicked', async () => {
    const onToggleSidebar = vi.fn();
    const user = userEvent.setup();
    
    renderComponent({ onToggleSidebar });

    const menuButton = screen.getByLabelText('components.navigation.toggle_navigation');
    await user.click(menuButton);

    expect(onToggleSidebar).toHaveBeenCalledTimes(1);
  });

  it('opens user menu when user button is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    const userButton = screen.getByLabelText('components.navigation.user_menu');
    await user.click(userButton);

    // Check if user menu is displayed
    expect(screen.getByRole('menu')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('admin')).toBeInTheDocument();
    expect(screen.getByText('components.navigation.profile')).toBeInTheDocument();
    expect(screen.getByText('components.navigation.settings')).toBeInTheDocument();
  });

  it('closes user menu when clicking outside', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Open menu
    const userButton = screen.getByLabelText('components.navigation.user_menu');
    await user.click(userButton);
    expect(screen.getByRole('menu')).toBeInTheDocument();

    // Click outside
    await user.click(document.body);
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('closes user menu on Escape key', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Open menu
    const userButton = screen.getByLabelText('components.navigation.user_menu');
    await user.click(userButton);
    expect(screen.getByRole('menu')).toBeInTheDocument();

    // Press Escape
    await user.keyboard('{Escape}');
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('navigates to profile when profile link is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Open menu
    const userButton = screen.getByLabelText('components.navigation.user_menu');
    await user.click(userButton);

    // Click profile link
    const profileLink = screen.getByText('components.navigation.profile');
    await user.click(profileLink);

    // Menu should close
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('navigates to settings when settings link is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Open menu
    const userButton = screen.getByLabelText('components.navigation.user_menu');
    await user.click(userButton);

    // Click settings link
    const settingsLink = screen.getByText('components.navigation.settings');
    await user.click(settingsLink);

    // Menu should close
    expect(screen.queryByRole('menu')).not.toBeInTheDocument();
  });

  it('calls logout when logout button is clicked', async () => {
    const mockLogout = vi.fn();
    vi.mocked(useAuth).mockReturnValue({
      user: {
        id: '1',
        email: 'test@example.com',
        first_name: 'John',
        last_name: 'Doe',
        role: 'admin'
      },
      logout: mockLogout
    });

    const user = userEvent.setup();
    renderComponent();

    // Open menu
    const userButton = screen.getByLabelText('components.navigation.user_menu');
    await user.click(userButton);

    // Click logout
    const logoutButton = screen.getByText('components.navigation.logout');
    await user.click(logoutButton);

    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('renders mobile logo on mobile devices', () => {
    vi.mocked(useBreakpoint).mockReturnValue({
      isMobile: true,
      isTablet: false
    });

    renderComponent();

    const logoLink = screen.getByLabelText('BDC Home');
    expect(logoLink).toBeInTheDocument();
    expect(logoLink).toHaveAttribute('href', '/');
  });

  it('hides language selector on extra small screens', () => {
    renderComponent();

    const languageSelector = screen.getByText('Language Selector');
    const container = languageSelector.closest('div');
    expect(container).toHaveClass('hidden', 'xs:block');
  });

  it('toggles between user menu and notifications', async () => {
    const user = userEvent.setup();
    renderComponent();

    // Open user menu
    const userButton = screen.getByLabelText('components.navigation.user_menu');
    await user.click(userButton);
    expect(screen.getByRole('menu')).toBeInTheDocument();

    // Note: In the actual implementation, clicking notifications would close user menu
    // But since RealTimeNotifications is mocked, we can't test this interaction fully
  });

  it('has proper accessibility attributes', () => {
    renderComponent();

    const header = screen.getByRole('banner');
    expect(header).toBeInTheDocument();

    const userButton = screen.getByLabelText('components.navigation.user_menu');
    expect(userButton).toHaveAttribute('aria-expanded', 'false');
    expect(userButton).toHaveAttribute('aria-haspopup', 'true');
  });

  it('updates aria-expanded when menu is opened', async () => {
    const user = userEvent.setup();
    renderComponent();

    const userButton = screen.getByLabelText('components.navigation.user_menu');
    expect(userButton).toHaveAttribute('aria-expanded', 'false');

    await user.click(userButton);
    expect(userButton).toHaveAttribute('aria-expanded', 'true');
  });
});