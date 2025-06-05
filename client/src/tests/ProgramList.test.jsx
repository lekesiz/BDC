import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { render, screen } from '@testing-library/react';
import { describe, it, beforeAll, afterAll, afterEach, expect } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProgramListPage from '@/pages/beneficiaries/BeneficiariesPageEnhanced'; // placeholder path
const programsMock = [{ id: 1, name: 'Program A' }, { id: 2, name: 'Program B' }];
const server = setupServer(
  rest.get('/api/programs', (req, res, ctx) => {
    return res(ctx.status(200), ctx.json(programsMock));
  })
);
beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
describe('ProgramListPage', () => {
  it('displays programs correctly', async () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <ProgramListPage />
      </QueryClientProvider>
    );
    expect(await screen.findByText('Program A')).toBeInTheDocument();
    expect(screen.getByText('Program B')).toBeInTheDocument();
  });
});