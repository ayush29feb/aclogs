import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { Suspense } from 'react';
import HistoryView from './views/HistoryView.js';
import ProgressView from './views/ProgressView.js';

const NAV = [
  { to: '/history',  icon: '📋', label: 'History'  },
  { to: '/progress', icon: '📈', label: 'Progress' },
];

export default function App() {
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <span className="topbar-brand">💪 Gym</span>
        </div>
      </header>

      <main className="shell">
        <Suspense fallback={<p style={{ color: 'var(--text-3)', marginTop: 32, textAlign: 'center' }}>Loading…</p>}>
          <Routes>
            <Route path="/" element={<Navigate to="/history" replace />} />
            <Route path="/history"  element={<HistoryView />} />
            <Route path="/progress" element={<ProgressView />} />
          </Routes>
        </Suspense>
      </main>

      <nav className="bottom-nav">
        {NAV.map(({ to, icon, label }) => (
          <NavLink key={to} to={to} className={({ isActive }) => isActive ? 'active' : ''}>
            <span className="nav-icon">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
