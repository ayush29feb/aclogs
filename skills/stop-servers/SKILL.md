---
name: stop-servers
description: Use when the user asks to stop AC Logs or shut down the servers
---

# Stop AC Logs Servers

Ask: "Can I stop the AC Logs servers?"

Once confirmed:
```bash
lsof -ti :47322 -ti :47323 | xargs kill -9 2>/dev/null || true
```

Verify both ports are clear:
```bash
lsof -i :47322 -i :47323 | grep LISTEN || echo "Servers stopped."
```

Tell the user: **Servers stopped.**
