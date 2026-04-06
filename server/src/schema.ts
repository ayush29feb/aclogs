export const typeDefs = /* GraphQL */ `
  type Query {
    workouts(limit: Int, tag: String): [Workout!]!
    workout(id: Int!): Workout
    exercises: [Exercise!]!
    exercise(name: String!): Exercise
    progress(exerciseName: String!, related: Boolean): Progress!
  }

  type Workout {
    id: Int!
    name: String!
    date: String!
    sleepHours: Float
    tags: [String!]!
    notes: String
    blocks: [Block!]!
  }

  type Block {
    id: Int!
    name: String!
    order: Int!
    scheme: String
    rounds: [Round!]!
  }

  type Round {
    round: Int!
    sets: [Set!]!
  }

  type Set {
    id: Int!
    exerciseId: Int!
    exerciseName: String!
    round: Int!
    weightLbs: Float
    reps: Int
    rpe: Float
    durationSecs: Int
    distanceM: Float
    calories: Float
    watts: Float
    notes: String
    loggedAt: String!
  }

  type Exercise {
    id: Int!
    name: String!
    muscleGroup: String
    notes: String
    relatedExercises: [Exercise!]!
  }

  type Progress {
    exerciseName: String!
    prs: [RepsPr!]!
    history: [HistoryEntry!]!
  }

  type RepsPr {
    reps: Int!
    weightLbs: Float!
    date: String!
  }

  type HistoryEntry {
    date: String!
    exerciseName: String!
    weightLbs: Float
    reps: Int
    rpe: Float
    watts: Float
    calories: Float
    durationSecs: Int
  }
`;
