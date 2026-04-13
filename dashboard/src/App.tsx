import { Suspense, useState, useRef } from 'react';
import HistoryView from './views/HistoryView.js';
import ProgressView from './views/ProgressView.js';
import { DateRangeContext, DATE_RANGES, sinceDate } from './DateRangeContext.js';

const PAGES = ['history', 'progress'] as const;
type Page = typeof PAGES[number];

const NAV: { id: Page; label: string; icon: React.ReactNode }[] = [
  {
    id: 'history',
    label: 'History',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
        <rect x="9" y="3" width="6" height="4" rx="1"/>
        <line x1="9" y1="12" x2="15" y2="12"/>
        <line x1="9" y1="16" x2="13" y2="16"/>
      </svg>
    ),
  },
  {
    id: 'progress',
    label: 'PRs',
    icon: (
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
        <polyline points="17 6 23 6 23 12"/>
      </svg>
    ),
  },
];

export default function App() {
  const [range, setRange] = useState<number | null>(null);
  const [page, setPage] = useState<Page>('history');
  const since = range != null ? sinceDate(range) : null;

  const touchStartX = useRef<number | null>(null);
  const touchStartY = useRef<number | null>(null);

  function handleTouchStart(e: React.TouchEvent) {
    touchStartX.current = e.touches[0].clientX;
    touchStartY.current = e.touches[0].clientY;
  }

  function handleTouchEnd(e: React.TouchEvent) {
    if (touchStartX.current === null || touchStartY.current === null) return;
    const dx = e.changedTouches[0].clientX - touchStartX.current;
    const dy = e.changedTouches[0].clientY - touchStartY.current;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
      const idx = PAGES.indexOf(page);
      if (dx < 0 && idx < PAGES.length - 1) setPage(PAGES[idx + 1]);
      if (dx > 0 && idx > 0) setPage(PAGES[idx - 1]);
    }
    touchStartX.current = null;
    touchStartY.current = null;
  }

  return (
    <DateRangeContext.Provider value={{ range, setRange, since }}>
      <header className="topbar">
        <div className="topbar-inner">
          <span className="topbar-brand">AC Logs</span>
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
                  color: range === months ? '#000000' : '#777777',
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

      <main
        className="shell"
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        <Suspense fallback={<p style={{ color: 'var(--text-3)', marginTop: 32, textAlign: 'center' }}>Loading…</p>}>
          {page === 'history' && <HistoryView />}
          {page === 'progress' && <ProgressView />}
        </Suspense>
      </main>

      <nav className="bottom-nav">
        {NAV.map(({ id, icon, label }) => (
          <button
            key={id}
            className={page === id ? 'active' : ''}
            onClick={() => setPage(id)}
          >
            <span className="nav-icon">{icon}</span>
            {label}
          </button>
        ))}
      </nav>
    </DateRangeContext.Provider>
  );
}
