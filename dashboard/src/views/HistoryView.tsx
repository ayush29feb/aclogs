import { graphql, useLazyLoadQuery } from 'react-relay';
import { useState } from 'react';
import type { HistoryViewQuery as HistoryViewQueryType } from './__generated__/HistoryViewQuery.graphql.js';

const query = graphql`
  query HistoryViewQuery($limit: Int, $tag: String) {
    workouts(limit: $limit, tag: $tag) {
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
    <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--border-light)' }}>
      <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: 6 }}>
        {block.name}
      </div>
      {exerciseOrder.map((name) => {
        const sets = bySets.get(name)!;
        const chips = sets.map(formatSetChip);
        return (
          <div key={name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontSize: 13, padding: '2px 0', gap: 8 }}>
            <span style={{ color: 'var(--text-1)', fontWeight: 500, flexShrink: 0 }}>{name}</span>
            <span style={{ color: 'var(--text-3)', fontSize: 12, textAlign: 'right' }}>{chips.join('  ')}</span>
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
    <div className="card" style={{ marginBottom: 12 }}>
      <button
        style={{ padding: '14px 16px', cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8, width: '100%', background: 'none', border: 'none', textAlign: 'left' }}
        onClick={() => setExpanded(!expanded)}
      >
        <div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>{workout.name}</div>
          <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>
            {workout.date} · {setCount} sets{workout.sleepHours != null && ` · 😴 ${workout.sleepHours}h`}
          </div>
        </div>
        <span style={{ color: 'var(--text-3)', fontSize: 18, marginTop: 2 }}>{expanded ? '▲' : '▼'}</span>
      </button>
      {expanded && (
        <div style={{ padding: '0 16px 14px' }}>
          {workout.notes && (
            <div style={{ fontSize: 12, color: 'var(--text-2)', marginBottom: 8, fontStyle: 'italic' }}>{workout.notes}</div>
          )}
          {workout.blocks.map((b) => <BlockSection key={b.id} block={b} />)}
        </div>
      )}
    </div>
  );
}

const QUICK_TAGS = ['upper', 'lower', 'squat', 'cardio'];

function HistoryContent({ tag }: { tag: string | null }) {
  const data = useLazyLoadQuery<HistoryViewQueryType>(query, { limit: 50, tag });
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
    <div style={{ paddingTop: 16 }}>
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
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
