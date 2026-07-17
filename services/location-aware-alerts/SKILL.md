---
name: location-aware-alerts
description: Build privacy-conscious location-gated alerts that combine Home Assistant presence with live local-service availability.
version: 1.0.0
platforms: [linux]
---

# Location-aware alerts

Use for alerts triggered only when the user is at/away from a place and a live external condition is useful: shared-bike availability, gym crowd level, nearby charging/parking, weather, or local transport.

## Design

1. **State the conjunction explicitly.** Example: `person.user == home` AND gym is quiet AND a usable bike is available. Silence when any predicate is false.
2. **Use Home Assistant as presence authority.** Query the specific `person.*` entity, not a guess based on server reachability. Treat `unknown`/`unavailable` as false.
3. **Prefer official/public live feeds.** Discover and verify the provider's actual client backend first; do not infer availability from static maps.
4. **Keep upstream credentials server-local.** Read service secrets from `/var/lib/hermes/secrets/services.env`; never print, put in chat, or put them in cron prompts. Favour scoped tokens, but a user may provision a service credential locally when the provider has no scoped alternative.
5. **Make the alert idempotent.** Persist a small state record with last alert/predicate result. Send at most one alert per qualifying window; reset only after the conjunction becomes false or after an explicit cooldown.
6. **Fail closed.** If any source errors, is stale, or yields an unrecognised schema, do not alert. Log enough non-secret diagnostic detail to repair it.
7. **Test each predicate independently before creating the recurring job.** Verify presence, live availability, authentication/session refresh, and notification delivery with real responses.
8. **Use a script-only cron watchdog for deterministic checks.** It should print only the final notification text; empty stdout means no delivery. The script owns all source calls and deduplication.

## Notification content

Include only decision-relevant facts: live count/level, the selected service/station, availability, distance if relevant, and the trigger time. Avoid repeated “nothing available” pings.

## References

- `references/veloh-live-availability.md` — verified live vel’OH! discovery/query pattern.
- `references/magicline-jims-utilisation.md` — Jims/Magicline endpoint map and authentication findings.
