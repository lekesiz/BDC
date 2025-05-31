import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProgramCard from '@/components/programs/ProgramCard';

const mockProgram = {
  id: 1,
  name: 'Test Program',
  description: 'Test program description',
  code: 'TEST001',
  status: 'active',
  duration: 30,
  enrolled_count: 15,
  max_participants: 25,
  module_count: 5,
  start_date: '2025-06-01',
  level: 'intermediate',
  category: 'technical'
};

const mockUser = {
  role: 'tenant_admin'
};

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ProgramCard', () => {
  it('renders program information correctly', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={mockUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    expect(screen.getByText('Test Program')).toBeInTheDocument();
    expect(screen.getByText('Code: TEST001')).toBeInTheDocument();
    expect(screen.getByText('Test program description')).toBeInTheDocument();
    expect(screen.getByText('Duration: 30 days')).toBeInTheDocument();
    expect(screen.getByText('Enrolled: 15 / 25')).toBeInTheDocument();
  });

  it('shows status badge with correct color', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={mockUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    const statusBadge = screen.getByText('Active');
    expect(statusBadge).toBeInTheDocument();
    expect(statusBadge).toHaveClass('bg-green-100', 'text-green-800');
  });

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={mockUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    const editButton = screen.getByRole('button', { name: /edit/i });
    fireEvent.click(editButton);
    
    expect(onEdit).toHaveBeenCalledWith(mockProgram);
  });

  it('calls onDelete when delete button is clicked and confirmed', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    // Mock confirm dialog
    global.confirm = vi.fn(() => true);
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={mockUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    const deleteButton = screen.getByRole('button', { name: /delete/i });
    fireEvent.click(deleteButton);
    
    expect(global.confirm).toHaveBeenCalledWith('Are you sure you want to delete this program?');
    expect(onDelete).toHaveBeenCalledWith(mockProgram.id);
  });

  it('does not show edit/delete buttons for non-admin users', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    const studentUser = { role: 'trainee' };
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={studentUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
  });

  it('displays level with correct icon', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={mockUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    expect(screen.getByText('Intermediate')).toBeInTheDocument();
  });

  it('displays formatted start date', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={mockUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    expect(screen.getByText(/Starts:/)).toBeInTheDocument();
  });

  it('displays category with proper formatting', () => {
    const onEdit = vi.fn();
    const onDelete = vi.fn();
    
    renderWithRouter(
      <ProgramCard 
        program={mockProgram} 
        user={mockUser} 
        onEdit={onEdit} 
        onDelete={onDelete} 
      />
    );
    
    expect(screen.getByText('Technical')).toBeInTheDocument();
  });
});