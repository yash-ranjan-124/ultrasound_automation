import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { StudiesPage } from './StudiesPage';
import { StudyDetailPage } from './StudyDetailPage';

const study = {
  id: 'mv-2025-041',
  filename: 'cardiac-cycle-07.dcm',
  study_type: 'DICOM' as const,
  modality: 'ULTRASOUND' as const,
  created_at: '2025-02-10T09:30:00Z',
  metadata: { rows: 640, pixel_spacing: [0.7, 0.7], anonymized: true },
};

function renderRoute(initialEntry: string) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0 } },
  });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={[initialEntry]}>
        <Routes>
          <Route path="/studies" element={<StudiesPage />} />
          <Route path="/studies/:studyId" element={<StudyDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe('study registry', () => {
  it('filters registered records by modality and filename', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      json: async () => [study, { ...study, id: 'mv-2025-042', filename: 'head-mri.nii', modality: 'MRI' }],
    }));
    renderRoute('/studies');

    expect(await screen.findByText('cardiac-cycle-07.dcm')).toBeInTheDocument();
    fireEvent.change(screen.getByRole('searchbox', { name: 'Search studies' }), { target: { value: 'head' } });
    expect(screen.getByText('head-mri.nii')).toBeInTheDocument();
    expect(screen.queryByText('cardiac-cycle-07.dcm')).not.toBeInTheDocument();
  });

  it('opens a study detail from its registry link', async () => {
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => [study] })
      .mockResolvedValueOnce({ ok: true, json: async () => study }));
    renderRoute('/studies');

    fireEvent.click(await screen.findByRole('link', { name: /cardiac-cycle-07\.dcm/ }));

    expect(await screen.findByRole('heading', { name: 'cardiac-cycle-07.dcm' })).toBeInTheDocument();
    expect(screen.getByText('Technical metadata')).toBeInTheDocument();
  });

  it('presents study fields and technical metadata without rendering an image viewer', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => study }));
    renderRoute('/studies/mv-2025-041');

    expect(await screen.findByRole('heading', { name: 'cardiac-cycle-07.dcm' })).toBeInTheDocument();
    expect(screen.getByText('Technical metadata')).toBeInTheDocument();
    expect(screen.getByText('pixel_spacing')).toBeInTheDocument();
    expect(screen.getAllByRole('cell').some((cell) => cell.textContent?.includes('0.7'))).toBe(true);
    expect(screen.getByText(/for research and educational use only/i)).toBeInTheDocument();
  });

  it('explains when a study ID is unknown', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({ error: { message: 'Study not found' } }),
    }));
    renderRoute('/studies/missing-id');

    expect(await screen.findByRole('heading', { name: 'Study not found' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Return to studies' })).toBeInTheDocument();
  });

  it('shows a composed empty state for an empty registry', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => [] }));
    renderRoute('/studies');

    expect(await screen.findByRole('heading', { name: 'No studies registered' })).toBeInTheDocument();
  });

  it('offers retry when the registry request fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network unavailable')));
    renderRoute('/studies');

    expect(await screen.findByRole('heading', { name: 'Study registry unavailable' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /retry connection/i })).toBeInTheDocument();
  });
});