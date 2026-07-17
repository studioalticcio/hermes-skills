---
name: apps
description: Open the Alticcio apps Telegram Mini App. Use when the user types /apps or asks to open Alticcio apps.
version: 1.0.0
metadata:
  hermes:
    tags: [miniapp, telegram, alticcio]
---

# /apps

Opens the hub linking every Alticcio Mini App.

When invoked, run exactly this and then reply with only the word "📲" (no other text):

```bash
~/.hermes/scripts/send-miniapp.sh apps
```

This posts a Telegram button that opens the Mini App in-app (needs Tailscale on).
