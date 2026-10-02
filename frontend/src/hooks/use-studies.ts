import { useQuery } from '@tanstack/react-query';
import { fetchStudies, fetchStudy } from '../api/studies';

export const studyQueryKeys = {
  all: ['studies'] as const,
  detail: (studyId: string | undefined) => ['studies', studyId] as const,
};

export function useStudies() {
  return useQuery({
    queryKey: studyQueryKeys.all,
    queryFn: ({ signal }) => fetchStudies(signal),
    retry: false,
  });
}

export function useStudy(studyId: string | undefined) {
  return useQuery({
    queryKey: studyQueryKeys.detail(studyId),
    queryFn: ({ signal }) => {
      if (!studyId) {
        throw new Error('A study ID is required.');
      }
      return fetchStudy(studyId, signal);
    },
    enabled: Boolean(studyId),
    retry: false,
  });
}