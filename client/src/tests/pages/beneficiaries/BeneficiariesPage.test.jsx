import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import BeneficiariesPage from '../BeneficiariesPage'
import { render } from '../../../test/test-utils'
import * as beneficiaryService from '../../../services/beneficiary.service'

vi.mock('../../../services/beneficiary.service')

const mockBeneficiaries = [
  {
    id: 1,
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    phone: '+33612345678',
    status: 'active',
    trainer: { name: 'Trainer 1' }
  },
  {
    id: 2,
    firstName: 'Jane',
    lastName: 'Smith',
    email: 'jane.smith@example.com',
    phone: '+33687654321',
    status: 'inactive',
    trainer: { name: 'Trainer 2' }
  }
]

describe('BeneficiariesPage', () => {
  const user = userEvent.setup()

  beforeEach(() => {
    vi.clearAllMocks()
    beneficiaryService.getBeneficiaries = vi.fn().mockResolvedValue({
      data: mockBeneficiaries,
      total: 2,
      page: 1,
      totalPages: 1
    })
  })

  it('renders beneficiaries list', async () => {
    render(<BeneficiariesPage />)
    
    await waitFor(() => {
      expect(screen.getByText('Bénéficiaires')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /Nouveau bénéficiaire/i })).toBeInTheDocument()
    })
    
    // Check if beneficiaries are displayed
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('Jane Smith')).toBeInTheDocument()
  })

  it('filters beneficiaries by search term', async () => {
    render(<BeneficiariesPage />)
    
    const searchInput = screen.getByPlaceholderText(/Rechercher/i)
    await user.type(searchInput, 'John')
    
    await waitFor(() => {
      expect(beneficiaryService.getBeneficiaries).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'John' })
      )
    })
  })

  it('filters beneficiaries by status', async () => {
    render(<BeneficiariesPage />)
    
    const statusFilter = screen.getByLabelText(/Statut/i)
    await user.selectOptions(statusFilter, 'active')
    
    await waitFor(() => {
      expect(beneficiaryService.getBeneficiaries).toHaveBeenCalledWith(
        expect.objectContaining({ status: 'active' })
      )
    })
  })

  it('navigates to create beneficiary page', async () => {
    render(<BeneficiariesPage />)
    
    const createButton = screen.getByRole('button', { name: /Nouveau bénéficiaire/i })
    await user.click(createButton)
    
    expect(window.location.pathname).toBe('/beneficiaries/new')
  })

  it('navigates to beneficiary detail page', async () => {
    render(<BeneficiariesPage />)
    
    await waitFor(() => {
      const firstBeneficiary = screen.getByText('John Doe')
      user.click(firstBeneficiary)
    })
    
    expect(window.location.pathname).toBe('/beneficiaries/1')
  })

  it('handles pagination', async () => {
    beneficiaryService.getBeneficiaries = vi.fn().mockResolvedValue({
      data: mockBeneficiaries,
      total: 20,
      page: 1,
      totalPages: 2
    })
    
    render(<BeneficiariesPage />)
    
    await waitFor(() => {
      const nextButton = screen.getByRole('button', { name: /Suivant/i })
      user.click(nextButton)
    })
    
    expect(beneficiaryService.getBeneficiaries).toHaveBeenCalledWith(
      expect.objectContaining({ page: 2 })
    )
  })

  it('exports beneficiaries to CSV', async () => {
    const mockExport = vi.fn()
    beneficiaryService.exportBeneficiaries = mockExport
    
    render(<BeneficiariesPage />)
    
    const exportButton = screen.getByRole('button', { name: /Exporter/i })
    await user.click(exportButton)
    
    expect(mockExport).toHaveBeenCalledWith('csv')
  })

  it('handles delete beneficiary', async () => {
    const mockDelete = vi.fn().mockResolvedValue({})
    beneficiaryService.deleteBeneficiary = mockDelete
    
    render(<BeneficiariesPage />)
    
    await waitFor(() => {
      const deleteButtons = screen.getAllByRole('button', { name: /Supprimer/i })
      user.click(deleteButtons[0])
    })
    
    // Confirm deletion
    const confirmButton = screen.getByRole('button', { name: /Confirmer/i })
    await user.click(confirmButton)
    
    expect(mockDelete).toHaveBeenCalledWith(1)
  })

  it('shows error message on API failure', async () => {
    beneficiaryService.getBeneficiaries = vi.fn().mockRejectedValue(
      new Error('Failed to fetch beneficiaries')
    )
    
    render(<BeneficiariesPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/Erreur lors du chargement/i)).toBeInTheDocument()
    })
  })

  it('displays empty state when no beneficiaries', async () => {
    beneficiaryService.getBeneficiaries = vi.fn().mockResolvedValue({
      data: [],
      total: 0,
      page: 1,
      totalPages: 0
    })
    
    render(<BeneficiariesPage />)
    
    await waitFor(() => {
      expect(screen.getByText(/Aucun bénéficiaire trouvé/i)).toBeInTheDocument()
    })
  })
})