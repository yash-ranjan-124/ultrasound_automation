export type StudyType = 'VIDEO' | 'NIFTI' | 'DICOM' | 'IMAGE';

export type StudyModality = 'ULTRASOUND' | 'MRI' | 'CT' | 'XRAY' | 'UNKNOWN';

export interface Study {
  id: string;
  filename: string;
  study_type: StudyType;
  modality: StudyModality;
  metadata: Record<string, unknown>;
  created_at: string;
}