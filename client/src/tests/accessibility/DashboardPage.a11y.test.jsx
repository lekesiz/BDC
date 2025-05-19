import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import DashboardPage from '../../pages/dashboard/DashboardPage';
import { useAuth } from '../../hooks/useAuth';

vi.mock('../../hooks/useAuth');
expect.extend(toHaveNoViolations);

describe('DashboardPage Accessibility', () => {
  beforeEach(() => {
    vi.mocked(useAuth).mockReturnValue({
      user: { id: 1, name: 'Test User', role: 'trainer' },
      isAuthenticated: true
    });
  });

  it('has no accessibility violations', async () => {
    const { container } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper heading hierarchy', () => {
    const { container } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    const headings = container.querySelectorAll('h1, h2, h3');
    const headingLevels = Array.from(headings).map(h => parseInt(h.tagName[1]));
    
    // Check that heading levels don't skip
    for (let i = 1; i < headingLevels.length; i++) {
      expect(headingLevels[i] - headingLevels[i-1]).toBeLessThanOrEqual(1);
    }
  });

  it('has proper landmarks', () => {
    const { getByRole } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    expect(getByRole('main')).toBeInTheDocument();
    expect(getByRole('navigation')).toBeInTheDocument();
  });

  it('has accessible data tables', async () => {
    const { container } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    const tables = container.querySelectorAll('table');
    for (const table of tables) {
      expect(table).toHaveAttribute('role', 'table');
      const headers = table.querySelectorAll('th');
      headers.forEach(header => {
        expect(header).toHaveAttribute('scope');
      });
    }
  });

  it('has accessible charts', () => {
    const { container } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    const charts = container.querySelectorAll('[role="img"][aria-label]');
    charts.forEach(chart => {
      expect(chart).toHaveAttribute('aria-label');
      expect(chart.getAttribute('aria-label')).not.toBe('');
    });
  });

  it('has keyboard navigation support', () => {
    const { getAllByRole } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    const interactiveElements = getAllByRole('button');
    interactiveElements.forEach(element => {
      expect(element).toHaveAttribute('tabindex');
      expect(parseInt(element.getAttribute('tabindex'))).toBeGreaterThanOrEqual(-1);
    });
  });

  it('has proper ARIA labels for icons', () => {
    const { container } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    const iconButtons = container.querySelectorAll('button svg');
    iconButtons.forEach(icon => {
      const button = icon.closest('button');
      expect(button).toHaveAttribute('aria-label');
    });
  });

  it('has accessible loading states', () => {
    const { getByRole } = render(
      <BrowserRouter>
        <DashboardPage loading={true} />
      </BrowserRouter>
    );
    
    const spinner = getByRole('status');
    expect(spinner).toHaveAttribute('aria-label', 'Loading');
  });

  it('has accessible error messages', () => {
    const { getByRole } = render(
      <BrowserRouter>
        <DashboardPage error="Something went wrong" />
      </BrowserRouter>
    );
    
    const alert = getByRole('alert');
    expect(alert).toBeInTheDocument();
    expect(alert).toHaveAttribute('aria-live', 'assertive');
  });

  it('supports reduced motion preference', () => {
    const { container } = render(
      <BrowserRouter>
        <DashboardPage />
      </BrowserRouter>
    );
    
    const animatedElements = container.querySelectorAll('[class*="transition"], [class*="animate"]');
    animatedElements.forEach(element => {
      const styles = window.getComputedStyle(element);
      expect(styles.getPropertyValue('transition-duration')).toBeTruthy();
    });
  });
});