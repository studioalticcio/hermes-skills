---
name: smart-home
description: Control a Home Assistant instance at <LAN_IP>:<PORT> -- lights, vacuum, media players. Token in HA_TOKEN env var.
version: 1.0.0
platforms: [linux]
metadata:
  hermes:
    tags: [Home Assistant, smart home, lights, vacuum, Hue, IKEA, automation]
---

# Home Assistant

## Reading Credentials
Secrets live in `/var/lib/hermes/secrets/services.env`. ALWAYS use this pattern -- do NOT check os.environ alone, it may fail in subprocesses:

```python
import os

def get_secret(key):
    # Try process env first (set by systemd EnvironmentFile)
    val = os.environ.get(key, "")
    if val:
        return val
    # Fall back to reading the secrets file directly
    try:
        for line in open("/var/lib/hermes/secrets/services.env"):
            line = line.strip()
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return ""
```

**URL:** `http://<LAN_IP>:<PORT>`
**Token:** HA_TOKEN in /var/lib/hermes/secrets/services.env

## Entity Quick Reference

Entity IDs are installation-specific — discover yours with the "Get all light
states" command below. Examples use generic names:

### Lights
- `light.living_room`, `light.bedroom`, `light.hallway`
- `light.kitchen_1` … `light.kitchen_4`
- `light.desk`, `light.accent`

### Media Players
- `media_player.living_room`, `media_player.kitchen`

### Switches
- `switch.string_lights`
- `switch.outlet_1` (a smart plug)

### Vacuum Scripts
```
script.vacuum_clean_house, script.vacuum_clean_kitchen,
script.vacuum_clean_living_room, script.vacuum_clean_bedroom,
script.vacuum_clean_bathroom, script.vacuum_clean_hallway,
script.vacuum_charge, script.vacuum_stop
```

## Commands

### Turn light on
```bash
HA=$(grep "^HA_TOKEN=" /var/lib/hermes/secrets/services.env | cut -d= -f2)
curl -s -X POST "http://<LAN_IP>:<PORT>/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}'
```

### Set brightness + colour temp
```bash
HA=$(grep "^HA_TOKEN=" /var/lib/hermes/secrets/services.env | cut -d= -f2)
curl -s -X POST "http://<LAN_IP>:<PORT>/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA" -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "brightness_pct": 60, "color_temp": 4000}'
```

### Turn off all lights
```bash
HA=$(grep "^HA_TOKEN=" /var/lib/hermes/secrets/services.env | cut -d= -f2)
curl -s -X POST "http://<LAN_IP>:<PORT>/api/services/light/turn_off" \
  -H "Authorization: Bearer $HA" -H "Content-Type: application/json" \
  -d '{"entity_id": "all"}'
```

### Run vacuum script
```bash
HA=$(grep "^HA_TOKEN=" /var/lib/hermes/secrets/services.env | cut -d= -f2)
curl -s -X POST "http://<LAN_IP>:<PORT>/api/services/script/turn_on" \
  -H "Authorization: Bearer $HA" -H "Content-Type: application/json" \
  -d '{"entity_id": "script.vacuum_clean_living_room"}'
```

### Get all light states
```bash
HA=$(grep "^HA_TOKEN=" /var/lib/hermes/secrets/services.env | cut -d= -f2)
curl -s "http://<LAN_IP>:<PORT>/api/states" -H "Authorization: Bearer $HA" | \
  python3 -c "import json,sys; [print(e['entity_id'],'->', e['state']) for e in json.load(sys.stdin) if e['entity_id'].startswith('light.')]"
```

## Rules
1. Always read HA_TOKEN from /var/lib/hermes/secrets/services.env
2. "Turn off lights" -> turn off all light.* entities
3. "Vacuum" without room -> script.vacuum_clean_house
4. Confirm before running vacuum -- it's noisy
