import type { Study, StudyModality, StudyType } from '../../types/study';

const typeLabels: Record<StudyType, string> = {
  VIDEO: 'Video',
  NIFTI: 'NIfTI',
  DICOM: 'DICOM',
  IMAGE: 'Image',
};

const modalityLabels: Record<StudyModality, string> = {
  ULTRASOUND: 'Ultrasound',
  MRI: 'MRI',
  CT: 'CT',
  XRAY: 'X-ray',
  UNKNOWN: 'Unknown',
};

export function studyTypeLabel(type: StudyType): string {
  return typeLabels[type] ?? type;
}

export function modalityLabel(modality: StudyModality): string {
  return modalityLabels[modality] ?? modality;
}

export function formatStudyDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Date unavailable';
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function metadataRows(study: Study): [string, string][] {
  return Object.entries(study.metadata ?? {})
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => [key, stringifyMetadataValue(value)]);
}

function stringifyMetadataValue(value: unknown): string {
  if (value === null) return 'null';
  if (typeof value === 'string') return value || '—';
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  try {
    return JSON.stringify(value, null, 2) ?? '—';
  } catch {
    return 'Value cannot be displayed';
  }
}