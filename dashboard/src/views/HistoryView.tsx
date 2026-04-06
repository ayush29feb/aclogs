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

function formatSet(s: Set): string {
  const parts: string[] = [];
  if (s.weightLbs != null && s.reps != null) parts.push(`${s.weightLbs} lbs × ${s.reps}`);
  else if (s.reps != null) parts.push(`${s.reps} reps`);
  else if (s.weightLbs != null) parts.push(`${s.weightLbs} lbs`);
  if (s.rpe != null) parts.push(`@${s.rpe}`);
  if (s.durationSecs != null) parts.push(`${Math.round(s.durationSecs / 60)}min`);
  if (s.distanceM != null) parts.push(`${(s.distanceM / 1000).toFixed(1)}km`);
  if (s.calories != null) parts.push(`${s.calories}cal`);
  if (s.watts != null) parts.push(`${s.watts}W`);
  return parts.join(' · ') || '—';
}

function RoundRow({ round, showRoundLabel }: { round: Round; showRoundLabel: boolean }) {
  return (
    <div style={{ marginBottom: 6 }}>
      {showRoundLabel && (
        <div style={{ fontSize: 11, fontWeight: 600, color: 'var(--text-3)', marginBottom: 2 }}>
          Round {round.round}
        </div>
      )}
      {round.sets.map((s) => (
        <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, padding: '2px 0', color: 'var(--text-2)' }}>
          <span style={{ fontWeight: 500, color: 'var(--text-1)' }}>{s.exerciseName}</span>
          <span>{formatSet(s)}</span>
        </div>
      ))}
    </div>
  );
}

function BlockSection({ block }: { block: Block }) {
  const showRoundLabels = block.rounds.length > 1;
  return (
    <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--border-light)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-1)' }}>{block.name}</span>
        {block.scheme && <span style={{ fontSize: 12, color: 'var(--text-3)' }}>{block.scheme}</span>}
      </div>
      {block.rounds.map((r) => (
        <RoundRow key={r.round} round={r} showRoundLabel={showRoundLabels} />
      ))}
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
          <div style={{ fontWeight: 600, fontSize: 15 }}>{workout.name}</div>
          <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2 }}>
            {workout.date} · {setCount} sets
            {workout.sleepHours != null && ` · 😴 ${workout.sleepHours}h`}
          </div>
          {workout.tags.length > 0 && (
            <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap', marginTop: 6 }}>
              {workout.tags.map((t) => <span key={t} className="tag">{t}</span>)}
            </div>
          )}
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
