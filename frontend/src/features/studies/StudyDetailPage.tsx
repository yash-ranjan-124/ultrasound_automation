import { ArrowLeft, FileText, RotateCw } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';
import { StudyApiError } from '../../api/studies';
import { useStudy } from '../../hooks/use-studies';
import { StudyLayout } from './StudyLayout';
import { formatStudyDate, metadataRows, modalityLabel, studyTypeLabel } from './study-format';

export function StudyDetailPage() {
  const { studyId } = useParams<{ studyId: string }>();
  const studyQuery = useStudy(studyId);

  if (studyQuery.isLoading) {
    return (
      <StudyLayout>
        <section className="study-main enter" aria-label="Loading study details" aria-busy="true">
          <div className="study-detail-top"><Link to="/studies" className="study-back"><ArrowLeft size={14} /> All studies</Link></div>
          <div className="study-skeleton" style={{ marginTop: 26, height: 125 }} />
          <div className="study-skeleton" style={{ marginTop: 20, height: 245 }} />
        </section>
      </StudyLayout>
    );
  }

  if (studyQuery.isError) {
    const isUnknown = studyQuery.error instanceof StudyApiError && studyQuery.error.status === 404;
    return (
      <StudyLayout>
        <section className="study-main enter">
          <div className="study-detail-top"><Link to="/studies" className="study-back"><ArrowLeft size={14} aria-hidden="true" /> All studies</Link></div>
          <div className="study-state" role="alert" style={{ marginTop: 28 }}>
            <span className="study-state-icon"><FileText size={19} aria-hidden="true" /></span>
            <h1>{isUnknown ? 'Study not found' : 'Study details unavailable'}</h1>
            <p>{isUnknown
              ? 'This study ID is not registered in the workspace. It may have been removed or the link may be out of date.'
              : 'The study service could not retrieve this record. Check the connection and try again.'}</p>
            <div className="flex flex-wrap justify-center gap-2">
              {!isUnknown && (
                <button className="study-button" type="button" onClick={() => void studyQuery.refetch()}>
                  <RotateCw size={14} aria-hidden="true" /> Retry
                </button>
              )}
              <Link className="study-button secondary" to="/studies">Return to studies</Link>
            </div>
          </div>
        </section>
      </StudyLayout>
    );
  }

  const study = studyQuery.data;
  if (!study) return null;
  const rows = metadataRows(study);

  return (
    <StudyLayout>
      <article className="study-main enter">
        <div className="study-detail-top">
          <Link to="/studies" className="study-back"><ArrowLeft size={14} aria-hidden="true" /> All studies</Link>
          <span className="eyebrow text-[#71837b]">Record detail / technical metadata</span>
        </div>

        <header className="study-detail-head">
          <div className="study-detail-file">
            <span className="study-file-mark" aria-hidden="true"><FileText size={20} strokeWidth={1.4} /></span>
            <div className="min-w-0">
              <p className="study-kicker eyebrow">Registered imaging study</p>
              <h1 className="study-detail-title">{study.filename}</h1>
              <p className="study-detail-id">Study ID · {study.id}</p>
            </div>
          </div>
          <span className="study-chip">Metadata only</span>
        </header>

        <div className="study-metadata-layout">
          <dl className="study-facts" aria-label="Study properties">
            <div className="study-fact"><dt>Data format</dt><dd>{studyTypeLabel(study.study_type)}</dd></div>
            <div className="study-fact"><dt>Modality</dt><dd>{modalityLabel(study.modality)}</dd></div>
            <div className="study-fact"><dt>Registered</dt><dd>{formatStudyDate(study.created_at)}</dd></div>
            <div className="study-fact"><dt>Record ID</dt><dd className="mono">{study.id}</dd></div>
          </dl>

          <section className="study-metadata-panel" aria-labelledby="metadata-heading">
            <div className="study-section-heading">
              <h2 id="metadata-heading">Technical metadata</h2>
              <span>{rows.length.toString().padStart(2, '0')} fields</span>
            </div>
            {rows.length ? (
              <table className="metadata-table">
                <caption className="sr-only">Technical metadata fields for this study</caption>
                <tbody>
                  {rows.map(([key, value]) => (
                    <tr key={key}>
                      <th scope="row">{key}</th>
                      <td>{value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="metadata-empty">
                No technical metadata has been recorded for this study.
              </div>
            )}
          </section>
        </div>
      </article>
    </StudyLayout>
  );
}