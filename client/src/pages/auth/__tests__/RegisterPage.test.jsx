import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import RegisterPage from '../RegisterPage'
import { render } from '../../../test/test-utils'
import * as authService from '../../../services/auth.service'

vi.mock('../../../services/auth.service')

describe('RegisterPage', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders registration form', () => {
    render(<RegisterPage />)
    
    expect(screen.getByText(/Créer un compte/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Prénom/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Nom/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Mot de passe/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /S'inscrire/i })).toBeInTheDocument()
  })

  it('shows validation errors for empty form submission', async () => {
    render(<RegisterPage />)
    
    const submitButton = screen.getByRole('button', { name: /S'inscrire/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Prénom requis/i)).toBeInTheDocument()
      expect(screen.getByText(/Nom requis/i)).toBeInTheDocument()
      expect(screen.getByText(/Email requis/i)).toBeInTheDocument()
      expect(screen.getByText(/Mot de passe requis/i)).toBeInTheDocument()
    })
  })

  it('shows password validation errors', async () => {
    render(<RegisterPage />)
    
    const passwordInput = screen.getByLabelText(/Mot de passe/i)
    await user.type(passwordInput, 'short')
    
    const submitButton = screen.getByRole('button', { name: /S'inscrire/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Le mot de passe doit contenir au moins 8 caractères/i)).toBeInTheDocument()
    })
  })

  it('submits form with valid data', async () => {
    const mockRegister = vi.fn().mockResolvedValue({
      user: { id: 1, email: 'newuser@example.com' },
      token: 'fake-token'
    })
    authService.register = mockRegister

    render(<RegisterPage />)
    
    const firstNameInput = screen.getByLabelText(/Prénom/i)
    const lastNameInput = screen.getByLabelText(/Nom/i)
    const emailInput = screen.getByLabelText(/Email/i)
    const passwordInput = screen.getByLabelText(/Mot de passe/i)
    
    await user.type(firstNameInput, 'John')
    await user.type(lastNameInput, 'Doe')
    await user.type(emailInput, 'john.doe@example.com')
    await user.type(passwordInput, 'Password123!')
    
    const submitButton = screen.getByRole('button', { name: /S'inscrire/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@example.com',
        password: 'Password123!'
      })
    })
  })

  it('shows error message when email already exists', async () => {
    const mockRegister = vi.fn().mockRejectedValue(new Error('Email already exists'))
    authService.register = mockRegister

    render(<RegisterPage />)
    
    const firstNameInput = screen.getByLabelText(/Prénom/i)
    const lastNameInput = screen.getByLabelText(/Nom/i)
    const emailInput = screen.getByLabelText(/Email/i)
    const passwordInput = screen.getByLabelText(/Mot de passe/i)
    
    await user.type(firstNameInput, 'John')
    await user.type(lastNameInput, 'Doe')
    await user.type(emailInput, 'existing@example.com')
    await user.type(passwordInput, 'Password123!')
    
    const submitButton = screen.getByRole('button', { name: /S'inscrire/i })
    await user.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/Cet email est déjà utilisé/i)).toBeInTheDocument()
    })
  })

  it('navigates to login page', async () => {
    render(<RegisterPage />)
    
    const loginLink = screen.getByText(/Se connecter/i)
    await user.click(loginLink)
    
    expect(window.location.pathname).toBe('/login')
  })

  it('accepts organization selection for tenant admins', async () => {
    render(<RegisterPage />)
    
    // Select tenant admin role
    const roleSelect = screen.getByLabelText(/Rôle/i)
    await user.selectOptions(roleSelect, 'tenant_admin')
    
    // Organization field should appear
    expect(screen.getByLabelText(/Organisation/i)).toBeInTheDocument()
    
    const orgSelect = screen.getByLabelText(/Organisation/i)
    await user.selectOptions(orgSelect, '1')
    
    expect(orgSelect.value).toBe('1')
  })

  it('shows loading state during registration', async () => {
    const mockRegister = vi.fn().mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    )
    authService.register = mockRegister

    render(<RegisterPage />)
    
    const firstNameInput = screen.getByLabelText(/Prénom/i)
    const lastNameInput = screen.getByLabelText(/Nom/i)
    const emailInput = screen.getByLabelText(/Email/i)
    const passwordInput = screen.getByLabelText(/Mot de passe/i)
    
    await user.type(firstNameInput, 'John')
    await user.type(lastNameInput, 'Doe')
    await user.type(emailInput, 'john.doe@example.com')
    await user.type(passwordInput, 'Password123!')
    
    const submitButton = screen.getByRole('button', { name: /S'inscrire/i })
    await user.click(submitButton)
    
    expect(screen.getByText(/Création du compte en cours/i)).toBeInTheDocument()
    expect(submitButton).toBeDisabled()
  })
})