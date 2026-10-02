import type { HealthStatus } from '../types/health';

export async function fetchHealth(signal?: AbortSignal): Promise<HealthStatus> {
  const response = await fetch('/api/v1/health', {
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Health check returned ${response.status}`);
  }

  return response.json() as Promise<HealthStatus>;
}