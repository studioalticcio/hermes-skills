---
name: adguard
description: Control AdGuard Home (stats, enable/disable protection, DNS rewrites, query log) via its REST API.
version: 1.0.0
platforms: [linux]
tags: [hermes, services, adguard, dns, network]
---

# AdGuard Home

AdGuard Home runs locally at `http://localhost:<PORT>` and serves DNS for the LAN.
The control API lives under `/control/`.

## Setup (credentials)

Basic-auth credentials are not in env. They were set during AdGuard setup
(often `admin` plus a chosen password). To find/reset, check the config:

```bash
grep -A2 'users:' /var/lib/AdGuardHome/AdGuardHome.yaml 2>/dev/null || \
grep -A2 'users:' /etc/AdGuardHome.yaml 2>/dev/null
# password there is a bcrypt hash; reset by replacing it and restarting the service.
```

Once known, add to secrets:

```
echo 'ADGUARD_USER=admin'    >> /var/lib/hermes/secrets/services.env
echo 'ADGUARD_PASS=<pass>'   >> /var/lib/hermes/secrets/services.env
```

```bash
set -a; . /var/lib/hermes/secrets/services.env; set +a
B="http://localhost:<PORT>/control"
A="-u $ADGUARD_USER:$ADGUARD_PASS"
```

## Commands

```bash
# Status (protection enabled, version, dns addrs)
curl -s $A "$B/status"

# Stats (queries, blocked, top domains)
curl -s $A "$B/stats"

# Disable protection for 1h (ms); 0 = indefinite
curl -s $A -X POST "$B/protection" -H "Content-Type: application/json" \
  -d '{"enabled":false,"duration":3600000}'

# Enable protection
curl -s $A -X POST "$B/protection" -H "Content-Type: application/json" \
  -d '{"enabled":true}'

# List custom DNS rewrites
curl -s $A "$B/rewrite/list"

# Add a DNS rewrite
curl -s $A -X POST "$B/rewrite/add" -H "Content-Type: application/json" \
  -d '{"domain":"nas.lan","answer":"<LAN_IP>"}'

# Remove a DNS rewrite
curl -s $A -X POST "$B/rewrite/delete" -H "Content-Type: application/json" \
  -d '{"domain":"nas.lan","answer":"<LAN_IP>"}'

# Recent query log
curl -s $A "$B/querylog?limit=20" | python3 -c "import json,sys; [print(q.get('time',''), q.get('question',{}).get('name',''), q.get('reason','')) for q in json.load(sys.stdin).get('data',[])]"
```

## Notes

- All commands are local. AdGuard also acts as the LAN DNS resolver — be careful disabling.
