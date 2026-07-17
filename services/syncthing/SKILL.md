---
name: syncthing
description: Manage Syncthing file sync — check folder status, sync progress, device connections. GUI at localhost:<PORT>. API key in config.xml.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [syncthing, sync, files, obsidian, documents]
---

# Syncthing

GUI at `http://localhost:<PORT>`. REST API needs the API key from the config file.

```bash
# Get API key from config
ST_KEY=$(python3 -c "import xml.etree.ElementTree as ET; t=ET.parse('/var/lib/syncthing/.config/syncthing/config.xml'); print(t.find('.//apikey').text)")
```

## System Status

```bash
curl -s http://localhost:<PORT>/rest/system/status -H "X-API-Key: $ST_KEY" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('ID:', d['myID'][:8])"
```

## List Folders

```bash
curl -s http://localhost:<PORT>/rest/config/folders -H "X-API-Key: $ST_KEY" \
  | python3 -c "import json,sys; [print(f['id'], '->', f['path']) for f in json.load(sys.stdin)]"
```

Known folders:
- Obsidian vault: `/srv/obsidian/`
- Documents (iCloud mirror): `/srv/documents/`

## Folder Sync Status

```bash
# Replace FOLDER_ID with the folder ID from the list above
curl -s "http://localhost:<PORT>/rest/db/status?folder=FOLDER_ID" -H "X-API-Key: $ST_KEY" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('State:', d['state'], ' NeedBytes:', d.get('needBytes',0))"
```

## Connected Devices

```bash
curl -s http://localhost:<PORT>/rest/system/connections -H "X-API-Key: $ST_KEY" \
  | python3 -c "
import json,sys; d=json.load(sys.stdin)
for dev_id, info in d.get('connections', {}).items():
    print(dev_id[:8], 'connected:', info.get('connected'), ' in:', info.get('inBytesTotal',0)//1024//1024, 'MB')
"
```

## Force Rescan a Folder

```bash
curl -s -X POST "http://localhost:<PORT>/rest/db/scan?folder=FOLDER_ID" -H "X-API-Key: $ST_KEY"
```

## Pending Devices (new pair requests)

```bash
curl -s http://localhost:<PORT>/rest/cluster/pending/devices -H "X-API-Key: $ST_KEY" \
  | python3 -c "import json,sys; [print(k[:8], v.get('name','?')) for k,v in json.load(sys.stdin).items()]"
```

## Rules

1. Device pairing is done via the GUI at localhost:<PORT> — do not automate this
2. Write to /srv/obsidian/ and changes propagate to Mac/iPhone/Boox automatically
3. /srv/documents/ is iCloud-mirrored — ask before writing anything there
4. If sync is stuck, check folder status for errors before restarting
5. Restart: `sudo systemctl restart syncthing`
