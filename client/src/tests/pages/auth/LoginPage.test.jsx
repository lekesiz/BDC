import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginPage from '../LoginPage'
import { render } from '../../../test/test-utils'
import * as authService from '../../../services/auth.service'

// Mock auth service
vi.mock('../../../services/auth.service')

describe('LoginPage', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form', () => {
    render(<LoginPage />)
    
    expect(screen.getByText(/Bienvenue/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Mot de passe/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Se connecter/i })).toBeInTheDocument()
  })

  it('shows validation errors for empty form submission', async () => {
    render(<LoginPage />)
    
    const submitButton = screen.getByRole('button', { name: /Se connecter/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Email requis/i)).toBeInTheDocument()
      expect(screen.getByText(/Mot de passe requis/i)).toBeInTheDocument()
    })
  })

  it('shows validation error for invalid email', async () => {
    render(<LoginPage />)
    
    const emailInput = screen.getByLabelText(/Email/i)
    await user.type(emailInput, 'invalid-email')
    
    const submitButton = screen.getByRole('button', { name: /Se connecter/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Format d'email invalide/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid credentials', async () => {
    const mockLogin = vi.fn().mockResolvedValue({
      user: { id: 1, email: 'test@example.com' },
      token: 'fake-token'
    })
    authService.login = mockLogin

    render(<LoginPage />)
    
    const emailInput = screen.getByLabelText(/Email/i)
    const passwordInput = screen.getByLabelText(/Mot de passe/i)
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    const submitButton = screen.getByRole('button', { name: /Se connecter/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      })
    })
  })

  it('shows error message on login failure', async () => {
    const mockLogin = vi.fn().mockRejectedValue(new Error('Invalid credentials'))
    authService.login = mockLogin

    render(<LoginPage />)
    
    const emailInput = screen.getByLabelText(/Email/i)
    const passwordInput = screen.getByLabelText(/Mot de passe/i)
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'wrongpassword')
    
    const submitButton = screen.getByRole('button', { name: /Se connecter/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Identifiants invalides/i)).toBeInTheDocument()
    })
  })

  it('navigates to forgot password page', async () => {
    render(<LoginPage />)
    
    const forgotPasswordLink = screen.getByText(/Mot de passe oublié/i)
    await user.click(forgotPasswordLink)
    
    // Check that navigation was called
    expect(window.location.pathname).toBe('/forgot-password')
  })

  it('navigates to register page', async () => {
    render(<LoginPage />)
    
    const registerLink = screen.getByText(/S'inscrire/i)
    await user.click(registerLink)
    
    // Check that navigation was called
    expect(window.location.pathname).toBe('/register')
  })

  it('shows loading state during login', async () => {
    const mockLogin = vi.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    )
    authService.login = mockLogin

    render(<LoginPage />)
    
    const emailInput = screen.getByLabelText(/Email/i)
    const passwordInput = screen.getByLabelText(/Mot de passe/i)
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    const submitButton = screen.getByRole('button', { name: /Se connecter/i })
    await user.click(submitButton)
    
    // Check loading state
    expect(screen.getByText(/Connexion en cours/i)).toBeInTheDocument()
    expect(submitButton).toBeDisabled()
  })
})