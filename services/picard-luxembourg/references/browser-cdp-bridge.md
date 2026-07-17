# Browser CDP bridge for grocery commerce

Use when the server must control a user-authenticated commerce session but server-side login is blocked by Cloudflare/DataDome or requires an interactive challenge.

## Design

- Keep normal browsing in Zen/Firefox if preferred.
- Use a dedicated **Google Chrome** profile only for the grocery session. Chrome is required by `mcp-leclerc-drive`, which connects via Chrome DevTools Protocol (CDP); Firefox-derived Zen cannot substitute.
- The Chrome profile may hold Picard and Leclerc sessions. Do not make it the default browser.
- Run Chrome on the Mac, not on the server, when bot protection reliability matters.

## Mac launch

```bash
mkdir -p "$HOME/.grocery-chrome"
open -na "Google Chrome" --args \
  --remote-debugging-address=127.0.0.1 \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.grocery-chrome"
```

Log into each shop and complete any anti-bot challenge manually. Select the desired pickup store before declaring the profile ready.

## Private reverse tunnel

Keep Chrome CDP local on the Mac, then make it available only on the server loopback interface:

```bash
ssh -fNT \
  -o ExitOnForwardFailure=yes \
  -R 127.0.0.1:<PORT>:127.0.0.1:<PORT> \
  user@alticcio-server.tailnet.ts.net
```

Do not bind CDP to `0.0.0.0`, a LAN address, or Tailscale directly. CDP grants browser control and is not an authenticated public service.

## Verification

1. Confirm `http://127.0.0.1:<PORT>/json/version` responds on the Mac.
2. Establish the SSH reverse tunnel.
3. Confirm the same URL responds from the server.
4. Run only a read-only store/product/cart probe first.
5. Enable cart mutations only after the correct account and pickup store are visibly established.

## Safety

- Never send or request passwords, browser cookies, or CDP endpoints in chat.
- Do not automate Cloudflare/DataDome challenges, MFA, payment, checkout, or slot booking.
- Keep cart mutations sequential; read back the remote cart after each mutation.
