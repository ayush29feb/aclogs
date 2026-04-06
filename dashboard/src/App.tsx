import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { Suspense, useState } from 'react';
import HistoryView from './views/HistoryView.js';
import ProgressView from './views/ProgressView.js';
import { DateRangeContext, DATE_RANGES, sinceDate } from './DateRangeContext.js';

const NAV = [
  { to: '/history', icon: '▤', label: 'History' },
  { to: '/progress', icon: '↑', label: 'PRs' },
];

export default function App() {
  const [range, setRange] = useState<number | null>(null);
  const since = range != null ? sinceDate(range) : null;

  return (
    <DateRangeContext.Provider value={{ range, setRange, since }}>
      <header className="topbar">
        <div className="topbar-inner">
          <span className="topbar-brand">Gym Log</span>
          <div style={{ display: 'flex', gap: 2 }}>
            {DATE_RANGES.map(({ label, months }) => (
              <button
                key={label}
                onClick={() => setRange(months)}
                style={{
                  padding: '4px 8px',
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase',
                  border: 'none',
                  background: range === months ? '#ffffff' : 'transparent',
                  color: range === months ? '#000000' : '#555555',
                  cursor: 'pointer',
                  transition: 'color 0.1s, background 0.1s',
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="shell">
        <Suspense fallback={<p style={{ color: 'var(--text-3)', marginTop: 32, textAlign: 'center' }}>Loading…</p>}>
          <Routes>
            <Route path="/" element={<Navigate to="/history" replace />} />
            <Route path="/history" element={<HistoryView />} />
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
    </DateRangeContext.Provider>
  );
}
