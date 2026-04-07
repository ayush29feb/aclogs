---
name: remote-control
description: Use when the user asks to access the dashboard on their phone, set up remote access, or get the Tailscale URL
---

# Remote Control — Dashboard on Phone

AC Logs can be opened on your phone over Tailscale, a free tool that creates a private connection between your Mac and phone.

## If Tailscale is not installed

Tell the user:
> **On your Mac:** Go to tailscale.com/download, install, launch, and sign in.
> **On your phone:** Install Tailscale from the App Store or Play Store and sign in with the same account.
> Once both devices show as connected in the Tailscale app, let me know.

## Once Tailscale is running on both devices

Get the Mac's Tailscale IP:
```bash
tailscale ip -4
```

Tell the user: open `http://<ip>:47323` in your phone's browser and bookmark it.

Make sure the dashboard server is running with `--host` (the aclogs:start-servers skill does this automatically).
