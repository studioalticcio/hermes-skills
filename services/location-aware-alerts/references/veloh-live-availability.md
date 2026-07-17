# vel'OH! live availability (Luxembourg)

Official `myveloh.lu` Angular app configuration (observed 2026-07-17) exposes a JCDecaux VLS v3 feed:

```text
GET https://api.jcdecaux.com/vls/v3/stations?contract=luxembourg&apiKey=<public-app key>
```

The current public-app key is embedded in the mapping bundle `https://myveloh.lu/chunk-4VJOEQLR.js` under `openData.stations.apiKey`; retrieve it at runtime rather than hard-coding/persisting it. Parse from the local `openData:{stations:` configuration region because chunk minification can vary.

Useful fields:

```text
name, status, position.latitude/longitude,
totalStands.availabilities.bikes,
totalStands.availabilities.electricalBikes,
totalStands.availabilities.stands
```

Require `status == OPEN` and `bikes >= minimum`. For a home-origin alert, select the closest viable station by geodesic distance, not the closest station irrespective of bikes.

Observed sample: `#00076-HOMESTATION` had 2 electric bikes and 12 free stands on 2026-07-17.
