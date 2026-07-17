---
name: immich
description: Query the Immich photo library via its REST API (server stats, albums, search assets, recent uploads).
version: 1.0.0
platforms: [linux]
tags: [hermes, services, immich, photos, media]
---

# Immich

Immich photo library runs locally at `http://localhost:<PORT>`.

## Setup (API key)

No key in env yet. Get one from the Immich web UI:
**Account Settings > API Keys > New API Key**. Add it to secrets:

```
echo 'IMMICH_API_KEY=<key>' >> /var/lib/hermes/secrets/services.env
```

Auth header: `x-api-key: $IMMICH_API_KEY`

```bash
set -a; . /var/lib/hermes/secrets/services.env; set +a
B="http://localhost:<PORT>/api"
H="x-api-key: $IMMICH_API_KEY"
```

## Commands

```bash
# Server stats (asset/photo/video counts, usage)
curl -s "$B/server/statistics" -H "$H"

# Server about/version
curl -s "$B/server/about" -H "$H"

# List albums
curl -s "$B/albums" -H "$H" | python3 -c "import json,sys; [print(a['id'], a['albumName'], a.get('assetCount','')) for a in json.load(sys.stdin)]"

# Recent uploads (metadata search, newest first)
curl -s -X POST "$B/search/metadata" -H "$H" -H "Content-Type: application/json" \
  -d '{"order":"desc","size":20}' | python3 -c "import json,sys; [print(a['id'], a.get('originalFileName','')) for a in json.load(sys.stdin)['assets']['items']]"

# Search by date range
curl -s -X POST "$B/search/metadata" -H "$H" -H "Content-Type: application/json" \
  -d '{"takenAfter":"2026-01-01T00:00:00Z","takenBefore":"2026-02-01T00:00:00Z","size":50}'

# Smart/label search (CLIP) — e.g. "beach", "dog"
curl -s -X POST "$B/search/smart" -H "$H" -H "Content-Type: application/json" \
  -d '{"query":"beach","size":20}' | python3 -c "import json,sys; [print(a['id'], a.get('originalFileName','')) for a in json.load(sys.stdin)['assets']['items']]"
```

## Notes

- All commands are local.
- See MEMORY: Immich self-host planned to replace iCloud; server `localhost:<PORT>`.
