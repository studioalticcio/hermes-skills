---
name: navidrome
description: Control the Navidrome music server via the Subsonic API (ping, artists, albums, playlists, now playing).
version: 1.0.0
platforms: [linux]
tags: [hermes, media, navidrome, music, subsonic]
---

# Navidrome

Navidrome music server runs locally at `http://localhost:<PORT>`. It exposes the
**Subsonic API** under `/rest/`.

## Setup (credentials)

No credentials in env — they live in Navidrome's own DB. Default admin user is
typically `admin`. To find or reset the password, inspect the SQLite DB:

```bash
ls /var/lib/navidrome/
sqlite3 /var/lib/navidrome/navidrome.db "SELECT user_name FROM user;"
```

Once you know the user/password, add them to secrets:

```
echo 'NAVIDROME_USER=admin'    >> /var/lib/hermes/secrets/services.env
echo 'NAVIDROME_PASS=<pass>'   >> /var/lib/hermes/secrets/services.env
```

Source: `set -a; . /var/lib/hermes/secrets/services.env; set +a`

## Auth params

Every Subsonic call needs these query params:
`u=$NAVIDROME_USER&p=$NAVIDROME_PASS&v=1.16.1&c=hermes&f=json`

```bash
AUTH="u=$NAVIDROME_USER&p=$NAVIDROME_PASS&v=1.16.1&c=hermes&f=json"
B="http://localhost:<PORT>/rest"
```

## Commands

```bash
# Ping (test connection)
curl -s "$B/ping?$AUTH"

# All artists
curl -s "$B/getArtists?$AUTH" | python3 -c "import json,sys; d=json.load(sys.stdin)['subsonic-response']['artists']['index']; [print(a['name']) for idx in d for a in idx.get('artist',[])]"

# Albums by artist (need artist id from getArtists)
curl -s "$B/getArtist?id=ARTIST_ID&$AUTH" | python3 -c "import json,sys; [print(a['name'], a.get('year','')) for a in json.load(sys.stdin)['subsonic-response']['artist'].get('album',[])]"

# Now playing
curl -s "$B/getNowPlaying?$AUTH" | python3 -c "import json,sys; e=json.load(sys.stdin)['subsonic-response'].get('nowPlaying',{}).get('entry',[]); [print(x.get('username'),'-',x.get('artist'),'-',x.get('title')) for x in e]"

# Create playlist
curl -s "$B/createPlaylist?name=NAME&$AUTH"

# Delete playlist (need playlist id)
curl -s "$B/deletePlaylist?id=PLAYLIST_ID&$AUTH"

# List playlists
curl -s "$B/getPlaylists?$AUTH" | python3 -c "import json,sys; [print(p['id'], p['name']) for p in json.load(sys.stdin)['subsonic-response']['playlists'].get('playlist',[])]"
```

## Notes

- `p=` can use plaintext or the `enc:<hex>` form. Plaintext is fine over localhost.
- All commands are local.
