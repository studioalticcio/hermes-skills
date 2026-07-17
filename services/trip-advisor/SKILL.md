---
name: trip-advisor
description: Use when the user asks whether to bike or take the bus/train to a place in Luxembourg, or wants a quick door-to-door comparison. Combines live vel'OH! availability with mobiliteit.lu transit routing.
version: 1.0.0
metadata:
  hermes:
    tags: [luxembourg, transit, veloh, bike, bus, travel, mobiliteit]
    related_skills: [mobiliteit, location-aware-alerts]
---

# Trip advisor (bike or bus)

Answers "should I bike or bus to X?" for trips starting from home (Kirchberg).

## Use it

```bash
~/.hermes/skills/services/trip-advisor/scripts/trip-advisor.py --json "Luxembourg, Gare Centrale"
```

Returns `{destination, recommend: bike|bus, bus:{depart,arrive,minutes,transfers}, bike:{minutes,pickup,pickup_bikes,dropoff,ride_km,walk_m}}`. Drop `--json` for a human-readable block.

## How it decides

- **Bike leg** reads the live vel'OH! feed at `/var/lib/server-dashboard/feeds/veloh.json` (refreshed every 3 min). It picks the nearest open station to home with a bike, the nearest open station to the destination with a free stand, and estimates walk + ride time. No available bike or dock => bike option is null.
- **Bus leg** shells out to the `mobiliteit` CLI (`route`) for the next real door-to-door itinerary.
- Recommends the faster option, with a small reliability bias toward transit on near-ties.

## Honest limits

- Distances are geodesic × a fixed detour factor; speeds are fixed (tune via `WALK_KMH`, `BIKE_KMH`, `DETOUR`, `HOME_STOP` env). It is a nudge, not turn-by-turn routing.
- No weather/rain input yet; mention that when it is close and the sky matters.
- Origin defaults to `HOME_STOP`; for a different origin, run `mobiliteit route "<origin>" "<dest>"` directly and read the bike feed for the same destination.

## When it says both are null

Feed stale or mobiliteit down — say so, do not invent times. Fail closed like the other location skills.
