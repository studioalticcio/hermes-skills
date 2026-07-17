---
name: leclerc-drive
description: Use when searching, comparing, or preparing a real E.Leclerc Drive cart through a user-authorized Chrome CDP session.
version: 1.0.0
metadata:
  hermes:
    tags: [leclerc, drive, groceries, cart, chrome, cdp, shopping]
---

# E.Leclerc Drive

## Overview

Operate E.Leclerc Drive through `mcp-leclerc-drive`, which performs requests inside a real Chrome session over CDP. This is required for DataDome; cookie replay and headless browsing are not an acceptable substitute.

Never promise a cart mutation based on an MCP acknowledgement alone. Read the remote cart after every add, quantity update, or removal.

## Prerequisites

1. Verify a dedicated, user-authorized Chrome profile is running and logged into the intended Drive.
2. Verify the server reaches its loopback-only CDP bridge:

```bash
curl -fsS http://127.0.0.1:<PORT>/json/version
```

3. Start from `find_stores` where it resolves the correct Drive. If its Luxembourg lookup is wrong, derive the active store ID and host from the authenticated Drive page, set the store explicitly, then prove search and `get_cart` before any mutation.
4. Never request or type passwords, cookies, payment credentials, or challenge responses. The user completes login/Cloudflare/DataDome in visible Chrome.

## MCP setup

Installed MCP: `leclerc-drive`.

The runtime command is:

```text
node /home/user/.npm-global/lib/node_modules/mcp-leclerc-drive/dist/index.js
```

It exposes:

- `find_stores`, `set_store`, `get_store`
- `search_product`
- `get_cart`, `add_to_cart`, `update_quantity`, `remove_from_cart`

A new Hermes session is required before newly configured MCP tools appear in tool selection.

## Safe workflow

1. **Readiness:** verify CDP, `get_store`, a narrow `search_product`, and `get_cart`.
2. **Comparison:** normalise unit price, pack size, availability, and actual pickup friction against the competing shops.
3. **Proposal:** show the basket split and substitutions. Obtain explicit approval before changing any real cart.
4. **Mutation:** add/update/remove one item at a time. Preserve the MCP's anti-strike cadence; never parallelise cart calls.
5. **Verification:** call `get_cart` after every mutation and compare expected product ID, quantity, and total. Treat ambiguity, session expiry, or unchanged state as failure.
6. **Boundary:** do not checkout, choose a slot, or pay.

## Luxembourg pitfall

The upstream store locator can mis-geocode Luxembourg searches to French locations. A real authenticated Foetz page exposed the correct Drive context only after opening its actual URL; do not trust a location result merely because it is returned.

See `references/foetz-bridge-2026-07-17.md`.

## Security

- The Chrome DevTools port must bind only to `127.0.0.1` on both machines.
- Bridge it with a reverse SSH tunnel; never expose CDP to LAN, Tailscale, or the public internet.
- Do not inspect unrelated browser tabs, print cookies, or leave a browser automation window on financial/email sites.

## Completion criteria

A Leclerc basket is ready only when `get_cart` confirms its final contents, quantities, total, and intended Drive context. Report it for collection/payment; leave checkout to the user.
