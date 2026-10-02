import { ArrowUpRight, House, Layers3 } from 'lucide-react';
import { NavLink, Link } from 'react-router-dom';
import './studies.css';

interface StudyLayoutProps {
  children: React.ReactNode;
}

export function StudyLayout({ children }: StudyLayoutProps) {
  return (
    <main className="study-shell">
      <div className="study-wrap">
        <header className="study-header">
          <Link to="/" className="study-brand" aria-label="MedVision AI Lab overview">
            <span className="study-brand-mark" aria-hidden="true" />
            <span>
              <span className="study-brand-name">MedVision <span className="font-medium">AI Lab</span></span>
              <span className="study-brand-sub">Research imaging workstation</span>
            </span>
          </Link>
          <nav className="study-nav" aria-label="Primary navigation">
            <NavLink to="/" end className="study-nav-link">
              <House size={14} aria-hidden="true" />
              Overview
            </NavLink>
            <NavLink to="/studies" end className="study-nav-link">
              <Layers3 size={14} aria-hidden="true" />
              Studies
              <ArrowUpRight size={12} aria-hidden="true" />
            </NavLink>
          </nav>
        </header>
        {children}
        <footer className="study-disclaimer">
          <strong>Research use only</strong>
          For research and educational use only. MedVision AI Lab is not a medical device and is not intended for diagnosis, treatment, or clinical decision-making.
        </footer>
      </div>
    </main>
  );
}