# mobiliteit.lu / Luxembourg public transport HAFAS notes

Use this when the user asks about mobiliteit.lu APIs, Luxembourg public-transport routing, stops, departures, or building a Mobiliteit client.

## Endpoints

mobiliteit.lu embeds a HAFAS web app:

- Web app: `https://cdt.hafas.de/`
- Config: `https://cdt.hafas.de/config/webapp.config.json`
- Working API gateway: `https://cdt.hafas.de/gate`

Config observed:

```json
{
  "urlMgate": "https://cdt.hafas.de/gate",
  "hciAuth": { "aid": "SkC81GuwuzL4e0" }
}
```

Gateway constants:

```text
base:   https://cdt.hafas.de
gate:   https://cdt.hafas.de/gate
aid:    SkC81GuwuzL4e0
client: {"id":"MMILUX","type":"WEB","name":"webapp","l":"vs_webapp"}
ver:    1.77
lang:   eng / fra / deu
```

## Working pattern: POST JSON to `/gate`

Base envelope:

```json
{
  "lang": "eng",
  "ver": "1.77",
  "auth": { "type": "AID", "aid": "SkC81GuwuzL4e0" },
  "client": { "id": "MMILUX", "type": "WEB", "name": "webapp", "l": "vs_webapp" },
  "svcReqL": []
}
```

Important: do **not** include `client.v` as the string web-app version (`"1.0.12"`); one tested request failed because HAFAS expected an integer there. Omitting `v` works.

## Stop search: `LocMatch`

```json
{
  "meth": "LocMatch",
  "req": {
    "input": {
      "field": "S",
      "loc": { "name": "Hamilius", "type": "S" }
    }
  }
}
```

Real result examples:

```text
Hamilius (Bus)
extId: 200405020
lid: A=1@O=Hamilius (Bus)@X=6125978@Y=49611502@U=82@L=200405020@p=1782988547@

Hamilius-Centre (Tram)
extId: 200405057
lid: A=1@O=Hamilius-Centre (Tram)@X=6126140@Y=49611098@U=82@L=200405057@p=1782988547@
```

## Departures / arrivals: `StationBoard`

Use a `lid` returned by `LocMatch`.

```json
{
  "meth": "StationBoard",
  "req": {
    "stbLoc": { "lid": "A=1@O=Hamilius (Bus)@X=6125978@Y=49611502@U=82@L=200405020@p=1782988547@" },
    "type": "DEP",
    "date": "20260708",
    "time": "120000",
    "maxJny": 5
  }
}
```

`type` can be `DEP` for departures; `ARR` is the likely arrival analogue.

## Opendata apiserver caveat

`https://cdt.hafas.de/opendata/apiserver/` exposes WADL links for `departureBoard`, `location.nearbystops`, and XSD, but the web-app AID is not authorized there. Tested call with `accessId=SkC81GuwuzL4e0` returned:

```json
{
  "errorCode": "API_AUTH",
  "errorText": "access denied for SkC81GuwuzL4e0 on location.nearbystops identified by location.nearbystops"
}
```

So use `/gate` unless the user has a separate official `accessId`.

## Likely useful HAFAS methods

- `LocMatch` — stop/address/POI search.
- `StationBoard` — departures/arrivals.
- `TripSearch` — route planning; inspect web-app requests or HAFAS docs/examples for exact request shape before using.
- Nearby stops may be `LocGeoPos` or another HAFAS geolocation method; inspect app traffic/config before committing.

## Minimal Python probe

```python
import json, urllib.request

AID = "SkC81GuwuzL4e0"

def gate(reqs):
    payload = {
        "lang": "eng",
        "ver": "1.77",
        "auth": {"type": "AID", "aid": AID},
        "client": {"id": "MMILUX", "type": "WEB", "name": "webapp", "l": "vs_webapp"},
        "svcReqL": reqs,
    }
    req = urllib.request.Request(
        "https://cdt.hafas.de/gate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

print(gate([{
    "meth": "LocMatch",
    "req": {"input": {"field": "S", "loc": {"name": "Hamilius", "type": "S"}}},
}]))
```
