---
name: jellyfin
description: Query and control the Jellyfin media server (libraries, search, recently added, playback sessions, system info).
version: 1.0.0
platforms: [linux]
tags: [hermes, media, jellyfin, movies, tv]
---

# Jellyfin

Jellyfin media server runs locally at `http://localhost:<PORT>`.

## Setup (one-time)

No API key in env yet. Get one from the Jellyfin web UI:
**Dashboard > Admin > API Keys > + (add new)**. Then add it to secrets:

```
echo 'JELLYFIN_API_KEY=<key>' >> /var/lib/hermes/secrets/services.env
```

All requests authenticate with the header `X-Emby-Token: $KEY`.

## Read the key

```python
def get_secret(key):
    val = __import__('os').environ.get(key, "")
    if val: return val
    for line in open("/var/lib/hermes/secrets/services.env"):
        if line.strip().startswith(key + "="):
            return line.strip().split("=", 1)[1]
    return ""
```

In bash, source it: `set -a; . /var/lib/hermes/secrets/services.env; set +a; KEY=$JELLYFIN_API_KEY`

## Commands

```bash
KEY=$JELLYFIN_API_KEY

# System info
curl -s "http://localhost:<PORT>/System/Info" -H "X-Emby-Token: $KEY"

# List libraries
curl -s "http://localhost:<PORT>/Library/VirtualFolders" -H "X-Emby-Token: $KEY" | python3 -c "import json,sys; [print(l['Name'], l['CollectionType']) for l in json.load(sys.stdin)]"

# Recently added (last 10)
curl -s "http://localhost:<PORT>/Items/Latest?Limit=10&IncludeItemTypes=Movie,Episode" -H "X-Emby-Token: $KEY" | python3 -c "import json,sys; [print(i.get('SeriesName',''), i['Name'], i.get('ProductionYear','')) for i in json.load(sys.stdin)]"

# Active playback sessions
curl -s "http://localhost:<PORT>/Sessions" -H "X-Emby-Token: $KEY" | python3 -c "import json,sys; [print(s.get('UserName','?'), '-', s.get('NowPlayingItem',{}).get('Name','idle')) for s in json.load(sys.stdin)]"

# Search (replace QUERY)
curl -s "http://localhost:<PORT>/Items?SearchTerm=QUERY&IncludeItemTypes=Movie,Series&Recursive=true&Limit=10" -H "X-Emby-Token: $KEY" | python3 -c "import json,sys; [print(i['Name'], i.get('ProductionYear',''), i['Type']) for i in json.load(sys.stdin).get('Items',[])]"
```

## Notes

- Previous `jellyfin-users` skill had the wrong IP (pointed at Home Assistant). Jellyfin is `localhost:<PORT>`.
- All commands are local — Hermes runs on the same host.
