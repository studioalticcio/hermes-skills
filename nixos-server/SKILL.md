---
name: nixos-server
description: Manage alticcio-server NixOS configuration — rebuild system, manage systemd services, Podman containers, and NixOS modules. You ARE running on this server.
version: 1.2.0
platforms: [linux]
metadata:
  hermes:
    tags: [NixOS, server, infrastructure, Podman, systemd, nix]
---

# alticcio-server (NixOS 25.11)

You ARE on this server. Do NOT SSH to yourself. All commands run locally.

NixOS config: `/etc/nixos/` (requires sudo). Flake rebuild:
```bash
sudo nixos-rebuild switch --flake /etc/nixos#alticcio-server
```

---

## System Health

```bash
# Service overview
systemctl list-units --type=service --state=failed
systemctl list-units --type=service --state=running --no-legend | wc -l

# Disk usage
df -h /srv /var /

# Memory
free -h

# Logs for any service
journalctl -u SERVICE_NAME -f --no-pager -n 50
```

---

## Podman Containers

```bash
# List all containers with status
podman ps -a --format "table {{.Names}}	{{.Status}}	{{.Ports}}"

# Container logs
podman logs --tail 50 CONTAINER_NAME

# Restart a container
sudo systemctl restart podman-CONTAINER_NAME.service

# Exec into container
sudo podman exec -it CONTAINER_NAME bash
```

Active containers: `calibre-web`, `kavita`, `mealie`, `miniflux`, `miniflux-db`, `ghostfolio`, `ghostfolio-db`, `ghostfolio-redis`, `ntfy`, `flaresolverr`, `devonthink-webdav`, `dufs`, `kiwix`, `kosync`

---

## NixOS Module Management

Config modules in `/etc/nixos/modules/`. Add/modify services by editing the relevant `.nix` file then rebuilding.

```bash
# Edit a module
sudo nano /etc/nixos/modules/SERVICE.nix

# Rebuild (applies changes)
sudo nixos-rebuild switch --flake /etc/nixos#alticcio-server

# Test without switching (dry run)
sudo nixos-rebuild dry-activate --flake /etc/nixos#alticcio-server

# Check current generation
nixos-version
sudo nix-env --list-generations --profile /nix/var/nix/profiles/system | tail -5
```

---

## Hermes Self-Management

### Separate Hermes instance for another person

A Hermes *profile* separates application state (sessions, memories, skills, config), but is **not** a filesystem security boundary. For a genuinely separate person on this host, use a dedicated Unix account and an independent systemd gateway service.

1. Create a dedicated user (e.g. `austin`) and private data root such as `/srv/austin/{uploads,workspace,archive}`, owned by that user and mode `0700`.
2. Give the service its own `HERMES_HOME` (normally `/home/austin/.hermes`), its own `SOUL.md`, `auth.json`, and per-instance secrets file. Never clone the primary profile's `.env`, `auth.json`, Google tokens, or shared `services.env` wholesale.
3. Run a distinct `hermes gateway run --replace` service as that Unix user. Set `WorkingDirectory`, `HERMES_HOME`, `ReadWritePaths`, resource limits, and network/path access deliberately; do not reuse the main service's broad `/srv` and secrets permissions.
4. Enable only capabilities intentionally shared. For shared APIs (*arr, Home Assistant) copy only the necessary credential into the instance-specific secret store; those capabilities can still affect shared media/home state. Calibre access likewise intentionally exposes the shared library and should remain read-only. For Navidrome, create a distinct non-admin service account rather than copying an administrator credential.
5. Never provide a general mailbox credential merely to retrieve a narrow OTP. Keep mailbox auth in a privileged bridge which returns only the required, tightly filtered value (for AXA EBN: newest six-digit code from `noreply@axa.lu` with the expected security-code subject) through a local authenticated endpoint. Do not expose message listings, bodies, attachments, arbitrary queries, or OTP values in logs. A secondary user’s own email account may be configured separately in their own protected state.
6. Use a separate Telegram bot token and pairing/allowlist. Keep the gateway disabled until its token is present, then start it and verify `systemctl status`, `hermes gateway list`, and a live paired message.
7. Configure `openai-codex` but have the secondary user complete interactive ChatGPT OAuth/device login inside their own `HERMES_HOME`; do not solicit or store their ChatGPT password. Subscriptions and OAuth identity are separate from host filesystem isolation.
8. Keep voice audio caches inside the secondary home. For cloud transcription/OCR, copy only the required provider credential and disclose external processing; restrict document inputs/outputs to the secondary workspace. On this 8 GB host, do not install heavyweight local OCR models by default when a cloud OCR path is available.

Use a VM/container only if the secondary agent will run arbitrary or untrusted code. For normal trusted use, Unix user + systemd path sandboxing is materially lighter and appropriate for this host.

```bash
# Restart Hermes (this service — will disconnect current session)
sudo systemctl restart hermes-telegram.service

# Check Hermes status
systemctl status hermes-telegram.service

# Hermes logs
journalctl -u hermes-telegram.service -f --no-pager -n 50

# Hermes secrets
cat /var/lib/hermes/secrets/services.env | grep -v KEY | grep -v TOKEN | grep -v PASS
```

---

## File Structure

```
/srv/calibre/library    Ebooks (Calibre-Web)
/srv/calibre/bds        BD/comics (Kavita)
/srv/media/movies       Movies (Radarr/Jellyfin)
/srv/media/tvshows      TV shows (Sonarr/Jellyfin)
/srv/media/music        Music (Lidarr/Navidrome)
/srv/media/.downloads   Transmission complete
/srv/media/.incomplete  Transmission in-progress
/srv/obsidian/          Obsidian vault (Syncthing)
/srv/documents/         iCloud mirror (Syncthing) — ask before writing
/srv/devonthink-sync/   DEVONthink WebDAV sync
/var/lib/hermes/        Hermes data and secrets
/etc/nixos/             NixOS configuration (sudo)
```

---

## Temporary iPhone HTTPS capture

For a consented, domain-limited iPhone app traffic capture hosted on this server, follow [references/ios-https-capture-proxy.md](references/ios-https-capture-proxy.md) and the extraction/dedup notes in [references/ios-traffic-capture-proxy.md](references/ios-traffic-capture-proxy.md). Keep it LAN-only and temporary.

## Rules

1. You are ON the server — never run `ssh alticcio-server ...` from within a skill
2. Always run `sudo nixos-rebuild switch --flake /etc/nixos#alticcio-server` after editing .nix files
3. Podman containers are managed as systemd services (`podman-NAME.service`)
4. For service-specific operations, use the dedicated skills (arr-stack, calibre, jellyfin, etc.)
5. Check `systemctl status SERVICE` before and after any service changes
6. Secrets are in `/var/lib/hermes/secrets/services.env` — always use the get_secret() pattern
