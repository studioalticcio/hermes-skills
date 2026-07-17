---
name: transmission
description: Control Transmission BitTorrent client. Add torrents, check download progress, manage queue. RPC on localhost:<PORT>.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [transmission, torrent, downloads, BitTorrent]
---

# Transmission

RPC at `http://localhost:<PORT>/transmission/rpc`. Requires `X-Transmission-Session-Id` header (get it by making a request that 409s, then use the returned header value).

Download paths: `/srv/media/.downloads` (complete), `/srv/media/.incomplete` (in progress)

---

## Helper (reusable session-id pattern)

```python
import urllib.request, urllib.error, json

RPC = "http://localhost:<PORT>/transmission/rpc"

def tr_request(method, arguments=None):
    """Make a Transmission RPC call, handling session-id automatically."""
    payload = json.dumps({"method": method, "arguments": arguments or {}}).encode()
    session_id = ""
    for _ in range(2):
        req = urllib.request.Request(RPC, data=payload,
            headers={"Content-Type": "application/json",
                     "X-Transmission-Session-Id": session_id})
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 409:
                session_id = e.headers.get("X-Transmission-Session-Id", "")
            else:
                raise
    raise Exception("Could not get Transmission session-id")
```

---

## List Active Downloads

```python
result = tr_request("torrent-get", {"fields": ["id", "name", "status", "percentDone", "rateDownload", "eta", "totalSize"]})
torrents = result["arguments"]["torrents"]

STATUS = {0:"stopped", 1:"check-wait", 2:"checking", 3:"dl-wait", 4:"downloading", 5:"seed-wait", 6:"seeding"}
for t in sorted(torrents, key=lambda x: x["percentDone"]):
    pct = t["percentDone"] * 100
    rate = t["rateDownload"] / 1024 / 1024
    status = STATUS.get(t["status"], "?")
    size_gb = t["totalSize"] / 1024**3
    eta = f"{t[eta]//3600}h{(t[eta]%3600)//60}m" if t["eta"] > 0 else "∞"
    print(f"[{t[id]}] {t[name][:50]}")
    print(f"     {pct:.1f}%  {rate:.2f}MB/s  ETA:{eta}  {size_gb:.2f}GB  [{status}]")
```

---

## Add a Torrent by URL/Magnet

```python
MAGNET_OR_URL = "magnet:?xt=urn:btih:..."
result = tr_request("torrent-add", {
    "filename": MAGNET_OR_URL,
    "download-dir": "/srv/media/.downloads"
})
print(result["arguments"].get("torrent-added", {}).get("name", "Added"))
```

---

## Add a Torrent File

```python
import base64

with open("/tmp/file.torrent", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

result = tr_request("torrent-add", {
    "metainfo": encoded,
    "download-dir": "/srv/media/.downloads"
})
print(result)
```

---

## Pause / Resume / Remove

```python
# Pause (by id list)
tr_request("torrent-stop", {"ids": [TORRENT_ID]})

# Resume
tr_request("torrent-start", {"ids": [TORRENT_ID]})

# Remove (keep files)
tr_request("torrent-remove", {"ids": [TORRENT_ID], "delete-local-data": False})

# Remove and delete files
tr_request("torrent-remove", {"ids": [TORRENT_ID], "delete-local-data": True})
```

---

## Session Stats

```python
stats = tr_request("session-stats")["arguments"]
print(f"Active: {stats[activeTorrentCount]}  Total: {stats[torrentCount]}")
print(f"Down: {stats[downloadSpeed]/1024/1024:.2f} MB/s  Up: {stats[uploadSpeed]/1024/1024:.2f} MB/s")
```

---

## Rules

1. ALWAYS confirm with user before adding a torrent — show name and size
2. Confirm before deleting local data
3. *arr stack manages its own torrents automatically — only intervene for manual requests
4. Downloads land in `/srv/media/.downloads` — *arr moves them to final locations
