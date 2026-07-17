---
name: public-transport-apis
description: "Discover and use public transport APIs, especially HAFAS-backed journey planners and departure boards."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [public-transport, transit, hafas, journey-planner, departures, mobiliteit, luxembourg]
    category: productivity
---

# Public Transport APIs

Use this when the user asks to investigate or use a public transport website/app API: journey planning, stop search, departures, disruptions, GTFS/HAFAS, or building a small transit CLI.

## Approach

1. **Find the actual app backend first.** Public websites often embed a vendor app (`HAFAS`, `Mentz`, `Navitia`, `OpenTripPlanner`) rather than documenting their useful API.
2. Inspect page HTML/config JS/JSON for:
   - gateway/base URLs (`/gate`, `/mgate`, `/api`, `/journey`, `/departureBoard`)
   - auth/access IDs (`aid`, `accessId`, client IDs)
   - client envelope fields (`client.id`, `type`, version, language)
3. Prefer reproducible stdlib probes (`urllib.request`) before adding dependencies.
4. Verify at least one harmless read call end-to-end: stop search, nearby stops, or departure board.
5. Report which endpoints are tested vs inferred. Transit APIs often expose multiple surfaces with different auth rights.

## HAFAS pattern

Many European transport apps use HAFAS. Two common surfaces:

- `/gate` or `/mgate`: web/mobile app JSON gateway. Usually POST JSON with an auth envelope and `svcReqL` service requests.
- `/opendata/apiserver/*`: documented REST/WADL endpoints. May require a separate official `accessId`; do not assume the web app `aid` works there.

Common HAFAS methods:

| Need | Likely method |
|---|---|
| Stop/address/POI search | `LocMatch` |
| Departures/arrivals | `StationBoard` |
| Route planning | `TripSearch` |
| Geolocation / nearby stops | `LocGeoPos` or installation-specific equivalent |

## References

- `references/mobiliteit-lu-hafas.md` — tested notes for Luxembourg `mobiliteit.lu` / `cdt.hafas.de` endpoints.

## Pitfalls

- **Do not harden transient auth failures into impossibility.** Distinguish “web app AID works on `/gate`” from “same AID not authorized on opendata REST endpoint”.
- HAFAS client fields can be type-sensitive. If a copied web version string causes parse errors, omit optional client version fields and retry with the minimal observed client envelope.
- Some HAFAS IDs (`lid`) contain volatile `p=` parts; for durable references prefer `extId` where accepted, but keep the full `lid` when a method specifically needs it.
