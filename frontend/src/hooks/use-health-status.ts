import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '../api/health';

export function useHealthStatus() {
  return useQuery({
    queryKey: ['health'],
    queryFn: ({ signal }) => fetchHealth(signal),
    refetchInterval: 15_000,
    retry: false,
    staleTime: 5_000,
  });
}