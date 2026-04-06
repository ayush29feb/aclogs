import { graphql, useLazyLoadQuery } from 'react-relay';
import { useState } from 'react';
import type { HistoryViewQuery as HistoryViewQueryType } from './__generated__/HistoryViewQuery.graphql.js';
import { useDateRange } from '../DateRangeContext.js';

const query = graphql`
  query HistoryViewQuery($limit: Int, $tag: String, $since: String) {
    workouts(limit: $limit, tag: $tag, since: $since) {
      id
      name
      date
      tags
      sleepHours
      notes
      blocks {
        id
        name
        order
        scheme
        rounds {
          round
          sets {
            id
            exerciseName
            weightLbs
            reps
            rpe
            durationSecs
            distanceM
            calories
            watts
            notes
          }
        }
      }
    }
  }
`;

function fmtDate(d: string): string {
  const [y, m, day] = d.split('-').map(Number);
  return new Date(y, m - 1, day).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

type Workout = HistoryViewQueryType['response']['workouts'][number];
type Block = Workout['blocks'][number];
type Round = Block['rounds'][number];
type Set = Round['sets'][number];

function formatSetChip(s: Set): string {
  if (s.weightLbs != null && s.reps != null) return `${s.weightLbs}×${s.reps}`;
  if (s.reps != null) return `×${s.reps}`;
  if (s.weightLbs != null) return `${s.weightLbs} lbs`;
  if (s.watts != null) return `${s.watts}W`;
  if (s.calories != null) return `${s.calories}cal`;
  if (s.durationSecs != null) return `${Math.round(s.durationSecs / 60)}min`;
  if (s.distanceM != null) return `${(s.distanceM / 1000).toFixed(1)}km`;
  return '—';
}

function BlockSection({ block }: { block: Block }) {
  // Flatten all sets across rounds, grouped by exercise name in order of first appearance
  const exerciseOrder: string[] = [];
  const bySets = new Map<string, Set[]>();
  for (const r of block.rounds) {
    for (const s of r.sets) {
      if (!bySets.has(s.exerciseName)) {
        exerciseOrder.push(s.exerciseName);
        bySets.set(s.exerciseName, []);
      }
      bySets.get(s.exerciseName)!.push(s);
    }
  }

  return (
    <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #2e2e2e' }}>
      <div style={{ fontSize: 9, fontWeight: 700, color: '#777777', textTransform: 'uppercase', letterSpacing: '0.14em', marginBottom: 8 }}>
        {block.name}
      </div>
      {exerciseOrder.map((name) => {
        const sets = bySets.get(name)!;
        const chips = sets.map(formatSetChip);
        return (
          <div key={name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '3px 0', gap: 12 }}>
            <span style={{ color: '#dddddd', fontSize: 13, fontWeight: 500, flexShrink: 0 }}>{name}</span>
            <span style={{ color: '#999999', fontSize: 12, textAlign: 'right', fontVariantNumeric: 'tabular-nums', letterSpacing: '0.03em' }}>{chips.join('  ·  ')}</span>
          </div>
        );
      })}
    </div>
  );
}

function WorkoutRow({ workout }: { workout: Workout }) {
  const [expanded, setExpanded] = useState(false);
  const setCount = workout.blocks.reduce(
    (acc, b) => acc + b.rounds.reduce((a, r) => a + r.sets.length, 0),
    0
  );

  return (
    <div style={{ border: '1px solid #2e2e2e', marginBottom: 8, background: '#0f0f0f' }}>
      <button
        style={{ padding: '14px 16px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 12, width: '100%', background: 'none', border: 'none', textAlign: 'left' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ minWidth: 0 }}>
          <div style={{ fontWeight: 700, fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#ffffff' }}>{workout.name}</div>
          <div style={{ fontSize: 11, color: '#888888', marginTop: 4, letterSpacing: '0.04em' }}>
            {fmtDate(workout.date)}<span style={{ margin: '0 6px', color: '#555' }}>·</span>{setCount} sets{workout.sleepHours != null && <><span style={{ margin: '0 6px', color: '#555' }}>·</span>{workout.sleepHours}h sleep</>}
          </div>
        </div>
        <span style={{ color: '#666666', fontSize: 10, flexShrink: 0 }}>{expanded ? '▲' : '▼'}</span>
      </button>
      {expanded && (
        <div style={{ padding: '0 16px 14px', borderTop: '1px solid #2e2e2e' }}>
          {workout.notes && (
            <div style={{ fontSize: 12, color: '#666666', marginTop: 10, marginBottom: 4 }}>{workout.notes}</div>
          )}
          {workout.blocks.map((b) => <BlockSection key={b.id} block={b} />)}
        </div>
      )}
    </div>
  );
}

const QUICK_TAGS = ['upper', 'lower', 'aps', 'mpa', 'test'];

function HistoryContent({ tag }: { tag: string | null }) {
  const { since } = useDateRange();
  const data = useLazyLoadQuery<HistoryViewQueryType>(query, { limit: 50, tag, since }, { fetchPolicy: 'network-only' });
  const workouts = data.workouts;

  if (workouts.length === 0) {
    return <p style={{ textAlign: 'center', color: 'var(--text-3)', marginTop: 32 }}>No workouts found.</p>;
  }

  return (
    <div>
      {workouts.map((w) => <WorkoutRow key={w.id} workout={w} />)}
    </div>
  );
}

export default function HistoryView() {
  const [activeTag, setActiveTag] = useState<string | null>(null);

  return (
    <div style={{ paddingTop: 12 }}>
      <div className="tag-row">
        <button
          className={`tag-btn${activeTag === null ? ' active' : ''}`}
          onClick={() => setActiveTag(null)}
        >
          All
        </button>
        {QUICK_TAGS.map((t) => (
          <button
            key={t}
            className={`tag-btn${activeTag === t ? ' active' : ''}`}
            onClick={() => setActiveTag(activeTag === t ? null : t)}
          >
            {t}
          </button>
        ))}
      </div>
      <HistoryContent tag={activeTag} />
    </div>
  );
}
