import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchStudies, fetchStudy, StudyApiError } from './studies';

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('study API', () => {
  it('loads the study collection using the versioned endpoint', async () => {
    const studyList = [{
      id: 'study-1',
      filename: 'scan.nii.gz',
      study_type: 'NIFTI',
      modality: 'MRI',
      metadata: { shape: [4, 5, 6] },
      created_at: '2026-10-02T10:00:00Z',
    }];
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => studyList,
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchStudies()).resolves.toEqual(studyList);
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/studies', {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: undefined,
    });
  });

  it('encodes the study ID and reports a safe not-found error', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => ({
        error: { code: 'STUDY_NOT_FOUND', message: 'The requested imaging study does not exist.' },
      }),
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchStudy('id/with spaces')).rejects.toMatchObject({
      name: 'StudyApiError',
      status: 404,
      message: 'The requested imaging study does not exist.',
    } satisfies Partial<StudyApiError>);
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/studies/id%2Fwith%20spaces', expect.any(Object));
  });

  it('uses a fallback message when the server error has no message', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({}),
    }));

    await expect(fetchStudies()).rejects.toThrow('Study request returned 503');
  });
});