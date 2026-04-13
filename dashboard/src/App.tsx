import { Suspense, useState, useRef } from 'react';
import HistoryView from './views/HistoryView.js';
import ProgressView from './views/ProgressView.js';
import { DateRangeContext, DATE_RANGES, sinceDate } from './DateRangeContext.js';

const PAGES = ['history', 'progress'] as const;
type Page = typeof PAGES[number];

const NAV: { id: Page; label: string; icon: (active: boolean) => React.ReactNode }[] = [
  {
    id: 'history',
    label: 'History',
    icon: (active) => (
      <svg width="26" height="26" viewBox="0 0 24 24" fill={active ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth={active ? 0 : 1.6} strokeLinecap="round" strokeLinejoin="round">
        {active ? (
          <path d="M8 3a1 1 0 0 0-1 1v1H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-1V4a1 1 0 0 0-1-1H8zm0 2h8v1H8V5zM6 8h12v11H6V8zm2 2v1.5h8V10H8zm0 3.5v1.5h5v-1.5H8z"/>
        ) : (
          <>
            <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
            <rect x="9" y="3" width="6" height="4" rx="1"/>
            <line x1="9" y1="12" x2="15" y2="12"/>
            <line x1="9" y1="16" x2="13" y2="16"/>
          </>
        )}
      </svg>
    ),
  },
  {
    id: 'progress',
    label: 'PRs',
    icon: (active) => (
      <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={active ? 2.2 : 1.6} strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/>
        <polyline points="16 7 22 7 22 13"/>
      </svg>
    ),
  },
];

export default function App() {
  const [range, setRange] = useState<number | null>(null);
  const [page, setPage] = useState<Page>('history');
  const [animClass, setAnimClass] = useState('');
  const since = range != null ? sinceDate(range) : null;

  const touchStartX = useRef<number | null>(null);
  const touchStartY = useRef<number | null>(null);

  function navigate(next: Page, direction: 'left' | 'right') {
    if (next === page) return;
    const cls = direction === 'left' ? 'slide-in-right' : 'slide-in-left';
    setPage(next);
    setAnimClass(cls);
    setTimeout(() => setAnimClass(''), 350);
  }

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
      if (dx < 0 && idx < PAGES.length - 1) navigate(PAGES[idx + 1], 'left');
      if (dx > 0 && idx > 0) navigate(PAGES[idx - 1], 'right');
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
        className={`shell ${animClass}`}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        <Suspense fallback={<p style={{ color: 'var(--text-3)', marginTop: 32, textAlign: 'center' }}>Loading…</p>}>
          {page === 'history' && <HistoryView />}
          {page === 'progress' && <ProgressView />}
        </Suspense>
      </main>

      <nav className="bottom-nav">
        <div className="tab-bar">
          {NAV.map(({ id, icon, label }, i) => (
            <button
              key={id}
              className={page === id ? 'active' : ''}
              onClick={() => navigate(id, PAGES.indexOf(id) > PAGES.indexOf(page) ? 'left' : 'right')}
            >
              <span className="nav-icon">{icon(page === id)}</span>
              <span className="nav-label">{label}</span>
            </button>
          ))}
        </div>
      </nav>
    </DateRangeContext.Provider>
  );
}
