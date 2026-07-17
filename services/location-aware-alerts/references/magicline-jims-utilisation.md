# Jims / Magicline utilisation research

Jims Luxembourg member app is Magicline/MySports (`com.mysports.branded.jimsfitness`). Infinity studio ID: `1215478390`.

Public discovery requires headers including `X-Nox-Client-Type: WEB`, `X-MS-Web-Context`, `X-Nox-Web-Context`, and `X-Tenant: jimsfitness`.

Relevant routes:

```text
/nox/public/v1/studios/1215478390/utilization/reveal
/nox/v1/studios/1215478390/utilization/v2/active-checkin
/nox/v1/studios/1215478390/utilization/v2/today
/nox/v1/studios/1215478390/utilization/v2/historic/week
/nox/v1/studios/1215478390/utilization/v2/indicator/limits
```

Public `reveal` returned `false`; public utilisation routes had no record. Member app UI nevertheless displayed live count and historical estimate.

Server-side POST `/login` with Basic auth plus JSON `{username,password}` succeeded and returned `SESSION` plus `access_token`, but a private `active-checkin` call still returned 401. Conclusion: an additional mobile/client-specific authorisation or session-state step is required. Next investigation: reverse engineer the Android client request sequence or capture an authenticated app request; do not assume cookie + returned token suffices.
