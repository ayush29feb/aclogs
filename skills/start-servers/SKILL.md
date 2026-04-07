---
name: start-servers
description: Use when the user asks to start AC Logs, start the servers, or open the dashboard
---

# Start AC Logs Servers

Never ask the user to run commands — always ask permission and run yourself.

Ask: "Can I start the AC Logs servers?"

Once confirmed:

```bash
source ~/.aclogs/config
```

Check for existing processes:
```bash
lsof -ti :47322 -ti :47323
```

If PIDs are returned, ask: "There are already processes running on AC Logs' ports — likely a previous session. Can I kill them and start fresh?" After confirmation:
```bash
lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
```

Start both servers:
```bash
cd "$ACLOGS_ROOT/server" && npm start &> /tmp/aclogs-server.log &
cd "$ACLOGS_ROOT/dashboard" && npm run dev -- --host &> /tmp/aclogs-dashboard.log &
sleep 3 && lsof -i :47322 -i :47323 | grep LISTEN
```

Tell the user: **Both servers are running.**
- GraphQL server: `http://localhost:47322/graphql`
- Dashboard: `http://localhost:47323` (also accessible on phone via Tailscale — use the aclogs:remote-control skill for the phone URL)

## View logs

```bash
tail -f /tmp/aclogs-server.log
tail -f /tmp/aclogs-dashboard.log
```
