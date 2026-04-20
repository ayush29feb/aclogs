# AC Logs

AC Logs is a self-hosted workout tracker for Athletic Clubs members. It runs a GraphQL server (port 47322) and a React dashboard (port 47323).

When the user asks about workouts, lifting data, or server management, use the AC Logs skills:

- **aclogs:setup** — first-time setup or re-setup on a new machine
- **aclogs:start-servers** — start the GraphQL server and dashboard
- **aclogs:stop-servers** — stop the servers
- **aclogs:import-workouts** — wipe and re-import workout data from markdown files
- **aclogs:remote-control** — set up Tailscale and get the phone URL

Data lives at `~/.aclogs/data/gym.db`. Plugin root is in `~/.aclogs/config`.
