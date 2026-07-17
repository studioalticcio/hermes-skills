---
name: miniflux
description: Manage the Miniflux RSS reader via its REST API (feeds, unread entries, mark read, add feeds).
version: 1.0.0
platforms: [linux]
tags: [hermes, services, miniflux, rss, feeds]
---

# Miniflux

Miniflux RSS reader runs locally at `http://localhost:<PORT>`.

## Setup (API key)

No key in env. Generate one in the Miniflux UI:
**Settings > API Keys > Create a new API key**. Add it to secrets:

```
echo 'MINIFLUX_API_KEY=<key>' >> /var/lib/hermes/secrets/services.env
```

Auth header: `X-Auth-Token: $MINIFLUX_API_KEY`

```bash
set -a; . /var/lib/hermes/secrets/services.env; set +a
B="http://localhost:<PORT>/v1"
H="X-Auth-Token: $MINIFLUX_API_KEY"
```

## Commands

```bash
# List feeds
curl -s "$B/feeds" -H "$H" | python3 -c "import json,sys; [print(f['id'], f['title']) for f in json.load(sys.stdin)]"

# List unread entries (newest first, limit 20)
curl -s "$B/entries?status=unread&direction=desc&limit=20" -H "$H" | python3 -c "import json,sys; [print(e['id'], e['title']) for e in json.load(sys.stdin)['entries']]"

# Entries for a specific feed
curl -s "$B/feeds/FEED_ID/entries?status=unread" -H "$H" | python3 -c "import json,sys; [print(e['id'], e['title']) for e in json.load(sys.stdin)['entries']]"

# Mark entries as read (entry ids in body)
curl -s -X PUT "$B/entries" -H "$H" -H "Content-Type: application/json" \
  -d '{"entry_ids":[123,456],"status":"read"}'

# Add a feed (need a category id; get with GET /categories)
curl -s -X POST "$B/feeds" -H "$H" -H "Content-Type: application/json" \
  -d '{"feed_url":"https://example.com/rss.xml","category_id":1}'

# List categories
curl -s "$B/categories" -H "$H" | python3 -c "import json,sys; [print(c['id'], c['title']) for c in json.load(sys.stdin)]"
```

## Notes

- All commands are local.
- `me` endpoint (`GET /v1/me`) is a quick auth test.
