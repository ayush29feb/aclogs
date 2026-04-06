import React, { useState, Suspense } from 'react';
import { graphql, useLazyLoadQuery } from 'react-relay';
import type { ProgressViewPrsQuery as PrsQueryType } from './__generated__/ProgressViewPrsQuery.graphql.js';
import type { ProgressViewHistoryQuery as HistoryQueryType } from './__generated__/ProgressViewHistoryQuery.graphql.js';

const prsQuery = graphql`
  query ProgressViewPrsQuery {
    exercisePrs {
      exerciseName
      isCompound
      pr1
      pr3
      pr5
      pr8
    }
  }
`;

const historyQuery = graphql`
  query ProgressViewHistoryQuery($exerciseName: String!) {
    progress(exerciseName: $exerciseName) {
      history {
        date
        weightLbs
      }
    }
  }
`;

type PrRow = PrsQueryType['response']['exercisePrs'][number];
type HistoryEntry = { date: string; weightLbs: number | null | undefined };

function fmt(v: number | null | undefined): React.ReactNode {
  if (v == null) return <span style={{ color: '#333333' }}>—</span>;
  return `${v}`;
}

function Sparkline({ exerciseName }: { exerciseName: string }) {
  const data = useLazyLoadQuery<HistoryQueryType>(historyQuery, { exerciseName });
  const history = data.progress.history;

  const byDate = new Map<string, number>();
  for (const h of history) {
    if (h.weightLbs != null) {
      const prev = byDate.get(h.date) ?? 0;
      if (h.weightLbs > prev) byDate.set(h.date, h.weightLbs);
    }
  }
  const points = Array.from(byDate.entries()).sort(([a], [b]) => a.localeCompare(b));
  if (points.length < 2) return <p style={{ fontSize: 12, color: 'var(--text-3)', margin: '8px 0 0' }}>Not enough data for chart.</p>;

  const W = 300;
  const H = 70;
  const pad = 8;
  const weights = points.map(([, w]) => w);
  const minW = Math.min(...weights);
  const maxW = Math.max(...weights);
  const range = maxW - minW || 1;
  const toX = (i: number) => pad + (i / (points.length - 1)) * (W - pad * 2);
  const toY = (w: number) => H - pad - ((w - minW) / range) * (H - pad * 2);
  const d = points.map(([, w], i) => `${i === 0 ? 'M' : 'L'}${toX(i).toFixed(1)},${toY(w).toFixed(1)}`).join(' ');
  const lastX = toX(points.length - 1);
  const lastY = toY(weights[weights.length - 1]);

  return (
    <div style={{ marginTop: 12 }}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: '100%', maxWidth: W, display: 'block' }} aria-label={`${exerciseName} weight over time`}>
        <path d={d} fill="none" stroke="var(--accent)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={lastX} cy={lastY} r={4} fill="var(--accent)" />
        <text x={lastX - 6} y={lastY - 6} fontSize={10} fill="var(--accent)" fontWeight="600" textAnchor="end">
          {weights[weights.length - 1]} lbs
        </text>
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-3)', paddingInline: pad }}>
        <span>{points[0][0]}</span>
        <span>{points[points.length - 1][0]}</span>
      </div>
    </div>
  );
}

function PrTable() {
  const data = useLazyLoadQuery<PrsQueryType>(prsQuery, {});
  const rows = data.exercisePrs;
  const [selected, setSelected] = useState<string | null>(null);

  const compounds = rows.filter((r) => r.isCompound);
  const accessories = rows.filter((r) => !r.isCompound);

  const thStyle: React.CSSProperties = {
    padding: '10px 10px', fontSize: 9, fontWeight: 700, color: '#777777',
    textAlign: 'right', textTransform: 'uppercase', letterSpacing: '0.14em',
    borderBottom: '1px solid #222222', whiteSpace: 'nowrap',
  };
  const tdStyle: React.CSSProperties = {
    padding: '10px 10px', fontSize: 13, textAlign: 'right', color: '#ffffff', fontWeight: 500,
    fontVariantNumeric: 'tabular-nums',
  };
  const nameTdStyle: React.CSSProperties = {
    padding: '10px 10px', fontSize: 12, fontWeight: 700, color: '#ffffff', textAlign: 'left', whiteSpace: 'nowrap',
    textTransform: 'uppercase', letterSpacing: '0.04em',
  };

  const renderRow = (row: PrRow) => {
    const isSelected = selected === row.exerciseName;
    return (
      <>
        <tr
          key={row.exerciseName}
          onClick={() => setSelected(isSelected ? null : row.exerciseName)}
          style={{ borderBottom: '1px solid var(--border)', cursor: 'pointer', background: isSelected ? '#1a1a1a' : undefined }}
        >
          <td style={nameTdStyle}>{row.exerciseName}</td>
          <td style={tdStyle}>{fmt(row.pr1)}</td>
          <td style={tdStyle}>{fmt(row.pr3)}</td>
          <td style={tdStyle}>{fmt(row.pr5)}</td>
          <td style={tdStyle}>{fmt(row.pr8)}</td>
        </tr>
        {isSelected && (
          <tr key={`${row.exerciseName}-detail`}>
            <td colSpan={5} style={{ padding: '0 8px 12px', background: '#1a1a1a' }}>
              <Suspense fallback={<p style={{ fontSize: 12, color: 'var(--text-3)', margin: '8px 0' }}>Loading…</p>}>
                <Sparkline exerciseName={row.exerciseName} />
              </Suspense>
            </td>
          </tr>
        )}
      </>
    );
  };

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>
            <th style={{ ...thStyle, textAlign: 'left' }}>Exercise</th>
            <th style={thStyle}>1RM</th>
            <th style={thStyle}>3RM</th>
            <th style={thStyle}>5RM</th>
            <th style={thStyle}>8RM</th>
          </tr>
        </thead>
        <tbody>
          {compounds.map(renderRow)}
          {accessories.length > 0 && (
            <tr>
              <td colSpan={5} style={{ padding: '12px 10px 4px', fontSize: 10, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                Accessories
              </td>
            </tr>
          )}
          {accessories.map(renderRow)}
        </tbody>
      </table>
    </div>
  );
}

export default function ProgressView() {
  return (
    <div style={{ paddingTop: 16 }}>
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <Suspense fallback={<p style={{ textAlign: 'center', color: 'var(--text-3)', padding: 32 }}>Loading…</p>}>
          <PrTable />
        </Suspense>
      </div>
    </div>
  );
}
