---
name: ntfy
description: Send push notifications to the user's phone via the local ntfy server (titles, priority, tags, actions, scheduling).
version: 1.0.0
platforms: [linux]
tags: [hermes, services, ntfy, notifications, push]
---

# ntfy

ntfy push notification server runs locally at `http://localhost:<PORT>`.
the user's phone is subscribed. No auth needed for local publish.

**Default topic for Hermes -> the user notifications: `alticcio`** (unless told otherwise).

This is the primary way Hermes pings the user: long task done, something needs
attention, a confirmation request, etc.

## Send a notification

```bash
curl -s http://localhost:<PORT>/alticcio \
  -H "Title: My Title" \
  -H "Priority: default" \
  -H "Tags: white_check_mark" \
  -d "Message body here"
```

- **Priority**: `min`, `low`, `default`, `high`, `urgent` (5 = urgent).
- **Tags**: comma-separated emoji shortcodes — e.g. `white_check_mark`, `warning`,
  `rotating_light`, `tada`, `floppy_disk`. First tags that match emoji render as icons.

## Action buttons

```bash
curl -s http://localhost:<PORT>/alticcio \
  -H "Title: Confirm?" \
  -H "Actions: confirm, Yes, http://...; deny, No, http://..." \
  -d "Do you want to proceed?"
```

Action format: `<action>, <label>, <url>` separated by `;`. Use `view` to open a
URL, or `http` to fire a request when the button is tapped.

## Schedule (delayed delivery)

```bash
# Deliver in 30 minutes
curl -s http://localhost:<PORT>/alticcio \
  -H "Title: Reminder" -H "Delay: 30min" \
  -d "Check the oven"

# Deliver at a natural-language / unix time
curl -s http://localhost:<PORT>/alticcio -H "Delay: tomorrow, 9am" -d "Standup"
```

`Delay` accepts `30s`, `15min`, `2h`, `tomorrow, 10am`, or a unix timestamp.

## Use from inside other Hermes tasks

At the end of a long-running task, notify the user:

```bash
curl -s http://localhost:<PORT>/alticcio \
  -H "Title: Task complete" -H "Tags: white_check_mark" \
  -d "Backup finished: 412 GB in 38 min."
```

Use `Priority: urgent` + `Tags: rotating_light` when something needs immediate attention.

## Notes

- All commands are local. Publishing is a plain POST/PUT to `/<topic>`.
