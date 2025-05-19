import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import LoginPage from '../../../pages/auth/LoginPage'
import { render } from '../../../test/test-utils'
import * as authService from '../../../services/auth.service'

// Mock auth service
vi.mock('../../../services/auth.service', () => ({
  login: vi.fn(),
  forgotPassword: vi.fn()
}))

describe('LoginPage', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login form', () => {
    render(<LoginPage />)
    
    expect(screen.getByPlaceholderText(/correo electrónico/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/contraseña/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument()
  })

  it('shows validation errors for empty fields', async () => {
    render(<LoginPage />)
    
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
    await user.click(submitButton)
    
    expect(await screen.findByText(/email é obrigatório/i)).toBeInTheDocument()
    expect(await screen.findByText(/a senha é obrigatória/i)).toBeInTheDocument()
  })

  it('shows validation error for invalid email', async () => {
    render(<LoginPage />)
    
    const emailInput = screen.getByPlaceholderText(/correo electrónico/i)
    await user.type(emailInput, 'invalid-email')
    
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
    await user.click(submitButton)
    
    expect(await screen.findByText(/digite um email válido/i)).toBeInTheDocument()
  })

  it('submits form with valid credentials', async () => {
    vi.mocked(authService).login.mockResolvedValue({
      access_token: 'fake-token',
      user: { email: 'test@example.com', role: 'trainer' }
    })
    
    render(<LoginPage />)
    
    const emailInput = screen.getByPlaceholderText(/correo electrónico/i)
    const passwordInput = screen.getByPlaceholderText(/contraseña/i)
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(authService.login).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      })
    })
  })

  it('shows error message on login failure', async () => {
    vi.mocked(authService).login.mockRejectedValue({
      response: { data: { message: 'Invalid credentials' } }
    })
    
    render(<LoginPage />)
    
    const emailInput = screen.getByPlaceholderText(/correo electrónico/i)
    const passwordInput = screen.getByPlaceholderText(/contraseña/i)
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'wrongpassword')
    
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
    await user.click(submitButton)
    
    expect(await screen.findByText(/Invalid credentials/i)).toBeInTheDocument()
  })

  it('navigates to register page', async () => {
    render(<LoginPage />)
    
    const registerLink = screen.getByText(/crear cuenta nueva/i)
    expect(registerLink).toBeInTheDocument()
    expect(registerLink).toHaveAttribute('href', '/register')
  })

  it('opens forgot password modal', async () => {
    render(<LoginPage />)
    
    const forgotPasswordLink = screen.getByText(/olvidaste tu contraseña/i)
    await user.click(forgotPasswordLink)
    
    expect(await screen.findByText(/recuperar contraseña/i)).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/ingrese su correo electrónico/i)).toBeInTheDocument()
  })

  it('submits forgot password request', async () => {
    vi.mocked(authService).forgotPassword.mockResolvedValue({
      message: 'Reset link sent'
    })
    
    render(<LoginPage />)
    
    const forgotPasswordLink = screen.getByText(/olvidaste tu contraseña/i)
    await user.click(forgotPasswordLink)
    
    const emailInput = screen.getByPlaceholderText(/ingrese su correo electrónico/i)
    await user.type(emailInput, 'test@example.com')
    
    const sendButton = screen.getByRole('button', { name: /enviar enlace/i })
    await user.click(sendButton)
    
    await waitFor(() => {
      expect(authService.forgotPassword).toHaveBeenCalledWith('test@example.com')
    })
    
    expect(await screen.findByText(/se ha enviado un enlace/i)).toBeInTheDocument()
  })

  it('handles API error gracefully', async () => {
    vi.mocked(authService).login.mockRejectedValue(new Error('Network error'))
    
    render(<LoginPage />)
    
    const emailInput = screen.getByPlaceholderText(/correo electrónico/i)
    const passwordInput = screen.getByPlaceholderText(/contraseña/i)
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    const submitButton = screen.getByRole('button', { name: /iniciar sesión/i })
    await user.click(submitButton)
    
    expect(await screen.findByText(/error al conectar/i)).toBeInTheDocument()
  })

  it('maintains form state when toggling password visibility', async () => {
    render(<LoginPage />)
    
    const passwordInput = screen.getByPlaceholderText(/contraseña/i)
    await user.type(passwordInput, 'mypassword')
    
    expect(passwordInput).toHaveAttribute('type', 'password')
    
    const toggleButton = screen.getByRole('button', { name: /mostrar contraseña/i })
    await user.click(toggleButton)
    
    expect(passwordInput).toHaveAttribute('type', 'text')
    expect(passwordInput).toHaveValue('mypassword')
  })
});