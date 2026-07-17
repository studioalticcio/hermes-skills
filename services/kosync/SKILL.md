---
name: kosync
description: KOSync server for the user's Boox e-reader (KOReader reading progress sync). Runs at localhost:<PORT>. Lightweight REST API.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [kosync, koreader, boox, ereader, reading, sync]
---

# KOSync

KOReader reading-progress sync server at `localhost:<PORT>`. Used by the user's Boox e-reader to sync reading positions across devices.

## Check Server Status

```bash
curl -s http://localhost:<PORT>/healthcheck
# Should return: {"state":"OK"}
```

## Service Management

```bash
# Check status
systemctl status podman-kosync.service

# Restart if needed
sudo systemctl restart podman-kosync.service

# Logs
journalctl -u podman-kosync.service -n 50 --no-pager
```

## Reading Progress (API)

KOSync uses Basic Auth with the credentials set in KOReader on the Boox.

```bash
# Check progress for a document (by MD5 hash of file)
curl -s -u "USER:PASS" http://localhost:<PORT>/syncs/progress/DOCUMENT_MD5

# Update progress (done by KOReader automatically)
curl -s -X PUT -u "USER:PASS" http://localhost:<PORT>/syncs/progress/DOCUMENT_MD5 \
  -H "Content-Type: application/json" \
  -d '{"document":"DOCUMENT_MD5","progress":"0.5","percentage":50,"device":"boox","device_id":"..."}'
```

## Rules

1. KOSync runs passively — Boox KOReader syncs automatically; no manual intervention normally needed
2. Only intervene if the user reports reading progress not syncing across devices
3. Credentials are configured in KOReader on the Boox device itself
4. Service data: check /var/lib/kosync/ or podman volume for user/progress storage
