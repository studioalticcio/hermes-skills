---
name: home-assistant
description: Read entity states and call services on Home Assistant (lights, switches, scenes, automations) over the REST API.
version: 1.0.0
platforms: [linux]
tags: [hermes, home, home-assistant, smarthome, automation]
---

# Home Assistant

Home Assistant runs on a separate LAN device at `http://<LAN_IP>:<PORT>`.
A long-lived access token is in env as `HA_TOKEN`.

## Auth

```bash
set -a; . /var/lib/hermes/secrets/services.env; set +a
HA="http://<LAN_IP>:<PORT>/api"
H="Authorization: Bearer $HA_TOKEN"
```

If `HA_TOKEN` is missing: create one in HA UI under **Profile > Long-Lived Access
Tokens > Create Token**, then `echo 'HA_TOKEN=<token>' >> /var/lib/hermes/secrets/services.env`.

## Read state

```bash
# All entities (id + state)
curl -s "$HA/states" -H "$H" | python3 -c "import json,sys; [print(e['entity_id'], '=', e['state']) for e in json.load(sys.stdin)]"

# Filter to lights
curl -s "$HA/states" -H "$H" | python3 -c "import json,sys; [print(e['entity_id'],'=',e['state']) for e in json.load(sys.stdin) if e['entity_id'].startswith('light.')]"

# Single entity state
curl -s "$HA/states/light.living_room" -H "$H"
```

## Call services

Pattern: `POST /api/services/<domain>/<service>` with JSON body naming the target.

```bash
# Turn a light on (with brightness 0-255 and color)
curl -s -X POST "$HA/services/light/turn_on" -H "$H" -H "Content-Type: application/json" \
  -d '{"entity_id":"light.living_room","brightness":180}'

# Turn a light off
curl -s -X POST "$HA/services/light/turn_off" -H "$H" -H "Content-Type: application/json" \
  -d '{"entity_id":"light.living_room"}'

# Toggle a switch
curl -s -X POST "$HA/services/switch/toggle" -H "$H" -H "Content-Type: application/json" \
  -d '{"entity_id":"switch.desk_lamp"}'

# Activate a scene
curl -s -X POST "$HA/services/scene/turn_on" -H "$H" -H "Content-Type: application/json" \
  -d '{"entity_id":"scene.movie_night"}'

# Trigger an automation
curl -s -X POST "$HA/services/automation/trigger" -H "$H" -H "Content-Type: application/json" \
  -d '{"entity_id":"automation.morning_routine"}'

# Enable / disable an automation
curl -s -X POST "$HA/services/automation/turn_off" -H "$H" -H "Content-Type: application/json" \
  -d '{"entity_id":"automation.morning_routine"}'
```

## Notes

- This is the one service NOT on localhost — it is a separate device on the LAN.
- `GET /api/` (with token) is a quick health check; returns `{"message":"API running."}`.
