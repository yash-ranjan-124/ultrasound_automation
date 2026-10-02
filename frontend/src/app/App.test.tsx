import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, describe, expect, it, vi } from 'vitest';
import App from './App';

function renderApp() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return render(<QueryClientProvider client={client}><MemoryRouter><App /></MemoryRouter></QueryClientProvider>);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe('overview foundation', () => {
  it('shows the three planned workflows and research disclaimer', () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok' }),
    }));
    renderApp();

    expect(screen.getByRole('heading', { name: /see the signal/i })).toBeInTheDocument();
    expect(screen.getByText('Ultrasound tracking')).toBeInTheDocument();
    expect(screen.getByText('Brain MRI segmentation')).toBeInTheDocument();
    expect(screen.getByText('Lung CT candidates')).toBeInTheDocument();
    expect(screen.getByText(/for research and educational use only/i)).toBeInTheDocument();
    expect(screen.getAllByText('Not yet implemented')).toHaveLength(3);
  });

  it('reads the health endpoint and reports an online service', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'ok' }),
    });
    vi.stubGlobal('fetch', fetchMock);
    renderApp();

    expect(await screen.findByText('Service online')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/health', expect.objectContaining({ method: 'GET' }));
  });

  it('shows an explicit offline state and retry action on a network error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network unavailable')));
    renderApp();

    expect(await screen.findByText('Service offline')).toBeInTheDocument();
    expect(screen.getByText(/the api did not respond/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });
});