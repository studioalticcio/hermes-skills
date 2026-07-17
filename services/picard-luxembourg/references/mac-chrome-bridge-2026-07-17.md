# Mac Chrome bridge — 2026-07-17

## Purpose

Use a real Mac Chrome profile for sites whose browser challenges reject server-side authentication. The server reaches Chrome DevTools through a reverse SSH tunnel; Chrome itself stays on the Mac.

## Verified topology

```text
Mac Chrome --debugging 127.0.0.1:<PORT>
     | SSH reverse forward
alticcio-server 127.0.0.1:<PORT>
```

Server identity: `alticcio-server.tailnet.ts.net`.

Mac launch pattern (dedicated profile; never Zen/Firefox for CDP work):

```bash
mkdir -p "$HOME/.grocery-chrome"
open -na "Google Chrome" --args \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.grocery-chrome"
```

Tunnel:

```bash
ssh -fNT -o ExitOnForwardFailure=yes \
  -R 127.0.0.1:<PORT>:127.0.0.1:<PORT> \
  user@alticcio-server.tailnet.ts.net
```

The reverse listener is loopback-only. Do not bind CDP to a LAN/Tailscale/public interface.

## Picard implication

Direct server-side login reached Picard's Cloudflare browser challenge. Password automation is therefore the wrong path. In the bridged Chrome profile, the user logs into Picard and completes challenges manually. Then build/read the server adapter against the established browser/session context; never ask for or type passwords/cookies in chat.

## Verification

On the server:

```bash
curl -fsS http://127.0.0.1:<PORT>/json/version
```

A valid result identifies a Mac Chrome browser. Do not inspect or print cookies, credentials, or unrelated tabs.
