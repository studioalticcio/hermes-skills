---
name: grocery
description: Open the Grocery compare Telegram Mini App. Use when the user types /grocery or asks to open Grocery compare.
version: 1.0.0
metadata:
  hermes:
    tags: [miniapp, telegram, alticcio]
---

# /grocery

Compares Auchan (live) vs Leclerc/Picard prices for the grocery watchlist.

When invoked, run exactly this and then reply with only the word "🛒" (no other text):

```bash
~/.hermes/scripts/send-miniapp.sh grocery
```

This posts a Telegram button that opens the Mini App in-app (needs Tailscale on).
