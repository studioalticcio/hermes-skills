---
name: mobiliteit
description: "Use when querying Luxembourg public transport via mobiliteit.lu / cdt.hafas.de: stop search, departures, route planning, and HAFAS API troubleshooting."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [luxembourg, transit, hafas, mobiliteit, transport, cli]
    related_skills: [maps]
---

# Mobiliteit.lu

## Overview

the user has a local `mobiliteit` CLI at `~/.local/bin/mobiliteit`. It talks directly to the HAFAS backend used by mobiliteit.lu:

- Web app: `https://cdt.hafas.de/`
- Config: `https://cdt.hafas.de/config/webapp.config.json`
- JSON gate endpoint: `https://cdt.hafas.de/gate`

Use this skill for Luxembourg public-transport queries where current stop, departure, or route data matters.

## Linked Files

- `references/hafas-gate.md` — condensed API notes, tested payloads, response quirks, and the `/opendata/apiserver` auth caveat.
- `scripts/mobiliteit.py` — packaged copy of the CLI. If `~/.local/bin/mobiliteit` is missing or stale, copy this script there and `chmod +x` it.

## Quick Commands

```bash
mobiliteit search Hamilius --max 5
mobiliteit departures Hamilius --max 10
mobiliteit departures Hamilius --time 18:00 --max 5
mobiliteit route Hamilius 'Kirchberg, Luxexpo' --time 12:00 --max 3
mobiliteit route 'Luxembourg, Gare Centrale' '<your home address>' --time 18:30 --json
```

The CLI accepts stop names, numeric `extId`s, or full HAFAS `lid`s for stops.

## CLI Location

```bash
~/.local/bin/mobiliteit
```

If PATH is uncertain, call it explicitly:

```bash
/home/user/.local/bin/mobiliteit search Hamilius
```

## Commands

### Search stops

```bash
mobiliteit search QUERY [--max N] [--json]
```

Example verified output:

```txt
1. Hamilius (Bus)  [S] extId=200405020 49.611502,6.125978
   lid=A=1@O=Hamilius (Bus)@X=6125978@Y=49611502@U=82@L=200405020@p=1782988547@
2. Hamilius-Centre (Tram)  [S] extId=200405057 49.611098,6.126140
```

### Departures / arrivals

```bash
mobiliteit departures STOP [--date YYYY-MM-DD] [--time HH:MM] [--max N] [--json]
mobiliteit departures STOP --arrivals
```

Example verified output:

```txt
Departures for Hamilius (Bus)
12:00 Bus 14       → Cents, Waassertuerm
12:00 Bus 8        → Bertrange, Waassertuerm
12:01 Bus 14       → Cessange, Boy Konen
```

### Route planning

```bash
mobiliteit route ORIGIN DESTINATION [--date YYYY-MM-DD] [--time HH:MM] [--max N] [--json]
```

Example verified output:

```txt
#1 12:02 → 12:19  001700
   - Bus 21: Hamilius (Bus) → Centre, Fondation Pescatore
   - WALK: Centre, Fondation Pescatore → Limpertsberg, Theater (Bus)
   - Bus 201: Limpertsberg, Theater (Bus) → Kirchberg, Gare routière Luxexpo
#2 12:02 → 12:21  001900
   - Bus 6: Hamilius (Bus) → Kirchberg, Gare routière Luxexpo
```

`dur` is raw HAFAS duration `HHMMSS` (`001700` = 17 min).

## API Notes

The working web app credentials are public in the mobiliteit HAFAS config:

```txt
gate:   https://cdt.hafas.de/gate
aid:    SkC81GuwuzL4e0
client: id=MMILUX type=WEB name=webapp l=vs_webapp
ver:    1.77
```

Basic `/gate` envelope:

```json
{
  "lang": "eng",
  "ver": "1.77",
  "auth": { "type": "AID", "aid": "SkC81GuwuzL4e0" },
  "client": { "id": "MMILUX", "type": "WEB", "name": "webapp", "l": "vs_webapp" },
  "svcReqL": [
    { "meth": "LocMatch", "req": { "input": { "field": "S", "loc": { "name": "Hamilius", "type": "S" } } } }
  ]
}
```

Known methods:

| Need | Method | CLI |
|---|---|---|
| Stop search | `LocMatch` | `mobiliteit search` |
| Departures / arrivals | `StationBoard` | `mobiliteit departures` |
| Route planning | `TripSearch` | `mobiliteit route` |

## OpenData Endpoint Caveat

`https://cdt.hafas.de/opendata/apiserver/` exists and advertises WADL endpoints such as `departureBoard` and `location.nearbystops`, but the web app AID is not authorised there. A tested call returned:

```json
{
  "errorCode": "API_AUTH",
  "errorText": "access denied for SkC81GuwuzL4e0 on location.nearbystops"
}
```

So default to `/gate`. Only use `/opendata/apiserver` if the user obtains a separate official `accessId`.

## Common Pitfalls

1. **Treating `err: "OK"` as failure.** HAFAS responses often carry `err: "OK"` at top level and per-service level. Only non-OK `err` is failure.
2. **Using `/opendata/apiserver` with the web AID.** It 401s. Use `/gate`.
3. **Route time field names differ.** Top-level connections use `dep.dTimeS` / `dep.dTimeR` and `arr.aTimeS` / `arr.aTimeR`, not plain `timeS`.
4. **Huge JSON.** Search/board responses include `common.prodL` and can be enormous. Use the CLI's human output unless raw data is needed.

## Verification Checklist

- [ ] Run `mobiliteit search Hamilius --max 1` and confirm a stop is returned.
- [ ] Run `mobiliteit departures Hamilius --max 3` and confirm current departures render.
- [ ] For route changes, run `mobiliteit route Hamilius 'Kirchberg, Luxexpo' --time 12:00 --max 1` and confirm departure/arrival times are sane.
- [ ] If HAFAS changes credentials, re-read `https://cdt.hafas.de/config/webapp.config.json` and update the CLI default AID/client if needed.
