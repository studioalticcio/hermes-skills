---
name: veloh
description: Open the vel'OH! & Jims Telegram Mini App. Use when the user types /veloh or asks to open vel'OH! & Jims.
version: 1.0.0
metadata:
  hermes:
    tags: [miniapp, telegram, alticcio]
---

# /veloh

Shows live vel'OH! bikes near home on a map plus the Jims Infinity crowd level.

When invoked, run exactly this and then reply with only the word "🚲" (no other text):

```bash
~/.hermes/scripts/send-miniapp.sh veloh
```

This posts a Telegram button that opens the Mini App in-app (needs Tailscale on).
