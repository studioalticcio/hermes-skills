# mobiliteit.lu HAFAS gate notes

## Working endpoint

mobiliteit.lu embeds a HAFAS web app served from `https://cdt.hafas.de/`.

Public runtime config:

```txt
https://cdt.hafas.de/config/webapp.config.json
```

As of 2026-07-08 the useful values were:

```txt
gate:   https://cdt.hafas.de/gate
aid:    SkC81GuwuzL4e0
client: id=MMILUX type=WEB name=webapp l=vs_webapp
ver:    1.77
```

If requests start failing, re-read the config and update the CLI default AID/client before assuming the API is gone.

## Envelope

```json
{
  "lang": "eng",
  "ver": "1.77",
  "auth": { "type": "AID", "aid": "SkC81GuwuzL4e0" },
  "client": { "id": "MMILUX", "type": "WEB", "name": "webapp", "l": "vs_webapp" },
  "svcReqL": []
}
```

## Tested methods

### LocMatch

Stop/location search:

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

Useful fields in matches:

- `name`
- `type`
- `extId`
- `lid`
- `crd.x` / `crd.y` as microdegrees (`x=lon`, `y=lat`)

### StationBoard

Departures / arrivals:

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

Response carries departures in `res.jnyL`. Resolve product names through `res.common.prodL[jny.prodX].name`; resolve location indices through `res.common.locL[index].name`.

### TripSearch

Route planning:

```json
{
  "meth": "TripSearch",
  "req": {
    "depLocL": [{ "lid": "..." }],
    "arrLocL": [{ "lid": "..." }],
    "outDate": "20260708",
    "outTime": "120000",
    "numF": 3,
    "getPasslist": false,
    "getPolyline": false,
    "jnyFltrL": [{ "type": "PROD", "mode": "INC", "value": 127 }]
  }
}
```

Top-level connection times use `dep.dTimeS` / `dep.dTimeR` and `arr.aTimeS` / `arr.aTimeR`. Do not look for plain `timeS`.

## Response semantics

HAFAS often returns both top-level and per-service `err: "OK"`. Treat only non-OK `err` as failure.

## OpenData apiserver caveat

`https://cdt.hafas.de/opendata/apiserver/` advertises WADL endpoints, including `departureBoard` and `location.nearbystops`, but the web-app AID is not authorised there. A tested request returned:

```json
{
  "serverVersion": "2.52.2",
  "dialectVersion": "2.52",
  "errorCode": "API_AUTH",
  "errorText": "access denied for SkC81GuwuzL4e0 on location.nearbystops identified by location.nearbystops"
}
```

Default to `/gate`. Use `/opendata/apiserver` only with a separate official `accessId`.
