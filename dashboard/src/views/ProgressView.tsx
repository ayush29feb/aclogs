import { graphql, useLazyLoadQuery } from 'react-relay';
import { useState, Suspense, useEffect, useMemo } from 'react';
import type { ProgressViewProgressQuery as ProgressQueryType } from './__generated__/ProgressViewProgressQuery.graphql.js';
import type { ProgressViewExercisesQuery as ExercisesQueryType } from './__generated__/ProgressViewExercisesQuery.graphql.js';

const progressQuery = graphql`
  query ProgressViewProgressQuery($exerciseName: String!) {
    progress(exerciseName: $exerciseName) {
      exerciseName
      prs {
        reps
        weightLbs
        date
      }
      history {
        date
        weightLbs
        reps
      }
    }
  }
`;

const exercisesQuery = graphql`
  query ProgressViewExercisesQuery {
    exercises {
      id
      name
    }
  }
`;

const BIG_4 = ['Back Squat', 'Deadlift', 'Bench Press', 'Pull-ups'];

type Pr = { reps: number; weightLbs: number; date: string };
type HistoryEntry = { date: string; weightLbs: number | null | undefined; reps: number | null | undefined };

function Sparkline({ history }: { history: readonly HistoryEntry[] }) {
  const byDate = new Map<string, number>();
  for (const h of history) {
    if (h.weightLbs != null) {
      const prev = byDate.get(h.date) ?? 0;
      if (h.weightLbs > prev) byDate.set(h.date, h.weightLbs);
    }
  }
  const points = Array.from(byDate.entries()).sort(([a], [b]) => a.localeCompare(b));
  if (points.length < 2) return null;

  const W = 300;
  const H = 80;
  const pad = 8;
  const weights = points.map(([, w]) => w);
  const minW = Math.min(...weights);
  const maxW = Math.max(...weights);
  const range = maxW - minW || 1;

  const toX = (i: number) => pad + (i / (points.length - 1)) * (W - pad * 2);
  const toY = (w: number) => H - pad - ((w - minW) / range) * (H - pad * 2);

  const d = points
    .map(([, w], i) => `${i === 0 ? 'M' : 'L'}${toX(i).toFixed(1)},${toY(w).toFixed(1)}`)
    .join(' ');

  const lastX = toX(points.length - 1);
  const lastY = toY(weights[weights.length - 1]);

  return (
    <div style={{ marginTop: 16, overflowX: 'auto' }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-3)', marginBottom: 4 }}>Weight over time</div>
      <svg width={W} height={H} style={{ display: 'block' }}>
        <path d={d} fill="none" stroke="var(--accent)" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        <circle cx={lastX} cy={lastY} r={4} fill="var(--accent)" />
        <text x={lastX + 6} y={lastY + 4} fontSize={10} fill="var(--accent)" fontWeight="600">
          {weights[weights.length - 1]} lbs
        </text>
      </svg>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-3)', marginTop: 2, paddingLeft: pad, paddingRight: pad }}>
        <span>{points[0][0]}</span>
        <span>{points[points.length - 1][0]}</span>
      </div>
    </div>
  );
}

function PrTable({ prs }: { prs: readonly Pr[] }) {
  if (prs.length === 0) {
    return <p style={{ fontSize: 13, color: 'var(--text-3)', marginTop: 8 }}>No PR data yet.</p>;
  }
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13, marginTop: 8 }}>
      <thead>
        <tr style={{ borderBottom: '1px solid var(--border)' }}>
          <th style={{ textAlign: 'left', padding: '6px 0', color: 'var(--text-3)', fontWeight: 600 }}>Reps</th>
          <th style={{ textAlign: 'right', padding: '6px 0', color: 'var(--text-3)', fontWeight: 600 }}>Weight</th>
          <th style={{ textAlign: 'right', padding: '6px 0', color: 'var(--text-3)', fontWeight: 600 }}>Date</th>
        </tr>
      </thead>
      <tbody>
        {[...prs].sort((a, b) => a.reps - b.reps).map((pr) => (
          <tr key={`${pr.reps}-${pr.date}`} style={{ borderBottom: '1px solid var(--border-light)' }}>
            <td style={{ padding: '8px 0', fontWeight: 600 }}>{pr.reps}</td>
            <td style={{ padding: '8px 0', textAlign: 'right', color: 'var(--green)', fontWeight: 700 }}>{pr.weightLbs} lbs</td>
            <td style={{ padding: '8px 0', textAlign: 'right', color: 'var(--text-3)' }}>{pr.date}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ProgressContent({ exerciseName }: { exerciseName: string }) {
  const data = useLazyLoadQuery<ProgressQueryType>(progressQuery, { exerciseName });
  const { prs, history } = data.progress;

  return (
    <div className="card" style={{ padding: '16px' }}>
      <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{exerciseName}</div>
      <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 12 }}>
        {history.length} sets logged
      </div>
      <PrTable prs={prs} />
      <Sparkline history={history} />
    </div>
  );
}

function ExercisePicker({ value, onChange }: { value: string; onChange: (name: string) => void }) {
  const data = useLazyLoadQuery<ExercisesQueryType>(exercisesQuery, {});
  const exercises = useMemo(
    () => data.exercises.map((e) => e.name).sort(),
    [data.exercises]
  );

  useEffect(() => {
    if (exercises.length > 0 && !exercises.includes(value)) {
      onChange(exercises[0]);
    }
  }, [exercises, value, onChange]);

  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        width: '100%', padding: '10px 12px', fontSize: 14,
        borderRadius: 'var(--radius-sm)', border: '1.5px solid var(--border)',
        background: 'var(--card)', color: 'var(--text-1)', cursor: 'pointer',
      }}
    >
      {exercises.map((name) => (
        <option key={name} value={name}>{name}</option>
      ))}
    </select>
  );
}

export default function ProgressView() {
  const [selected, setSelected] = useState(BIG_4[0]);

  return (
    <div style={{ paddingTop: 16 }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
        {BIG_4.map((name) => (
          <button
            key={name}
            className={`tag-btn${selected === name ? ' active' : ''}`}
            onClick={() => setSelected(name)}
          >
            {name}
          </button>
        ))}
      </div>

      <div style={{ marginBottom: 16 }}>
        <Suspense fallback={null}>
          <ExercisePicker value={selected} onChange={setSelected} />
        </Suspense>
      </div>

      <Suspense fallback={<p style={{ textAlign: 'center', color: 'var(--text-3)', marginTop: 32 }}>Loading…</p>}>
        <ProgressContent exerciseName={selected} />
      </Suspense>
    </div>
  );
}
