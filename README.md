# AC Logs

A personal workout tracking dashboard for Athletic Clubs members. View your training history, personal records, and progress — from your phone.

For architecture, schema, and technical details see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## How it works

AC Logs runs on your Mac. You view it from your phone via Tailscale.

```
Your phone
  └── Safari / Chrome ───Tailscale──► Dashboard (localhost:47323)
                                           └── GraphQL API (localhost:47322)
                                                    └── ~/.aclogs/data/gym.db
```

---

## Prerequisites

- Node.js 20+
- [Tailscale](https://tailscale.com) installed and connected on both Mac and phone

---

## Install

```bash
claude plugin install ayush29feb/aclogs
```

Then in any Claude Code session:

> "Set up AC Logs for the first time."

Claude will install all dependencies, build the server, generate types, and start both servers.

---

## Dashboard

| View | What you see |
|---|---|
| **History** | Every workout session, expandable with all blocks and sets. Filter by tag (upper/lower/APS/MPA etc.) with multi-select intersection. |
| **PRs** | Best lifts per rep count (1RM / 3RM / 5RM / 8RM) for every exercise. Click any row to see a weight-over-time sparkline. |

The date range picker in the top-right filters both views simultaneously.

---

## Daily use

With servers running and Tailscale connected, open `http://<tailscale-ip>:47323` in your phone's browser. Bookmark it.

Say "start the servers" in Claude Code any time to restart.
