import { useMemo, useState } from 'react';
import { ArrowRight, FileText, RotateCw, Search, SlidersHorizontal } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useStudies } from '../../hooks/use-studies';
import type { StudyModality, StudyType } from '../../types/study';
import { StudyLayout } from './StudyLayout';
import { formatStudyDate, modalityLabel, studyTypeLabel } from './study-format';

type ModalityFilter = 'ALL' | StudyModality;

const modalities: ModalityFilter[] = ['ALL', 'ULTRASOUND', 'MRI', 'CT', 'XRAY', 'UNKNOWN'];

export function StudiesPage() {
  const studiesQuery = useStudies();
  const [search, setSearch] = useState('');
  const [modality, setModality] = useState<ModalityFilter>('ALL');

  const studies = useMemo(() => studiesQuery.data ?? [], [studiesQuery.data]);
  const filteredStudies = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    return studies.filter((study) => {
      const matchesModality = modality === 'ALL' || study.modality === modality;
      const matchesSearch = !query
        || study.filename.toLocaleLowerCase().includes(query)
        || study.id.toLocaleLowerCase().includes(query)
        || studyTypeLabel(study.study_type).toLocaleLowerCase().includes(query)
        || modalityLabel(study.modality).toLocaleLowerCase().includes(query);
      return matchesModality && matchesSearch;
    }).sort((a, b) => b.created_at.localeCompare(a.created_at));
  }, [studies, search, modality]);

  return (
    <StudyLayout>
      <section className="study-main enter" aria-labelledby="studies-heading">
        <p className="study-kicker eyebrow">Study registry / 01</p>
        <h1 id="studies-heading" className="study-title">Registered studies</h1>
        <p className="study-intro">
          Browse the imaging studies available to this research workspace. Open a record to review its technical metadata.
        </p>

        <div className="study-toolbar">
          <p className="study-count" aria-live="polite">
            <strong>{studiesQuery.isLoading ? '—' : filteredStudies.length.toString().padStart(2, '0')}</strong>
            {search || modality !== 'ALL' ? `of ${studies.length} studies` : 'studies in registry'}
          </p>
          <div className="study-controls">
            <label className="study-search-wrap">
              <span className="sr-only">Search studies</span>
              <Search className="study-search-icon" size={15} aria-hidden="true" />
              <input
                className="study-search"
                type="search"
                placeholder="Search filename or ID"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
            </label>
            <label>
              <span className="sr-only">Filter by modality</span>
              <SlidersHorizontal className="sr-only" aria-hidden="true" />
              <select className="study-filter" value={modality} onChange={(event) => setModality(event.target.value as ModalityFilter)}>
                {modalities.map((item) => (
                  <option key={item} value={item}>{item === 'ALL' ? 'All modalities' : modalityLabel(item)}</option>
                ))}
              </select>
            </label>
          </div>
        </div>

        {studiesQuery.isLoading ? (
          <div className="study-list" aria-label="Loading studies" aria-busy="true">
            <div className="study-skeleton" />
            <div className="study-skeleton" />
            <div className="study-skeleton" />
          </div>
        ) : studiesQuery.isError ? (
          <div className="study-state" role="alert">
            <span className="study-state-icon"><RotateCw size={19} aria-hidden="true" /></span>
            <h2>Study registry unavailable</h2>
            <p>The study service did not respond. Your workspace is unchanged; try again when the connection is available.</p>
            <button className="study-button" type="button" onClick={() => void studiesQuery.refetch()}>
              <RotateCw size={14} aria-hidden="true" /> Retry connection
            </button>
          </div>
        ) : studies.length === 0 ? (
          <div className="study-state">
            <span className="study-state-icon"><FileText size={19} aria-hidden="true" /></span>
            <h2>No studies registered</h2>
            <p>There are no study records in this workspace yet. This catalog displays registered records only.</p>
          </div>
        ) : filteredStudies.length === 0 ? (
          <div className="study-state">
            <span className="study-state-icon"><Search size={19} aria-hidden="true" /></span>
            <h2>No matching studies</h2>
            <p>Try a different filename, identifier, or modality filter.</p>
            <button className="study-button secondary" type="button" onClick={() => { setSearch(''); setModality('ALL'); }}>
              Clear filters
            </button>
          </div>
        ) : (
          <div className="study-list">
            <div className="study-list-head" aria-hidden="true">
              <span>Study record</span><span>Format</span><span>Modality</span><span>Registered</span><span />
            </div>
            {filteredStudies.map((study) => (
              <Link key={study.id} to={`/studies/${encodeURIComponent(study.id)}`} className="study-row">
                <span className="study-file">
                  <span className="study-file-mark" aria-hidden="true"><FileText size={17} strokeWidth={1.5} /></span>
                  <span className="study-file-copy">
                    <span className="study-file-name" title={study.filename}>{study.filename}</span>
                    <span className="study-file-id">{study.id}</span>
                  </span>
                </span>
                <span className="study-type">{studyTypeLabel(study.study_type as StudyType)}</span>
                <span className="study-modality"><span className="study-chip">{modalityLabel(study.modality)}</span></span>
                <span className="study-created">{formatStudyDate(study.created_at)}</span>
                <ArrowRight className="study-arrow" size={15} aria-hidden="true" />
              </Link>
            ))}
          </div>
        )}
      </section>
    </StudyLayout>
  );
}