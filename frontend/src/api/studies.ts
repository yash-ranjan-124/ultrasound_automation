import type { Study } from '../types/study';

interface ApiErrorEnvelope {
  error?: {
    message?: unknown;
  };
}

export class StudyApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
    this.name = 'StudyApiError';
  }
}

async function requestStudyJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, {
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => undefined) as ApiErrorEnvelope | undefined;
    const message = typeof body?.error?.message === 'string'
      ? body.error.message
      : `Study request returned ${response.status}`;
    throw new StudyApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

export function fetchStudies(signal?: AbortSignal): Promise<Study[]> {
  return requestStudyJson<Study[]>('/api/v1/studies', signal);
}

export function fetchStudy(studyId: string, signal?: AbortSignal): Promise<Study> {
  return requestStudyJson<Study>(`/api/v1/studies/${encodeURIComponent(studyId)}`, signal);
}