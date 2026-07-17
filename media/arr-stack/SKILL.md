---
name: arr-stack
description: Manage the *arr media stack — Sonarr (TV), Radarr (movies), Lidarr (music), Prowlarr (indexers), Bazarr (subtitles). All run locally. API keys in services.env.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [sonarr, radarr, lidarr, prowlarr, bazarr, media, TV, movies, music]
---

# *arr Media Stack

All services run locally. Secrets in `/var/lib/hermes/secrets/services.env`.

| Service  | Port | Env key          | Purpose         |
|----------|------|------------------|-----------------|
| Sonarr   | 8989 | SONARR_API_KEY   | TV shows        |
| Radarr   | 7878 | RADARR_API_KEY   | Movies          |
| Lidarr   | 8686 | LIDARR_API_KEY   | Music           |
| Prowlarr | 9696 | PROWLARR_API_KEY | Indexer manager |
| Bazarr   | 6767 | BAZARR_API_KEY   | Subtitles       |

Media paths: `/srv/media/tvshows`, `/srv/media/movies`, `/srv/media/music`

---

## Sonarr — TV Shows

```bash
KEY=$SONARR_API_KEY

# Search for a show
curl -s "http://localhost:<PORT>/api/v3/series/lookup?term=SHOW+NAME" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; [print(r['tvdbId'], r['title'], r.get('year','')) for r in json.load(sys.stdin)[:8]]"

# Add a show (fill TVDB_ID and TITLE from search result)
curl -s -X POST "http://localhost:<PORT>/api/v3/series" \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"tvdbId":TVDB_ID,"title":"TITLE","qualityProfileId":1,"rootFolderPath":"/srv/media/tvshows","monitored":true,"addOptions":{"searchForMissingEpisodes":true}}'

# List monitored shows
curl -s "http://localhost:<PORT>/api/v3/series" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; [print(s['title'], '-', s.get('episodeCount',0), 'eps') for s in sorted(json.load(sys.stdin), key=lambda x: x['title'])]"

# Check download queue
curl -s "http://localhost:<PORT>/api/v3/queue" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['title'][:60], r.get('status','')) for r in d.get('records',[])]"

# Force search missing episodes
curl -s -X POST "http://localhost:<PORT>/api/v3/command" \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"name":"MissingEpisodeSearch"}'
```

---

## Radarr — Movies

```bash
KEY=$RADARR_API_KEY

# Search for a movie
curl -s "http://localhost:<PORT>/api/v3/movie/lookup?term=MOVIE+NAME" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; [print(r['tmdbId'], r['title'], r.get('year','')) for r in json.load(sys.stdin)[:8]]"

# Add a movie (fill TMDB_ID and TITLE)
curl -s -X POST "http://localhost:<PORT>/api/v3/movie" \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"tmdbId":TMDB_ID,"title":"TITLE","qualityProfileId":1,"rootFolderPath":"/srv/media/movies","monitored":true,"addOptions":{"searchForMovie":true}}'

# List all movies
curl -s "http://localhost:<PORT>/api/v3/movie" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; [print(m['title'], m.get('year','')) for m in sorted(json.load(sys.stdin), key=lambda x: x['title'])[:30]]"

# Check download queue
curl -s "http://localhost:<PORT>/api/v3/queue" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(r['title'][:60], r.get('status','')) for r in d.get('records',[])]"
```

---

## Lidarr — Music

```bash
KEY=$LIDARR_API_KEY

# Search for an artist
curl -s "http://localhost:<PORT>/api/v1/artist/lookup?term=ARTIST+NAME" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; [print(r.get('foreignArtistId',''), r['artistName']) for r in json.load(sys.stdin)[:8]]"

# Add an artist (fill FOREIGN_ID and ARTIST_NAME from lookup)
curl -s -X POST "http://localhost:<PORT>/api/v1/artist" \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"foreignArtistId":"FOREIGN_ID","artistName":"ARTIST_NAME","qualityProfileId":1,"metadataProfileId":1,"rootFolderPath":"/srv/media/music","monitored":true,"addOptions":{"searchForMissingAlbums":true}}'

# List all tracked artists
curl -s "http://localhost:<PORT>/api/v1/artist" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; [print(a['artistName']) for a in sorted(json.load(sys.stdin), key=lambda x: x['artistName'])]"
```

---

## Prowlarr — Indexers

```bash
KEY=$PROWLARR_API_KEY

# List indexers and status
curl -s "http://localhost:<PORT>/api/v1/indexer" -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; [print(i['name'], '- enabled:', i.get('enable', False)) for i in json.load(sys.stdin)]"

# Trigger indexer test
curl -s -X POST "http://localhost:<PORT>/api/v1/indexer/test" -H "X-Api-Key: $KEY" -H "Content-Type: application/json" -d '{}'
```

---

## Bazarr — Subtitles

```bash
KEY=$BAZARR_API_KEY

# Episodes missing subtitles
curl -s "http://localhost:<PORT>/api/episodes/wanted?start=0&length=20" \
  -H "X-Api-Key: $KEY" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(e.get('seriesTitle','?'), '-', e.get('title','?')) for e in d.get('data',[])]"
```

---

## Rules

1. ALWAYS confirm with user before adding content — show title, year, and what will be searched.
2. Lidarr “discography” requests are bulk downloads: lookup the artist first, show the likely MusicBrainz `foreignArtistId` plus disambiguation, and get explicit confirmation before adding/searching missing albums.
3. Use quality profile ID 1 (default) unless user specifies otherwise.
4. After adding, check the queue to confirm a download started.
5. If downloads stall, check Prowlarr indexer status first.
6. Bazarr runs automatically — only intervene if subtitles are missing after 24h.
