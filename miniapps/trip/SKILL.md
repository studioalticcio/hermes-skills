---
name: trip
description: Open the Bike or bus Telegram Mini App. Use when the user types /trip or asks to open Bike or bus.
version: 1.0.0
metadata:
  hermes:
    tags: [miniapp, telegram, alticcio]
---

# /trip

Opens the door-to-door trip planner comparing a vel'OH! ride vs the next bus.

When invoked, run exactly this and then reply with only the word "🧭" (no other text):

```bash
~/.hermes/scripts/send-miniapp.sh trip
```

This posts a Telegram button that opens the Mini App in-app (needs Tailscale on).
