# hermes-skills

A curated set of custom [Hermes Agent](https://github.com/) skills I wrote to run a self-hosted life-automation setup in Luxembourg: grocery-drive integrations, live transit and bike planning, a home server, Telegram Mini Apps, and a self-hosted media/home stack.

Every skill here is my own; Hermes' built-in skills are excluded. Each is a folder with a `SKILL.md` (instructions the agent loads on demand) plus optional `scripts/` and `references/`. All personal data — names, home address, device/entity names, LAN IPs, ports, tokens — is replaced with placeholders. Adapt them to your own setup.

**31 skills** across 9 categories.

## Skills

### Luxembourg & self-hosted service integrations

| Skill | What it does |
|-------|--------------|
| `adguard` | Control AdGuard Home (stats, enable/disable protection, DNS rewrites, query log) via its REST API. |
| `auchan-lu-mcp` | Patch and operate mcp-auchan-drive against Auchan Luxembourg's PrestaShop/Klevu stack. |
| `grocery-cart-automation` | Use when comparing retailers and creating or maintaining authenticated grocery carts across retailer-specific web stacks, MCPs, or browser sessions. |
| `grocery-shopping-mcps` | Use when planning groceries or connecting supermarket MCPs for the user in Luxembourg. Distinguish live catalogues, local planning carts, and real che |
| `immich` | Query the Immich photo library via its REST API (server stats, albums, search assets, recent uploads). |
| `kosync` | KOSync server for the user's Boox e-reader (KOReader reading progress sync). Runs at localhost:<PORT>. Lightweight REST API. |
| `leclerc-drive` | Use when searching, comparing, or preparing a real E.Leclerc Drive cart through a user-authorized Chrome CDP session. |
| `location-aware-alerts` | Build privacy-conscious location-gated alerts that combine Home Assistant presence with live local-service availability. |
| `mealie` | Manage the Mealie recipe manager via its REST API (list/search recipes, scrape from URL, meal plans). |
| `miniflux` | Manage the Miniflux RSS reader via its REST API (feeds, unread entries, mark read, add feeds). |
| `mobiliteit` | Use when querying Luxembourg public transport via mobiliteit.lu / cdt.hafas.de: stop search, departures, route planning, and HAFAS API troubleshooting |
| `ntfy` | Send push notifications to the user's phone via the local ntfy server (titles, priority, tags, actions, scheduling). |
| `picard-luxembourg` | Use when planning, pricing, or building a real Picard Luxembourg Click & Collect basket, including cross-store comparison with Auchan Luxembourg. |
| `syncthing` | Manage Syncthing file sync — check folder status, sync progress, device connections. GUI at localhost:<PORT>. API key in config.xml. |
| `trip-advisor` | Use when the user asks whether to bike or take the bus/train to a place in Luxembourg, or wants a quick door-to-door comparison. Combines live vel'OH! |

### Telegram Mini Apps

| Skill | What it does |
|-------|--------------|
| `apps` | Open the Alticcio apps Telegram Mini App. Use when the user types /apps or asks to open Alticcio apps. |
| `grocery` | Open the Grocery compare Telegram Mini App. Use when the user types /grocery or asks to open Grocery compare. |
| `home` | Open the Home glance Telegram Mini App. Use when the user types /home or asks to open Home glance. |
| `trip` | Open the Bike or bus Telegram Mini App. Use when the user types /trip or asks to open Bike or bus. |
| `veloh` | Open the vel'OH! & Jims Telegram Mini App. Use when the user types /veloh or asks to open vel'OH! & Jims. |

### Home Assistant

| Skill | What it does |
|-------|--------------|
| `home-assistant` | Read entity states and call services on Home Assistant (lights, switches, scenes, automations) over the REST API. |

### Smart home

| Skill | What it does |
|-------|--------------|
| `smart-home` | Control a Home Assistant instance at <LAN_IP>:<PORT> -- lights, vacuum, media players. Token in HA_TOKEN env var. |

### Media stack

| Skill | What it does |
|-------|--------------|
| `arr-stack` | Manage the *arr media stack — Sonarr (TV), Radarr (movies), Lidarr (music), Prowlarr (indexers), Bazarr (subtitles). All run locally. API keys in serv |
| `jellyfin` | Query and control the Jellyfin media server (libraries, search, recently added, playback sessions, system info). |
| `jellyfin-users` | Retrieve and list users configured in a Jellyfin instance. |
| `navidrome` | Control the Navidrome music server via the Subsonic API (ping, artists, albums, playlists, now playing). |
| `transmission` | Control Transmission BitTorrent client. Add torrents, check download progress, manage queue. RPC on localhost:<PORT>. |

### NixOS server

| Skill | What it does |
|-------|--------------|
| `nixos-server` | Manage alticcio-server NixOS configuration — rebuild system, manage systemd services, Podman containers, and NixOS modules. You ARE running on this se |

### Productivity

| Skill | What it does |
|-------|--------------|
| `public-transport-apis` | Discover and use public transport APIs, especially HAFAS-backed journey planners and departure boards. |

### Leisure

| Skill | What it does |
|-------|--------------|
| `find-nearby` | Find nearby places (restaurants, cafes, bars, pharmacies, etc.) using OpenStreetMap. Works with coordinates, addresses, cities, zip codes, or Telegram |

### Development workflows

| Skill | What it does |
|-------|--------------|
| `telegram-bot-commands` | Design and implement Telegram bot commands for Hermes, including interactive callback flows, confirmations, and destructive-action safety. |

## Usage

Drop a skill folder into `~/.hermes/skills/<category>/` and run `/reload_skills`. Skills auto-register as slash commands. Many reference secrets by name (e.g. `MEALIE_API_TOKEN`, `HA_TOKEN`) that you supply in your own environment.

## License

MIT - see [LICENSE](LICENSE). Provided as-is; service integrations track third-party sites that change without notice.
