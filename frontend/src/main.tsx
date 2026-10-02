import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import App from './app/App';
import { AppProviders } from './app/providers';
import { StudiesPage } from './features/studies/StudiesPage';
import { StudyDetailPage } from './features/studies/StudyDetailPage';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppProviders>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/studies" element={<StudiesPage />} />
          <Route path="/studies/:studyId" element={<StudyDetailPage />} />
        </Routes>
      </BrowserRouter>
    </AppProviders>
  </React.StrictMode>,
);