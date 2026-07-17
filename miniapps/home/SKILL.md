---
name: home
description: Open the Home glance Telegram Mini App. Use when the user types /home or asks to open Home glance.
version: 1.0.0
metadata:
  hermes:
    tags: [miniapp, telegram, alticcio]
---

# /home

Shows presence, weather, home power and device battery levels from Home Assistant.

When invoked, run exactly this and then reply with only the word "🏠" (no other text):

```bash
~/.hermes/scripts/send-miniapp.sh home
```

This posts a Telegram button that opens the Mini App in-app (needs Tailscale on).
